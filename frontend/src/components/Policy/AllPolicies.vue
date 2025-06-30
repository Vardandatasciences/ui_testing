<template>
  <div class="policy-tabs-container">
    <!-- Loading Indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="fas fa-circle-notch fa-spin"></i>
        <span>Loading...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- Modern Pill Toggle Tabs: Only show on first page (framework selection) -->
    <div v-if="!selectedFramework" class="pill-tabs-bar">
      <button class="pill-tab" :class="{active: activeTab==='framework'}" @click="activeTab='framework'">
        <span v-if="activeTab==='framework'" class="pill-dot"></span>
        Compliance Frameworks
      </button>
      <button class="pill-tab" :class="{active: activeTab==='policies'}" @click="activeTab='policies'">
        <span v-if="activeTab==='policies'" class="pill-dot"></span>
        Policies
      </button>
      <button class="pill-tab" :class="{active: activeTab==='subpolicies'}" @click="activeTab='subpolicies'">
        <span v-if="activeTab==='subpolicies'" class="pill-dot"></span>
        Subpolicies
      </button>
    </div>

    <!-- Breadcrumb chips for navigation context -->
    <div class="breadcrumbs" v-if="breadcrumbs.length">
      <TransitionGroup name="breadcrumb">
        <span v-for="(crumb, idx) in breadcrumbs" 
              :key="crumb.id" 
              class="breadcrumb-chip">
          {{ crumb.name }}
          <span class="breadcrumb-close" @click.stop="resetNavigation(idx)">×</span>
        </span>
      </TransitionGroup>
    </div>

    <!-- Framework selection step (tab toggle) -->
    <template v-if="!selectedFramework">
      <template v-if="activeTab==='framework'">
        <div class="framework-page-desc">
          <!-- <h2>Select the framework you are interested, and we will display Subpolicies and Policies.</h2> -->
        </div>
        <div style="max-width:340px;margin:0 auto 18px auto;">
          <label style="font-size:1.1rem;font-weight:500;display:block;margin-bottom:6px;">Framework</label>
          <select v-model="frameworkDropdown" class="card-dropdown" @change="handleFrameworkSelection">
            <option value="">Select Framework</option>
            <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
          </select>
        </div>
        <div class="section-header">Frameworks</div>
        <div class="card-grid">
          <div v-for="fw in filteredFrameworks" :key="fw.id" class="card" @click="selectFramework(fw)">
            <div class="card-header">
              <div class="card-icon">
                <i :class="categoryIcon(fw.category)"></i>
              </div>
              <div class="card-status" :class="statusClass(fw.status)">{{ fw.status }}</div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ fw.name }}</div>
              <div class="card-category">Category: {{ fw.category }}</div>
              <div class="card-desc">{{ fw.description }}</div>
            </div>
            <div class="card-actions card-actions-bottom">
              <button class="pdf-icon-btn" @click.stop="showDetails(fw)">
                <i class="fas fa-file-pdf"></i>
              </button>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="activeTab==='policies'">
        <div class="framework-select-container">
          <div class="framework-select-wrapper">
            <label>Select Framework</label>
            <select v-model="selectedPolicyFramework" class="card-dropdown">
              <option value="">All Frameworks</option>
              <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
            </select>
          </div>
          <div class="view-toggle">
            <button class="view-toggle-btn" :class="{ active: policyViewMode === 'table' }" @click="policyViewMode = policyViewMode === 'card' ? 'table' : 'card'">
              <i class="fas fa-table"></i>
            </button>
          </div>
        </div>

        <!-- Show initial data immediately while loading full details -->
        <div v-if="policiesLoading && !policies.length" class="loading-message">
          <i class="fas fa-circle-notch fa-spin"></i> Loading policies...
        </div>

        <div v-if="policyViewMode === 'card'" class="card-grid">
          <div v-for="policy in filteredPolicies" :key="policy.id" class="card">
            <div class="card-header">
              <div class="card-icon">
                <i :class="categoryIcon(policy.category)"></i>
              </div>
              <div class="card-status" :class="statusClass(policy.status)">{{ policy.status }}</div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ policy.name }}</div>
              <div class="card-category">Category: {{ policy.category }}</div>
              <div class="card-count">
                <span v-if="policy.version_count !== undefined">
                  Versions: {{ policy.version_count }}
                </span>
                <span v-else-if="policy.versions">
                  Versions: {{ policy.versions.length }}
                </span>
                <span v-else-if="policiesLoading" class="loading-versions">
                  <i class="fas fa-circle-notch fa-spin fa-sm"></i>
                </span>
                <span v-else>
                  Versions: 0
                </span>
              </div>
              <div class="card-desc">{{ policy.description }}</div>
            </div>
            <div class="card-actions card-actions-bottom">
              <button class="pdf-icon-btn" @click.stop="showDetails(policy)">
                <i class="fas fa-file-pdf"></i>
              </button>
            </div>
          </div>
        </div>

        <table v-else class="table-view">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Status</th>
              <th>Versions</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="policy in filteredPolicies" :key="policy.id">
              <td>{{ policy.name }}</td>
              <td>{{ policy.category }}</td>
              <td>
                <span class="table-status-badge" :class="statusClass(policy.status)">
                  {{ policy.status }}
                </span>
              </td>
              <td>
                <div class="table-version-tags">
                  <span v-for="version in policy.versions" :key="version.id" class="table-version-tag">
                    {{ version.name }}
                  </span>
                </div>
              </td>
              <td>{{ policy.description }}</td>
            </tr>
          </tbody>
        </table>
      </template>
      <template v-else-if="activeTab==='subpolicies'">
        <div class="framework-select-container">
          <div class="framework-select-wrapper">
            <label>Select Framework</label>
            <select v-model="selectedSubpolicyFramework" class="card-dropdown">
              <option value="">All Frameworks</option>
              <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
            </select>
          </div>
          <div class="view-toggle">
            <button class="view-toggle-btn" :class="{ active: subpolicyViewMode === 'table' }" @click="subpolicyViewMode = subpolicyViewMode === 'card' ? 'table' : 'card'">
              <i class="fas fa-table"></i>
            </button>
          </div>
        </div>

        <!-- Show loading indicator -->
        <div v-if="subpoliciesLoading && !subpolicies.length" class="loading-message">
          <i class="fas fa-circle-notch fa-spin"></i> Loading subpolicies...
        </div>

        <div v-if="subpolicyViewMode === 'card'" class="card-grid">
          <div v-for="subpolicy in filteredSubpolicies" :key="subpolicy.id" class="card">
            <div class="card-header">
              <div class="card-icon">
                <i :class="categoryIcon(subpolicy.category)"></i>
              </div>
              <div class="card-status" :class="statusClass(subpolicy.status)">{{ subpolicy.status }}</div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ subpolicy.name }}</div>
              <div class="card-category">Category: {{ subpolicy.category }}</div>
              <div class="card-desc">{{ subpolicy.description }}</div>
            </div>
            <div class="card-actions card-actions-bottom">
              <button class="pdf-icon-btn" @click.stop="showDetails(subpolicy)">
                <i class="fas fa-file-pdf"></i>
              </button>
            </div>
          </div>
        </div>

        <table v-else class="table-view">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Status</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subpolicy in filteredSubpolicies" :key="subpolicy.id">
              <td>{{ subpolicy.name }}</td>
              <td>{{ subpolicy.category }}</td>
              <td>
                <span class="table-status-badge" :class="statusClass(subpolicy.status)">
                  {{ subpolicy.status }}
                </span>
              </td>
              <td>{{ subpolicy.description }}</td>
            </tr>
          </tbody>
        </table>
      </template>
    </template>

    <!-- Framework versions step (after framework selection, before policies) -->
    <template v-else-if="selectedFramework && !selectedFrameworkVersion">
      <div class="section-header">Versions</div>
      <div class="card-grid">
        <div v-for="version in selectedFramework.versions" :key="version.id" class="card" @click="selectFrameworkVersion(version)">
          <div class="card-header">
            <div class="card-icon">
              <i :class="categoryIcon(version.category)"></i>
            </div>
            <div class="card-status" :class="statusClass(version.status)">{{ version.status }}</div>
          </div>
          <div class="card-content">
            <div class="card-title">{{ version.name }}</div>
            <div class="card-category">Category: {{ version.category }}</div>
            <div class="card-count">
              <span class="policies-count">
                <i class="fas fa-file-alt"></i> Policies: {{ version.policy_count || 0 }}
              </span>
            </div>
            <div v-if="version.previous_version_id" class="card-version-info">
              <span>Previous version: {{ version.previous_version_name }}</span>
            </div>
            <div class="card-desc">{{ version.description }}</div>
          </div>
          <div class="card-actions card-actions-bottom">
            <button class="pdf-icon-btn" @click.stop="showDetails(version)">
              <i class="fas fa-file-pdf"></i>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Policies in framework version step -->
    <template v-else-if="selectedFramework && selectedFrameworkVersion && !selectedPolicy">
      <div class="section-header">Policies</div>
      <div class="card-grid">
        <div v-for="policy in selectedFrameworkVersion.policies" :key="policy.id" class="card" @click="selectPolicy(policy)">
          <div class="card-header">
            <div class="card-icon">
              <i :class="categoryIcon(policy.category)"></i>
            </div>
            <div class="card-status" :class="statusClass(policy.status)">{{ policy.status }}</div>
          </div>
          <div class="card-content">
            <div class="card-title">{{ policy.name }}</div>
            <div class="card-category">Category: {{ policy.category }}</div>
            <div class="card-count">Versions: {{ policy.version_count || (policy.versions ? policy.versions.length : 0) }}</div>
            <div class="card-desc">{{ policy.description }}</div>
          </div>
          <div class="card-actions card-actions-bottom">
            <button class="pdf-icon-btn" @click.stop="showDetails(policy)">
              <i class="fas fa-file-pdf"></i>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Policy versions step (after policy selection) -->
    <template v-else-if="selectedFramework && selectedFrameworkVersion && selectedPolicy && !selectedPolicyVersion">
      <div class="section-header">Policy Versions</div>
      <div class="card-grid">
        <div v-for="version in selectedPolicy.versions" :key="version.id" class="card" @click="selectPolicyVersion(version)">
          <div class="card-header">
            <div class="card-icon">
              <i :class="categoryIcon(version.category)"></i>
            </div>
            <div class="card-status" :class="statusClass(version.status)">{{ version.status }}</div>
          </div>
          <div class="card-content">
            <div class="card-title">{{ version.name }}</div>
            <div class="card-category">Category: {{ version.category }}</div>
            <div class="card-count">
              <span class="policies-count">
                <i class="fas fa-file-alt"></i> Subpolicies: {{ version.subpolicy_count || 0 }}
              </span>
            </div>
            <div v-if="version.previous_version_id" class="card-version-info">
              <span>Previous version: {{ version.previous_version_name }}</span>
            </div>
            <div class="card-desc">{{ version.description }}</div>
          </div>
          <div class="card-actions card-actions-bottom">
            <button class="pdf-icon-btn" @click.stop="showDetails(version)">
              <i class="fas fa-file-pdf"></i>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Policy version step: show subpolicies -->
    <template v-else-if="selectedFramework && selectedFrameworkVersion && selectedPolicy && selectedPolicyVersion">
      <div class="section-header">Subpolicies</div>
      <div class="card-grid">
        <div v-for="sub in selectedPolicyVersion.subpolicies" :key="sub.id" class="card">
          <div class="card-header">
            <div class="card-icon">
              <i :class="categoryIcon(sub.category)"></i>
            </div>
            <div class="card-status" :class="statusClass(sub.status)">{{ sub.status }}</div>
          </div>
          <div class="card-content">
            <div class="card-title">{{ sub.name }}</div>
            <div class="card-category">Category: {{ sub.category }}</div>
            <div class="card-desc">{{ sub.description }}</div>
          </div>
          <div class="card-actions card-actions-bottom">
            <button class="pdf-icon-btn" @click.stop="showDetails(sub)">
              <i class="fas fa-file-pdf"></i>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Add Modal Component -->
    <div v-if="showDetailsModal" class="details-modal-overlay" @click="closeDetailsModal">
      <div class="details-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedDetails.name }}</h2>
          <button class="modal-close" @click="closeDetailsModal">×</button>
        </div>
        <div class="modal-content">
          <div class="modal-section">
            <h3>Description</h3>
            <p>{{ selectedDetails.description }}</p>
          </div>
          
          <!-- Version information section -->
          <div class="modal-section" v-if="selectedDetails.previous_version_id">
            <h3>Version Information</h3>
            <div class="version-info-container">
              <div class="version-info-item">
                <span class="version-info-label">Version Number:</span>
                <span class="version-info-value">{{ selectedDetails.version }}</span>
              </div>
              <div class="version-info-item">
                <span class="version-info-label">Previous Version:</span>
                <span class="version-info-value">{{ selectedDetails.previous_version_name }}</span>
              </div>
              <div class="version-info-item">
                <span class="version-info-label">Created By:</span>
                <span class="version-info-value">{{ selectedDetails.created_by }}</span>
              </div>
              <div class="version-info-item">
                <span class="version-info-label">Created Date:</span>
                <span class="version-info-value">{{ formatDate(selectedDetails.created_date) }}</span>
              </div>
            </div>
          </div>
          
          <div class="modal-section" v-if="selectedDetails.versions">
            <!-- <h3>Versions</h3> -->
            <div class="version-list">
              <div v-for="version in selectedDetails.versions" :key="version.id" class="version-item">
                <span class="version-name">{{ version.name }}</span>
                <span class="version-status" :class="statusClass(version.status)">{{ version.status }}</span>
              </div>
            </div>
          </div>
          <div class="modal-section" v-if="selectedDetails.subpolicies">
            <!-- <h3>Subpolicies</h3> -->
            <div class="subpolicy-list">
              <div v-for="sub in selectedDetails.subpolicies" :key="sub.id" class="subpolicy-item">
                <h4>{{ sub.name }}</h4>
                <p>{{ sub.description }}</p>
                <span class="subpolicy-status" :class="statusClass(sub.status)">{{ sub.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'

const activeTab = ref('framework')
const selectedFramework = ref(null)
const selectedFrameworkVersion = ref(null)
const selectedPolicy = ref(null)
const selectedPolicyVersion = ref(null)
// const selectedSubpolicy = ref(null) // Not used anymore since we don't navigate to subpolicy details
const frameworkDropdown = ref('')

// Add new refs for view modes and framework selection
const policyViewMode = ref('card')
const subpolicyViewMode = ref('card')
const selectedPolicyFramework = ref('')
const selectedSubpolicyFramework = ref('')

// Add new refs for modal
const showDetailsModal = ref(false)
const selectedDetails = ref(null)

// Add loading and error states
const loading = ref(false)
const policiesLoading = ref(false) // Separate loading state for policies
const error = ref(null)

// Add cache for subpolicies data to avoid redundant API calls
const subpoliciesCache = ref({
  lastFetched: null,
  data: null,
  frameworkFilter: null
})

// Add separate loading state for subpolicies
const subpoliciesLoading = ref(false)

// API constants
const API_BASE_URL = 'http://localhost:8000/api'

// Data stores
const frameworks = ref([])
const policies = ref([])
const subpolicies = ref([])

// Add a cache for policies data to avoid redundant API calls
const policiesCache = ref({
  lastFetched: null,
  data: null,
  frameworkFilter: null
})

// Fetch all frameworks from API
const fetchFrameworks = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`${API_BASE_URL}/all-policies/frameworks/`)
    frameworks.value = response.data
    loading.value = false
  } catch (err) {
    console.error('Error fetching frameworks:', err)
    error.value = 'Failed to fetch frameworks'
    loading.value = false
  }
}

// Fetch framework versions
const fetchFrameworkVersions = async (frameworkId) => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching framework versions for framework ID: ${frameworkId}`)
    const response = await axios.get(`${API_BASE_URL}/all-policies/frameworks/${frameworkId}/versions/`)
    
    console.log('Framework versions response:', response.data)
    
    // Initialize versions array if not present
    if (!selectedFramework.value.versions) {
      selectedFramework.value.versions = []
    }
    
    // Update the selected framework with the versions data
    selectedFramework.value.versions = response.data
    
    loading.value = false
  } catch (err) {
    console.error('Error fetching framework versions:', err)
    if (err.response) {
      console.error('Response status:', err.response.status)
      console.error('Response data:', err.response.data)
      error.value = `Failed to fetch framework versions: ${err.response.data.error || 'Server error'}`
    } else if (err.request) {
      console.error('No response received:', err.request)
      error.value = 'Failed to fetch framework versions: No response from server'
    } else {
      console.error('Error details:', err.message)
      error.value = `Failed to fetch framework versions: ${err.message}`
    }
    
    // Initialize empty versions array to prevent UI errors
    if (selectedFramework.value) {
      selectedFramework.value.versions = []
    }
    
    loading.value = false
  }
}

// Fetch policies for a specific framework version
const fetchFrameworkVersionPolicies = async (versionId) => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`${API_BASE_URL}/all-policies/framework-versions/${versionId}/policies/`)
    // Update the selected framework version with the policies data
    if (selectedFrameworkVersion.value) {
      selectedFrameworkVersion.value.policies = response.data
    }
    loading.value = false
  } catch (err) {
    console.error('Error fetching framework version policies:', err)
    error.value = 'Failed to fetch policies'
    loading.value = false
  }
}

// Fetch all policies for Policies tab with optimized performance
const fetchAllPolicies = async () => {
  policiesLoading.value = true
  error.value = null
  
  const currentFrameworkFilter = selectedPolicyFramework.value
  
  // Check if we have cached data for this filter and it's recent (less than 1 minute old)
  const now = Date.now()
  const cacheAge = policiesCache.value.lastFetched ? now - policiesCache.value.lastFetched : null
  const isCacheValid = policiesCache.value.data && 
                      cacheAge && 
                      cacheAge < 60000 && // Cache valid for 1 minute
                      policiesCache.value.frameworkFilter === currentFrameworkFilter
  
  if (isCacheValid) {
    console.log("Using cached policies data")
    policies.value = policiesCache.value.data
    policiesLoading.value = false
    return
  }
  
  console.log("Cache invalid, fetching fresh policy data")
  
  let url = `${API_BASE_URL}/all-policies/policies/`
  
  // Add framework filter if selected
  if (currentFrameworkFilter) {
    url += `?framework_id=${currentFrameworkFilter}`
  }
  
  try {
    console.log("Fetching all policies...")
    const response = await axios.get(url)
    
    // Show initial data immediately for better user experience
    const initialPolicies = response.data
    policies.value = initialPolicies.map(policy => ({
      ...policy,
      // Initialize with null version_count to show loading indicator
      version_count: policy.version_count
    }))
    
    // Check if the backend can provide versions count without needing additional API calls
    const hasVersionsInfo = initialPolicies.length > 0 && 
                          (initialPolicies[0].version_count !== undefined || 
                           (initialPolicies[0].versions && Array.isArray(initialPolicies[0].versions)))
    
    if (hasVersionsInfo) {
      // Backend already provides version info, no need for additional calls
      console.log("Backend already provides version info, using it directly")
      
      // Ensure all policies have version_count property
      const processedPolicies = initialPolicies.map(policy => ({
        ...policy,
        version_count: policy.version_count || (policy.versions ? policy.versions.length : 0)
      }))
      
      policies.value = processedPolicies
      
      // Update cache
      policiesCache.value = {
        lastFetched: now,
        data: processedPolicies,
        frameworkFilter: currentFrameworkFilter
      }
      
      policiesLoading.value = false
      return
    }
    
    // If we need version info, use a more efficient approach with Promise.all
    console.log("Fetching version info for policies in parallel")
    
    // Prepare all version fetch promises
    const versionFetchPromises = initialPolicies.map(policy => {
      return axios.get(`${API_BASE_URL}/all-policies/policies/${policy.id}/versions/`)
        .then(versionsResponse => {
          if (versionsResponse.data && Array.isArray(versionsResponse.data)) {
            return {
              ...policy,
              versions: versionsResponse.data,
              version_count: versionsResponse.data.length
            }
          }
          return policy
        })
        .catch(err => {
          console.error(`Error fetching versions for policy ${policy.id}:`, err)
          return policy
        })
    })
    
    // Wait for all promises to resolve in parallel
    const enhancedPolicies = await Promise.all(versionFetchPromises)
    
    policies.value = enhancedPolicies
    
    // Update cache
    policiesCache.value = {
      lastFetched: now,
      data: enhancedPolicies,
      frameworkFilter: currentFrameworkFilter
    }
    
    console.log(`Loaded ${enhancedPolicies.length} policies with complete version data`)
    
  } catch (err) {
    console.error('Error fetching policies:', err)
    error.value = 'Failed to fetch policies'
  } finally {
    policiesLoading.value = false
  }
}

// Fetch policy versions
const fetchPolicyVersions = async (policyId) => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching policy versions for policy ID: ${policyId}`)
    
    // This is the most reliable endpoint to get ALL versions
    const response = await axios.get(`${API_BASE_URL}/all-policies/policies/${policyId}/versions/`)
    
    console.log('Policy versions response:', response.data)
    
    // Initialize versions array if not present
    if (!selectedPolicy.value.versions) {
      selectedPolicy.value.versions = []
    }
    
    // Update the selected policy with the versions data
    selectedPolicy.value.versions = response.data
    
    // Also update the versions count in the display
    if (selectedPolicy.value && response.data.length > 0) {
      // Update the versions count property to match actual number of versions
      selectedPolicy.value.version_count = response.data.length
    }
    
    loading.value = false
  } catch (err) {
    console.error('Error fetching policy versions:', err)
    if (err.response) {
      console.error('Response status:', err.response.status)
      console.error('Response data:', err.response.data)
      error.value = `Failed to fetch policy versions: ${err.response.data.error || 'Server error'}`
    } else if (err.request) {
      console.error('No response received:', err.request)
      error.value = 'Failed to fetch policy versions: No response from server'
    } else {
      console.error('Error details:', err.message)
      error.value = `Failed to fetch policy versions: ${err.message}`
    }
    
    // Initialize empty versions array to prevent UI errors
    if (selectedPolicy.value) {
      selectedPolicy.value.versions = []
    }
    
    loading.value = false
  }
}

// Fetch all subpolicies for Subpolicies tab
const fetchAllSubpolicies = async () => {
  subpoliciesLoading.value = true
  error.value = null
  
  const currentFrameworkFilter = selectedSubpolicyFramework.value
  
  // Check if we have cached data for this filter and it's recent (less than 1 minute old)
  const now = Date.now()
  const cacheAge = subpoliciesCache.value.lastFetched ? now - subpoliciesCache.value.lastFetched : null
  const isCacheValid = subpoliciesCache.value.data && 
                      cacheAge && 
                      cacheAge < 60000 && // Cache valid for 1 minute
                      subpoliciesCache.value.frameworkFilter === currentFrameworkFilter
  
  if (isCacheValid) {
    console.log("Using cached subpolicies data")
    subpolicies.value = subpoliciesCache.value.data
    subpoliciesLoading.value = false
    return
  }
  
  console.log("Cache invalid, fetching fresh subpolicies data")
  
  let url = `${API_BASE_URL}/all-policies/subpolicies/`
  
  // Add framework filter if selected
  if (currentFrameworkFilter) {
    url += `?framework_id=${currentFrameworkFilter}`
  }
  
  try {
    console.log(`Fetching subpolicies from: ${url}`)
    const response = await axios.get(url)
    console.log(`Received ${response.data.length} subpolicies`)
    
    // For debugging
    if (response.data.length > 0) {
      console.log('Sample subpolicy:', response.data[0])
    }
    
    const subpolicyData = response.data
    
    // Update the subpolicies with the data
    subpolicies.value = subpolicyData
    
    // Update cache
    subpoliciesCache.value = {
      lastFetched: now,
      data: subpolicyData,
      frameworkFilter: currentFrameworkFilter
    }
    
    console.log(`Successfully loaded ${subpolicyData.length} subpolicies`)
  } catch (err) {
    console.error('Error fetching subpolicies:', err)
    if (err.response) {
      console.error('Response status:', err.response.status)
      console.error('Response data:', err.response.data)
      error.value = `Failed to fetch subpolicies: ${err.response.data.error || 'Server error'}`
    } else if (err.request) {
      console.error('No response received:', err.request)
      error.value = 'Failed to fetch subpolicies: No response from server'
    } else {
      console.error('Error details:', err.message)
      error.value = `Failed to fetch subpolicies: ${err.message}`
    }
    
    // Initialize empty array if error occurs
    subpolicies.value = []
  } finally {
    subpoliciesLoading.value = false
  }
}

// Fetch subpolicies for a specific policy version
const fetchPolicyVersionSubpolicies = async (versionId) => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching subpolicies for policy version ID: ${versionId}`)
    const response = await axios.get(`${API_BASE_URL}/all-policies/policy-versions/${versionId}/subpolicies/`)
    
    console.log('Subpolicies response:', response.data)
    
    // Initialize subpolicies array if not present
    if (!selectedPolicyVersion.value.subpolicies) {
      selectedPolicyVersion.value.subpolicies = []
    }
    
    // Update the selected policy version with the subpolicies data
    selectedPolicyVersion.value.subpolicies = response.data
    
    loading.value = false
  } catch (err) {
    console.error('Error fetching policy version subpolicies:', err)
    if (err.response) {
      console.error('Response status:', err.response.status)
      console.error('Response data:', err.response.data)
      error.value = `Failed to fetch subpolicies: ${err.response.data.error || 'Server error'}`
    } else if (err.request) {
      console.error('No response received:', err.request)
      error.value = 'Failed to fetch subpolicies: No response from server'
    } else {
      console.error('Error details:', err.message)
      error.value = `Failed to fetch subpolicies: ${err.message}`
    }
    
    // Initialize empty subpolicies array to prevent UI errors
    if (selectedPolicyVersion.value) {
      selectedPolicyVersion.value.subpolicies = []
    }
    
    loading.value = false
  }
}

// Event handlers for selection changes
const selectFramework = (fw) => {
  selectedFramework.value = fw
  selectedFrameworkVersion.value = null
  selectedPolicy.value = null
  selectedPolicyVersion.value = null
  
  // Update the framework dropdown to keep UI in sync
  if (fw && fw.id) {
    frameworkDropdown.value = fw.id.toString()
  }
  
  // Fetch framework versions
  fetchFrameworkVersions(fw.id)
}

const selectFrameworkVersion = (version) => {
  selectedFrameworkVersion.value = version
  selectedPolicy.value = null
  selectedPolicyVersion.value = null
  
  // Fetch policies for this framework version
  fetchFrameworkVersionPolicies(version.id)
}

const selectPolicy = (policy) => {
  selectedPolicy.value = policy
  selectedPolicyVersion.value = null
  
  // Fetch policy versions
  fetchPolicyVersions(policy.id)
}

const selectPolicyVersion = (version) => {
  selectedPolicyVersion.value = version
  
  // Fetch subpolicies for this policy version
  fetchPolicyVersionSubpolicies(version.id)
}

// Watch for tab changes to load relevant data
const handleTabChange = () => {
  // Clear error message when switching tabs
  error.value = null;
  
  if (activeTab.value === 'policies') {
    console.log('Switching to Policies tab, fetching all policies...');
    fetchAllPolicies();
  } else if (activeTab.value === 'subpolicies') {
    console.log('Switching to Subpolicies tab, fetching all subpolicies...');
    fetchAllSubpolicies();
  } else if (activeTab.value === 'framework') {
    console.log('Switching to Frameworks tab');
    // Frameworks are already loaded on component mount
  }
}

// Watch for framework filter changes in policies tab
const handlePolicyFrameworkChange = () => {
  fetchAllPolicies()
}

// Watch for framework filter changes in subpolicies tab
const handleSubpolicyFrameworkChange = () => {
  fetchAllSubpolicies()
}

// Add a simple, direct selection method for the framework dropdown
const handleFrameworkSelection = async () => {
  try {
    if (!frameworkDropdown.value) {
      // If no framework is selected, reset the state
      selectedFramework.value = null
      selectedFrameworkVersion.value = null
      selectedPolicy.value = null
      selectedPolicyVersion.value = null
      return
    }

    // Find the selected framework
    const fwId = String(frameworkDropdown.value)
    console.log(`Selecting framework ID: ${fwId}`)
    
    const fw = frameworks.value.find(f => String(f.id) === fwId)
    if (fw) {
      console.log(`Found framework: ${fw.name}`)
      
      // Wait for the next tick to avoid reactivity issues
      await nextTick()
      
      // Set the selected framework
      selectedFramework.value = { ...fw }  // Use spread operator to create a new object
      
      // Reset other selections
      selectedFrameworkVersion.value = null
      selectedPolicy.value = null
      selectedPolicyVersion.value = null
      
      // Fetch versions
      fetchFrameworkVersions(fw.id)
    } else {
      console.error(`No framework found with ID: ${fwId}`)
    }
  } catch (err) {
    console.error('Error in framework selection:', err)
    error.value = 'Error selecting framework'
  }
}

// Show details modal
const showDetails = async (item) => {
  loading.value = true
  error.value = null
  
  try {
    console.log('Showing details for item:', item)
    
    // Check if item exists and has an ID
    if (item && item.id) {
      // Framework 
      if (item.category) {
        console.log('Detected framework, fetching all versions for framework:', item.id)
        try {
          // This is the endpoint that should return the complete version chain
          const response = await axios.get(`${API_BASE_URL}/all-policies/framework-versions/${item.id}/`)
          if (response.data && Array.isArray(response.data)) {
            console.log('Fetched complete framework versions:', response.data.length)
            // Replace existing versions with the complete set
            item.versions = response.data
            
            // Update the displayed version count
            updatePolicyInList(item.id, { 
              versions: response.data,
              version_count: response.data.length
            })
          } else {
            console.log('No framework versions returned')
          }
        } catch (err) {
          console.error('Error fetching framework versions:', err)
          // Try fallback to original endpoint if there's an error
          try {
            console.log('Trying fallback endpoint for framework versions')
            const fallbackResponse = await axios.get(`${API_BASE_URL}/all-policies/frameworks/${item.id}/versions/`)
            item.versions = fallbackResponse.data
            
            // Update the displayed version count
            updatePolicyInList(item.id, { 
              versions: fallbackResponse.data,
              version_count: fallbackResponse.data.length
            })
          } catch (fallbackErr) {
            console.error('Error in fallback endpoint:', fallbackErr)
            if (!item.versions) {
              item.versions = []
            }
          }
        }
      }
      
      // Policy - Always fetch the complete versions regardless of what's already loaded
      else if (!item.previous_version_id && !item.parent_policy_id) {
        console.log('Detected policy, fetching complete versions for policy:', item.id)
        try {
          // Use the specialized endpoint that returns the complete version chain
          const response = await axios.get(`${API_BASE_URL}/all-policies/policies/${item.id}/versions/`)
          
          if (response.data && Array.isArray(response.data)) {
            const versionCount = response.data.length
            console.log(`Fetched ${versionCount} policy versions`)
            
            // Update the policy with the complete version data
            item.versions = response.data
            item.version_count = versionCount
            
            // Update the policy in the main list
            updatePolicyInList(item.id, { 
              versions: response.data,
              version_count: versionCount
            })
          }
        } catch (err) {
          console.error('Error fetching policy versions:', err)
          if (!item.versions) {
            item.versions = []
          }
        }
      }
      
      // Policy version
      else if (item.previous_version_id && !item.subpolicies) {
        console.log('Detected policy version, fetching subpolicies:', item.id)
        try {
          const response = await axios.get(`${API_BASE_URL}/all-policies/policy-versions/${item.id}/subpolicies/`)
          item.subpolicies = response.data
        } catch (err) {
          console.error('Error fetching subpolicies:', err)
          item.subpolicies = []
        }
      }
      
      // Subpolicy - When clicked directly, fetch more details if needed
      else if (selectedPolicyVersion.value) {
        console.log('Detected subpolicy click, checking for complete details:', item.id)
        try {
          // Fetch detailed subpolicy information if needed
          if (!item.full_details_loaded) {
            console.log('Fetching complete subpolicy details')
            const response = await axios.get(`${API_BASE_URL}/all-policies/subpolicies/${item.id}/`)
            
            // Merge the detailed data with our item
            Object.assign(item, response.data)
            item.full_details_loaded = true
          }
        } catch (err) {
          console.error('Error fetching subpolicy details:', err)
        }
      }
    }
    
    selectedDetails.value = item
    showDetailsModal.value = true
  } catch (err) {
    console.error('Error in showDetails:', err)
    error.value = 'Failed to load complete details'
  } finally {
    loading.value = false
  }
}

// Helper function to update policy in policies list with updated data
const updatePolicyInList = (policyId, updatedData) => {
  // Update in policies list
  const policyIndex = policies.value.findIndex(p => p.id === policyId)
  if (policyIndex !== -1) {
    policies.value[policyIndex] = { ...policies.value[policyIndex], ...updatedData }
  }
  
  // If it's the selected policy, update that too
  if (selectedPolicy.value && selectedPolicy.value.id === policyId) {
    selectedPolicy.value = { ...selectedPolicy.value, ...updatedData }
  }
}

// Close modal
const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedDetails.value = null
}

// Reset navigation to previous level
const resetNavigation = (idx) => {
  // Always go back to the previous filter (one step back)
  switch(idx) {
    case 0:
      // If first breadcrumb, reset everything
      selectedFramework.value = null;
      selectedFrameworkVersion.value = null;
      selectedPolicy.value = null;
      selectedPolicyVersion.value = null;
      frameworkDropdown.value = '';
      activeTab.value = 'framework';
      break;
    case 1:
      selectedFrameworkVersion.value = null;
      selectedPolicy.value = null;
      selectedPolicyVersion.value = null;
      break;
    case 2:
      selectedPolicy.value = null;
      selectedPolicyVersion.value = null;
      break;
    case 3:
      selectedPolicyVersion.value = null;
      break;
    default:
      // fallback: reset all
      selectedFramework.value = null;
      selectedFrameworkVersion.value = null;
      selectedPolicy.value = null;
      selectedPolicyVersion.value = null;
      frameworkDropdown.value = '';
      activeTab.value = 'framework';
      break;
  }
}

// Utility functions
const statusClass = (status) => {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s.includes('inactive')) return 'inactive'
  if (s.includes('active')) return 'active'
  if (s.includes('pending')) return 'pending'
  return ''
}

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  } catch (e) {
    return dateString
  }
}

// Icon mapping for categories
const categoryIcon = (category) => {
  switch ((category || '').toLowerCase()) {
    case 'governance': return 'fas fa-shield-alt';
    case 'access control': return 'fas fa-user-shield';
    case 'asset management': return 'fas fa-boxes';
    case 'cryptography': return 'fas fa-key';
    case 'data management': return 'fas fa-database';
    case 'device management': return 'fas fa-mobile-alt';
    case 'risk management': return 'fas fa-exclamation-triangle';
    case 'supplier management': return 'fas fa-handshake';
    case 'business continuity': return 'fas fa-business-time';
    case 'privacy': return 'fas fa-user-secret';
    case 'system protection': return 'fas fa-shield-virus';
    case 'incident response': return 'fas fa-ambulance';
    default: return 'fas fa-file-alt';
  }
}

// Computed properties for filtered data
const filteredFrameworks = computed(() => {
  // If no frameworks data yet, return empty array to avoid errors
  if (!frameworks.value || frameworks.value.length === 0) {
    return []
  }

  // If no dropdown selection, show all frameworks
  if (!frameworkDropdown.value) {
    return frameworks.value
  }
  
  // Safe string comparison to handle different types
  const fwId = String(frameworkDropdown.value)
  const filtered = frameworks.value.filter(fw => String(fw.id) === fwId)
  
  console.log(`Framework filtering: looking for ID ${fwId}, found ${filtered.length} matches`)
  
  // If we couldn't find any matches, return all frameworks instead of empty array
  return filtered.length > 0 ? filtered : frameworks.value
})

const filteredPolicies = computed(() => {
  return policies.value
})

const filteredSubpolicies = computed(() => {
  return subpolicies.value
})

const breadcrumbs = computed(() => {
  const arr = []
  if (selectedFramework.value) {
    arr.push({ 
      id: 'fw-' + selectedFramework.value.id, 
      name: selectedFramework.value.name 
    })
  }
  if (selectedFrameworkVersion.value) {
    arr.push({ 
      id: 'fwv-' + selectedFrameworkVersion.value.id, 
      name: selectedFrameworkVersion.value.name 
    })
  }
  if (selectedPolicy.value) {
    arr.push({
      id: 'policy-' + selectedPolicy.value.id,
      name: selectedPolicy.value.name
    })
  }
  if (selectedPolicyVersion.value) {
    arr.push({
      id: 'policyv-' + selectedPolicyVersion.value.id,
      name: selectedPolicyVersion.value.name
    })
  }
  return arr
})

// Add a preload function to fetch data in the background
const preloadData = () => {
  // Preload policies data if not cached
  if (!policiesCache.value.data) {
    console.log('Preloading policies data in the background...')
    // Use a setTimeout to avoid blocking the UI
    setTimeout(() => {
      fetchAllPolicies()
    }, 1000) // Wait 1 second after component load before preloading
  }
  
  // Preload subpolicies data if not cached
  if (!subpoliciesCache.value.data) {
    console.log('Preloading subpolicies data in the background...')
    // Use a setTimeout to avoid blocking the UI
    setTimeout(() => {
      fetchAllSubpolicies()
    }, 2000) // Wait 2 seconds after component load before preloading (stagger requests)
  }
}

// Load data on component mount
onMounted(() => {
  fetchFrameworks()
  
  // If starting directly on policies or subpolicies tab, load that data too
  if (activeTab.value === 'policies') {
    fetchAllPolicies()
  } else if (activeTab.value === 'subpolicies') {
    fetchAllSubpolicies()
  } else {
    // If on frameworks tab, preload other tab data in the background for faster tab switching
    preloadData()
  }
})

// Setup watchers outside of onMounted to avoid reactivity issues
watch(activeTab, handleTabChange)
watch(selectedPolicyFramework, handlePolicyFrameworkChange)
watch(selectedSubpolicyFramework, handleSubpolicyFrameworkChange)
// We're not watching frameworkDropdown since we have the direct @change handler
</script> 

<style src="./AllPolicies.css"></style> 
<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.loading-message {
  text-align: center;
  padding: 16px;
  color: #4f6cff;
  font-weight: 500;
}

.loading-versions {
  display: inline-flex;
  align-items: center;
  color: #4f6cff;
  font-size: 0.9rem;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 24px 32px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.loading-spinner i {
  font-size: 2rem;
  color: #4f6cff;
  margin-bottom: 12px;
}

.loading-spinner span {
  font-size: 1rem;
  font-weight: 500;
  color: #333;
}

.error-message {
  margin: 0 auto 20px auto;
  padding: 12px 16px;
  background: #fbeaea;
  color: #dc2626;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 600px;
}

.error-message i {
  font-size: 1.2rem;
}

.card-version-info {
  margin: 8px 0;
  padding: 6px 10px;
  background: #f0f5ff;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #4a5568;
  border-left: 3px solid #4f6cff;
}

.card-version-info span {
  display: block;
  font-weight: 500;
}

.version-info-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f7f9fb;
  padding: 12px;
  border-radius: 8px;
}

.version-info-item {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
}

.version-info-label {
  font-weight: 600;
  color: #4a5568;
  min-width: 120px;
}

.version-info-value {
  color: #1f2937;
}

.policies-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: #4a5568;
}

.policies-count i {
  color: #4f6cff;
  font-size: 0.9rem;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style> 
