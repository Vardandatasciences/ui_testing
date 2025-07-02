<template>
  <div class="dashboard-container">
    <!-- Only show summary and list if not viewing details -->
    <template v-if="!showDetails || !selectedApproval">
      <div class="dashboard-header">
        <h2 class="dashboard-heading">Compliance Approver</h2>
        <div class="dashboard-actions">
          <button class="action-btn" @click="refreshData" :disabled="isLoading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
          </button>
          <button class="action-btn"><i class="fas fa-download"></i></button>
        </div>
      </div>
      <!-- Error message -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="refreshData" class="retry-btn">Retry</button>
      </div>
      <!-- Performance Summary Cards -->
      <div class="performance-summary">
        <div class="summary-card growth">
          <div class="summary-icon"><i class="fas fa-user-check"></i></div>
          <div class="summary-content">
            <div class="summary-label">Pending Approvals</div>
            <div class="summary-value">{{ pendingApprovalsCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon"><i class="fas fa-check-circle"></i></div>
          <div class="summary-content">
            <div class="summary-label">Approved</div>
            <div class="summary-value">{{ approvedApprovalsCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon"><i class="fas fa-times-circle"></i></div>
          <div class="summary-content">
            <div class="summary-label">Rejected</div>
            <div class="summary-value">{{ rejectedApprovalsCount }}</div>
          </div>
        </div>
      </div>
      <!-- Loading state -->
      <div v-if="isLoading && !approvals.length" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i> Loading approvals...
      </div>
      <!-- No data state -->
      <div v-else-if="!isLoading && complianceApprovals.length === 0" class="no-data-state">
        <i class="fas fa-inbox"></i>
        <p>No pending approvals found.</p>
        <small>Any compliance items with "Under Review" status will appear here.</small>
      </div>
      <!-- Compliance Approvals List -->
      <div>
        <CollapsibleTable
          v-for="(tasks, status) in groupedApprovals"
          :key="status"
          :sectionConfig="{
            name: status,
            statusClass: status.toLowerCase().replace(' ', '-'),
            tasks: tasks.map(mapApprovalToRow)
          }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="collapsibleStates[status]"
          @toggle="toggleSection(status)"
          @taskClick="handleApprovalAction"
        />
      </div>
      <!-- Recently Approved Compliances -->
      <div v-if="approvedComplianceItems.length > 0">
        <CollapsibleTable
          :sectionConfig="{
            name: 'Recently Approved',
            statusClass: 'approved',
            tasks: approvedComplianceItems.map(mapApprovalToRow)
          }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="collapsibleStates['Recently Approved']"
          @toggle="toggleSection('Recently Approved')"
          @taskClick="handleApprovalAction"
        />
      </div>
      <!-- Rejected Compliances List -->
      <div v-if="rejectedCompliances.length">
        <CollapsibleTable
          :sectionConfig="{
            name: 'Rejected',
            statusClass: 'rejected',
            tasks: rejectedCompliances.map(mapRejectedToRow)
          }"
          :tableHeaders="rejectedTableHeaders"
          :isExpanded="collapsibleStates['Rejected']"
          @toggle="toggleSection('Rejected')"
          @taskClick="handleRejectedAction"
        />
      </div>
      <!-- Edit Modal for Rejected Compliance -->
      <div v-if="showEditComplianceModal && editingCompliance" class="edit-policy-modal">
        <div class="edit-policy-content">
          <h3>Edit & Resubmit Compliance: {{ editingCompliance.Identifier }}</h3>
          <button class="close-btn" @click="closeEditComplianceModal">Close</button>
          <!-- Compliance fields -->
          <div>
            <label>Description:</label>
            <input v-model="editingCompliance.ExtractedData.ComplianceItemDescription" />
          </div>
          <div>
            <label>Criticality:</label>
            <select v-model="editingCompliance.ExtractedData.Criticality">
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>
          <div>
            <label>Severity Rating:</label>
            <input v-model="editingCompliance.ExtractedData.Impact" />
          </div>
          <div>
            <label>Probability:</label>
            <input v-model="editingCompliance.ExtractedData.Probability" />
          </div>
          <div>
            <label>Mitigation:</label>
            <textarea v-model="editingCompliance.ExtractedData.mitigation"></textarea>
          </div>
          <!-- Show rejection reason -->
          <div>
            <label>Rejection Reason:</label>
            <div class="rejection-reason">{{ editingCompliance.ExtractedData.compliance_approval?.remarks }}</div>
          </div>
          <button class="resubmit-btn" @click="resubmitCompliance(editingCompliance)">Resubmit for Review</button>
        </div>
      </div>
      <!-- Add PopupModal component -->
      <PopupModal />
    </template>
    <!-- Details Section (Full Page Section) -->
    <!-- Enhanced Details Section Template -->
<template v-else>
  <div class="compliance-details-section">
    <!-- Header Section with Gradient Background -->
    <div class="compliance-details-header">
      <button class="back-btn" @click="closeApprovalDetails">
        <i class="fas fa-arrow-left"></i>
        <span>Back to Dashboard</span>
      </button>
      
      <h3>
        <span class="detail-type-indicator">Compliance</span>
        <span v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'">
          Deactivation Request: {{ selectedApproval.Identifier }}
        </span>
        <span v-else>
          Details: {{ selectedApproval.Identifier }}
        </span>
      </h3>
    </div>

    <!-- Main Content Area -->
    <div class="policy-details-content">
      <!-- Compliance Approval Section -->
      <div class="policy-approval-section">
        <h4>
          <span v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'">
            Compliance Deactivation Approval
          </span>
          <span v-else>
            Compliance Approval
          </span>
        </h4>
        
        <!-- Quick Action Button -->
        <div class="policy-actions">
          <button class="submit-btn" @click="submitReview()">
            <i class="fas fa-paper-plane"></i>
            <span>Submit Review</span>
          </button>
        </div>
        
        <!-- Approval Status Display -->
        <div v-if="approvalStatus" class="policy-approval-status">
          <div class="status-container">
            <div class="status-label">Current Status:</div>
            <div class="status-value" :class="{
              'approved': approvalStatus.approved === true,
              'rejected': approvalStatus.approved === false,
              'pending': approvalStatus.approved === null
            }">
              {{ approvalStatus.approved === true ? 'Approved' :
                 approvalStatus.approved === false ? 'Rejected' : 'Pending Review' }}
            </div>
          </div>
          
          <!-- Approval Date Display -->
          <div v-if="selectedApproval.ApprovedDate" class="approval-date">
            <div class="date-label">
              <i class="fas fa-calendar-check"></i>
              Approved on:
            </div>
            <div class="date-value">{{ formatDate(selectedApproval.ApprovedDate) }}</div>
          </div>
          
          <!-- Rejection Remarks -->
          <div v-if="approvalStatus.approved === false && approvalStatus.remarks" class="policy-rejection-remarks">
            <div class="remarks-label">
              <i class="fas fa-exclamation-circle"></i>
              Rejection Reason:
            </div>
            <div class="remarks-value">{{ approvalStatus.remarks }}</div>
          </div>
        </div>
      </div>
      
      <!-- Compliance Details Display -->
      <div v-if="selectedApproval.ExtractedData" class="compliance-details">
        <!-- Deactivation Request Details -->
        <div v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'" 
             class="deactivation-request-details">
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-question-circle"></i>
              Reason for Deactivation:
            </strong>
            <span>{{ selectedApproval.ExtractedData.reason || 'No reason provided' }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-info-circle"></i>
              Current Status:
            </strong>
            <span class="status-badge current">{{ selectedApproval.ExtractedData.current_status }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-arrow-right"></i>
              Requested Status:
            </strong>
            <span class="status-badge requested">{{ selectedApproval.ExtractedData.requested_status }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-sitemap"></i>
              Cascade to Policies:
            </strong>
            <span class="cascade-indicator" :class="{ 'warning': selectedApproval.ExtractedData.cascade_to_policies === 'Yes' }">
              {{ selectedApproval.ExtractedData.cascade_to_policies }}
            </span>
          </div>
          
          <div v-if="selectedApproval.ExtractedData.affected_policies_count > 0" class="compliance-detail-row">
            <strong>
              <i class="fas fa-file-alt"></i>
              Affected Policies:
            </strong>
            <span class="policy-count">{{ selectedApproval.ExtractedData.affected_policies_count }} policies</span>
          </div>
          
          <!-- Enhanced Warning Message -->
          <div class="warning-message">
            <i class="fas fa-exclamation-triangle"></i>
            <span>
              <strong>Warning:</strong> Deactivating this compliance will make it inactive.
              {{ selectedApproval.ExtractedData.cascade_to_policies === 'Yes' ? 
                 'All related policies will also be deactivated.' : 
                 'Related policies will not be affected.' }}
            </span>
          </div>
        </div>
        
        <!-- Regular Compliance Details -->
        <div v-else>
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-file-text"></i>
              Description:
            </strong>
            <span>{{ selectedApproval.ExtractedData.ComplianceItemDescription }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-exclamation"></i>
              Criticality:
            </strong>
            <span class="criticality-badge" :class="selectedApproval.ExtractedData.Criticality?.toLowerCase()">
              {{ selectedApproval.ExtractedData.Criticality }}
            </span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-chart-line"></i>
              Severity Rating:
            </strong>
            <span class="severity-rating">{{ selectedApproval.ExtractedData.Impact }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-percentage"></i>
              Probability:
            </strong>
            <span class="probability-value">{{ selectedApproval.ExtractedData.Probability }}</span>
          </div>
          
          <div class="compliance-detail-row">
            <strong>
              <i class="fas fa-shield-alt"></i>
              Mitigation:
            </strong>
            <span>{{ selectedApproval.ExtractedData.mitigation }}</span>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="policy-actions">
          <button class="approve-btn" @click="approveCompliance()">
            <i class="fas fa-check"></i>
            <span>Approve</span>
          </button>
          <button class="reject-btn" @click="rejectCompliance()">
            <i class="fas fa-times"></i>
            <span>Reject</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Enhanced Rejection Modal -->
    <div v-if="showRejectModal" class="reject-modal">
      <div class="reject-modal-content">
        <h4>
          <i class="fas fa-times-circle"></i>
          Rejection Reason Required
        </h4>
        <p>Please provide a detailed reason for rejecting this compliance item. This information will be used to improve future submissions.</p>
        
        <textarea
          v-model="rejectionComment"
          class="rejection-comment"
          placeholder="Enter your detailed comments here...">
        </textarea>
        
        <div class="reject-modal-actions">
          <button class="cancel-btn" @click="cancelRejection">
            <i class="fas fa-arrow-left"></i>
            Cancel
          </button>
          <button class="confirm-btn" @click="confirmRejection">
            <i class="fas fa-check"></i>
            Confirm Rejection
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Popup Modal Component -->
  <PopupModal />
</template>
  </div>
</template>
 
<script>
import { complianceService } from '@/services/api';
import { PopupModal } from '../../modules/popup';
import PopupMixin from './mixins/PopupMixin';
import { CompliancePopups } from './utils/popupUtils';
import CollapsibleTable from '../CollapsibleTable.vue';
 
export default {
  name: 'ComplianceApprover',
  components: {
    PopupModal,
    CollapsibleTable
  },
  mixins: [PopupMixin],
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      rejectedCompliances: [],
      showEditComplianceModal: false,
      editingCompliance: null,
      userId: 2, // Default user id
      isLoading: false,
      error: null,
      counts: {
        pending: 0,
        approved: 0,
        rejected: 0
      },
      refreshInterval: null,
      isLoadingRejected: false,
      isDeactivationRequest: false,
      collapsibleStates: {
        Pending: true,
        Approved: false,
        Rejected: false,
        'Recently Approved': false
      }
    }
  },
  async mounted() {
    console.log('ComplianceApprover mounted');
    await this.refreshData();
    
    // Set up auto-refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, 30000);
  },
  beforeUnmount() {
    // Clear the refresh interval when component is destroyed
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async refreshData() {
      if (this.isLoading) return; // Prevent multiple simultaneous refreshes
      
      this.isLoading = true;
      this.error = null;
      console.log('Refreshing data...');
      
      try {
        // Fetch approvals with reviewer_id
        const approvalsResponse = await complianceService.getCompliancePolicyApprovals({
          reviewer_id: this.userId
        });
        console.log('Approvals response:', approvalsResponse);

        if (approvalsResponse.data.success) {
          // Debug the incoming data
          console.log('Raw approvals data:', approvalsResponse.data.data);
          
          // Check for deactivation requests specifically
          const deactivationRequests = (approvalsResponse.data.data || []).filter(approval => 
            approval.ExtractedData?.type === 'compliance_deactivation' || 
            approval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
            (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'))
          );
          
          console.log(`Found ${deactivationRequests.length} deactivation requests in the response:`, deactivationRequests);
          
          // Ensure ExtractedData is properly formatted
          this.approvals = (approvalsResponse.data.data || []).map(approval => ({
            ...approval,
            ExtractedData: {
              ...approval.ExtractedData,
              type: approval.ExtractedData?.type || 'compliance',
              compliance_approval: approval.ExtractedData?.compliance_approval || {
                approved: null,
                remarks: ''
              }
            }
          }));
          
          this.counts = approvalsResponse.data.counts || {
            pending: 0,
            approved: 0,
            rejected: 0
          };
          
          // Log approved compliances specifically to debug
          const approvedItems = this.approvals.filter(a => a.ApprovedNot === true);
          console.log(`Found ${approvedItems.length} approved compliances:`, approvedItems);
          
          console.log('Updated approvals:', this.approvals);
          console.log('Updated counts:', this.counts);
        } else {
          throw new Error(approvalsResponse.data.message || 'Failed to fetch approvals');
        }
        
        // Load rejected compliances
        await this.loadRejectedCompliances();
        
      } catch (error) {
        console.error('Error refreshing data:', error);
        this.error = error.response?.data?.message || error.message || 'Failed to load approvals';
      } finally {
        this.isLoading = false;
      }
    },
   
    openApprovalDetails(approval) {
      console.log('Opening approval details:', approval);
      this.selectedApproval = approval;
      this.showDetails = true;
    },
   
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
   
    async submitReview() {
      // Use popup for confirmation instead of window.confirm
      this.showConfirmPopup(
        'Do you want to approve this compliance item?',
        'Compliance Review',
        () => this.processApproval(true),
        () => this.showRejectPopup()
      );
    },
   
    showRejectPopup() {
      // Use popup for getting rejection comments
      this.showCommentPopup(
        'Please provide a reason for rejecting this compliance:',
        'Reject Compliance',
        (comments) => this.processApproval(false, comments)
      );
    },
    
    async processApproval(isApproved, remarks = '') {
      try {
        if (!this.selectedApproval) {
          return;
        }
        
        this.isSubmitting = true;
        
        let approvalId = this.selectedApproval.ApprovalId;
        
        // Handle different approval types
        if (this.selectedApproval.ExtractedData?.type === 'compliance_deactivation' ||
            this.selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive') {
          
          // Deactivation approval/rejection
          if (isApproved) {
            await complianceService.approveComplianceDeactivation(
              approvalId,
              { user_id: this.userId }
            );
          } else {
            await complianceService.rejectComplianceDeactivation(
              approvalId,
              { 
                user_id: this.userId,
                remarks: remarks
              }
            );
          }
        } else {
          // Regular compliance approval
          
          // Extract data from selected approval
          let extractedData = this.selectedApproval.ExtractedData;
          
          // Update approval status in the extracted data
          if (!extractedData.compliance_approval) {
            extractedData.compliance_approval = {};
          }
          
          extractedData.compliance_approval.approved = isApproved;
          extractedData.compliance_approval.remarks = remarks;
          
          await complianceService.submitComplianceReview(
            approvalId,
            {
              ExtractedData: extractedData,
              ApprovedNot: isApproved
            }
          );
        }
        
        // Show success popup
        CompliancePopups.reviewSubmitted(isApproved);
        
        // Update local approval status
        this.approvalStatus = {
          approved: isApproved,
          remarks: remarks
        };
        
        // Refresh the list
        this.refreshData();
      } catch (error) {
        console.error('Error submitting review:', error);
        // Show error popup
        this.showErrorPopup(`Error submitting review: ${error.message || 'Unknown error'}`);
      } finally {
        this.isSubmitting = false;
      }
    },
   
    async approveCompliance() {
      if (!this.selectedApproval) return;
     
      try {
        this.isLoading = true;
        console.log("Starting approval process for compliance ID:", this.selectedApproval.ApprovalId);
       
        // Check if this is a deactivation request
        const isDeactivationRequest = 
          this.selectedApproval.ExtractedData?.type === 'compliance_deactivation' || 
          this.selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
          (this.selectedApproval.Identifier && this.selectedApproval.Identifier.includes('COMP-DEACTIVATE'));
        
        console.log(`This is ${isDeactivationRequest ? 'a' : 'not a'} deactivation request`);
        
        let response;
        
        if (isDeactivationRequest) {
          // This is a deactivation request
          console.log("Processing deactivation approval...");
          response = await complianceService.approveComplianceDeactivation(
            this.selectedApproval.ApprovalId,
            { user_id: this.userId }
          );
          
          // Update the local data to reflect the compliance was deactivated
          if (this.selectedApproval.ExtractedData) {
            this.selectedApproval.ExtractedData.current_status = 'Inactive';
            if (this.selectedApproval.ExtractedData.compliance_approval) {
              this.selectedApproval.ExtractedData.compliance_approval.approved = true;
            }
          }
        } else {
          // This is a regular compliance approval
          // Initialize compliance approval if doesn't exist
          if (!this.selectedApproval.ExtractedData.compliance_approval) {
            this.selectedApproval.ExtractedData.compliance_approval = {};
          }
          this.selectedApproval.ExtractedData.compliance_approval.approved = true;
          this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
         
          // Update the overall approval status
          this.selectedApproval.ApprovedNot = true;
         
          // Update status in ExtractedData - IMPORTANT for update after approval
          this.selectedApproval.ExtractedData.Status = 'Approved';
          this.selectedApproval.ExtractedData.ActiveInactive = 'Active';
         
          console.log('Approving compliance with data:', JSON.stringify(this.selectedApproval.ExtractedData));
         
          // Create a payload with just what's needed to reduce chance of network issues
          const reviewPayload = {
            ExtractedData: this.selectedApproval.ExtractedData,
            ApprovedNot: true
          };
          
          try {
            // First try with the full data
            response = await complianceService.submitComplianceReview(
              this.selectedApproval.ApprovalId,
              reviewPayload
            );
          } catch (apiError) {
            console.error('API call failed:', apiError);
            
            // If there's a network error, try with a simplified payload
            if (apiError.message === 'Network Error' || apiError.code === 'ERR_NETWORK') {
              console.log('Retrying with simplified payload due to network error');
              
              // Create a minimal payload for the retry
              const minimalPayload = {
                approved: true,
                remarks: ''
              };
              
              response = await complianceService.submitComplianceReview(
                this.selectedApproval.ApprovalId, 
                minimalPayload
              );
            } else {
              // If it's not a network error, rethrow
              throw apiError;
            }
          }
        }
       
        console.log('Approval response:', response?.data);
       
        // Remove from rejected list if it was previously rejected
        if (this.selectedApproval.Identifier) {
          console.log(`Checking if identifier ${this.selectedApproval.Identifier} exists in rejected list...`);
          const beforeCount = this.rejectedCompliances.length;
          
          this.rejectedCompliances = this.rejectedCompliances.filter(item =>
            item.Identifier !== this.selectedApproval.Identifier
          );
          
          const afterCount = this.rejectedCompliances.length;
          if (beforeCount > afterCount) {
            console.log(`Removed ${beforeCount - afterCount} item(s) with identifier ${this.selectedApproval.Identifier} from rejected list`);
          }
        }
       
        // Replace alert with popup
        this.showSuccessPopup(
          isDeactivationRequest ? 
          'Compliance has been deactivated successfully!' : 
          'Compliance has been approved successfully!',
          isDeactivationRequest ? 'Deactivation Complete' : 'Approval Complete'
        );
          
        this.closeApprovalDetails();
       
        // Force a refresh after a short delay to ensure backend has updated
        setTimeout(() => {
          this.refreshData();
        }, 1000);
      } catch (error) {
        console.error('Error approving compliance:', error);
        // Replace alert with popup
        this.showErrorPopup(
          'Error approving compliance: ' + (error.response?.data?.message || error.message || 'Network error - please check server connection'),
          'Approval Error'
        );
      } finally {
        this.isLoading = false;
      }
    },
   
    rejectCompliance() {
      // Check if this is a deactivation request
      const isDeactivationRequest = 
        this.selectedApproval?.ExtractedData?.type === 'compliance_deactivation' || 
        this.selectedApproval?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (this.selectedApproval?.Identifier && this.selectedApproval?.Identifier.includes('COMP-DEACTIVATE'));
      
      // Store the request type in the component data to use in confirmation
      this.isDeactivationRequest = isDeactivationRequest;
      
      this.showRejectModal = true;
    },
   
    async confirmRejection() {
      if (!this.rejectionComment.trim()) {
        alert('Please provide a reason for rejection');
        return;
      }
     
      try {
        this.isLoading = true;
        console.log("Starting rejection process for compliance ID:", this.selectedApproval.ApprovalId);
        
        let response;
        
        // Check if this is a deactivation request based on stored value
        if (this.isDeactivationRequest) {
          // This is a deactivation request rejection
          console.log("Processing deactivation rejection...");
          response = await complianceService.rejectComplianceDeactivation(
            this.selectedApproval.ApprovalId,
            { 
              user_id: this.userId,
              remarks: this.rejectionComment
            }
          );
          
          // Update the local data to reflect the deactivation was rejected
          if (this.selectedApproval.ExtractedData) {
            // Ensure compliance status remains Active in the local data
            this.selectedApproval.ExtractedData.current_status = 'Active';
            if (this.selectedApproval.ExtractedData.compliance_approval) {
              this.selectedApproval.ExtractedData.compliance_approval.approved = false;
              this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
            }
          }
        } else {
          // This is a regular compliance rejection
          // Initialize compliance approval object if it doesn't exist
          if (!this.selectedApproval.ExtractedData.compliance_approval) {
            this.selectedApproval.ExtractedData.compliance_approval = {};
          }
          
          // Set the approval status to rejected and add remarks
          this.selectedApproval.ExtractedData.compliance_approval.approved = false;
          this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
          this.selectedApproval.ApprovedNot = false;
          
          // Update status in ExtractedData - IMPORTANT for update after rejection
          this.selectedApproval.ExtractedData.Status = 'Rejected';
          this.selectedApproval.ExtractedData.ActiveInactive = 'Inactive';
          
          console.log('Rejecting compliance with data:', JSON.stringify(this.selectedApproval.ExtractedData));
          
          // Submit the review with the updated data
          response = await complianceService.submitComplianceReview(
            this.selectedApproval.ApprovalId,
            {
              ExtractedData: this.selectedApproval.ExtractedData,
              ApprovedNot: false
            }
          );
        }
        
        console.log('Rejection response:', response.data);
        
        // Replace alert with popup
        this.showSuccessPopup(
          this.isDeactivationRequest ? 
          'Deactivation request has been rejected successfully!' : 
          'Compliance has been rejected successfully!',
          'Rejection Complete'
        );
          
        this.showRejectModal = false;
        this.rejectionComment = '';
        this.closeApprovalDetails();
        
        // Force a refresh after a short delay to ensure backend has updated
        setTimeout(() => {
          this.refreshData();
        }, 1000);
      } catch (error) {
        console.error('Error rejecting compliance:', error);
        // Replace alert with popup
        this.showErrorPopup(
          'Error rejecting compliance: ' + (error.response?.data?.message || error.message),
          'Rejection Error'
        );
      } finally {
        this.isLoading = false;
      }
    },
   
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
   
    openRejectedItem(item) {
      console.log('Opening rejected item:', item);
      this.editingCompliance = JSON.parse(JSON.stringify(item));
      this.showEditComplianceModal = true;
      
      // Log details for debugging
      console.log('Opened rejected item in edit modal:', {
        ApprovalId: this.editingCompliance.ApprovalId,
        Identifier: this.editingCompliance.Identifier,
        ApprovedNot: this.editingCompliance.ApprovedNot,
        remarks: this.editingCompliance.ExtractedData?.compliance_approval?.remarks
      });
    },
   
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
   
    async resubmitCompliance(compliance) {
      try {
        // Reset approval status
        if (compliance.ExtractedData.compliance_approval) {
          compliance.ExtractedData.compliance_approval.approved = null;
          compliance.ExtractedData.compliance_approval.remarks = '';
          // Mark as being resubmitted to prevent showing in the rejected list
          compliance.ExtractedData.compliance_approval.inResubmission = true;
        } else {
          compliance.ExtractedData.compliance_approval = {
            approved: null,
            remarks: '',
            inResubmission: true
          };
        }
       
        this.isLoading = true;
        console.log("Resubmitting compliance with ID:", compliance.ApprovalId);
        console.log("Resubmitting with data:", JSON.stringify(compliance.ExtractedData));
        
        const response = await complianceService.resubmitComplianceApproval(
          compliance.ApprovalId,
          { ExtractedData: compliance.ExtractedData }
        );
       
        console.log("Resubmission response:", response);
        
        if (response.data && (response.data.ApprovalId || response.data.success)) {
          // Remove the resubmitted item from the rejected list immediately
          this.rejectedCompliances = this.rejectedCompliances.filter(item => 
            item.ApprovalId !== compliance.ApprovalId
          );
          
          this.showEditComplianceModal = false;
          this.editingCompliance = null;
          
          // Show success message after the UI updates
          this.showSuccessPopup('Compliance resubmitted for review successfully!', 'Resubmission Complete');
          
          // Show more details about what happened
          console.log(`Resubmitted compliance with ID ${compliance.ApprovalId}. New version: ${response.data.Version}`);
          
          // Wait a moment before refreshing to allow the backend to update
          setTimeout(() => {
            this.refreshData();
          }, 1000);
        } else {
          throw new Error('Failed to get confirmation from server');
        }
      } catch (error) {
        console.error('Error resubmitting compliance:', error);
        this.showErrorPopup('Error resubmitting compliance: ' + (error.response?.data?.message || error.message), 'Resubmission Error');
      } finally {
        this.isLoading = false;
      }
    },
   
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        // Handle different date formats
        let date;
        if (typeof dateString === 'string') {
          // Try different date formats
          if (dateString.includes('T')) {
            // ISO format
            date = new Date(dateString);
          } else if (dateString.includes('-')) {
            // YYYY-MM-DD format
            const parts = dateString.split(' ')[0].split('-');
            date = new Date(parts[0], parts[1] - 1, parts[2]);
          } else if (dateString.includes('/')) {
            // MM/DD/YYYY format
            const parts = dateString.split(' ')[0].split('/');
            date = new Date(parts[2], parts[0] - 1, parts[1]);
          } else {
            date = new Date(dateString);
          }
        } else {
          date = new Date(dateString);
        }
        
        // Format the date
        return date.toLocaleString();
      } catch (e) {
        console.error('Error formatting date:', e);
        return dateString; // Return the original string if parsing fails
      }
    },
    async checkForApprovedIdentifiers() {
      // This is a manual check to see if any items in rejectedCompliances should be removed
      // because they have been approved
      if (this.rejectedCompliances.length === 0) return;
      
      const identifiersToCheck = this.rejectedCompliances.map(item => item.Identifier);
      console.log('Checking rejected identifiers for approved status:', identifiersToCheck);
      
      // Filter out any identifiers that appear in the approved list
      this.rejectedCompliances = this.rejectedCompliances.filter(item => {
        const isApproved = this.isCompliantIdentifierApproved(item.Identifier);
        if (isApproved) {
          console.log(`Found approved item with identifier ${item.Identifier}, removing from rejected list`);
        }
        return !isApproved;
      });
    },
    isCompliantIdentifierApproved(identifier) {
      // Check if any approval with this identifier exists and is approved
      return this.approvals.some(approval => 
        approval.Identifier === identifier && approval.ApprovedNot === true
      );
    },
    // Load rejected compliances
    async loadRejectedCompliances() {
      try {
        this.isLoadingRejected = true;
        console.log(`Loading rejected compliances for reviewer_id: ${this.userId}`);
        const response = await complianceService.getComplianceRejectedApprovals(this.userId);
        console.log('Rejected compliances response:', response);

        if (response.data) {
          // Process the rejected items, excluding any that have been approved
          let filteredRejected = response.data
            .filter(item => 
              item.ApprovedNot === false && 
              item.Identifier &&
              !item.ExtractedData?.compliance_approval?.inResubmission
            )
            .sort((a, b) => {
              // Sort by ApprovalId (descending) so newest items appear first
              if (a.ApprovalId && b.ApprovalId) {
                return b.ApprovalId - a.ApprovalId;
              }
              return 0;
            });
          
          console.log('Filtered rejected compliances:', filteredRejected);
          
          // Get unique items (latest version only for each identifier)
          const uniqueIdentifiers = new Set();
          this.rejectedCompliances = filteredRejected.filter(item => {
            if (!uniqueIdentifiers.has(item.Identifier)) {
              uniqueIdentifiers.add(item.Identifier);
              // IMPORTANT: Check if any approval with this identifier exists and is approved
              const isApproved = this.approvals.some(approval => 
                approval.Identifier === item.Identifier && approval.ApprovedNot === true
              );
              
              // Only include if not approved
              return !isApproved;
            }
            return false;
          });
         
          console.log('Final rejected compliances list:', this.rejectedCompliances);
        }
      } catch (error) {
        console.error('Error fetching rejected compliances:', error);
      } finally {
        this.isLoadingRejected = false;
      }
    },
    mapApprovalToRow(approval) {
      return {
        ...approval,
        Identifier: approval.Identifier,
        Description: approval.ExtractedData?.ComplianceItemDescription || approval.ExtractedData?.reason || 'No Description',
        Criticality: approval.ExtractedData?.Criticality || 'N/A',
        CreatedBy: approval.ExtractedData?.CreatedByName || 'System',
        Version: approval.ExtractedData?.ComplianceVersion || approval.ExtractedData?.version || '1.0',
        actions: approval // Pass the whole object for the action button
      };
    },
    mapRejectedToRow(compliance) {
      return {
        ...compliance,
        Identifier: compliance.Identifier,
        Description: compliance.ExtractedData?.ComplianceItemDescription || 'No Description',
        Criticality: compliance.ExtractedData?.Criticality || 'N/A',
        CreatedBy: compliance.ExtractedData?.CreatedByName || 'System',
        Version: compliance.ExtractedData?.ComplianceVersion || compliance.ExtractedData?.version || '1.0',
        actions: compliance // Pass the whole object for the action button
      };
    },
    handleApprovalAction(approval) {
      this.openApprovalDetails(approval);
    },
    handleRejectedAction(compliance) {
      this.openRejectedItem(compliance);
    },
    toggleSection(section) {
      this.collapsibleStates = {
        ...this.collapsibleStates,
        [section]: !this.collapsibleStates[section]
      };
    },
  },
  computed: {
    pendingApprovalsCount() {
      return this.counts.pending || 0;
    },
    approvedApprovalsCount() {
      return this.counts.approved || 0;
    },
    rejectedApprovalsCount() {
      return this.counts.rejected || 0;
    },
    complianceApprovals() {
      console.log("Computing complianceApprovals from", this.approvals.length, "total approvals");
      
      // Debug all incoming approval data to verify deactivation requests
      console.log("All approvals:");
      this.approvals.forEach((approval, index) => {
        if (!approval) {
          console.log(`[${index}] Approval is null or undefined`);
          return;
        }
        
        console.log(`[${index}] ID: ${approval.ApprovalId}, Identifier: ${approval.Identifier}`);
        
        if (!approval.ExtractedData) {
          console.log(`    WARNING: ExtractedData is null or undefined`);
          return;
        }
        
        console.log(`    Type: ${approval.ExtractedData?.type}, RequestType: ${approval.ExtractedData?.RequestType}`);
        console.log(`    ApprovedNot: ${approval.ApprovedNot}`);
        
        // Check if this appears to be a deactivation request
        const isDeactivation = 
          approval.ExtractedData?.type === 'compliance_deactivation' || 
          approval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
          (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'));
          
        console.log(`    Is deactivation request: ${isDeactivation}`);
        
        if (isDeactivation) {
          console.log(`    Deactivation request details:`, 
            JSON.stringify({
              reason: approval.ExtractedData?.reason,
              compliance_id: approval.ExtractedData?.compliance_id,
              current_status: approval.ExtractedData?.current_status,
              requested_status: approval.ExtractedData?.requested_status
            })
          );
        }
      });
      
      // Apply the filter with detailed logging
      const filtered = this.approvals.filter(approval => {
        // Skip null or undefined approvals
        if (!approval) {
          console.log(`Skipping null approval`);
          return false;
        }
        
        // Check if ExtractedData exists
        if (!approval.ExtractedData) {
          console.log(`Approval ${approval.ApprovalId || 'unknown'}: ExtractedData is missing`);
          return false;
        }
        
        // For each approval, check if it matches our criteria
        const isCompliance = 
          approval.ExtractedData?.type === 'compliance' ||
          approval.ExtractedData?.type === 'compliance_deactivation' ||
          (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'));
          
        const isPending = approval.ApprovedNot === null;
        
        // CRITICAL: Log the exact properties we're testing for
        if (approval.ExtractedData?.type === 'compliance_deactivation') {
          console.log(`Found deactivation by type: ${approval.Identifier}`);
        }
        
        if (approval.ExtractedData?.RequestType === 'Change Status to Inactive') {
          console.log(`Found deactivation by RequestType: ${approval.Identifier}`);
        }
        
        if (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE')) {
          console.log(`Found deactivation by Identifier: ${approval.Identifier}`);
        }
        
        console.log(`Approval ${approval.ApprovalId}: isCompliance=${isCompliance}, isPending=${isPending}`);
        
        return isCompliance && isPending;
      });
      
      console.log(`Filtered to ${filtered.length} pending compliance approvals`);
      
      // If we have deactivation requests in the original data but none in the filtered list, log a warning
      const deactivationRequests = this.approvals.filter(approval => 
        approval?.ExtractedData?.type === 'compliance_deactivation' || 
        approval?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (approval?.Identifier && approval?.Identifier.includes('COMP-DEACTIVATE'))
      );
      
      if (deactivationRequests.length > 0 && !filtered.some(item => 
        item?.ExtractedData?.type === 'compliance_deactivation' || 
        item?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (item?.Identifier && item?.Identifier.includes('COMP-DEACTIVATE'))
      )) {
        console.warn('WARNING: Deactivation requests exist but none passed the filter!');
        
        // Try to find out why they were filtered out
        deactivationRequests.forEach(request => {
          console.log(`Deactivation request ${request.ApprovalId} with ApprovedNot=${request.ApprovedNot}`);
          
          // If it was filtered because it's already approved/rejected, add it anyway for testing
          if (request.ApprovedNot !== null) {
            console.log(`This request was filtered because ApprovedNot=${request.ApprovedNot}`);
            // Uncomment this line to force inclusion of these items for debugging
            // filtered.push(request);
          }
        });
      }
      
      return filtered;
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
    },
    approvedComplianceItems() {
      // Debug the approvals array
      console.log('Computing approvedComplianceItems from approvals:', this.approvals);
     
      // Filter approved items and include more details in the debug log
      const approved = this.approvals.filter(approval => {
        const isApproved = approval.ApprovedNot === true;
        const isCompliance = approval.ExtractedData?.type === 'compliance';
       
        if (isApproved) {
          console.log(`Approval ${approval.ApprovalId} is approved:`,
            {isCompliance, type: approval.ExtractedData?.type, ApprovedNot: approval.ApprovedNot});
        }
       
        return isApproved && isCompliance;
      });
     
      console.log(`Found ${approved.length} approved compliance items`);
      return approved;
    },
    groupedApprovals() {
      // Group approvals by status
      const groups = {
        Pending: [],
        Approved: [],
        Rejected: []
      };
      this.approvals.forEach(approval => {
        if (approval.ApprovedNot === null) {
          groups.Pending.push(approval);
        } else if (approval.ApprovedNot === true) {
          groups.Approved.push(approval);
        } else if (approval.ApprovedNot === false) {
          groups.Rejected.push(approval);
        }
      });
      return groups;
    },
    approvalTableHeaders() {
      return [
        { key: 'Identifier', label: 'Identifier' },
        { key: 'Description', label: 'Description' },
        { key: 'Criticality', label: 'Criticality' },
        { key: 'CreatedBy', label: 'Created By' },
        { key: 'Version', label: 'Version' },
        { key: 'actions', label: 'Actions' }
      ];
    },
    rejectedTableHeaders() {
      return [
        { key: 'Identifier', label: 'Identifier' },
        { key: 'Description', label: 'Description' },
        { key: 'Criticality', label: 'Criticality' },
        { key: 'CreatedBy', label: 'Created By' },
        { key: 'Version', label: 'Version' },
        { key: 'actions', label: 'Actions' }
      ];
    },
  }
}
</script>
 
<style scoped>
.error-message {
  background-color: #fee;
  color: #c00;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  border: 1px solid #fcc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
 
.retry-btn {
  background: #c00;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
 
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}
 
.no-data-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
  margin: 1rem 0;
}
 
.no-data-state i {
  font-size: 2rem;
  color: #999;
  margin-bottom: 1rem;
}
 
.approval-details {
  margin: 0.5rem 0;
}
 
.description {
  margin: 0.5rem 0;
  color: #666;
}
 
.meta-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}
 
.criticality {
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-weight: 500;
}
 
.criticality.high {
  background: #fee;
  color: #c00;
}
 
.criticality.medium {
  background: #ffd;
  color: #960;
}
 
.criticality.low {
  background: #efe;
  color: #060;
}
 
.created-by {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
 
.version {
  color: #999;
}
 
.approval-status.approved {
  color: #28a745;
  font-weight: 500;
}
 
.approved-list {
  margin-top: 2rem;
  background-color: #f8fff8;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #d0e9d0;
}
 
.approved-list h3 {
  color: #28a745;
  border-bottom: 1px solid #d0e9d0;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
 
.approved-list li {
  background-color: white;
  border: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 4px;
  position: relative;
}
 
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-left: 0.5rem;
}
 
.status-badge.approved {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
 
.approval-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #28a745;
}
 
.approval-date i {
  font-size: 0.9rem;
}
 
.rejection-reason {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fff0f0;
  border-left: 3px solid #ff3333;
  border-radius: 0 4px 4px 0;
  color: #c00;
  font-size: 0.9rem;
}

.badge.rejected {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.rejected-approvals-list {
  margin-top: 2rem;
  background-color: #fff8f8;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid #e6d0d0;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.1);
}

.rejected-approvals-list h3 {
  color: #c00;
  border-bottom: 1px solid #e6d0d0;
  padding-bottom: 0.8rem;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.rejected-approvals-list li {
  background-color: white;
  border: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 4px;
  position: relative;
}

.rejected-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.rejected-item-details {
  padding-left: 0.5rem;
  border-left: 2px solid #f0f0f0;
}

.rejected-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #d32f2f;
}

.rejected-date i {
  font-size: 0.9rem;
}

.edit-rejected-btn {
  margin-top: 1rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.edit-rejected-btn:hover {
  background-color: #eeeeee;
  border-color: #ccc;
}

.edit-rejected-btn i {
  font-size: 0.9rem;
  color: #555;
}

.rejected-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6d0d0;
  padding-bottom: 0.8rem;
  margin-bottom: 1.5rem;
}

.refresh-rejected-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #dc3545;
  background-color: #fff;
  color: #dc3545;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.refresh-rejected-btn:hover {
  background-color: #dc3545;
  color: white;
}

@import './ComplianceApprover.css';

/* Add styles for the deactivation badge */
.deactivation-badge {
  display: inline-block;
  background-color: #ffe0b2;
  color: #e65100;
  border: 1px solid #ffcc80;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

/* Add styles for the warning message */
.warning-message {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #fff3e0;
  border-left: 4px solid #ff9800;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning-message i {
  color: #ff9800;
  font-size: 1.2rem;
}

.deactivation-request-details {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff8e1;
  border-radius: 4px;
}

.compliance-details-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 2rem;
  margin: 2rem auto;
  max-width: 900px;
  position: relative;
  animation: fadeIn 0.3s;
}
.back-btn {
  background: #f5f5f5;
  border: none;
  color: #333;
  font-size: 1rem;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: background 0.2s;
}
.back-btn:hover {
  background: #e0e0e0;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(30px);}
  to { opacity: 1; transform: translateY(0);}
}
</style>