<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Status Change Approval Tasks</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="fetchRequests"><i class="fas fa-sync-alt"></i></button>
      </div>
    </div>

    <!-- Reviewer Filter Section -->
    <div class="filter-section">
      <div class="filter-group">
        <CustomDropdown
          :config="reviewerDropdownConfig"
          v-model="selectedReviewerId"
          @change="filterByReviewer"
        />
      </div>
    </div>

    <!-- Status Change Requests List -->
    <div v-if="isLoading" class="loading-indicator">
      <i class="fas fa-spinner fa-spin"></i> Loading status change requests...
    </div>
    
    <div v-else-if="requests.length === 0" class="no-requests">
      <p>No status change requests found.</p>
    </div>
    
    <div v-else>
      <!-- Collapsible Table for Pending Approval Tasks -->
      <CollapsibleTable
        v-if="pendingRequests.length > 0"
        :sectionConfig="{ name: 'Pending', statusClass: 'pending', tasks: pendingTableRows }"
        :tableHeaders="pendingTableHeaders"
        :isExpanded="true"
        @taskClick="openRequestDetails"
      />
      
      <!-- Framework Grid for non-pending requests -->
      <div class="framework-grid">
        <div v-for="request in requests.filter(r => r.Status !== 'Pending Approval')" :key="request.ApprovalId" class="framework-card">
          <div class="framework-header">
            <i :class="request.ItemType === 'policy' ? 'fas fa-file-alt' : 'fas fa-book'"></i>
            <span>{{ request.FrameworkName || request.PolicyName }}</span>
          </div>
          
          <div class="category-tag">
            {{ request.ItemType === 'policy' ? 'Department' : 'Category' }}: 
            {{ request.Category || request.Department }}
          </div>
          
          <div class="framework-description">{{ request.Reason }}</div>
          
          <div class="framework-footer">
            <div class="status-toggle">
              <input 
                type="checkbox" 
                :checked="request.Status === 'Approved'" 
                disabled
              />
              <span class="switch-label" :class="{
                'active': request.Status === 'Rejected' || request.Status === 'Pending Approval',
                'inactive': request.Status === 'Approved'
              }">
                {{ request.Status === 'Approved' ? 'Inactive' : 
                   request.Status === 'Rejected' ? 'Active' : 'Pending' }}
              </span>
            </div>
            
            <div class="actions">
              <button class="view-btn" @click="openRequestDetails(request)">
                <i class="fas fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Change Request Details Modal -->
    <div v-if="showDetails && selectedRequest" class="framework-details-modal">
      <div class="framework-details-content">
        <h3>
          <span class="detail-type-indicator">
            {{ selectedRequest.ItemType === 'policy' ? 'POLICY' : 'FRAMEWORK' }} STATUS CHANGE REQUEST
          </span> 
          Details: {{ selectedRequest.FrameworkName || selectedRequest.PolicyName }}
          <span class="version-pill">Version: {{ selectedRequest.Version }}</span>
        </h3>
        
        <button class="close-btn" @click="closeRequestDetails">Close</button>
        
        <!-- Status Change Approval Section -->
        <div class="framework-approval-section">
          <h4>Status Change Approval</h4>
          
          <!-- Status Change Request indicator -->
          <div class="framework-status-indicator">
            <span class="status-label">Request Type:</span>
            <span class="status-value status-inactive">
              Change Status to Inactive
            </span>
          </div>
          
          <div class="approval-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedRequest.Status === 'Approved',
              'status-inactive': selectedRequest.Status === 'Rejected',
              'status-pending': selectedRequest.Status === 'Pending Approval'
            }">
              {{ selectedRequest.Status }}
            </span>
          </div>
          
          <div v-if="selectedRequest.Status === 'Pending Approval'" class="framework-actions">
            <button class="approve-btn" @click="approveRequest(selectedRequest)">
              <i class="fas fa-check"></i> Approve (Make Inactive)
            </button>
            <button class="reject-btn" @click="rejectRequest(selectedRequest)">
              <i class="fas fa-times"></i> Reject (Keep Active)
            </button>
          </div>
          
          <div v-else class="approval-result">
            <div v-if="selectedRequest.Remarks" class="approval-remarks">
              <strong>Remarks:</strong> {{ selectedRequest.Remarks }}
            </div>
            <div v-if="selectedRequest.ApprovedDate" class="approval-date">
              <strong>Date:</strong> {{ formatDate(selectedRequest.ApprovedDate) }}
            </div>
          </div>
        </div>
        
        <!-- Display request details -->
        <div class="request-details">
          <div class="framework-detail-row">
            <strong>{{ selectedRequest.ItemType === 'policy' ? 'Policy' : 'Framework' }} Name:</strong> 
            <span>{{ selectedRequest.FrameworkName || selectedRequest.PolicyName }}</span>
          </div>
          <div class="framework-detail-row">
            <strong>{{ selectedRequest.ItemType === 'policy' ? 'Department' : 'Category' }}:</strong> 
            <span>{{ selectedRequest.Category || selectedRequest.Department }}</span>
          </div>
          <div class="framework-detail-row">
            <strong>Request Date:</strong> <span>{{ formatDate(selectedRequest.RequestDate) }}</span>
          </div>
          <div class="framework-detail-row">
            <strong>Current Status:</strong> 
            <span :class="{
              'status-active': selectedRequest.Status === 'Rejected' || selectedRequest.Status === 'Pending Approval',
              'status-inactive': selectedRequest.Status === 'Approved'
            }">
              {{ selectedRequest.Status === 'Approved' ? 'Inactive' : 'Active' }}
            </span>
          </div>
          <div class="framework-detail-row">
            <strong>Reason for Change:</strong> <span>{{ selectedRequest.Reason }}</span>
          </div>
          <div class="framework-detail-row" v-if="selectedRequest.ItemType === 'framework'">
            <strong>Cascade to Policies:</strong> 
            <span :class="{'cascade-yes': selectedRequest.CascadeToApproved, 'cascade-no': !selectedRequest.CascadeToApproved}">
              {{ selectedRequest.CascadeToApproved ? 'Yes' : 'No' }}
              <span class="policy-count" v-if="selectedRequest.PolicyCount > 0">
                ({{ selectedRequest.PolicyCount }} policies will be affected)
              </span>
            </span>
          </div>
          <div class="framework-detail-row" v-if="selectedRequest.ItemType === 'policy'">
            <strong>Cascade to Subpolicies:</strong> 
            <span :class="{'cascade-yes': selectedRequest.CascadeToSubpolicies, 'cascade-no': !selectedRequest.CascadeToSubpolicies}">
              {{ selectedRequest.CascadeToSubpolicies ? 'Yes' : 'No' }}
              <span class="policy-count" v-if="selectedRequest.SubpolicyCount > 0">
                ({{ selectedRequest.SubpolicyCount }} subpolicies will be affected)
              </span>
            </span>
          </div>
        </div>

        <!-- Affected Policies/Subpolicies Section -->
        <div v-if="(selectedRequest.AffectedPolicies && selectedRequest.AffectedPolicies.length > 0) || 
                   (selectedRequest.AffectedSubpolicies && selectedRequest.AffectedSubpolicies.length > 0)" 
             class="affected-policies-section">
          <h4>{{ selectedRequest.ItemType === 'policy' ? 'Affected Subpolicies' : 'Affected Policies' }}</h4>
          <p class="section-description">
            <span v-if="selectedRequest.Status === 'Approved'">
              The following {{ selectedRequest.ItemType === 'policy' ? 'subpolicies' : 'policies' }} have been set to Inactive:
            </span>
            <span v-else>
              The following {{ selectedRequest.ItemType === 'policy' ? 'subpolicies' : 'policies' }} will become inactive if this request is approved:
            </span>
          </p>
          
          <div class="policies-list">
            <!-- Framework Policies -->
            <template v-if="selectedRequest.ItemType === 'framework'">
              <div v-for="policy in selectedRequest.AffectedPolicies" 
                   :key="policy.PolicyId" 
                   class="policy-item">
                <div class="policy-header">
                  <span class="policy-name">{{ policy.PolicyName }}</span>
                  <span class="policy-status" :class="{
                    'active': selectedRequest.Status !== 'Approved',
                    'inactive': selectedRequest.Status === 'Approved'
                  }">
                    {{ selectedRequest.Status === 'Approved' ? 'Inactive' : 'Active' }}
                  </span>
                </div>
                <div class="policy-details">
                  <div class="policy-detail-item" v-if="policy.Identifier">
                    <strong>Identifier:</strong> {{ policy.Identifier }}
                  </div>
                  <div class="policy-detail-item" v-if="policy.Department">
                    <strong>Department:</strong> {{ policy.Department }}
                  </div>
                  <div class="policy-detail-item" v-if="policy.Description">
                    <strong>Description:</strong> {{ policy.Description }}
                  </div>
                </div>
              </div>
            </template>
            
            <!-- Policy Subpolicies -->
            <template v-if="selectedRequest.ItemType === 'policy'">
              <div v-for="subpolicy in selectedRequest.AffectedSubpolicies" 
                   :key="subpolicy.SubPolicyId" 
                   class="policy-item">
                <div class="policy-header">
                  <span class="policy-name">{{ subpolicy.SubPolicyName }}</span>
                  <span class="policy-status" :class="{
                    'active': selectedRequest.Status !== 'Approved',
                    'inactive': selectedRequest.Status === 'Approved'
                  }">
                    {{ selectedRequest.Status === 'Approved' ? 'Inactive' : 'Active' }}
                  </span>
                </div>
                <div class="policy-details">
                  <div class="policy-detail-item" v-if="subpolicy.Identifier">
                    <strong>Identifier:</strong> {{ subpolicy.Identifier }}
                  </div>
                  <div class="policy-detail-item" v-if="subpolicy.Control">
                    <strong>Control:</strong> {{ subpolicy.Control }}
                  </div>
                  <div class="policy-detail-item" v-if="subpolicy.Description">
                    <strong>Description:</strong> {{ subpolicy.Description }}
                  </div>
                </div>
              </div>
            </template>
          </div>
          
          <div v-if="selectedRequest.Status !== 'Approved'" class="affected-policies-summary">
            <div class="summary-warning">
              <i class="fas fa-exclamation-triangle"></i>
              <span>All of these policies will be changed to <strong>Inactive</strong> if the request is approved.</span>
            </div>
          </div>
        </div>

        <div v-else-if="selectedRequest.CascadeToApproved" class="no-policies-message">
          <i class="fas fa-info-circle"></i>
          <span>No active policies found that would be affected by this change.</span>
        </div>

        <div class="approval-implications" v-if="selectedRequest.Status === 'Pending Approval'">
          <h4>Approval Implications</h4>
          <div class="implication-item warning">
            <i class="fas fa-exclamation-triangle"></i>
            <div class="implication-text">
              <strong>If approved:</strong> The framework will become <span class="status-inactive">Inactive</span>.
              <span v-if="selectedRequest.CascadeToApproved && selectedRequest.PolicyCount > 0">
                Additionally, <strong>{{ selectedRequest.PolicyCount }} approved policies</strong> will also become inactive.
              </span>
            </div>
          </div>
          <div class="implication-item info">
            <i class="fas fa-info-circle"></i>
            <div class="implication-text">
              <strong>If rejected:</strong> The framework will remain <span class="status-approved">Active</span> and no changes will be made.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CollapsibleTable from '@/components/CollapsibleTable.vue'
import CustomDropdown from '@/components/CustomDropdown.vue'

const requests = ref([])
const isLoading = ref(false)
const showDetails = ref(false)
const selectedRequest = ref(null)
const selectedReviewerId = ref('')
const reviewers = ref([])

// Dropdown configuration for reviewer filter
const reviewerDropdownConfig = computed(() => ({
  label: 'Filter by Reviewer',
  name: 'reviewer',
  values: [
    { value: '', label: 'All Reviewers' },
    ...reviewers.value.map(reviewer => ({
      value: reviewer.UserId,
      label: `${reviewer.UserName} (${reviewer.Email})`
    }))
  ],
  defaultValue: 'All Reviewers'
}))

// Computed property for pending requests
const pendingRequests = computed(() => {
  return requests.value.filter(req => req.Status === 'Pending Approval')
})

// Table headers for pending requests
const pendingTableHeaders = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'category', label: 'Category/Department' },
  { key: 'date', label: 'Request Date' },
  { key: 'reason', label: 'Reason' },
  { key: 'actions', label: 'Actions' }
]

// Table rows for pending requests
const pendingTableRows = computed(() =>
  pendingRequests.value.map(req => ({
    ...req,
    name: req.FrameworkName || req.PolicyName,
    type: req.ItemType === 'policy' ? 'POLICY STATUS CHANGE' : 'FRAMEWORK STATUS CHANGE',
    category: req.Category || req.Department,
    date: formatDate(req.RequestDate),
    reason: req.Reason
  }))
)

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

// Process frameworks and ensure consistent status
const processFrameworks = (frameworks) => {
  // Create a map of framework status by framework name to ensure consistency
  const frameworkStatusMap = {}
  
  // First pass: determine the status of each framework
  frameworks.forEach(framework => {
    if (framework.ApprovedNot === true) {
      frameworkStatusMap[framework.FrameworkName] = 'Approved' // Will display as Inactive
      framework.Status = 'Approved'
    } else if (framework.ApprovedNot === false) {
      frameworkStatusMap[framework.FrameworkName] = 'Rejected' // Will display as Active
      framework.Status = 'Rejected'
    } else {
      frameworkStatusMap[framework.FrameworkName] = 'Pending Approval'
      framework.Status = 'Pending Approval'
    }
  })
  
  // Second pass: ensure all instances of the same framework have the same status
  frameworks.forEach(framework => {
    // Set the status based on the map to ensure consistency
    framework.Status = frameworkStatusMap[framework.FrameworkName]
    
    // Update affected policies status to match framework status
    if (framework.AffectedPolicies) {
      framework.AffectedPolicies.forEach(policy => {
        if (framework.Status === 'Approved') {
          policy.ActiveInactive = 'Inactive'
        } else if (framework.Status === 'Rejected') {
          policy.ActiveInactive = 'Active'
        }
      })
    }
  })
  
  return frameworks
}

// Fetch status change requests
const fetchRequests = async () => {
  isLoading.value = true
  try {
    const [frameworkResponse, policyResponse] = await Promise.all([
      axios.get('/api/framework-status-change-requests/'),
      axios.get('/api/policy-status-change-requests/')
    ])
    
    // Process all frameworks to ensure consistent status
    const frameworkRequests = processFrameworks(frameworkResponse.data)
    
    // Process policy requests and add type indicator
    const policyRequests = policyResponse.data.map(request => ({
      ...request,
      RequestType: 'Policy Status Change',
      ItemType: 'policy'
    }))
    
    // Combine and sort by request date (newest first)
    const allRequests = [...frameworkRequests, ...policyRequests]
    allRequests.forEach(request => {
      if (!request.ItemType) {
        request.ItemType = 'framework'
      }
    })
    
    requests.value = allRequests.sort((a, b) => {
      const dateA = new Date(a.RequestDate || 0)
      const dateB = new Date(b.RequestDate || 0)
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('Error fetching status change requests:', error)
  } finally {
    isLoading.value = false
  }
}

// Open request details modal
const openRequestDetails = (request) => {
  selectedRequest.value = request
  showDetails.value = true
}

// Close request details modal
const closeRequestDetails = () => {
  selectedRequest.value = null
  showDetails.value = false
}

// Approve status change request
const approveRequest = async (request) => {
  const itemName = request.FrameworkName || request.PolicyName
  const itemType = request.ItemType === 'policy' ? 'policy' : 'framework'
  const cascadeMessage = request.ItemType === 'policy' 
    ? (request.CascadeToSubpolicies ? ' This will also make all subpolicies inactive.' : '')
    : (request.CascadeToApproved ? ' This will also make all approved policies inactive.' : '')
  
  // Use PopupService.confirm with callbacks
  PopupService.confirm(
    `Are you sure you want to approve changing the status of "${itemName}" to Inactive?${cascadeMessage}`,
    'Confirm Approval',
    async () => {
      // User confirmed - now ask for remarks
      PopupService.comment(
        'Enter any remarks (optional):',
        'Approval Remarks',
        async (remarks) => {
          try {
            const endpoint = request.ItemType === 'policy' 
              ? `/api/policy-approvals/${request.ApprovalId}/approve-status-change/`
              : `/api/framework-approvals/${request.ApprovalId}/approve-status-change/`
            
            await axios.post(endpoint, {
              approved: true,
              remarks: remarks || 'Status change approved'
            })
            
            const affectedCount = request.ItemType === 'policy' ? request.SubpolicyCount : request.PolicyCount
            const affectedType = request.ItemType === 'policy' ? 'subpolicies' : 'policies'
            
            PopupService.success(
              `${itemType.charAt(0).toUpperCase() + itemType.slice(1)} "${itemName}" has been set to Inactive.${affectedCount > 0 ? ` ${affectedCount} ${affectedType} were also made inactive.` : ''}`,
              'Status Changed'
            )
            
            // Close modal and refresh the list
            closeRequestDetails()
            await fetchRequests()
          } catch (error) {
            console.error('Error approving status change request:', error)
            PopupService.error('Failed to approve status change request. Please try again.', 'Approval Failed')
          }
        }
      )
    }
  )
}

// Reject status change request
const rejectRequest = async (request) => {
  const itemName = request.FrameworkName || request.PolicyName
  const itemType = request.ItemType === 'policy' ? 'policy' : 'framework'
  
  PopupService.confirm(
    `Are you sure you want to reject the status change request for "${itemName}"? The ${itemType} will remain Active.`,
    'Confirm Rejection',
    async () => {
      // User confirmed - now ask for rejection reason
      PopupService.comment(
        'Enter rejection reason (optional):',
        'Rejection Reason',
        async (remarks) => {
          try {
            const endpoint = request.ItemType === 'policy' 
              ? `/api/policy-approvals/${request.ApprovalId}/approve-status-change/`
              : `/api/framework-approvals/${request.ApprovalId}/approve-status-change/`
            
            await axios.post(endpoint, {
              approved: false,
              remarks: remarks || 'Status change rejected'
            })
            
            PopupService.success(
              `Status change request for "${itemName}" has been rejected. The ${itemType} remains Active.`,
              'Request Rejected'
            )
            
            // Close modal and refresh the list
            closeRequestDetails()
            await fetchRequests()
          } catch (error) {
            console.error('Error rejecting status change request:', error)
            PopupService.error('Failed to reject status change request. Please try again.', 'Rejection Failed')
          }
        }
      )
    }
  )
}

// Fetch requests on component mount
onMounted(() => {
  fetchRequests()
  fetchReviewers()
})

// Fetch reviewers for dropdown
const fetchReviewers = async () => {
  try {
    const response = await axios.get('/api/users-for-reviewer-selection/')
    reviewers.value = response.data
  } catch (error) {
    console.error('Error fetching reviewers:', error)
  }
}

// Filter requests by reviewer
const filterByReviewer = async (selectedOption) => {
  selectedReviewerId.value = selectedOption.value
  isLoading.value = true
  try {
    let frameworkResponse, policyResponse
    
    if (selectedReviewerId.value) {
      // Fetch requests filtered by reviewer
      frameworkResponse = await axios.get(`/api/status-change-requests-by-reviewer/${selectedReviewerId.value}/`)
      policyResponse = await axios.get(`/api/policy-status-change-requests-by-reviewer/${selectedReviewerId.value}/`)
    } else {
      // Fetch all requests
      frameworkResponse = await axios.get('/api/framework-status-change-requests/')
      policyResponse = await axios.get('/api/policy-status-change-requests/')
    }
    
    // Process all frameworks to ensure consistent status
    const frameworkRequests = processFrameworks(frameworkResponse.data)
    
    // Process policy requests and add type indicator
    const policyRequests = policyResponse.data.map(request => ({
      ...request,
      RequestType: 'Policy Status Change',
      ItemType: 'policy'
    }))
    
    // No need for additional filtering since the API already handles it
    const filteredPolicyRequests = policyRequests
    
    // Combine and sort by request date (newest first)
    const allRequests = [...frameworkRequests, ...filteredPolicyRequests]
    allRequests.forEach(request => {
      if (!request.ItemType) {
        request.ItemType = 'framework'
      }
    })
    
    requests.value = allRequests.sort((a, b) => {
      const dateA = new Date(a.RequestDate || 0)
      const dateB = new Date(b.RequestDate || 0)
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('Error filtering requests by reviewer:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 32px 40px;
  margin-left: 200px;
  max-width: calc(100vw - 240px);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-heading {
  font-size: 1.8rem;
  color: #2c3e50;
  font-weight: 700;
  margin: 0;
}

.dashboard-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background-color: #f5f6fa;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #4f6cff;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #e8edfa;
  transform: translateY(-2px);
}

.performance-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
}

.summary-card {
  background: #f5f6fa;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 220px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.summary-card.growth {
  background: linear-gradient(135deg, #e3f0ff 0%, #f5f6fa 100%);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #4f6cff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-label {
  color: #666;
  font-size: 0.95rem;
}

.summary-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2c3e50;
}

.loading-indicator, .no-requests {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #666;
  font-size: 1.1rem;
}

.loading-indicator i {
  margin-right: 10px;
  color: #4f6cff;
}

/* Status Tasks Section */
.section-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 32px;
}

.section-title {
  margin-top: 0;
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 1.2rem;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.status-tasks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-task-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s ease;
}

.status-task-item:last-child {
  border-bottom: none;
}

.status-task-item:hover {
  background: #f9faff;
}

.task-name {
  flex: 1;
  color: #4f6cff;
  font-weight: 500;
}

.task-type {
  padding: 4px 10px;
  border-radius: 12px;
  background-color: #ffebee;
  color: #e53935;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0 16px;
}

.task-date {
  color: #666;
  font-size: 0.9rem;
  margin: 0 16px;
}

.task-category {
  font-size: 0.9rem;
  color: #444;
  background: #f5f6fa;
  padding: 4px 10px;
  border-radius: 4px;
  margin-right: 16px;
}

.task-status {
  font-size: 0.85rem;
  font-weight: 600;
}

.task-status.pending {
  color: #f5a623;
}

.task-status.approved {
  color: #22a722;
}

.task-status.rejected {
  color: #e53935;
}

/* Framework Grid */
.framework-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.framework-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.framework-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.framework-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.framework-header i {
  color: #4f6cff;
  font-size: 1.2rem;
}

.framework-header span {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-tag {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 0.8rem;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  color: #666;
}

.framework-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 16px;
  flex-grow: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.framework-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.status-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-toggle input[type="checkbox"] {
  appearance: none;
  width: 40px;
  height: 22px;
  background-color: #e0e0e0;
  border-radius: 11px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s;
}

.status-toggle input[type="checkbox"]:checked {
  background-color: #4f6cff;
}

.status-toggle input[type="checkbox"]::before {
  content: "";
  position: absolute;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: white;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.status-toggle input[type="checkbox"]:checked::before {
  transform: translateX(18px);
}

.switch-label {
  font-size: 0.9rem;
  font-weight: 600;
}

.switch-label.active {
  color: #22a722;
}

.switch-label.inactive {
  color: #e53935;
}

.switch-label.pending {
  color: #f5a623;
}

.status-active {
  color: #22a722;
}

.status-inactive {
  color: #e53935;
}

.actions {
  display: flex;
  gap: 8px;
}

.view-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f5f6fa;
  border: none;
  color: #4f6cff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background-color: #4f6cff;
  color: white;
}

/* Modal Styles */
.framework-details-modal {
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

.framework-details-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
}

.framework-details-content h3 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-type-indicator {
  font-size: 0.9rem;
  padding: 4px 10px;
  border-radius: 8px;
  background: #ffebee;
  color: #e53935;
  font-weight: 600;
}

.version-pill {
  font-size: 0.85rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f0f0;
  color: #666;
  margin-left: auto;
}

.close-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #e53935;
}

.framework-approval-section {
  background: #f9faff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 24px;
}

.framework-approval-section h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #4f6cff;
}

.framework-status-indicator, .approval-status-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-label {
  font-weight: 600;
  color: #444;
}

.status-value {
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-approved {
  background: #e8f7ee;
  color: #22a722;
}

.status-inactive {
  background: #ffebee;
  color: #e53935;
}

.status-pending {
  background: #fff5e6;
  color: #f5a623;
}

.framework-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.approve-btn, .reject-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.approve-btn {
  background: #22a722;
  color: white;
}

.approve-btn:hover {
  background: #1b8c1b;
  transform: translateY(-2px);
}

.reject-btn {
  background: #e53935;
  color: white;
}

.reject-btn:hover {
  background: #c62828;
  transform: translateY(-2px);
}

.approval-result {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
}

.approval-remarks, .approval-date {
  margin-bottom: 8px;
}

.approval-remarks strong, .approval-date strong {
  color: #444;
}

.request-details {
  margin-bottom: 24px;
}

.framework-detail-row {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
}

.framework-detail-row:last-child {
  border-bottom: none;
}

.framework-detail-row strong {
  width: 180px;
  color: #444;
}

.cascade-yes {
  color: #22a722;
  font-weight: 600;
}

.cascade-no {
  color: #e53935;
  font-weight: 600;
}

.policy-count {
  color: #666;
  font-size: 0.85rem;
  margin-left: 6px;
  font-weight: normal;
}

.approval-implications {
  background: #f9faff;
  border-radius: 10px;
  padding: 20px;
}

.approval-implications h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #4f6cff;
}

.implication-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
  align-items: flex-start;
}

.implication-item:last-child {
  margin-bottom: 0;
}

.implication-item.warning {
  background: #fff5e6;
}

.implication-item.info {
  background: #e3f0ff;
}

.implication-item i {
  font-size: 1.2rem;
}

.implication-item.warning i {
  color: #f5a623;
}

.implication-item.info i {
  color: #4f6cff;
}

.implication-text {
  flex: 1;
}

.affected-policies-section {
  background: #f9faff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 24px;
}

.affected-policies-section h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #4f6cff;
  font-size: 1.1rem;
}

.section-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.policies-list {
  margin-bottom: 16px;
}

.policy-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.policy-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
}

.policy-name {
  font-weight: 600;
  color: #4f6cff;
  font-size: 1rem;
}

.policy-status {
  font-size: 0.85rem;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
}

.policy-status.active {
  background-color: #e8f7ee;
  color: #22a722;
}

.policy-status.inactive {
  background-color: #ffebee;
  color: #e53935;
}

.policy-details {
  margin-left: 0;
}

.policy-detail-item {
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.policy-detail-item strong {
  font-weight: 600;
  color: #444;
  display: inline-block;
  width: auto;
  margin-right: 8px;
}

.affected-policies-summary {
  background: #fff5e6;
  border-radius: 10px;
  padding: 16px;
  margin-top: 16px;
}

.summary-warning {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f5a623;
}

.summary-warning i {
  font-size: 1.2rem;
}

.no-policies-message {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  background: #e3f0ff;
  border-radius: 10px;
  padding: 16px;
  color: #4f6cff;
}

/* Filter Section Styles */
.filter-section {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
 
}

/* Custom width for the dropdown filter */
.filter-group :deep(.filter-btn) {
  min-width: 250px !important;
  max-width: 300px !important;
}

.filter-group :deep(.dropdown-menu) {
  min-width: 250px !important;
  max-width: 300px !important;
}

/* Remove the old filter styles since CustomDropdown handles its own styling */
.filter-group label {
  display: none; /* Hide the old label since CustomDropdown has its own */
}

.filter-dropdown {
  display: none; /* Hide the old dropdown since we're using CustomDropdown */
}
</style> 