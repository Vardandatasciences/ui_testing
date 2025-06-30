<template>
  <div class="notifications-container">
    <div class="notifications-header-row">
      <h1 class="notifications-title">
        Notifications
        <i class="fas fa-bell notifications-bell"></i>
      </h1>
    </div>
    <div class="notifications-filters-row">
      <span class="recent-label filter-btn active">
        <i class="fas fa-clock"></i> Recent Notifications
      </span>
      <div class="filter-dropdown-wrapper">
        <button class="filter-btn active" @click="showDaysDropdown = !showDaysDropdown">
          <i class="fas fa-calendar-alt"></i> Last {{ selectedDays }} days
        </button>
        <div v-if="showDaysDropdown" class="days-dropdown">
          <div class="days-option" v-for="d in daysOptions" :key="d" @click="selectDays(d)">
            Last {{ d }} days
          </div>
        </div>
      </div>
      <div class="filter-dropdown-wrapper">
        <button class="filter-btn add-filter-btn" @click="showPriorityFilter = !showPriorityFilter">
          <i class="fas fa-filter"></i> Add filter
        </button>
        <div v-if="showPriorityFilter" class="priority-dropdown">
          <div class="priority-option" v-for="p in priorities" :key="p" @click="selectPriority(p)">
            <span>{{ p }}</span>
          </div>
        </div>
      </div>
      <span v-if="selectedPriority" class="selected-priority">Priority: {{ selectedPriority }}</span>
    </div>
    
    <!-- List of Notifications -->
    <div class="notification-list" v-if="incidents.length > 0 && !showMappedRisks && !showRiskInstanceForm">
      <div class="notification-card" v-for="incident in incidents" :key="incident.IncidentId">
        <div class="notification-header">
          <h3>{{ incident.IncidentTitle }}</h3>
          <span class="notification-date"><i class="fas fa-calendar-alt"></i> {{ formatDate(incident.Date) }}</span>
        </div>
        
        <div class="notification-content">
          <p class="description">{{ incident.Description }}</p>
          <div class="notification-details">
            <div class="detail-item">
              <span class="label">Priority:</span>
              <span class="value" :class="priorityClass(incident.PriorityLevel)">
                {{ incident.PriorityLevel }}
              </span>
            </div>
            <div class="detail-item">
              <span class="label">Category:</span>
              <span class="value">{{ incident.RiskCategory }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Origin:</span>
              <span class="value">{{ incident.Origin }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Compliance ID:</span>
              <span class="value">{{ incident.ComplianceId }}</span>
            </div>
          </div>
        </div>
        
        <div class="notification-actions">
          <button class="accept-btn" @click="showAcceptOptions(incident)">
            Accept
          </button>
          <button class="reject-btn" @click="rejectIncident(incident)">
            Reject
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mapped Risks View -->
    <div v-if="showMappedRisks" class="mapped-risks-container">
      <div class="mapped-risks-header">
        <button class="back-btn" @click="returnToNotifications">
          &larr; Back to Notifications
        </button>
        <h2>Mapped Risks for Incident: {{ selectedIncident.IncidentTitle }}</h2>
      </div>
      
      <!-- Display risk form inline instead of as a popup -->
      <div v-if="showCreateRiskForm" class="add-risk-form">
        <h3>Create New Risk</h3>
        <form @submit.prevent="submitNewRisk" class="risk-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Compliance ID</label>
              <input 
                type="number" 
                v-model="riskForm.ComplianceId" 
                readonly 
                class="readonly-field"
              />
            </div>
            
            <div class="form-group">
              <label>Category *</label>
              <select v-model="riskForm.Category" required>
                <option value="">Select Category</option>
                <option value="Operational">Operational</option>
                <option value="Compliance">Compliance</option>
                <option value="IT Security">IT Security</option>
                <option value="Financial">Financial</option>
                <option value="Strategic">Strategic</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Criticality *</label>
              <select v-model="riskForm.Criticality" required>
                <option value="">Select Criticality</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group wide">
              <label>Risk Description *</label>
              <textarea v-model="riskForm.RiskDescription" required></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Possible Damage</label>
              <textarea v-model="riskForm.PossibleDamage"></textarea>
            </div>
            
            <div class="form-group">
              <label>Risk Likelihood *</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskLikelihood" 
                required 
                placeholder="Enter value (e.g. 8.5)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Impact *</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskImpact" 
                required 
                placeholder="Enter value (e.g. 6.0)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Exposure Rating</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskExposureRating" 
                placeholder="Enter value (e.g. 7.2)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Priority *</label>
              <select v-model="riskForm.RiskPriority" required>
                <option value="">Select Priority</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group wide">
              <label>Risk Mitigation</label>
              <textarea v-model="riskForm.RiskMitigation"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showCreateRiskForm = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn">Create Risk</button>
          </div>
        </form>
      </div>
      
      <!-- Fixed the double v-if with a v-else-if structure -->
      <div v-else-if="mappedRisks.length > 0" class="risk-list">
        <table class="risk-table">
          <thead>
            <tr>
              <th width="40">
                <input 
                  type="checkbox" 
                  :checked="allRisksSelected" 
                  @change="toggleAllRisks"
                  class="checkbox"
                />
              </th>
              <th>Risk ID</th>
              <th>Category</th>
              <th>Criticality</th>
              <th>Description</th>
              <th>Likelihood</th>
              <th>Impact</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="risk in mappedRisks" :key="risk.RiskId">
              <td>
                <input 
                  type="checkbox" 
                  :value="risk.RiskId" 
                  v-model="selectedRisks"
                  class="checkbox"
                />
              </td>
              <td>{{ risk.RiskId }}</td>
              <td>{{ risk.Category }}</td>
              <td>{{ risk.Criticality }}</td>
              <td>{{ risk.RiskDescription }}</td>
              <td>{{ risk.RiskLikelihood }}</td>
              <td>{{ risk.RiskImpact }}</td>
              <td>{{ risk.RiskPriority }}</td>
            </tr>
          </tbody>
        </table>
        
        <div class="risk-action-bar" v-if="hasSelectedRisks">
          <button class="create-instance-btn" @click="showCreateRiskInstanceForm">
            Create Risk Instance{{ selectedRisks.length > 1 ? 's' : '' }}
          </button>
        </div>
      </div>
      
      <!-- Fixed the double directive issue -->
      <div v-else class="empty-risks">
        <p v-if="loadingRisks">Loading mapped risks...</p>
        <p v-else>No risks mapped to this incident</p>
        
        <div class="risk-buttons">
          <button class="create-risk-btn own-risk" @click="showOwnRiskForm">
            Create Own Risk
          </button>
          <button class="create-risk-btn ai-risk" @click="showNewRiskForm">
            Create AI Suggestion Risk
          </button>
        </div>
      </div>
      
      <div v-if="loadingRiskAnalysis" class="loading-analysis">
        <p>Analyzing incident with AI assistant...</p>
      </div>
    </div>
    
    <!-- Risk Instance Form -->
    <div v-if="showRiskInstanceForm" class="risk-instance-form-container">
      <div class="form-header">
        <button class="back-btn" @click="returnToMappedRisks">
          &larr; Back to Mapped Risks
        </button>
        <h2>Create Risk Instance</h2>
      </div>
      
      <form @submit.prevent="submitRiskInstance" class="risk-instance-form">
        <div class="form-grid">
          <!-- Pre-filled fields from selected risk -->
          <div class="form-group">
            <label>Risk ID</label>
            <input type="text" v-model="riskInstanceForm.RiskId" readonly class="readonly-field" />
          </div>
          
          <div class="form-group">
            <label>Category</label>
            <input type="text" v-model="riskInstanceForm.Category" readonly class="readonly-field" />
          </div>
          
          <div class="form-group">
            <label>Criticality *</label>
            <select v-model="riskInstanceForm.Criticality" required>
              <option value="">Select Criticality</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Risk Description *</label>
            <textarea v-model="riskInstanceForm.RiskDescription" required></textarea>
          </div>
          
          <div class="form-group">
            <label>Possible Damage</label>
            <textarea v-model="riskInstanceForm.PossibleDamage"></textarea>
          </div>
          
          <div class="form-group">
            <label>Risk Appetite</label>
            <select v-model="riskInstanceForm.Appetite">
              <option value="">Select Appetite</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Risk Likelihood *</label>
            <input 
              type="number" 
              step="0.1" 
              v-model="riskInstanceForm.RiskLikelihood" 
              required 
              placeholder="Enter value (e.g. 8.5)"
            />
          </div>
          
          <div class="form-group">
            <label>Risk Impact *</label>
            <input 
              type="number" 
              step="0.1" 
              v-model="riskInstanceForm.RiskImpact" 
              required 
              placeholder="Enter value (e.g. 6.0)"
            />
          </div>
          
          <div class="form-group">
            <label>Risk Exposure Rating</label>
            <input 
              type="number" 
              step="0.1" 
              v-model="riskInstanceForm.RiskExposureRating" 
              placeholder="Enter value (e.g. 7.2)"
            />
          </div>
          
          <div class="form-group">
            <label>Risk Priority *</label>
            <select v-model="riskInstanceForm.RiskPriority" required>
              <option value="">Select Priority</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Risk Response Type</label>
            <select v-model="riskInstanceForm.RiskResponseType">
              <option value="">Select Response Type</option>
              <option value="Avoidance">Avoidance</option>
              <option value="Mitigation">Mitigation</option>
              <option value="Transfer">Transfer</option>
              <option value="Acceptance">Acceptance</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Risk Response Description</label>
            <textarea v-model="riskInstanceForm.RiskResponseDescription"></textarea>
          </div>
          
          <div class="form-group">
            <label>Risk Mitigation</label>
            <textarea v-model="riskInstanceForm.RiskMitigation"></textarea>
          </div>
          
          <div class="form-group">
            <label>Risk Owner *</label>
            <input type="text" v-model="riskInstanceForm.RiskOwner" required />
          </div>
          
          <div class="form-group">
            <label>Risk Status *</label>
            <select v-model="riskInstanceForm.RiskStatus" required>
              <option value="">Select Status</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Closed">Closed</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="showRiskInstanceForm = false; showMappedRisks = true;">Cancel</button>
          <button type="submit" class="submit-btn">Create Risk Instance</button>
        </div>
      </form>
    </div>
    
    <!-- Accept Options Modal -->
    <div v-if="showAcceptModal" class="modal-overlay">
      <div class="accept-options-modal modal-content stylish-accept-modal">
        <div class="form-header stylish-header">
          <i class="fas fa-check-circle header-icon"></i>
          <h2>Select Action</h2>
          <button class="close-btn" @click="showAcceptModal = false">×</button>
        </div>
        <div class="accept-options">
          <p>How would you like to proceed with this incident?</p>
          <div class="options-buttons">
            <button class="option-btn map-btn stylish-btn" @click="proceedWithPredefinedRisk">
              <i class="fas fa-link"></i>
              Map with Predefined Risk
            </button>
            <button class="option-btn create-btn stylish-btn" @click="proceedWithNewRisk">
              <i class="fas fa-plus-circle"></i>
              Create New Risk
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-exclamation-circle header-icon" style="color: #dc3545;"></i>
          <h2>Incident Rejected</h2>
          <button class="close-btn" @click="showRejectModal = false">×</button>
        </div>
        <div class="success-content">
          <p>This incident has been marked as rejected. Would you like to create a risk instance?</p>
          <div class="options-buttons">
            <button class="option-btn create-btn stylish-btn" @click="createRiskInstanceForRejected">
              <i class="fas fa-clipboard-list"></i>
              Create Risk Instance
            </button>
            <button class="option-btn map-btn stylish-btn" @click="showRejectModal = false">
              <i class="fas fa-times"></i>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div class="empty-state" v-if="incidents.length === 0 && !showMappedRisks && !showRiskInstanceForm">
      <p v-if="loading">Loading notifications...</p>
      <p v-else>No notifications found</p>
    </div>
    
    <!-- Add a new success modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-check-circle header-icon success-icon"></i>
          <h2>Risk Created Successfully</h2>
          <button class="close-btn" @click="showSuccessModal = false">×</button>
        </div>
        <div class="success-content">
          <p>Your risk has been created and added to the system.</p>
          <div class="options-buttons">
            <button class="option-btn create-btn stylish-btn" @click="createInstanceFromNewRisk">
              <i class="fas fa-clipboard-list"></i>
              Create Risk Instance
            </button>
            <button class="option-btn map-btn stylish-btn" @click="showSuccessModal = false">
              <i class="fas fa-check"></i>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'NotificationsPage',
  data() {
    return {
      incidents: [],
      loading: true,
      showMappedRisks: false,
      showRiskInstanceForm: false,
      selectedIncident: null,
      mappedRisks: [],
      loadingRisks: false,
      selectedRisks: [],
      riskInstanceForm: {
        RiskId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Open',
        UserId: 1,  // Default user ID or you can make this dynamic
        Date: new Date().toISOString().split('T')[0]
      },
      currentRisk: null,
      showCreateRiskForm: false,
      riskForm: {
        ComplianceId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskMitigation: ''
      },
      showAcceptModal: false,
      loadingRiskAnalysis: false,
      showPriorityFilter: false,
      selectedPriority: '',
      priorities: ['High', 'Medium', 'Low', 'Critical'],
      showDaysDropdown: false,
      selectedDays: 7,
      daysOptions: [7, 14, 30],
      showSuccessModal: false,
      newlyCreatedRisk: null, // To store the newly created risk for instance creation
      showRejectModal: false,
      rejectedIncident: null,
    }
  },
  computed: {
    hasSelectedRisks() {
      return this.selectedRisks.length > 0
    },
    allRisksSelected() {
      return this.mappedRisks.length > 0 && this.selectedRisks.length === this.mappedRisks.length
    }
  },
  mounted() {
    this.fetchIncidents()
  },
  methods: {
    fetchIncidents() {
      axios.get('http://localhost:8000/api/incidents/')
        .then(response => {
          this.incidents = response.data
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching incidents:', error)
          this.loading = false
        })
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },
    priorityClass(priority) {
      if (!priority) return ''
      
      const priorityLower = priority.toLowerCase()
      if (priorityLower.includes('critical') || priorityLower.includes('high')) {
        return 'priority-high'
      } else if (priorityLower.includes('medium')) {
        return 'priority-medium'
      }
      return 'priority-low'
    },
    acceptIncident(incident) {
      this.selectedIncident = incident;
      this.proceedWithPredefinedRisk();
    },
    fetchMappedRisks(complianceId) {
      // Fetch all risks and filter by ComplianceId
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          // Filter risks with matching ComplianceId
          this.mappedRisks = response.data.filter(risk => 
            risk.ComplianceId === complianceId
          )
          this.loadingRisks = false
        })
        .catch(error => {
          console.error('Error fetching mapped risks:', error)
          this.loadingRisks = false
        })
    },
    toggleAllRisks(event) {
      if (event.target.checked) {
        // Select all risks
        this.selectedRisks = this.mappedRisks.map(risk => risk.RiskId)
      } else {
        // Deselect all risks
        this.selectedRisks = []
      }
    },
    showCreateRiskInstanceForm() {
      // Allow creating only one instance at a time for simplicity
      if (this.selectedRisks.length === 0) {
        alert('Please select at least one risk.')
        return
      }
      
      // For now, we'll just handle the first selected risk
      this.currentRisk = this.mappedRisks.find(risk => risk.RiskId === this.selectedRisks[0])
      
      // Pre-fill the form with values from the selected risk
      this.riskInstanceForm = {
        ...this.riskInstanceForm,
        RiskId: this.currentRisk.RiskId,
        Category: this.currentRisk.Category,
        Criticality: this.currentRisk.Criticality,
        PossibleDamage: this.currentRisk.PossibleDamage,
        RiskDescription: this.currentRisk.RiskDescription,
        RiskLikelihood: this.currentRisk.RiskLikelihood,
        RiskImpact: this.currentRisk.RiskImpact,
        RiskPriority: this.currentRisk.RiskPriority,
        RiskMitigation: this.currentRisk.RiskMitigation,
        Date: new Date().toISOString().split('T')[0]
      }
      
      this.showRiskInstanceForm = true
      this.showMappedRisks = false
    },
    submitRiskInstance() {
      // Convert the numeric string values to actual numbers
      const formData = {
        ...this.riskInstanceForm,
        // Ensure numeric fields are sent as numbers, not strings
        RiskLikelihood: parseFloat(this.riskInstanceForm.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.riskInstanceForm.RiskImpact) || 0,
        RiskExposureRating: this.riskInstanceForm.RiskExposureRating ? 
          parseFloat(this.riskInstanceForm.RiskExposureRating) : null
      };
      
      console.log('Submitting risk instance:', formData);
      
      // Add the IncidentId from the selected incident
      formData.IncidentId = this.selectedIncident.IncidentId;
      
      axios.post('http://localhost:8000/api/risk-instances/', formData)
        .then(response => {
          console.log('Risk instance created:', response.data);
          alert('Risk instance created successfully!');
          
          // Return to the mapped risks view
          this.showRiskInstanceForm = false;
          this.showMappedRisks = true;
          
          // Reset the form for next time
          this.resetRiskInstanceForm();
        })
        .catch(error => {
          console.error('Error creating risk instance:', error.response?.data || error.message);
          alert(`Error creating risk instance: ${error.response?.data || 'Please check your form data and try again.'}`);
        });
    },
    resetRiskInstanceForm() {
      this.riskInstanceForm = {
        RiskId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Open',
        UserId: 1,
        Date: new Date().toISOString().split('T')[0]
      }
    },
    rejectIncident(incident) {
      this.rejectedIncident = incident;
      this.showRejectModal = true;
      
      // Update the incident status to rejected with source as RISK
      axios.put(`http://localhost:8000/incidents/${incident.IncidentId}/status/`, {
        status: 'Rejected',
        rejection_source: 'RISK'
      })
      .then(response => {
        console.log('Incident rejected:', response.data);
      })
      .catch(error => {
        console.error('Error rejecting incident:', error);
      });
      
      // Log the rejection
      console.log(`Rejected incident ${incident.IncidentId}`);
    },
    proceedWithPredefinedRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      this.loadingRisks = true;
      this.selectedRisks = []; // Reset selections
      
      // Fetch risks that match the ComplianceId
      this.fetchMappedRisks(this.selectedIncident.ComplianceId);
    },
    proceedWithNewRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      
      // No form display here - just go to the mapped risks screen
      // Remove all of these form-related lines:
      // this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
      // this.riskForm.Criticality = '';
      // this.riskForm.PossibleDamage = '';
      // etc...
      
      // Don't show the form
      // this.showCreateRiskForm = true;
    },
    proceedWithAIRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      
      // Show loading indicator
      this.loadingRiskAnalysis = true;
      
      // Prepare the data for analysis
      const incidentData = {
        title: this.selectedIncident.IncidentTitle,
        description: this.selectedIncident.Description
      };
      
      console.log('Sending to API:', incidentData);
      
      // Call the SLM API to get analysis
      axios.post('http://localhost:8000/api/analyze-incident/', incidentData)
        .then(response => {
          console.log('SLM Analysis:', response.data);
          
          // Map the SLM response to the form fields
          this.mapAnalysisToForm(response.data);
          
          // Pre-fill the ComplianceId from the incident
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        })
        .catch(error => {
          console.error('Error analyzing incident:', error.response || error);
          alert('Failed to analyze incident. Creating blank form instead.');
          
          // Still pre-fill the ComplianceId
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form anyway
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        });
    },
    showAcceptOptions(incident) {
      this.selectedIncident = incident;
      this.showAcceptModal = true;
    },
    mapAnalysisToForm(analysis) {
      // Map the SLM analysis fields to the risk form fields
      
      // Map criticality (convert from text to the dropdown values if needed)
      if (analysis.criticality) {
        const criticalityMap = {
          'Severe': 'Critical',
          'Significant': 'High',
          'Moderate': 'Medium',
          'Minor': 'Low'
        };
        this.riskForm.Criticality = criticalityMap[analysis.criticality] || analysis.criticality;
      }
      
      // Map possible damage
      this.riskForm.PossibleDamage = analysis.possibleDamage || '';
      
      // Map category
      this.riskForm.Category = analysis.category || '';
      
      // Map risk description
      this.riskForm.RiskDescription = analysis.riskDescription || '';
      
      // Map risk likelihood (convert from text to number if needed)
      if (analysis.riskLikelihood) {
        const likelihoodMap = {
          'Highly Probable': '9.0',
          'Probable': '7.0',
          'Possible': '5.0',
          'Unlikely': '3.0',
          'Remote': '1.0'
        };
        this.riskForm.RiskLikelihood = likelihoodMap[analysis.riskLikelihood] || '5.0';
      }
      
      // Map risk impact (convert from text to number if needed)
      if (analysis.riskImpact) {
        const impactMap = {
          'Catastrophic': '9.0',
          'Major': '7.0',
          'Moderate': '5.0',
          'Minor': '3.0',
          'Negligible': '1.0'
        };
        this.riskForm.RiskImpact = impactMap[analysis.riskImpact] || '5.0';
      }
      
      // Map risk exposure rating
      this.riskForm.RiskExposureRating = analysis.riskExposureRating ? '7.0' : '';
      
      // Map risk priority
      if (analysis.riskPriority) {
        const priorityMap = {
          'P0': 'Critical',
          'P1': 'High',
          'P2': 'Medium',
          'P3': 'Low'
        };
        this.riskForm.RiskPriority = priorityMap[analysis.riskPriority] || 'Medium';
      }
      
      // Map risk mitigation
      if (analysis.riskMitigation && Array.isArray(analysis.riskMitigation)) {
        // Join but ensure it doesn't exceed 100 characters
        const fullMitigation = analysis.riskMitigation.join('\n');
        this.riskForm.RiskMitigation = fullMitigation.length > 100 
          ? fullMitigation.substring(0, 97) + '...' 
          : fullMitigation;
      }
    },
    showErrorAlert(title, message) {
      // Get a formatted error message
      const formattedMessage = typeof message === 'object' 
        ? JSON.stringify(message, null, 2) 
        : message;
      
      // For now, just use alert, but you could use a nicer modal
      alert(`${title}\n\n${formattedMessage}`);
    },
    selectPriority(priority) {
      this.selectedPriority = priority;
      this.showPriorityFilter = false;
    },
    selectDays(days) {
      this.selectedDays = days;
      this.showDaysDropdown = false;
    },
    showOwnRiskForm() {
      // Pre-fill only the ComplianceId from the incident
      this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
      
      // Reset other form fields
      this.riskForm.Criticality = '';
      this.riskForm.PossibleDamage = '';
      this.riskForm.Category = '';
      this.riskForm.RiskDescription = '';
      this.riskForm.RiskLikelihood = '';
      this.riskForm.RiskImpact = '';
      this.riskForm.RiskExposureRating = '';
      this.riskForm.RiskPriority = '';
      this.riskForm.RiskMitigation = '';
      
      // Show the create risk form
      this.showCreateRiskForm = true;
    },
    showNewRiskForm() {
      // Show loading indicator
      this.loadingRiskAnalysis = true;
      
      // Prepare the data for analysis
      const incidentData = {
        title: this.selectedIncident.IncidentTitle,
        description: this.selectedIncident.Description
      };
      
      console.log('Sending to API:', incidentData);
      
      // Call the SLM API to get analysis
      axios.post('http://localhost:8000/api/analyze-incident/', incidentData)
        .then(response => {
          console.log('SLM Analysis:', response.data);
          
          // Map the SLM response to the form fields
          this.mapAnalysisToForm(response.data);
          
          // Pre-fill the ComplianceId from the incident
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        })
        .catch(error => {
          console.error('Error analyzing incident:', error.response || error);
          alert('Failed to analyze incident. Creating blank form instead.');
          
          // Still pre-fill the ComplianceId
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form anyway
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        });
    },
    submitNewRisk() {
      // Convert numeric string values to actual numbers
      const formData = {
        ...this.riskForm,
        ComplianceId: parseInt(this.riskForm.ComplianceId) || null,
        RiskLikelihood: parseFloat(this.riskForm.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.riskForm.RiskImpact) || 0,
        RiskExposureRating: this.riskForm.RiskExposureRating ? 
          parseFloat(this.riskForm.RiskExposureRating) : null
      };
      
      console.log('Submitting new risk:', formData);
      
      axios.post('http://localhost:8000/api/risks/', formData)
        .then(response => {
          console.log('Risk created:', response.data);
          
          // Store the newly created risk
          this.newlyCreatedRisk = response.data;
          
          // Add the newly created risk to the mapped risks array
          this.mappedRisks.push(response.data);
          
          // Hide the form but stay on mapped risks view
          this.showCreateRiskForm = false;
          
          // Show success modal instead of alert
          this.showSuccessModal = true;
          
          // Reset the form for next time
          this.resetRiskForm();
        })
        .catch(error => {
          console.error('Error creating risk:', error.response?.data || error.message);
          
          let errorMessage = 'Please check your form data and try again.';
          if (error.response && error.response.data) {
            errorMessage = error.response.data;
          }
          
          this.showErrorAlert('Error creating risk', errorMessage);
        });
    },
    resetRiskForm() {
      this.riskForm = {
        ComplianceId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskMitigation: ''
      };
    },
    createInstanceFromNewRisk() {
      // Close the success modal
      this.showSuccessModal = false;
      
      // Pre-fill the risk instance form with values from the newly created risk
      this.currentRisk = this.newlyCreatedRisk;
      
      // Similar to showCreateRiskInstanceForm method
      this.riskInstanceForm = {
        ...this.riskInstanceForm,
        RiskId: this.currentRisk.RiskId,
        Category: this.currentRisk.Category,
        Criticality: this.currentRisk.Criticality,
        PossibleDamage: this.currentRisk.PossibleDamage,
        RiskDescription: this.currentRisk.RiskDescription,
        RiskLikelihood: this.currentRisk.RiskLikelihood,
        RiskImpact: this.currentRisk.RiskImpact,
        RiskPriority: this.currentRisk.RiskPriority,
        RiskMitigation: this.currentRisk.RiskMitigation,
        Date: new Date().toISOString().split('T')[0]
      }
      
      // Show the risk instance form
      this.showRiskInstanceForm = true;
      this.showMappedRisks = false;
    },
    createRiskInstanceForRejected() {
      // Close the reject modal
      this.showRejectModal = false;
      
      // Set the current incident for risk instance creation
      this.selectedIncident = this.rejectedIncident;
      
      // Initialize a blank risk instance form
      this.resetRiskInstanceForm();
      
      // Set incident-related fields
      this.riskInstanceForm.IncidentId = this.rejectedIncident.IncidentId;
      this.riskInstanceForm.Category = this.rejectedIncident.RiskCategory || '';
      this.riskInstanceForm.RiskDescription = this.rejectedIncident.Description || '';
              this.riskInstanceForm.CreatedAt = new Date().toISOString().split('T')[0];
      
      // Show the risk instance form
      this.showRiskInstanceForm = true;
    },
    returnToNotifications() {
      this.showMappedRisks = false;
    },
    returnToMappedRisks() {
      this.showRiskInstanceForm = false;
    },
  }
}
</script>

<style scoped>
.notifications-container {
  padding: 5px;
  max-width: 1200px;
  margin: 0 auto;
  margin-left: 200px;
}

.notifications-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
}

.notifications-title {
  font-size: 32px;
  margin-bottom: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.notifications-bell {
  font-size: 1.5rem;
  margin-left: 8px;
  color: #222;
}

.notifications-filters-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 18px 0 18px 0;
}

.recent-label {
  font-size: 1.1rem;
  color: #222;
  font-weight: 500;
  margin-right: 12px;
  background: #e6f0ff;
  border-radius: 20px;
  padding: 8px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-btn {
  background: #f5f7fa;
  border: none;
  border-radius: 20px;
  padding: 8px 18px;
  font-size: 1rem;
  color: #222;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: background 0.18s;
  box-shadow: none;
}

.filter-btn.active, .filter-btn:hover {
  background: #e6f0ff;
  color: #0056b3;
}

.filter-dropdown-wrapper {
  position: relative;
}

.priority-dropdown {
  position: absolute;
  top: 38px;
  left: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  min-width: 140px;
  z-index: 10;
  padding: 6px 0;
}

.priority-option {
  padding: 8px 18px;
  cursor: pointer;
  font-size: 1rem;
  color: #222;
  transition: background 0.15s;
}

.priority-option:hover {
  background: #e6f0ff;
  color: #0056b3;
}

.selected-priority {
  background: #e6f0ff;
  color: #0056b3;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 1rem;
  margin-left: 8px;
}

.notification-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px 20px;
  max-height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
}

.notification-card {
  background: #f7faff;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(0, 60, 180, 0.06);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  min-width: 0;
  border: 2px solid rgba(0,0,0,0.10);
}

.notification-card:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 8px 24px rgba(0, 60, 180, 0.10);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 28px 12px 28px;
  background-color: #eaf1fb;
  border-bottom: 1px solid #e0e7ef;
}

.notification-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #22314a;
  font-weight: 700;
}

.notification-date {
  font-size: 1rem;
  color: #7a8ca7;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.notification-content {
  padding: 20px 28px 0 28px;
}

.description {
  margin-top: 0;
  margin-bottom: 18px;
  color: #2c3e50;
  font-size: 1.05rem;
  line-height: 1.6;
}

.notification-details {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}

.detail-item {
  display: flex;
  align-items: center;
  background-color: #f0f4fa;
  padding: 8px 18px;
  border-radius: 16px;
  border: 1px solid #e0e7ef;
  font-size: 1rem;
}

.label {
  font-weight: 600;
  color: #22314a;
  margin-right: 8px;
  font-size: 1rem;
}

.value {
  color: #22314a;
  font-size: 1rem;
  font-weight: 500;
}

.priority-high {
  color: #e53935;
  font-weight: 700;
}

.priority-medium {
  color: #fb8c00;
  font-weight: 700;
}

.priority-low {
  color: #43a047;
  font-weight: 700;
}

.notification-actions {
  display: flex;
  gap: 16px;
  padding: 18px 28px 22px 28px;
  background-color: #eaf1fb;
  border-top: 1px solid #e0e7ef;
  justify-content: flex-end;
}

.accept-btn {
  background-color: #28a745;
  color: white;
  padding: 10px 28px;
  border-radius: 8px;
  font-weight: 700;
  border: 2px solid #e0e7ef;
  transition: all 0.2s;
}

.accept-btn:hover {
  background-color: #218838;
  transform: translateY(-1px) scale(1.03);
}

.reject-btn {
  background-color: #dc3545;
  color: white;
  padding: 10px 28px;
  border-radius: 8px;
  font-weight: 700;
  border: 2px solid #e0e7ef;
  transition: all 0.2s;
}

.reject-btn:hover {
  background-color: #c82333;
  transform: translateY(-1px) scale(1.03);
}

.back-btn {
  background-color: #222;
  color: #fff;
  border-radius: 6px;
  padding: 8px 18px;
  font-weight: 600;
  margin-bottom: 18px;
  border: none;
  box-shadow: 2px 2px 0 #8882;
  transition: background 0.18s;
}

.back-btn:hover {
  background-color: #444;
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  color: #6c757d;
}

/* Mapped Risks Styles */
.mapped-risks-container {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(0,60,180,0.06);
  padding: 32px 24px 24px 24px;
  margin-top: 24px;
}

.mapped-risks-header {
  margin-bottom: 20px;
}

.mapped-risks-header h2 {
  font-size: 1.35rem;
  color: #22314a;
  font-weight: 700;
  margin-bottom: 18px;
}

.risk-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,60,180,0.04);
}

.risk-table th {
  background: #f8fafd;
  font-weight: 700;
  color: #22314a;
  padding: 16px 10px;
  border-bottom: 2px solid #e0e7ef;
  text-align: left;
  font-size: 1.08rem;
}

.risk-table td {
  padding: 14px 10px;
  border-bottom: 1px solid #e0e7ef;
  color: #22314a;
  font-size: 1.05rem;
}

.risk-table tr:last-child td {
  border-bottom: none;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.risk-action-bar {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.create-instance-btn {
  background-color: #4285f4;
  color: white;
  font-size: 16px;
  padding: 10px 20px;
}

.create-instance-btn:hover {
  background-color: #3367d6;
}

.empty-risks {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

/* Risk Instance Form Styles */
.risk-instance-form-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-header {
  margin-bottom: 24px;
}

.form-header h2 {
  font-size: 20px;
  color: #2c3e50;
  margin-top: 16px;
}

.risk-instance-form {
  width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #495057;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.readonly-field {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-actions {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  background-color: #4285f4;
  color: white;
  padding: 10px 20px;
}

.submit-btn:hover {
  background-color: #3367d6;
}

/* Add new styles */
.create-risk-btn {
  background-color: #4285f4;
  color: white;
  font-size: 16px;
  padding: 10px 20px;
  margin-top: 20px;
  border-radius: 4px;
}

.create-risk-btn:hover {
  background-color: #3367d6;
}

.risk-form-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Modal overlay styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal-content {
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  overflow-y: auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

/* Accept Options Modal Styles */
.accept-options-modal {
  padding: 30px;
  max-width: 500px;
}

.accept-options {
  text-align: center;
}

.accept-options p {
  margin-bottom: 20px;
  font-size: 16px;
}

.options-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.option-btn {
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  min-width: 180px;
}

.map-btn {
  background-color: #4285f4;
  color: white;
}

.map-btn:hover {
  background-color: #3367d6;
}

.create-btn {
  background-color: #28a745;
  color: white;
}

.create-btn:hover {
  background-color: #218838;
}

.loading-analysis {
  text-align: center;
  padding: 40px;
  color: #4285f4;
  font-weight: 600;
}

.days-dropdown {
  position: absolute;
  top: 38px;
  left: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  min-width: 140px;
  z-index: 10;
  padding: 6px 0;
}

.days-option {
  padding: 8px 18px;
  cursor: pointer;
  font-size: 1rem;
  color: #222;
  transition: background 0.15s;
}

.days-option:hover {
  background: #e6f0ff;
  color: #0056b3;
}

.add-filter-btn {
  background: #e6f0ff;
  color: #0056b3;
}

.add-filter-btn:hover, .add-filter-btn.active {
  background: #e6f0ff;
  color: #0056b3;
}

.stylish-accept-modal {
  background: #f7faff;
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(0,60,180,0.10);
  border: 2px solid #e0e7ef;
  padding: 36px 36px 32px 36px;
  max-width: 440px;
}
.stylish-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 18px;
  position: relative;
}
.header-icon {
  color: #4285f4;
  font-size: 2rem;
}
.stylish-header h2 {
  font-size: 1.35rem;
  color: #22314a;
  font-weight: 700;
  margin: 0;
}
.stylish-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-width: 200px;
  max-width: 220px;
  width: 100%;
  font-size: 1.08rem;
  font-weight: 700;
  padding: 14px 0;
  box-shadow: 0 2px 8px rgba(66,133,244,0.07);
  border-radius: 8px;
  border: 2px solid #e0e7ef;
  transition: all 0.18s;
}
.stylish-btn i {
  font-size: 1.2em;
}
.options-buttons {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 32px;
}

.risk-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.own-risk {
  background-color: #6c757d;
}

.own-risk:hover {
  background-color: #5a6268;
}

.ai-risk {
  background-color: #4285f4;
}

.ai-risk:hover {
  background-color: #3367d6;
}

/* Add these styles for the inline form */
.add-risk-form {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.add-risk-form h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 1.2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group.wide {
  grid-column: span 3;
}

.success-icon {
  color: #28a745;
}

.success-content {
  text-align: center;
  margin-top: 10px;
}

.success-content p {
  margin-bottom: 20px;
  font-size: 16px;
  color: #22314a;
}
</style>