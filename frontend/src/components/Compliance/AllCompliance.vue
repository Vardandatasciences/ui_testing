<template>
  <div class="compliance-container">
    <div class="custom-header">
      <span>Control Management</span>
      <div class="custom-header-underline"></div>
    </div>


    <!-- Loading State -->
    <div v-if="loading" class="compliance-loading-spinner">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Loading...</span>
    </div>

    <!-- Breadcrumbs -->
    <div class="breadcrumbs" v-if="breadcrumbs.length > 0">
      <div v-for="(crumb, index) in breadcrumbs" :key="crumb.id" class="breadcrumb-chip">
        {{ crumb.name }}
        <span class="breadcrumb-close" @click="goToStep(index)">&times;</span>
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
              </div>
              <div class="compliance-card-actions">
                <button class="compliance-action-btn primary" @click.stop="viewAllCompliances('framework', fw.id, fw.name)">
                  <i class="fas fa-list"></i> View All Controls
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
              </div>
              <div class="compliance-card-actions">
                <button class="compliance-action-btn primary" @click.stop="viewAllCompliances('policy', policy.id, policy.name)">
                  <i class="fas fa-list"></i> View All Controls
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
                  <i class="fas fa-list"></i> View All Controls
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
            <button class="compliance-view-toggle-btn small-view-toggle" @click="toggleViewMode">
              <i :class="viewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ viewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="compliance-loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading controls...</span>
        </div>
        
        <div v-else-if="!hasCompliances" class="compliance-no-data">
          <i class="fas fa-inbox"></i>
          <p>No controls found for this subpolicy</p>
        </div>
        
        <!-- Card View -->
        <div v-else-if="viewMode === 'card'" class="compliance-grid">
          <div v-for="compliance in filteredCompliances" 
               :key="compliance.id" 
               class="compliance-card"
               @click="handleComplianceExpand(compliance)">
            <div class="compliance-header">
              <span :class="['compliance-criticality-badge', 'compliance-criticality-' + compliance.category.toLowerCase()]">
                {{ compliance.category }}
              </span>
            </div>
            
            <div class="compliance-body">
              <h3>{{ compliance.name }}</h3>
              <div class="compliance-details">
                <div class="compliance-detail-row">
                  <span class="compliance-label">Maturity Level:</span>
                  <span class="compliance-value">{{ compliance.maturityLevel }}</span>
                </div>
                <div class="compliance-detail-row">
                  <span class="compliance-label">Type:</span>
                  <span class="compliance-value">{{ compliance.mandatoryOptional }} | {{ compliance.manualAutomatic }}</span>
                </div>
                <div class="compliance-detail-row">
                  <span class="compliance-label">Version:</span>
                  <span class="compliance-value">{{ compliance.version }}</span>
                </div>
                <div class="compliance-detail-row" v-if="compliance.isRisk">
                  <span class="compliance-label">Risk Status:</span>
                  <span class="compliance-value compliance-risk">Risk Identified</span>
                </div>
              </div>
              
              <!-- Expanded Details Section -->
              <div v-if="expandedCompliance === compliance.id" class="expanded-details">
                <h4><i class="fas fa-info-circle"></i> Complete Control Details</h4>

                <div class="expanded-details-grid">
                  <!-- Basic Information -->
                  <div class="expanded-section-box">
                    <h5>Description</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.description">
                        {{ compliance.description }}
                      </template>
                      <template v-else>
                        <span class="empty-value">No description available</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Control Title</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.title">
                        {{ compliance.title }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Scope</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.scope">
                        {{ compliance.scope }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Objective</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.objective">
                        {{ compliance.objective }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <!-- Control Type & Classification -->
                  <div class="expanded-section-box">
                    <h5>Control Type</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.complianceType">
                        {{ compliance.complianceType }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Implementation Type</h5>
                    <div class="expanded-content-box">
                      {{ compliance.manualAutomatic || 'Not specified' }}
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Requirement Level</h5>
                    <div class="expanded-content-box">
                      {{ compliance.mandatoryOptional || 'Not specified' }}
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Duration</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.permanentTemporary">
                        {{ compliance.permanentTemporary }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <!-- Risk Information -->
                  <div class="expanded-section-box">
                    <h5>Risk Status</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.isRisk !== undefined">
                        <span :class="compliance.isRisk ? 'risk-identified' : 'no-risk'">
                          {{ compliance.isRisk ? 'Risk Identified' : 'No Risk' }}
                        </span>
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Possible Damage</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.possibleDamage">
                        {{ compliance.possibleDamage }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Mitigation Strategy</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.mitigation">
                        <pre class="mitigation-text">{{ formatMitigation(compliance.mitigation) }}</pre>
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Severity Rating</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.impact">
                        <span :class="'severity-' + compliance.impact.toLowerCase()">
                          {{ compliance.impact }}
                        </span>
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Probability</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.probability">
                        {{ compliance.probability }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <!-- Business Information -->
                  <div class="expanded-section-box">
                    <h5>Applicability</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.applicability">
                        {{ compliance.applicability }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Business Units Covered</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.businessUnitsCovered">
                        {{ compliance.businessUnitsCovered }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>

                  <div class="expanded-section-box">
                    <h5>Risk Scenarios</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.potentialRiskScenarios">
                        {{ compliance.potentialRiskScenarios }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <!-- Status Information -->
                  <div class="expanded-section-box">
                    <h5>Control Status</h5>
                    <div class="expanded-content-box">
                      <span :class="['status-badge', compliance.status?.toLowerCase()]">
                        {{ compliance.status || 'Not specified' }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Active Status</h5>
                    <div class="expanded-content-box">
                      <span :class="['status-badge', compliance.activeInactive?.toLowerCase()]">
                        {{ compliance.activeInactive || 'Not specified' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="compliance-footer">
                <div class="created-info">
                  <span>Created by {{ compliance.createdBy }}</span>
                  <span>{{ formatDate(compliance.createdDate) }}</span>
                </div>
                <div class="identifier">ID: {{ compliance.identifier }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- List View -->
        <div v-else class="compliance-list-view">
          <div class="compliance-dynamic-table-wrapper">
            <DynamicTable
              :data="filteredCompliances"
              :columns="tableColumns"
              uniqueKey="id"
              :showPagination="true"
              :showActions="true"
            >
              <template #actions="{ row }">
                <button class="compliance-action-btn" @click="handleViewCompliance(row)"><i class="fas fa-eye"></i></button>
                <button class="compliance-action-btn" @click="handleEditCompliance(row)"><i class="fas fa-edit"></i></button>
              </template>
            </DynamicTable>
          </div>
        </div>
      </template>
    </div>

    <!-- Versions Modal -->
    <div v-if="showVersionsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ versionModalTitle }}</h3>
          <button class="close-btn" @click="closeVersionsModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="versions.length === 0" class="no-versions">
            No versions found.
          </div>
          <div v-else class="version-grid">
            <div v-for="version in versions" :key="version.id" class="version-card">
              <div class="version-header">
                <span class="version-number">Version {{ version.version }}</span>
                <div class="version-badges">
                  <span class="status-badge" :class="statusClass(version.status)">{{ version.status }}</span>
                  <span class="status-badge" :class="statusClass(version.activeInactive)">{{ version.activeInactive }}</span>
                </div>
              </div>
              <div class="version-details">
                <p class="version-desc">{{ version.description }}</p>
                <div class="version-info-grid">
                  <div class="info-group">
                    <span class="info-label">Maturity Level:</span>
                    <span class="info-value">{{ version.maturityLevel }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Type:</span>
                    <span class="info-value">{{ version.mandatoryOptional }} | {{ version.manualAutomatic }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Criticality:</span>
                    <span class="info-value" :class="'criticality-' + version.criticality.toLowerCase()">
                      {{ version.criticality }}
                    </span>
                  </div>
                  <div class="info-group" v-if="version.isRisk">
                    <span class="info-label">Risk Status:</span>
                    <span class="info-value risk">Risk Identified</span>
                  </div>
                </div>
                <div class="version-metadata">
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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { PopupService } from '@/modules/popup'
import DynamicTable from '../DynamicTable.vue'

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
const viewMode = ref('list') // Changed to list as default view
const expandedCompliance = ref(null)
const router = useRouter()

// Define columns for DynamicTable
const tableColumns = [
  { key: 'identifier', label: 'ID', sortable: true },
  { key: 'name', label: 'Control', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'category', label: 'Criticality', sortable: true },
  { key: 'maturityLevel', label: 'Maturity Level', sortable: true },
  { key: 'mandatoryOptional', label: 'Type', sortable: true },
  { key: 'version', label: 'Version', sortable: true },
  { key: 'createdBy', label: 'Created By', sortable: true },
  { key: 'createdDate', label: 'Created Date', sortable: true },
]

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

// Replace the filtered computed properties
const filteredCompliances = computed(() => {
  if (!selectedSubpolicy.value || !selectedSubpolicy.value.compliances) return [];
  return selectedSubpolicy.value.compliances; // Return all compliances without filtering
});

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    console.log('Fetching frameworks...')
    
    // Get all frameworks with their versions
    const response = await axios.get('/api/compliance/all-policies/frameworks/')
    console.log('Frameworks response:', response.data)
    
    if (response.data && Array.isArray(response.data)) {
      frameworks.value = response.data.map(framework => ({
        id: framework.id,
        name: framework.name,
        category: framework.category || 'General',
        status: framework.status || 'Active',
        description: framework.description || '',
        versions: framework.versions || []
      }))
      console.log('Processed frameworks:', frameworks.value)
    } else {
      console.error('Invalid frameworks response format:', response.data)
      frameworks.value = []
      error.value = 'Invalid response format from server'
    }
  } catch (err) {
    error.value = 'Failed to load frameworks'
    console.error('Error fetching frameworks:', err.response?.data || err.message)
    frameworks.value = []
    PopupService.error('Failed to load frameworks. Please refresh the page and try again.', 'Loading Error')
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
    const response = await axios.get('/api/compliance/all-policies/policies/', {
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
    PopupService.error('Failed to load policies. Please try selecting a different framework.', 'Loading Error')
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
    const response = await axios.get('/api/compliance/all-policies/subpolicies/', {
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
    PopupService.error('Failed to load subpolicies. Please try selecting a different policy.', 'Loading Error')
  } finally {
    loading.value = false
  }
}

async function selectSubpolicy(subpolicy) {
  try {
    loading.value = true;
    selectedSubpolicy.value = subpolicy;
    
    const response = await axios.get(`/api/compliance/all-policies/subpolicies/${subpolicy.id}/compliances/`);
    console.log('Subpolicy compliances response:', response.data);
    
    if (response.data && response.data.success) {
      // Enhanced logging for debugging
      if (response.data.compliances.length > 0) {
        const firstCompliance = response.data.compliances[0];
        console.log('DETAILED COMPLIANCE OBJECT:', JSON.stringify(firstCompliance, null, 2));
        
        // Display all field names and values for better debugging
        console.log('COMPLIANCE FIELD VALUES:');
        Object.keys(firstCompliance).forEach(key => {
          console.log(`- ${key}: ${JSON.stringify(firstCompliance[key])}`);
        });
      }
      
      // Store the original compliance objects as they come from the API
      selectedSubpolicy.value = {
        ...subpolicy,
        compliances: response.data.compliances.map(compliance => {
          return {
            // IMPORTANT: Use the exact PascalCase field names from the API
            id: compliance.ComplianceId,
            name: compliance.ComplianceItemDescription,
            description: compliance.ComplianceItemDescription,
            status: compliance.Status,
            category: compliance.Criticality,
            maturityLevel: compliance.MaturityLevel,
            mandatoryOptional: compliance.MandatoryOptional,
            manualAutomatic: compliance.ManualAutomatic,
            createdBy: compliance.CreatedByName,
            createdDate: compliance.CreatedByDate,
            identifier: compliance.Identifier,
            version: compliance.ComplianceVersion,
            isRisk: compliance.IsRisk,
            
            // Keep the original Pascal case names for these fields
            PossibleDamage: compliance.PossibleDamage,
            mitigation: compliance.mitigation,
            SeverityRating: compliance.Impact,
            Probability: compliance.Probability,
            PermanentTemporary: compliance.PermanentTemporary,
            ActiveInactive: compliance.ActiveInactive,
            
            // Store the original object to access all fields in the expanded view
            originalData: compliance
          };
        })
      };
    } else {
      selectedSubpolicy.value.compliances = [];
    }
  } catch (err) {
    console.error('Error fetching subpolicy compliances:', err);
    error.value = 'Failed to load compliances';
    selectedSubpolicy.value.compliances = [];
  } finally {
    loading.value = false;
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

const viewAllCompliances = (type, id, name) => {
  router.push({
    name: 'ComplianceView',
    params: {
      type: type,
      id: id,
      name: encodeURIComponent(name)
    }
  });
};

async function handleExport(format) {
  try {
    if (!selectedSubpolicy.value) {
      PopupService.warning('No subpolicy selected for export', 'Export Warning');
      return;
    }
    
    const itemType = 'subpolicy';
    const itemId = selectedSubpolicy.value.SubPolicyId;
    
    // Show confirmation popup before export
    PopupService.confirm(
      `Do you want to export ${selectedSubpolicy.value.name} controls to ${format.toUpperCase()} format?`,
      'Confirm Export',
      async () => {
        console.log(`Attempting export for ${itemType} ${itemId} in ${format} format`);
        
        // Show processing popup
        PopupService.success('Export is being processed. This may take a few moments...', 'Processing Export');
        
        try {
          // Update the API endpoint URL with path parameters
          const response = await axios({
            url: `/api/compliance/export/all-compliances/${format}/${itemType}/${itemId}/`,
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
          
          PopupService.success(`Export completed successfully! File: ${filename}`, 'Export Complete');
        } catch (downloadError) {
          console.error('Export error:', downloadError);
          const errorMessage = downloadError.response?.data?.message || downloadError.message || 'Failed to export compliances';
          PopupService.error(`Export failed: ${errorMessage}`, 'Export Error');
        }
      },
      () => {
        PopupService.success('Export cancelled', 'Cancelled');
      }
    );
  } catch (error) {
    console.error('Export error:', error);
    const errorMessage = error.response?.data?.message || error.message || 'Failed to export compliances';
    PopupService.error(`Export failed: ${errorMessage}`, 'Export Error');
  }
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'card' ? 'list' : 'card';
}

const handleComplianceExpand = (compliance) => {
  if (expandedCompliance.value === compliance.id) {
    expandedCompliance.value = null;
  } else {
    expandedCompliance.value = compliance.id;
  }
};

// Add method to format mitigation display
const formatMitigation = (mitigation) => {
  if (!mitigation) {
    return 'Not specified';
  }
  
  // Check if it's JSON format
  if (typeof mitigation === 'string' && (mitigation.startsWith('[') || mitigation.startsWith('{'))) {
    try {
      const parsed = JSON.parse(mitigation);
      
      // If it's an array of steps
      if (Array.isArray(parsed)) {
        return parsed.map((step, index) => `${index + 1}. ${step}`).join('\n');
      }
      
      // If it's an object, extract meaningful values
      if (typeof parsed === 'object') {
        if (parsed.steps && Array.isArray(parsed.steps)) {
          return parsed.steps.map((step, index) => `${index + 1}. ${step}`).join('\n');
        }
        if (parsed.description) {
          return parsed.description;
        }
        // Convert object to readable format
        return Object.entries(parsed)
          .map(([key, value]) => `${key}: ${value}`)
          .join('\n');
      }
      
      return String(parsed);
    } catch (e) {
      // If JSON parsing fails, treat as plain text
      return mitigation;
    }
  }
  
  // Return as plain text
  return mitigation;
};

// Add methods for actions
function handleViewCompliance(row) {
  // Implement view logic, e.g., open a modal or navigate
  PopupService.info(`View compliance: ${row.name}`, 'View Compliance');
}
function handleEditCompliance(row) {
  // Implement edit logic, e.g., open an edit modal
  PopupService.info(`Edit compliance: ${row.name}`, 'Edit Compliance');
}
</script>

<style src="./AllCompliance.css"></style>

<style>
/* Add these styles to your existing CSS */
.version-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.version-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
  color: #4b5563;
}

.version-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.version-desc {
  color: #4b5563;
  margin: 12px 0;
  line-height: 1.5;
}

.card {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  transition: all 0.3s ease;
}

.card:hover {
  border-color: #4b5563;
  transform: translateY(-2px);
}

.card-title {
  color: #4b5563;
  font-weight: 600;
}

.card-desc {
  color: #4b5563;
}

.detail-label {
  color: #4b5563;
}

.detail-value {
  color: #4b5563;
  font-weight: 500;
}

.version-info-grid {
  background: #f9fafb;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
}

.info-group {
  margin-bottom: 8px;
}

.info-label {
  color: #4b5563;
  font-size: 0.85rem;
  font-weight: 500;
}

.info-value {
  color: #4b5563;
  font-size: 0.9rem;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.action-btn.primary {
  background-color: #4a90e2;
  color: white;
}

.action-btn.secondary {
  background-color: #f8f9fa;
  color: #4a90e2;
  border: 1px solid #4a90e2;
}

.action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.export-options {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.export-options select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.compliance-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.status-badge.approved {
  background-color: #4caf50;
  color: white;
}

.status-badge.under-review {
  background-color: #ff9800;
  color: white;
}

.status-badge.rejected {
  background-color: #f44336;
  color: white;
}

.criticality-high {
  color: #f44336;
}

.criticality-medium {
  color: #ff9800;
}

.criticality-low {
  color: #4caf50;
}

/* Modal Styles */
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
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 80px);
}

/* Export Controls */
.export-controls {
  margin: 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.export-controls .format-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.export-controls .format-selector label {
  font-weight: 500;
  color: #4b5563;
}

.export-controls .format-selector select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
  color: #374151;
  font-size: 0.95rem;
  min-width: 150px;
}

.export-btn.enhanced {
  background-color: #3b82f6;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.export-btn.enhanced:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.export-btn.enhanced:active {
  transform: translateY(0);
}

.export-btn.enhanced i {
  font-size: 1.1rem;
}

/* Compliances Grid */
.compliance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.compliance-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliance-header {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  background-color: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
}

.status-badge.approved { background-color: #4CAF50; color: white; }
.status-badge.rejected { background-color: #f44336; color: white; }
.status-badge.under-review { background-color: #ff9800; color: white; }

.criticality-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 500;
}

.criticality-high { background-color: #ffebee; color: #d32f2f; }
.criticality-medium { background-color: #fff3e0; color: #f57c00; }
.criticality-low { background-color: #e8f5e9; color: #388e3c; }

.compliance-body {
  padding: 15px;
}

.compliance-body h3 {
  margin: 0 0 15px 0;
  font-size: 1.1em;
  color: #333;
}

.compliance-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compliance-detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9em;
}

.compliance-detail-row .compliance-label {
  color: #666;
}

.compliance-detail-row .compliance-value {
  font-weight: 500;
  color: #333;
}

.compliance-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  font-size: 0.85em;
  color: #666;
}

.created-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.identifier {
  font-family: monospace;
  color: #888;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* No Data State */
.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 20px;
  color: #ddd;
}

.export-buttons {
  margin: 16px 0;
  text-align: right;
}

.export-controls .el-alert {
  margin-top: 10px;
  text-align: left;
}

/* Styles for expanded details view */
.expanded-details {
  margin-top: 16px;
  padding: 16px;
  background-color: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.expanded-details h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #1f2937;
  font-size: 1.1rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.expanded-section-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.expanded-section-box h5 {
  margin: 0;
  padding: 10px 15px;
  background-color: #f3f4f6;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.expanded-content-box {
  padding: 15px;
  min-height: 40px;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Add field category headings */
.expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.expanded-details h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0;
  margin-bottom: 16px;
  color: #1f2937;
  font-size: 1.1rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 12px;
}

.expanded-details h4:before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 20px;
  background-color: #4f46e5;
  border-radius: 2px;
}

/* Add "empty value" styling */
.empty-value {
  color: #d1d5db;
  font-style: italic;
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #f3f4f6;
  border: 1px dashed #cbd5e1;
}

.compliance-expanded-row {
  background-color: #f8fafc !important;
}

.details-row {
  background-color: #f1f5f9;
}

.details-row td {
  padding: 20px !important;
  border-bottom: 1px solid #e2e8f0;
}

/* Make expanded boxes slightly larger in list view */
.details-row .expanded-content-box {
  padding: 15px;
  min-height: 50px;
  font-size: 1rem;
}

/* Override grid layout for list view for better readability */
.details-row .expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

/* Add a subtle animation for expanding rows */
.details-row {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Mitigation text formatting */
.mitigation-text {
  font-family: inherit;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 0;
  background: none;
  border: none;
  color: inherit;
  font-size: inherit;
  line-height: 1.5;
}
</style>