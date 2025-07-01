<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Framework Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <!-- Performance Summary Cards for Framework Approver -->
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

    <!-- Framework Approvals using CollapsibleTable -->
    <div class="approvals-container">
      <h3>My Framework Approval Tasks</h3>
      
      <!-- Pending/Under Review Frameworks -->
      <CollapsibleTable
        v-if="pendingFrameworks.length > 0"
        :section-config="pendingSectionConfig"
        :table-headers="tableHeaders"
        :is-expanded="sectionExpansion.pending"
        @toggle="toggleSection('pending')"
        @task-click="handleTaskClick"
      />
      
      <!-- Approved Frameworks -->
      <CollapsibleTable
        v-if="approvedFrameworks.length > 0"
        :section-config="approvedSectionConfig"
        :table-headers="tableHeaders"
        :is-expanded="sectionExpansion.approved"
        @toggle="toggleSection('approved')"
        @task-click="handleTaskClick"
      />
      
      <!-- Rejected Frameworks -->
      <CollapsibleTable
        v-if="rejectedFrameworksForTable.length > 0"
        :section-config="rejectedSectionConfig"
        :table-headers="tableHeaders"
        :is-expanded="sectionExpansion.rejected"
        @toggle="toggleSection('rejected')"
        @task-click="handleTaskClick"
      />
      
      <!-- Empty State -->
      <div v-if="sortedFrameworks.length === 0" class="empty-state">
        <div class="empty-state-content">
          <i class="fas fa-inbox"></i>
          <h4>No Framework Approval Tasks</h4>
          <p>There are currently no frameworks awaiting your approval.</p>
        </div>
      </div>
    </div>

    <!-- Framework Details Modal -->
    <div v-if="showFrameworkDetails && selectedApproval" class="framework-details-modal">
      <div class="framework-details-content">
        <h3>
          <span class="detail-type-indicator">Framework</span> 
          Details: {{ getFrameworkId(selectedApproval) }}
          <span class="version-pill">Version: {{ selectedApproval.version || 'u1' }}</span>
        </h3>
        
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Framework Approval Section -->
        <div class="framework-approval-section">
          <h4>Framework Approval</h4>
          
          <!-- Framework status indicator -->
          <div class="framework-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': selectedApproval.ApprovedNot === null && selectedApproval.ExtractedData?.Status !== 'Approved' && selectedApproval.ExtractedData?.Status !== 'Rejected'
            }">
              {{ selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
            <span v-if="selectedApproval.ApprovedDate" class="approval-date">
              (Approved on: {{ formatDate(selectedApproval.ApprovedDate) }})
            </span>
          </div>
          
          <div class="framework-actions">
            <button class="approve-btn" @click="approveFramework()" v-if="isReviewer && selectedApproval.ApprovedNot === null">
              <i class="fas fa-check"></i> Approve
            </button>
            <button class="reject-btn" @click="rejectFramework()" v-if="isReviewer && selectedApproval.ApprovedNot === null">
              <i class="fas fa-times"></i> Reject
            </button>
            <button class="submit-btn" @click="submitReview()" v-if="isReviewer && selectedApproval.ApprovedNot !== null">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
        </div>
        
        <!-- Display framework details -->
        <div v-if="selectedApproval.ExtractedData">
          <div v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="framework-detail-row">
            <template v-if="key !== 'policies' && key !== 'framework_approval' && key !== 'type' && key !== 'totalPolicies' && key !== 'totalSubpolicies'">
              <strong>{{ formatFieldName(key) }}:</strong> <span>{{ value }}</span>
            </template>
          </div>
        </div>

        <!-- Display policies from ExtractedData (for frameworks from tailoring) -->
        <div v-if="selectedApproval.ExtractedData?.policies && selectedApproval.ExtractedData.policies.length > 0" class="policies-section">
          <h4>Framework Policies ({{ selectedApproval.ExtractedData.totalPolicies || selectedApproval.ExtractedData.policies.length }})</h4>
          <div v-for="policy in selectedApproval.ExtractedData.policies" :key="policy.PolicyId" class="policy-item-detailed">
            <div class="policy-header">
              <h5 class="policy-name">{{ policy.PolicyName }}</h5>
              <div class="policy-header-actions">
                <span class="policy-status" :class="{
                  'status-approved': policy.Status === 'Approved',
                  'status-rejected': policy.Status === 'Rejected',
                  'status-pending': policy.Status === 'Under Review'
                }">{{ policy.Status }}</span>
                
                <!-- Policy Actions -->
                <div v-if="isReviewer && selectedApproval.ApprovedNot === null" class="policy-actions">
                  <button 
                    class="approve-policy-btn" 
                    @click="approvePolicy(policy)"
                    :disabled="!canApprovePolicy(policy)"
                    :title="!canApprovePolicy(policy) ? 'All subpolicies must be approved first' : 'Approve Policy'"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    class="reject-policy-btn" 
                    @click="rejectPolicy(policy)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <div class="policy-details">
              <div class="policy-detail-item">
                <strong>Description:</strong> {{ policy.PolicyDescription }}
              </div>
              <div class="policy-detail-item" v-if="policy.Objective">
                <strong>Objective:</strong> {{ policy.Objective }}
              </div>
              <div class="policy-detail-item" v-if="policy.Scope">
                <strong>Scope:</strong> {{ policy.Scope }}
              </div>
              <div class="policy-detail-item" v-if="policy.Department">
                <strong>Department:</strong> {{ policy.Department }}
              </div>
              <div class="policy-detail-item" v-if="policy.Applicability">
                <strong>Applicability:</strong> {{ policy.Applicability }}
              </div>
              <div class="policy-detail-item" v-if="policy.Identifier">
                <strong>Identifier:</strong> {{ policy.Identifier }}
              </div>
              <div class="policy-detail-item" v-if="policy.CoverageRate">
                <strong>Coverage Rate:</strong> {{ policy.CoverageRate }}%
              </div>
              <div class="policy-detail-item" v-if="policy.PolicyType">
                <strong>Policy Type:</strong>
                <span>{{ policy.PolicyType }}</span>
              </div>
              <div class="policy-detail-item" v-if="policy.PolicyCategory">
                <strong>Policy Category:</strong>
                <span>{{ policy.PolicyCategory }}</span>
              </div>
              <div class="policy-detail-item" v-if="policy.PolicySubCategory">
                <strong>Policy Sub Category:</strong>
                <span>{{ policy.PolicySubCategory }}</span>
              </div>
            </div>
            
            <!-- Display subpolicies -->
            <div v-if="policy.subpolicies && policy.subpolicies.length > 0" class="subpolicies-section">
              <h6>Sub-Policies ({{ policy.subpolicies.length }})</h6>
              <div v-for="subpolicy in policy.subpolicies" :key="subpolicy.SubPolicyId" class="subpolicy-item">
                <div class="subpolicy-header">
                  <span class="subpolicy-name">{{ subpolicy.SubPolicyName }}</span>
                  <div class="subpolicy-header-actions">
                    <span class="subpolicy-status" :class="{
                      'status-approved': subpolicy.Status === 'Approved',
                      'status-rejected': subpolicy.Status === 'Rejected',
                      'status-pending': subpolicy.Status === 'Under Review'
                    }">{{ subpolicy.Status }}</span>
                    
                    <!-- Subpolicy Actions -->
                    <div v-if="isReviewer && selectedApproval.ApprovedNot === null" class="subpolicy-actions">
                      <button 
                        class="approve-subpolicy-btn" 
                        @click="approveSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Approved'"
                      >
                        <i class="fas fa-check"></i>
                      </button>
                      <button 
                        class="reject-subpolicy-btn" 
                        @click="rejectSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Rejected'"
                      >
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="subpolicy-details">
                  <div class="subpolicy-detail-item">
                    <strong>Description:</strong> {{ subpolicy.Description }}
                  </div>
                  <div class="subpolicy-detail-item" v-if="subpolicy.Control">
                    <strong>Control:</strong> {{ subpolicy.Control }}
                  </div>
                  <div class="subpolicy-detail-item" v-if="subpolicy.Identifier">
                    <strong>Identifier:</strong> {{ subpolicy.Identifier }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Framework level approval summary -->
          <div class="framework-approval-summary">
            <div class="approval-summary-item">
              <strong>Approval Status:</strong>
              <span>{{ getFrameworkApprovalStatus() }}</span>
            </div>
            <div v-if="canApproveFramework()" class="framework-final-actions">
              <button class="approve-framework-btn" @click="approveEntireFramework()">
                <i class="fas fa-check-circle"></i> Approve Entire Framework
              </button>
            </div>
          </div>
        </div>

        <!-- Display policies from API call (for approved frameworks) -->
        <div v-else-if="selectedApproval.ApprovedNot === true && selectedApproval.policies && selectedApproval.policies.length > 0" class="policies-section">
          <h4>Framework Policies</h4>
          <ul class="policies-list">
            <li v-for="policy in selectedApproval.policies" :key="policy.PolicyId" class="policy-item">
              <span class="policy-name">{{ policy.PolicyName }}</span>
              <span class="policy-status" :class="{
                'status-approved': policy.Status === 'Approved',
                'status-rejected': policy.Status === 'Rejected',
                'status-pending': policy.Status === 'Under Review'
              }">{{ policy.Status }}</span>
            </li>
          </ul>
        </div>

        <!-- Add a message for rejected frameworks -->
        <div v-if="selectedApproval.ApprovedNot === false" class="rejected-framework-message">
          <div class="rejection-note">
            <i class="fas fa-exclamation-triangle"></i>
            This framework has been rejected. All policies and subpolicies within this framework have been automatically rejected.
          </div>
        </div>
      </div>
      
      <!-- Rejection Modal -->
      <div v-if="showRejectModal" class="reject-modal">
        <div class="reject-modal-content">
          <h4>Rejection Reason</h4>
          <p>Please provide a reason for rejecting this {{ currentRejectionType }}</p>
          <textarea 
            v-model="rejectionComment" 
            class="rejection-comment" 
            placeholder="Enter your comments here..."></textarea>
          <div class="reject-modal-actions">
            <button class="cancel-btn" @click="cancelRejection">Cancel</button>
            <button class="confirm-btn" @click="confirmRejection">Confirm Rejection</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rejected Frameworks List -->
    <div class="rejected-approvals-list" v-if="rejectedFrameworks.length">
      <h3>Rejected Frameworks (Edit & Resubmit)</h3>
      
      <!-- DynamicTable for Rejected Frameworks -->
      <DynamicTable
        :data="rejectedFrameworksTableData"
        :columns="rejectedFrameworksColumns"
        :show-actions="true"
        :show-pagination="true"
        :default-page-size="5"
        unique-key="FrameworkId"
        @row-select="handleRejectedFrameworkSelect"
      >
        <template #cell-rejectionReason="{ row }">
          <span 
            :title="row.originalFramework.rejection_reason || 'No reason provided'"
            class="rejection-reason-cell"
          >
            {{ row.rejectionReason }}
          </span>
        </template>
        <template #cell-status="{ row }">
          <span class="status-badge status-rejected">
            <i class="fas fa-times-circle"></i> {{ row.status }}
          </span>
        </template>
        <template #actions="{ row }">
          <button 
            class="view-btn"
            @click="openRejectedItem(row.originalFramework)"
            title="View and Edit Framework"
          >
            <i class="fas fa-eye"></i> View
          </button>
        </template>
      </DynamicTable>
    </div>

    <!-- Edit Modal for Rejected Framework -->
    <div v-if="showEditModal && editingFramework" class="edit-framework-modal">
      <div class="edit-framework-content">
        <h3>Edit & Resubmit Framework: {{ getFrameworkId(editingFramework) }}</h3>
        <button class="close-btn" @click="closeEditModal">Close</button>
        
        <!-- Framework fields -->
        <div>
          <label>Framework Name:</label>
          <input v-model="editingFramework.ExtractedData.FrameworkName" />
        </div>
        <div>
          <label>Framework Description:</label>
          <textarea v-model="editingFramework.ExtractedData.FrameworkDescription"></textarea>
        </div>
        <div>
          <label>Category:</label>
          <input v-model="editingFramework.ExtractedData.Category" />
        </div>
        <div>
          <label>Effective Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EffectiveDate" />
        </div>
        <div>
          <label>Start Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.StartDate" />
        </div>
        <div>
          <label>End Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EndDate" />
        </div>
        
        <!-- Show rejection reason -->
        <div v-if="editingFramework.rejection_reason">
          <label>Rejection Reason:</label>
          <div class="rejection-reason">{{ editingFramework.rejection_reason }}</div>
        </div>
        
        <!-- Edit Policies -->
        <div v-if="editingFramework.ExtractedData.policies" class="edit-policies-section">
          <h4>Edit Policies</h4>
          <div v-for="(policy, policyIndex) in editingFramework.ExtractedData.policies" :key="policyIndex" class="edit-policy-item">
            <h5>{{ policy.PolicyName }}</h5>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Name:</label>
                <input v-model="policy.PolicyName" />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="policy.PolicyDescription"></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Objective:</label>
                <textarea v-model="policy.Objective"></textarea>
              </div>
              <div class="form-group">
                <label>Scope:</label>
                <textarea v-model="policy.Scope"></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Type:</label>
                <select v-model="policy.PolicyType" class="form-control" @change="handlePolicyTypeChange(policy)">
                  <option value="">Select Type</option>
                  <option v-for="type in policyTypeOptions" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Policy Category:</label>
                <select v-model="policy.PolicyCategory" class="form-control" @change="handlePolicyCategoryChange(policy)">
                  <option value="">Select Category</option>
                  <option v-for="category in filteredPolicyCategories(policy.PolicyType)" :key="category" :value="category">{{ category }}</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Sub Category:</label>
                <select v-model="policy.PolicySubCategory" class="form-control">
                  <option value="">Select Sub Category</option>
                  <option v-for="subCategory in filteredPolicySubCategories(policy.PolicyType, policy.PolicyCategory)" :key="subCategory" :value="subCategory">{{ subCategory }}</option>
                </select>
              </div>
            </div>
            
            <!-- Edit Subpolicies -->
            <div v-if="policy.subpolicies" class="edit-subpolicies-section">
              <h6>Edit Sub-Policies</h6>
              <div v-for="(subpolicy, subIndex) in policy.subpolicies" :key="subIndex" class="edit-subpolicy-item">
                <div class="form-row">
                  <div class="form-group">
                    <label>Sub-Policy Name:</label>
                    <input v-model="subpolicy.SubPolicyName" />
                  </div>
                  <div class="form-group">
                    <label>Description:</label>
                    <textarea v-model="subpolicy.Description"></textarea>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Control:</label>
                    <textarea v-model="subpolicy.Control"></textarea>
                  </div>
                  <div class="form-group">
                    <label>Identifier:</label>
                    <input v-model="subpolicy.Identifier" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitFramework(editingFramework)">Resubmit for Review</button>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CollapsibleTable from '@/components/CollapsibleTable.vue'
import DynamicTable from '@/components/DynamicTable.vue'

export default {
  name: 'FrameworkApprover',
  components: {
    PopupModal,
    CollapsibleTable,
    DynamicTable
  },
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showFrameworkDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      currentRejectionType: 'framework', // 'framework', 'policy', or 'subpolicy'
      currentRejectionItem: null, // Store the item being rejected
      rejectedFrameworks: [],
      showEditModal: false,
      editingFramework: null,
      userId: 2, // Default user id
      isReviewer: true, // Set based on user role, for testing
      policyCategories: [], // Store all policy categories
      policyCategoriesMap: {}, // Structured map of policy categories
      // Table headers for CollapsibleTable
      tableHeaders: [
        { key: 'frameworkId', label: 'Framework ID', width: '120px' },
        { key: 'frameworkName', label: 'Framework Name', width: '200px' },
        { key: 'category', label: 'Category', width: '150px' },
        { key: 'createdBy', label: 'Created By', width: '150px' },
        { key: 'createdDate', label: 'Created Date', width: '120px' },
        { key: 'version', label: 'Version', width: '80px' },
        { key: 'status', label: 'Status', width: '120px' },
        { key: 'actions', label: 'Actions', width: '150px', className: 'actions-column' }
      ],
      // Expansion state for CollapsibleTable sections
      sectionExpansion: {
        pending: true,
        approved: false,
        rejected: false
      },
      rejectedFrameworksTableData: [],
      rejectedFrameworksColumns: [
        { key: 'frameworkId', label: 'Framework ID', width: '120px' },
        { key: 'frameworkName', label: 'Framework Name', width: '200px' },
        { key: 'category', label: 'Category', width: '150px' },
        { key: 'createdBy', label: 'Created By', width: '150px' },
        { key: 'createdDate', label: 'Created Date', width: '120px' },
        { key: 'version', label: 'Version', width: '80px' },
        { key: 'status', label: 'Status', width: '120px' },
        { key: 'rejectionReason', label: 'Rejection Reason', width: '200px' },
        { key: 'actions', label: 'Actions', width: '120px', className: 'actions-column' }
      ]
    }
  },
  mounted() {
    this.fetchFrameworks();
    this.fetchRejectedFrameworks();
    this.fetchPolicyTypes();
  },
  methods: {
    fetchFrameworks() {
      console.log('Fetching frameworks...');
      // Fetch all frameworks for approval workflow (including Under Review)
      axios.get('http://localhost:8000/api/frameworks/', {
        params: { include_all_status: true }
      })
        .then(response => {
          console.log('Frameworks response:', response.data);
          this.approvals = response.data.map(framework => {
            // Get latest version for framework
            let frameworkVersion = framework.CurrentVersion?.toString() || 'u1';
            
            return {
              FrameworkId: framework.FrameworkId,
              ExtractedData: {
                type: 'framework',
                FrameworkName: framework.FrameworkName,
                CreatedByName: framework.CreatedByName,
                CreatedByDate: framework.CreatedByDate,
                Category: framework.Category,
                Status: framework.Status,
                FrameworkDescription: framework.FrameworkDescription,
                EffectiveDate: framework.EffectiveDate,
                StartDate: framework.StartDate,
                EndDate: framework.EndDate,
                Identifier: framework.Identifier,
                DocURL: framework.DocURL,
                Reviewer: framework.Reviewer,
                InternalExternal: framework.InternalExternal
              },
              ApprovedNot: framework.Status === 'Approved' ? true : 
                          framework.Status === 'Rejected' ? false : null,
              version: frameworkVersion
            };
          })
          // Filter to show only frameworks that need approval or are in review
          .filter(framework => 
            framework.ExtractedData.Status === 'Under Review' || 
            framework.ExtractedData.Status === 'Approved' ||
            framework.ExtractedData.Status === 'Rejected'
          );
          console.log('Processed frameworks for approval:', this.approvals);
        })
        .catch(error => {
          console.error('Error fetching frameworks:', error);
        });
    },
    
    openApprovalDetails(framework) {
      // If clicking the same framework, toggle the details
      if (this.selectedApproval && this.selectedApproval.FrameworkId === framework.FrameworkId) {
        this.showDetails = !this.showDetails;
        if (!this.showDetails) {
          this.selectedApproval = null;
        }
        return;
      }

      // Get the framework ID
      const frameworkId = this.getFrameworkId(framework);

      // Fetch the latest framework approval
      axios.get(`http://localhost:8000/api/framework-approvals/latest/${frameworkId}/`)
        .then(approvalResponse => {
          console.log('Latest framework approval:', approvalResponse.data);
          
          // If we got data and it has ExtractedData, use it
          if (approvalResponse.data && approvalResponse.data.ExtractedData) {
            const latestApproval = approvalResponse.data;
            
            // Create a complete approval object with the latest data
            const updatedApproval = {
              ...framework,
              ...latestApproval,
              ExtractedData: latestApproval.ExtractedData
            };
            
            // Ensure consistency between framework status and policy/subpolicy statuses
            if (updatedApproval.ApprovedNot === true && updatedApproval.ExtractedData) {
              if (updatedApproval.ExtractedData.Status === 'Approved') {
                // If framework is approved, ensure all policies and subpolicies are also marked as approved
                if (updatedApproval.ExtractedData.policies) {
                  updatedApproval.ExtractedData.policies.forEach(policy => {
                    if (policy.Status !== 'Approved') {
                      console.log(`Correcting status for policy ${policy.PolicyId} from ${policy.Status} to Approved`);
                      policy.Status = 'Approved';
                    }
                    
                    if (policy.subpolicies) {
                      policy.subpolicies.forEach(subpolicy => {
                        if (subpolicy.Status !== 'Approved') {
                          console.log(`Correcting status for subpolicy ${subpolicy.SubPolicyId} from ${subpolicy.Status} to Approved`);
                          subpolicy.Status = 'Approved';
                        }
                      });
                    }
                  });
                }
              }
            }
            
            this.selectedApproval = updatedApproval;
            this.showFrameworkDetails = true;
            
            // Scroll to top of modal when opened
            this.$nextTick(() => {
              if (this.$refs.frameworkDetailsContent) {
                this.$refs.frameworkDetailsContent.scrollTop = 0;
              }
            });
          } else {
            console.error('Invalid approval data received:', approvalResponse.data);
            PopupService.error('Error: Could not load framework approval details', 'Loading Error');
          }
        })
        .catch(error => {
          this.handleError(error, 'loading framework approval details');
        });
    },
    
    refreshData() {
      this.fetchFrameworks();
      
      if (this.selectedApproval && this.selectedApproval.FrameworkId) {
        this.openApprovalDetails(this.selectedApproval);
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return ''; // Invalid date
      
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    isNewFramework(framework) {
      const createdDate = framework.ExtractedData?.CreatedByDate || framework.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    
    getFrameworkId(framework) {
      if (framework.FrameworkId) {
        return typeof framework.FrameworkId === 'object' ? framework.FrameworkId.FrameworkId : framework.FrameworkId;
      }
      return framework.ApprovalId;
    },
    
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showFrameworkDetails = false;
    },
    
    approveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for approval');
        return;
      }
      
      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = true;
      this.selectedApproval.ExtractedData.framework_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
      this.selectedApproval.ExtractedData.Status = 'Approved';
    },
    
    rejectFramework() {
      this.currentRejectionType = 'framework';
      this.currentRejectionItem = null;
      this.showRejectModal = true;
    },
    
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
      this.currentRejectionType = 'framework';
      this.currentRejectionItem = null;
    },
    
    confirmRejection() {
      if (!this.rejectionComment.trim()) {
        PopupService.warning('Please provide a rejection reason', 'Missing Reason');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      if (this.currentRejectionType === 'subpolicy' && this.currentRejectionItem) {
        const { policy, subpolicy } = this.currentRejectionItem;
        
        // Call backend endpoint for subpolicy rejection
        axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/subpolicies/${subpolicy.SubPolicyId}/approve-reject/`, {
          approved: false,
          rejection_reason: this.rejectionComment,
          submit_review: true // Add flag to submit review automatically
        })
          .then(response => {
            console.log('Subpolicy rejected successfully:', response.data);
            
            // Update local state
            subpolicy.Status = 'Rejected';
            policy.Status = 'Rejected';
            if (policy.subpolicies) {
              policy.subpolicies.forEach(sp => {
                sp.Status = 'Rejected';
              });
            }
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            this.selectedApproval.ApprovedNot = false;
            
            PopupService.success('Subpolicy rejected. Framework has been rejected and sent back for revision.', 'Subpolicy Rejected');
            this.cancelRejection();
            this.fetchFrameworks();
            this.fetchRejectedFrameworks();
            this.closeApprovalDetails(); // Close the details modal
          })
          .catch(error => {
            this.handleError(error, 'rejecting subpolicy');
          });
          
      } else if (this.currentRejectionType === 'policy' && this.currentRejectionItem) {
        const policy = this.currentRejectionItem;
        
        // Call backend endpoint for policy rejection
        axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/approve-reject/`, {
          approved: false,
          rejection_reason: this.rejectionComment,
          submit_review: true // Add flag to submit review automatically
        })
          .then(response => {
            console.log('Policy rejected successfully:', response.data);
            
            // Update local state
            policy.Status = 'Rejected';
            if (policy.subpolicies) {
              policy.subpolicies.forEach(subpolicy => {
                subpolicy.Status = 'Rejected';
              });
            }
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            this.selectedApproval.ApprovedNot = false;
            
            PopupService.success('Policy rejected. Framework has been rejected and sent back for revision.', 'Policy Rejected');
            this.cancelRejection();
            this.fetchFrameworks();
            this.fetchRejectedFrameworks();
            this.closeApprovalDetails(); // Close the details modal
          })
          .catch(error => {
            this.handleError(error, 'rejecting policy');
          });
          
      } else if (this.currentRejectionType === 'framework') {
        // For direct framework rejection, use submitFrameworkReview with rejection reason
        if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
          console.error('No framework selected for rejection');
          this.cancelRejection();
          return;
        }
        
        // Initialize framework approval if doesn't exist
        if (!this.selectedApproval.ExtractedData.framework_approval) {
          this.selectedApproval.ExtractedData.framework_approval = {};
        }
        
        // Update the framework status and approval state in the UI
        this.selectedApproval.ExtractedData.framework_approval.approved = false;
        this.selectedApproval.ExtractedData.framework_approval.remarks = this.rejectionComment;
        this.selectedApproval.ExtractedData.Status = 'Rejected';
        this.selectedApproval.ApprovedNot = false;
        
        // Submit the review with rejection data
        this.submitFrameworkReview(false, this.rejectionComment);
        
        this.cancelRejection();
      }
    },
    
    // Helper method to handle and display errors
    handleError(error, context) {
      console.error(`Error ${context}:`, error);
      let errorMessage = 'An unexpected error occurred';
      
      if (error.response) {
        // The server responded with a status code outside of 2xx range
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data && typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else {
          errorMessage = `Server error: ${error.response.status}`;
        }
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something happened in setting up the request
        errorMessage = error.message || errorMessage;
      }
      
      PopupService.error(`Error ${context}: ${errorMessage}`, 'Error');
      return errorMessage;
    },
    
    // Helper method to submit framework review
    submitFrameworkReview(approved, remarks = '') {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for review submission');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      console.log(`Submitting framework review for framework ${frameworkId}`, {
        approved: approved,
        remarks: remarks
      });
      
      // Create the framework review data
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: approved,
        remarks: remarks,
        UserId: this.userId,
        ReviewerId: this.userId,
        currentVersion: this.selectedApproval.version || 'u1'
      };
      
      // If approving, set all policies and subpolicies to Approved status
      if (approved === true && reviewData.ExtractedData.policies) {
        reviewData.ExtractedData.policies.forEach(policy => {
          policy.Status = 'Approved';
          policy.ActiveInactive = 'Active'; // Set policies to Active when framework is approved
          
          if (policy.subpolicies) {
            policy.subpolicies.forEach(subpolicy => {
              subpolicy.Status = 'Approved';
            });
          }
        });
      }

      // Set framework ActiveInactive to Active when approved
      if (approved === true) {
        reviewData.ExtractedData.ActiveInactive = 'Active';
      }
      
      // If rejecting, ensure framework_approval contains rejection remarks
      if (approved === false && remarks) {
        if (!reviewData.ExtractedData.framework_approval) {
          reviewData.ExtractedData.framework_approval = {};
        }
        reviewData.ExtractedData.framework_approval.remarks = remarks;
      }
      
      // Submit framework review
      axios.post(`http://localhost:8000/api/frameworks/${frameworkId}/submit-review/`, reviewData)
        .then(response => {
          console.log('Framework review submitted successfully:', response.data);
          
          // Update the approval data with the response
          this.selectedApproval.ApprovedNot = approved;
          this.selectedApproval.Version = response.data.Version;
          
          if (approved) {
            this.selectedApproval.ExtractedData.Status = 'Approved';
            
            // Store the approval date from the response
            if (response.data.ApprovedDate) {
              this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
            }
            
            // Update all policies and subpolicies to Approved status in the UI
            if (this.selectedApproval.ExtractedData.policies) {
              this.selectedApproval.ExtractedData.policies.forEach(policy => {
                policy.Status = 'Approved';
                
                if (policy.subpolicies) {
                  policy.subpolicies.forEach(subpolicy => {
                    subpolicy.Status = 'Approved';
                  });
                }
              });
            }
            
            PopupService.success('Framework approved successfully!', 'Framework Approved');
          } else {
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            PopupService.success('Framework rejected successfully!', 'Framework Rejected');
          }
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          this.handleError(error, 'submitting framework review');
        });
    },
    
    fetchRejectedFrameworks() {
      console.log('Fetching rejected frameworks...');
      // Use the user ID for fetching rejected frameworks
      axios.get(`http://localhost:8000/api/frameworks/rejected/`, {
        params: { user_id: this.userId }
      })
        .then(response => {
          console.log('Rejected frameworks response:', response.data);
          this.rejectedFrameworks = response.data.map(framework => {
            // Make sure framework data is properly structured
            if (!framework.ExtractedData) {
              framework.ExtractedData = {};
            }
            return framework;
          });
          
          // Transform data for table display
          this.rejectedFrameworksTableData = this.rejectedFrameworks.map(framework => 
            this.transformRejectedFrameworkForTable(framework)
          );
        })
        .catch(error => {
          console.error('Error fetching rejected frameworks:', error);
        });
    },
    
    openRejectedItem(framework) {
      console.log('Opening rejected framework for editing:', framework);
      this.editingFramework = JSON.parse(JSON.stringify(framework)); // Deep copy
      
      // Ensure the framework has the proper structure for editing
      if (!this.editingFramework.ExtractedData) {
        this.editingFramework.ExtractedData = {};
      }
      
      // Ensure policies array exists
      if (!this.editingFramework.ExtractedData.policies) {
        console.warn('No policies found in rejected framework, initializing empty policies array');
        this.editingFramework.ExtractedData.policies = [];
      } else {
        console.log(`Found ${this.editingFramework.ExtractedData.policies.length} policies in framework`);
        
        // Process each policy
        this.editingFramework.ExtractedData.policies.forEach(policy => {
          // Initialize policy category fields if they don't exist
          if (!policy.PolicyType) policy.PolicyType = '';
          if (!policy.PolicyCategory) policy.PolicyCategory = '';
          if (!policy.PolicySubCategory) policy.PolicySubCategory = '';
          
          console.log(`Policy ${policy.PolicyId} category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure each policy has subpolicies array
          if (!policy.subpolicies) {
            policy.subpolicies = [];
          }
        });
      }
      
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.editingFramework = null;
    },
    
    resubmitFramework(framework) {
      const frameworkId = this.getFrameworkId(framework);
      console.log('Resubmitting framework with ID:', frameworkId);
      console.log('Framework data before preparing:', framework);
      
      // Validate framework data
      const validationErrors = this.validateFrameworkData(framework);
      if (validationErrors.length > 0) {
        PopupService.warning(`Please fix the following errors before resubmitting:\n${validationErrors.join('\n')}`, 'Validation Errors');
        return;
      }
      
      // Check if policies exist and have proper structure
      if (framework.ExtractedData.policies && framework.ExtractedData.policies.length > 0) {
        // Ensure each policy has the correct fields
        framework.ExtractedData.policies.forEach((policy, index) => {
          console.log(`Checking policy ${index} with ID: ${policy.PolicyId}`);
          console.log(`Policy category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure subpolicies are properly formatted
          if (policy.subpolicies && policy.subpolicies.length > 0) {
            policy.subpolicies.forEach((subpolicy, subIndex) => {
              console.log(`Checking subpolicy ${subIndex} with ID: ${subpolicy.SubPolicyId}`);
              
              // Make sure required fields exist
              if (!subpolicy.SubPolicyName) {
                console.warn(`SubpolicyName is missing for subpolicy ${subIndex} in policy ${index}`);
              }
              if (!subpolicy.Description) {
                console.warn(`Description is missing for subpolicy ${subIndex} in policy ${index}`);
              }
            });
          } else {
            console.log(`Policy ${index} has no subpolicies or they are not properly structured`);
          }
        });
      } else {
        console.warn('No policies found in framework data or policies array is not properly structured');
      }
      
      // Prepare data for resubmission
      const resubmitData = {
        FrameworkName: framework.ExtractedData.FrameworkName,
        FrameworkDescription: framework.ExtractedData.FrameworkDescription,
        Category: framework.ExtractedData.Category,
        EffectiveDate: framework.ExtractedData.EffectiveDate,
        StartDate: framework.ExtractedData.StartDate,
        EndDate: framework.ExtractedData.EndDate,
        policies: framework.ExtractedData.policies ? framework.ExtractedData.policies.map(policy => {
          // Log each policy's category fields before mapping
          console.log(`Processing policy ${policy.PolicyId} for resubmission with category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure all policy fields are included, especially the category fields
          const mappedPolicy = {
            ...policy,
            PolicyId: policy.PolicyId,
            PolicyName: policy.PolicyName,
            PolicyDescription: policy.PolicyDescription,
            Status: policy.Status,
            StartDate: policy.StartDate,
            EndDate: policy.EndDate,
            Department: policy.Department,
            Objective: policy.Objective,
            Scope: policy.Scope,
            Applicability: policy.Applicability,
            Identifier: policy.Identifier,
            CoverageRate: policy.CoverageRate,
            // Explicitly include category fields with fallbacks
            PolicyType: policy.PolicyType || '',
            PolicyCategory: policy.PolicyCategory || '',
            PolicySubCategory: policy.PolicySubCategory || '',
            subpolicies: policy.subpolicies || []
          };
          
          return mappedPolicy;
        }) : []
      };
      
      console.log('Prepared resubmission data:', resubmitData);
      console.log('Policies in resubmission data:', resubmitData.policies);
      console.log('Number of policies:', resubmitData.policies.length);
      
      // Submit resubmission request
      console.log('Final resubmission data to be sent:', JSON.stringify(resubmitData));
      
      // Add explicit logging for policy category fields
      if (resubmitData.policies && resubmitData.policies.length > 0) {
        console.log('CRITICAL - Policy category fields in final resubmission data:');
        resubmitData.policies.forEach((policy, index) => {
          // Ensure policy category fields are properly set (not undefined)
          policy.PolicyType = policy.PolicyType || '';
          policy.PolicyCategory = policy.PolicyCategory || '';
          policy.PolicySubCategory = policy.PolicySubCategory || '';
          
          console.log(`Policy ${index} (${policy.PolicyId}):`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
        });
      }
      
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/resubmit-approval/`, resubmitData)
        .then(response => {
          console.log('Framework resubmitted successfully:', response.data);
          
          // Show version information in the alert
          PopupService.success(`Framework resubmitted for review! New version: ${response.data.Version}`, 'Framework Resubmitted');
          
          this.closeEditModal();
          this.fetchRejectedFrameworks();
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error data:', error.response ? error.response.data : 'No response data');
          this.handleError(error, 'resubmitting framework');
        });
    },
    
    formatFieldName(field) {
      // Convert camelCase or PascalCase to display format
      return field
        // Insert space before all uppercase letters
        .replace(/([A-Z])/g, ' $1')
        // Replace first char with uppercase
        .replace(/^./, str => str.toUpperCase())
        .trim();
    },
    
    approvePolicy(policy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for policy approval');
        return;
      }
      
      // Check if all subpolicies are approved first
      if (!this.canApprovePolicy(policy)) {
        PopupService.warning('All subpolicies must be approved before approving the policy', 'Subpolicies Not Approved');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Call backend endpoint
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/approve-reject/`, {
        approved: true
      })
        .then(response => {
          console.log('Policy approved successfully:', response.data);
          
          // Update policy status
          policy.Status = 'Approved';
          
          // Check if all policies are approved to update framework status
          if (this.areAllPoliciesApproved()) {
            this.selectedApproval.ExtractedData.Status = 'Ready for Final Approval';
          }
          
          PopupService.success('Policy approved successfully!', 'Policy Approved');
        })
        .catch(error => {
          this.handleError(error, 'approving policy');
        });
    },
    
    rejectPolicy(policy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for policy rejection');
        return;
      }
      
      this.currentRejectionType = 'policy';
      this.currentRejectionItem = policy;
      this.showRejectModal = true;
    },
    
    rejectSubpolicy(policy, subpolicy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for subpolicy rejection');
        return;
      }
      
      this.currentRejectionType = 'subpolicy';
      this.currentRejectionItem = { policy, subpolicy };
      this.showRejectModal = true;
    },
    
    canApprovePolicy(policy) {
      if (policy.Status === 'Approved') return false;
      if (policy.Status === 'Rejected') return false;
      
      // Policy with Ready for Approval status can be approved
      if (policy.Status === 'Ready for Approval') return true;
      
      // Check if all subpolicies are approved
      if (policy.subpolicies && policy.subpolicies.length > 0) {
        return policy.subpolicies.every(subpolicy => subpolicy.Status === 'Approved');
      }
      
      return true; // Policy with no subpolicies can be approved
    },
    
    approveSubpolicy(policy, subpolicy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for subpolicy approval');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Call backend endpoint
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/subpolicies/${subpolicy.SubPolicyId}/approve-reject/`, {
        approved: true
      })
        .then(response => {
          console.log('Subpolicy approved successfully:', response.data);
          
          // Update subpolicy status
          subpolicy.Status = 'Approved';
          
          // Check if all subpolicies in this policy are approved
          const allSubpoliciesApproved = policy.subpolicies && 
            policy.subpolicies.every(sp => sp.Status === 'Approved');
          
          if (allSubpoliciesApproved) {
            console.log(`All subpolicies in policy "${policy.PolicyName}" are now approved`);
            // Update the policy status to "Ready for Approval"
            policy.Status = 'Ready for Approval';
          }
          
          PopupService.success('Subpolicy approved successfully!', 'Subpolicy Approved');
        })
        .catch(error => {
          this.handleError(error, 'approving subpolicy');
        });
    },
    
    areAllSubpoliciesApproved(policy) {
      if (!policy.subpolicies || policy.subpolicies.length === 0) return true;
      return policy.subpolicies.every(subpolicy => subpolicy.Status === 'Approved');
    },
    
    areAllPoliciesApproved() {
      if (!this.selectedApproval.ExtractedData.policies) return false;
      return this.selectedApproval.ExtractedData.policies.every(policy => policy.Status === 'Approved');
    },
    
    getFrameworkApprovalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return 'Unknown';
      
      const policies = this.selectedApproval.ExtractedData.policies || [];
      if (policies.length === 0) return 'No Policies';
      
      const approvedCount = policies.filter(p => p.Status === 'Approved').length;
      const rejectedCount = policies.filter(p => p.Status === 'Rejected').length;
      const totalCount = policies.length;
      
      if (rejectedCount > 0) {
        return `Rejected (${rejectedCount}/${totalCount} policies rejected)`;
      } else if (approvedCount === totalCount) {
        return `Ready for Final Approval (${approvedCount}/${totalCount} policies approved)`;
      } else {
        return `Under Review (${approvedCount}/${totalCount} policies approved)`;
      }
    },
    
    canApproveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return false;
      if (this.selectedApproval.ApprovedNot !== null) return false; // Already approved/rejected
      
      // Check if all policies are approved
      return this.areAllPoliciesApproved();
    },
    
    approveEntireFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for entire framework approval');
        return;
      }
      
      if (!this.canApproveFramework()) {
        PopupService.warning('All policies must be approved before approving the framework', 'Policies Not Approved');
        return;
      }
      
      PopupService.confirm(
        'Are you sure you want to give final approval to this entire framework?',
        'Confirm Final Approval',
        () => {
          this.proceedWithFrameworkApproval();
        }
      );
    },
    
    proceedWithFrameworkApproval() {
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Call backend endpoint for final framework approval
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/approve-final/`)
        .then(response => {
          console.log('Framework approved successfully:', response.data);
          
          // Update framework status and store approval date
          this.selectedApproval.ExtractedData.Status = 'Approved';
          this.selectedApproval.ApprovedNot = true;
          
          // Store the approval date from the response
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
          
          // Update all policies and subpolicies to Approved status
          if (this.selectedApproval.ExtractedData.policies) {
            this.selectedApproval.ExtractedData.policies.forEach(policy => {
              policy.Status = 'Approved';
              
              if (policy.subpolicies) {
                policy.subpolicies.forEach(subpolicy => {
                  subpolicy.Status = 'Approved';
                });
              }
            });
          }
          
          PopupService.success('Framework approved successfully!', 'Framework Approved');
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          this.handleError(error, 'approving entire framework');
        });
    },
    
    // Update the existing submitReview method to use our helper method
    submitReview() {
      console.log('submitReview called with approval:', this.selectedApproval);
      if (this.selectedApproval && this.selectedApproval.ApprovedNot !== null) {
        console.log('Delegating to submitFrameworkReview with approval status:', this.selectedApproval.ApprovedNot);
        this.submitFrameworkReview(this.selectedApproval.ApprovedNot);
      } else {
        console.error('Cannot submit review - no approval or approval status set');
      }
    },
    
    // Helper method to validate framework data before submission
    validateFrameworkData(framework) {
      const validationErrors = [];
      
      // Check required framework fields
      if (!framework.ExtractedData.FrameworkName) {
        validationErrors.push('Framework Name is required');
      }
      
      if (!framework.ExtractedData.FrameworkDescription) {
        validationErrors.push('Framework Description is required');
      }
      
      // Check policies if they exist
      if (framework.ExtractedData.policies && framework.ExtractedData.policies.length > 0) {
        framework.ExtractedData.policies.forEach((policy, index) => {
          if (!policy.PolicyName) {
            validationErrors.push(`Policy #${index + 1} is missing a name`);
          }
          
          // Log policy category fields to help with debugging
          console.log(`Validating policy #${index + 1} category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Check subpolicies if they exist
          if (policy.subpolicies && policy.subpolicies.length > 0) {
            policy.subpolicies.forEach((subpolicy, subIndex) => {
              if (!subpolicy.SubPolicyName) {
                validationErrors.push(`Subpolicy #${subIndex + 1} in Policy "${policy.PolicyName || `#${index + 1}`}" is missing a name`);
              }
            });
          }
        });
      }
      
      return validationErrors;
    },
    
    fetchPolicyTypes() {
      console.log('Fetching policy categories...');
      axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          console.log('Policy categories response:', response.data);
          // Store the raw categories data
          this.policyCategories = response.data;
          
          // Create a structured map for easier filtering
          const typeMap = {};
          
          // Process the categories into a nested structure
          response.data.forEach(category => {
            if (!typeMap[category.PolicyType]) {
              typeMap[category.PolicyType] = {
                categories: {}
              };
            }
            
            if (!typeMap[category.PolicyType].categories[category.PolicyCategory]) {
              typeMap[category.PolicyType].categories[category.PolicyCategory] = {
                subCategories: []
              };
            }
            
            typeMap[category.PolicyType].categories[category.PolicyCategory].subCategories.push(
              category.PolicySubCategory
            );
          });
          
          this.policyCategoriesMap = typeMap;
          console.log('Processed policy categories map:', this.policyCategoriesMap);
        })
        .catch(error => {
          console.error('Error fetching policy categories:', error);
        });
    },
    
    // Helper method to initialize or update policy category fields
    initializePolicyCategoryFields(policy) {
      console.log(`Initializing policy category fields for policy: ${policy.PolicyId || 'New Policy'}`);
      
      // Log current values
      console.log('Current policy category fields:', {
        PolicyType: policy.PolicyType,
        PolicyCategory: policy.PolicyCategory,
        PolicySubCategory: policy.PolicySubCategory
      });
      
      // If policy type changes, reset category and subcategory
      this.$watch(() => policy.PolicyType, (newType, oldType) => {
        if (newType !== oldType) {
          console.log(`Policy type changed from ${oldType} to ${newType}, resetting category and subcategory`);
          policy.PolicyCategory = '';
          policy.PolicySubCategory = '';
        }
      });
      
      // If policy category changes, reset subcategory
      this.$watch(() => policy.PolicyCategory, (newCategory, oldCategory) => {
        if (newCategory !== oldCategory) {
          console.log(`Policy category changed from ${oldCategory} to ${newCategory}, resetting subcategory`);
          policy.PolicySubCategory = '';
        }
      });
      
      return policy;
    },
    
    // Handle policy type change
    handlePolicyTypeChange(policy) {
      console.log(`Policy type changed to: ${policy.PolicyType}`);
      // Reset dependent fields when type changes
      policy.PolicyCategory = '';
      policy.PolicySubCategory = '';
    },
    
    // Handle policy category change
    handlePolicyCategoryChange(policy) {
      console.log(`Policy category changed to: ${policy.PolicyCategory}`);
      // Reset subcategory when category changes
      policy.PolicySubCategory = '';
    },
    
    // Get action buttons based on framework status
    getActionButtons(framework, status) {
      switch (status) {
        case 'Under Review':
          return '<span class="action-text review-approve">Review & Approve</span>';
        case 'Approved':
          return '<span class="action-text">View Details</span>';
        case 'Rejected':
          return '<span class="action-text edit-resubmit">Edit & Resubmit</span>';
        default:
          return '<span class="action-text">View Details</span>';
      }
    },
    
    // Transform framework data for table display
    transformFrameworkForTable(framework) {
      const status = this.getFrameworkStatus(framework);
      const isNew = this.isNewFramework(framework);
      
      return {
        incidentId: framework.FrameworkId || framework.ApprovalId,
        frameworkId: this.getFrameworkId(framework),
        frameworkName: framework.ExtractedData?.FrameworkName || 'Unnamed Framework',
        category: framework.ExtractedData?.Category || 'No Category',
        createdBy: framework.ExtractedData?.CreatedByName || 'System',
        createdDate: this.formatDate(framework.ExtractedData?.CreatedByDate || framework.created_at),
        version: framework.version || 'u1',
        status: this.getStatusBadge(status, isNew),
        criticality: this.getCriticalityBadge(framework),
        priority: this.getPriorityBadge(framework),
        actions: this.getActionButtons(framework, status),
        // Include the original framework object for proper event handling
        originalFramework: framework
      };
    },
    
    // Get framework status
    getFrameworkStatus(framework) {
      if (framework.ApprovedNot === true || framework.ExtractedData?.Status === 'Approved') {
        return 'Approved';
      } else if (framework.ApprovedNot === false || framework.ExtractedData?.Status === 'Rejected') {
        return 'Rejected';
      } else {
        return 'Under Review';
      }
    },
    
    // Get status badge HTML
    getStatusBadge(status, isNew = false) {
      let badgeClass = '';
      let icon = '';
      
      switch (status) {
        case 'Approved':
          badgeClass = 'status-approved';
          icon = '<i class="fas fa-check-circle"></i>';
          break;
        case 'Rejected':
          badgeClass = 'status-rejected';
          icon = '<i class="fas fa-times-circle"></i>';
          break;
        case 'Under Review':
        default:
          badgeClass = 'status-pending';
          icon = '<i class="fas fa-clock"></i>';
          break;
      }
      
      const newBadge = isNew ? '<span class="new-badge">NEW</span>' : '';
      
      return `<span class="status-badge ${badgeClass}">${icon} ${status}</span>${newBadge}`;
    },
    
    // Get criticality badge (based on framework type or category)
    getCriticalityBadge(framework) {
      const category = framework.ExtractedData?.Category?.toLowerCase() || '';
      
      if (category.includes('critical') || category.includes('high')) {
        return '<span class="criticality-badge critical">Critical</span>';
      } else if (category.includes('medium') || category.includes('moderate')) {
        return '<span class="criticality-badge medium">Medium</span>';
      } else {
        return '<span class="criticality-badge low">Low</span>';
      }
    },
    
    // Get priority badge (based on creation date - newer items are higher priority)
    getPriorityBadge(framework) {
      const createdDate = new Date(framework.ExtractedData?.CreatedByDate || framework.created_at);
      const now = new Date();
      const daysDiff = Math.floor((now - createdDate) / (1000 * 60 * 60 * 24));
      
      if (daysDiff <= 1) {
        return '<span class="priority-badge high">High</span>';
      } else if (daysDiff <= 3) {
        return '<span class="priority-badge medium">Medium</span>';
      } else {
        return '<span class="priority-badge low">Low</span>';
      }
    },
    
    // Action methods for table buttons
    approveFrameworkFromTable(frameworkId) {
      const framework = this.findFrameworkById(frameworkId);
      if (framework) {
        this.selectedApproval = framework;
        this.approveFramework();
      }
    },
    
    rejectFrameworkFromTable(frameworkId) {
      const framework = this.findFrameworkById(frameworkId);
      if (framework) {
        this.selectedApproval = framework;
        this.rejectFramework();
      }
    },
    
    openApprovalDetailsFromTable(frameworkId) {
      const framework = this.findFrameworkById(frameworkId);
      if (framework) {
        this.openApprovalDetails(framework);
      }
    },
    
    openRejectedItemFromTable(frameworkId) {
      const framework = this.findFrameworkById(frameworkId);
      if (framework) {
        this.openRejectedItem(framework);
      }
    },
    
    downloadFramework(frameworkId) {
      // Implement framework download functionality
      console.log('Downloading framework:', frameworkId);
      PopupService.info('Download functionality will be implemented soon.', 'Download');
    },
    
    findFrameworkById(frameworkId) {
      return this.approvals.find(framework => 
        this.getFrameworkId(framework) === frameworkId
      );
    },
    
    // Toggle section expansion
    toggleSection(sectionName) {
      this.sectionExpansion[sectionName] = !this.sectionExpansion[sectionName];
    },
    
    // Handle task click from CollapsibleTable
    handleTaskClick(task) {
      // Get the original framework object from the task
      const framework = task.originalFramework;
      if (!framework) {
        console.error('No framework data found in task:', task);
        return;
      }
      
      // Determine the action based on framework status
      const status = this.getFrameworkStatus(framework);
      
      switch (status) {
        case 'Under Review':
          // For pending frameworks, open the approval details modal
          this.openApprovalDetails(framework);
          break;
        case 'Approved':
          // For approved frameworks, open the approval details modal to view
          this.openApprovalDetails(framework);
          break;
        case 'Rejected':
          // For rejected frameworks, open the edit modal
          this.openRejectedItem(framework);
          break;
        default:
          // Default to opening approval details
          this.openApprovalDetails(framework);
          break;
      }
    },
    
    // Handle rejected framework table row selection
    handleRejectedFrameworkSelect({ row, selected }) {
      console.log('Rejected framework selected:', row, selected);
    },
    
    // Transform rejected framework data for table display
    transformRejectedFrameworkForTable(framework) {
      const status = 'Rejected';
      const isNew = this.isNewFramework(framework);
      
      return {
        FrameworkId: framework.FrameworkId || framework.ApprovalId,
        frameworkId: this.getFrameworkId(framework),
        frameworkName: framework.ExtractedData?.FrameworkName || 'Unnamed Framework',
        category: framework.ExtractedData?.Category || 'No Category',
        createdBy: framework.ExtractedData?.CreatedByName || 'System',
        createdDate: this.formatDate(framework.ExtractedData?.CreatedByDate || framework.created_at),
        version: framework.version || 'u1',
        status: this.getStatusBadge(status, isNew),
        rejectionReason: this.formatRejectionReason(framework.rejection_reason),
        // Include the original framework object for proper event handling
        originalFramework: framework
      };
    },
    
    // Format rejection reason for table display
    formatRejectionReason(reason) {
      if (!reason) return 'No reason provided';
      
      // Truncate long reasons and add ellipsis
      if (reason.length > 50) {
        return reason.substring(0, 50) + '...';
      }
      
      return reason;
    },
  },
  computed: {
    pendingApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === false).length;
    },
    sortedFrameworks() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    },
    // Frameworks organized by status
    pendingFrameworks() {
      return this.sortedFrameworks.filter(framework => 
        framework.ApprovedNot === null || 
        framework.ExtractedData?.Status === 'Under Review'
      );
    },
    approvedFrameworks() {
      return this.sortedFrameworks.filter(framework => 
        framework.ApprovedNot === true || 
        framework.ExtractedData?.Status === 'Approved'
      );
    },
    rejectedFrameworksForTable() {
      return this.sortedFrameworks.filter(framework => 
        framework.ApprovedNot === false || 
        framework.ExtractedData?.Status === 'Rejected'
      );
    },
    // Section configurations for CollapsibleTable
    pendingSectionConfig() {
      return {
        name: 'Pending Review',
        statusClass: 'pending',
        tasks: this.pendingFrameworks.map(framework => this.transformFrameworkForTable(framework))
      };
    },
    approvedSectionConfig() {
      return {
        name: 'Approved',
        statusClass: 'completed',
        tasks: this.approvedFrameworks.map(framework => this.transformFrameworkForTable(framework))
      };
    },
    rejectedSectionConfig() {
      return {
        name: 'Rejected',
        statusClass: 'rejected',
        tasks: this.rejectedFrameworksForTable.map(framework => this.transformFrameworkForTable(framework))
      };
    },
    policyTypeOptions() {
      // Get unique policy types from the structured map
      return Object.keys(this.policyCategoriesMap);
    },
    filteredPolicyCategories() {
      return (policyType) => {
        if (!policyType || !this.policyCategoriesMap[policyType]) return [];
        // Get categories for the selected policy type
        return Object.keys(this.policyCategoriesMap[policyType].categories);
      };
    },
    filteredPolicySubCategories() {
      return (policyType, policyCategory) => {
        if (!policyType || !policyCategory || 
            !this.policyCategoriesMap[policyType] || 
            !this.policyCategoriesMap[policyType].categories[policyCategory]) {
          return [];
        }
        // Get subcategories for the selected policy type and category
        return this.policyCategoriesMap[policyType].categories[policyCategory].subCategories;
      };
    },
  },
}
</script>

<style scoped>
@import './FrameworkApprover.css';
</style> 