<template>
  <div class="audit-findings-container">
    <div class="audit-findings-header">
      <h1>Audit Finding Incidents</h1>
      <div class="incident-actions">
        <!-- Search input -->
        <div class="incident-search-controls">
          <input 
            v-model="searchQuery" 
            @input="applyFilters"
            type="text" 
            placeholder="Search by title, ID, or description..." 
            class="incident-search-input"
          />
        </div>
        
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
          <button @click="exportAuditFindings" class="incident-export-btn" :disabled="isExporting">
            <span v-if="isExporting">Exporting...</span>
            <span v-else>Export</span>
          </button>
        </div>
        <div class="incident-filters">
          <select v-model="filterStatus" @change="applyFilters">
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="closed">Closed</option>
            <option value="rejected">Rejected</option>
            <option value="scheduled">Escalated to Risk</option>
          </select>
          <select v-model="sortBy" @change="applyFilters">
            <option value="Date">Date (Newest First)</option>
            <option value="IncidentTitle">Title</option>
            <option value="RiskPriority">Priority</option>
            <option value="Status">Status</option>
          </select>
        </div>
        <button class="incident-refresh-btn" @click="fetchData">
          <i class="fas fa-sync"></i> Refresh
        </button>
      </div>
    </div>

    <div class="loading-container" v-if="loading">
      <div class="spinner"></div>
      <p>Loading audit findings...</p>
    </div>

    <div class="error-container" v-if="error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="fetchData">Retry</button>
    </div>

    <div class="incident-findings-content" v-if="!loading && !error">
      <div class="incident-summary-cards">
        <div class="incident-summary-card open-card" :class="{ active: filterStatus === 'open' }" @click="filterByStatus('open')">
          <div class="card-icon open">
            <i class="fas fa-exclamation-circle"></i>
          </div>
          <div class="card-content">
            <h3>Open</h3>
            <div class="card-value">{{ summary.open || 0 }}</div>
          </div>
        </div>

        <div class="incident-summary-card assigned-card" :class="{ active: filterStatus === 'assigned' }" @click="filterByStatus('assigned')">
          <div class="card-icon assigned">
            <i class="fas fa-user-check"></i>
          </div>
          <div class="card-content">
            <h3>Assigned</h3>
            <div class="card-value">{{ summary.assigned || 0 }}</div>
          </div>
        </div>

        <div class="incident-summary-card closed-card" :class="{ active: filterStatus === 'closed' }" @click="filterByStatus('closed')">
          <div class="card-icon closed">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>Closed</h3>
            <div class="card-value">{{ summary.closed || 0 }}</div>
          </div>
        </div>

        <div class="incident-summary-card rejected-card" :class="{ active: filterStatus === 'rejected' }" @click="filterByStatus('rejected')">
          <div class="card-icon rejected">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="card-content">
            <h3>Rejected</h3>
            <div class="card-value">{{ summary.rejected || 0 }}</div>
          </div>
        </div>

        <div class="incident-summary-card mitigated-card" :class="{ active: filterStatus === 'scheduled' }" @click="filterByStatus('scheduled')">
          <div class="card-icon mitigated">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>Mitigated to Risk</h3>
            <div class="card-value">{{ summary.mitigated || 0 }}</div>
          </div>
        </div>

        <div class="incident-summary-card total-card" :class="{ active: filterStatus === 'all' }" @click="filterByStatus('all')">
          <div class="card-icon total">
            <i class="fas fa-list-alt"></i>
          </div>
          <div class="card-content">
            <h3>Total Incidents</h3>
            <div class="card-value">{{ summary.total || 0 }}</div>
          </div>
        </div>
      </div>

      <div class="incident-findings-table" :class="{ 'dropdown-open': dropdownOpenFor !== null }">
        <table>
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Title</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Origin</th>
              <th>Date</th>
              <th>Time</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in findings" :key="index" :class="getRowClass(item.Status)">
              <td>{{ item.IncidentId }}</td>
              <td>{{ item.IncidentTitle }}</td>
              <td>{{ item.RiskPriority || 'N/A' }}</td>
              <td>
                <span 
                  class="status-badge" 
                  :class="getStatusClass(item.Status)"
                  style="display: inline-block !important; visibility: visible !important;"
                >
                  {{ item.Status || 'Open' }}
                </span>
              </td>
              <td>{{ item.Origin }}</td>
              <td>{{ formatDate(item.Date) }}</td>
              <td>{{ item.Time || 'N/A' }}</td>
              <td>{{ truncateText(item.Description, 50) }}</td>
              <td>
                <div class="action-buttons">
                  <!-- Show Actions dropdown only for Open status -->
                  <div v-if="!item.Status || item.Status === 'Open'" class="actions-dropdown">
                    <button 
                      class="actions-button" 
                      @click="toggleActionDropdown(index)"
                      :class="{ active: dropdownOpenFor === index }"
                    >
                      <i class="fas fa-cog gear-icon"></i>
                      Actions
                      <i class="fas fa-chevron-down dropdown-arrow" :class="{ rotate: dropdownOpenFor === index }"></i>
                    </button>
                    <div 
                      class="actions-dropdown-menu" 
                      :class="{ show: dropdownOpenFor === index }"
                    >
                      <button class="dropdown-item" @click="handleDropdownAction('view', item)">
                        <i class="fas fa-eye"></i>
                        View Details
                      </button>
                      <button class="dropdown-item" @click="handleDropdownAction('assign', item)">
                        <i class="fas fa-user-plus"></i>
                        Assign as Incident
                      </button>
                      <button class="dropdown-item" @click="handleDropdownAction('escalate', item)">
                        <i class="fas fa-arrow-up"></i>
                        Escalate to Risk
                      </button>
                      <button class="dropdown-item" @click="handleDropdownAction('reject', item)">
                        <i class="fas fa-times"></i>
                        Reject Incident
                      </button>
                    </div>
                  </div>
                  
                  <!-- Show only View Details button for processed items -->
                  <button 
                    v-else
                    class="view-details-btn" 
                    @click="viewDetails(item)" 
                    title="View Details"
                  >
                    <i class="fas fa-eye"></i>
                    View Details
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="findings.length === 0" class="empty-state">
        <i class="fas fa-search"></i>
        <p>No audit finding incidents match your criteria.</p>
      </div>
    </div>

    <!-- Modal for Solve/Reject -->
    <div v-if="showModal && modalAction !== 'assign'" class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <button class="modal-close-btn" @click="closeModal">✕</button>
        <div class="modal-content">
          <div v-if="modalAction === 'solve'" class="solve-container">
            <div class="solve-icon">🔄</div>
            <h3 class="modal-title solve">Forwarded to Risk</h3>
            <p class="modal-subtitle">You will be directed to the Risk module</p>
            <div class="modal-footer">
              <button @click="confirmSolve" class="modal-btn confirm-btn">Confirm Forward</button>
              <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
            </div>
          </div>
          
          <div v-else-if="modalAction === 'reject'" class="rejected-container">
            <div class="rejected-icon">✕</div>
            <h3 class="modal-title rejected">REJECTED</h3>
            <div class="modal-footer">
              <button @click="confirmReject" class="modal-btn reject-btn">Confirm Reject</button>
              <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assignment Workflow Section -->
    <div v-if="showAssignmentWorkflow" class="assignment-workflow-section">
      <div class="assignment-header">
        <button class="back-btn" @click="closeAssignmentWorkflow">
          <i class="fas fa-arrow-left"></i> Back to Audit Findings
        </button>
      </div>
      <div class="assignment-body">
        <div class="incident-summary">
          <h3>{{ selectedIncident.IncidentTitle || 'Incident #' + selectedIncident.IncidentId }}</h3>
          <div class="incident-details">
            <p><strong>ID:</strong> {{ selectedIncident.IncidentId }}</p>
            <p><strong>Priority:</strong> {{ selectedIncident.RiskPriority }}</p>
            <p><strong>Origin:</strong> {{ selectedIncident.Origin }}</p>
          </div>
        </div>

        <!-- User Selection -->
        <div class="user-selection">
          <h3>Assignment Details</h3>
          <div class="user-form">
              <div class="form-group">
                <label for="assigner">Assigner:</label>
                <select v-model="selectedAssigner" id="assigner" class="assign-select" required>
                  <option value="">Select Assigner</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="reviewer">Reviewer:</label>
                <select v-model="selectedReviewer" id="reviewer" class="assign-select" required>
                  <option value="">Select Reviewer</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.name }}
                  </option>
                </select>
            </div>
          </div>
        </div>
        
        <!-- Mitigation Workflow -->
        <div class="mitigation-workflow">
          <h3>Mitigation Steps</h3>
          <!-- Existing Mitigation Steps -->
          <div v-if="mitigationSteps.length" class="workflow-timeline">
            <div v-for="(step, index) in mitigationSteps" :key="index" class="workflow-step">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <textarea 
                  v-model="step.description" 
                  class="mitigation-textarea"
                  placeholder="Enter mitigation step description"
                ></textarea>
                <div class="step-actions">
                  <button @click="removeMitigationStep(index)" class="remove-step-btn">
                    <i class="fas fa-trash"></i> Remove
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-mitigations">
            <p>No mitigation steps found for this incident. Add steps below.</p>
          </div>
          
          <!-- Add New Mitigation Step -->
          <div class="add-mitigation">
            <textarea 
              v-model="newMitigationStep" 
              class="mitigation-textarea"
              placeholder="Enter mitigation step description(s). You can add multiple steps by separating them with commas or new lines."
            ></textarea>
            <button @click="addMitigationStep" class="add-step-btn" :disabled="!newMitigationStep.trim()">
              <i class="fas fa-plus"></i> Add Mitigation Step
            </button>
          </div>
          
          <!-- Due Date Input -->
          <div class="due-date-section">
            <h4>Due Date for Mitigation Completion</h4>
            <input 
              type="date" 
              v-model="mitigationDueDate" 
              class="due-date-input" 
              :min="getTodayDate()"
            />
          </div>

          <!-- Assignment Notes -->
          <div class="assignment-notes-section">
            <h4>Assignment Notes (Optional)</h4>
                <textarea 
                  v-model="assignmentNotes" 
              class="assignment-notes-textarea"
                  placeholder="Add any specific instructions or notes for the assignees..."
                  rows="3"
                ></textarea>
            </div>
            
          <!-- Submit Section -->
          <div class="assignment-actions">
              <button 
              @click="confirmAssignmentWorkflow" 
              class="submit-assignment-btn"
              :disabled="!selectedAssigner || !selectedReviewer || mitigationSteps.length === 0 || !mitigationDueDate"
              >
              <i class="fas fa-user-plus"></i> Assign Incident with Mitigations
              </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { PopupModal, PopupService } from '@/modules/popup';

export default {
  name: 'AuditFindings',
  components: {
    PopupModal
  },
  setup() {
    const router = useRouter();
    const findings = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const summary = ref({});
    
    // Modal and workflow state
    const showModal = ref(false);
    const modalAction = ref(''); // 'solve', 'reject', or 'assign'
    const selectedIncident = ref(null);
    const showAssignmentWorkflow = ref(false);
    
    // Assignment related data
    const selectedAssigner = ref('');
    const selectedReviewer = ref('');
    const assignmentNotes = ref('');
    const availableUsers = ref([]);
    
    // Mitigation workflow data
    const mitigationSteps = ref([]);
    const newMitigationStep = ref('');
    const mitigationDueDate = ref('');
    
    // Filters
    const filterStatus = ref('all');
    const sortBy = ref('Date');
    
    // Export controls
    const exportFormat = ref('xlsx');
    const isExporting = ref(false);
    
    // Dropdown state
    const dropdownOpenFor = ref(null);
    
    // Search query
    const searchQuery = ref('');
    
    // Fetch data from the API
    const fetchData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const params = {};
        
        // Apply status filter if not 'all'
        if (filterStatus.value !== 'all') {
          params.status = filterStatus.value;
        }
        
        // Apply sorting
        params.sort = sortBy.value;
        params.order = sortBy.value === 'Date' ? 'desc' : 'asc';
        
        // Apply search query
        if (searchQuery.value) {
          params.search = searchQuery.value;
        }
        
        const response = await axios.get('http://localhost:8000/api/audit-findings/', { params });
        
        if (response.data && response.data.success) {
          findings.value = response.data.data || [];
          summary.value = response.data.summary || {};
        } else {
          throw new Error(response.data?.message || 'Failed to load audit finding incidents');
        }
      } catch (err) {
        console.error('Error fetching audit finding incidents:', err);
        error.value = err.message || 'Failed to load audit finding incidents. Please try again.';
      } finally {
        loading.value = false;
      }
    };
    
    // Apply filters and sorting
    const applyFilters = () => {
      fetchData();
    };
    
    // Filter by status when clicking on summary cards
    const filterByStatus = (status) => {
      filterStatus.value = status;
      applyFilters();
    };
    
    // Utility functions for styling
    const getRowClass = (status) => {
      if (!status || status === 'Open') return 'row-open';
      if (status === 'Assigned') return 'row-assigned';
      if (status === 'Closed') return 'row-closed';
      if (status === 'Rejected') return 'row-rejected';
      if (status === 'Scheduled') return 'row-escalated';
      return '';
    };
    
    const getStatusClass = (status) => {
      if (!status || status === 'Open') return 'status-open';
      if (status === 'Assigned') return 'status-assigned';
      if (status === 'Closed') return 'status-closed';
      if (status === 'Rejected') return 'status-rejected';
      if (status === 'Scheduled') return 'status-escalated';
      return '';
    };
    
    // Navigate to audit finding details
    const viewDetails = (item) => {
      router.push(`/incident/audit-finding-details/${item.IncidentId}`);
    };
    
    // Modal and workflow methods
    const openSolveModal = (incident) => {
      selectedIncident.value = incident;
      modalAction.value = 'solve';
      showModal.value = true;
    };
    
    const openRejectModal = (incident) => {
      selectedIncident.value = incident;
      modalAction.value = 'reject';
      showModal.value = true;
    };
    
    const openAssignModal = (incident) => {
      selectedIncident.value = incident;
      showAssignmentWorkflow.value = true;
      // Reset assignment form
      selectedAssigner.value = '';
      selectedReviewer.value = '';
      assignmentNotes.value = '';
      newMitigationStep.value = '';
      mitigationDueDate.value = '';
      
      // Fetch users for assignment
      fetchUsers();
      
      // Load existing mitigation steps from the incident's Mitigation field
      console.log('Selected incident:', incident);
      console.log('Incident Mitigation field:', incident.Mitigation);
      loadExistingMitigations(incident);
    };
    
    const closeModal = () => {
      showModal.value = false;
      selectedIncident.value = null;
      // Reset assignment form data
      selectedAssigner.value = '';
      selectedReviewer.value = '';
      assignmentNotes.value = '';
    };
    
    const closeAssignmentWorkflow = () => {
      showAssignmentWorkflow.value = false;
      selectedIncident.value = null;
      // Reset assignment form data
      selectedAssigner.value = '';
      selectedReviewer.value = '';
      assignmentNotes.value = '';
      mitigationSteps.value = [];
      newMitigationStep.value = '';
      mitigationDueDate.value = '';
    };
    
    const addMitigationStep = () => {
      if (!newMitigationStep.value.trim()) return;
      
      // Split by commas or newlines to allow multiple steps at once
      const steps = newMitigationStep.value.split(/[,\n]/).filter(step => step.trim());
      
      steps.forEach(step => {
        mitigationSteps.value.push({
          description: step.trim(),
          status: 'Not Started'
        });
      });
      
      newMitigationStep.value = '';
    };
    
    const removeMitigationStep = (index) => {
      mitigationSteps.value.splice(index, 1);
    };
    
    const getTodayDate = () => {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    const loadExistingMitigations = (incident) => {
      // Initialize with empty array
      mitigationSteps.value = [];
      
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
            const steps = mitigationData.split(/[,\n]/).filter(step => step.trim());
            mitigationSteps.value = steps.map((step) => ({
              description: step.trim(),
              status: 'Not Started'
            }));
          } else if (Array.isArray(mitigationData)) {
            // Array format
            mitigationSteps.value = mitigationData.map(item => ({
              description: typeof item === 'string' ? item : (item.description || item.title || 'Mitigation step'),
              status: item.status || 'Not Started'
            }));
          } else if (typeof mitigationData === 'object') {
            // Object format (like {"1": "Step 1", "2": "Step 2"})
            mitigationSteps.value = Object.values(mitigationData).map(step => ({
              description: typeof step === 'string' ? step : (step.description || step.title || 'Mitigation step'),
              status: step.status || 'Not Started'
            }));
          }
          
          console.log('Loaded existing mitigation steps:', mitigationSteps.value);
        } catch (error) {
          console.error('Error parsing mitigation data:', error);
          // Fallback: treat as plain text
          mitigationSteps.value = [{
            description: incident.Mitigation,
            status: 'Not Started'
          }];
        }
      }
      
      // If no mitigation steps were loaded, start with empty array
      if (mitigationSteps.value.length === 0) {
        console.log('No existing mitigation steps found');
      }
    };
    
    const confirmAssignmentWorkflow = () => {
      // Validate selections
      if (!selectedAssigner.value || !selectedReviewer.value) {
        PopupService.error('Please select both assigner and reviewer');
        return;
      }

      if (selectedAssigner.value === selectedReviewer.value) {
        PopupService.error('Assigner and reviewer cannot be the same person');
        return;
      }

      if (mitigationSteps.value.length === 0) {
        PopupService.error('Please add at least one mitigation step');
        return;
      }

      if (!mitigationDueDate.value) {
        PopupService.error('Please select a due date');
        return;
      }

      console.log('Assigning incident:', selectedIncident.value.IncidentId);

      // Find user details
      const assigner = availableUsers.value.find(user => user.id === selectedAssigner.value);
      const reviewer = availableUsers.value.find(user => user.id === selectedReviewer.value);

      // Convert mitigations to the expected JSON format
      const mitigationsJson = {};
      mitigationSteps.value.forEach((step, index) => {
        mitigationsJson[index + 1] = step.description;
      });

      // Update incident with assignment details and mitigations
      axios.put(`http://localhost:8000/api/incidents/${selectedIncident.value.IncidentId}/assign/`, {
        status: 'In Progress',
        assigner_id: selectedAssigner.value,
        assigner_name: assigner.name,
        reviewer_id: selectedReviewer.value,
        reviewer_name: reviewer.name,
        assignment_notes: assignmentNotes.value,
        assigned_date: new Date().toISOString(),
        mitigations: mitigationsJson,
        due_date: mitigationDueDate.value
      })
      .then(response => {
        console.log('Incident assigned successfully - API response:', response.data);
        
        // Show success popup
        PopupService.success(`Incident ${selectedIncident.value.IncidentId} assigned successfully with mitigation steps!`);
        
        // Refresh the audit findings data
        fetchData();
        
        // Close workflow and redirect
        closeAssignmentWorkflow();
        setTimeout(() => {
          router.push('/incident/incident');
        }, 2000);
      })
      .catch(err => {
        console.error('Error assigning incident:', err);
        PopupService.error('Failed to assign incident. Please try again.');
      });
    };
    
    const confirmSolve = () => {
      console.log('Escalating incident to risk:', selectedIncident.value.IncidentId);
      
      // Update incident status to "Scheduled"
      axios.put(`http://localhost:8000/api/incidents/${selectedIncident.value.IncidentId}/status/`, {
        status: 'Scheduled'
      })
      .then(response => {
        console.log('Incident escalated to risk - API response:', response.data);
        
        // Show success popup
        PopupService.success(`Incident ${selectedIncident.value.IncidentId} escalated to Risk successfully!`);
        
        // Refresh the audit findings data
        fetchData();
        
        // Close modal and redirect after 2 seconds
        closeModal();
        setTimeout(() => {
          router.push('/incident/incident');
        }, 2000);
      })
      .catch(err => {
        console.error('Error updating incident status:', err);
        PopupService.error('Failed to escalate incident. Please try again.');
      });
    };
    
    const confirmReject = () => {
      console.log('Rejecting incident:', selectedIncident.value.IncidentId);
      
      // Update incident status to "Rejected"
      axios.put(`http://localhost:8000/api/incidents/${selectedIncident.value.IncidentId}/status/`, {
        status: 'Rejected',
        rejection_source: 'INCIDENT'
      })
      .then(response => {
        console.log('Incident rejected - API response:', response.data);
        
        // Show success popup
        PopupService.success(`Incident ${selectedIncident.value.IncidentId} rejected successfully!`);
        
        // Refresh the audit findings data
        fetchData();
        
        // Close modal and redirect after 2 seconds
        closeModal();
        setTimeout(() => {
          router.push('/incident/incident');
        }, 2000);
      })
      .catch(err => {
        console.error('Error updating incident status:', err);
        PopupService.error('Failed to reject incident. Please try again.');
      });
    };
    
    // Fetch users for assignment
    const fetchUsers = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/users/');
        // Map the API response to match the expected frontend structure
        availableUsers.value = response.data.map(user => ({
          id: user.UserId,
          name: user.UserName,
          role: user.role
        }));
        console.log('Fetched users:', availableUsers.value);
        } catch (err) {
        console.error('Failed to fetch users:', err);
        // Keep empty array if fetch fails
        availableUsers.value = [];
      }
    };
    

    
    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    // Truncate long text
    const truncateText = (text, maxLength) => {
      if (!text) return 'N/A';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };
    
    // Export audit findings
    const exportAuditFindings = async () => {
      isExporting.value = true;
      
      // Determine what to export - current filtered findings
      const dataToExport = findings.value;
      
      try {
        const response = await axios.post('http://localhost:8000/api/audit-findings/export/', {
          file_format: exportFormat.value,
          data: JSON.stringify(dataToExport),
          user_id: 'audit_user', // You might want to get this from your auth system
          options: JSON.stringify({
            filters: {
              filterStatus: filterStatus.value,
              sortBy: sortBy.value
            }
          })
        });
        
        console.log('Export successful:', response.data);
        
        // Check if we have a file URL
        if (response.data && response.data.file_url) {
          // Create a temporary anchor to trigger download
          const link = document.createElement('a');
          link.href = response.data.file_url;
          link.setAttribute('download', response.data.file_name || `audit_findings.${exportFormat.value}`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          // Show success popup
          PopupService.success('Export completed successfully');
        }
        
      } catch (err) {
        console.error('Export failed:', err);
        PopupService.error('Export failed. Please try again.');
      } finally {
        isExporting.value = false;
      }
    };
    
    // Dropdown methods
    const toggleActionDropdown = (index) => {
      if (dropdownOpenFor.value === index) {
        dropdownOpenFor.value = null;
        return;
      }
      
      dropdownOpenFor.value = index;
    };
    
    const closeAllDropdowns = () => {
      dropdownOpenFor.value = null;
    };

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest('.actions-dropdown')) {
        closeAllDropdowns();
      }
    };
    
    const handleDropdownAction = (action, item) => {
      closeAllDropdowns();
      
      switch (action) {
        case 'view':
          viewDetails(item);
          break;
        case 'assign':
          openAssignModal(item);
          break;
        case 'escalate':
          openSolveModal(item);
          break;
        case 'reject':
          openRejectModal(item);
          break;
      }
    };
    
    onMounted(() => {
      fetchData();
      fetchUsers();
      
      // Close dropdowns when clicking outside
      document.addEventListener('click', handleClickOutside);
    });

    // Cleanup on unmount
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside);
    });
    
    return {
      findings,
      loading,
      error,
      summary,
      
      // Modal and workflow state
      showModal,
      modalAction,
      selectedIncident,
      showAssignmentWorkflow,
      
      // Assignment related data
      selectedAssigner,
      selectedReviewer,
      assignmentNotes,
      availableUsers,
      
      // Mitigation workflow data
      mitigationSteps,
      newMitigationStep,
      mitigationDueDate,

      filterStatus,
      sortBy,
      exportFormat,
      isExporting,
      
      // Dropdown state
      dropdownOpenFor,
      
      // Search query
      searchQuery,
      
      fetchData,
      fetchUsers,
      applyFilters,
      filterByStatus,
      getRowClass,
      getStatusClass,
      viewDetails,
      
      // Dropdown methods
      toggleActionDropdown,
      closeAllDropdowns,
      handleDropdownAction,
      
      // Modal and workflow methods
      openSolveModal,
      openRejectModal,
      openAssignModal,
      closeModal,
      closeAssignmentWorkflow,
      addMitigationStep,
      removeMitigationStep,
      getTodayDate,
      loadExistingMitigations,
      confirmAssignmentWorkflow,
      confirmSolve,
      confirmReject,

      formatDate,
      truncateText,
      exportAuditFindings
    };
  }
};
</script>

<style scoped>
@import './AuditFindings.css';
</style> 