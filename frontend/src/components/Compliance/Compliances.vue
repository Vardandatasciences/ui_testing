<template>
  <div class="compliance-all-compliances-container">
    <h1>Compliance Audit Status</h1>

    <!-- Error Message -->
    <div v-if="error" class="compliance-error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="compliance-loading-spinner">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Loading...</span>
    </div>

    <!-- Breadcrumbs -->
    <div class="compliance-breadcrumbs" v-if="breadcrumbs.length > 0">
      <div v-for="(crumb, index) in breadcrumbs" :key="crumb.id" class="compliance-breadcrumb-chip">
        {{ crumb.name }}
        <span class="compliance-breadcrumb-close" @click="goToStep(index)">&times;</span>
      </div>
    </div>

    <div class="compliance-content-wrapper">
      <!-- Frameworks Section -->
      <template v-if="showFrameworks">
        <div class="compliance-section-header">Frameworks</div>
        <div class="compliance-card-grid">
          <div v-for="fw in frameworks" :key="fw.id" class="compliance-card" @click="selectFramework(fw)">
            <div class="compliance-card-icon">
              <i :class="categoryIcon(fw.category)"></i>
            </div>
            <div class="compliance-card-content">
              <div class="compliance-card-title">{{ fw.name }}</div>
              <div class="compliance-card-category">{{ fw.category }}</div>
              <div class="compliance-card-status" :class="statusClass(fw.status)">{{ fw.status }}</div>
              <div class="compliance-card-desc">{{ fw.description }}</div>
              <div class="compliance-version-info">
                <span>Versions: {{ fw.versions.length }}</span>
                <button class="compliance-version-btn" @click.stop="showVersions('framework', fw)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
              <div class="compliance-card-actions">
                <button class="compliance-action-btn primary" @click.stop="viewAllCompliances('framework', fw.id, fw.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Policies Section -->
      <template v-else-if="showPolicies">
        <div class="compliance-section-header">Policies in {{ selectedFramework.name }}</div>
        <div class="compliance-card-grid">
          <div v-for="policy in policies" :key="policy.id" class="compliance-card" @click="selectPolicy(policy)">
            <div class="compliance-card-icon">
              <i :class="categoryIcon(policy.category)"></i>
            </div>
            <div class="compliance-card-content">
              <div class="compliance-card-title">{{ policy.name }}</div>
              <div class="compliance-card-category">{{ policy.category }}</div>
              <div class="compliance-card-status" :class="statusClass(policy.status)">{{ policy.status }}</div>
              <div class="compliance-card-desc">{{ policy.description }}</div>
              <div class="compliance-version-info">
                <span>Versions: {{ policy.versions.length }}</span>
                <button class="compliance-version-btn" @click.stop="showVersions('policy', policy)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
              <div class="compliance-card-actions">
                <button class="compliance-action-btn primary" @click.stop="viewAllCompliances('policy', policy.id, policy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Subpolicies Section -->
      <template v-else-if="showSubpolicies">
        <div class="compliance-section-header">Subpolicies in {{ selectedPolicy.name }}</div>
        <div class="compliance-card-grid">
          <div v-for="subpolicy in subpolicies" :key="subpolicy.id" class="compliance-card" @click="selectSubpolicy(subpolicy)">
            <div class="compliance-card-icon">
              <i :class="categoryIcon(subpolicy.category)"></i>
            </div>
            <div class="compliance-card-content">
              <div class="compliance-card-title">{{ subpolicy.name }}</div>
              <div class="compliance-card-category">{{ subpolicy.category }}</div>
              <div class="compliance-card-status" :class="statusClass(subpolicy.status)">{{ subpolicy.status }}</div>
              <div class="compliance-card-desc">{{ subpolicy.description }}</div>
              <div class="compliance-metadata">
                <span>Control: {{ subpolicy.control }}</span>
                <span>{{ subpolicy.permanent_temporary }}</span>
              </div>
              <div class="compliance-card-actions">
                <button class="compliance-action-btn primary" @click.stop="viewAllCompliances('subpolicy', subpolicy.id, subpolicy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Compliances Section -->
      <template v-else-if="selectedSubpolicy">
        <div class="compliance-section-header">
          <span>Compliances in {{ selectedSubpolicy.name }}</span>
          <div class="compliance-section-actions">
            <!-- Export Controls -->
            <div class="compliance-inline-export-controls">
              <select v-model="selectedFormat" class="compliance-format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
              </select>
              <button class="compliance-export-btn" @click="handleExport(selectedFormat)">
                <i class="fas fa-download"></i> Export
              </button>
            </div>
            <button class="compliance-view-toggle-btn" @click="toggleViewMode">
              <i :class="viewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ viewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
            <button class="compliance-action-btn" @click="goToStep(2)">
              <i class="fas fa-arrow-left"></i> Back to Subpolicies
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="compliance-loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading compliances...</span>
        </div>
        
        <div v-else-if="!hasCompliances" class="compliance-no-data">
          <i class="fas fa-inbox"></i>
          <p>No compliances found for this subpolicy</p>
        </div>
        
        <div v-else-if="filteredCompliances.length === 0" class="compliance-no-data">
          <i class="fas fa-filter"></i>
          <p>No approved compliances found for this subpolicy</p>
        </div>
        
        <!-- Card View -->
        <div v-else-if="viewMode === 'card'" class="compliance-card-grid">
          <div v-for="compliance in filteredCompliances" 
               :key="compliance.id" 
               class="compliance-card">
            <div class="compliance-header">
              <span :class="['compliance-criticality-badge', 'compliance-criticality-' + compliance.category.toLowerCase()]">
                {{ compliance.category }}
              </span>
            </div>
            
            <div class="compliance-body">
              <h3>{{ compliance.name }}</h3>
              
              <div class="compliance-clean-details-grid">
                <div class="compliance-fetch-audit-actions" v-if="!complianceAudits[compliance.id]">
                  <button class="compliance-fetch-audit-btn" @click="fetchAuditInfo(compliance.id)">
                    <i class="fas fa-sync"></i> Load Compliance Information
                  </button>
                </div>
                
                <div class="compliance-detail-row">
                  <span class="compliance-detail-label">Compliance Performed By:</span>
                  <span class="compliance-detail-value">{{ complianceAudits[compliance.id]?.audit_performer_name || 'N/A' }}</span>
                </div>
                
                <div class="compliance-detail-row">
                  <span class="compliance-detail-label">Compliance Approved By:</span>
                  <span class="compliance-detail-value">{{ complianceAudits[compliance.id]?.audit_approver_name || 'N/A' }}</span>
                </div>
                
                <div class="compliance-detail-row">
                  <span class="compliance-detail-label">Completion Date:</span>
                  <span class="compliance-detail-value">{{ complianceAudits[compliance.id]?.audit_date || 'N/A' }}</span>
                </div>
                
                <div class="compliance-detail-row">
                  <span class="compliance-detail-label">Completion Status:</span>
                  <span class="compliance-detail-value" :class="getAuditStatusClass(complianceAudits[compliance.id]?.audit_findings_status)">
                    <i :class="getAuditStatusIcon(complianceAudits[compliance.id]?.audit_findings_status)"></i>
                    {{ formatAuditStatus(complianceAudits[compliance.id]?.audit_findings_status) }}
                  </span>
                </div>
              </div>
              
              <div class="compliance-footer">
                <div class="compliance-identifier">ID: {{ compliance.identifier }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- List View -->
        <div v-else class="compliance-list-view">
          <table class="compliance-table">
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
              <tr v-for="compliance in filteredCompliances" :key="compliance.id">
                <td class="compliance-audit-id">
                  <a 
                    v-if="complianceAudits[compliance.id]?.audit_findings_id" 
                    href="#" 
                    class="compliance-audit-id-link"
                    @click.prevent="handleAuditLinkClick(complianceAudits[compliance.id]?.audit_findings_id)">
                    {{ complianceAudits[compliance.id]?.audit_findings_id }}
                  </a>
                  <span v-else>N/A</span>
                </td>
                <td class="compliance-name">{{ compliance.name }}</td>
                <td>
                  <span :class="['compliance-criticality-badge', 'compliance-criticality-' + compliance.category.toLowerCase()]">
                    {{ compliance.category }}
                  </span>
                </td>
                <td>
                  <span :class="getAuditStatusClass(complianceAudits[compliance.id]?.audit_findings_status)">
                    <i :class="getAuditStatusIcon(complianceAudits[compliance.id]?.audit_findings_status)"></i>
                    {{ formatAuditStatus(complianceAudits[compliance.id]?.audit_findings_status) }}
                  </span>
                </td>
                <td>
                  <span v-if="!complianceAudits[compliance.id]">
                    <button class="compliance-mini-fetch-btn" @click="fetchAuditInfo(compliance.id)">
                      <i class="fas fa-sync"></i> Load
                    </button>
                  </span>
                  <span v-else>{{ complianceAudits[compliance.id]?.audit_performer_name || 'N/A' }}</span>
                </td>
                <td>{{ complianceAudits[compliance.id]?.audit_approver_name || 'N/A' }}</td>
                <td>{{ complianceAudits[compliance.id]?.audit_date || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <!-- Versions Modal -->
    <div v-if="showVersionsModal" class="compliance-modal">
      <div class="compliance-modal-content">
        <div class="compliance-modal-header">
          <h3>{{ versionModalTitle }}</h3>
          <button class="compliance-close-btn" @click="closeVersionsModal">&times;</button>
        </div>
        <div class="compliance-modal-body">
          <div v-if="versions.length === 0" class="compliance-no-versions">
            No versions found.
          </div>
          <div v-else class="compliance-version-grid">
            <div v-for="version in versions" :key="version.id" class="compliance-version-card">
              <div class="compliance-version-header">
                <span class="compliance-version-number">Version {{ version.version }}</span>
                <div class="compliance-version-badges">
                  <span class="compliance-status-badge" :class="statusClass(version.status)">{{ version.status }}</span>
                  <span class="compliance-status-badge" :class="statusClass(version.activeInactive)">{{ version.activeInactive }}</span>
                </div>
              </div>
              <div class="compliance-version-details">
                <p class="compliance-version-desc">{{ version.description }}</p>
                <div class="compliance-version-info-grid">
                  <div class="compliance-info-group">
                    <span class="compliance-info-label">Maturity Level:</span>
                    <span class="compliance-info-value">{{ version.maturityLevel }}</span>
                  </div>
                  <div class="compliance-info-group">
                    <span class="compliance-info-label">Type:</span>
                    <span class="compliance-info-value">{{ version.mandatoryOptional }} | {{ version.manualAutomatic }}</span>
                  </div>
                  <div class="compliance-info-group">
                    <span class="compliance-info-label">Criticality:</span>
                    <span class="compliance-info-value" :class="'compliance-criticality-' + version.criticality.toLowerCase()">
                      {{ version.criticality }}
                    </span>
                  </div>
                  <div class="compliance-info-group" v-if="version.isRisk">
                    <span class="compliance-info-label">Risk Status:</span>
                    <span class="compliance-info-value risk">Risk Identified</span>
                  </div>
                </div>
                <div class="compliance-version-metadata">
                  <span>
                    <i class="fas fa-user"></i>
                    {{ version.createdBy }}
                  </span>
                  <span>
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(version.createdDate) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

export default {
  name: 'ComplianceManagement',
  setup() {
// State
const frameworks = ref([])
const selectedFramework = ref(null)
const selectedPolicy = ref(null)
const selectedSubpolicy = ref(null)
const showVersionsModal = ref(false)
const versions = ref([])
const policies = ref([])
const subpolicies = ref([])
const loading = ref(false)
const error = ref(null)
const versionModalTitle = ref('')
const selectedFormat = ref('xlsx')
const isExporting = ref(false)
const exportError = ref(null)
const complianceAudits = ref({})
const viewMode = ref('list') // Changed default to 'list' view
const router = useRouter() // Add router for navigation

// Computed
const breadcrumbs = computed(() => {
  const arr = []
  if (selectedFramework.value) arr.push({ id: 0, name: selectedFramework.value.name })
  if (selectedPolicy.value) arr.push({ id: 1, name: selectedPolicy.value.name })
  if (selectedSubpolicy.value) arr.push({ id: 2, name: selectedSubpolicy.value.name })
  return arr
})

const showFrameworks = computed(() => !selectedFramework.value)
const showPolicies = computed(() => selectedFramework.value && !selectedPolicy.value)
const showSubpolicies = computed(() => selectedPolicy.value && !selectedSubpolicy.value)

const hasCompliances = computed(() => {
  return selectedSubpolicy.value && 
         selectedSubpolicy.value.compliances && 
         selectedSubpolicy.value.compliances.length > 0;
})

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    // Get all frameworks with their versions
    const response = await axios.get('/api/all-policies/frameworks/')
    if (response.data && Array.isArray(response.data)) {
      frameworks.value = response.data.map(framework => ({
        ...framework,
        versions: framework.versions || [] // Versions should be included in the framework response
      }))
    } else {
      frameworks.value = []
    }
  } catch (err) {
    error.value = 'Failed to load frameworks'
    console.error('Error fetching frameworks:', err)
    frameworks.value = []
  } finally {
    loading.value = false
  }
})

// Methods
async function selectFramework(fw) {
  try {
    loading.value = true
    selectedFramework.value = fw
    selectedPolicy.value = null
    selectedSubpolicy.value = null
    
    // Get active policies for the selected framework using the correct endpoint
    const response = await axios.get('/api/all-policies/policies/', {
      params: { 
        framework_id: fw.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      policies.value = response.data.map(policy => ({
        ...policy,
        versions: policy.versions || [] // Versions count should be included in the response
      }))
    } else {
      policies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load policies'
    console.error('Error fetching policies:', err)
    policies.value = []
  } finally {
    loading.value = false
  }
}

async function selectPolicy(policy) {
  try {
    loading.value = true
    selectedPolicy.value = policy
    selectedSubpolicy.value = null
    
    // Get active subpolicies for the selected policy using the correct endpoint
    const response = await axios.get('/api/all-policies/subpolicies/', {
      params: { 
        policy_id: policy.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      subpolicies.value = response.data
    } else {
      subpolicies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load subpolicies'
    console.error('Error fetching subpolicies:', err)
    subpolicies.value = []
  } finally {
    loading.value = false
  }
}

async function selectSubpolicy(subpolicy) {
  try {
    loading.value = true;
    selectedSubpolicy.value = subpolicy;
        complianceAudits.value = {}; // Reset audit data
        
        console.log(`Selecting subpolicy: ${subpolicy.id} - ${subpolicy.name}`);
    
    const response = await axios.get(`/api/all-policies/subpolicies/${subpolicy.id}/compliances/`);
    console.log('Subpolicy compliances response:', response.data);
    
    if (response.data && response.data.success) {
          const compliances = response.data.compliances.map(compliance => ({
          id: compliance.ComplianceId,
          name: compliance.ComplianceItemDescription,
          status: compliance.Status,
          description: compliance.ComplianceItemDescription,
          category: compliance.Criticality,
          maturityLevel: compliance.MaturityLevel,
          mandatoryOptional: compliance.MandatoryOptional,
          manualAutomatic: compliance.ManualAutomatic,
          createdBy: compliance.CreatedByName,
          createdDate: compliance.CreatedByDate,
          isRisk: compliance.IsRisk,
          activeInactive: compliance.ActiveInactive,
          identifier: compliance.Identifier,
          version: compliance.ComplianceVersion
          }));
          
          selectedSubpolicy.value = {
            ...subpolicy,
            compliances: compliances
          };
          
          console.log(`Found ${compliances.length} compliances for subpolicy ${subpolicy.id}`);
          
          // Fetch audit info for each compliance
          if (compliances.length > 0) {
            for (const compliance of compliances) {
              try {
                await fetchAuditInfo(compliance.id);
                // Add a small delay to prevent overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 100));
              } catch (auditErr) {
                console.error(`Error fetching audit info for compliance ${compliance.id}:`, auditErr);
                // Continue with next compliance
              }
            }
            console.log('All audit information fetched:', complianceAudits.value);
          }
    } else {
          selectedSubpolicy.value = {
            ...subpolicy,
            compliances: []
          };
          console.log('No compliances found or API returned error');
    }
  } catch (err) {
    console.error('Error fetching subpolicy compliances:', err);
    error.value = 'Failed to load compliances';
        selectedSubpolicy.value = {
          ...subpolicy,
          compliances: []
        };
  } finally {
    loading.value = false;
  }
}

async function showVersions(type, item) {
  try {
    loading.value = true
    let endpoint = ''
    
    switch (type) {
      case 'policy':
        versionModalTitle.value = `Versions of ${item.name}`
        endpoint = `/api/all-policies/policies/${item.id}/versions/`
        break
      case 'compliance':
        versionModalTitle.value = `Versions of Compliance ${item.name}`
        endpoint = `/api/all-policies/compliances/${item.id}/versions/`
        break
    }
    
    const response = await axios.get(endpoint)
    if (response.data && Array.isArray(response.data)) {
      versions.value = response.data.map(version => ({
        id: version.ComplianceId,
        version: version.ComplianceVersion,
        name: version.ComplianceItemDescription,
        status: version.Status,
        description: version.ComplianceItemDescription,
        criticality: version.Criticality,
        maturityLevel: version.MaturityLevel,
        mandatoryOptional: version.MandatoryOptional,
        manualAutomatic: version.ManualAutomatic,
        createdBy: version.CreatedByName,
        createdDate: version.CreatedByDate,
        isRisk: version.IsRisk,
        activeInactive: version.ActiveInactive,
        identifier: version.Identifier
      }))
    } else {
      versions.value = []
    }
    showVersionsModal.value = true
  } catch (err) {
    error.value = `Failed to load ${type} versions`
    console.error(`Error fetching ${type} versions:`, err)
    versions.value = []
  } finally {
    loading.value = false
  }
}

function closeVersionsModal() {
  showVersionsModal.value = false
  versions.value = []
  versionModalTitle.value = ''
}

function goToStep(idx) {
  if (idx <= 0) {
    selectedFramework.value = null
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 1) {
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 2) {
    selectedSubpolicy.value = null
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

function categoryIcon(category) {
  switch ((category || '').toLowerCase()) {
    case 'governance': return 'fas fa-shield-alt'
    case 'access control': return 'fas fa-user-shield'
    case 'asset management': return 'fas fa-boxes'
    case 'cryptography': return 'fas fa-key'
    case 'data management': return 'fas fa-database'
    case 'device management': return 'fas fa-mobile-alt'
    case 'risk management': return 'fas fa-exclamation-triangle'
    case 'supplier management': return 'fas fa-handshake'
    case 'business continuity': return 'fas fa-business-time'
    case 'privacy': return 'fas fa-user-secret'
    case 'system protection': return 'fas fa-shield-virus'
    case 'incident response': return 'fas fa-ambulance'
    default: return 'fas fa-file-alt'
  }
}

function statusClass(status) {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s.includes('active')) return 'active'
  if (s.includes('inactive')) return 'inactive'
  if (s.includes('pending')) return 'pending'
  return ''
}

const viewAllCompliances = async (type, id, name) => {
  try {
    // Navigate to the ComplianceAuditView component instead of showing a modal
    router.push({
      name: 'ComplianceAuditView',
      params: {
        type: type,
        id: id,
        name: encodeURIComponent(name)
      }
    });
  } catch (error) {
    console.error('Error navigating to audit view:', error);
    error.value = 'Failed to navigate to audit view. Please try again.';
  }
}

async function handleExport(format) {
  try {
    isExporting.value = true;
    exportError.value = null;
    
    let itemType = '';
    let itemId = null;
    
    // Determine the item type and ID based on current selection
    if (selectedSubpolicy.value) {
      itemType = 'subpolicy';
      itemId = selectedSubpolicy.value.id;
    } else if (selectedPolicy.value) {
      itemType = 'policy';
      itemId = selectedPolicy.value.id;
    } else if (selectedFramework.value) {
      itemType = 'framework';
      itemId = selectedFramework.value.id;
    } else {
      throw new Error('No item selected for export');
    }
    
    console.log(`Attempting export for ${itemType} ${itemId} in ${format} format`);
    
    // Update the API endpoint URL with path parameters
    const response = await axios({
      url: `/api/export/all-compliances/${format}/${itemType}/${itemId}/`,
      method: 'GET',
      responseType: 'blob',
      timeout: 30000,
      headers: {
        'Accept': 'application/json, application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv, application/xml'
      }
    });

    // Handle successful download
    const contentType = response.headers['content-type'];
    const blob = new Blob([response.data], { type: contentType });
    
    // Get filename from header or create default
    let filename = `compliances_${itemType}_${itemId}.${format}`;
    const disposition = response.headers['content-disposition'];
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '');
    }
    
    // Trigger download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    
    ElMessage({
      message: 'Export completed successfully',
      type: 'success',
      duration: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    const errorMessage = error.response?.data?.message || error.message || 'Failed to export compliances';
    exportError.value = errorMessage;
    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 5000
    });
  } finally {
    isExporting.value = false;
  }
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'card' ? 'list' : 'card'
}

const filteredCompliances = computed(() => {
  if (!selectedSubpolicy.value || !selectedSubpolicy.value.compliances) return [];
  return selectedSubpolicy.value.compliances.filter(compliance => compliance.status === 'Approved');
});

async function fetchAuditInfo(complianceId) {
  try {
    console.log(`Fetching audit info for compliance ID: ${complianceId}`);
    
    // Check if we already have this data to avoid unnecessary requests
    if (complianceAudits.value[complianceId] && 
        complianceAudits.value[complianceId].audit_findings_status !== 'Not Audited') {
      console.log(`Using cached audit data for compliance ID: ${complianceId}`);
      return;
    }
    
    // Set a temporary loading state in the audit data
    complianceAudits.value = {
      ...complianceAudits.value,
      [complianceId]: { 
        audit_findings_status: 'Loading...',
        isLoading: true
      }
    };
    
    const response = await axios.get(`/api/compliance/${complianceId}/audit-info/`);
    console.log(`Audit info response for compliance ID ${complianceId}:`, response.data);
    
    if (response.data && response.data.success) {
      complianceAudits.value = {
        ...complianceAudits.value,
        [complianceId]: {
          ...response.data.data,
          isLoading: false
        }
      };
      console.log(`Updated audit data for compliance ID ${complianceId}:`, complianceAudits.value[complianceId]);
    } else {
      throw new Error(response.data.message || 'Failed to fetch audit data');
    }
  } catch (err) {
    console.error(`Error fetching audit info for compliance ${complianceId}:`, err);
    // Set an empty object to prevent repeated requests
    complianceAudits.value = {
      ...complianceAudits.value,
      [complianceId]: { 
        audit_findings_status: 'Not Audited',
        isLoading: false,
        error: err.message
      }
    };
  }
}

function getAuditStatusClass(status) {
  if (!status) return 'not-audited';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'non-compliant';
  if (statusLower.includes('partially')) return 'partially-compliant';
  if (statusLower.includes('fully')) return 'fully-compliant';
  if (statusLower.includes('not applicable')) return 'not-applicable';
  
  return 'not-audited';
}

function getAuditStatusIcon(status) {
  if (!status) return 'fas fa-question-circle';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'fas fa-times-circle';
  if (statusLower.includes('partially')) return 'fas fa-exclamation-circle';
  if (statusLower.includes('fully')) return 'fas fa-check-circle';
  if (statusLower.includes('not applicable')) return 'fas fa-ban';
  
  return 'fas fa-question-circle';
}

// Method to format the status display text for the UI
function formatAuditStatus(status) {
  if (!status) return 'Not Audited';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'Non Conformity';
  if (statusLower.includes('partially')) return 'Control Gap';
  
  // Return the original status for other cases
  return status;
}

const handleAuditLinkClick = (auditFindingsId) => {
  if (!auditFindingsId) return;
  console.log(`Clicked on audit findings ID: ${auditFindingsId}`);
  // This function will be used for redirecting in the future
  // You can implement the redirection logic here when needed
}

return {
  frameworks,
  selectedFramework,
  selectedPolicy,
  selectedSubpolicy,
  showVersionsModal,
  versions,
  policies,
  subpolicies,
  loading,
  error,
  versionModalTitle,
  selectedFormat,
  isExporting,
  exportError,
  complianceAudits,
  viewMode,
  router,
  breadcrumbs,
  showFrameworks,
  showPolicies,
  showSubpolicies,
  hasCompliances,
  selectFramework,
  selectPolicy,
  selectSubpolicy,
  showVersions,
  closeVersionsModal,
  goToStep,
  formatDate,
  categoryIcon,
  statusClass,
  viewAllCompliances,
  handleExport,
  fetchAuditInfo,
  getAuditStatusClass,
  getAuditStatusIcon,
  formatAuditStatus,
  handleAuditLinkClick,
  toggleViewMode,
  filteredCompliances
}
}
}
</script>

<style src="./Compliances.css"></style>

<style>
/* Styling for audit status icons */
.compliance-fully-compliant i {
  color: #10b981;
  margin-right: 5px;
}

/* "Partially Compliant" displayed as "Control Gaps" in UI */
.compliance-partially-compliant i {
  color: #f59e0b;
  margin-right: 5px;
}

/* "Non Compliant" displayed as "Non Conformity" in UI */
.compliance-non-compliant i {
  color: #ef4444;
  margin-right: 5px;
}

.compliance-not-applicable i {
  color: #6b7280;
  margin-right: 5px;
}

.compliance-not-audited i {
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

/* Add these styles for the list view of compliances */
.compliance-section-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.compliance-view-toggle-btn {
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

.compliance-view-toggle-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.compliance-view-toggle-btn i {
  color: #6b7280;
}

.compliance-list-view {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: auto;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliance-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.compliance-table th {
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
.compliance-table th:nth-child(1) { /* Audit Findings ID */
  min-width: 120px;
}

.compliance-table th:nth-child(2) { /* Compliance */
  min-width: 250px;
}

.compliance-table th:nth-child(3) { /* Criticality */
  min-width: 100px;
}

.compliance-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.compliance-table tr:last-child td {
  border-bottom: none;
}

.compliance-table tr:hover {
  background-color: #f9fafb;
}

.compliance-name {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.compliance-audit-id {
  font-family: monospace;
  color: #6b7280;
}

.compliance-mini-fetch-btn {
  padding: 4px 8px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.compliance-mini-fetch-btn:hover {
  background-color: #e5e7eb;
}

.compliance-mini-fetch-btn i {
  margin-right: 4px;
  font-size: 0.8rem;
}

/* Modal Controls */
.compliance-modal-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.compliance-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .compliance-table {
    min-width: 1000px; /* Ensure horizontal scroll on small screens */
  }
  
  .compliance-list-view {
    overflow-x: auto;
  }
}

/* Add these styles to enhance the audit information presentation */
.compliance-clean-details-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 14px;
  margin: 15px 0;
}

.compliance-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #e5e7eb;
  padding-bottom: 8px;
  font-size: 0.95rem;
}

.compliance-detail-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.compliance-detail-label, .compliance-label {
  color: #4b5563;
  font-weight: 500;
  min-width: 150px;
}

.compliance-detail-value, .compliance-value {
  color: #111827;
  font-weight: 500;
}

/* Audit status classes */
.compliance-fully-compliant {
  color: #10b981;
  font-weight: 500;
}

/* "Partially Compliant" displayed as "Control Gaps" in UI */
.compliance-partially-compliant {
  color: #f59e0b;
  font-weight: 500;
}

/* "Non Compliant" displayed as "Non Conformity" in UI */
.compliance-non-compliant {
  color: #ef4444;
  font-weight: 500;
}

.compliance-not-applicable {
  color: #6b7280;
  font-weight: 500;
}

.compliance-not-audited {
  color: #9ca3af;
  font-style: italic;
}

.compliance-fetch-audit-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.compliance-fetch-audit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #4b5563;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.compliance-fetch-audit-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.compliance-fetch-audit-btn i {
  color: #6b7280;
}

/* Enhanced compliance cards */
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

/* Add audit ID link styling */
.compliance-audit-id-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.compliance-audit-id-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}
</style> 