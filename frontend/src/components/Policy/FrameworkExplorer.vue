<template>
  <div class="framework-explorer-container">
    <div class="export-controls">
      <div class="export-controls-inner">
        <select v-model="selectedExportFormat" class="export-dropdown">
          <option value="" disabled>Select format</option>
          <option value="xlsx">Excel (.xlsx)</option>
          <option value="pdf">PDF (.pdf)</option>
          <option value="csv">CSV (.csv)</option>
          <option value="json">JSON (.json)</option>
          <option value="xml">XML (.xml)</option>
          <option value="txt">Text (.txt)</option>
        </select>
        <button @click="exportFrameworkPolicies">
          Export
        </button>
      </div>
    </div>
    <div class="page-header">
      <h1>Framework Explorer</h1>
      <div class="page-header-underline"></div>
    </div>
    <div class="summary-cards">
      <div class="summary-card active-framework" @click="filterByStatus('Active', 'framework')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-shield-alt"></i>
        </div>
        <div>Active Framework</div>
        <span class="summary-value">{{ summary.active_frameworks }}</span>
      </div>
      <div class="summary-card inactive-framework" @click="filterByStatus('Inactive', 'framework')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-shield"></i>
        </div>
        <div>Inactive Framework</div>
        <span class="summary-value">{{ summary.inactive_frameworks }}</span>
      </div>
      <div class="summary-card active-policy" @click="filterByStatus('Active', 'policy')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-file-circle-check"></i>
        </div>
        <div>Active Policy</div>
        <span class="summary-value">{{ summary.active_policies }}</span>
      </div>
      <div class="summary-card inactive-policy" @click="filterByStatus('Inactive', 'policy')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-file-circle-xmark"></i>
        </div>
        <div>Inactive Policy</div>
        <span class="summary-value">{{ summary.inactive_policies }}</span>
      </div>
    </div>
    <div class="top-controls">
      <div class="framework-dropdown-section">
        <CustomDropdown
          :config="frameworkDropdownConfig"
          v-model="selectedFrameworkId"
        />
      </div>
      <div class="internal-external-dropdown-section">
        <CustomDropdown
          :config="typeDropdownConfig"
          v-model="selectedInternalExternal"
        />
      </div>
      <div class="entity-dropdown-section">
        <CustomDropdown
          :config="entityDropdownConfig"
          v-model="selectedEntity"
        />
      </div>
      <div v-if="activeFilter" class="active-filter">
        <span>Filtered by: {{ activeFilter }}</span>
        <button class="clear-filter-btn" @click="clearFilter">Clear Filter</button>
      </div>
    </div>
    <div class="framework-card-grid">
      <div v-for="fw in filteredFrameworks" :key="fw.id" class="framework-card" @click="goToPolicies(fw.id)">
        <div class="framework-card-header">
          <div class="framework-title-section">
            <span class="framework-icon">
              <i class="fas fa-book"></i>
            </span>
            <span class="framework-card-title">{{ fw.name }}</span>
          </div>
        </div>
        <div class="framework-card-category">Category: {{ fw.category }}</div>
        <div class="framework-card-type" :class="{ 
          'type-internal': (fw.internalExternal || 'Internal') === 'Internal',
          'type-external': (fw.internalExternal || 'Internal') === 'External'
        }">
          Type: {{ fw.internalExternal || 'Internal' }}
        </div>
        <div class="framework-card-desc">{{ fw.description }}</div>
        <div class="framework-card-actions">
          <div class="action-buttons">
            <label class="switch" @click.stop>
              <input type="checkbox" :checked="fw.status === 'Active'" @change.stop="toggleStatus(fw)" />
              <span class="slider"></span>
            </label>
            <span class="switch-label" :class="fw.status === 'Active' ? 'active' : 'inactive'">{{ fw.status }}</span>
          </div>
          <span class="document-icon" @click.stop="showFrameworkDetails(fw.id)">
            <i class="fas fa-file-alt"></i>
          </span>
        </div>
      </div>
    </div>
 
    <!-- Framework Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-btn" @click="closeModal">&times;</button>
        <div class="modal-header">
          <h3>Framework Details</h3>
        </div>
        <div v-if="isLoadingDetails" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i> Loading details...
        </div>
        <div v-else-if="frameworkDetails" class="modal-body">
          <div class="framework-details">
            <div class="detail-row">
              <span class="detail-label">Framework Name:</span>
              <span class="detail-value">{{ frameworkDetails.FrameworkName }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Description:</span>
              <span class="detail-value">{{ frameworkDetails.FrameworkDescription }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Category:</span>
              <span class="detail-value">{{ frameworkDetails.Category }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Version:</span>
              <span class="detail-value">{{ frameworkDetails.CurrentVersion }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Status:</span>
              <span class="detail-value">{{ frameworkDetails.Status }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Active/Inactive:</span>
              <span class="detail-value">{{ frameworkDetails.ActiveInactive }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Identifier:</span>
              <span class="detail-value">{{ frameworkDetails.Identifier }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Effective Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.EffectiveDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Start Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.StartDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">End Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.EndDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Created By:</span>
              <span class="detail-value">{{ frameworkDetails.CreatedByName }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Created Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.CreatedByDate) }}</span>
            </div>
            <div class="detail-row" v-if="frameworkDetails.DocURL">
              <span class="detail-label">Documentation:</span>
              <a :href="frameworkDetails.DocURL" target="_blank" class="doc-link">View Documentation</a>
            </div>
          </div>
        </div>
        <div v-else class="modal-error">
          Failed to load framework details.
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>
 
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CustomDropdown from '@/components/CustomDropdown.vue'
 
const frameworks = ref([])
const selectedFrameworkId = ref('')
const selectedInternalExternal = ref('')
const selectedEntity = ref('')
const entities = ref([])
const router = useRouter()
const summary = ref({
  active_frameworks: 0,
  inactive_frameworks: 0,
  active_policies: 0,
  inactive_policies: 0
})
const isLoading = ref(false)
const statusFilter = ref(null)
const typeFilter = ref(null)
const activeFilter = computed(() => {
  const filters = []
  
  if (statusFilter.value && typeFilter.value) {
    filters.push(`${statusFilter.value} ${typeFilter.value}s`)
  }
  
  if (selectedInternalExternal.value) {
    filters.push(selectedInternalExternal.value)
  }
  
  if (selectedEntity.value) {
    const entityName = entities.value.find(e => e.id === selectedEntity.value)?.label || selectedEntity.value
    filters.push(entityName)
  }
  
  return filters.length > 0 ? filters.join(' & ') : null
})
 
// Modal and details states
const showModal = ref(false)
const isLoadingDetails = ref(false)
const frameworkDetails = ref(null)
 
// Add export controls above the framework grid
const selectedExportFormat = ref('');
const exportFrameworkPolicies = async () => {
  if (!selectedFrameworkId.value || !selectedExportFormat.value) {
    PopupService.warning('Please select a framework and format.', 'Missing Selection');
    return;
  }
  try {
    // Step 1: Request export and get file_url and file_name
    const res = await axios.post(`/api/frameworks/${selectedFrameworkId.value}/export/`, {
      format: selectedExportFormat.value
    });
    const { file_url, file_name } = res.data;
    if (!file_url || !file_name) {
      PopupService.error('Export failed: No file URL or name returned.', 'Export Error');
      return;
    }
 
    // Step 2: Download the file as a blob
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
      PopupService.success('Export completed successfully!', 'Export Success');
      console.error(downloadErr);
    }
  } catch (err) {
    PopupService.error('Export failed. Please try again.', 'Export Error');
    console.error(err);
  }
};
 
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
 
// Fetch frameworks from API
const fetchFrameworks = async () => {
  isLoading.value = true
  try {
    const params = {}
    if (selectedEntity.value) {
      params.entity = selectedEntity.value
    }
    
    const response = await axios.get('/api/framework-explorer/', { params })
    frameworks.value = response.data.frameworks
    summary.value = response.data.summary
  } catch (error) {
    console.error('Error fetching frameworks:', error)
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
 
// Show framework details
const showFrameworkDetails = async (frameworkId) => {
  frameworkDetails.value = null
  showModal.value = true
  isLoadingDetails.value = true
 
  try {
    const response = await axios.get(`/api/frameworks/${frameworkId}/details/`)
    frameworkDetails.value = response.data
  } catch (error) {
    console.error('Error fetching framework details:', error)
  } finally {
    isLoadingDetails.value = false
  }
}
 
// Close the modal
const closeModal = () => {
  showModal.value = false
}
 
// Filter frameworks by status
const filterByStatus = (status, type) => {
  // Check if we're clicking the same filter that's already active
  if (statusFilter.value === status && typeFilter.value === type) {
    // Clear the filter if it's already active
    clearFilter();
  } else {
    // Apply the new filter
    statusFilter.value = status;
    typeFilter.value = type;
  }
}
 
// Clear all filters
const clearFilter = () => {
  statusFilter.value = null
  typeFilter.value = null
  selectedInternalExternal.value = ''
  selectedEntity.value = ''
}
 
// Toggle framework status
const toggleStatus = async (fw) => {
  try {
    // Check if we're deactivating (Active -> Inactive)
    if (fw.status === 'Active') {
      // First fetch the list of available reviewers
      try {
        const reviewersResponse = await axios.get('/api/users-for-reviewer-selection/');
        const reviewers = reviewersResponse.data;
        
        if (reviewers.length === 0) {
          PopupService.warning('No reviewers available. Please contact an administrator.', 'No Reviewers');
          return;
        }
        
        // Create reviewer selection popup
        const reviewerOptions = reviewers.map(reviewer => ({
          value: reviewer.UserId,
          label: `${reviewer.UserName} (${reviewer.Email})`
        }));
        
        // Use popup service for reviewer selection and reason input
        PopupService.select(
          'Please select a reviewer for this framework deactivation request:',
          'Select Reviewer',
          reviewerOptions,
          async (selectedReviewerId) => {
            console.log('DEBUG: Selected reviewer ID:', selectedReviewerId, 'Type:', typeof selectedReviewerId);
            if (!selectedReviewerId) {
              PopupService.warning('Reviewer selection is required.', 'Missing Information');
              return;
            }
            
            // Now ask for the reason
            PopupService.comment(
              'Please provide a reason for deactivating this framework:',
              'Framework Deactivation',
              async (reason) => {
                console.log('DEBUG: Reason provided:', reason);
                if (!reason || reason.trim() === '') {
                  PopupService.warning('Deactivation reason is required.', 'Missing Information');
                  return;
                }
                
                try {
                  console.log('DEBUG: Sending API request with data:', {
                    reason: reason.trim(),
                    cascadeToApproved: true,
                    ReviewerId: selectedReviewerId,
                    UserId: 1
                  });
                  
                  // Call the API to request status change approval
                  const response = await axios.post(`/api/frameworks/${fw.id}/request-status-change/`, {
                    reason: reason.trim(),
                    cascadeToApproved: true,
                    ReviewerId: selectedReviewerId,
                    UserId: 1 // You might want to get this from user context
                  });
                  
                  console.log('DEBUG: API response:', response.data);
                  
                  // Show success message
                  PopupService.success('Framework deactivation request submitted. Awaiting approval.', 'Request Submitted');
                  
                  // Refresh data to reflect the new 'Under Review' status
                  await fetchFrameworks();
                } catch (error) {
                  console.error('Error submitting deactivation request:', error);
                  console.error('Error response:', error.response?.data);
                  PopupService.error('Failed to submit deactivation request. Please try again.', 'Request Failed');
                }
              }
            );
          }
        );
        
      } catch (error) {
        console.error('Error fetching reviewers:', error);
        PopupService.error('Failed to fetch reviewers. Please try again.', 'Error');
        return;
      }
    } else {
      // For activation (Inactive -> Active), use the direct toggle endpoint
      const response = await axios.post(`/api/frameworks/${fw.id}/toggle-status/`, {
        reason: 'Reactivating framework',
        cascadeToApproved: true
      });
     
      // Update local state
      fw.status = response.data.status || 'Active';
     
      // Show feedback to the user
      let message = `Framework status change request submitted.`;
     
      PopupService.success(message, 'Status Update');
     
      // Refresh summary counts
      await fetchFrameworks();
    }
  } catch (error) {
    console.error('Error toggling framework status:', error);
    PopupService.error('Failed to update framework status. Please try again.', 'Update Failed');
  }
}
 
const filteredFrameworks = computed(() => {
  let result = frameworks.value;
 
  // Apply framework ID filter if selected
  if (selectedFrameworkId.value) {
    result = result.filter(fw => fw.id === parseInt(selectedFrameworkId.value));
    return result;
  }
 
  // Apply Internal/External filter
  if (selectedInternalExternal.value) {
    result = result.filter(fw => fw.internalExternal === selectedInternalExternal.value);
  }

  // Entity filtering is handled by the backend API
  // The frameworks data is already filtered when selectedEntity changes
 
  // Apply status and type filters
  if (statusFilter.value && typeFilter.value) {
    if (typeFilter.value === 'framework') {
      // Filter frameworks by their status
      result = result.filter(fw => fw.status === statusFilter.value);
    } else if (typeFilter.value === 'policy') {
      // Filter frameworks that have active/inactive policies
      if (statusFilter.value === 'Active') {
        result = result.filter(fw => fw.active_policies_count > 0);
      } else {
        result = result.filter(fw => fw.inactive_policies_count > 0);
      }
    }
  }
 
  return result;
})
 
function goToPolicies(frameworkId) {
  const routeParams = { name: 'FrameworkPolicies', params: { frameworkId } }
  
  // If an entity filter is selected, pass it as a query parameter
  if (selectedEntity.value) {
    routeParams.query = { entity: selectedEntity.value }
  }
  
  router.push(routeParams)
}
 
// Watch for entity filter changes
watch(selectedEntity, () => {
  fetchFrameworks()
})

// Fetch frameworks on component mount
onMounted(() => {
  fetchEntities()
  
  // Check if there's an entity filter from the route query parameters
  const entityFromRoute = useRoute().query.entity
  if (entityFromRoute) {
    selectedEntity.value = entityFromRoute
  }
  
  fetchFrameworks() // Fetch frameworks after setting entity filter
})

// Dropdown configs
const frameworkDropdownConfig = computed(() => ({
  label: 'Framework',
  values: [
    { value: '', label: 'Select Framework' },
    ...frameworks.value.map(fw => ({ value: String(fw.id), label: fw.name }))
  ]
}))
const typeDropdownConfig = {
  label: 'Type',
  values: [
    { value: '', label: 'All Types' },
    { value: 'Internal', label: 'Internal' },
    { value: 'External', label: 'External' }
  ]
}
const entityDropdownConfig = computed(() => ({
  label: 'Entity',
  values: [
    { value: '', label: 'All Entities' },
    ...entities.value.map(entity => ({ value: String(entity.id), label: entity.label }))
  ]
}))
</script>
 
<style scoped>
.framework-explorer-container {
  padding: 24px 32px;
  margin-left: 280px;
  max-width: calc(100vw - 280px);
  width: 100%;
  box-sizing: border-box;
  position: relative;
  padding-top: 70px; /* Add space for export controls */
}
.page-header {
  margin-bottom: 18px;
  margin-top: 0;
}
.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  letter-spacing: -1px;
}
.page-header-underline {
  width: 75px;
  height: 5px;
  border-radius: 3px;
  background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
  margin-top: 0;
}
.export-controls {
  position: absolute;
  top: 20px;
  right: 32px;
  z-index: 10;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: auto;
  margin-bottom: 0;
}
.export-controls-inner {
  display: flex;
  gap: 8px;
  align-items: center;
}
.export-dropdown {
  min-width: 120px;
  height: 32px;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.85rem;
  padding: 0 10px;
  background: #fff;
  color: #222;
}
.export-controls button {
  padding: 6px 16px;
  border-radius: 8px;
  border: none;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  background: #4f6cff;
  color: #fff;
  transition: background 0.2s;
}
.export-controls button:disabled {
  background: #bfc8e6;
  cursor: not-allowed;
}
.summary-cards {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: nowrap;
  width: 100%;
  max-width: 100%;
}
.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f2f2f7;
  border-radius: 16px;
  padding: 20px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
  min-width: 180px;
  max-width: 200px;
  min-height: 140px;
  box-shadow: 0 2px 12px rgba(79,108,255,0.10);
  transition: box-shadow 0.18s, transform 0.18s;
  position: relative;
  cursor: pointer;
  flex: 1;
}
.summary-card.active-framework {
  background: linear-gradient(135deg, #e8f7ee 60%, #f2f2f7 100%);
}
.summary-card.inactive-framework {
  background: linear-gradient(135deg, #fbeaea 60%, #f2f2f7 100%);
}
.summary-card.active-policy {
  background: linear-gradient(135deg, #e6f7ff 60%, #f2f2f7 100%);
}
.summary-card.inactive-policy {
  background: linear-gradient(135deg, #fffbe6 60%, #f2f2f7 100%);
}
.summary-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  font-size: 1.4rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.active-framework .summary-icon-wrapper {
  background: #e8f7ee;
  color: #22a722;
}
.inactive-framework .summary-icon-wrapper {
  background: #fbeaea;
  color: #e53935;
}
.active-policy .summary-icon-wrapper {
  background: #e6f7ff;
  color: #4f6cff;
}
.inactive-policy .summary-icon-wrapper {
  background: #fff5e6;
  color: #f5a623;
}
.summary-card:hover .summary-icon-wrapper {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}
.summary-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(79,108,255,0.15);
}
.summary-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  margin-top: 10px;
  color: #222;
}
.top-controls {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 20px;
  margin-bottom: 16px;
  width: 100%;
  flex-wrap: wrap;
}
.framework-dropdown-section,
.internal-external-dropdown-section,
.entity-dropdown-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0;
}
.framework-dropdown,
.internal-external-dropdown,
.entity-dropdown {
  min-width: 140px;
  height: 32px;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.85rem;
  padding: 0 10px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
}
.framework-dropdown:hover,
.internal-external-dropdown:hover,
.entity-dropdown:hover {
  border-color: #4f6cff;
}
.framework-dropdown:focus,
.internal-external-dropdown:focus,
.entity-dropdown:focus {
  outline: none;
  border-color: #4f6cff;
  box-shadow: 0 0 0 3px rgba(79, 108, 255, 0.1);
}
.active-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f0f4ff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #4f6cff;
}
.clear-filter-btn {
  background: #4f6cff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
}
.clear-filter-btn:hover {
  background: #3a57e8;
}
.framework-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  width: 100%;
  margin-top: 20px;
}
.framework-card {
  background: #f7f7fa !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 14px rgba(79,108,255,0.08) !important;
  padding: 20px 18px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
  position: relative !important;
  font-size: 0.85rem !important;
  cursor: pointer !important;
  transition: box-shadow 0.18s, transform 0.18s !important;
  min-height: 180px !important;
}
.framework-card:hover {
  box-shadow: 0 8px 24px rgba(79,108,255,0.13) !important;
  transform: translateY(-2px) scale(1.025) !important;
}
.framework-card-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  width: 100% !important;
}
.framework-title-section {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}
.framework-icon {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 28px !important;
  height: 28px !important;
  background: #e8edfa !important;
  border-radius: 8px !important;
  color: #7c3aed !important;
  font-size: 0.9rem !important;
}
.framework-card-status {
  padding: 4px 10px !important;
  border-radius: 12px !important;
  font-size: 0.8rem !important;
  background: #f5f5f7 !important;
}
.framework-card-status.active {
  color: #22a722 !important;
  background: #e8f7ee !important;
}
.framework-card-status.inactive {
  color: #e53935 !important;
  background: #fbeaea !important;
}
.framework-card-category {
  font-size: 0.8rem !important;
  color: #7c3aed !important;
  font-weight: 600 !important;
  background: #e8edfa !important;
  border-radius: 8px !important;
  padding: 2px 6px !important;
  width: fit-content !important;
}
.framework-card-type {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 2px 6px !important;
  width: fit-content !important;
  margin-top: 4px !important;
}
.framework-card-type.type-internal {
  color: #059669 !important;
  background: #d1fae5 !important;
}
.framework-card-type.type-external {
  color: #dc2626 !important;
  background: #fecaca !important;
}
.framework-card-desc {
  font-size: 0.85rem !important;
  line-height: 1.4 !important;
  margin-top: 6px !important;
  color: #444 !important;
  font-weight: 400 !important;
  flex-grow: 1;
}
.framework-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}
.action-buttons {
  display: flex;
  gap: 6px;
}
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 26px;
  margin-right: 6px;
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
  border-radius: 26px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
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
  -webkit-transform: translateX(18px);
  -ms-transform: translateX(18px);
  transform: translateX(18px);
}
.switch-label {
  font-weight: 600;
  color: #4f6cff;
  min-width: 50px;
  display: inline-block;
  text-align: left;
  font-size: 0.8rem;
}
.switch-label.active {
  color: #22a722;
}
.switch-label.inactive {
  color: #e53935;
}
.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
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
 
/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  position: relative;
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
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
}
.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.6rem;
  font-weight: 700;
}
.modal-close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 2.2rem;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
  background: transparent;
  border: none;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.modal-close-btn:hover {
  color: #e53935;
}
.modal-body {
  padding: 25px 30px;
}
.modal-loading, .modal-error {
  padding: 30px;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
}
.detail-row {
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
}
.detail-label {
  font-weight: 600;
  width: 160px;
  color: #444;
  font-size: 1rem;
  position: relative;
  padding-right: 12px;
}
.detail-label::after {
  content: ":";
  position: absolute;
  right: 4px;
}
.detail-value {
  flex: 1;
  min-width: 200px;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}
.doc-link {
  color: #4f6cff;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  padding: 6px 12px;
  background: #f0f4ff;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}
.doc-link:hover {
  text-decoration: none;
  background: #e0e7ff;
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(79,108,255,0.15);
}
.framework-details {
  margin-top: 10px;
  background: #fcfcff;
  border-radius: 8px;
  padding: 15px;
}
</style>