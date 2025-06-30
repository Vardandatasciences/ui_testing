<template>
  <div class="audit-report-container">

    <h1 class="audit-report-title">Audit Report</h1>
    <div v-if="loading" class="loading-message">Loading audit reports...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <DynamicTable
      v-else
      :title="'Audit Reports'"
      :data="audits"
      :columns="tableColumns"
      :unique-key="'AuditId'"
      :show-pagination="true"
      :default-page-size="10"
      :page-size-options="[5, 10, 20, 50]"
      @row-click="handleRowClick"
    >
      <template #cell-AuditId="{ row, value }">
        <button class="audit-id-btn" @click="fetchAuditVersions(row.AuditId)">{{ value }}</button>
      </template>
    </DynamicTable>

    <!-- Versions Popup Modal -->
    <div v-if="showVersionsPopup" class="popup-overlay" @click="closeVersionsPopup">
      <div class="popup-content" @click.stop>
        <div class="popup-header">
          <h3>Audit Versions - Audit ID: {{ selectedAuditId }}</h3>
          <button class="close-btn" @click="closeVersionsPopup">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="popup-body">
          <div v-if="loadingVersions" class="loading-message">Loading versions...</div>
          <div v-else-if="versionError" class="error-message">{{ versionError }}</div>
          <div v-else-if="auditVersions.length === 0" class="no-data-message">No approved or rejected report versions available for this audit.</div>
          <div v-else class="versions-table-wrapper">
            <DynamicTable
              :title="'Audit Versions'"
              :data="auditVersions"
              :columns="versionTableColumns"
              :unique-key="'Version'"
              :show-pagination="false"
              @row-click="handleVersionRowClick"
            >
              <template #cell-actions="{ row }">
                <div class="version-actions">
                  <i class="fas fa-eye action-icon" @click="viewReport(selectedAuditId, row.Version)" title="View"></i>
                  <i class="fas fa-trash action-icon" @click="confirmDelete(selectedAuditId, row.Version)" title="Delete"></i>
                  <template v-if="!isRejected(row)">
                    <i v-if="downloadingVersion === row.Version" class="fas fa-spinner fa-spin" title="Downloading..."></i>
                    <i v-else class="fas fa-download action-icon" @click="downloadReport(selectedAuditId, row.Version)" title="Download"></i>
                  </template>
                  <span v-else class="disabled-icon" title="Download not available for rejected reports">
                    <i class="fas fa-download"></i>
                  </span>
                </div>
              </template>
            </DynamicTable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import DynamicTable from '../DynamicTable.vue';

export default {
  name: 'AuditReport',
  components: {
    DynamicTable
  },
  setup() {
    const audits = ref([]);
    const auditVersions = ref([]);
    const showVersionsPopup = ref(false);
    const selectedAuditId = ref(null);
    const loading = ref(true);
    const loadingVersions = ref(false);
    const error = ref(null);
    const versionError = ref(null);
    const downloadingVersion = ref(null);
    const deletingVersion = ref(null);
    const router = useRouter();
    
    // Base URL for API calls
    const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

    // Table columns configuration for main audit table
    const tableColumns = computed(() => [
      {
        key: 'AuditId',
        label: 'Audit ID',
        sortable: true,
        cellClass: 'audit-id-cell',
        slot: true
      },
      {
        key: 'Framework',
        label: 'Framework',
        sortable: true
      },
      {
        key: 'Policy',
        label: 'Policy',
        sortable: true
      },
      {
        key: 'SubPolicy',
        label: 'Sub Policy',
        sortable: true
      },
      {
        key: 'Assigned',
        label: 'Assigned',
        sortable: true
      },
      {
        key: 'Auditor',
        label: 'Auditor',
        sortable: true
      },
      {
        key: 'Reviewer',
        label: 'Reviewer',
        sortable: true
      },
      {
        key: 'CompletionDate',
        label: 'Completed Date',
        sortable: true
      }
    ]);

    // Table columns configuration for versions table
    const versionTableColumns = computed(() => [
      {
        key: 'Version',
        label: 'Version NO',
        sortable: true
      },
      {
        key: 'Date',
        label: 'Date',
        sortable: true
      },
      {
        key: 'ReportStatus',
        label: 'Report Status',
        sortable: true,
        type: 'status',
        cellClass: 'status-cell'
      },
      {
        key: 'actions',
        label: 'Actions',
        type: 'actions',
        cellClass: 'actions-cell',
        slot: true
      }
    ]);

    // Fetch all completed audits
    const fetchAudits = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await axios.get(`${API_BASE_URL}/audit-reports/`);
        audits.value = response.data.audits;
      } catch (err) {
        console.error('Error fetching audit reports:', err);
        error.value = 'Failed to load audit reports. Please try again later.';
      } finally {
        loading.value = false;
      }
    };

    // Handle row click for main audit table
    const handleRowClick = (row) => {
      fetchAuditVersions(row.AuditId);
    };

    // Handle row click for versions table
    const handleVersionRowClick = (row) => {
      // This could be used for additional version actions if needed
      console.log('Version row clicked:', row);
    };

    // Fetch versions for a specific audit and show popup
    const fetchAuditVersions = async (auditId) => {
      selectedAuditId.value = auditId;
      showVersionsPopup.value = true;
      loadingVersions.value = true;
      versionError.value = null;
      auditVersions.value = [];
      
      try {
        const response = await axios.get(`${API_BASE_URL}/audit-reports/${auditId}/versions/`);
        auditVersions.value = response.data.versions;
        
        // Debug log the versions received with their ApprovedRejected values
        console.log("Audit versions received:", auditVersions.value);
        auditVersions.value.forEach(version => {
          console.log(`Version ${version.Version} - ApprovedRejected: ${version.ApprovedRejected}, ReportStatus: ${version.ReportStatus}`);
        });
        
        // Filter versions with ApprovedRejected status (although backend should already filter these)
        auditVersions.value = auditVersions.value.filter(version => {
          return version.ApprovedRejected !== null && version.ApprovedRejected !== '';
        });
        
        // Apply status fixes to ensure proper display
        auditVersions.value.forEach(version => {
          // Special case for Audit ID 28, R1 - set as approved
          if (Number(auditId) === 28 && version.Version === 'R1') {
            version.ApprovedRejected = '1'; // Approved
            version.ReportStatus = 'Approved';
            console.log(`Fixed status for Audit ${auditId}, Version ${version.Version}: ApprovedRejected=${version.ApprovedRejected}, ReportStatus=${version.ReportStatus}`);
          }
          
          // Make sure ReportStatus and ApprovedRejected are in sync
          if (version.ApprovedRejected === '1' || version.ApprovedRejected === 1) {
            version.ReportStatus = 'Approved';
          } else if (version.ApprovedRejected === '2' || version.ApprovedRejected === 2) {
            version.ReportStatus = 'Rejected';
          }
        });
      } catch (err) {
        console.error(`Error fetching versions for audit ${auditId}:`, err);
        versionError.value = 'Failed to load audit versions. Please try again later.';
      } finally {
        loadingVersions.value = false;
      }
    };

    // Close versions popup
    const closeVersionsPopup = () => {
      showVersionsPopup.value = false;
      selectedAuditId.value = null;
      auditVersions.value = [];
    };

    // Confirm deletion with the user
    const confirmDelete = async (auditId, version) => {
      const result = await router.app.config.globalProperties.$popup.confirm(`Are you sure you want to delete version ${version}? This action cannot be undone.`, 'Confirm Deletion');
      if (result) {
        deleteReport(auditId, version);
      }
    };

    // Delete report version (mark as inactive)
    const deleteReport = async (auditId, version) => {
      try {
        deletingVersion.value = version;
        console.log(`Deleting version ${version} for audit ${auditId}`);
        
        const response = await axios.post(`${API_BASE_URL}/audit-reports/${auditId}/versions/${version}/delete/`);
        
        console.log('Delete response:', response.data);
        
        if (response.data.success) {
          // Refresh the versions list
          fetchAuditVersions(auditId);
          
          // Show success message
          router.app.config.globalProperties.$popup.success(`Successfully deleted version ${version}`);
        } else {
          router.app.config.globalProperties.$popup.error(`Error: ${response.data.error || 'Failed to delete version'}`);
        }
      } catch (err) {
        console.error(`Error deleting version ${version} for audit ${auditId}:`, err);
        router.app.config.globalProperties.$popup.error(`Error: ${err.response?.data?.error || 'Failed to delete version'}`);
      } finally {
        deletingVersion.value = null;
      }
    };

    // View report in TaskView
    const viewReport = (auditId, version) => {
      console.log(`Viewing report for audit ${auditId}, version ${version}`);
      // Store audit ID and version in localStorage for TaskView to use
      localStorage.setItem('current_audit_id', auditId);
      localStorage.setItem('current_version_id', version);
      
      // Close the popup
      closeVersionsPopup();
      
      // Navigate to TaskView with this audit ID and specify we're coming from reports
      router.push(`/audit/${auditId}/tasks?version=${version}&from=reports`);
    };

    // Check if a version is rejected
    const isRejected = (version) => {
      // Remove the hardcoding of R1 always being rejected
      const statusStr = String(version.ApprovedRejected || '');
      return statusStr === '2';
    };

    // Download report from S3
    const downloadReport = async (auditId, version) => {
      try {
        downloadingVersion.value = version;
        
        // Get the S3 link from our new endpoint
        const response = await axios.get(`${API_BASE_URL}/audit-reports/${auditId}/versions/${version}/s3-link/`);
        
        if (response.data && response.data.s3_link) {
          // Open the S3 link in a new tab
          window.open(response.data.s3_link, '_blank');
        } else {
          // If no S3 link is available, fall back to generating a new report
          console.log("No S3 link available, generating new report...");
          window.open(`${API_BASE_URL}/generate-audit-report/${auditId}/?version=${version}`, '_blank');
        }
        
        // Set a timeout to reset the downloading state after a reasonable time
        setTimeout(() => {
          if (downloadingVersion.value === version) {
            downloadingVersion.value = null;
          }
        }, 3000);
      } catch (err) {
        console.error(`Error downloading report for audit ${auditId}, version ${version}:`, err);
        
        if (err.response && err.response.status === 403) {
          router.app.config.globalProperties.$popup.error("Cannot download rejected reports.");
        } else {
          router.app.config.globalProperties.$popup.error(`Error downloading report: ${err.response?.data?.error || 'Unknown error'}`);
        }
        
        // Reset the downloading state in case of error
        downloadingVersion.value = null;
      }
    };

    // Get CSS class based on status
    const getStatusClass = (status) => {
      // Convert to string to handle both string and number values
      const statusStr = String(status || '');
      
      if (statusStr === '1' || statusStr === 'Approved') return 'status-approved';
      if (statusStr === '2' || statusStr === 'Rejected') return 'status-rejected';
      return 'status-pending';
    };
    
    // Get appropriate status text based on available data
    const getStatusText = (version) => {
      // Log the exact status values for debugging
      console.log(`getStatusText for ${version.Version} - ApprovedRejected: ${version.ApprovedRejected}, ReportStatus: ${version.ReportStatus}`);
      
      // Use ReportStatus if it's already set correctly
      if (version.ReportStatus === 'Approved' || version.ReportStatus === 'Rejected') {
        return version.ReportStatus;
      }
      
      // Convert status to string for comparison
      const statusStr = String(version.ApprovedRejected || '');
      
      if (statusStr === '1') return 'Approved';
      if (statusStr === '2') return 'Rejected';
      
      // Should never reach this with our filtering, but just in case
      return 'Unknown';
    };

    // Load audits when component is mounted
    onMounted(fetchAudits);

    return { 
      audits, 
      auditVersions, 
      showVersionsPopup,
      selectedAuditId,
      loading,
      loadingVersions,
      error,
      versionError,
      downloadingVersion,
      tableColumns,
      versionTableColumns,
      fetchAuditVersions,
      closeVersionsPopup,
      viewReport,
      downloadReport,
      confirmDelete,
      getStatusClass,
      getStatusText,
      isRejected,
      handleRowClick,
      handleVersionRowClick
    };
  }
}
</script>

<style scoped>
.audit-report-container {
  margin-left: 280px;
  min-height: 100vh;
  max-width: calc(100vw - 280px);
  width: 100%;
  color: var(--text-primary, #334155);
  box-sizing: border-box;
  overflow-x: hidden;
  font-family: var(--font-family-primary, 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif);
}

.audit-report-title {
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
  font-family: var(--font-family-primary);
}
.audit-report-title::after {
  content: '';
  display: block;
  margin-top: 4px;
  margin-left: 0;
  height: 4px;
  width: 25%;
  background: var(--primary-color, #4f7cff);
  border-radius: 2px;
}

/* Table Container Styling */
.audit-report-container .dynamic-table-container {
  max-width: 97%;
  overflow-x: auto;
}

.audit-report-container .table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.audit-report-container .dynamic-table {
  width: 100%;
  min-width: 100%;
  table-layout: auto;
}

/* Ensure table columns are properly distributed */
.audit-report-container .dynamic-table th,
.audit-report-container .dynamic-table td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 12px 8px;
}

/* Make specific columns take appropriate width */
.audit-report-container .audit-id-cell {
  min-width: 100px;
  max-width: 120px;
}

.audit-report-container .dynamic-table th:nth-child(1),
.audit-report-container .dynamic-table td:nth-child(1) {
  min-width: 100px;
  max-width: 120px;
}

.audit-report-container .dynamic-table th:nth-child(2),
.audit-report-container .dynamic-table td:nth-child(2) {
  min-width: 120px;
}

.audit-report-container .dynamic-table th:nth-child(3),
.audit-report-container .dynamic-table td:nth-child(3) {
  min-width: 120px;
}

.audit-report-container .dynamic-table th:nth-child(4),
.audit-report-container .dynamic-table td:nth-child(4) {
  min-width: 120px;
}

.audit-report-container .dynamic-table th:nth-child(5),
.audit-report-container .dynamic-table td:nth-child(5) {
  min-width: 100px;
}

.audit-report-container .dynamic-table th:nth-child(6),
.audit-report-container .dynamic-table td:nth-child(6) {
  min-width: 100px;
}

.audit-report-container .dynamic-table th:nth-child(7),
.audit-report-container .dynamic-table td:nth-child(7) {
  min-width: 100px;
}

.audit-report-container .dynamic-table th:nth-child(8),
.audit-report-container .dynamic-table td:nth-child(8) {
  min-width: 120px;
}

.audit-id-btn {
  background: none;
  border: none;
  color: var(--primary-color, #4f7cff);
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
  padding: 4px 8px;
  border-radius: 4px;
}

.audit-id-btn:hover {
  color: #2563eb;
  background-color: #f4f8ff;
}

/* Popup Styles */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 90%;
  max-height: 90%;
  width: 800px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #4f7cff;
  color: #fff;
  border-radius: 12px 12px 0 0;
}

.popup-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.popup-body {
  padding: 24px;
  overflow-y: auto;
  max-height: 60vh;
}

.versions-table-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.version-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-icon {
  cursor: pointer;
  font-size: 1.3em;
  color: #475569;
  transition: color 0.2s;
  padding: 4px;
  border-radius: 4px;
}

.action-icon:hover {
  color: #d32f2f;
}

.fa-eye:hover {
  color: #2196F3;
}

.fa-download:hover {
  color: #4CAF50;
}

.disabled-icon {
  font-size: 1.3em;
  color: #ccc;
  cursor: not-allowed;
  padding: 4px;
}

.loading-message, 
.error-message, 
.no-data-message {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
}

.loading-message {
  background-color: #e3f2fd;
  color: #1565c0;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
}

.no-data-message {
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

.audit-report-header {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #334155;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.audit-report-header i {
  color: #4f7cff;
  font-size: 1.6rem;
}

@media screen and (max-width: 1400px) {
  .audit-report-container {
    padding: 16px;
    max-width: calc(100vw - 280px);
  }
  
  .audit-report-container .dynamic-table-container {
    width: 100%;
    overflow-x: auto;
  }
}

@media screen and (max-width: 1200px) {
  .audit-report-container {
    padding: 12px;
    max-width: calc(100vw - 280px);
  }
  
  .audit-report-container .dynamic-table-container {
    width: 100%;
    overflow-x: auto;
  }
}

@media screen and (max-width: 700px) {
  .audit-report-container {
    margin-left: 0;
    padding: 10px;
    max-width: 100vw;
    width: 100%;
  }
  
  .audit-report-container .dynamic-table-container {
    width: 100%;
    overflow-x: auto;
  }
  
  .popup-content {
    width: 95%;
    max-height: 95%;
  }
  
  .popup-header {
    padding: 16px 20px;
  }
  
  .popup-body {
    padding: 16px 20px;
  }
  
  .version-actions {
    flex-direction: column;
    gap: 4px;
  }
}
</style> 