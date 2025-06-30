<template>
  <div class="risk-resolution-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <!-- Toggle buttons for Risk Resolution and Risk Workflow -->
    <div class="risk-resolution-toggle-buttons">
      <button 
        class="risk-resolution-toggle-button active" 
        @click="navigateTo('resolution')"
      >
        Risk Resolution
      </button>
      <button 
        class="risk-resolution-toggle-button" 
        @click="navigateTo('workflow')"
      >
        Risk Workflow
      </button>
    </div>
    
    <!-- Search and Filter Bar -->
    <div class="risk-resolution-filters-wrapper">
      <Dynamicalsearch 
        v-model="searchQuery" 
        placeholder="Search risks..."
        @input="filterRisks"
      />
      <div class="risk-resolution-filter-dropdowns">
        <CustomDropdown 
          :config="criticalityDropdownConfig"
          v-model="criticalityFilter"
          @change="filterRisks"
        />
        <CustomDropdown 
          :config="statusDropdownConfig"
          v-model="statusFilter"
          @change="filterRisks"
        />
        <CustomDropdown 
          :config="assignedToDropdownConfig"
          v-model="assignedToFilter"
          @change="filterRisks"
        />
        <CustomDropdown 
          :config="reviewerDropdownConfig"
          v-model="reviewerFilter"
          @change="filterRisks"
        />
      </div>
    </div>
    
    <div v-if="loading" class="risk-resolution-loading">
      <div class="risk-resolution-spinner"></div>
      <span>Loading risk data...</span>
    </div>
    
    <div v-else-if="error" class="risk-resolution-error-message">
      {{ error }}
    </div>
    
    <div v-else-if="filteredRisks.length === 0" class="risk-resolution-no-data">
      <p>No eligible risk instances found for resolution. Either there are no risks with completed scoring, or all scored risks have been rejected.</p>
      <p class="risk-resolution-no-data-subtitle">Note: Rejected risks are not displayed in Risk Resolution as they don't require further processing.</p>
    </div>
    
    <!-- Show collapsible table if not in mitigation workflow -->
    <div v-else-if="!showMitigationModal" class="risk-resolution-collapsible-container">
      <CollapsibleTable
        v-for="(section, index) in riskSections"
        :key="section.name"
        :section-config="section"
        :table-headers="tableHeaders"
        :is-expanded="expandedSections[index]"
        @toggle="toggleSection(index)"
        @task-click="openMitigationModal"
        @add-task="addTaskToSection"
      />
    </div>

    <!-- Mitigation Workflow Section -->
    <div v-if="showMitigationModal" class="risk-resolution-mitigation-workflow-section">
      <div class="risk-resolution-mitigation-header">
        <button class="risk-resolution-back-btn" @click="closeMitigationModal">
          <i class="fas fa-arrow-left"></i> Back to Risks
        </button>
        <h2 v-if="viewOnlyMitigationModal">Viewing Mitigation Steps</h2>
        <h2 v-else>Assign Risk with Mitigation Steps</h2>
      </div>
      <div class="risk-resolution-mitigation-body">
        <div v-if="loadingMitigations" class="risk-resolution-loading">
          <div class="risk-resolution-spinner"></div>
          <span>Loading mitigation steps...</span>
        </div>
        <div v-else>
          <div class="risk-resolution-risk-summary">
            <h3>{{ selectedRisk.RiskTitle || 'Risk #' + selectedRisk.RiskInstanceId }}</h3>
            <div class="risk-resolution-risk-details">
              <p><strong>ID:</strong> {{ selectedRisk.RiskInstanceId }}</p>
              <p><strong>Category:</strong> {{ selectedRisk.Category }}</p>
              <p><strong>Criticality:</strong> {{ selectedRisk.Criticality }}</p>
              <p><strong>Reviewer:</strong> <span class="risk-resolution-reviewer-info">{{ selectedRisk.Reviewer || selectedRisk.ReviewerName || 'Not Assigned' }}</span></p>
            </div>
          </div>
          
          <!-- Add User and Reviewer Assignment Section -->
          <div v-if="!viewOnlyMitigationModal" class="risk-resolution-assignment-section">
            <h3>Assign Risk</h3>
            <div class="risk-resolution-assignment-fields">
              <div class="risk-resolution-assignment-field">
                <label>Assign To:</label>
                <select v-model="selectedUsers[selectedRisk.RiskInstanceId]" class="risk-resolution-assignment-dropdown">
                  <option value="">Select User</option>
                  <option v-for="user in users" :key="getUserId(user)" :value="getUserId(user)">
                    {{ getUserName(user) }} (ID: {{ getUserId(user) }})
                  </option>
                </select>
                <div v-if="selectedUsers[selectedRisk.RiskInstanceId]" class="risk-resolution-selected-user-info">
                  Selected User ID: {{ selectedUsers[selectedRisk.RiskInstanceId] }}
                </div>
              </div>
              <div class="risk-resolution-assignment-field">
                <label>Reviewer:</label>
                <select v-model="selectedReviewers[selectedRisk.RiskInstanceId]" class="risk-resolution-assignment-dropdown">
                  <option value="">Select Reviewer</option>
                  <option v-for="user in users" :key="getUserId(user)" :value="getUserId(user)">
                    {{ getUserName(user) }} (ID: {{ getUserId(user) }})
                  </option>
                </select>
                <div v-if="selectedReviewers[selectedRisk.RiskInstanceId]" class="risk-resolution-selected-user-info">
                  Selected Reviewer ID: {{ selectedReviewers[selectedRisk.RiskInstanceId] }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="risk-resolution-mitigation-workflow">
            <h3>Mitigation Steps</h3>
            <!-- Existing Mitigation Steps -->
            <div v-if="mitigationSteps.length" class="risk-resolution-workflow-timeline">
              <div v-for="(step, index) in mitigationSteps" :key="index" class="risk-resolution-workflow-step">
                <div class="risk-resolution-step-number">{{ index + 1 }}</div>
                <div class="risk-resolution-step-content">
                  <textarea 
                    v-model="step.description" 
                    class="risk-resolution-mitigation-textarea"
                    :readonly="viewOnlyMitigationModal"
                    placeholder="Enter mitigation step description"
                  ></textarea>
                  <div class="risk-resolution-step-actions">
                    <button @click="removeMitigationStep(index)" class="risk-resolution-remove-step-btn" :disabled="viewOnlyMitigationModal">
                      <i class="fas fa-trash"></i> Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="risk-resolution-no-mitigations">
              <p>No mitigation steps defined for this risk. Add steps below.</p>
            </div>
            <!-- Add New Mitigation Step -->
            <div class="risk-resolution-add-mitigation">
              <textarea 
                v-model="newMitigationStep" 
                class="risk-resolution-mitigation-textarea"
                :readonly="viewOnlyMitigationModal"
                placeholder="Enter a new mitigation step description"
              ></textarea>
              <button @click="addMitigationStep" class="risk-resolution-add-step-btn" :disabled="viewOnlyMitigationModal || !newMitigationStep.trim()">
                <i class="fas fa-plus"></i> Add Mitigation Step
              </button>
            </div>
            <!-- Due Date Input -->
            <div class="risk-resolution-due-date-section">
              <h4>Due Date for Mitigation Completion</h4>
              <input 
                type="date" 
                v-model="mitigationDueDate" 
                class="risk-resolution-due-date-input" 
                :readonly="viewOnlyMitigationModal"
                :min="getTodayDate()"
              />
            </div>
            <!-- Risk Form Section -->
            <div class="risk-resolution-form-section" style="display: none;">
              <h4>Risk Mitigation Questionnaire</h4>
              <p class="risk-resolution-form-note">Please complete these details about the risk mitigation:</p>
              <div class="risk-resolution-form-field horizontal">
                <label for="cost-input">1. What is the cost for this mitigation?</label>
                <input 
                  id="cost-input" 
                  v-model="riskFormDetails.cost" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter the cost..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="impact-input">2. What is the impact for this mitigation?</label>
                <input 
                  id="impact-input" 
                  v-model="riskFormDetails.impact" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter the impact..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="financial-impact-input">3. What is the financial impact for this mitigation?</label>
                <input 
                  id="financial-impact-input" 
                  v-model="riskFormDetails.financialImpact" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter the financial impact..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="reputational-impact-input">4. What is the reputational impact for this mitigation?</label>
                <textarea 
                  id="reputational-impact-input" 
                  v-model="riskFormDetails.reputationalImpact" 
                  :readonly="viewOnlyMitigationModal"
                  placeholder="Describe the reputational impact..."
                  class="risk-resolution-form-textarea"
                ></textarea>
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="operational-impact-input">5. What is the Operational Impact for this mitigation?</label>
                <input 
                  id="operational-impact-input" 
                  v-model="riskFormDetails.operationalImpact" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter the operational impact..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="financial-loss-input">6. What is the Financial Loss for this mitigation?</label>
                <input 
                  id="financial-loss-input" 
                  v-model="riskFormDetails.financialLoss" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter the financial loss..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="system-downtime-input">7. What is the expected system downtime (hrs) if this risk occurs?</label>
                <input 
                  id="system-downtime-input" 
                  v-model="riskFormDetails.systemDowntime" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter expected downtime in hours..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="recovery-time-input">8. How long did it take to recover last time (hrs)?</label>
                <input 
                  id="recovery-time-input" 
                  v-model="riskFormDetails.recoveryTime" 
                  type="number"
                  :readonly="viewOnlyMitigationModal"
                  min="0"
                  placeholder="Enter recovery time in hours..."
                  class="risk-resolution-form-textarea"
                />
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="recurrence-possible-input">9. Is it possible that this risk will recur again?</label>
                <select 
                  id="recurrence-possible-input" 
                  v-model="riskFormDetails.recurrencePossible" 
                  :disabled="viewOnlyMitigationModal"
                  class="risk-resolution-form-textarea"
                >
                  <option value="">Select</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>
              <div class="risk-resolution-form-field horizontal">
                <label for="improvement-initiative-input">10. Is this an Improvement Initiative which will prevent the future recurrence of said risk?</label>
                <select 
                  id="improvement-initiative-input" 
                  v-model="riskFormDetails.improvementInitiative" 
                  :disabled="viewOnlyMitigationModal"
                  class="risk-resolution-form-textarea"
                >
                  <option value="">Select</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>
            </div>
            <!-- Submit Section -->
            <div class="risk-resolution-mitigation-actions">
              <button 
                @click="assignRiskWithMitigations" 
                class="risk-resolution-submit-mitigations-btn"
                :disabled="viewOnlyMitigationModal || mitigationSteps.length === 0 || !mitigationDueDate || !selectedUsers[selectedRisk.RiskInstanceId] || !selectedReviewers[selectedRisk.RiskInstanceId]"
              >
                <i class="fas fa-user-plus"></i> Assign with Mitigations
              </button>
              <div v-if="viewOnlyMitigationModal && !isFormComplete()" class="risk-resolution-form-warning" style="display: none;">
                <i class="fas fa-exclamation-circle"></i> Please complete all questionnaire fields
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Questionnaire Modal -->
    <div v-if="showQuestionnaireModal" class="risk-resolution-questionnaire-modal-overlay">
      <div class="risk-resolution-questionnaire-modal-content">
        <button class="risk-resolution-close-modal-btn" @click="closeQuestionnaireModal"><i class="fas fa-times"></i></button>
        <h3>Risk Mitigation Questionnaire (View Only)</h3>
        <div v-if="selectedQuestionnaire">
          <div class="risk-resolution-questionnaire-field"><strong>1. Cost:</strong> {{ selectedQuestionnaire.cost }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>2. Impact:</strong> {{ selectedQuestionnaire.impact }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>3. Financial Impact:</strong> {{ selectedQuestionnaire.financialImpact }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>4. Reputational Impact:</strong> {{ selectedQuestionnaire.reputationalImpact }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>5. Operational Impact:</strong> {{ selectedQuestionnaire.operationalImpact }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>6. Financial Loss:</strong> {{ selectedQuestionnaire.financialLoss }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>7. System Downtime (hrs):</strong> {{ selectedQuestionnaire.systemDowntime }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>8. Recovery Time (hrs):</strong> {{ selectedQuestionnaire.recoveryTime }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>9. Recurrence Possible:</strong> {{ selectedQuestionnaire.recurrencePossible }}</div>
          <div class="risk-resolution-questionnaire-field"><strong>10. Improvement Initiative:</strong> {{ selectedQuestionnaire.improvementInitiative }}</div>
        </div>
        <div v-else>
          <p>No questionnaire data found for this risk.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CustomDropdown from '../CustomDropdown.vue';
import Dynamicalsearch from '../Dynamicalsearch.vue';
import CollapsibleTable from '../CollapsibleTable.vue';
import { PopupModal } from '@/modules/popup';

export default {
  name: 'RiskResolution',
  components: {
    CustomDropdown,
    Dynamicalsearch,
    CollapsibleTable,
    PopupModal
  },
  data() {
    return {
      risks: [],
      filteredRisks: [],
      users: [],
      selectedUsers: {},
      selectedReviewers: {},
      loading: true,
      error: null,
      // New properties for mitigation modal
      showMitigationModal: false,
      selectedRisk: {},
      mitigationSteps: [],
      newMitigationStep: '',
      loadingMitigations: false,
      mitigationDueDate: '',
      riskFormDetails: {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: '',
        operationalImpact: '',
        financialLoss: '',
        systemDowntime: '',
        recoveryTime: '',
        recurrencePossible: '',
        improvementInitiative: ''
      },
      showQuestionnaireModal: false,
      selectedQuestionnaire: null,
      viewOnlyMitigationModal: false,
      // New properties for search and filtering
      searchQuery: '',
      criticalityFilter: '',
      statusFilter: '',
      assignedToFilter: '',
      reviewerFilter: '',
      expandedSections: []
    }
  },
  computed: {
    uniqueCriticalities() {
      return [...new Set(this.risks.map(risk => risk.Criticality).filter(Boolean))];
    },
    uniqueStatuses() {
      return [...new Set(this.risks.map(risk => risk.RiskStatus).filter(Boolean))];
    },
    uniqueAssignedUsers() {
      return [...new Set(this.risks.map(risk => 
        risk.RiskOwner && risk.RiskOwner !== 'System Owner' && risk.RiskOwner !== 'System User' ? 
        risk.RiskOwner : 'Not Assigned'
      ))];
    },
    uniqueReviewers() {
      return [...new Set(this.risks.map(risk => risk.ReviewerName || 'Not Assigned'))];
    },
    // Table headers for CollapsibleTable
    tableHeaders() {
      return [
        { key: 'riskId', label: 'ID', width: '80px' },
        { key: 'riskTitle', label: 'Risk Title', width: '200px' },
        { key: 'category', label: 'Category', width: '120px' },
        { key: 'criticality', label: 'Criticality', width: '100px' },
        { key: 'priority', label: 'Priority', width: '100px' },
        { key: 'status', label: 'Status', width: '120px' },
        { key: 'assignedTo', label: 'Assigned To', width: '150px' },
        { key: 'reviewer', label: 'Reviewer', width: '150px' },
        { key: 'reviewCount', label: 'Review Count', width: '100px' },
        { key: 'actions', label: 'Action', width: '120px' }
      ];
    },
    // Group risks by status for CollapsibleTable
    riskSections() {
      const sections = {};
      
      this.filteredRisks.forEach(risk => {
        const status = risk.RiskStatus || 'Unknown';
        if (!sections[status]) {
          sections[status] = {
            name: status,
            statusClass: this.getStatusClass(status),
            tasks: []
          };
        }
        
        // Format risk data for table display
        const formattedRisk = {
          incidentId: risk.RiskInstanceId,
          riskId: risk.RiskInstanceId,
          riskTitle: risk.RiskTitle || 'No title',
          category: risk.Category || 'N/A',
          criticality: `<span class="risk-resolution-criticality-badge ${this.getCriticalityClass(risk.Criticality)}">${risk.Criticality || 'N/A'}</span>`,
          priority: `<span class="risk-resolution-priority-badge ${this.getPriorityClass(risk.RiskPriority)}">${risk.RiskPriority || 'N/A'}</span>`,
          status: `<span class="risk-resolution-status-badge">${risk.RiskStatus || 'N/A'}</span>`,
          assignedTo: risk.RiskOwner && risk.RiskOwner !== 'System Owner' && risk.RiskOwner !== 'System User' ? 
            risk.RiskOwner : 'Not Assigned',
          reviewer: risk.Reviewer || risk.ReviewerName || 'Not Assigned',
          reviewCount: risk.ReviewerCount || 0,
          actions: 'assign',
          originalRisk: risk // Keep reference to original risk data
        };
        
        sections[status].tasks.push(formattedRisk);
      });
      
      // Convert to array and sort by status priority
      return Object.values(sections).sort((a, b) => {
        const statusPriority = {
          'Assigned': 1,
          'In Progress': 2,
          'Pending': 3,
          'Open': 4,
          'Completed': 5,
          'Closed': 6,
          'Rejected': 7
        };
        return (statusPriority[a.name] || 999) - (statusPriority[b.name] || 999);
      });
    },
    // Dropdown configurations
    criticalityDropdownConfig() {
      return {
        label: 'Criticality',
        defaultValue: 'All Criticality',
        values: [
          { value: '', label: 'All Criticality' },
          ...this.uniqueCriticalities.map(criticality => ({
            value: criticality,
            label: criticality
          }))
        ]
      };
    },
    statusDropdownConfig() {
      return {
        label: 'Status',
        defaultValue: 'All Status',
        values: [
          { value: '', label: 'All Status' },
          ...this.uniqueStatuses.map(status => ({
            value: status,
            label: status
          }))
        ]
      };
    },
    assignedToDropdownConfig() {
      return {
        label: 'Assigned To',
        defaultValue: 'All Assigned To',
        values: [
          { value: '', label: 'All Assigned To' },
          ...this.uniqueAssignedUsers.map(user => ({
            value: user,
            label: user
          }))
        ]
      };
    },
    reviewerDropdownConfig() {
      return {
        label: 'Reviewer',
        defaultValue: 'All Reviewers',
        values: [
          { value: '', label: 'All Reviewers' },
          ...this.uniqueReviewers.map(reviewer => ({
            value: reviewer,
            label: reviewer
          }))
        ]
      };
    }
  },
  mounted() {
    // Reset all filters to default "All" values
    this.searchQuery = '';
    this.criticalityFilter = '';
    this.statusFilter = '';
    this.assignedToFilter = '';
    this.reviewerFilter = '';
    
    this.fetchRisks();
    this.fetchUsers();
  },
  created() {
    // Initialize filteredRisks with all risks that have completed scoring
    this.filteredRisks = this.risks;
  },
  methods: {
    fetchRisks() {
      axios.get('http://localhost:8000/api/risk-instances/')
        .then(response => {
          console.log('Risk data received:', response.data);
          
          // Log reviewer information for debugging
          if (response.data && response.data.length > 0) {
            response.data.forEach(risk => {
              console.log(`Risk ID: ${risk.RiskInstanceId}, Reviewer: ${risk.Reviewer || risk.ReviewerName || 'None'}, ReviewerId: ${risk.ReviewerId || 'None'}`);
            });
          }
          
          // First filter: Only include risks with completed scoring (Risk Impact, Risk Likelihood, Risk Exposure Rating)
          // and not rejected (Appetite is not 'No' and Status is not 'Rejected')
          // This is the base requirement for risks to appear in Risk Resolution
          const filteredRisks = response.data.filter(risk => {
            // Use helper methods to check if risk has completed scoring and is not rejected
            const hasScoring = this.hasCompletedScoring(risk);
            const isNotRejected = !this.isRiskRejected(risk);
            
            // Only include risks with complete scoring and not rejected
            return hasScoring && isNotRejected;
          });
          
          console.log(`Filtered ${response.data.length - filteredRisks.length} risks without complete scoring or rejected status`);
          
          this.risks = filteredRisks;
          this.filteredRisks = [...filteredRisks]; // Initialize filtered risks with all risks that have completed scoring
          this.loading = false;
          
          // Initialize expanded sections
          this.initializeExpandedSections();
        })
        .catch(error => {
          console.error('Error fetching risks:', error);
          this.error = `Failed to fetch risks: ${error.message}`;
          this.loading = false;
        });
    },
    fetchUsers() {
      // Based on the logs, the /api/users/ endpoint returns 401 Unauthorized
      // So we'll directly use the custom-users endpoint which is working
      axios.get('http://localhost:8000/api/custom-users/')
        .then(response => {
          console.log('User data received:', response.data);
          this.users = response.data;
          
          // Check if users were loaded correctly
          if (this.users && this.users.length > 0) {
            console.log(`Loaded ${this.users.length} users successfully`);
            console.log('Sample user data:', this.users[0]);
            
            // Debug each user's ID to ensure we're getting the right data
            this.users.forEach(user => {
              const userId = this.getUserId(user);
              console.log(`User: ${this.getUserName(user)}, ID: ${userId}, Type: ${typeof userId}`);
            });
          } else {
            console.warn('No users found or empty users array returned');
          }
        })
        .catch(error => {
          console.error('Error fetching users:', error);
          this.error = 'Failed to load user data. Please refresh the page or contact support.';
        });
    },
    filterRisks() {
      // Apply filters to all risks that already have complete scoring
      this.filteredRisks = this.risks.filter(risk => {
        // Search query filter
        const searchLower = this.searchQuery.toLowerCase();
        const matchesSearch = !this.searchQuery || 
          (risk.RiskInstanceId && risk.RiskInstanceId.toString().toLowerCase().includes(searchLower)) ||
          (risk.RiskTitle && risk.RiskTitle.toLowerCase().includes(searchLower)) ||
          (risk.Category && risk.Category.toLowerCase().includes(searchLower)) ||
          (risk.Criticality && risk.Criticality.toLowerCase().includes(searchLower)) ||
          (risk.RiskStatus && risk.RiskStatus.toLowerCase().includes(searchLower)) ||
          (risk.RiskDescription && risk.RiskDescription.toLowerCase().includes(searchLower));
        
        // Dropdown filters
        const matchesCriticality = !this.criticalityFilter || risk.Criticality === this.criticalityFilter;
        const matchesStatus = !this.statusFilter || risk.RiskStatus === this.statusFilter;
        
        // Assigned to filter
        const assignedTo = risk.RiskOwner && risk.RiskOwner !== 'System Owner' && risk.RiskOwner !== 'System User' ? 
          risk.RiskOwner : 'Not Assigned';
        const matchesAssignedTo = !this.assignedToFilter || assignedTo === this.assignedToFilter;
        
        // Reviewer filter
        const reviewer = risk.ReviewerName || 'Not Assigned';
        const matchesReviewer = !this.reviewerFilter || reviewer === this.reviewerFilter;
        
        return matchesSearch && matchesCriticality && matchesStatus && matchesAssignedTo && matchesReviewer;
      });
      
      console.log(`Applied filters: ${this.filteredRisks.length} risks displayed out of ${this.risks.length} total risks with completed scoring`);
    },
    initializeExpandedSections() {
      // Initialize all sections as expanded by default
      this.expandedSections = this.riskSections.map(() => true);
    },
    toggleSection(status) {
      this.expandedSections[status] = !this.expandedSections[status];
    },
    addTaskToSection(section) {
      // Implementation of adding a task to a section
      console.log('Adding task to section:', section);
    },
    openMitigationModal(taskOrId) {
      // Accept either a task object or an incidentId
      let incidentId = taskOrId;
      if (typeof taskOrId === 'object' && taskOrId !== null) {
        incidentId = taskOrId.incidentId;
      }
      let risk = null;
      for (const section of this.riskSections) {
        const task = section.tasks.find(task => task.incidentId === incidentId);
        if (task) {
          risk = task.originalRisk;
          break;
        }
      }
      
      if (!risk) {
        console.error('Risk not found for incidentId:', incidentId);
        return;
      }
      
      this.selectedRisk = risk;
      this.showMitigationModal = true;
      this.loadingMitigations = true;
      
      // Initialize user and reviewer selections if they exist
      if (risk.UserId) {
        this.selectedUsers[risk.RiskInstanceId] = risk.UserId;
      }
      if (risk.ReviewerId) {
        this.selectedReviewers[risk.RiskInstanceId] = risk.ReviewerId;
      }
      
      // First get the risk instance details to get mitigations
      axios.get(`http://localhost:8000/api/risk-instances/${risk.RiskInstanceId}/`)
        .then(response => {
          console.log('Risk instance data:', response.data);
          this.selectedRisk = response.data;
          
          // Check if there are mitigations in the risk instance data
          if (response.data.RiskMitigation) {
            let mitigations = [];
            const mitData = response.data.RiskMitigation;
            
            // Handle different mitigation data formats
            if (typeof mitData === 'string') {
              try {
                const parsed = JSON.parse(mitData);
                if (typeof parsed === 'object') {
                  // Convert object format to array format
                  Object.keys(parsed).forEach(key => {
                    mitigations.push({
                      description: parsed[key],
                      status: 'Not Started'
                    });
                  });
                }
              } catch (e) {
                // If not valid JSON, create a single step
                mitigations = [{
                  description: mitData,
                  status: 'Not Started'
                }];
              }
            } else if (typeof mitData === 'object' && !Array.isArray(mitData)) {
              // Convert object format to array format
              Object.keys(mitData).forEach(key => {
                mitigations.push({
                  description: mitData[key],
                  status: 'Not Started'
                });
              });
            } else if (Array.isArray(mitData)) {
              mitigations = mitData.map(step => ({
                description: typeof step === 'string' ? step : step.description,
                status: step.status || 'Not Started'
              }));
            }
            
            this.mitigationSteps = mitigations;
          } else {
            this.mitigationSteps = [];
          }
          
          this.loadingMitigations = false;
          
          // Set due date if it exists
          if (response.data.MitigationDueDate) {
            this.mitigationDueDate = response.data.MitigationDueDate;
          } else {
            // Set default due date to 7 days from today
            const date = new Date();
            date.setDate(date.getDate() + 7);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            this.mitigationDueDate = `${year}-${month}-${day}`;
          }
        })
        .catch(error => {
          console.error('Error fetching risk instance:', error);
          this.mitigationSteps = [];
          this.loadingMitigations = false;
          
          // Set default due date to 7 days from today
          const date = new Date();
          date.setDate(date.getDate() + 7);
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          this.mitigationDueDate = `${year}-${month}-${day}`;
        });
    },
    closeMitigationModal() {
      this.showMitigationModal = false;
      this.selectedRisk = {};
      this.mitigationSteps = [];
      this.newMitigationStep = '';
      this.mitigationDueDate = '';
      this.riskFormDetails = {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: '',
        operationalImpact: '',
        financialLoss: '',
        systemDowntime: '',
        recoveryTime: '',
        recurrencePossible: '',
        improvementInitiative: ''
      };
      this.viewOnlyMitigationModal = false;
    },
    parseMitigations(data) {
      // Convert different mitigation formats to our standard format
      if (!data || data.length === 0) {
        return [];
      }
      
      // If it's already an array of objects with descriptions
      if (Array.isArray(data) && data[0] && data[0].description) {
        return data.map(item => ({
          description: item.description || item.title || '',
          status: item.status || 'Not Started'
        }));
      }
      
      // If it's an array of strings or simple objects
      if (Array.isArray(data)) {
        return data.map((item, index) => ({
          description: typeof item === 'string' ? item : (item.description || item.title || `Step ${index + 1}`),
          status: item.status || 'Not Started'
        }));
      }
      
      // If it's an object with numbered keys (e.g., {"1": "Step 1", "2": "Step 2"})
      if (typeof data === 'object' && !Array.isArray(data)) {
        const steps = [];
        Object.keys(data).forEach(key => {
          const value = data[key];
          steps.push({
            description: typeof value === 'string' ? value : (value.description || value.title || `Step ${key}`),
            status: value.status || 'Not Started'
          });
        });
        return steps;
      }
      
      // Fallback: if it's a string, create a single step
      if (typeof data === 'string') {
        return [{
          description: data,
          status: 'Not Started'
        }];
      }
      
      return [];
    },
    addMitigationStep() {
      if (!this.newMitigationStep.trim()) return;
      
      this.mitigationSteps.push({
        description: this.newMitigationStep,
        status: 'Not Started'
      });
      
      this.newMitigationStep = '';
    },
    removeMitigationStep(index) {
      this.mitigationSteps.splice(index, 1);
    },
    assignRiskWithMitigations() {
      const riskId = this.selectedRisk.RiskInstanceId;
      const userId = this.selectedUsers[riskId];
      const reviewerId = this.selectedReviewers[riskId];
      
      // Convert IDs to numbers to ensure proper format
      // Handle null or undefined values
      if (!userId) {
        this.$popup.warning('No user selected. Please select a user to assign this risk to.');
        this.loading = false;
        return;
      }
      
      // if (!reviewerId) {
      //   this.$popup.warning('No reviewer selected. Please select a reviewer for this risk.');
      //   this.loading = false;
      //   return;
      // }
      
      const userIdNum = parseInt(userId, 10);
      const reviewerIdNum = parseInt(reviewerId, 10);
      
      console.log('Assigning risk with following IDs:', { 
        riskId, 
        userId: userIdNum, 
        reviewerId: reviewerIdNum 
      });
      
      if (!userIdNum || !reviewerIdNum || this.mitigationSteps.length === 0 || !this.mitigationDueDate) {
        // Show validation error
        if (!userIdNum) {
          this.$popup.warning('Please select a valid user to assign this risk to.');
          return;
        }
        if (!reviewerIdNum) {
          this.$popup.warning('Please select a valid reviewer for this risk.');
          return;
        }
        if (this.mitigationSteps.length === 0) {
          this.$popup.warning('Please add at least one mitigation step.');
          return;
        }
        if (!this.mitigationDueDate) {
          this.$popup.warning('Please select a due date for mitigation completion.');
          return;
        }
        return;
      }
      
      this.loading = true;
      
      // Convert mitigations to the expected JSON format
      // Format: {"1": "Description 1", "2": "Description 2", ...}
      const mitigationsJson = {};
      this.mitigationSteps.forEach((step, index) => {
        mitigationsJson[index + 1] = step.description;
      });
      
      console.log('Sending mitigation data:', mitigationsJson);
      console.log('User ID type:', typeof userIdNum, 'value:', userIdNum);
      console.log('Reviewer ID type:', typeof reviewerIdNum, 'value:', reviewerIdNum);
      
      // Log the exact payload we're sending to the API
      const assignPayload = {
        risk_id: parseInt(riskId, 10),
        UserId: userIdNum,
        mitigations: mitigationsJson,
        due_date: this.mitigationDueDate,
        risk_form_details: {} // Empty object instead of form details
      };
      console.log('Exact payload being sent to risk-assign API:', JSON.stringify(assignPayload));
      
      // First assign the risk to the user with mitigations
      axios.post('http://localhost:8000/api/risk-assign/', assignPayload, {
        // Add headers to ensure proper content type
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log('Assignment response:', response.data);
        
        // Now assign the reviewer - explicitly set create_approval_record to false
        const reviewerPayload = {
          risk_id: parseInt(riskId, 10),
          ReviewerId: reviewerIdNum,
          UserId: userIdNum,
          mitigations: mitigationsJson,
          risk_form_details: {}, // Empty object instead of form details
          create_approval_record: false // Explicitly set to false to prevent creating version entry
        };
        console.log('Exact payload being sent to assign-reviewer API:', JSON.stringify(reviewerPayload));
        
        return axios.post('http://localhost:8000/api/assign-reviewer/', reviewerPayload, {
          // Add headers to ensure proper content type
          headers: {
            'Content-Type': 'application/json'
          }
        });
      })
      .then(response => {
        console.log('Reviewer assignment response:', response.data);
        
        // Update the local risk data to show assignment
        const index = this.risks.findIndex(r => r.RiskInstanceId === riskId);
        if (index !== -1) {
          const assignedUser = this.users.find(u => this.getUserId(u) == userId);
          const assignedReviewer = this.users.find(u => this.getUserId(u) == reviewerId);
          
          // Make sure we have both user objects
          if (assignedUser && assignedReviewer) {
            this.risks[index].RiskOwner = this.getUserName(assignedUser);
            this.risks[index].UserId = userId;
            
            // Update both Reviewer and ReviewerName fields to ensure compatibility
            this.risks[index].ReviewerId = Number(reviewerId);
            this.risks[index].ReviewerName = this.getUserName(assignedReviewer);
            this.risks[index].Reviewer = this.getUserName(assignedReviewer);
            
            this.risks[index].RiskStatus = 'Assigned';
            this.risks[index].RiskMitigation = mitigationsJson;
            this.risks[index].MitigationDueDate = this.mitigationDueDate;
            this.risks[index].MitigationStatus = 'Yet to Start';
            this.risks[index].RiskFormDetails = {}; // Empty object instead of form details
          } else {
            console.error('Could not find assigned user or reviewer:', { userId, reviewerId });
          }
        }
        
        this.loading = false;
        this.closeMitigationModal();
        
        // Show success message
        this.$popup.success('Risk assigned successfully with mitigation steps and reviewer!');
      })
      .catch(error => {
        console.error('Error assigning risk:', error);
        this.loading = false;
        
        // Show more detailed error message
        let errorMessage = 'Failed to assign risk. ';
        
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorMessage += `Server error: ${error.response.status} - ${error.response.data.message || error.response.data || 'Unknown error'}`;
          console.error('Error response data:', error.response.data);
        } else if (error.request) {
          // The request was made but no response was received
          errorMessage += 'No response received from server. Please check your network connection.';
        } else {
          // Something happened in setting up the request that triggered an Error
          errorMessage += error.message || 'Unknown error occurred';
        }
        
        this.$popup.error(errorMessage);
      });
    },
    getCriticalityClass(criticality) {
      if (!criticality) return '';
      const level = criticality.toLowerCase();
      if (level.includes('high')) return 'high';
      if (level.includes('medium')) return 'medium';
      if (level.includes('low')) return 'low';
      if (level.includes('critical')) return 'critical';
      return '';
    },
    getPriorityClass(priority) {
      if (!priority) return '';
      const level = priority.toLowerCase();
      if (level.includes('high')) return 'high';
      if (level.includes('medium')) return 'medium';
      if (level.includes('low')) return 'low';
      return '';
    },
    getStatusClass(status) {
      if (!status) return 'pending';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('assigned') || statusLower.includes('in progress')) return 'in-progress';
      if (statusLower.includes('completed') || statusLower.includes('closed') || statusLower.includes('approved')) return 'completed';
      if (statusLower.includes('rejected')) return 'rejected';
      if (statusLower.includes('pending') || statusLower.includes('open')) return 'pending';
      return 'pending';
    },
    getRowClass(status) {
      if (!status) return '';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('approved')) return 'row-approved';
      if (statusLower.includes('review')) return 'row-review';
      return '';
    },
    getTodayDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    isFormComplete() {
      // Always return true since we're not requiring questionnaire completion here anymore
      return true;
    },
    isRiskRejected(risk) {
      // Helper method to check if a risk is rejected
      // Used in filtering risks for the resolution screen
      if (!risk) return false;
      
      const appetite = (risk.Appetite || '').toLowerCase();
      const status = (risk.RiskStatus || '').toLowerCase();
      
      return appetite === 'no' || status === 'rejected';
    },
    hasCompletedScoring(risk) {
      // Helper method to check if a risk has completed scoring
      // Used to determine if a risk should be displayed in the resolution screen
      if (!risk) return false;
      
      return (
        risk.RiskLikelihood !== undefined && 
        risk.RiskLikelihood !== null && 
        risk.RiskImpact !== undefined && 
        risk.RiskImpact !== null && 
        risk.RiskExposureRating !== undefined && 
        risk.RiskExposureRating !== null
      );
    },
    viewQuestionnaire(risk) {
      console.log("Viewing mitigation steps for risk:", risk.RiskInstanceId);
      
      axios.get(`http://localhost:8000/api/risk-instances/${risk.RiskInstanceId}/`)
        .then(response => {
          const data = response.data;
          this.selectedRisk = data;
          
          // Fetch mitigation steps
          axios.get(`http://localhost:8000/api/risk-mitigations/${risk.RiskInstanceId}/`)
            .then(mitResp => {
              console.log("Mitigation steps:", mitResp.data);
              this.mitigationSteps = this.parseMitigations(mitResp.data);
              
              // Show the mitigation modal in view-only mode
              this.showMitigationModal = true;
              this.viewOnlyMitigationModal = true;
              this.mitigationDueDate = data.MitigationDueDate || '';
              
              // --- Parse RiskFormDetails if it's a string ---
              let formDetails = data.RiskFormDetails;
              if (typeof formDetails === 'string') {
                try {
                  formDetails = JSON.parse(formDetails);
                } catch (e) {
                  formDetails = {};
                }
              }
              this.riskFormDetails = this.mapRiskFormDetails(formDetails);
            })
            .catch(error => {
              console.error("Error fetching mitigation steps:", error);
              // Fallback to risk mitigation data from risk object
              this.mitigationSteps = this.parseMitigations(data.RiskMitigation || {});
              
              // Show the mitigation modal in view-only mode
              this.showMitigationModal = true;
              this.viewOnlyMitigationModal = true;
              this.mitigationDueDate = data.MitigationDueDate || '';
              
              // --- Parse RiskFormDetails if it's a string ---
              let formDetails = data.RiskFormDetails;
              if (typeof formDetails === 'string') {
                try {
                  formDetails = JSON.parse(formDetails);
                } catch (e) {
                  formDetails = {};
                }
              }
              this.riskFormDetails = this.mapRiskFormDetails(formDetails);
            });
        })
        .catch(error => {
          console.error("Error fetching risk details:", error);
          this.$popup.error('Failed to fetch risk details');
        });
    },
    closeQuestionnaireModal() {
      this.showQuestionnaireModal = false;
      this.selectedQuestionnaire = null;
    },
    mapRiskFormDetails(details) {
      if (!details) return {
        cost: '', impact: '', financialImpact: '', reputationalImpact: '', operationalImpact: '', financialLoss: '', systemDowntime: '', recoveryTime: '', recurrencePossible: '', improvementInitiative: ''
      };
      // Normalize Yes/No/Unknown for selects
      function normalizeYN(val) {
        if (!val) return '';
        if (typeof val === 'string') {
          if (val.toLowerCase() === 'yes') return 'Yes';
          if (val.toLowerCase() === 'no') return 'No';
          if (val.toLowerCase() === 'unknown') return 'Unknown';
        }
        return val;
      }
      return {
        cost: details.cost ?? '',
        impact: details.impact ?? '',
        financialImpact: details.financialImpact ?? details.financialimpact ?? '',
        reputationalImpact: details.reputationalImpact ?? details.reputationalimpact ?? '',
        operationalImpact: details.operationalImpact ?? details.operationalimpact ?? '',
        financialLoss: details.financialLoss ?? details.financialloss ?? '',
        systemDowntime: details.systemDowntime ?? details.expecteddowntime ?? '',
        recoveryTime: details.recoveryTime ?? details.recoverytime ?? '',
        recurrencePossible: normalizeYN(details.recurrencePossible ?? details.riskrecurrence),
        improvementInitiative: normalizeYN(details.improvementInitiative ?? details.improvementinitiative)
      };
    },
    
    // Helper methods to handle different user data structures
    getUserId(user) {
      // Handle different possible user object structures
      if (!user) return '';
      
      // Django Users model structure
      if (user.UserId !== undefined) return parseInt(user.UserId, 10);
      
      // Custom users API structure
      if (user.user_id !== undefined) return parseInt(user.user_id, 10);
      
      // Django auth User model structure
      if (user.id !== undefined) return parseInt(user.id, 10);
      
      // Fallback - try to parse any available ID field
      const id = user.id || user.UserId || user.user_id || '';
      return id ? parseInt(id, 10) : '';
    },
    
    getUserName(user) {
      // Handle different possible user object structures
      if (!user) return 'Unknown User';
      
      // Django Users model structure
      if (user.UserName) {
        return user.UserName + (user.email ? ` (${user.email})` : '');
      }
      
      // Custom users API structure
      if (user.user_name) {
        let displayName = user.user_name;
        if (user.department || user.designation) {
          displayName += ' (';
          if (user.department) displayName += user.department;
          if (user.department && user.designation) displayName += ', ';
          if (user.designation) displayName += user.designation;
          displayName += ')';
        }
        return displayName;
      }
      
      // Django auth User model structure
      if (user.username) {
        return user.first_name && user.last_name 
          ? `${user.first_name} ${user.last_name} (${user.username})` 
          : user.username;
      }
      
      // Fallback
      return user.UserName || user.user_name || user.username || user.email || 'User ' + this.getUserId(user);
    },
    navigateTo(screen) {
      // Remove active class from all buttons
      const buttons = document.querySelectorAll('.risk-resolution-toggle-button');
      buttons.forEach(button => button.classList.remove('active'));
      
      // Add active class to the clicked button
      const clickedButton = Array.from(buttons).find(button => 
        button.textContent.trim().toLowerCase().includes(screen)
      );
      if (clickedButton) clickedButton.classList.add('active');
      
      // Navigate to the appropriate screen
      switch(screen) {
        case 'resolution':
          // Already on resolution page
          break;
        case 'workflow':
          this.$router.push('/risk/workflow');
          break;
      }
    }
  }
}
</script>

<style scoped>
/* Import the CSS file */
@import './RiskResolution.css';

/* Add additional styles for the section title */
.section-title {
  margin: 20px 0;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
}

/* Enhance the toggle buttons styling */
.risk-resolution-toggle-buttons {
  display: flex;
  background: #f8f9fa;
  border-radius: 50px;
  overflow: hidden;
  width: fit-content;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin: 30px auto;
}

.risk-resolution-toggle-button {
  padding: 12px 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #555;
  transition: all 0.3s ease;
  position: relative;
  outline: none;
  min-width: 180px;
  text-align: center;
}

.risk-resolution-toggle-button:not(:last-child) {
  border-right: 1px solid #eee;
}

.risk-resolution-toggle-button:hover {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.risk-resolution-toggle-button.active {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
}

/* Style for selected user info */
.risk-resolution-selected-user-info {
  margin-top: 5px;
  font-size: 0.85rem;
  color: #666;
  background-color: #f5f5f5;
  padding: 3px 8px;
  border-radius: 4px;
  border-left: 3px solid #3498db;
}
</style> 