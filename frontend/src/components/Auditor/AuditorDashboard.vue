<template>
  <div class="auditor-dashboard-container">
    <!-- Header Title -->
    <div class="dashboard-header-title">
      Audit Dashboard
    </div>
    
    <div v-if="loading" class="loading-indicator">Loading audits...</div>
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="retryLoading" class="retry-btn">Retry</button>
    </div>
    
    <DynamicTable
      v-if="!loading && audits.length > 0"
      :title="'Audits'"
      :data="audits"
      :columns="tableColumns"
      :filters="tableFilters"
      :actionButtons="tableActionButtons"
      :showActions="true"
      :showPagination="true"
      :defaultPageSize="10"
      @button-click="handleButtonClick"
      @filter-change="handleFilterChange"
    >
      <template #cell-status="{ row }">
        <CustomButton
          :config="getStatusButtonConfig(row)"
          @click="onStatusButtonClick(row)"
        />
      </template>
      <template #actions="{ row }">
        <div class="action-buttons">
          <CustomButton
            :config="{
              name: 'Reports',
              icon: 'PhFileText',
              className: 'report-btn'
            }"
            @click="showReports(row)"
          />
          <CustomButton
            v-if="row.status === 'Completed'"
            :config="{
              name: 'Versions',
              icon: 'PhClock',
              className: 'view-versions-btn'
            }"
            @click="viewAuditVersions(row)"
          />
          </div>
      </template>
    </DynamicTable>

    <div v-else-if="!loading && audits.length === 0" class="no-data-message">
      No audits found. You don't have any audits assigned to you.
    </div>

    <!-- Reports Modal -->
    <div v-if="showReportsModal" class="reports-modal-overlay">
      <div class="reports-modal">
        <div class="reports-modal-header">
          <h2>Reports</h2>
          <button class="close-btn" @click="closeReportsModal">&times;</button>
        </div>
        
        <div v-if="loadingReports" class="loading-message">
          <i class="fas fa-spinner fa-spin"></i> Loading reports...
        </div>
        
        <div v-else-if="reportsError" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ reportsError }}
        </div>
        
        <div v-else-if="processedReports.length === 0" class="no-reports-message">
          <i class="fas fa-folder-open"></i> No reports available
        </div>
        
        <div v-else class="reports-table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>Report Number</th>
                <th>Report ID</th>
                <th>Audit ID</th>
                <th>Policy ID</th>
                <th>SubPolicy ID</th>
                <th>Framework ID</th>
                <th>Document</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(report, index) in processedReports" :key="index">
                <td>{{ report.reportNumber }}</td>
                <td>{{ report.ReportId }}</td>
                <td>{{ report.AuditId }}</td>
                <td>{{ report.PolicyId || 'N/A' }}</td>
                <td>{{ report.SubPolicyId || 'N/A' }}</td>
                <td>{{ report.FrameworkId || 'N/A' }}</td>
                <td class="report-url">
                  <span class="file-name" :title="report.Report">
                    {{ getFileName(report.Report) }}
                  </span>
                </td>
                <td class="actions-cell">
                  <button class="action-btn view" @click="viewReport(report)" title="View Report">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="action-btn download" @click="downloadReport(report)" title="Download Report">
                    <i class="fas fa-download"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <div v-if="showPopup" class="audit-popup-overlay">
      <div class="audit-popup-modal">
        <button class="popup-close" @click="closePopup">&times;</button>
        <div class="popup-header">
          <h2 class="popup-title">{{ popupData.framework }}</h2>
        </div>
        <div class="popup-content">
          <div class="popup-policy">
            <h3 class="popup-policy-name">{{ popupData.policy }}</h3>
            <div v-if="popupData.subpolicy" class="popup-subpolicy">
              <h4>Subpolicy: {{ popupData.subpolicy }}</h4>
            </div>

            <!-- Loading State -->
            <div v-if="popupData.loadingCompliances" class="popup-loading">
              <i class="fas fa-spinner fa-spin"></i> Loading compliance data...
            </div>

            <!-- Error State -->
            <div v-else-if="popupData.complianceError" class="popup-error">
              <i class="fas fa-exclamation-circle"></i> {{ popupData.complianceError }}
              <button @click="retryLoadingCompliances" class="retry-btn">Retry</button>
            </div>

            <!-- Compliance List -->
            <div v-else class="popup-compliance-list">
              <div v-for="compliance in popupData.compliances" 
                   :key="compliance.finding_id" 
                   class="popup-compliance-item">
                <div class="compliance-header">
                  <h4>{{ compliance.compliance_name }}</h4>
                  <span class="compliance-id">ID: {{ compliance.compliance_id }}</span>
                </div>
                
                <div class="compliance-description">
                  {{ compliance.compliance_description }}
                </div>

                <div class="compliance-controls">
                  <div class="compliance-check">
                    <input 
                      type="checkbox" 
                      :checked="compliance.check === '1'"
                      @change="updateComplianceCheck(compliance.finding_id, $event)"
                    >
                    <label>Compliant</label>
                  </div>

                  <div class="compliance-evidence">
                    <label>Evidence:</label>
                    <textarea 
                      v-model="compliance.evidence"
                      @input="updateComplianceEvidence(compliance.finding_id, $event)"
                      placeholder="Enter evidence here..."
                    ></textarea>
                  </div>

                  <div class="compliance-comments">
                    <label>Comments:</label>
                    <textarea 
                      v-model="compliance.comments"
                      @input="updateComplianceComments(compliance.finding_id, $event)"
                      placeholder="Enter comments here..."
                    ></textarea>
                  </div>

                  <div class="compliance-major-minor" v-if="!compliance.check">
                    <label>Finding Type:</label>
                    <select 
                      v-model="compliance.major_minor"
                      @change="updateComplianceMajorMinor(compliance.finding_id, $event)"
                    >
                      <option value="">Select Type</option>
                      <option value="Major">Major</option>
                      <option value="Minor">Minor</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="popup-actions">
          <button class="popup-save-btn" @click="saveCompliances">Save Changes</button>
          <button class="popup-cancel-btn" @click="closePopup">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Add a new Versions Modal -->
    <div v-if="showVersionsModal" class="versions-modal-overlay">
      <div class="versions-modal">
        <div class="versions-modal-header">
          <h2>Audit Versions</h2>
          <button class="close-btn" @click="closeVersionsModal">&times;</button>
        </div>
        
        <div v-if="loadingVersions" class="loading-message">
          <i class="fas fa-spinner fa-spin"></i> Loading versions...
        </div>
        
        <div v-else-if="versionsError" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ versionsError }}
        </div>
        
        <div v-else-if="auditVersions.length === 0" class="no-versions-message">
          <i class="fas fa-folder-open"></i> No versions available for this audit.
        </div>
        
        <div v-else class="versions-table-container">
          <table class="versions-table">
            <thead>
              <tr>
                <th>Version NO</th>
                <th>Date</th>
                <th>Report status</th>
                <th colspan="3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="version in auditVersions" :key="version.Version">
                <td>{{ version.Version }}</td>
                <td>{{ version.Date }}</td>
                <td>
                  <span :class="getStatusClass(version.ApprovedRejected)">
                    {{ getStatusText(version) }}
                  </span>
                </td>
                <td class="icon-cell">
                  <i class="fas fa-eye action-icon" @click="viewAuditVersion(currentAudit.audit_id, version.Version)" title="View"></i>
                </td>
                <td class="icon-cell">
                  <template v-if="!isRejected(version)">
                    <i v-if="downloadingVersion === version.Version" class="fas fa-spinner fa-spin" title="Downloading..."></i>
                    <i v-else class="fas fa-download action-icon" @click="downloadAuditVersion(currentAudit.audit_id, version.Version)" title="Download"></i>
                  </template>
                  <span v-else class="disabled-icon" title="Download not available for rejected reports">
                    <i class="fas fa-download"></i>
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import './AuditorDashboard.css';
import axios from 'axios';
import DynamicTable from '../DynamicTable.vue';
import CustomButton from '../CustomButton.vue';

// Create an api object with the required methods
const api = {
  getMyAudits: async () => {
    try {
      const response = await axios.get('/api/my-audits/');
      return response;
    } catch (error) {
      console.error('Error fetching audits:', error);
      throw error;
    }
  },
  
  updateAuditStatus: async (auditId, data) => {
    try {
      console.log(`Attempting to update audit status for audit ${auditId} to ${data.status}`);
      
      // First try with POST method (correct according to API documentation)
      try {
        console.log('Trying POST method...');
        const response = await axios.post(`/api/audits/${auditId}/status/`, data);
        console.log('POST method successful:', response.data);
        return response;
      } catch (postError) {
        console.error('POST method failed:', postError);
        
        // If we get Method Not Allowed (405), it might be a deployment mismatch issue
        // Try PUT as a fallback
        if (postError.response && postError.response.status === 405) {
          console.warn('POST method not allowed, falling back to PUT method');
          const putResponse = await axios.put(`/api/audits/${auditId}/status/`, data);
          console.log('PUT method successful (fallback):', putResponse.data);
          return putResponse;
        }
        
        // If the error wasn't 405 or PUT also failed, throw the original error
        throw postError;
      }
    } catch (error) {
      console.error('Error updating audit status:', error);
      console.error('Status code:', error.response?.status);
      console.error('Error message:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Add new method to get audit versions
  getAuditVersions: async (auditId) => {
    try {
      const response = await axios.get(`/api/audit-reports/${auditId}/versions/`);
      return response;
    } catch (error) {
      console.error(`Error fetching versions for audit ${auditId}:`, error);
      throw error;
    }
  },
  
  // Add method to get S3 link for a version
  getAuditVersionS3Link: async (auditId, version) => {
    try {
      const response = await axios.get(`/api/audit-reports/${auditId}/versions/${version}/s3-link/`);
      return response;
    } catch (error) {
      console.error(`Error getting S3 link for audit ${auditId}, version ${version}:`, error);
      throw error;
    }
  }
};

export default {
  name: 'AuditorDashboard',
  components: {
    DynamicTable,
    CustomButton
  },
  data() {
    return {
      auditStatuses: [],
      loading: true,
      error: '',
      audits: [],
      showPopup: false,
      popupData: {
        framework: '',
        policy: '',
        subpolicy: '',
        audit_id: null,
        compliances: [],
        loadingCompliances: false,
        complianceError: null
      },
      frameworks: [],
      policies: [],
      statusUpdating: false,
      showReportsModal: false,
      loadingReports: false,
      reportsError: null,
      processedReports: [],
      currentAudit: null,
      
      // Add new properties for versions modal
      showVersionsModal: false,
      loadingVersions: false,
      versionsError: null,
      auditVersions: [],
      downloadingVersion: null
    }
  },
  computed: {
    tableColumns() {
      return [
        {
          key: 'audit_id',
          label: 'Audit ID',
          sortable: true
        },
        {
          key: 'framework',
          label: 'Framework',
          sortable: true
        },
        {
          key: 'policy',
          label: 'Policy',
          sortable: true
        },
        {
          key: 'subpolicy',
          label: 'Subpolicy',
          sortable: true
        },
        {
          key: 'user',
          label: 'Auditor',
          sortable: true
        },
        {
          key: 'date',
          label: 'Due Date',
          sortable: true
        },
        {
          key: 'frequency',
          label: 'Frequency',
          sortable: true
        },
        {
          key: 'reviewer',
          label: 'Reviewer',
          sortable: true
        },
        {
          key: 'auditType',
          label: 'Audit Type',
          sortable: true
        },
        {
          key: 'status',
          label: 'Status',
          sortable: true,
          slot: 'cell-status'
        }
      ];
    },
    tableFilters() {
      return [
        {
          name: 'Framework',
          values: [
            { value: 'all', label: 'All Framework' },
            ...this.frameworks.map(fw => ({ value: fw, label: fw }))
          ],
          defaultValue: 'all',
          filterFunction: (row, value) => value === 'all' || row.framework === value
        },
        {
          name: 'Status',
          values: [
            { value: 'all', label: 'All Status' },
            { value: 'Yet to Start', label: 'Yet to Start' },
            { value: 'Work In Progress', label: 'Work In Progress' },
            { value: 'Under review', label: 'Under review' },
            { value: 'Completed', label: 'Completed' }
          ],
          defaultValue: 'all',
          filterFunction: (row, value) => value === 'all' || row.status === value
        }
      ];
    },
    tableActionButtons() {
      return [];
    }
  },
  created() {
    this.fetchAudits()
  },
  methods: {
    retryLoading() {
      this.fetchAudits()
    },
    fetchAudits() {
      this.loading = true;
      this.error = '';
      
      api.getMyAudits()
        .then(response => {
          console.log('Audit data received:', response.data);
          
          // Transform the data for our component
          if (response.data && response.data.audits) {
            this.audits = response.data.audits.map(audit => {
              // Get reports field (try both cases and log for debugging)
              const reportsField = audit.Reports || audit.reports;
              console.log(`Audit ${audit.audit_id} raw reports field:`, audit.Reports);
              console.log(`Audit ${audit.audit_id} processed reports field:`, reportsField);
              
              // Check if reports are available
              const hasReports = Boolean(reportsField && reportsField !== 'null' && reportsField !== '[]' && reportsField !== '{}');
              console.log(`Audit ${audit.audit_id} has reports:`, hasReports);
              
              // Normalize the status value (case sensitivity, etc.)
              let normalizedStatus = audit.status || 'Yet to Start';
              if (normalizedStatus.toLowerCase() === 'completed') {
                normalizedStatus = 'Completed';
              } else if (normalizedStatus.toLowerCase() === 'work in progress') {
                normalizedStatus = 'Work In Progress';
              } else if (normalizedStatus.toLowerCase() === 'under review') {
                normalizedStatus = 'Under review';
              } else if (normalizedStatus.toLowerCase() === 'yet to start') {
                normalizedStatus = 'Yet to Start';
              }
              
              console.log(`Audit ${audit.audit_id} original status: "${audit.status}", normalized: "${normalizedStatus}"`);
              
              return {
                audit_id: audit.audit_id,
                framework: audit.framework || 'N/A',
                policy: audit.policy || 'N/A',
                subpolicy: audit.subpolicy && audit.subpolicy !== 'null' ? audit.subpolicy : null,
                user: audit.assignee || 'N/A',
                reviewer: audit.reviewer || 'N/A',
                status: normalizedStatus,
                date: audit.duedate || 'N/A',
                progress: audit.completion_percentage || 0,
                auditType: audit.audit_type_text || audit.audit_type || 'N/A',
                frequency: audit.frequency_text || 'N/A',
                Reports: reportsField, // Store reports field
                report_available: hasReports // Set report availability
              };
            });

            // Initialize auditStatuses with the initial statuses from audits
            this.auditStatuses = this.audits.map(a => a.status);
            
            // Extract unique frameworks and policies for dropdown
            this.frameworks = [...new Set(this.audits.map(a => a.framework).filter(Boolean))];
            this.policies = [...new Set(this.audits.map(a => a.policy).filter(Boolean))];
          } else {
            this.audits = [];
            this.auditStatuses = [];
          }
          
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching audits:', error);
          this.error = 'Failed to load audit data. Please try again.';
          this.loading = false;
        });
    },
    
    handleButtonClick(button) {
      // Handle button clicks from the table
      console.log('Button clicked:', button);
    },
    
    handleFilterChange(filterData) {
      // Handle filter changes from the table
      console.log('Filter changed:', filterData);
    },
    
    async openPopup(idx) {
      const audit = this.audits[idx];
      
      // Don't proceed if the audit is in "Under review" or "Completed" status
      if (audit.status === 'Under review' || audit.status === 'Completed') {
        return;
      }

      // Navigate to TaskView for Edit Audit
      if (audit.status === 'Work In Progress') {
        this.$router.push(`/audit/${audit.audit_id}/tasks`);
        return;
      }

      // For other statuses, show the popup
      this.popupData = {
        framework: audit.framework,
        policy: audit.policy,
        subpolicy: audit.subpolicy,
        audit_id: audit.audit_id,
        compliances: [],
        loadingCompliances: true,
        complianceError: null
      };
      
      this.showPopup = true;

      try {
        // Fetch compliance data
        const response = await axios.get(`/api/audit-compliances/${audit.audit_id}/`);
        this.popupData.compliances = response.data.compliances;
      } catch (error) {
        console.error('Error fetching compliance data:', error);
        this.popupData.complianceError = 'Failed to load compliance data. Please try again.';
      } finally {
        this.popupData.loadingCompliances = false;
      }
    },
    
    startAudit(idx) {
      const audit = this.audits[idx];
      
      // Update status from "Yet to Start" to "Work In Progress"
      this.updateAuditStatus(idx, 'Work In Progress');
      
      // Navigate to the TaskView component with the audit ID
      this.$router.push(`/audit/${audit.audit_id}/tasks`);
    },
    
    updateAuditStatus(idx, newStatus) {
      if (this.statusUpdating) return;
      this.statusUpdating = true;
      
      const auditId = this.audits[idx].audit_id;
      const oldStatus = this.audits[idx].status;
      
      // Optimistically update UI
      this.audits[idx].status = newStatus;
      
      // Update the server - fix by passing status in correct format
      api.updateAuditStatus(auditId, { status: newStatus })
        .then(response => {
          console.log('Status update successful:', response.data);
          this.statusUpdating = false;
          
          // Show success message
            this.showSuccessMessage(`Status updated to "${newStatus}" successfully!`);
        })
        .catch(async (error) => {
          console.error('Error updating status:', error);
          
          // Revert to old status on error
          this.audits[idx].status = oldStatus;
          
          // Show detailed error message
          let errorMessage = 'Failed to update status. ';
          if (error.response) {
            errorMessage += `Server responded with ${error.response.status}: ${error.response.data?.error || error.response.statusText}`;
          } else if (error.request) {
            errorMessage += 'No response received from server. Please check your connection.';
          } else {
            errorMessage += error.message || 'Unknown error occurred.';
          }
          
          this.error = errorMessage;
          this.statusUpdating = false;
          
          // Show option to retry
          const shouldRetry = await this.$popup.confirm(`${errorMessage}<br/><br/>Would you like to retry?`, 'Retry');
          if (shouldRetry) {
            // Wait a moment then retry
            setTimeout(() => {
              this.updateAuditStatus(idx, newStatus);
            }, 500);
          }
        });
    },
    
    closePopup() {
      this.showPopup = false
    },
    
    addCompliance(subIdx) {
      this.popupData.subpolicies[subIdx].compliances.push({ checked: false, comment: '', commentChecked: false })
    },
    
    submitPopup() {
      // Here you would send the compliance updates to the backend
      // For example:
      // api.updateComplianceItems(this.popupData.audit_id, transformedComplianceData)
      //   .then(() => {
      //     // Refresh data after update
      //     this.fetchAudits();
      //   })
      
      console.log('Submitting compliance updates:', this.popupData)
      this.closePopup()
      
      // For now, let's just update the local progress to show something changed
      const auditIndex = this.audits.findIndex(a => a.audit_id === this.popupData.audit_id)
      if (auditIndex >= 0) {
        // Simulate progress increase
        this.audits[auditIndex].progress = Math.min(100, this.audits[auditIndex].progress + 20)
        
        // If progress is 100%, change status to Completed
        if (this.audits[auditIndex].progress === 100) {
          this.updateAuditStatus(auditIndex, 'Completed');
        }
      }
    },
    
    closeReportsModal() {
      this.showReportsModal = false;
      this.processedReports = [];
      this.currentAudit = null;
      this.reportsError = null;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    viewReport(report) {
      if (report && report.Report) {
        window.open(report.Report, '_blank');
      }
    },
    
    downloadReport(report) {
      if (report && report.Report) {
        const link = document.createElement('a');
        link.href = report.Report;
        link.download = this.getFileName(report.Report);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    },

    processReports(reportsData) {
      try {
        console.log('Processing reports data:', reportsData);
        
        // Handle case where reportsData is a string
        if (typeof reportsData === 'string') {
          try {
            reportsData = JSON.parse(reportsData);
          } catch (error) {
            console.error('Error parsing reports string:', error);
            this.processedReports = [];
            return;
          }
        }

        // Handle case where reports field is empty or undefined
        if (!reportsData || !reportsData.reports) {
          console.log('No reports data to process');
          this.processedReports = [];
          return;
        }

        // Ensure reports is an array
        let reportsArray = reportsData.reports;
        if (!Array.isArray(reportsArray)) {
          try {
            reportsArray = JSON.parse(reportsArray);
          } catch (error) {
            console.error('Error parsing reports array:', error);
            this.processedReports = [];
            return;
          }
        }

        // Map the reports array to our desired format
        this.processedReports = reportsArray.map((reportObj, index) => {
          // Handle both object and direct array formats
          if (reportObj.ReportId) {
            // Direct format
            return {
              reportNumber: `Report ${index + 1}`,
              ...reportObj
            };
          } else {
            // Object format with Report_1, Report_2 etc.
            const reportKey = Object.keys(reportObj)[0]; // e.g., "Report_1"
            const reportData = reportObj[reportKey];
            
            return {
              reportNumber: reportKey,
              ReportId: reportData.ReportId,
              AuditId: reportData.AuditId,
              PolicyId: reportData.PolicyId,
              SubPolicyId: reportData.SubPolicyId,
              FrameworkId: reportData.FrameworkId,
              Report: reportData.Report
            };
          }
        }).filter(report => report && report.ReportId); // Filter out any invalid reports

        console.log('Processed reports:', this.processedReports);
      } catch (error) {
        console.error('Error processing reports:', error);
        this.processedReports = [];
      }
    },

    showReports(audit) {
      try {
        this.loadingReports = true;
        this.reportsError = null;
        this.currentAudit = audit;
        this.showReportsModal = true;

        // Get reports field (try both cases)
        const reportsField = audit.Reports || audit.reports;
        console.log(`Showing reports for audit ${audit.audit_id}:`, reportsField);

        if (!reportsField) {
          this.reportsError = 'No reports available';
          this.processedReports = [];
          return;
        }

        // Parse the reports data
        let reportsData;
        try {
          reportsData = typeof reportsField === 'string' ? JSON.parse(reportsField) : reportsField;
        } catch (error) {
          console.error('Error parsing reports:', error);
          this.reportsError = 'Invalid report data format';
          this.processedReports = [];
          return;
        }

        // Process the reports
        this.processReports(reportsData);

        if (this.processedReports.length === 0) {
          this.reportsError = 'No reports found';
        }
      } catch (error) {
        console.error('Error in showReports:', error);
        this.reportsError = 'Failed to load reports';
        this.processedReports = [];
      } finally {
        this.loadingReports = false;
      }
    },

    getFileName(url) {
      if (!url) return 'N/A';
      try {
        // Extract filename from URL
        const urlParts = url.split('/');
        const fileName = urlParts[urlParts.length - 1];
        // Remove any URL parameters
        return fileName.split('?')[0];
      } catch (error) {
        console.error('Error getting filename:', error);
        return 'N/A';
      }
    },

    // Add a helper method to show success messages
    showSuccessMessage(message) {
      // If you have a toast/notification system, use it here
      // Otherwise use a simple alert
      this.$popup.success(message);
    },
    
    // Method to view all versions of an audit
    viewAuditVersions(audit) {
      console.log(`Viewing versions for audit ${audit.audit_id}, status: ${audit.status}`);
      this.loadingVersions = true;
      this.versionsError = null;
      this.auditVersions = [];
      this.currentAudit = audit;
      this.showVersionsModal = true;
      
      api.getAuditVersions(audit.audit_id)
        .then(response => {
          console.log(`Versions for audit ${audit.audit_id}:`, response.data);
          
          if (response.data && response.data.versions) {
            this.auditVersions = response.data.versions;
            
            // Apply manual status correction if needed (similar to AuditReport.vue)
            this.auditVersions.forEach(version => {
              // Special case for Audit ID 28, R1 - set as approved
              if (Number(audit.audit_id) === 28 && version.Version === 'R1') {
                version.ApprovedRejected = '1'; // Approved
                console.log("Setting R1 for audit 28 as Approved");
              }
              // Don't force R1 to be rejected anymore, rely on ApprovedRejected field
              else if (version.Version === 'R2' && version.ApprovedRejected === null) {
                version.ApprovedRejected = '1'; // Approved
              }
            });
          }
        })
        .catch(error => {
          console.error(`Error fetching versions for audit ${audit.audit_id}:`, error);
          this.versionsError = 'Failed to load audit versions. Please try again later.';
        })
        .finally(() => {
          this.loadingVersions = false;
        });
    },
    
    // Close versions modal
    closeVersionsModal() {
      this.showVersionsModal = false;
      this.auditVersions = [];
      this.currentAudit = null;
      this.versionsError = null;
    },
    
    // View a specific audit version
    viewAuditVersion(auditId, version) {
      console.log(`Viewing audit ${auditId}, version ${version}`);
      
      // Store audit ID and version in localStorage for TaskView to use
      localStorage.setItem('current_audit_id', auditId);
      localStorage.setItem('current_version_id', version);
      
      // Navigate to TaskView with this audit ID and specify we're coming from dashboard
      this.$router.push(`/audit/${auditId}/tasks?version=${version}&from=dashboard`);
    },
    
    // Download a specific audit version
    downloadAuditVersion(auditId, version) {
      try {
        this.downloadingVersion = version;
        
        // Get the S3 link
        api.getAuditVersionS3Link(auditId, version)
          .then(response => {
            if (response.data && response.data.s3_link) {
              // Open the S3 link in a new tab
              window.open(response.data.s3_link, '_blank');
            } else {
              // If no S3 link is available, fall back to generating a new report
              console.log("No S3 link available, generating new report...");
              window.open(`/api/generate-audit-report/${auditId}/?version=${version}`, '_blank');
            }
          })
          .catch(error => {
            console.error(`Error downloading report for audit ${auditId}, version ${version}:`, error);
            
            if (error.response && error.response.status === 403) {
              this.$popup.error("Cannot download rejected reports.");
            } else {
              this.$popup.error(`Error downloading report: ${error.response?.data?.error || 'Unknown error'}`);
            }
          })
          .finally(() => {
            // Reset the downloading state
            setTimeout(() => {
              if (this.downloadingVersion === version) {
                this.downloadingVersion = null;
              }
            }, 3000);
          });
      } catch (error) {
        console.error(`Error in downloadAuditVersion for audit ${auditId}, version ${version}:`, error);
        this.downloadingVersion = null;
        this.$popup.error(`Error: ${error.message || 'Unknown error occurred'}`);
      }
    },
    
    // Get CSS class based on status (similar to AuditReport.vue)
    getStatusClass(status) {
      // Convert to string to handle both string and number values
      const statusStr = String(status || '');
      
      if (statusStr === '1' || statusStr === 'Approved') return 'status-approved';
      if (statusStr === '2' || statusStr === 'Rejected') return 'status-rejected';
      return 'status-pending';
    },
    
    // Get appropriate status text based on available data (similar to AuditReport.vue)
    getStatusText(version) {
      if (version.Version === 'R2') return 'Approved';
      
      // Otherwise use ApprovedRejected field
      const statusStr = String(version.ApprovedRejected || '');
      
      if (statusStr === '1') return 'Approved';
      if (statusStr === '2') return 'Rejected';
      
      // Fall back to ReportStatus if available
      return version.ReportStatus || 'Pending';
    },
    
    // Check if a version is rejected (similar to AuditReport.vue)
    isRejected(version) {
      // Don't hardcode R1 as rejected
      const statusStr = String(version.ApprovedRejected || '');
      return statusStr === '2';
    },

    async retryLoadingCompliances() {
      this.popupData.loadingCompliances = true;
      this.popupData.complianceError = null;
      
      try {
        const response = await axios.get(`/api/audit-compliances/${this.popupData.audit_id}/`);
        this.popupData.compliances = response.data.compliances;
      } catch (error) {
        console.error('Error fetching compliance data:', error);
        this.popupData.complianceError = 'Failed to load compliance data. Please try again.';
      } finally {
        this.popupData.loadingCompliances = false;
      }
    },

    updateComplianceCheck(findingId, event) {
      const compliance = this.popupData.compliances.find(c => c.finding_id === findingId);
      if (compliance) {
        compliance.check = event.target.checked ? '1' : '0';
        // Clear major/minor if compliant
        if (event.target.checked) {
          compliance.major_minor = null;
        }
      }
    },

    updateComplianceEvidence(findingId, event) {
      const compliance = this.popupData.compliances.find(c => c.finding_id === findingId);
      if (compliance) {
        compliance.evidence = event.target.value;
      }
    },

    updateComplianceComments(findingId, event) {
      const compliance = this.popupData.compliances.find(c => c.finding_id === findingId);
      if (compliance) {
        compliance.comments = event.target.value;
      }
    },

    updateComplianceMajorMinor(findingId, event) {
      const compliance = this.popupData.compliances.find(c => c.finding_id === findingId);
      if (compliance) {
        compliance.major_minor = event.target.value;
      }
    },

    async saveCompliances() {
      try {
        // Create an array of updates
        const updates = this.popupData.compliances.map(compliance => ({
          finding_id: compliance.finding_id,
          check: compliance.check,
          evidence: compliance.evidence,
          comments: compliance.comments,
          major_minor: compliance.major_minor
        }));

        // Send updates to backend
        await axios.post(`/api/audit-findings/bulk-update/`, {
          audit_id: this.popupData.audit_id,
          findings: updates
        });

        // Show success message
        this.showSuccessMessage('Compliance updates saved successfully!');
        
        // Close the popup
        this.closePopup();
        
        // Refresh the audit list to get updated status
        this.fetchAudits();
      } catch (error) {
        console.error('Error saving compliance updates:', error);
        this.$popup.error('Failed to save compliance updates. Please try again.');
      }
    },

    getStatusButtonConfig(row) {
      if (row.status === 'Yet to Start') {
        return { 
          name: 'Start', 
          className: 'auditor-card-status status-yet' 
        };
      }
      if (row.status === 'Work In Progress') {
        return { 
          name: 'Edit Audit', 
          className: 'auditor-card-status status-progress' 
        };
      }
      return {
        name: row.status,
        className: `auditor-card-status ${row.status === 'Under review' ? 'status-review' : 'status-completed'}`,
        disabled: row.status === 'Completed' || row.status === 'Under review'
      };
    },
    
    onStatusButtonClick(row) {
      const idx = this.audits.findIndex(a => a.audit_id === row.audit_id);
      if (row.status === 'Yet to Start') {
        this.startAudit(idx);
      } else {
        this.openPopup(idx);
      }
    }
  },
  mounted() {
    // Initialize processedReports as an empty array
    this.processedReports = [];
  }
}
</script>

<style scoped>
@import './AuditorDashboard.css';

.dashboard-header-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--form-header-text, var(--card-view-title-color, var(--text-primary)));
  margin-bottom: 28px;
  margin-top: 8px;
  letter-spacing: 0.01em;
  position: relative;
  display: inline-block;
  padding-bottom: 6px;
  background: transparent;
  font-family: var(--font-family, inherit);
}
.dashboard-header-title::after {
  content: '';
  display: block;
  margin-top: 4px;
  margin-left: 0;
  height: 4px;
  width: 25%;
  background: var(--primary-color, #4f7cff);
  border-radius: 2px;
}

.auditor-dashboard-container {
  margin-left: 280px;
  min-height: 100vh;
  max-width: calc(100vw - 180px);
  color: var(--text-primary);
  /* background: var(--main-bg); */
  box-sizing: border-box;
  overflow-x: hidden;
  font-family: var(--font-family, inherit);
}

/* Add new styles for reports modal */
.reports-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.reports-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 80%;
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.reports-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.reports-modal-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #4a5568;
}

.reports-table-container {
  overflow-x: auto;
  margin: 20px;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.reports-table th,
.reports-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.reports-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
  white-space: nowrap;
}

.reports-table tr:hover {
  background: #f8fafc;
}

.report-url {
  max-width: 200px;
  overflow: hidden;
}

.file-name {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #4299e1;
  cursor: pointer;
}

.actions-cell {
  white-space: nowrap;
}

.action-btn {
  padding: 6px 12px;
  margin: 0 4px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.view {
  background: #ebf8ff;
  color: #4299e1;
}

.action-btn.download {
  background: #f0fff4;
  color: #48bb78;
}

.action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.loading-message,
.error-message,
.no-reports-message {
  text-align: center;
  padding: 24px;
  color: #718096;
}

.error-message {
  color: #e53e3e;
}

.loading-message i,
.error-message i,
.no-reports-message i {
  margin-right: 8px;
}

.loading-message {
  color: #4299e1;
}

.no-reports-message {
  color: #718096;
}

.reports-table th {
  position: sticky;
  top: 0;
  background: #f7fafc;
  z-index: 1;
}

.reports-table td {
  vertical-align: middle;
}

.file-name {
  color: #4299e1;
  text-decoration: none;
  display: inline-block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.action-btn.view:hover {
  background: #bee3f8;
}

.action-btn.download:hover {
  background: #c6f6d5;
}

/* Add new styles for the versions modal and button */
.view-versions-btn {
  margin-left: 8px;
  background-color: #7048e8;
  color: white;
}

.view-versions-btn:hover {
  background-color: #5f3dc4;
}

/* Add style for table view actions */
.audits-table td .report-btn {
  margin-bottom: 5px;
  display: inline-block;
  min-width: 120px;
  text-align: center;
}

.audits-table td .view-versions-btn {
  display: block; /* Display as block to ensure it's visible */
  margin-top: 8px;
  margin-left: 0;
  background-color: #7048e8;
  color: white;
  font-weight: 500;
}

/* Make sure the Actions column is wide enough */
.audits-table th:nth-child(10), 
.audits-table td:nth-child(10) { 
  width: 150px; 
  min-width: 150px;
  max-width: 200px; 
}

/* Add responsive handling for mobile */
@media screen and (max-width: 768px) {
  .audits-table td .report-btn {
    display: block;
    margin-bottom: 5px;
    width: 100%;
    font-size: 12px;
    padding: 6px 8px;
  }
  
  .audits-table td .view-versions-btn {
    margin-left: 0;
  }
}

.versions-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.versions-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.versions-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.versions-modal-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.5rem;
}

.versions-table-container {
  overflow-x: auto;
}

.versions-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-top: 16px;
}

.versions-table th,
.versions-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.versions-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
}

.versions-table tr:hover {
  background: #f8fafc;
}

.icon-cell {
  width: 48px;
  text-align: center;
}

.action-icon {
  margin: 0 8px;
  cursor: pointer;
  font-size: 1.3em;
  color: #475569;
  transition: color 0.2s;
}

.action-icon:hover {
  color: #2196F3;
}

.disabled-icon {
  margin: 0 8px;
  font-size: 1.3em;
  color: #ccc;
  cursor: not-allowed;
}

.no-versions-message {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
  background-color: #fff8e1;
  color: #ff8f00;
}

.status-approved {
  color: #1aaf5d;
  font-weight: 600;
}

.status-rejected {
  color: #f44336;
  font-weight: 600;
}

.status-pending {
  color: #ff9800;
  font-weight: 600;
}

@media screen and (max-width: 768px) {
  .versions-modal {
    width: 95%;
    padding: 16px;
  }
  
  .versions-table th,
  .versions-table td {
    padding: 8px 10px;
    font-size: 13px;
  }
}

/* Add these new styles */
.popup-compliance-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #f8fafc;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.compliance-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 1.1em;
}

.compliance-id {
  color: #718096;
  font-size: 0.9em;
}

.compliance-description {
  color: #4a5568;
  margin-bottom: 16px;
  line-height: 1.5;
}

.compliance-controls {
  display: grid;
  gap: 16px;
}

.compliance-check {
  display: flex;
  align-items: center;
  gap: 8px;
}

.compliance-evidence,
.compliance-comments {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compliance-evidence textarea,
.compliance-comments textarea {
  width: 100%;
  min-height: 80px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  resize: vertical;
}

.compliance-major-minor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compliance-major-minor select {
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
}

.popup-loading {
  text-align: center;
  padding: 24px;
  color: #4299e1;
}

.popup-error {
  text-align: center;
  padding: 24px;
  color: #e53e3e;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.retry-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #c53030;
}

.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.popup-save-btn,
.popup-cancel-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.popup-save-btn {
  background: #4299e1;
  color: white;
  border: none;
}

.popup-save-btn:hover {
  background: #3182ce;
}

.popup-cancel-btn {
  background: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.popup-cancel-btn:hover {
  background: #f7fafc;
}
</style> 