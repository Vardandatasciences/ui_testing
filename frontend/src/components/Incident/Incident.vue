<template>
  <div class="incident-view-container">
    <div class="incident-view-header">
      <h2 class="incident-view-title">Incident Management</h2>
      <div class="incident-header-actions">
        <!-- Export controls -->
        <div class="incident-export-controls">
          <select v-model="exportFormat" class="incident-export-format-select">
            <option value="xlsx">Excel (.xlsx)</option>
            <option value="csv">CSV (.csv)</option>
            <option value="pdf">PDF (.pdf)</option>
            <option value="json">JSON (.json)</option>
            <option value="xml">XML (.xml)</option>
            <option value="txt">Text (.txt)</option>
          </select>
          <button @click="exportIncidents" class="incident-export-btn" :disabled="isExporting">
            <span v-if="isExporting">Exporting...</span>
            <span v-else>Export</span>
          </button>
        </div>
      </div>
    </div>
    
    <div class="incident-list-wrapper">
      <!-- Search and Filter Section -->
      <div class="incident-filter-controls">
        <div class="incident-filter-group">
          <!-- Search Section -->
          <div class="incident-search-section">
            <label class="incident-search-label">Search Incidents:</label>
            <div class="incident-search-container">
              <i class="fas fa-search incident-search-icon"></i>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search by ID, title, origin, priority, category, or status..." 
                class="incident-search-input"
                @input="filterIncidents"
                @keyup.enter="performSearch"
              />
              <button 
                v-if="searchQuery" 
                @click.stop="clearSearch" 
                class="incident-search-clear-btn"
                title="Clear search"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          
          <!-- Sort Section -->
          <div class="incident-sort-section">
            <label class="incident-sort-label">Sort:</label>
            <div class="incident-sort-filter">
              <select v-model="sortField" @change="sortIncidents" class="incident-sort-select">
                <option value="">Sort by</option>
                <option value="IncidentId">ID</option>
                <option value="IncidentTitle">Title</option>
                <option value="Date">Date</option>
                <option value="RiskPriority">Priority</option>
                <option value="Origin">Origin</option>
              </select>
              <button @click="toggleSortOrder" class="incident-sort-direction-btn" :class="{ 'incident-active-sort': sortField }">
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Dynamic Table -->
      <DynamicTable
        :data="incidents"
        :columns="tableColumns"
        :uniqueKey="'IncidentId'"
        :showActions="true"
        :showPagination="true"
        :pageSizeOptions="[10, 20, 50]"
        :defaultPageSize="10"
      >
        <!-- Custom cell slots -->
        <template #cell-IncidentTitle="{ row }">
          <router-link :to="`/incident/${row.IncidentId}`" class="incident-title-link">
            {{ row.IncidentTitle }}
          </router-link>
        </template>

        <template #cell-Origin="{ row }">
          <span :class="['incident-origin-badge', getOriginClass(row.Origin)]">
            {{ row.Origin }}
          </span>
        </template>

        <template #cell-RiskPriority="{ row }">
          <span :class="['incident-priority-badge', getPriorityClass(row.RiskPriority)]">
            {{ row.RiskPriority }}
          </span>
        </template>

        <template #cell-Date="{ row }">
          {{ formatDate(row.Date) }}
        </template>

        <!-- Actions slot -->
        <template #actions="{ row }">
          <!-- Handle all possible status values -->
          <div v-if="row.Status === 'Scheduled'">
            <span class="incident-status-badge incident-mitigated">Mitigated to Risk</span>
          </div>
          <div v-else-if="row.Status === 'Rejected'">
            <span class="incident-status-badge incident-rejected" :data-source="row.RejectionSource || 'INCIDENT'">
              {{ row.RejectionSource === 'RISK' ? 'Rejected from Risk' : 'Rejected as Incident' }}
            </span>
          </div>
          <div v-else-if="row.Status === 'Assigned'">
            <span class="incident-status-badge incident-assigned">Assigned</span>
          </div>
          <div v-else-if="row.Status === 'Approved'">
            <span class="incident-status-badge incident-approved">Approved</span>
          </div>
          <div v-else-if="row.Status === 'Active'">
            <span class="incident-status-badge incident-active">Active</span>
          </div>
          <div v-else-if="row.Status === 'Under Review'">
            <span class="incident-status-badge incident-under-review">Under Review</span>
          </div>
          <div v-else-if="row.Status === 'Completed'">
            <span class="incident-status-badge incident-completed">Completed</span>
          </div>
          <div v-else-if="row.Status === 'Closed'">
            <span class="incident-status-badge incident-closed">Closed</span>
          </div>
          <div v-else-if="row.Status === 'Open' || !row.Status || row.Status.trim() === ''">
            <!-- Action Dropdown for Open incidents -->
            <div class="incident-action-dropdown-container" :class="{ 'dropdown-open': dropdownOpenFor === row.IncidentId }">
              <!-- Hand Pointer Indicator -->
              <div class="incident-action-indicator">
                <i class="fas fa-hand-point-right incident-hand-pointer"></i>
              </div>
              
              <button 
                @click.stop="toggleActionDropdown(row.IncidentId)"
                class="incident-action-dropdown-trigger"
                :class="{ 'active': dropdownOpenFor === row.IncidentId }"
              >
                <i class="fas fa-cog incident-dropdown-icon incident-rotating-gear"></i>
                <span>Actions</span>
                <i class="fas fa-chevron-down incident-dropdown-arrow" :class="{ 'incident-rotated': dropdownOpenFor === row.IncidentId }"></i>
              </button>
              
              <div 
                v-show="dropdownOpenFor === row.IncidentId"
                class="incident-action-dropdown-menu"
                @click.stop
              >
                <div class="incident-dropdown-item incident-assign-item" @click.stop="handleDropdownAction('assign', row)">
                  <i class="fas fa-user-plus"></i>
                  <span>Assign as Incident</span>
                </div>
                <div class="incident-dropdown-item incident-escalate-item" @click.stop="handleDropdownAction('escalate', row)">
                  <i class="fas fa-arrow-up"></i>
                  <span>Escalate to Risk</span>
                </div>
                <div class="incident-dropdown-item incident-reject-item" @click.stop="handleDropdownAction('reject', row)">
                  <i class="fas fa-times"></i>
                  <span>Reject Incident</span>
                </div>
                <!-- Show message if no permissions -->
                <div 
                  v-if="!canAssignIncident() && !canEscalateIncident() && !canEditIncident()" 
                  class="dropdown-item no-permission"
                >
                  <i class="fas fa-lock"></i>
                  <span>No actions available</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="row.Status && row.Status.trim() !== ''">
            <!-- Show any other status that exists -->
            <span class="incident-status-badge incident-other-status">{{ row.Status }}</span>
          </div>
        </template>
      </DynamicTable>
    </div>
    
    <!-- Modal for Solve/Reject -->
    <div v-if="showModal && modalAction !== 'assign'" class="incident-modal-overlay" @click="closeModal">
      <div class="incident-modal-container" @click.stop>
        <button class="incident-modal-close-btn" @click="closeModal">✕</button>
        <div class="incident-modal-content">
          <div v-if="modalAction === 'solve'" class="incident-solve-container">
            <div class="incident-solve-icon">🔄</div>
            <h3 class="incident-modal-title incident-solve">Forwarded to Risk</h3>
            <p class="incident-modal-subtitle">You will be directed to the Risk module</p>
            <div class="incident-modal-footer">
              <button @click="confirmSolve" class="incident-modal-btn incident-confirm-btn">Confirm Forward</button>
              <button @click="closeModal" class="incident-modal-btn incident-cancel-btn">Cancel</button>
            </div>
          </div>
          
          <div v-else-if="modalAction === 'reject'" class="incident-rejected-container">
            <div class="incident-rejected-icon">✕</div>
            <h3 class="incident-modal-title incident-rejected">REJECTED</h3>
            <div class="incident-modal-footer">
              <button @click="confirmReject" class="incident-modal-btn incident-reject-btn">Confirm Reject</button>
              <button @click="closeModal" class="incident-modal-btn incident-cancel-btn">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assignment Workflow Section -->
    <div v-if="showAssignmentWorkflow" class="incident-assignment-workflow-section">
      <div class="incident-assignment-header">
        <button class="incident-back-btn" @click="closeAssignmentWorkflow">
          <i class="fas fa-arrow-left"></i> Back to Incidents
        </button>
      </div>
      <div class="assignment-body">
        <div class="incident-summary">
          <h3>{{ selectedIncident.IncidentTitle || 'Incident #' + selectedIncident.IncidentId }}</h3>
          <div class="incident-details">
            <p><strong>ID:</strong> {{ selectedIncident.IncidentId }}</p>
            <p><strong>Category:</strong> {{ selectedIncident.RiskCategory }}</p>
            <p><strong>Priority:</strong> {{ selectedIncident.RiskPriority }}</p>
            <p><strong>Origin:</strong> {{ selectedIncident.Origin }}</p>
          </div>
        </div>

        <!-- User Selection -->
        <div class="incident-user-selection">
          <h3>Assignment Details</h3>
          <div class="incident-user-form">
              <div class="incident-form-group">
                <label for="assigner">Assigner:</label>
                <select v-model="selectedAssigner" id="assigner" class="incident-assign-select" required>
                  <option value="">Select Assigner</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.role }})
                  </option>
                </select>
              </div>
              
              <div class="incident-form-group">
                <label for="reviewer">Reviewer:</label>
                <select v-model="selectedReviewer" id="reviewer" class="incident-assign-select" required>
                  <option value="">Select Reviewer</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.role }})
                  </option>
                </select>
            </div>
          </div>
        </div>
        
        <!-- Mitigation Workflow -->
        <div class="incident-mitigation-workflow">
          <h3>Mitigation Steps</h3>
          <!-- Existing Mitigation Steps -->
          <div v-if="mitigationSteps.length" class="incident-workflow-timeline">
            <div v-for="(step, index) in mitigationSteps" :key="index" class="incident-workflow-step">
              <div class="incident-step-number">{{ index + 1 }}</div>
              <div class="incident-step-content">
                <textarea 
                  v-model="step.description" 
                  class="incident-mitigation-textarea"
                  placeholder="Enter mitigation step description"
                ></textarea>
                <div class="incident-step-actions">
                  <button @click="removeMitigationStep(index)" class="incident-remove-step-btn">
                    <i class="fas fa-trash"></i> Remove
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="incident-no-mitigations">
            <p>No mitigation steps found for this incident. Add steps below.</p>
          </div>
          
          <!-- Add New Mitigation Step -->
          <div class="incident-add-mitigation">
            <textarea 
              v-model="newMitigationStep" 
              class="incident-mitigation-textarea"
              placeholder="Enter mitigation step(s). Use commas to separate multiple steps (e.g., 'Step 1, Step 2, Step 3')"
            ></textarea>
            <button @click="addMitigationStep" class="incident-add-step-btn" :disabled="!newMitigationStep.trim()">
              <i class="fas fa-plus"></i> Add Mitigation Step
            </button>
          </div>
          
          <!-- Due Date Input -->
          <div class="incident-due-date-section">
            <h4>Due Date for Mitigation Completion</h4>
            <input 
              type="date" 
              v-model="mitigationDueDate" 
              class="incident-due-date-input" 
              :min="getTodayDate()"
            />
          </div>

          <!-- Assignment Notes -->
          <div class="incident-assignment-notes-section">
            <h4>Assignment Notes (Optional)</h4>
                <textarea 
                  v-model="assignmentNotes" 
              class="incident-assignment-notes-textarea"
                  placeholder="Add any specific instructions or notes for the assignees..."
                  rows="3"
                ></textarea>
            </div>
            
          <!-- Submit Section -->
          <div class="incident-assignment-actions">
              <button 
              @click="confirmAssignmentWorkflow" 
              class="incident-submit-assignment-btn"
              :disabled="!selectedAssigner || !selectedReviewer || mitigationSteps.length === 0 || !mitigationDueDate"
              >
              <i class="fas fa-user-plus"></i> Assign Incident with Mitigations
              </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Popup Modal -->
  <PopupModal />
</template>

<script>
import axios from 'axios';
import './Incident.css';
import { PopupService, PopupModal } from '@/modules/popup';
import { permissionMixin } from '@/mixins/permissionMixin.js';
import DynamicTable from '@/components/DynamicTable.vue';

export default {
  name: 'IncidentManagement',
  components: {
    PopupModal,
    DynamicTable
  },
  mixins: [permissionMixin],
  data() {
    return {
      incidents: [],
      filteredIncidents: [],
      searchQuery: '',
      sortField: '',
      sortOrder: 'asc',
      searchTimeout: null,
      isLoadingIncidents: false,
      currentPage: 1,
      incidentsPerPage: 10,
      showModal: false,
      modalAction: '', // 'solve', 'reject', or 'assign'
      selectedIncident: null,
      exportFormat: 'xlsx',
      isExporting: false,
      // Assignment related data
      selectedAssigner: '',
      selectedReviewer: '',
      assignmentNotes: '',
      availableUsers: [],
      // Assignment workflow data
      showAssignmentWorkflow: false,
      mitigationSteps: [],
      newMitigationStep: '',
      mitigationDueDate: '',
      // Dropdown state
      dropdownOpenFor: null,
      // Table configuration
      tableColumns: [
        {
          key: 'IncidentId',
          label: 'ID',
          sortable: true,
          headerClass: 'incident-header-cell id-header',
          cellClass: 'incident-table-cell incident-id-cell',
          width: '50px'
        },
        {
          key: 'IncidentTitle',
          label: 'Title',
          sortable: true,
          headerClass: 'incident-header-cell title-header',
          cellClass: 'incident-table-cell incident-title-cell',
          slot: true,
          width: 'auto'
        },
        {
          key: 'Origin',
          label: 'Origin',
          sortable: true,
          headerClass: 'incident-header-cell origin-header',
          cellClass: 'incident-table-cell incident-origin-cell',
          slot: true,
          width: '100px'
        },
        {
          key: 'RiskPriority',
          label: 'Priority',
          sortable: true,
          headerClass: 'incident-header-cell priority-header',
          cellClass: 'incident-table-cell incident-priority-cell',
          slot: true,
          width: '90px'
        },
        {
          key: 'Date',
          label: 'Date',
          sortable: true,
          headerClass: 'incident-header-cell date-header',
          cellClass: 'incident-table-cell incident-date-cell',
          slot: true,
          width: '90px'
        }
      ]
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.filteredIncidents.length / this.incidentsPerPage);
    },
    paginatedIncidents() {
      const startIndex = (this.currentPage - 1) * this.incidentsPerPage;
      const endIndex = startIndex + this.incidentsPerPage;
      return this.filteredIncidents.slice(startIndex, endIndex);
    },
    pageNumbers() {
      const pages = [];
      // Show max 5 page numbers
      let startPage = Math.max(1, this.currentPage - 2);
      let endPage = Math.min(this.totalPages, startPage + 4);
      
      // Adjust if we're near the end
      if (endPage - startPage < 4 && this.totalPages > 5) {
        startPage = Math.max(1, endPage - 4);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      return pages;
    }
  },
  watch: {
    incidents: {
      handler(newIncidents) {
        console.log('Incidents array updated. Current statuses:', 
          newIncidents.slice(0, 5).map(inc => ({ id: inc.IncidentId, status: inc.Status }))
        );
      },
      deep: true
    }
  },
  mounted() {
    console.log('Incident component mounted - fetching incidents from database...');
    this.fetchIncidents();
    this.fetchUsers();
    // Ensure the main document scrolls to see all checklist data
    document.documentElement.style.overflow = 'auto';
    document.body.style.overflow = 'auto';
    
    // Add resize event listener to handle responsive behavior
    window.addEventListener('resize', this.handleResize);
    
    // Add click event listener to close dropdowns when clicking outside
    document.addEventListener('click', this.closeAllDropdowns);
  },
  beforeUnmount() {
    // Clean up event listeners
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('click', this.closeAllDropdowns);
        },
    methods: {
      // Dropdown methods
      toggleActionDropdown(incidentId) {
        console.log('Toggle dropdown for incident:', incidentId);
        console.log('Current dropdownOpenFor:', this.dropdownOpenFor);
        
        if (this.dropdownOpenFor === incidentId) {
          this.dropdownOpenFor = null;
        } else {
          this.dropdownOpenFor = incidentId;
        }
        
        console.log('New dropdownOpenFor:', this.dropdownOpenFor);
      },
      closeAllDropdowns(event) {
        // Only close if clicking outside the dropdown
        if (event && event.target) {
          const isDropdownClick = event.target.closest('.action-dropdown-container');
          if (isDropdownClick) {
            return; // Don't close if clicking inside dropdown
          }
        }
        
        console.log('Closing all dropdowns');
        this.dropdownOpenFor = null;
      },
      handleDropdownAction(action, incident) {
        console.log('Dropdown action:', action, 'for incident:', incident.IncidentId);
        
        // RBAC Debug - Log user action attempt
        this.logUserAction(`INCIDENT_${action.toUpperCase()}`, 'incident', incident.IncidentId);
        
        // Check permissions before allowing action
        let hasPermission = false;
        switch(action) {
          case 'assign':
            hasPermission = this.canAssignIncident();
            break;
          case 'escalate':
            hasPermission = this.canEscalateIncident();
            break;
          case 'reject':
            hasPermission = this.canEditIncident();
            break;
        }
        
        if (!hasPermission) {
          console.warn(`❌ Permission denied for action: ${action}`);
          PopupService.error(`You don't have permission to ${action} incidents`);
          this.dropdownOpenFor = null;
          return;
        }
        
        console.log(`✅ Permission granted for action: ${action}`);
        this.dropdownOpenFor = null; // Close dropdown
        
        switch(action) {
          case 'assign':
            this.openAssignModal(incident);
            break;
          case 'escalate':
            this.openSolveModal(incident);
            break;
          case 'reject':
            this.openRejectModal(incident);
            break;
        }
      },
      openSolveModal(incident) {
      this.selectedIncident = incident;
      this.modalAction = 'solve';
      this.showModal = true;
    },
    openRejectModal(incident) {
      this.selectedIncident = incident;
      this.modalAction = 'reject';
      this.showModal = true;
    },
    openAssignModal(incident) {
      this.selectedIncident = incident;
      this.showAssignmentWorkflow = true;
      // Reset assignment form
      this.selectedAssigner = '';
      this.selectedReviewer = '';
      this.assignmentNotes = '';
      this.newMitigationStep = '';
      this.mitigationDueDate = '';
      
      // Load existing mitigation steps from the incident's Mitigation field
      console.log('Selected incident:', incident);
      console.log('Incident Mitigation field:', incident.Mitigation);
      this.loadExistingMitigations(incident);
    },
    closeModal() {
      this.showModal = false;
      this.selectedIncident = null;
      // Reset assignment form data
      this.selectedAssigner = '';
      this.selectedReviewer = '';
      this.assignmentNotes = '';
    },
    closeAssignmentWorkflow() {
      this.showAssignmentWorkflow = false;
      this.selectedIncident = null;
      // Reset assignment form data
      this.selectedAssigner = '';
      this.selectedReviewer = '';
      this.assignmentNotes = '';
      this.mitigationSteps = [];
      this.newMitigationStep = '';
      this.mitigationDueDate = '';
    },
    addMitigationStep() {
      if (!this.newMitigationStep.trim()) return;
      
      // Check if the user entered multiple steps separated by commas
      const steps = this.newMitigationStep.split(',').filter(step => step.trim());
      
      if (steps.length > 1) {
        // Multiple comma-separated steps
        steps.forEach(step => {
          this.mitigationSteps.push({
            description: step.trim(),
            status: 'Not Started'
          });
        });
      } else {
        // Single step
        this.mitigationSteps.push({
          description: this.newMitigationStep.trim(),
          status: 'Not Started'
        });
      }
      
      this.newMitigationStep = '';
    },
    removeMitigationStep(index) {
      this.mitigationSteps.splice(index, 1);
    },
    getTodayDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    loadExistingMitigations(incident) {
      // Initialize with empty array
      this.mitigationSteps = [];
      
      // Check if incident has existing mitigation data
      if (incident.Mitigation) {
        try {
          let mitigationData = incident.Mitigation;
          
          // If it's a string, try to parse it as JSON
          if (typeof mitigationData === 'string') {
            // Check if it's JSON format
            if (mitigationData.trim().startsWith('{') || mitigationData.trim().startsWith('[')) {
              try {
                mitigationData = JSON.parse(mitigationData);
              } catch (e) {
                // If JSON parsing fails, treat as plain text
                console.log('Mitigation data is not JSON, treating as plain text');
              }
            }
          }
          
          // Handle different mitigation data formats
          if (typeof mitigationData === 'string') {
            // Plain text - split by lines, commas, or use as single step
            let steps = [];
            
            // First try splitting by newlines
            const lineSteps = mitigationData.split('\n').filter(step => step.trim());
            
            if (lineSteps.length > 1) {
              // Multiple lines found, use line separation
              steps = lineSteps;
            } else {
              // Single line or no newlines, try splitting by commas
              const commaSteps = mitigationData.split(',').filter(step => step.trim());
              if (commaSteps.length > 1) {
                // Multiple comma-separated items found
                steps = commaSteps;
              } else {
                // Single step
                steps = [mitigationData];
              }
            }
            
            this.mitigationSteps = steps.map((step) => ({
              description: step.trim(),
              status: 'Not Started'
            }));
          } else if (Array.isArray(mitigationData)) {
            // Array format
            this.mitigationSteps = mitigationData.map(item => ({
              description: typeof item === 'string' ? item : (item.description || item.title || 'Mitigation step'),
              status: item.status || 'Not Started'
            }));
          } else if (typeof mitigationData === 'object') {
            // Object format (like {"1": "Step 1", "2": "Step 2"})
            this.mitigationSteps = Object.values(mitigationData).map(step => ({
              description: typeof step === 'string' ? step : (step.description || step.title || 'Mitigation step'),
              status: step.status || 'Not Started'
            }));
          }
          
          console.log('Loaded existing mitigation steps:', this.mitigationSteps);
        } catch (error) {
          console.error('Error parsing mitigation data:', error);
          // Fallback: treat as plain text
          this.mitigationSteps = [{
            description: incident.Mitigation,
            status: 'Not Started'
          }];
        }
      }
      
      // If no mitigation steps were loaded, start with empty array
      if (this.mitigationSteps.length === 0) {
        console.log('No existing mitigation steps found');
      }
    },
    confirmAssignmentWorkflow() {
      // Validate selections
      if (!this.selectedAssigner || !this.selectedReviewer) {
        PopupService.warning('Please select both assigner and reviewer');
        return;
      }

      if (this.selectedAssigner === this.selectedReviewer) {
        PopupService.warning('Assigner and reviewer cannot be the same person');
        return;
      }

      if (this.mitigationSteps.length === 0) {
        PopupService.warning('Please add at least one mitigation step');
        return;
      }

      if (!this.mitigationDueDate) {
        PopupService.warning('Please select a due date');
        return;
      }

      console.log('Assigning incident:', this.selectedIncident.IncidentId);

      // Find user details
      const assigner = this.availableUsers.find(user => user.id === this.selectedAssigner);
      const reviewer = this.availableUsers.find(user => user.id === this.selectedReviewer);

      // Convert mitigations to the expected JSON format
      const mitigationsJson = {};
      this.mitigationSteps.forEach((step, index) => {
        mitigationsJson[index + 1] = step.description;
      });

      // Update incident with assignment details and mitigations
      axios.put(`http://localhost:8000/api/incidents/${this.selectedIncident.IncidentId}/assign/`, {
        status: 'Assigned',
        assigner_id: this.selectedAssigner,
        assigner_name: assigner.name,
        reviewer_id: this.selectedReviewer,
        reviewer_name: reviewer.name,
        assignment_notes: this.assignmentNotes,
        assigned_date: new Date().toISOString(),
        mitigations: mitigationsJson,
        due_date: this.mitigationDueDate
      })
      .then(response => {
        console.log('Incident assigned successfully - API response:', response.data);
        
        // Immediately update the local incident object for instant UI feedback
        const incident = this.incidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (incident) {
          incident.Status = 'Assigned';
          incident.AssignerId = this.selectedAssigner;
          incident.ReviewerId = this.selectedReviewer;
          console.log('Updated local incident status to Assigned');
        }
        
        // Update filtered incidents as well
        const filteredIncident = this.filteredIncidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (filteredIncident) {
          filteredIncident.Status = 'Assigned';
          filteredIncident.AssignerId = this.selectedAssigner;
          filteredIncident.ReviewerId = this.selectedReviewer;
        }
        
        // Refresh incidents list after assignment for data consistency
        this.fetchIncidents();
        
        // Show success message and close workflow
        PopupService.success('Incident assigned successfully with mitigation steps!');
        this.closeAssignmentWorkflow();
      })
      .catch(error => {
        console.error('Error assigning incident:', error);
        PopupService.error('Failed to assign incident. Please try again.');
      });
    },
    confirmSolve() {
      console.log('Escalating incident to risk:', this.selectedIncident.IncidentId);
      
      // Update incident status to "Scheduled"
      axios.put(`http://localhost:8000/api/incidents/${this.selectedIncident.IncidentId}/status/`, {
        status: 'Scheduled'
      })
      .then(response => {
        console.log('Incident escalated to risk - API response:', response.data);
        
        // Show success popup
        PopupService.success(`Incident #${this.selectedIncident.IncidentId} has been successfully escalated to Risk Management for further evaluation and mitigation.`);
        
        // Immediately update the local incident object for instant UI feedback
        const incident = this.incidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (incident) {
          incident.Status = 'Scheduled';
          console.log('Updated local incident status to Scheduled');
        }
        
        // Update filtered incidents as well
        const filteredIncident = this.filteredIncidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (filteredIncident) {
          filteredIncident.Status = 'Scheduled';
        }
        
        // Refresh incidents list after status update for data consistency
        this.fetchIncidents();
        
        // Auto close modal after 2 seconds to allow user to see the success message
        setTimeout(() => {
          this.closeModal();
          // Redirect to Risk module
          // this.$router.push('/risk');
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating incident status:', error);
        PopupService.error('Failed to escalate incident. Please try again.');
      });
    },
    confirmReject() {
      console.log('Rejecting incident:', this.selectedIncident.IncidentId);
      
      // Update incident status to "Rejected"
      axios.put(`http://localhost:8000/api/incidents/${this.selectedIncident.IncidentId}/status/`, {
        status: 'Rejected',
        rejection_source: 'INCIDENT'
      })
      .then(response => {
        console.log('Incident rejected - API response:', response.data);
        
        // Immediately update the local incident object for instant UI feedback
        const incident = this.incidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (incident) {
          incident.Status = 'Rejected';
          incident.RejectionSource = 'INCIDENT';
          console.log('Updated local incident status to Rejected');
        }
        
        // Update filtered incidents as well
        const filteredIncident = this.filteredIncidents.find(inc => inc.IncidentId === this.selectedIncident.IncidentId);
        if (filteredIncident) {
          filteredIncident.Status = 'Rejected';
          filteredIncident.RejectionSource = 'INCIDENT';
        }
        
        // Refresh incidents list after status update for data consistency
        this.fetchIncidents();
        
        // Auto close the modal after 2 seconds
        setTimeout(() => {
          this.closeModal();
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating incident status:', error);
        PopupService.error('Failed to reject incident. Please try again.');
      });
    },
    confirmAssign() {
      // Validate selections
      if (!this.selectedAssigner || !this.selectedReviewer) {
        PopupService.warning('Please select both assigner and reviewer');
        return;
      }

      if (this.selectedAssigner === this.selectedReviewer) {
        PopupService.warning('Assigner and reviewer cannot be the same person');
        return;
      }

      // Find user details
      const assigner = this.availableUsers.find(user => user.id === this.selectedAssigner);
      const reviewer = this.availableUsers.find(user => user.id === this.selectedReviewer);

      // Update incident with assignment details
      axios.put(`http://localhost:8000/api/incidents/${this.selectedIncident.IncidentId}/assign/`, {
        status: 'Assigned',
        assigner_id: this.selectedAssigner,
        assigner_name: assigner.name,
        reviewer_id: this.selectedReviewer,
        reviewer_name: reviewer.name,
        assignment_notes: this.assignmentNotes,
        assigned_date: new Date().toISOString()
      })
      .then(response => {
        console.log('Incident assigned successfully:', response.data);
        // Refresh incidents list after assignment
        this.fetchIncidents();
        
        // Show success message and close modal
        setTimeout(() => {
          this.closeModal();
        }, 1500);
      })
      .catch(error => {
        console.error('Error assigning incident:', error);
        PopupService.error('Failed to assign incident. Please try again.');
      });
    },
    getRiskCategoryClass(category) {
      if (!category) return '';
      const categoryLower = category.toLowerCase();
      if (categoryLower.includes('security')) return 'category-security';
      if (categoryLower.includes('compliance')) return 'category-compliance';
      if (categoryLower.includes('operational')) return 'category-operational';
      if (categoryLower.includes('financial')) return 'category-financial';
      if (categoryLower.includes('strategic')) return 'category-strategic';
      return 'category-other';
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        // Scroll to top of container when changing pages
        const container = document.querySelector('.incident-list-wrapper');
        if (container) {
          container.scrollTop = 0;
          window.scrollTo({ top: container.offsetTop, behavior: 'smooth' });
        }
      }
    },
    getStatusClass(priority) {
      const priorityLower = priority?.toLowerCase() || '';
      if (priorityLower === 'high') return 'status-active';
      if (priorityLower === 'medium') return 'status-medium';
      if (priorityLower === 'low') return 'status-inactive';
      return 'status-default';
    },
    getOriginClass(origin) {
      const originType = origin?.toLowerCase() || '';
      if (originType.includes('manual')) return 'incident-origin-manual';
      if (originType.includes('audit')) return 'incident-origin-audit';
      if (originType.includes('siem')) return 'incident-origin-siem';
      return 'incident-origin-other';
    },
    async fetchIncidents() {
      try {
        this.isLoadingIncidents = true;
        
        // Build query parameters for backend search and sort
        const params = {};
        
        if (this.searchQuery.trim()) {
          params.search = this.searchQuery.trim();
          console.log('Adding search parameter:', params.search);
        }
        
        if (this.sortField) {
          params.sort_field = this.sortField;
          params.sort_order = this.sortOrder;
          console.log('Adding sort parameters:', params.sort_field, params.sort_order);
        }
        
        console.log('Fetching incidents with params:', params);
        console.log('API URL:', 'http://localhost:8000/api/incident-incidents/');
        
        const response = await axios.get('http://localhost:8000/api/incident-incidents/', { params });
        
        console.log('Response received:', response);
        console.log('Response data length:', response.data.length);
        
        this.incidents = response.data;
        this.filteredIncidents = [...this.incidents];
        console.log('Fetched incidents:', this.incidents);
        console.log('Sample incident statuses:', this.incidents.slice(0, 3).map(inc => ({ id: inc.IncidentId, status: inc.Status })));
        
        // Debug: Show all unique status values
        const uniqueStatuses = [...new Set(this.incidents.map(inc => inc.Status).filter(status => status))];
        console.log('All unique status values found:', uniqueStatuses);
        
        // Reset to first page when data is loaded
        this.currentPage = 1;
        
        // Force re-render after data is loaded to ensure proper layout
        this.$nextTick(() => {
          this.handleResize();
        });
      } catch (error) {
        console.error('Failed to fetch incidents:', error);
        console.error('Error details:', error.response);
        PopupService.error('Failed to load incidents. Please try again.');
      } finally {
        this.isLoadingIncidents = false;
      }
    },
    async fetchUsers() {
      try {
        const response = await axios.get('http://localhost:8000/api/incidents-users/');
        // Map the API response to match the expected frontend structure
        this.availableUsers = response.data.map(user => ({
          id: user.UserId,
          name: user.UserName,
          role: user.role
        }));
        console.log('Fetched users:', this.availableUsers);
      } catch (error) {
        console.error('Failed to fetch users:', error);
        // Keep empty array if fetch fails
        this.availableUsers = [];
      }
    },
    filterIncidents() {
      console.log('filterIncidents called with searchQuery:', this.searchQuery);
      
      // Clear existing timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Set new timeout for debounced search
      this.searchTimeout = setTimeout(() => {
        console.log('Debounce timeout reached, calling performSearch');
        this.performSearch();
      }, 300); // 300ms delay
    },
    
    performSearch() {
      console.log('performSearch called');
      // Perform backend search by refetching data
      this.fetchIncidents();
    },
    
    clearSearch() {
      console.log('Clear search clicked');
      this.searchQuery = '';
      // Clear any pending search timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = null;
      }
      this.fetchIncidents();
    },
    setSortField(field) {
      // Toggle sort order if clicking the same field
      if (this.sortField === field) {
        this.toggleSortOrder();
      } else {
        this.sortField = field;
        // Default to ascending order when changing fields
        this.sortOrder = 'asc';
      }
      // Refetch data with new sorting from backend
      this.fetchIncidents();
    },
    sortIncidents() {
      // Refetch data with sorting from backend
      this.fetchIncidents();
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      // Refetch data with new sort order from backend
      this.fetchIncidents();
    },
    handleResize() {
      // Update layout when window is resized
      const wrapper = document.querySelector('.incident-list-wrapper');
      if (wrapper) {
        wrapper.style.maxWidth = '100%';
      }
    },
    getPriorityClass(priority) {
      switch(priority?.toLowerCase()) {
        case 'high':
          return 'incident-priority-high';
        case 'medium':
          return 'incident-priority-medium';
        case 'low':
          return 'incident-priority-low';
        default:
          return '';
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      
      const [year, month, day] = dateString.split('-');
      return `${month}/${day}/${year}`;
    },
    closeIncidentDetails() {
      this.selectedIncident = null;
      this.showIncidentDetails = false;
    },
    exportIncidents() {
      console.log('Exporting incidents...');
      this.isExporting = true;
      
      // Determine what to export - either all incidents or filtered list
      const dataToExport = this.searchQuery ? this.filteredIncidents : this.incidents;
      
      // Only send necessary fields to reduce payload size
      const trimmedData = dataToExport.map(incident => ({
        IncidentId: incident.IncidentId,
        IncidentTitle: incident.IncidentTitle,
        Date: incident.Date,
        RiskPriority: incident.RiskPriority,
        Origin: incident.Origin,
        Status: incident.Status
      }));
      
      axios.post('http://localhost:8000/api/incidents/export/', {
        file_format: this.exportFormat,
        data: JSON.stringify(trimmedData),
        options: JSON.stringify({
          filters: {
            searchQuery: this.searchQuery,
            sortField: this.sortField,
            sortOrder: this.sortOrder
          }
        })
      })
      .then(response => {
        console.log('Export successful:', response.data);
        
        // Check if we have a file URL
        if (response.data && response.data.file_url) {
          // Create a temporary anchor to trigger download
          const link = document.createElement('a');
          link.href = response.data.file_url;
          link.setAttribute('download', response.data.file_name || `incidents.${this.exportFormat}`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
        
        this.isExporting = false;
        PopupService.success('Export completed successfully');
      })
      .catch(error => {
        console.error('Export failed:', error);
        PopupService.error('Export failed. Please try again.');
        this.isExporting = false;
      });
    }
  }
}
</script>

<style>
/* Add these styles to your existing CSS file or inline here */
.sort-indicator {
  margin-left: 5px;
  display: inline-block;
}

.checklist-header-row div {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.checklist-header-row div:not(.incident-actions-header):hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.checklist-header-row div.sorted {
  font-weight: bold;
  color: #3366cc;
}

.active-sort {
  background-color: #e0e7ff;
  color: #3366cc;
}

/* Header layout with export controls */
.incident-view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.export-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.export-format-select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
}

.export-btn {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.export-btn:hover {
  background-color: #45a049;
}

.export-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
