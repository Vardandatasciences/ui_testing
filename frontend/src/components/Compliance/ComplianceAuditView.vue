<template>
  <div class="compliance-view-container">
    <h1>{{ title }}</h1>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Loading...</span>
    </div>

    <div class="content-wrapper">
      <div class="section-header">
        <span>{{ title }}</span>
        <div class="section-actions">
          <!-- Export Controls -->
          <div class="inline-export-controls">
            <select v-model="selectedFormat" class="format-select">
              <option value="xlsx">Excel (.xlsx)</option>
              <option value="csv">CSV (.csv)</option>
              <option value="pdf">PDF (.pdf)</option>
              <option value="json">JSON (.json)</option>
              <option value="xml">XML (.xml)</option>
            </select>
            <button class="export-btn" @click="handleExport(selectedFormat)">
              <i class="fas fa-download"></i> Export
            </button>
          </div>
          <button class="view-toggle-btn" @click="toggleViewMode">
            <i :class="viewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
            {{ viewMode === 'card' ? 'List View' : 'Card View' }}
          </button>
          <button class="action-btn" @click="goBack">
            <i class="fas fa-arrow-left"></i> Back
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading-spinner">
        <i class="fas fa-circle-notch fa-spin"></i>
        <span>Loading compliances...</span>
      </div>
      
      <div v-else-if="!compliances.length" class="no-data">
        <i class="fas fa-inbox"></i>
        <p>No compliances found</p>
      </div>
      
      <!-- Card View -->
      <div v-else-if="viewMode === 'card'" class="compliances-grid">
        <div v-for="compliance in compliances" 
             :key="compliance.ComplianceId" 
             class="compliance-card">
          <div class="compliance-header">
            <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
              {{ compliance.Criticality }}
            </span>
          </div>
          
          <div class="compliance-body">
            <h3>{{ compliance.ComplianceItemDescription }}</h3>
            
            <div class="clean-details-grid">
              <div class="detail-row">
                <span class="detail-label">Compliance Performed By:</span>
                <span class="detail-value">{{ compliance.audit_performer_name || 'N/A' }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Compliance Approved By:</span>
                <span class="detail-value">{{ compliance.audit_approver_name || 'N/A' }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Completion Date:</span>
                <span class="detail-value">{{ formatDate(compliance.audit_date) }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Completion Status:</span>
                <span class="detail-value" :class="getAuditStatusClass(compliance.audit_findings_status)">
                  <i :class="getAuditStatusIcon(compliance.audit_findings_status)"></i>
                  {{ formatAuditStatus(compliance.audit_findings_status) }}
                </span>
              </div>
            </div>
            
            <div class="compliance-footer">
              <div class="identifier">ID: {{ compliance.Identifier }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- List View -->
      <div v-else class="compliances-list-view">
        <table class="compliances-table">
          <thead>
            <tr>
              <th>Audit Findings ID</th>
              <th>Compliance</th>
              <th>Criticality</th>
              <th>Completion Status</th>
              <th>Compliance Performed By</th>
              <th>Compliance Approved By</th>
              <th>Completion Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="compliance in compliances" :key="compliance.ComplianceId">
              <td class="audit-id">
                <a 
                  v-if="compliance.audit_findings_id" 
                  href="#" 
                  class="audit-id-link"
                  @click.prevent="handleAuditLinkClick(compliance.audit_findings_id)">
                  {{ compliance.audit_findings_id }}
                </a>
                <span v-else>N/A</span>
              </td>
              <td class="compliance-name">{{ compliance.ComplianceItemDescription }}</td>
              <td>
                <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
                  {{ compliance.Criticality }}
                </span>
              </td>
              <td>
                <span :class="getAuditStatusClass(compliance.audit_findings_status)">
                  <i :class="getAuditStatusIcon(compliance.audit_findings_status)"></i>
                  {{ formatAuditStatus(compliance.audit_findings_status) }}
                </span>
              </td>
              <td>{{ compliance.audit_performer_name || 'N/A' }}</td>
              <td>{{ compliance.audit_approver_name || 'N/A' }}</td>
              <td>{{ formatDate(compliance.audit_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

// Get route parameters
const type = ref(route.params.type)
const id = ref(route.params.id)
const name = ref(decodeURIComponent(route.params.name))

// State
const compliances = ref([])
const loading = ref(false)
const error = ref(null)
const selectedFormat = ref('xlsx')
const viewMode = ref('list') // Default to list view

// Computed properties
const title = computed(() => {
  return `Compliance Audit Status - ${name.value}`
})

// Fetch compliances on component mount
onMounted(async () => {
  await fetchCompliances()
})

// Methods
async function fetchCompliances() {
  try {
    loading.value = true
    error.value = null
    
    let endpoint = ''
    switch(type.value) {
      case 'framework':
        endpoint = `/compliances/framework/${id.value}/`
        break
      case 'policy':
        endpoint = `/compliances/policy/${id.value}/`
        break
      case 'subpolicy':
        endpoint = `/api/all-policies/subpolicies/${id.value}/compliances/`
        break
      default:
        throw new Error('Invalid type specified')
    }
    
    const response = await axios.get(endpoint)
    console.log('API Response:', response.data)
    
    if (response.data && response.data.success) {
      // Get the compliances
      const fetchedCompliances = response.data.compliances
      
      // Fetch audit information for each compliance
      const compliancesWithAudit = await Promise.all(
        fetchedCompliances.map(async (compliance) => {
          try {
            const auditResponse = await axios.get(`/api/compliance/${compliance.ComplianceId}/audit-info/`)
            if (auditResponse.data && auditResponse.data.success) {
              return {
                ...compliance,
                ...auditResponse.data.data
              }
            }
            return compliance
          } catch (err) {
            console.error(`Error fetching audit info for compliance ${compliance.ComplianceId}:`, err)
            return compliance
          }
        })
      )
      
      compliances.value = compliancesWithAudit
    } else {
      throw new Error(response.data.message || 'Failed to fetch compliances')
    }
  } catch (err) {
    console.error('Error fetching compliances:', err)
    error.value = 'Failed to fetch compliances. Please try again.'
    compliances.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

function getAuditStatusClass(status) {
  if (!status) return 'not-audited'
  
  const statusLower = status.toLowerCase()
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'non-compliant'
  if (statusLower.includes('partially')) return 'partially-compliant'
  if (statusLower.includes('fully')) return 'fully-compliant'
  if (statusLower.includes('not applicable')) return 'not-applicable'
  
  return 'not-audited'
}

function getAuditStatusIcon(status) {
  if (!status) return 'fas fa-question-circle'
  
  const statusLower = status.toLowerCase()
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'fas fa-times-circle'
  if (statusLower.includes('partially')) return 'fas fa-exclamation-circle'
  if (statusLower.includes('fully')) return 'fas fa-check-circle'
  if (statusLower.includes('not applicable')) return 'fas fa-ban'
  
  return 'fas fa-question-circle'
}

// Method to format the status display text for the UI
function formatAuditStatus(status) {
  if (!status) return 'Not Audited'
  
  const statusLower = status.toLowerCase()
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'Non Conformity'
  if (statusLower.includes('partially')) return 'Control Gap'
  
  // Return the original status for other cases
  return status
}

function toggleViewMode() {
  viewMode.value = viewMode.value === 'card' ? 'list' : 'card'
}

function goBack() {
  router.back()
}

function handleAuditLinkClick(auditFindingsId) {
  if (!auditFindingsId) return
  // Redirect to the audit findings detail page
  router.push(`/audit-findings/${auditFindingsId}`)
}

async function handleExport(format) {
  try {
    console.log(`Attempting export for ${type.value} ${id.value} in ${format} format`)
    
    // Update the API endpoint URL with path parameters
    const response = await axios({
      url: `/api/export/audit-compliances/${format}/${type.value}/${id.value}/`,
      method: 'GET',
      responseType: 'blob',
      timeout: 30000,
      headers: {
        'Accept': 'application/json, application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv, application/xml'
      }
    })

    // Handle successful download
    const contentType = response.headers['content-type']
    const blob = new Blob([response.data], { type: contentType })
    
    // Get filename from header or create default
    let filename = `audit_compliances_${type.value}_${id.value}.${format}`
    const disposition = response.headers['content-disposition']
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '')
    }
    
    // Trigger download
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
    
    ElMessage({
      message: 'Export completed successfully',
      type: 'success',
      duration: 3000
    })
  } catch (error) {
    console.error('Export error:', error)
    const errorMessage = error.response?.data?.message || error.message || 'Failed to export compliances'
    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 5000
    })
  }
}
</script>

<style>
.compliance-view-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  margin-left: 180px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-weight: 600;
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #4b5563;
  margin: 20px 0;
}

.content-wrapper {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.5rem;
  color: #1f2937;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #4b5563;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.view-toggle-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.view-toggle-btn i {
  color: #6b7280;
}

.compliances-list-view {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: auto;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliances-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.compliances-table th {
  background-color: #f9fafb;
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
  min-width: 140px; /* Ensure minimum width for columns */
  overflow: visible;
}

/* Specific sizing for different columns */
.compliances-table th:nth-child(1) { /* Audit Findings ID */
  min-width: 120px;
}

.compliances-table th:nth-child(2) { /* Compliance */
  min-width: 250px;
}

.compliances-table th:nth-child(3) { /* Criticality */
  min-width: 100px;
}

.compliances-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.compliances-table tr:last-child td {
  border-bottom: none;
}

.compliances-table tr:hover {
  background-color: #f9fafb;
}

.compliance-name {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audit-id {
  font-family: monospace;
  color: #6b7280;
}

.compliances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.compliance-card {
  transition: all 0.25s ease;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliance-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #d1d5db;
}

.compliance-header {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
}

.compliance-body {
  padding: 16px;
}

.compliance-body h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1f2937;
  font-size: 1.1rem;
  line-height: 1.4;
}

.compliance-footer {
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 0.85rem;
  color: #6b7280;
}

.inline-export-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.format-select {
  padding: 7px 10px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
  color: #4b5563;
  font-size: 0.9rem;
  outline: none;
  min-width: 140px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-btn:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.export-btn i {
  font-size: 0.9rem;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
  text-align: center;
}

.no-data i {
  font-size: 2rem;
  margin-bottom: 12px;
}

.criticality-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 500;
}

.criticality-high { background-color: #ffebee; color: #d32f2f; }
.criticality-medium { background-color: #fff3e0; color: #f57c00; }
.criticality-low { background-color: #e8f5e9; color: #388e3c; }

/* Add these styles to enhance the audit information presentation */
.clean-details-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 14px;
  margin: 15px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #e5e7eb;
  padding-bottom: 8px;
  font-size: 0.95rem;
}

.detail-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.detail-label, .label {
  color: #4b5563;
  font-weight: 500;
  min-width: 150px;
}

.detail-value, .value {
  color: #111827;
  font-weight: 500;
}

/* Audit status classes */
.fully-compliant {
  color: #10b981;
  font-weight: 500;
}

/* "Partially Compliant" displayed as "Control Gaps" in UI */
.partially-compliant {
  color: #f59e0b;
  font-weight: 500;
}

/* "Non Compliant" displayed as "Non Conformity" in UI */
.non-compliant {
  color: #ef4444;
  font-weight: 500;
}

.not-applicable {
  color: #6b7280;
  font-weight: 500;
}

.not-audited {
  color: #9ca3af;
  font-style: italic;
}

/* Styling for audit status icons */
.fully-compliant i {
  color: #10b981;
  margin-right: 5px;
}

/* "Partially Compliant" displayed as "Control Gaps" in UI */
.partially-compliant i {
  color: #f59e0b;
  margin-right: 5px;
}

/* "Non Compliant" displayed as "Non Conformity" in UI */
.non-compliant i {
  color: #ef4444;
  margin-right: 5px;
}

.not-applicable i {
  color: #6b7280;
  margin-right: 5px;
}

.not-audited i {
  color: #9ca3af;
  margin-right: 5px;
}

/* Add animation for loading state */
.fa-sync {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Add audit ID link styling */
.audit-id-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.audit-id-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .compliances-table {
    min-width: 1000px; /* Ensure horizontal scroll on small screens */
  }
  
  .compliances-list-view {
    overflow-x: auto;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .section-actions {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
  
  .inline-export-controls {
    order: 1;
    width: 100%;
    margin-bottom: 8px;
    justify-content: flex-end;
  }
}
</style> 