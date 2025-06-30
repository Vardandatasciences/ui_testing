<template>
  <div class="framework-policies-container">
    <div class="breadcrumb-tab">
      <span class="breadcrumb-chip">
        {{ frameworkName }}
        <span class="breadcrumb-close" @click="goBack">×</span>
      </span>
    </div>
    <h2>Policies for {{ frameworkName }}</h2>
    <div class="top-controls">
      <div class="entity-dropdown-section">
        <label>Filter by Entity</label>
        <select v-model="selectedEntity" class="entity-dropdown">
          <option value="">All Entities</option>
          <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.label }}</option>
        </select>
      </div>
      <div v-if="selectedEntity" class="active-filter">
        <span>Filtered by: {{ entities.find(e => e.id === selectedEntity)?.label || selectedEntity }}</span>
        <button class="clear-filter-btn" @click="clearEntityFilter">Clear Filter</button>
      </div>
    </div>
    <div class="policy-card-grid">
      <div v-for="policy in policies" :key="policy.id" class="policy-card">
        <div class="policy-card-header">
          <div class="policy-title-section">
            <span class="policy-icon">
              <i class="fas fa-file-alt"></i>
            </span>
            <span class="policy-card-title">{{ policy.name }}</span>
          </div>
        </div>
        <div class="policy-card-category">Category: {{ policy.category }}</div>
        <div class="policy-card-desc">{{ policy.description }}</div>
        <div class="policy-card-actions">
          <div class="action-buttons">
            <label class="switch" @click.stop>
              <input type="checkbox" :checked="policy.status === 'Active'" @change="toggleStatus(policy)" />
              <span class="slider"></span>
            </label>
            <span class="switch-label" :class="policy.status === 'Active' ? 'active' : 'inactive'">{{ policy.status }}</span>
            <button v-if="policy.status === 'Active'"
                    @click="acknowledgePolicy(policy)"
                    class="acknowledge-btn"
                    :class="{ 'acknowledged': policy.isAcknowledged }">
              {{ policy.isAcknowledged ? 'Acknowledged' : 'Acknowledge' }}
            </button>
            <!-- Export controls -->
            <select v-model="selectedExportFormat[policy.id]" class="export-dropdown" style="margin-left:8px;">
              <option value="" disabled selected>Select format</option>
              <option v-for="fmt in exportFormats" :key="fmt" :value="fmt">{{ fmt.toUpperCase() }}</option>
            </select>
            <button @click="exportPolicy(policy.id)" :disabled="!selectedExportFormat[policy.id]" style="margin-left:4px;">
              Export
            </button>
          </div>
          <span class="document-icon" @click="showPolicyDetails(policy.id)">
            <i class="fas fa-file-lines"></i>
          </span>
        </div>
      </div>
    </div>
 
    <!-- Policy Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Policy Details</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div v-if="isLoadingDetails" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i> Loading details...
        </div>
        <div v-else-if="policyDetails" class="modal-body">
          <div class="detail-row">
            <span class="detail-label">Policy Name:</span>
            <span class="detail-value">{{ policyDetails.PolicyName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span class="detail-value">{{ policyDetails.PolicyDescription }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Department:</span>
            <span class="detail-value">{{ policyDetails.Department }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Version:</span>
            <span class="detail-value">{{ policyDetails.CurrentVersion }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">{{ policyDetails.Status }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Active/Inactive:</span>
            <span class="detail-value">{{ policyDetails.ActiveInactive }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Identifier:</span>
            <span class="detail-value">{{ policyDetails.Identifier }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Start Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.StartDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">End Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.EndDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created By:</span>
            <span class="detail-value">{{ policyDetails.CreatedByName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.CreatedByDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Applicability:</span>
            <span class="detail-value">{{ policyDetails.Applicability }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Scope:</span>
            <span class="detail-value">{{ policyDetails.Scope }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Objective:</span>
            <span class="detail-value">{{ policyDetails.Objective }}</span>
          </div>
          <div class="detail-row" v-if="policyDetails.DocURL">
            <span class="detail-label">Documentation:</span>
            <a :href="policyDetails.DocURL" target="_blank" class="doc-link">View Documentation</a>
          </div>
         
          <!-- Subpolicies section -->
          <div v-if="policyDetails.subpolicies && policyDetails.subpolicies.length > 0" class="subpolicies-section">
            <h4>Subpolicies</h4>
            <div v-for="(subpolicy, index) in policyDetails.subpolicies" :key="index" class="subpolicy-item">
              <div class="subpolicy-header">
                <span class="subpolicy-name">{{ subpolicy.SubPolicyName }}</span>
                <span class="subpolicy-status" :class="subpolicy.Status.toLowerCase()">{{ subpolicy.Status }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Identifier:</span>
                <span>{{ subpolicy.Identifier }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Description:</span>
                <span>{{ subpolicy.Description }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Control:</span>
                <span>{{ subpolicy.Control }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-subpolicies">
            No subpolicies found for this policy.
          </div>
        </div>
        <div v-else class="modal-error">
          Failed to load policy details.
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>
 
<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
 
const router = useRouter()
const route = useRoute()
const frameworkId = route.params.frameworkId
const frameworkName = ref('')
const policies = ref([])
const allPolicies = ref([]) // Store all policies for filtering
const selectedEntity = ref('')
const entities = ref([])
const isLoading = ref(false)
 
// Add export format state for each policy
const exportFormats = ['xlsx', 'pdf', 'csv', 'json', 'xml', 'txt']
const selectedExportFormat = reactive({}) // { [policyId]: format }
 
// Modal and details states
const showModal = ref(false)
const isLoadingDetails = ref(false)
const policyDetails = ref(null)
 
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
 
// Fetch policies for the selected framework
const fetchPolicies = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`/api/frameworks/${frameworkId}/policies-list/`)
    allPolicies.value = response.data.policies
    frameworkName.value = response.data.framework.name
    // Initialize export format for each policy to "" so the placeholder shows
    for (const policy of allPolicies.value) {
      if (selectedExportFormat[policy.id] === undefined) {
        selectedExportFormat[policy.id] = "";
      }
    }
  } catch (error) {
    console.error('Error fetching policies:', error)
  } finally {
    isLoading.value = false
  }
}

// Fetch entities from API
const fetchEntities = async () => {
  try {
    const response = await axios.get('/api/entities/')
    entities.value = response.data.entities || []
  } catch (error) {
    console.error('Error fetching entities:', error)
  }
}

// Filter policies based on selected entity
const filteredPolicies = computed(() => {
  if (!selectedEntity.value) {
    return allPolicies.value
  }
  
  console.log('Filtering policies with entity:', selectedEntity.value)
  console.log('Total policies before filtering:', allPolicies.value.length)
  
  const filtered = allPolicies.value.filter(policy => {
    // If policy has no entities field, don't show it when filtering
    if (!policy.Entities) return false
    
    // If policy applies to all entities, always show it when any entity filter is active
    if (policy.Entities === 'all') {
      return true
    }
    
    // If "All Entities" is selected, show all policies
    if (selectedEntity.value === 'all') {
      return true
    }
    
    // For specific entity selection
    if (Array.isArray(policy.Entities)) {
      // Show policy if it applies to all entities OR includes the selected entity
      // Handle both string and numeric entity IDs
      const selectedEntityInt = parseInt(selectedEntity.value)
      const selectedEntityStr = selectedEntity.value.toString()
      
      return policy.Entities.includes('all') || 
             policy.Entities.includes(selectedEntityInt) || 
             policy.Entities.includes(selectedEntityStr)
    }
    
    return false
  })
  
  console.log('Filtered policies count:', filtered.length)
  console.log('Filtered policies:', filtered.map(p => ({ name: p.name, entities: p.Entities })))
  
  return filtered
})

// Assign filtered policies to the reactive ref
watch(filteredPolicies, (newPolicies) => {
  policies.value = newPolicies
}, { immediate: true })

// Clear entity filter
const clearEntityFilter = () => {
  selectedEntity.value = ''
}
 
// Export selected policy using the framework export API
const exportPolicy = async (policyId) => {
  const format = selectedExportFormat[policyId]
  if (!format) {
    PopupService.warning('Please select an export format.', 'Missing Selection');
    return;
  }
  try {
    // Call the existing framework export API, passing the selected policy ID and format
    const res = await axios.post(`/api/frameworks/${frameworkId}/export/`, {
      format,
      policy_id: policyId // Backend should filter export to this policy
    });
    const { file_url, file_name } = res.data;
    if (!file_url || !file_name) {
      PopupService.error('Export failed: No file URL or name returned.', 'Export Error');
      return;
    }
    try {
      const fileRes = await axios.get(file_url, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([fileRes.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      PopupService.success('Export completed successfully!', 'Export Success');
    } catch (downloadErr) {
      PopupService.error('Export failed during file download.', 'Download Error');
      console.error(downloadErr);
    }
  } catch (err) {
    PopupService.error('Export failed. Please try again.', 'Export Error');
    console.error(err);
  }
}
 
// Show policy details
const showPolicyDetails = async (policyId) => {
  policyDetails.value = null
  showModal.value = true
  isLoadingDetails.value = true
 
  try {
    const response = await axios.get(`/api/policies/${policyId}/details/`)
    policyDetails.value = response.data
  } catch (error) {
    console.error('Error fetching policy details:', error)
  } finally {
    isLoadingDetails.value = false
  }
}
 
// Close the modal
const closeModal = () => {
  showModal.value = false
}
 
// Toggle policy status
const toggleStatus = async (policy) => {
  try {
    // Check if we're deactivating (Active -> Inactive)
    if (policy.status === 'Active') {
      // First: Show reviewer selection popup
      try {
        const response = await axios.get('/api/users-for-reviewer-selection/');
        const reviewers = response.data;
        
        if (reviewers.length === 0) {
          PopupService.warning('No reviewers available. Please contact administrator.', 'No Reviewers');
          return;
        }
        
        // Step 1: Select reviewer
        const reviewerOptions = reviewers.map(reviewer => ({
          value: reviewer.UserId,
          label: `${reviewer.UserName} (${reviewer.Email})`
        }));
        
        PopupService.select(
          'Select a reviewer for this policy deactivation request:',
          'Select Reviewer',
          reviewerOptions,
          async (selectedReviewerId) => {
            console.log('Selected reviewer ID:', selectedReviewerId);
            
            // Step 2: Get reason after reviewer selection
            PopupService.comment(
              'Please provide a reason for deactivating this policy:',
              'Policy Deactivation Reason',
              async (reason) => {
                if (!reason || reason.trim() === '') {
                  PopupService.warning('Deactivation reason is required.', 'Missing Information');
                  return;
                }
                
                try {
                  // Call the API to request status change approval with reviewer ID
                  await axios.post(`/api/policies/${policy.id}/toggle-status/`, {
                    reason: reason.trim(),
                    ReviewerId: selectedReviewerId,
                    cascadeSubpolicies: true
                  });
                  
                  // Show success message
                  PopupService.success('Policy deactivation request submitted. Awaiting approval.', 'Request Submitted');
                  
                  // Refresh data to reflect the new 'Under Review' status
                  await fetchPolicies();
                } catch (error) {
                  console.error('Error submitting deactivation request:', error);
                  PopupService.error('Failed to submit deactivation request. Please try again.', 'Request Failed');
                }
              }
            );
          }
        );
      } catch (error) {
        console.error('Error fetching reviewers:', error);
        PopupService.error('Failed to load reviewers. Please try again.', 'Load Error');
      }
    } else {
      // For activation (Inactive -> Active), use the direct toggle endpoint
      const response = await axios.post(`/api/policies/${policy.id}/toggle-status/`, {
        cascadeSubpolicies: true
      });
     
      // Update local state
      policy.status = response.data.status || 'Active';
     
      // Show feedback to the user
      let message = `Policy status change request submitted.`;
     
      if (response.data.other_versions_deactivated > 0) {
        message += ` ${response.data.other_versions_deactivated} previous version(s) of this policy were automatically deactivated.`;
      }
     
      if (response.data.subpolicies_affected > 0) {
        message += ` ${response.data.subpolicies_affected} subpolicies were also activated.`;
      }
     
      PopupService.success(message, 'Status Update');
     
      // Refresh summary counts
      await fetchPolicies();
    }
  } catch (error) {
    console.error('Error toggling policy status:', error);
    PopupService.error('Failed to update policy status. Please try again.', 'Update Failed');
  }
}
 
// Add acknowledge policy function
const acknowledgePolicy = async (policy) => {
  try {
    const response = await axios.post(`/api/acknowledge-policy/${policy.id}/`)
    policy.isAcknowledged = true
    PopupService.success(response.data.message, 'Policy Acknowledged');
  } catch (error) {
    console.error('Error acknowledging policy:', error)
    PopupService.error('Failed to acknowledge policy. Please try again.', 'Acknowledgment Failed');
  }
}
 
function goBack() {
  const routeParams = { name: 'FrameworkExplorer' }
  
  // If an entity filter is selected, pass it back as a query parameter
  if (selectedEntity.value) {
    routeParams.query = { entity: selectedEntity.value }
  }
  
  router.push(routeParams)
}
 
// Fetch policies on component mount
onMounted(() => {
  fetchPolicies()
  fetchEntities()
  
  // Check if there's an entity filter from the route query parameters
  const entityFromRoute = route.query.entity
  if (entityFromRoute) {
    selectedEntity.value = entityFromRoute
  }
})
</script>
 
<style scoped>
.framework-policies-container {
  padding: 32px 40px;
  margin-left: 200px;
  max-width: calc(100vw - 240px);
  min-height: calc(100vh - 64px);
}
 
.breadcrumb-tab {
  margin-bottom: 24px;
}
 
.breadcrumb-chip {
  background: #e8edfa;
  color: #4f6cff;
  border-radius: 24px;
  padding: 12px 24px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(79,108,255,0.12);
  letter-spacing: 0.01em;
  transition: all 0.2s ease;
}
 
.breadcrumb-chip:hover {
  box-shadow: 0 4px 12px rgba(79,108,255,0.18);
  transform: translateY(-1px);
}
 
.breadcrumb-close {
  margin-left: 12px;
  color: #888;
  font-size: 1rem;
  cursor: pointer;
  font-weight: bold;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
}
 
.breadcrumb-close:hover {
  color: #e53935;
  background-color: rgba(229, 57, 53, 0.1);
}

.top-controls {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 24px;
  margin-bottom: 18px;
  width: 100%;
}

.entity-dropdown-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
}

.entity-dropdown {
  min-width: 160px;
  height: 34px;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.9rem;
  padding: 0 12px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.entity-dropdown:hover {
  border-color: #4f6cff;
}

.entity-dropdown:focus {
  outline: none;
  border-color: #4f6cff;
  box-shadow: 0 0 0 3px rgba(79, 108, 255, 0.1);
}

.active-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f0f4ff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #4f6cff;
}

.clear-filter-btn {
  background: #4f6cff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-filter-btn:hover {
  background: #3a57e8;
}
 
.policy-card-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  width: 100%;
  margin-top: 24px;
  box-sizing: border-box;
  padding: 0 16px;
}
 
.policy-card {
  background: #f7f7fa;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  font-size: 0.85rem;
  cursor: pointer;
  min-height: 120px;
  box-shadow: 0 2px 8px rgba(79,108,255,0.08);
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
  margin: 0;
}
 
.policy-card:hover {
  transform: translateY(-2px) scale(1.025);
  box-shadow: 0 8px 24px rgba(79,108,255,0.13);
}
 
.policy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 700;
  width: 100%;
  margin-bottom: 4px;
}
 
.policy-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #e8e3ff;
  border-radius: 8px;
  color: #6b46c1;
  font-size: 1rem;
}
 
.policy-card-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #f5f5f7;
}
 
.policy-card-status.active {
  color: #22a722;
  background: #e8f7ee;
}
 
.policy-card-status.inactive {
  color: #e53935;
  background: #fbeaea;
}
 
.policy-card-category {
  font-size: 0.85rem;
  color: #6b46c1;
  font-weight: 600;
  background: #e8e3ff;
  border-radius: 8px;
  padding: 2px 8px;
  width: fit-content;
  margin-bottom: 8px;
}
 
.policy-card-desc {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #444;
  font-weight: 400;
  flex-grow: 1;
}
 
.policy-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
 
button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: #4f6cff;
  color: #fff;
  transition: all 0.2s;
  width: fit-content;
}
 
button:hover {
  background: #3a57e8;
  transform: translateY(-1px);
}
 
.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f0f4ff;
  border-radius: 50%;
  color: #4f6cff;
  cursor: pointer;
  transition: all 0.2s ease;
}
 
.document-icon:hover {
  background: #e0e7ff;
  transform: translateY(-2px);
}
 
h2 {
  font-size: 1.6rem;
  margin-bottom: 24px;
  color: #2c3e50;
  font-weight: 700;
}
 
.policy-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}
 
.policy-card-title {
  margin-left: 0;
  word-break: break-word;
  color: #6b46c1;
}
 
/* Modal styles */
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
 
.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.15);
}
 
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 2;
}
 
.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4rem;
}
 
.close-btn {
  font-size: 1.8rem;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
}
 
.close-btn:hover {
  color: #e53935;
}
 
.modal-body {
  padding: 24px;
}
 
.modal-loading, .modal-error {
  padding: 24px;
  text-align: center;
  color: #666;
}
 
.detail-row {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
}
 
.detail-label {
  font-weight: 600;
  width: 140px;
  color: #555;
}
 
.detail-value {
  flex: 1;
  min-width: 200px;
}
 
.doc-link {
  color: #4f6cff;
  text-decoration: none;
  font-weight: 600;
}
 
.doc-link:hover {
  text-decoration: underline;
}
 
/* Subpolicies section */
.subpolicies-section {
  margin-top: 24px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}
 
.subpolicies-section h4 {
  font-size: 1.2rem;
  margin-bottom: 16px;
  color: #2c3e50;
}
 
.subpolicy-item {
  background: #f8f9fd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 3px solid #4f6cff;
}
 
.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
 
.subpolicy-name {
  font-weight: 600;
  font-size: 1rem;
  color: #2c3e50;
}
 
.subpolicy-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}
 
.subpolicy-status.approved {
  color: #22a722;
  background: #e8f7ee;
}
 
.subpolicy-status.inactive, .subpolicy-status.rejected {
  color: #e53935;
  background: #fbeaea;
}
 
.subpolicy-status.under.review {
  color: #f5a623;
  background: #fff5e6;
}
 
.subpolicy-detail {
  margin-bottom: 6px;
  font-size: 0.9rem;
}
 
.subpolicy-label {
  font-weight: 600;
  color: #555;
  margin-right: 6px;
}
 
.no-subpolicies {
  margin-top: 16px;
  color: #666;
  font-style: italic;
  text-align: center;
}
 
@media (max-width: 1200px) {
  .policy-card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    padding: 0 12px;
  }
}
 
@media (max-width: 800px) {
  .policy-card-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 0 8px;
  }
 
  .framework-policies-container {
    padding: 20px;
  }
}
 
.action-buttons {
  display: flex;
  gap: 8px;
}
 
.acknowledge-btn {
  background: #22a722 !important;
}
 
.acknowledge-btn.acknowledged {
  background: #ff9800 !important;
  opacity: 0.95;
  cursor: default;
}
 
.acknowledge-btn:hover:not(.acknowledged) {
  background: #1b8c1b !important;
}
 
.export-dropdown {
  padding: 8px 12px;
  border: 1px solid #6b46c1;
  border-radius: 8px;
  background-color: #fff;
  color: #6b46c1;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236b46c1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 32px;
  min-width: 120px;
}
 
.export-dropdown:hover {
  border-color: #805ad5;
  box-shadow: 0 2px 8px rgba(107, 70, 193, 0.15);
}
 
.export-dropdown:focus {
  outline: none;
  border-color: #805ad5;
  box-shadow: 0 0 0 3px rgba(107, 70, 193, 0.2);
}
 
.export-dropdown option {
  background-color: #fff;
  color: #2d3748;
  padding: 8px;
}
 
.export-dropdown option:checked {
  background-color: #e8e3ff;
  color: #6b46c1;
  font-weight: 600;
}
 
.export-dropdown:disabled {
  background-color: #f7f7fa;
  border-color: #e2e8f0;
  color: #a0aec0;
  cursor: not-allowed;
}
 
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 28px;
  margin-right: 8px;
  vertical-align: middle;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #4f6cff;
  -webkit-transition: .4s;
  transition: .4s;
  border-radius: 28px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: #f5f6fa;
  -webkit-transition: .4s;
  transition: .4s;
  border-radius: 50%;
}
.switch input:checked + .slider {
  background-color: #4f6cff;
}
.switch input:not(:checked) + .slider {
  background-color: #bfc8e6;
}
.switch input:checked + .slider:before {
  -webkit-transform: translateX(20px);
  -ms-transform: translateX(20px);
  transform: translateX(20px);
}
.switch-label {
  font-weight: 600;
  color: #4f6cff;
  min-width: 60px;
  display: inline-block;
  text-align: left;
}
.switch-label.active {
  color: #22a722;
}
.switch-label.inactive {
  color: #e53935;
}
</style>