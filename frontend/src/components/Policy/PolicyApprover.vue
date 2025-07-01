<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Policy Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        
      </div>
    </div>

    <!-- Performance Summary Cards for Policy Approver -->
    <div class="performance-summary">
      <!-- Loading state -->
      <div v-if="isLoading" class="loading-message">
        <i class="fas fa-spinner fa-spin"></i>
        <span>Loading approval data...</span>
      </div>
      
      <!-- Error state -->
      <div v-else-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="refreshData" class="retry-btn">Retry</button>
      </div>
      
      <!-- Normal state -->
      <template v-else>
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
      </template>
    </div>

    <!-- Add this after the performance-summary div -->
    <div class="approvals-list">
      <h3>My Approval Tasks</h3>
      
      <!-- Collapsible Tables for different statuses -->
      <div class="approval-tables-container">
        <!-- Pending Approvals Table -->
        <div v-if="actualPolicyCounts.pending > 0" class="approval-section">
          <CollapsibleTable
            :section-config="pendingSectionConfig"
            :table-headers="tableHeaders"
            :is-expanded="pendingExpanded"
            @task-click="handleTaskClick"
            @toggle="togglePendingSection"
          />
          <!-- Pagination for Pending -->
          <div class="pagination-controls" v-if="pagination.pending.totalPages > 1">
            <button 
              @click="prevPage('pending')" 
              :disabled="pagination.pending.currentPage === 1"
              class="pagination-btn"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            
            <span class="pagination-info">
              Page {{ pagination.pending.currentPage }} of {{ pagination.pending.totalPages }}
              (Showing {{ pendingApprovals.length }} of {{ actualPolicyCounts.pending }} total)
            </span>
            
            <button 
              @click="nextPage('pending')" 
              :disabled="pagination.pending.currentPage === pagination.pending.totalPages"
              class="pagination-btn"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
        
        <!-- Approved Approvals Table -->
        <div v-if="actualPolicyCounts.approved > 0" class="approval-section">
          <CollapsibleTable
            :section-config="approvedSectionConfig"
            :table-headers="tableHeaders"
            :is-expanded="approvedExpanded"
            @task-click="handleTaskClick"
            @toggle="toggleApprovedSection"
          />
          <!-- Pagination for Approved -->
          <div class="pagination-controls" v-if="pagination.approved.totalPages > 1">
            <button 
              @click="prevPage('approved')" 
              :disabled="pagination.approved.currentPage === 1"
              class="pagination-btn"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            
            <span class="pagination-info">
              Page {{ pagination.approved.currentPage }} of {{ pagination.approved.totalPages }}
              (Showing {{ approvedApprovals.length }} of {{ actualPolicyCounts.approved }} total)
            </span>
            
            <button 
              @click="nextPage('approved')" 
              :disabled="pagination.approved.currentPage === pagination.approved.totalPages"
              class="pagination-btn"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
        
        <!-- Rejected Approvals Table -->
        <div v-if="actualPolicyCounts.rejected > 0" class="approval-section">
          <CollapsibleTable
            :section-config="rejectedSectionConfig"
            :table-headers="tableHeaders"
            :is-expanded="rejectedExpanded"
            @task-click="handleTaskClick"
            @toggle="toggleRejectedSection"
          />
          <!-- Pagination for Rejected -->
          <div class="pagination-controls" v-if="pagination.rejected.totalPages > 1">
            <button 
              @click="prevPage('rejected')" 
              :disabled="pagination.rejected.currentPage === 1"
              class="pagination-btn"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            
            <span class="pagination-info">
              Page {{ pagination.rejected.currentPage }} of {{ pagination.rejected.totalPages }}
              (Showing {{ rejectedApprovals.length }} of {{ actualPolicyCounts.rejected }} total)
            </span>
            
            <button 
              @click="nextPage('rejected')" 
              :disabled="pagination.rejected.currentPage === pagination.rejected.totalPages"
              class="pagination-btn"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
        
        <!-- No approvals message -->
        <div v-if="actualPolicyCounts.pending === 0 && actualPolicyCounts.approved === 0 && actualPolicyCounts.rejected === 0" class="no-approvals-message">
          <div class="no-approvals-content">
            <i class="fas fa-inbox"></i>
            <h4>No Policies Found</h4>
            <p>There are no policies in the system at the moment.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Policy/Compliance Details Section (New Inline Section) -->
    <div v-if="showDetails && selectedApproval" class="policy-details-section">
      <div class="policy-details-content">
        <div class="details-header">
        <h3>
          <span class="detail-type-indicator">
            {{ isComplianceApproval ? 'Compliance' : 'Policy' }}
          </span> 
          Details: {{ getPolicyId(selectedApproval) }}
          <span class="version-pill">Version: {{ selectedApproval.version || 'u1' }}</span>
          <span v-if="selectedApproval.showingApprovedOnly" class="approved-only-badge">
            Showing Approved Only
          </span>
        </h3>
          <button class="back-btn" @click="closeApprovalDetails">
            <i class="fas fa-arrow-left"></i> Back to Tasks
          </button>
        </div>
        
        <!-- Add version history section -->
        <div class="version-history" v-if="selectedApproval.ExtractedData">
          <div class="version-info">
            <div class="version-label">Current Version:</div>
            <div class="version-value">{{ selectedApproval.version || 'u1' }}</div>
          </div>
          <div v-if="selectedApproval.ExtractedData.subpolicies && selectedApproval.ExtractedData.subpolicies.length > 0" 
               class="subpolicies-versions">
            <h4>Subpolicies Versions:</h4>
            <ul class="version-list">
              <li v-for="sub in selectedApproval.ExtractedData.subpolicies" :key="sub.SubPolicyId">
                <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                <span class="version-tag">v{{ sub.version || 'u1' }}</span>
                <span v-if="sub.resubmitted" class="resubmitted-tag">Resubmitted</span>
              </li>
            </ul>
          </div>
        </div>
        
        <!-- Policy/Compliance Approval Section -->
        <div class="policy-approval-section">
          <h4>{{ isComplianceApproval ? 'Compliance' : 'Policy' }} Approval</h4>
          
          <!-- Add policy status indicator -->
          <div class="policy-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.dbStatus === 'Approved' || selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.dbStatus === 'Rejected' || selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': !(['Approved', 'Rejected'].includes(selectedApproval.dbStatus)) && selectedApproval.ApprovedNot === null && !(['Approved', 'Rejected'].includes(selectedApproval.ExtractedData?.Status))
            }">
              {{ selectedApproval.dbStatus === 'Approved' || selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.dbStatus === 'Rejected' || selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
          </div>
          
          <div class="policy-actions">
            <button class="submit-btn" @click="submitReview()" data-action="submit-policy-review">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
          
          <!-- Add this section to show policy approval status - hide when already showing in the indicator -->
          <div v-if="approvalStatus && 
                    !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved') && 
                    !(selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected')" 
               class="policy-approval-status">
            <div class="status-container">
              <div class="status-label">Status:</div>
              <div class="status-value" :class="{
                'approved': approvalStatus.approved === true,
                'rejected': approvalStatus.approved === false,
                'pending': approvalStatus.approved === null
              }">
                {{ approvalStatus.approved === true ? 'Approved' : 
                   approvalStatus.approved === false ? 'Rejected' : 'Pending' }}
              </div>
            </div>
            
            <!-- Show approved date if approved -->
            <div v-if="approvalStatus.approved === true && selectedApproval.ApprovedDate" class="policy-approved-date">
              <div class="date-label">Approved Date:</div>
              <div class="date-value">{{ formatDate(selectedApproval.ApprovedDate) }}</div>
            </div>
            
            <!-- Show remarks if rejected -->
            <div v-if="approvalStatus.approved === false && 
                      approvalStatus.remarks" class="policy-rejection-remarks">
              <div class="remarks-label">Rejection Reason:</div>
              <div class="remarks-value">{{ approvalStatus.remarks }}</div>
            </div>
          </div>
        </div>
        
        <!-- Display details based on type -->
        <div v-if="selectedApproval.ExtractedData">
          <!-- For compliance approvals -->
          <div v-if="isComplianceApproval" class="compliance-details">
            <div class="compliance-detail-row">
              <strong>Description:</strong> <span>{{ selectedApproval.ExtractedData.ComplianceItemDescription }}</span>
            </div>
            <div class="compliance-detail-row">
              <strong>Criticality:</strong> <span>{{ selectedApproval.ExtractedData.Criticality }}</span>
            </div>
            <div class="compliance-detail-row">
              <strong>Impact:</strong> <span>{{ selectedApproval.ExtractedData.Impact }}</span>
            </div>
            <div class="compliance-detail-row">
              <strong>Probability:</strong> <span>{{ selectedApproval.ExtractedData.Probability }}</span>
            </div>
            <div class="compliance-detail-row">
              <strong>Mitigation:</strong> <span>{{ selectedApproval.ExtractedData.mitigation }}</span>
            </div>
            <div class="policy-actions">
              <button class="approve-btn" @click="approveCompliance()">Approve</button>
              <button class="reject-btn" @click="rejectCompliance()">Reject</button>
            </div>
          </div>
          
          <!-- For policy approvals (existing code) -->
          <div v-else v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="policy-detail-row">
            <template v-if="key !== 'subpolicies' && key !== 'policy_approval'">
              <strong>{{ key }}:</strong> <span>{{ value }}</span>
            </template>
            
            <!-- Subpolicies Section -->
            <template v-if="key === 'subpolicies' && Array.isArray(value)">
              <h4>Subpolicies</h4>
              <ul v-if="value && value.length">
                <li v-for="sub in value" :key="sub.Identifier" class="subpolicy-status">
                  <div>
                    <span class="subpolicy-id">{{ sub.Identifier }}</span> :
                    <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                    <span class="item-type-badge subpolicy-badge">Subpolicy</span>
                    <span
                      class="badge"
                      :class="{
                        approved: sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        rejected: sub.approval?.approved === false && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        pending: sub.approval?.approved === null && !sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        resubmitted: sub.approval?.approved === null && sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved')
                      }"
                    >
                      {{
                        (sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'))
                          ? 'Approved'
                          : sub.approval?.approved === false
                          ? 'Rejected'
                          : sub.resubmitted
                          ? 'Resubmitted'
                          : 'Pending'
                      }}
                    </span>
                  </div>
                  <div><strong>Description:</strong> {{ sub.Description }}</div>
                  <div><strong>Control:</strong> {{ sub.Control }}</div>
                  <div v-if="sub.approval?.approved === false">
                    <strong>Reason:</strong> {{ sub.approval?.remarks }}
                  </div>
                  <!-- Add these buttons inside the subpolicies view, under the approval buttons -->
                  <div class="subpolicy-actions">
                    <template v-if="isReviewer">
                      <!-- Show approve/reject buttons for reviewer -->
                      <button 
                        v-if="sub.Status === 'Under Review' || !sub.Status"
                        @click="approveSubpolicy(sub)" 
                        class="approve-button"
                      >
                        Approve
                      </button>
                      <button 
                        v-if="sub.Status === 'Under Review' || !sub.Status"
                        @click="rejectSubpolicy(sub)" 
                        class="reject-button"
                      >
                        Reject
                      </button>
                    </template>
                    
                    <!-- For users (not reviewers), add edit button for rejected subpolicies -->
                    <template v-else>
                      <button 
                        v-if="sub.Status === 'Rejected'"
                        @click="openEditSubpolicyModal(sub)" 
                        class="edit-button"
                      >
                        Edit & Resubmit
                      </button>
                    </template>
                  </div>
                </li>
              </ul>
            </template>
          </div>
        </div>

        <!-- Add this inside the policy-details-content div -->
        <div v-if="selectedApproval && selectedApproval.PolicyId" class="policy-detail-row">
          <strong>Policy ID:</strong> <span>{{ getPolicyId(selectedApproval) }}</span>
        </div>
      </div>
    </div>
      
    <!-- Policy/Compliance Details Modal/Section -->
    <!-- Original modal section removed to fix nested-comment parsing error -->

    <!-- GRC Tasks Card -->

    <!-- Rejected Policies & Compliances List -->
    <div class="rejected-approvals-list" v-if="rejectedPolicies.length">
      <h3>Rejected Policies & Compliances (Edit & Resubmit)</h3>
      
      <!-- Dynamic Table for Rejected Items -->
      <DynamicTable
        :data="rejectedPoliciesTableData"
        :columns="rejectedPoliciesColumns"
        :show-actions="true"
        :show-pagination="true"
        :default-page-size="10"
        unique-key="ApprovalId"
        @row-action="handleRejectedItemAction"
      >
        <template #actions="{ row }">
          <button 
            class="view-details-btn"
            @click="openRejectedItem(row.originalPolicy)"
            title="View Details"
          >
            <i class="fas fa-eye"></i>
            View
          </button>
        </template>
      </DynamicTable>
    </div>

    <!-- Edit Modal for Rejected Compliance -->
    <div v-if="showEditComplianceModal && editingCompliance" class="edit-policy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Compliance: {{ getPolicyId(editingCompliance) }}</h3>
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
          <label>Impact:</label>
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

    <!-- Edit Modal for Rejected Policy -->
    <div v-if="showEditModal && editingPolicy" class="edit-policy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Policy: {{ getPolicyId(editingPolicy) }}</h3>
        <button class="close-btn" @click="closeEditModal">Close</button>
        
        <!-- Main policy fields -->
        <div>
          <label>Scope:</label>
          <input v-model="editingPolicy.ExtractedData.Scope" />
        </div>
        <div>
          <label>Objective:</label>
          <input v-model="editingPolicy.ExtractedData.Objective" />
        </div>
        
        <!-- Policy Category fields -->
        <div>
          <label>Policy Type:</label>
          <select v-model="editingPolicy.ExtractedData.PolicyType" class="form-control" @change="handlePolicyTypeChange(editingPolicy)">
            <option value="">Select Type</option>
            <option v-for="type in policyTypeOptions" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
        <div>
          <label>Policy Category:</label>
          <select v-model="editingPolicy.ExtractedData.PolicyCategory" class="form-control" @change="handlePolicyCategoryChange(editingPolicy)">
            <option value="">Select Category</option>
            <option v-for="category in filteredPolicyCategories(editingPolicy.ExtractedData.PolicyType)" :key="category" :value="category">{{ category }}</option>
          </select>
        </div>
        <div>
          <label>Policy Sub Category:</label>
          <select v-model="editingPolicy.ExtractedData.PolicySubCategory" class="form-control">
            <option value="">Select Sub Category</option>
            <option v-for="subCategory in filteredPolicySubCategories(editingPolicy.ExtractedData.PolicyType, editingPolicy.ExtractedData.PolicyCategory)" :key="subCategory" :value="subCategory">{{ subCategory }}</option>
          </select>
        </div>
        
        <!-- Rejected Subpolicies Section -->
        <div class="edit-subpolicy-section" v-if="hasRejectedSubpolicies">
          <h4>Rejected Subpolicies</h4>
          
          <div v-for="sub in rejectedSubpoliciesInPolicy" :key="sub.Identifier" class="subpolicy-edit-item">
            <div class="subpolicy-edit-header">
              <span>{{ sub.Identifier }}: {{ sub.SubPolicyName }}</span>
              <span class="subpolicy-badge">Rejected</span>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Name:</label>
              <input v-model="sub.SubPolicyName" />
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Description:</label>
              <textarea v-model="sub.Description"></textarea>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Control:</label>
              <textarea v-model="sub.Control"></textarea>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Rejection Reason:</label>
              <div class="rejection-reason">{{ sub.approval?.remarks }}</div>
            </div>
          </div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitPolicy(editingPolicy)">Resubmit for Review</button>
      </div>
    </div>

    <!-- Edit Modal for Rejected Subpolicy -->
    <div v-if="showEditSubpolicyModal" class="modal">
      <div class="modal-content edit-modal">
        <span class="close" @click="closeEditSubpolicyModal">&times;</span>
        <h2>Edit Rejected Subpolicy
          <span v-if="editingSubpolicy && (editingSubpolicy.Status === 'Rejected' || editingSubpolicy.approval?.approved === false)" 
                class="version-tag reviewer-version">
            Version: {{ editingSubpolicy.reviewerVersion || 'R1' }}
          </span>
        </h2>
        <div v-if="editingSubpolicy">
          <div class="form-group">
            <label>Subpolicy Name:</label>
            <input type="text" v-model="editingSubpolicy.SubPolicyName" disabled />
          </div>
          <div class="form-group">
            <label>Identifier:</label>
            <input type="text" v-model="editingSubpolicy.Identifier" disabled />
          </div>
          
          <!-- Add this prominent rejection reason section -->
          <div v-if="editingSubpolicy.approval && editingSubpolicy.approval.remarks" class="rejection-reason-container">
            <div class="rejection-reason-header">
              <i class="fas fa-exclamation-triangle"></i> Rejection Reason
            </div>
            <div class="rejection-reason-content">
              {{ editingSubpolicy.approval.remarks }}
            </div>
          </div>
          
          <div class="form-group">
            <label>Description:</label>
            <textarea v-model="editingSubpolicy.Description" @input="trackChanges"></textarea>
          </div>
          <div class="form-group">
            <label>Control:</label>
            <textarea v-model="editingSubpolicy.Control" @input="trackChanges"></textarea>
          </div>
          
          <div v-if="hasChanges" class="changes-summary">
            <div class="changes-header">
              <i class="fas fa-exclamation-circle"></i> Changes detected
            </div>
            <div class="changes-content">
              <div v-if="editingSubpolicy.Description !== editingSubpolicy.originalDescription" class="change-item">
                Description has been modified
              </div>
              <div v-if="editingSubpolicy.Control !== editingSubpolicy.originalControl" class="change-item">
                Control has been modified
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              class="resubmit-btn" 
              @click="resubmitSubpolicy()" 
              :disabled="!hasChanges"
            >
              {{ hasChanges ? 'Resubmit with Changes' : 'Make changes to resubmit' }}
            </button>
            <button class="cancel-btn" @click="closeEditSubpolicyModal">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subpolicies Modal -->
    <div v-if="showSubpoliciesModal && selectedPolicyForSubpolicies" class="subpolicies-modal">
      <div class="subpolicies-modal-content">
        <h3>
          <span v-if="isReviewer">Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
          <span v-else>Edit Rejected Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
          
          <!-- Show appropriate version based on status -->
          <span v-if="selectedPolicyForSubpolicies.ApprovedNot === false || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Rejected'"
                class="version-pill reviewer-version">
            Version: {{ selectedPolicyForSubpolicies.reviewerVersion || 'R1' }}
          </span>
          <span v-else class="version-pill">
            Version: {{ selectedPolicyForSubpolicies.version || 'u1' }}
          </span>
        </h3>
        <button class="close-btn" @click="closeSubpoliciesModal">Close</button>
        
        <!-- Filter to only show rejected subpolicies in user mode -->
        <div v-for="sub in filteredSubpolicies" :key="sub.Identifier" class="subpolicy-status" :class="{'resubmitted-item': sub.resubmitted}">
          <div class="subpolicy-header">
            <span class="subpolicy-id">{{ sub.Identifier }}</span>
            <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
            
            <!-- Show R version for rejected items, u version otherwise -->
            <span v-if="sub.Status === 'Rejected' || (sub.approval && sub.approval.approved === false)" 
                  class="version-tag reviewer-version">
              Version: {{ sub.reviewerVersion || 'R1' }}
            </span>
            <span v-else class="version-tag">
              Version: {{ sub.version || 'u1' }}
            </span>
          </div>

          <div class="subpolicy-content">
            <div><strong>Description:</strong> {{ sub.Description }}</div>
            <div><strong>Control:</strong> {{ sub.Control }}</div>
              
            <!-- Show rejection reason for rejected items -->
            <div v-if="sub.approval?.approved === false">
              <strong>Rejection Reason:</strong> {{ sub.approval?.remarks }}
            </div>
              
            <!-- Show edit history for resubmitted items -->
            <div v-if="sub.resubmitted && isReviewer" class="edit-history">
              <div class="edit-history-header">
                <i class="fas fa-history"></i> Resubmitted with Changes
              </div>
              <div class="edit-history-content">
                <div class="edit-field">
                  <div v-if="sub.previousVersion">
                    <div class="field-label">Original Description:</div>
                    <div class="field-previous">{{ sub.previousVersion.Description || 'Not available' }}</div>
                  </div>
                  <div class="field-current">
                    <div class="field-label">Updated Description:</div>
                    <div class="field-value">{{ sub.Description }}</div>
                  </div>
                </div>
                <div class="edit-field">
                  <div v-if="sub.previousVersion">
                    <div class="field-label">Original Control:</div>
                    <div class="field-previous">{{ sub.previousVersion.Control || 'Not available' }}</div>
                  </div>
                  <div class="field-current">
                    <div class="field-label">Updated Control:</div>
                    <div class="field-value">{{ sub.Control }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Show Approve/Reject buttons if pending and in reviewer mode -->
          <div v-if="isReviewer && (sub.approval?.approved === null || sub.approval?.approved === undefined)" class="subpolicy-actions">
            <button class="approve-btn" @click="approveSubpolicyFromModal(sub)">Approve</button>
            <button class="reject-btn" @click="rejectSubpolicyFromModal(sub)">Reject</button>
          </div>
          
          <!-- Edit form for rejected subpolicies -->
          <div v-if="sub.approval?.approved === false || sub.Status === 'Rejected'">
            <div v-if="sub.showEditForm">
              <!-- Inline edit form -->
              <div class="subpolicy-inline-edit">
                <h4>Edit Rejected Subpolicy
                  <span class="version-tag reviewer-version">Version: {{ sub.reviewerVersion || 'R1' }}</span>
                </h4>
                <div>
                  <label>Name:</label>
                  <input v-model="sub.SubPolicyName" disabled />
                </div>
                <div>
                  <label>Description:</label>
                  <textarea v-model="sub.Description"></textarea>
                </div>
                <div>
                  <label>Control:</label>
                  <textarea v-model="sub.Control"></textarea>
                </div>
                <div>
                  <label>Rejection Reason:</label>
                  <div class="rejection-reason">
                    {{ sub.approval && sub.approval.remarks ? sub.approval.remarks : 'No rejection reason provided' }}
                  </div>
                </div>
                <div class="subpolicy-edit-actions">
                  <button class="resubmit-btn" @click="resubmitSubpolicyDirect(sub)">Resubmit for Review</button>
                  <button v-if="isReviewer" class="cancel-btn" @click="hideEditFormInline(sub)">Cancel</button>
                </div>
              </div>
            </div>
            <button v-else class="edit-btn" @click="showEditFormInline(sub)">Edit & Resubmit</button>
          </div>
        </div>
      </div>
    </div>

    
    <!-- Pending Tasks Tab -->
    <!-- Popup Modal -->
    <PopupModal />

    <!-- Rejection Modal -->
    <div v-if="showRejectModal" class="reject-modal">
      <div class="reject-modal-content">
        <h4>Rejection Reason</h4>
        <p>Please provide a reason for rejecting {{ rejectingType === 'policy' ? 'the policy' : 'subpolicy ' + rejectingSubpolicy?.Identifier }}</p>
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
</template>

<script>
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CollapsibleTable from '@/components/CollapsibleTable.vue'
import DynamicTable from '@/components/DynamicTable.vue'

export default {
  name: 'PolicyApprover',
  components: {
    PopupModal,
    CollapsibleTable,
    DynamicTable
  },
  data() {
    return {
      approvals: [], // This will hold all policy approvals
      rejectedPolicies: [], // This will hold rejected policies
      rejectedSubpolicies: [], // This will hold rejected subpolicies specifically
      showDetails: false,
      selectedApproval: null,
      selectedPolicyForSubpolicies: null,
      rejectedPolicyToEdit: null,
      editingSubpolicy: null,
      editingPolicy: null,
      editingSubpolicyParent: null,
      userId: 2, // Default user id
      showSubpoliciesModal: false,
      showEditComplianceModal: false,
      editingCompliance: null,
      isReviewer: true, // Set based on user role, for testing
      activeTab: 'pending', // Track active tab
      policyCategories: [], // Store all policy categories
      policyCategoriesMap: {}, // Structured map of policy categories
      // CollapsibleTable expansion states
      pendingExpanded: true,
      approvedExpanded: false,
      rejectedExpanded: false,
      // Add loading state
      isLoading: false,
      // Add error state
      error: null,
      // Add actual policy counts from database
      actualPolicyCounts: {
        pending: 0,
        approved: 0,
        rejected: 0
      },
      // Add actual policies by status with pagination
      actualPolicies: {
        pending: [],
        approved: [],
        rejected: []
      },
      // Add pagination state
      pagination: {
        pending: { currentPage: 1, pageSize: 10, totalPages: 0 },
        approved: { currentPage: 1, pageSize: 10, totalPages: 0 },
        rejected: { currentPage: 1, pageSize: 10, totalPages: 0 }
      }
    }
  },
  mounted() {
    console.log('PolicyApprover component mounted');
    this.isLoading = true;
    
    Promise.all([
      this.fetchPolicyTypes(), // Fetch policy categories
      this.fetchPolicyCounts() // Fetch actual policy counts first
    ]).then(() => {
      // After getting counts, fetch the actual policies by status
      return this.fetchAllPoliciesByStatus();
    }).then(() => {
      console.log('All initial data loaded');
      this.isLoading = false;
      // Debug the data state after loading
      setTimeout(() => {
        this.debugDataState();
      }, 1000);
    }).catch(error => {
      console.error('Error loading initial data:', error);
      this.error = 'Failed to load data';
      this.isLoading = false;
    });
    
    // Also fetch rejected subpolicies if in user mode
    if (!this.isReviewer) {
      this.fetchRejectedSubpolicies();
    }
  },
  watch: {
    // Watch for changes in isReviewer and fetch appropriate data
    isReviewer(newVal) {
      if (newVal) {
        // If switched to reviewer mode
        this.fetchPolicies();
        this.fetchRejectedPolicies();
      } else {
        // If switched to user mode
        this.fetchRejectedSubpolicies();
      }
    }
  },
  methods: {
    // Update the method to fetch policies and policy approvals
    fetchPolicies() {
      console.log('Fetching policy approvals for reviewer...');
      // Fix the API endpoint URL - it was missing 'policy-approvals'
      return axios.get('http://localhost:8000/api/policy-approvals/reviewer/')
        .then(response => {
          console.log('Policy approvals response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let approvalsData;
          if (response.data.success && response.data.data) {
            approvalsData = response.data.data;
          } else if (Array.isArray(response.data)) {
            approvalsData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            this.approvals = []; // Set empty array as fallback
            return;
          }
          
          console.log('Processing approvals data:', approvalsData.length, 'items');
          
          if (!Array.isArray(approvalsData) || approvalsData.length === 0) {
            console.log('No policy approvals found');
            this.approvals = [];
            return;
          }
          
          // Create initial approvals array from policy approvals data
          const approvals = approvalsData.map(approval => {
            console.log('Processing approval:', approval.ApprovalId, 'PolicyId:', approval.PolicyId, 'ApprovedNot:', approval.ApprovedNot);
            return {
              ApprovalId: approval.ApprovalId,
              PolicyId: approval.PolicyId,
              ExtractedData: approval.ExtractedData || {},
              ApprovedNot: approval.ApprovedNot,
              ApprovedDate: approval.ApprovedDate,
              version: approval.Version || 'u1',
              UserId: approval.UserId,
              ReviewerId: approval.ReviewerId,
              dbStatus: null, // Will be populated from database table
              Identifier: approval.Identifier
            };
          });
          
          console.log('Created approvals array:', approvals.length, 'items');
          
          // Get policy IDs to fetch their direct status from database
          const policyIds = approvals
            .filter(approval => approval.PolicyId && approval.PolicyId !== null)
            .map(approval => approval.PolicyId);
          
          console.log('Policy IDs to fetch status for:', policyIds);
          
          if (policyIds.length > 0) {
            // Fetch the actual policy status from the database table for all policies
            const fetchPromises = policyIds.map(policyId => 
              axios.get(`http://localhost:8000/api/policies/${policyId}/`)
                .then(policyResponse => {
                  console.log(`Policy ${policyId} status:`, policyResponse.data.Status);
                  return {
                    policyId: policyId,
                    status: policyResponse.data.Status
                  };
                })
                .catch(error => {
                  console.error(`Error fetching policy ${policyId}:`, error);
                  return { policyId: policyId, status: 'Under Review' }; // Default status
                })
            );
            
            return Promise.all(fetchPromises)
              .then(policyStatuses => {
                console.log('Fetched policy statuses:', policyStatuses);
                
                // Update the approvals with database status
                policyStatuses.forEach(policyStatus => {
                  const approval = approvals.find(a => a.PolicyId === policyStatus.policyId);
                  
                  if (approval) {
                    approval.dbStatus = policyStatus.status;
                    
                    // Update ExtractedData Status as well to ensure consistency
                    if (approval.ExtractedData) {
                      approval.ExtractedData.Status = policyStatus.status;
                    }
                    
                    console.log(`Updated approval ${approval.ApprovalId} with status: ${policyStatus.status}`);
                  }
                });
                
                this.approvals = approvals;
                console.log('Final approvals with database status:', this.approvals);
                
                // Log counts for debugging
                console.log('Pending:', this.pendingApprovalsCount);
                console.log('Approved:', this.approvedApprovalsCount);
                console.log('Rejected:', this.rejectedApprovalsCount);
              })
              .catch(error => {
                console.error('Error updating policy statuses:', error);
                // Even if status fetch fails, still show the approvals
                this.approvals = approvals;
              });
          } else {
            console.log('No valid policy IDs found');
            this.approvals = approvals;
          }
        })
        .catch(error => {
          console.error('Error fetching policy approvals:', error);
          this.approvals = []; // Set empty array on error
          throw error; // Re-throw for Promise.all to catch
        });
    },
    // Remove the fetchLatestApprovalForPolicy method as it's causing errors
    
    openApprovalDetails(approval) {
      // Get the policy ID
      const policyId = this.getPolicyId(approval);

      // First, let's get the latest version information for this policy
      axios.get(`http://localhost:8000/api/policies/${policyId}/version/`)
        .then(versionResponse => {
          const policyVersion = versionResponse.data.version || 'u1';
          console.log(`Latest policy version: ${policyVersion}`);
          
          // Also fetch the policy's current database status
          axios.get(`http://localhost:8000/api/policies/${policyId}/`)
            .then(policyResponse => {
              const dbStatus = policyResponse.data.Status;
              console.log(`Policy database status: ${dbStatus}`);
              
              // Now fetch the latest policy approval with this version
              axios.get(`http://localhost:8000/api/policy-approvals/latest/${policyId}/`)
                .then(approvalResponse => {
                  console.log('Latest policy approval:', approvalResponse.data);
                  
                  // If we got data and it has ExtractedData, use it
                  if (approvalResponse.data && approvalResponse.data.ExtractedData) {
                    const latestApproval = approvalResponse.data;
                    
                    // Create a complete approval object with the latest data
                    const updatedApproval = {
                      ...approval,
                      ...latestApproval,
                      dbStatus: dbStatus,
                      version: policyVersion,
                      ExtractedData: latestApproval.ExtractedData
                    };
                    
                    // Update ExtractedData Status to match database status for consistency
                    if (updatedApproval.ExtractedData && dbStatus) {
                      updatedApproval.ExtractedData.Status = dbStatus;
                    }
                    
                    // Now get subpolicy versions if there are any
                    if (updatedApproval.ExtractedData && updatedApproval.ExtractedData.subpolicies && updatedApproval.ExtractedData.subpolicies.length > 0) {
                      console.log('Fetching versions for', updatedApproval.ExtractedData.subpolicies.length, 'subpolicies');
                      
                      const promises = updatedApproval.ExtractedData.subpolicies.map(sub => {
                        if (sub.SubPolicyId) {
                          return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/version/`)
                            .then(subVersionResponse => {
                              console.log(`Subpolicy ${sub.SubPolicyId} version:`, subVersionResponse.data.version);
                              sub.version = subVersionResponse.data.version || 'u1';
                              return sub;
                            })
                            .catch(err => {
                              console.error(`Error fetching version for subpolicy ${sub.SubPolicyId}:`, err);
                              sub.version = 'u1'; // Default fallback
                              return sub;
                            });
                        } else {
                          sub.version = 'u1'; // Default for subpolicies without ID
                          return Promise.resolve(sub);
                        }
                      });
                      
                      // Wait for all version fetching to complete
                      Promise.all(promises)
                        .then(updatedSubpolicies => {
                          updatedApproval.ExtractedData.subpolicies = updatedSubpolicies;
                          this.completeApprovalSelection(updatedApproval);
                        })
                        .catch(error => {
                          console.error('Error updating subpolicy versions:', error);
                          this.completeApprovalSelection(updatedApproval);
                        });
                    } else {
                      // No subpolicies to process
                      this.completeApprovalSelection(updatedApproval);
                    }
                  } else {
                    // If we couldn't get the latest approval data, fall back to using existing data with just the version updated
                    const updatedApproval = JSON.parse(JSON.stringify(approval));
                    updatedApproval.version = policyVersion;
                    updatedApproval.dbStatus = dbStatus;
                    
                    // Update ExtractedData Status to match database status for consistency
                    if (updatedApproval.ExtractedData && dbStatus) {
                      updatedApproval.ExtractedData.Status = dbStatus;
                    }
                    
                    this.processSubpolicyVersions(updatedApproval);
                  }
                })
                .catch(approvalError => {
                  console.error('Error fetching latest approval:', approvalError);
                  
                  // Fall back to just updating the version
                  const updatedApproval = JSON.parse(JSON.stringify(approval));
                  updatedApproval.version = policyVersion;
                  updatedApproval.dbStatus = dbStatus;
                  
                  // Update ExtractedData Status to match database status for consistency
                  if (updatedApproval.ExtractedData && dbStatus) {
                    updatedApproval.ExtractedData.Status = dbStatus;
                  }
                  
                  this.processSubpolicyVersions(updatedApproval);
                });
            })
            .catch(error => {
              console.error('Error fetching policy status:', error);
              
              // Fall back to just updating with version
              const updatedApproval = JSON.parse(JSON.stringify(approval));
              updatedApproval.version = policyVersion;
              
              this.processSubpolicyVersions(updatedApproval);
            });
        })
        .catch(error => {
          console.error('Error fetching policy version:', error);
          // Fall back to using the approval as-is
          this.completeApprovalSelection(approval);
        });
    },
    
    // Helper method to process subpolicy versions
    processSubpolicyVersions(approval) {
      // Get subpolicy versions if there are any
      if (approval.ExtractedData && approval.ExtractedData.subpolicies && approval.ExtractedData.subpolicies.length > 0) {
        console.log('Fetching versions for', approval.ExtractedData.subpolicies.length, 'subpolicies');
        
        const promises = approval.ExtractedData.subpolicies.map(sub => {
          if (sub.SubPolicyId) {
            return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/version/`)
              .then(subVersionResponse => {
                console.log(`Subpolicy ${sub.SubPolicyId} version:`, subVersionResponse.data.version);
                sub.version = subVersionResponse.data.version || 'u1';
                
                // Also fetch subpolicy status
                return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/`)
                  .then(subpolicyResponse => {
                    // Update the subpolicy status from database
                    if (subpolicyResponse.data && subpolicyResponse.data.Status) {
                      sub.Status = subpolicyResponse.data.Status;
                    }
                    return sub;
                  })
                  .catch(err => {
                    console.error(`Error fetching subpolicy status for ${sub.SubPolicyId}:`, err);
                    return sub;
                  });
              })
              .catch(err => {
                console.error(`Error fetching version for subpolicy ${sub.SubPolicyId}:`, err);
                sub.version = 'u1'; // Default fallback
                return sub;
              });
          } else {
            sub.version = 'u1'; // Default for subpolicies without ID
            return Promise.resolve(sub);
          }
        });
        
        // Wait for all version fetching to complete
        Promise.all(promises)
          .then(updatedSubpolicies => {
            approval.ExtractedData.subpolicies = updatedSubpolicies;
            this.completeApprovalSelection(approval);
          })
          .catch(error => {
            console.error('Error updating subpolicy versions:', error);
            this.completeApprovalSelection(approval);
          });
      } else {
        // No subpolicies to process
        this.completeApprovalSelection(approval);
      }
    },
    
    // Helper method to finish the approval selection process
    completeApprovalSelection(approval) {
      this.selectedApproval = approval;
      
      // If policy is approved, filter subpolicies to only show approved ones
      if (this.selectedApproval.ExtractedData && 
          (this.selectedApproval.ApprovedNot === true || this.selectedApproval.ExtractedData.Status === 'Approved') && 
          this.selectedApproval.ExtractedData.subpolicies) {
        
        // When a policy is approved, all its subpolicies should be treated as approved
        this.selectedApproval.ExtractedData.subpolicies = this.selectedApproval.ExtractedData.subpolicies.map(sub => {
          // Mark all subpolicies as approved when parent policy is approved
          if (!sub.approval) {
            sub.approval = {};
          }
          sub.approval.approved = true;
          sub.Status = 'Approved';
          return sub;
        });
        
        // Add a flag to indicate this is showing only accepted items
        this.selectedApproval.showingApprovedOnly = true;
      }
      
      this.showDetails = true;
    },
    // Update the refresh method
    refreshData() {
      console.log('Refreshing Policy Approver data...');
      
      // Reset data first
      this.actualPolicies = {
        pending: [],
        approved: [],
        rejected: []
      };
      
      // Reset pagination to first page
      this.pagination.pending.currentPage = 1;
      this.pagination.approved.currentPage = 1;
      this.pagination.rejected.currentPage = 1;
      
      // Show loading state
      this.isLoading = true;
      this.error = null;
      
      // Fetch all data
      Promise.all([
        this.fetchPolicyTypes(),
        this.fetchPolicyCounts()
      ]).then(() => {
        // After getting counts, fetch the actual policies by status
        return this.fetchAllPoliciesByStatus();
      }).then(() => {
        console.log('All data refreshed successfully');
        this.isLoading = false;
      }).catch(error => {
        console.error('Error refreshing data:', error);
        this.error = 'Failed to refresh data';
        this.isLoading = false;
      });
    },
    // Update the refresh approvals method
    refreshApprovals() {
      this.fetchPolicies();
    },
    // Update fetchRejectedPolicies to use policy table
    fetchRejectedPolicies() {
      console.log('Fetching rejected policies...');
      return axios.get('http://localhost:8000/api/policies/?status=Rejected')
        .then(response => {
          console.log('Rejected policies response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let rejectedData;
          if (response.data.success && response.data.data) {
            rejectedData = response.data.data;
          } else if (Array.isArray(response.data)) {
            rejectedData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          if (Array.isArray(rejectedData) && rejectedData.length > 0) {
            this.rejectedPolicies = rejectedData.map(policy => ({
              PolicyId: policy.PolicyId,
              ExtractedData: {
                type: 'policy',
                PolicyName: policy.PolicyName,
                CreatedByName: policy.CreatedByName,
                CreatedByDate: policy.CreatedByDate,
                Scope: policy.Scope,
                Status: policy.Status,
                Objective: policy.Objective,
                subpolicies: policy.subpolicies || []
              },
              ApprovedNot: false,
              main_policy_rejected: true
            }));
            console.log('Processed rejected policies:', this.rejectedPolicies.length);
          } else {
            console.log('No rejected policies found from API');
            // We'll check for policies with rejected subpolicies instead
            return this.fetchPoliciesWithRejectedSubpolicies();
          }
        })
        .catch(error => {
          console.error('Error fetching rejected policies:', error);
          throw error; // Re-throw for Promise.all to catch
        });
    },
    // Add a method to fetch policies that have rejected subpolicies
    fetchPoliciesWithRejectedSubpolicies() {
      console.log('Fetching policies with rejected subpolicies...');
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('All policies response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let policiesData;
          if (response.data.success && response.data.data) {
            policiesData = response.data.data;
          } else if (Array.isArray(response.data)) {
            policiesData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          console.log('Policies data length:', policiesData.length);
          if (Array.isArray(policiesData)) {
            // Filter policies that have at least one rejected subpolicy
            const policiesWithRejected = policiesData.filter(policy => 
              policy.subpolicies && 
              policy.subpolicies.some(sub => sub.Status === 'Rejected')
            );
            
            console.log('Found policies with rejected subpolicies:', policiesWithRejected.length);
            
            if (policiesWithRejected.length > 0) {
              this.rejectedPolicies = policiesWithRejected.map(policy => ({
                PolicyId: policy.PolicyId,
                ExtractedData: {
                  type: 'policy',
                  PolicyName: policy.PolicyName,
                  CreatedByName: policy.CreatedByName,
                  CreatedByDate: policy.CreatedByDate,
                  Scope: policy.Scope,
                  Status: policy.Status,
                  Objective: policy.Objective,
                  subpolicies: policy.subpolicies || []
                },
                ApprovedNot: policy.Status === 'Rejected' ? false : null,
                main_policy_rejected: policy.Status === 'Rejected'
              }));
            }
          }
      })
      .catch(error => {
          console.error('Error fetching policies with rejected subpolicies:', error);
      });
    },
    // Modify submitReview to update policy status
    submitReview() {
      if (!this.isComplianceApproval) {
        const policyId = this.selectedApproval.PolicyId;
        
        // Create the policy approval data
        const reviewData = {
          ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
          ApprovedNot: this.selectedApproval.ApprovedNot,
          UserId: this.userId,
          ReviewerId: this.userId
        };
        
        // First get the current version
        axios.get(`http://localhost:8000/api/policies/${policyId}/version/`)
          .then(versionResponse => {
            const currentVersion = versionResponse.data.version;
            console.log('Current version before submission:', currentVersion);
            
            // Add logic to check if any subpolicies are rejected
            const hasRejectedSubpolicies = this.selectedApproval.ExtractedData.subpolicies &&
              this.selectedApproval.ExtractedData.subpolicies.some(subpolicy => 
                subpolicy.Status === 'Rejected');
            
            if (this.reviewDecision === 'approve' && hasRejectedSubpolicies) {
              // Show warning
              this.$swal({
                title: 'Warning',
                text: 'One or more subpolicies are rejected. The policy will still be marked as rejected regardless of approval.',
                icon: 'warning',
                confirmButtonText: 'Continue'
              }).then(() => {
                // Continue with submission after warning
                this.submitPolicyReview(policyId, reviewData, currentVersion);
              });
            } else {
              // No rejected subpolicies, proceed normally
              this.submitPolicyReview(policyId, reviewData, currentVersion);
            }
          })
          .catch(error => {
            console.error('Error getting policy version:', error);
            PopupService.error('Error getting policy version: ' + (error.response?.data?.error || error.message), 'Policy Version Error');
          });
        
        return;
      }
      
      // For compliance reviews
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot
      };
      
      axios.put(
        `http://localhost:8000/api/compliance-approvals/${this.selectedApproval.ApprovalId}/review/`,
        reviewData
      )
      .then(response => {
        console.log('Response:', response.data);
        if (response.data.ApprovalId) {
          this.selectedApproval.ApprovalId = response.data.ApprovalId;
          this.selectedApproval.Version = response.data.Version;
          // Update approved date if provided
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
          PopupService.success('Compliance review submitted successfully!', 'Review Submitted');
          
          // First close the details view
          this.closeApprovalDetails();
          
          // Then refresh the approvals list to update the UI
          this.refreshApprovals();
        }
      })
      .catch(error => {
        console.error('Error submitting compliance review:', error);
        PopupService.error('Error submitting review: ' + (error.response?.data?.error || error.message), 'Review Error');
      });
    },
    // Add this helper method to handle the actual submission
    submitPolicyReview(policyId, reviewData, currentVersion) {
      // Submit policy review with current version info
      axios.post(`http://localhost:8000/api/policies/${policyId}/submit-review/`, {
        ...reviewData,
        currentVersion: currentVersion,
        approved: this.reviewDecision === 'approve'
      })
      .then(response => {
        console.log('Policy review submitted successfully:', response.data);
        
        // Update the local approval with the returned data
        this.selectedApproval.Version = response.data.Version;
        
        if (response.data.ApprovedDate) {
          this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
        }
        
        PopupService.success(`Policy review submitted successfully! New version: ${response.data.Version}`, 'Review Submitted');
        
        // Close the details view
        this.closeApprovalDetails();
        
        // Refresh the policies list
        this.refreshApprovals();
      })
      .catch(error => {
        console.error('Error submitting review:', error);
        PopupService.error('Error submitting review: ' + (error.response?.data?.error || error.message), 'Submission Error');
      });
    },
    // Update resubmitPolicy to change status back to "Under Review"
    resubmitPolicy(policy) {
      const policyId = this.getPolicyId(policy);
      console.log('Resubmitting policy with ID:', policyId);
      console.log('Policy data before preparing:', policy);
      
      // Validate policy data
      const validationErrors = this.validatePolicyData(policy);
      if (validationErrors.length > 0) {
        PopupService.warning(`Please fix the following errors before resubmitting:\n${validationErrors.join('\n')}`, 'Validation Errors');
        return;
      }
      
      // Check if subpolicies exist and have proper structure
      if (policy.ExtractedData.subpolicies && policy.ExtractedData.subpolicies.length > 0) {
        // Ensure each subpolicy has the correct fields
        policy.ExtractedData.subpolicies.forEach((subpolicy, index) => {
          console.log(`Checking subpolicy ${index} with ID: ${subpolicy.SubPolicyId}`);
          
          // Make sure required fields exist
          if (!subpolicy.SubPolicyName) {
            console.warn(`SubPolicyName is missing for subpolicy ${index}`);
          }
          if (!subpolicy.Description) {
            console.warn(`Description is missing for subpolicy ${index}`);
          }
        });
      } else {
        console.warn('No subpolicies found in policy data or subpolicies array is not properly structured');
      }
      
      // Prepare data for resubmission
      const resubmitData = {
        PolicyName: policy.ExtractedData.PolicyName,
        PolicyDescription: policy.ExtractedData.PolicyDescription,
        Scope: policy.ExtractedData.Scope,
        Objective: policy.ExtractedData.Objective,
        Department: policy.ExtractedData.Department,
        Applicability: policy.ExtractedData.Applicability,
        subpolicies: policy.ExtractedData.subpolicies || []
      };
      
      console.log('Prepared resubmission data:', resubmitData);
      console.log('Subpolicies in resubmission data:', resubmitData.subpolicies);
      console.log('Number of subpolicies:', resubmitData.subpolicies.length);
      
      // Submit resubmission request
      axios.put(`http://localhost:8000/api/policies/${policyId}/resubmit-approval/`, resubmitData)
        .then(response => {
          console.log('Policy resubmitted successfully:', response.data);
          
          // Show version information in the alert
          PopupService.success(`Policy resubmitted for review! New version: ${response.data.Version}`, 'Policy Resubmitted');
          
          this.closeEditModal();
          this.fetchRejectedPolicies();
          this.fetchPolicies();
        })
        .catch(error => {
          console.error('Error data:', error.response ? error.response.data : 'No response data');
          this.handleError(error, 'resubmitting policy');
        });
    },
    
    // Helper method to validate policy data before submission
    validatePolicyData(policy) {
      const validationErrors = [];
      
      // Check required policy fields
      if (!policy.ExtractedData.PolicyName) {
        validationErrors.push('Policy Name is required');
      }
      
      if (!policy.ExtractedData.PolicyDescription) {
        validationErrors.push('Policy Description is required');
      }
      
      // Check subpolicies if they exist
      if (policy.ExtractedData.subpolicies && policy.ExtractedData.subpolicies.length > 0) {
        policy.ExtractedData.subpolicies.forEach((subpolicy, index) => {
          if (!subpolicy.SubPolicyName) {
            validationErrors.push(`Subpolicy #${index + 1} is missing a name`);
          }
          
          if (!subpolicy.Description) {
            validationErrors.push(`Subpolicy #${index + 1} is missing a description`);
          }
        });
      }
      
      return validationErrors;
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
    // Update approveSubpolicy to handle subpolicy approval
    approveSubpolicy(subpolicy) {
      // Set subpolicy approval status
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Also update the UI to show policy is now approved
          if (this.selectedApproval && this.selectedApproval.ExtractedData) {
            this.selectedApproval.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies are now approved
        this.checkAllSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        PopupService.error('Error approving subpolicy. Please try again.', 'Approval Error');
      });
    },
    
    // Add a method to check if all subpolicies are approved
    checkAllSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedApproval.ExtractedData.policy_approval) {
          this.selectedApproval.ExtractedData.policy_approval = {};
        }
        this.selectedApproval.ExtractedData.policy_approval.approved = true;
        this.selectedApproval.ApprovedNot = true;
        
        // Show notification to user
        PopupService.success('All subpolicies are approved! The policy has been automatically approved.', 'Auto-Approval');
      }
    },
    // Add the missing rejectSubpolicy method
    rejectSubpolicy(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
    },
    // Add the missing cancelRejection method
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectingSubpolicy = null;
      this.rejectingType = '';
      this.rejectionComment = '';
    },
    // Update rejectSubpolicy via confirmRejection
    confirmRejection() {
      if (this.rejectingType === 'policy' && this.rejectingPolicy) {
        // Handle policy rejection
        const policyId = typeof this.rejectingPolicy.PolicyId === 'object' 
          ? this.rejectingPolicy.PolicyId.PolicyId 
          : this.rejectingPolicy.PolicyId;
        
        console.log('Rejecting policy with ID:', policyId);
        
        axios.put(`http://localhost:8000/api/policies/${policyId}/`, {
          Status: 'Rejected'
        })
        .then(() => {
          // Update local state
          this.rejectingPolicy.ExtractedData.Status = 'Rejected';
          this.rejectingPolicy.policy_approval = { 
            approved: false, 
            remarks: this.rejectionComment 
          };
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingPolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
        })
        .catch(error => {
          console.error('Error rejecting policy:', error);
          PopupService.error('Error rejecting policy: ' + (error.response?.data?.error || error.message), 'Rejection Error');
        });
      } 
      else if (this.rejectingType === 'subpolicy' && this.rejectingSubpolicy) {
        if (!this.rejectingSubpolicy.SubPolicyId) {
          console.error('Missing SubPolicyId, cannot reject subpolicy', this.rejectingSubpolicy);
          PopupService.error('Error: Cannot reject subpolicy - missing SubPolicyId', 'Missing ID Error');
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          return;
        }
        
        console.log('Rejecting subpolicy with ID:', this.rejectingSubpolicy.SubPolicyId);
        
        // Ensure Status is a string, not null
        const statusToSend = 'Rejected';
        console.log('Sending data:', { Status: statusToSend });
        
        // First update subpolicy status via API
        axios.put(`http://localhost:8000/api/subpolicies/${this.rejectingSubpolicy.SubPolicyId}/`, {
          Status: statusToSend
        })
      .then(response => {
          console.log('Subpolicy status updated successfully:', response.data);
          
          // Then save the rejection in the PolicyApproval table
          return axios.put(`http://localhost:8000/api/subpolicies/${this.rejectingSubpolicy.SubPolicyId}/review/`, {
            Status: statusToSend,
            remarks: this.rejectionComment
          });
        })
        .then(approvalResponse => {
          console.log('Policy approval created successfully:', approvalResponse.data);
          
          // Update local state
          if (!this.rejectingSubpolicy.approval) {
            this.rejectingSubpolicy.approval = {};
          }
          
          this.rejectingSubpolicy.Status = 'Rejected';
          this.rejectingSubpolicy.approval.approved = false;
          this.rejectingSubpolicy.approval.remarks = this.rejectionComment;
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          
          // Fetch rejected subpolicies if in user mode
          if (!this.isReviewer) {
            this.fetchRejectedSubpolicies();
        }
      })
      .catch(error => {
          console.error('Error rejecting subpolicy:', error);
          PopupService.error('Error rejecting subpolicy. Please try again.', 'Rejection Error');
        });
      }
    },
    getPolicyId(policy) {
      if (policy.PolicyId) {
        return typeof policy.PolicyId === 'object' ? policy.PolicyId.PolicyId : policy.PolicyId;
      }
      return policy.ApprovalId;
    },
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
    approveCompliance() {
      // Initialize compliance approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.compliance_approval) {
        this.selectedApproval.ExtractedData.compliance_approval = {};
      }
      this.selectedApproval.ExtractedData.compliance_approval.approved = true;
      this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
    },
    rejectCompliance() {
      this.rejectingType = 'compliance';
      this.showRejectModal = true;
    },
    openRejectedItem(item) {
      this.selectedApproval = item;
      this.showDetails = true;
      this.showEditComplianceModal = false;
      this.showEditModal = false;
      this.showSubpoliciesModal = false;
    },
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
    resubmitCompliance(compliance) {
      // Reset approval status
      if (compliance.ExtractedData.compliance_approval) {
        compliance.ExtractedData.compliance_approval.approved = null;
        compliance.ExtractedData.compliance_approval.remarks = '';
      }
      
      axios.put(`http://localhost:8000/api/compliance-approvals/resubmit/${compliance.ApprovalId}/`, {
        ExtractedData: compliance.ExtractedData
      })
      .then(() => {
        PopupService.success('Compliance resubmitted for review!', 'Compliance Resubmitted');
        this.showEditComplianceModal = false;
        this.fetchRejectedPolicies();
        // Force reload to update UI
        setTimeout(() => {
          window.location.reload();
        }, 500);
      })
      .catch(error => {
        PopupService.error('Error resubmitting compliance', 'Resubmission Error');
        console.error(error);
      });
    },
    showEditFormInline(subpolicy) {
      console.log('Opening inline edit form for subpolicy:', subpolicy.SubPolicyId);
      
      // Store original values before editing
      subpolicy.originalDescription = subpolicy.Description;
      subpolicy.originalControl = subpolicy.Control;
      
      // Make sure approval object exists before accessing it
      if (!subpolicy.approval) {
        subpolicy.approval = { remarks: '', approved: false };
      }
      
      // If this is a rejected subpolicy, fetch the latest reviewer version
      if (subpolicy.Status === 'Rejected' || (subpolicy.approval && subpolicy.approval.approved === false)) {
        axios.get(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Using reviewer version ${rVersion} for rejected subpolicy ${subpolicy.SubPolicyId}`);
            subpolicy.reviewerVersion = rVersion;
            
            // If we have approval data with this subpolicy, use it
            if (versionResponse.data.approval_data && 
                versionResponse.data.approval_data.ExtractedData && 
                versionResponse.data.approval_data.ExtractedData.subpolicies) {
              
              const approvalData = versionResponse.data.approval_data;
              
              // Find this subpolicy in the ExtractedData
              const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                s => s.SubPolicyId === subpolicy.SubPolicyId
              );
              
              if (subpolicyData) {
                // Keep original values for comparison
                const originalDescription = subpolicy.originalDescription;
                const originalControl = subpolicy.originalControl;
                
                // Update this subpolicy with the R version data
                Object.assign(subpolicy, subpolicyData);
                
                // Restore original values for comparison
                subpolicy.originalDescription = originalDescription;
                subpolicy.originalControl = originalControl;
                
                // Make sure approval object exists
                if (!subpolicy.approval) {
                  subpolicy.approval = { remarks: '', approved: false };
                }
                
                console.log(`Updated subpolicy ${subpolicy.SubPolicyId} with R version data for inline edit`);
              }
            }
          })
          .catch(error => {
            console.error('Error fetching reviewer version:', error);
            subpolicy.reviewerVersion = 'R1'; // Default fallback
          });
      }
      
      // Show the edit form
      subpolicy.showEditForm = true;
    },
    hideEditFormInline(subpolicy) {
      subpolicy.showEditForm = false;
    },
    resubmitSubpolicy() {
      if (!this.editingSubpolicy || !this.editingSubpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', this.editingSubpolicy);
        PopupService.error('Error: Cannot resubmit subpolicy - missing SubPolicyId', 'Missing ID Error');
        return;
      }
      
      // Check if any changes were made
      if (!this.hasChanges) {
        PopupService.warning('No changes detected. Please modify the subpolicy before resubmitting.', 'No Changes');
        return;
      }
      
      const updateData = {
        Control: this.editingSubpolicy.Control,
        Description: this.editingSubpolicy.Description,
        SubPolicyId: this.editingSubpolicy.SubPolicyId
      };
      
      // Send the resubmit request
      axios.put(`http://localhost:8000/api/subpolicies/${this.editingSubpolicy.SubPolicyId}/resubmit/`, updateData)
          .then(response => {
              console.log('Subpolicy resubmitted successfully:', response.data);
              
              // Update the UI with new version
              const newVersion = response.data.version;
              this.editingSubpolicy.Status = 'Under Review';
              this.editingSubpolicy.version = newVersion;
              
              if (!this.editingSubpolicy.approval) {
                  this.editingSubpolicy.approval = {};
              }
              this.editingSubpolicy.approval.approved = null;
              this.editingSubpolicy.resubmitted = true;
              
              // Show success message with new version
              PopupService.success(`Subpolicy "${this.editingSubpolicy.SubPolicyName}" resubmitted successfully with version ${newVersion}!`, 'Subpolicy Resubmitted');
              
              // Close the edit modal
              this.closeEditSubpolicyModal();
              
              // Refresh data
              this.fetchRejectedSubpolicies();
              this.refreshData();
          })
          .catch(error => {
              console.error('Error resubmitting subpolicy:', error.response || error);
              PopupService.error(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`, 'Resubmission Error');
          });
    },
    
    // Add a helper method to update subpolicy references across the UI
    updateSubpolicyReferences(subpolicyId, updates) {
      // Update in selectedApproval if applicable
      if (this.selectedApproval?.ExtractedData?.subpolicies) {
        const subpolicy = this.selectedApproval.ExtractedData.subpolicies.find(
          sub => sub.SubPolicyId === subpolicyId
        );
        if (subpolicy) {
          Object.assign(subpolicy, updates);
        }
      }
      
      // Update in selectedPolicyForSubpolicies if applicable
      if (this.selectedPolicyForSubpolicies?.ExtractedData?.subpolicies) {
        const subpolicy = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.find(
          sub => sub.SubPolicyId === subpolicyId
        );
        if (subpolicy) {
          Object.assign(subpolicy, updates);
        }
      }
      
      // Update in rejectedSubpolicies if applicable
      const rejectedSubpolicy = this.rejectedSubpolicies.find(
        sub => sub.SubPolicyId === subpolicyId
      );
      if (rejectedSubpolicy) {
        Object.assign(rejectedSubpolicy, updates);
      }
    },
    resubmitSubpolicyDirect(subpolicy) {
      if (!subpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', subpolicy);
        PopupService.error('Error: Cannot resubmit subpolicy - missing SubPolicyId', 'Missing ID Error');
        return;
      }
      
      // Check if any changes were made
      const hasChanges = (
        subpolicy.Description !== subpolicy.originalDescription ||
        subpolicy.Control !== subpolicy.originalControl
      );
      
      if (!hasChanges) {
        PopupService.warning('No changes detected. Please modify the subpolicy before resubmitting.', 'No Changes');
        return;
      }
      
      console.log('Resubmitting subpolicy with ID:', subpolicy.SubPolicyId);
      console.log('Changes detected in inline edit form');
      
      // Store original values before resubmitting
      const previousVersion = {
        Description: subpolicy.originalDescription,
        Control: subpolicy.originalControl
      };
      
      // Mark as resubmitted
      subpolicy.resubmitted = true;
      
      // Prepare data to send to the backend
      const updateData = {
        Control: subpolicy.Control,
        Description: subpolicy.Description,
        previousVersion: previousVersion,
        SubPolicyId: subpolicy.SubPolicyId
      };
      
      // Send the updated subpolicy data to the resubmit endpoint
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/resubmit/`, updateData)
      .then(response => {
          console.log('Subpolicy resubmitted successfully:', response.data);
          
          // Update the UI to show resubmitted status
          subpolicy.Status = 'Under Review';
          if (!subpolicy.approval) {
            subpolicy.approval = {};
          }
          subpolicy.approval.approved = null;
          subpolicy.previousVersion = previousVersion;
          
          if (response.data.Version) {
            subpolicy.version = response.data.Version;
          }
          
          // Show success message
          PopupService.success(`Subpolicy "${subpolicy.SubPolicyName}" resubmitted successfully with version ${response.data.Version || 'u1'}!`, 'Subpolicy Resubmitted');
          
          // Hide the edit form
        this.hideEditFormInline(subpolicy);
        
          // Close the modal after successful resubmission
          this.closeSubpoliciesModal();
          
          // Refresh the data
          this.fetchRejectedSubpolicies();
          this.fetchPolicies();
      })
      .catch(error => {
          console.error('Error resubmitting subpolicy:', error.response || error);
          PopupService.error(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`, 'Resubmission Error');
      });
    },
    getSubpolicyVersion(subpolicy) {
      if (subpolicy.version) {
        return subpolicy.version;
      } else if (subpolicy.approval && subpolicy.approval.version) {
        return subpolicy.approval.version;
      } else {
        return 'u1'; // Default version
      }
    },
    openSubpoliciesModal(policy) {
      this.selectedPolicyForSubpolicies = policy;
      
      // If policy is already approved, mark all subpolicies as approved
      if (policy.ExtractedData && 
          (policy.ApprovedNot === true || policy.ExtractedData.Status === 'Approved') && 
          policy.ExtractedData.subpolicies) {
        
        // Make a deep copy to avoid modifying the original data
        this.selectedPolicyForSubpolicies = JSON.parse(JSON.stringify(policy));
        
        // When a policy is approved, mark all subpolicies as approved too
        this.selectedPolicyForSubpolicies.ExtractedData.subpolicies = 
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.map(sub => {
            if (!sub.approval) {
              sub.approval = {};
            }
            sub.approval.approved = true;
            sub.Status = 'Approved';
            return sub;
          });
      } else if (policy.ExtractedData && 
          (policy.ApprovedNot === false || policy.ExtractedData.Status === 'Rejected') && 
          policy.ExtractedData.subpolicies) {
        
        // Make a deep copy for rejected policies
        this.selectedPolicyForSubpolicies = JSON.parse(JSON.stringify(policy));
        
        // For rejected policies, fetch the latest reviewer version (R1, R2, etc.) with full data
        const policyId = this.getPolicyId(policy);
        
        // Fetch the latest R version for the policy with its approval data
        axios.get(`http://localhost:8000/api/policies/${policyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Using reviewer version: ${rVersion} for policy ${policyId}`);
            
            // If we have approval data, use it to replace the current data
            if (versionResponse.data.approval_data) {
              const approvalData = versionResponse.data.approval_data;
              console.log('Found R version approval data:', approvalData);
              
              // Use the ExtractedData from the R version instead of the current data
              if (approvalData.ExtractedData) {
                // Keep reference to original policy for ID, etc.
                const originalPolicy = this.selectedPolicyForSubpolicies;
                
                // Replace the extracted data with the R version data
                this.selectedPolicyForSubpolicies = {
                  ...originalPolicy,
                  ExtractedData: approvalData.ExtractedData,
                  reviewerVersion: rVersion,
                  ApprovalId: approvalData.ApprovalId,
                  Version: approvalData.Version
                };
                
                console.log('Updated policy data with R version data:', this.selectedPolicyForSubpolicies);
              }
            } else {
              // Just update the version info if we don't have approval data
              this.selectedPolicyForSubpolicies.reviewerVersion = rVersion;
              
              // Now fetch R versions for each subpolicy
              this.fetchSubpolicyVersions();
            }
          })
          .catch(error => {
            console.error('Error fetching policy reviewer version:', error);
            // Try to fetch subpolicy versions anyway
            this.fetchSubpolicyVersions();
          });
      }
      
      this.showSubpoliciesModal = true;

      // If in user mode, ensure rejected subpolicies show edit options immediately
      if (!this.isReviewer) {
        // Process each subpolicy to ensure rejected ones can be edited
        setTimeout(() => {
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData && 
              this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
            
            this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.forEach(sub => {
              if (sub.Status === 'Rejected' || 
                 (sub.approval && sub.approval.approved === false)) {
                // Pre-populate the edit form for rejected subpolicies
                sub.showEditForm = true;
              }
            });
          }
        }, 100); // Small delay to ensure DOM is updated
      }
    },
    
    // Helper method to fetch subpolicy versions
    fetchSubpolicyVersions() {
      if (this.selectedPolicyForSubpolicies && 
          this.selectedPolicyForSubpolicies.ExtractedData && 
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        
        const promises = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.map(sub => {
          if (sub.SubPolicyId) {
            return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/reviewer-version/`)
              .then(subVersionResponse => {
                const subRVersion = subVersionResponse.data.version || 'R1';
                console.log(`Subpolicy ${sub.SubPolicyId} reviewer version: ${subRVersion}`);
                
                // Store reviewer version
                sub.reviewerVersion = subRVersion;
                
                // If we have approval data for this subpolicy, update its data
                if (subVersionResponse.data.approval_data && 
                    subVersionResponse.data.approval_data.ExtractedData && 
                    subVersionResponse.data.approval_data.ExtractedData.subpolicies) {
                  
                  const approvalData = subVersionResponse.data.approval_data;
                  
                  // Find this subpolicy in the ExtractedData
                  const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                    s => s.SubPolicyId === sub.SubPolicyId
                  );
                  
                  if (subpolicyData) {
                    // Update this subpolicy with the R version data
                    Object.assign(sub, subpolicyData);
                    console.log(`Updated subpolicy ${sub.SubPolicyId} with R version data`);
                  }
                }
                
                return sub;
              })
              .catch(err => {
                console.error(`Error fetching reviewer version for subpolicy ${sub.SubPolicyId}:`, err);
                sub.reviewerVersion = 'R1'; // Default fallback
                return sub;
              });
          } else {
            sub.reviewerVersion = 'R1'; // Default for subpolicies without ID
            return Promise.resolve(sub);
          }
        });
        
        Promise.all(promises).then(() => {
          console.log('All reviewer versions fetched for subpolicies');
        });
      }
    },
    closeSubpoliciesModal() {
      this.selectedPolicyForSubpolicies = null;
      this.showSubpoliciesModal = false;
    },
    approveSubpolicyFromModal(subpolicy) {
      // Set subpolicy approval status in UI
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Update the UI to show the policy is now approved
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData) {
            this.selectedPolicyForSubpolicies.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies in the modal are approved
        this.checkAllModalSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        PopupService.error('Error approving subpolicy. Please try again.', 'Approval Error');
      });
    },
    
    // Add a method to check if all subpolicies in the modal view are approved
    checkAllModalSubpoliciesApproved() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies ||
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies in the modal are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedPolicyForSubpolicies.ExtractedData.policy_approval) {
          this.selectedPolicyForSubpolicies.ExtractedData.policy_approval = {};
        }
        this.selectedPolicyForSubpolicies.ExtractedData.policy_approval.approved = true;
        this.selectedPolicyForSubpolicies.ApprovedNot = true;
        
        // Show notification to user
        PopupService.success('All subpolicies are approved! The policy has been automatically approved.', 'Auto-Approval');
      }
    },
    rejectSubpolicyFromModal(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
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
    isNewPolicy(policy) {
      const createdDate = policy.ExtractedData?.CreatedByDate || policy.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    // Add a new method for opening the edit modal for a rejected subpolicy
    openEditSubpolicyModal(subpolicy) {
      // Create a deep copy of the subpolicy to edit
      this.editingSubpolicy = JSON.parse(JSON.stringify(subpolicy));
      
      // Store original values for comparison
      this.editingSubpolicy.originalDescription = subpolicy.Description;
      this.editingSubpolicy.originalControl = subpolicy.Control;
      
      // Fetch the latest reviewer version for this rejected subpolicy with complete data
      if (subpolicy.SubPolicyId) {
        axios.get(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Fetched reviewer version for edit modal: ${rVersion}`);
            this.editingSubpolicy.reviewerVersion = rVersion;
            
            // If we have approval data with this subpolicy, use it
            if (versionResponse.data.approval_data && 
                versionResponse.data.approval_data.ExtractedData && 
                versionResponse.data.approval_data.ExtractedData.subpolicies) {
              
              const approvalData = versionResponse.data.approval_data;
              
              // Find this subpolicy in the ExtractedData
              const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                s => s.SubPolicyId === subpolicy.SubPolicyId
              );
              
              if (subpolicyData) {
                // Keep original values for comparison
                const originalDescription = this.editingSubpolicy.originalDescription;
                const originalControl = this.editingSubpolicy.originalControl;
                
                // Update this subpolicy with the R version data
                Object.assign(this.editingSubpolicy, subpolicyData);
                
                // Restore original values for comparison
                this.editingSubpolicy.originalDescription = originalDescription;
                this.editingSubpolicy.originalControl = originalControl;
                
                console.log(`Updated subpolicy ${subpolicy.SubPolicyId} with R version data for edit modal`);
              }
            }
          })
          .catch(err => {
            console.error('Error fetching reviewer version:', err);
            this.editingSubpolicy.reviewerVersion = 'R1'; // Default
          });
      }
      
      // Show the edit modal
      this.showEditSubpolicyModal = true;
      
      console.log('Edit modal opened with subpolicy:', this.editingSubpolicy);
    },
    
    // Add a method to close the edit subpolicy modal
    closeEditSubpolicyModal() {
      this.showEditSubpolicyModal = false;
      this.editingSubpolicy = null;
    },
    
    // Helper method to find a subpolicy by ID
    findSubpolicyById(subpolicyId) {
      if (!this.selectedPolicyForSubpolicies || !this.selectedPolicyForSubpolicies.ExtractedData || !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return null;
      }
      
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.find(
        sub => sub.SubPolicyId === subpolicyId
      );
    },
    // Add method to fetch rejected subpolicies
    fetchRejectedSubpolicies() {
      console.log('Fetching rejected subpolicies...');
      // For now, we'll fetch all policies and filter for rejected subpolicies
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('Received policies for subpolicy check:', response.data.length);
          const allPolicies = response.data;
          let rejectedSubs = [];
          
          // Go through each policy and collect rejected subpolicies
          allPolicies.forEach(policy => {
            if (policy.subpolicies && policy.subpolicies.length > 0) {
              console.log(`Policy ${policy.PolicyId} has ${policy.subpolicies.length} subpolicies`);
              const rejected = policy.subpolicies.filter(sub => sub.Status === 'Rejected');
              console.log(`Policy ${policy.PolicyId} has ${rejected.length} rejected subpolicies`);
              
              // Add policy info to each subpolicy for context
              rejected.forEach(sub => {
                sub.PolicyName = policy.PolicyName;
                sub.PolicyId = policy.PolicyId;
              });
              
              rejectedSubs = [...rejectedSubs, ...rejected];
            }
          });
          
          console.log('Total rejected subpolicies found:', rejectedSubs.length);
          this.rejectedSubpolicies = rejectedSubs;
          
          // If we're in user mode and there are rejected subpolicies, update the view
          if (!this.isReviewer && rejectedSubs.length > 0) {
            this.updateRejectedSubpoliciesView();
          }
        })
        .catch(error => {
          console.error('Error fetching rejected subpolicies:', error);
        });
    },
    // Add a method to update the rejected subpolicies view in user mode
    updateRejectedSubpoliciesView() {
      // Set the active tab to rejected if we have rejected subpolicies
      if (this.rejectedSubpolicies.length > 0) {
        this.activeTab = 'rejected';
      }
    },
    // Method to track changes in the edit form
    trackChanges() {
      // No need for complex logic here - Vue's reactivity will handle updates to the model
      // We just need this method to trigger when input happens
      console.log('Changes detected in form');
    },
    // Add helper method to increment version
    incrementVersion(currentVersion) {
      if (!currentVersion) return 'u1';
      const match = currentVersion.match(/u(\d+)/);
      if (!match) return 'u1';
      const num = parseInt(match[1]) + 1;
      return `u${num}`;
    },
    // Add this helper method
    getSubpolicyRemarks(sub) {
      return sub && sub.approval && sub.approval.remarks ? sub.approval.remarks : 'No reason provided';
    },
    // Add a method to fetch policy categories
    fetchPolicyCategories() {
      axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          // Handle both response formats: direct array or success wrapper
          if (response.data.success && response.data.data) {
            this.policyCategories = response.data.data;
          } else if (Array.isArray(response.data)) {
            this.policyCategories = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
          }
        })
        .catch(error => {
          console.error('Error fetching policy categories:', error);
        });
    },
    fetchPolicyTypes() {
      console.log('Fetching policy categories...');
      return axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          console.log('Policy categories response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let categoriesData;
          if (response.data.success && response.data.data) {
            categoriesData = response.data.data;
          } else if (Array.isArray(response.data)) {
            categoriesData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          // Store the raw categories data
          this.policyCategories = categoriesData;
          
          // Create a structured map for easier filtering
          const typeMap = {};
          
          // Process the categories into a nested structure
          categoriesData.forEach(category => {
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
          throw error; // Re-throw for Promise.all to catch
        });
    },
    // Helper method to initialize or update policy category fields
    initializePolicyCategoryFields(policy) {
      console.log(`Initializing policy category fields for policy: ${policy.PolicyId || 'New Policy'}`);
      
      // Initialize policy category fields if they don't exist
      if (!policy.ExtractedData.PolicyType) policy.ExtractedData.PolicyType = '';
      if (!policy.ExtractedData.PolicyCategory) policy.ExtractedData.PolicyCategory = '';
      if (!policy.ExtractedData.PolicySubCategory) policy.ExtractedData.PolicySubCategory = '';
      
      // Log current values
      console.log('Current policy category fields:', {
        PolicyType: policy.ExtractedData.PolicyType,
        PolicyCategory: policy.ExtractedData.PolicyCategory,
        PolicySubCategory: policy.ExtractedData.PolicySubCategory
      });
      
      return policy;
    },
    openRejectedPolicy(policy) {
      console.log('Opening rejected policy for editing:', policy);
      this.editingPolicy = JSON.parse(JSON.stringify(policy)); // Deep copy
      
      // Initialize policy category fields
      this.initializePolicyCategoryFields(this.editingPolicy);
      
      this.showEditModal = true;
    },
    // Handle policy type change
    handlePolicyTypeChange(policy) {
      console.log(`Policy type changed to: ${policy.ExtractedData.PolicyType}`);
      // Reset dependent fields when type changes
      policy.ExtractedData.PolicyCategory = '';
      policy.ExtractedData.PolicySubCategory = '';
    },
    
    // Handle policy category change
    handlePolicyCategoryChange(policy) {
      console.log(`Policy category changed to: ${policy.ExtractedData.PolicyCategory}`);
      // Reset subcategory when category changes
      policy.ExtractedData.PolicySubCategory = '';
    },
    
    // CollapsibleTable related methods
    handleTaskClick(task) {
      // Find the original policy object from the task data using policyId
      let policy = null;
      
      // Search in all status categories for the policy
      const allPolicies = [
        ...this.actualPolicies.pending,
        ...this.actualPolicies.approved,
        ...this.actualPolicies.rejected
      ];
      
      policy = allPolicies.find(p => 
        p.PolicyId === task.policyId || p.PolicyId === task.approvalId
      );
      
      if (policy) {
        this.openApprovalDetails(policy);
      } else {
        console.error('Policy not found for task:', task);
      }
    },
    
    formatPolicyForTable(policy) {
      const policyId = policy.PolicyId || 'N/A';
      const policyName = policy.ExtractedData?.PolicyName || 'No Name';
      const scope = policy.ExtractedData?.Scope || 'No Scope';
      const createdBy = policy.ExtractedData?.CreatedByName || 'System';
      const createdDate = this.formatDate(policy.ExtractedData?.CreatedByDate || policy.created_at);
      const version = policy.version || 'v1.0';
      
      // Determine status based on database status
      let status = policy.dbStatus || policy.ExtractedData?.Status || 'Unknown';
      let statusClass = 'pending';
      
      if (status === 'Approved') {
        statusClass = 'approved';
      } else if (status === 'Rejected') {
        statusClass = 'rejected';
      } else if (status === 'Under Review') {
        status = 'Pending';
        statusClass = 'pending';
      }
      
      return {
        incidentId: policyId, // Using policyId as the key for CollapsibleTable
        approvalId: policy.ApprovalId || policyId, // Keep approvalId for compatibility
        policyId: policyId,
        policyName: policyName,
        scope: scope,
        createdBy: createdBy,
        createdDate: createdDate,
        version: version,
        status: `<span class="status-badge ${statusClass}">${status}</span>`,
        originalPolicy: policy // Keep reference to original policy object
      };
    },
    togglePendingSection() {
      this.pendingExpanded = !this.pendingExpanded;
    },
    toggleApprovedSection() {
      this.approvedExpanded = !this.approvedExpanded;
    },
    toggleRejectedSection() {
      this.rejectedExpanded = !this.rejectedExpanded;
    },
    
    // Handle rejected item action from DynamicTable
    handleRejectedItemAction(action, row) {
      console.log('Rejected item action:', action, row);
      
      if (action === 'view') {
        this.openRejectedItem(row.originalPolicy);
      }
    },
    // Debug method to help troubleshoot
    debugDataState() {
      console.log('=== Policy Approver Debug Info ===');
      console.log('Total approvals:', this.approvals.length);
      console.log('Pending count:', this.pendingApprovalsCount);
      console.log('Approved count:', this.approvedApprovalsCount);
      console.log('Rejected count:', this.rejectedApprovalsCount);
      console.log('Pending approvals:', this.pendingApprovals);
      console.log('Approved approvals:', this.approvedApprovals);
      console.log('Rejected approvals:', this.rejectedApprovals);
      console.log('Raw approvals data:', this.approvals);
      console.log('=== End Debug Info ===');
    },
    // Add method to fetch actual policy counts from database
    fetchPolicyCounts() {
      console.log('Fetching actual policy counts from database...');
      return axios.get('http://localhost:8000/api/policy-counts/')
        .then(response => {
          console.log('Policy counts response:', response.data);
          
          // Store the actual counts from the new endpoint
          this.actualPolicyCounts = {
            pending: response.data.pending || 0,
            approved: response.data.approved || 0,
            rejected: response.data.rejected || 0
          };
          
          // Calculate total pages for pagination
          this.pagination.pending.totalPages = Math.ceil(this.actualPolicyCounts.pending / this.pagination.pending.pageSize);
          this.pagination.approved.totalPages = Math.ceil(this.actualPolicyCounts.approved / this.pagination.approved.pageSize);
          this.pagination.rejected.totalPages = Math.ceil(this.actualPolicyCounts.rejected / this.pagination.rejected.pageSize);
          
          console.log('Actual policy counts from database:', this.actualPolicyCounts);
          console.log('Pagination info:', this.pagination);
        }).catch(error => {
          console.error('Error fetching policy counts:', error);
          // Fallback to the old method if the new endpoint fails
          console.log('Falling back to individual API calls...');
          return Promise.all([
            axios.get('http://localhost:8000/api/policies/?status=Under Review'),
            axios.get('http://localhost:8000/api/policies/?status=Approved'), 
            axios.get('http://localhost:8000/api/policies/?status=Rejected')
          ]).then(([pendingResponse, approvedResponse, rejectedResponse]) => {
            const pendingData = Array.isArray(pendingResponse.data) ? pendingResponse.data : (pendingResponse.data.data || []);
            const approvedData = Array.isArray(approvedResponse.data) ? approvedResponse.data : (approvedResponse.data.data || []);
            const rejectedData = Array.isArray(rejectedResponse.data) ? rejectedResponse.data : (rejectedResponse.data.data || []);
            
            this.actualPolicyCounts = {
              pending: pendingData.length,
              approved: approvedData.length,
              rejected: rejectedData.length
            };
            
            // Calculate total pages for pagination
            this.pagination.pending.totalPages = Math.ceil(this.actualPolicyCounts.pending / this.pagination.pending.pageSize);
            this.pagination.approved.totalPages = Math.ceil(this.actualPolicyCounts.approved / this.pagination.approved.pageSize);
            this.pagination.rejected.totalPages = Math.ceil(this.actualPolicyCounts.rejected / this.pagination.rejected.pageSize);
            
            console.log('Actual policy counts from fallback method:', this.actualPolicyCounts);
          }).catch(fallbackError => {
            console.error('Fallback method also failed:', fallbackError);
            this.actualPolicyCounts = {
              pending: 0,
              approved: 0,
              rejected: 0
            };
          });
        });
    },
    
    // Add method to fetch actual policies by status with pagination
    fetchPoliciesByStatus(status, page = 1) {
      console.log(`Fetching ${status} policies for page ${page}...`);
      
      const statusMap = {
        'pending': 'Under Review',
        'approved': 'Approved',
        'rejected': 'Rejected'
      };
      
      const actualStatus = statusMap[status] || status;
      const pageSize = this.pagination[status].pageSize;
      const offset = (page - 1) * pageSize;
      
      return axios.get(`http://localhost:8000/api/policies-paginated/`, {
        params: {
          status: actualStatus,
          limit: pageSize,
          offset: offset
        }
      })
      .then(response => {
        console.log(`${status} policies response:`, response.data);
        
        // Handle the response from the new paginated endpoint
        if (response.data.success && response.data.data) {
          const policiesData = response.data.data;
          const paginationInfo = response.data.pagination;
          
          // Update pagination info from backend response
          this.pagination[status].totalPages = paginationInfo.total_pages;
          this.pagination[status].currentPage = paginationInfo.current_page;
          
          // Store the policies for this status and page
          this.actualPolicies[status] = policiesData.map(policy => ({
            PolicyId: policy.PolicyId,
            ExtractedData: {
              PolicyName: policy.PolicyName || 'No Name',
              CreatedByName: policy.CreatedByName || 'System',
              CreatedByDate: policy.CreatedByDate || policy.created_at,
              Scope: policy.Scope || 'No Scope',
              Status: policy.Status,
              Objective: policy.Objective || 'No Objective',
              Department: policy.Department || 'No Department',
              subpolicies: policy.subpolicies || []
            },
            ApprovedNot: policy.Status === 'Approved' ? true : (policy.Status === 'Rejected' ? false : null),
            ApprovedDate: policy.ApprovedDate,
            version: policy.Version || 'v1.0',
            dbStatus: policy.Status
          }));
          
          console.log(`Stored ${this.actualPolicies[status].length} ${status} policies for page ${page}`);
          console.log(`Updated pagination: ${this.pagination[status].currentPage}/${this.pagination[status].totalPages}`);
        } else {
          console.error('Unexpected response format from paginated endpoint:', response.data);
          this.actualPolicies[status] = [];
        }
      })
      .catch(error => {
        console.error(`Error fetching ${status} policies:`, error);
        this.actualPolicies[status] = [];
        throw error;
      });
    },
    
    // Add method to fetch all policy statuses with pagination
    fetchAllPoliciesByStatus() {
      console.log('Fetching all policies by status with pagination...');
      
      return Promise.all([
        this.fetchPoliciesByStatus('pending', this.pagination.pending.currentPage),
        this.fetchPoliciesByStatus('approved', this.pagination.approved.currentPage),
        this.fetchPoliciesByStatus('rejected', this.pagination.rejected.currentPage)
      ]);
    },
    
    // Add pagination methods
    changePage(status, page) {
      console.log(`Changing to page ${page} for ${status} policies`);
      this.pagination[status].currentPage = page;
      this.fetchPoliciesByStatus(status, page);
    },
    
    nextPage(status) {
      if (this.pagination[status].currentPage < this.pagination[status].totalPages) {
        this.changePage(status, this.pagination[status].currentPage + 1);
      }
    },
    
    prevPage(status) {
      if (this.pagination[status].currentPage > 1) {
        this.changePage(status, this.pagination[status].currentPage - 1);
      }
    }
  },
  computed: {
    policyApprovals() {
      // Return all approvals since we're now directly using the policies data
      return this.approvals;
    },
    pendingApprovalsCount() {
      return this.actualPolicyCounts.pending;
    },
    approvedApprovalsCount() {
      return this.actualPolicyCounts.approved;
    },
    rejectedApprovalsCount() {
      return this.actualPolicyCounts.rejected;
    },
    sortedPolicies() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
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
    hasUnreviewedSubpolicies() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies) {
        return true;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.some(sub => {
        return sub.approval?.approved === null || sub.approval?.approved === undefined;
      });
    },
    hasRejectedSubpolicies() {
      return this.rejectedSubpolicies && this.rejectedSubpolicies.length > 0;
    },
    hasChanges() {
      if (!this.editingSubpolicy) return false;
      
      // Check if Description or Control have changed from their original values
      const descriptionChanged = this.editingSubpolicy.Description !== this.editingSubpolicy.originalDescription;
      const controlChanged = this.editingSubpolicy.Control !== this.editingSubpolicy.originalControl;
      
      return descriptionChanged || controlChanged;
    },
    rejectedSubpoliciesInPolicy() {
      if (!this.editingPolicy || !this.editingPolicy.ExtractedData || !this.editingPolicy.ExtractedData.subpolicies) {
        return [];
      }
      
      return this.editingPolicy.ExtractedData.subpolicies.filter(sub => 
        sub.approval?.approved === false
      );
    },
    isComplianceApproval() {
      return this.selectedApproval?.ExtractedData?.type === 'compliance';
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      
      if (this.isComplianceApproval) {
        return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
      } else {
        return this.selectedApproval.ExtractedData.policy_approval || { approved: null, remarks: '' };
      }
    },
    allSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return false;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.every(sub => sub.approval?.approved === true);
    },
    filteredSubpolicies() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return [];
      }
      
      // If in reviewer mode, show all subpolicies
      if (this.isReviewer) {
        return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      }
      
      // In user mode, only show rejected subpolicies
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.filter(sub => 
        sub.Status === 'Rejected' || 
        (sub.approval && sub.approval.approved === false)
      );
    },
    
    // CollapsibleTable related computed properties - now using actual policies
    pendingApprovals() {
      return this.actualPolicies.pending.map(policy => ({
        ...policy,
        // Ensure consistent data structure
        version: policy.version || 'v1.0',
        created_at: policy.ExtractedData?.CreatedByDate
      }));
    },
    
    approvedApprovals() {
      return this.actualPolicies.approved.map(policy => ({
        ...policy,
        // Ensure consistent data structure
        version: policy.version || 'v1.0',
        created_at: policy.ExtractedData?.CreatedByDate
      }));
    },
    
    rejectedApprovals() {
      return this.actualPolicies.rejected.map(policy => ({
        ...policy,
        // Ensure consistent data structure
        version: policy.version || 'v1.0',
        created_at: policy.ExtractedData?.CreatedByDate
      }));
    },
    
    // Table headers configuration
    tableHeaders() {
      return [
        { key: 'approvalId', label: 'Approval ID', width: '120px', className: 'approval-id' },
        { key: 'policyId', label: 'Policy ID', width: '120px', className: 'policy-id' },
        { key: 'policyName', label: 'Policy Name', width: '200px', className: 'policy-name' },
        { key: 'scope', label: 'Scope', width: '150px', className: 'policy-scope' },
        { key: 'createdBy', label: 'Created By', width: '120px', className: 'created-by' },
        { key: 'createdDate', label: 'Created Date', width: '120px', className: 'created-date' },
        { key: 'version', label: 'Version', width: '80px', className: 'version' },
        { key: 'status', label: 'Status', width: '100px', className: 'status' },
        { key: 'actions', label: 'Actions', width: '150px', className: 'actions' }
      ];
    },
    
    // Section configurations for CollapsibleTable
    pendingSectionConfig() {
      return {
        name: 'Pending',
        statusClass: 'pending',
        tasks: this.pendingApprovals.map(policy => this.formatPolicyForTable(policy)),
        pagination: this.pagination.pending,
        totalCount: this.actualPolicyCounts.pending
      };
    },
    
    approvedSectionConfig() {
      return {
        name: 'Approved',
        statusClass: 'completed',
        tasks: this.approvedApprovals.map(policy => this.formatPolicyForTable(policy)),
        pagination: this.pagination.approved,
        totalCount: this.actualPolicyCounts.approved
      };
    },
    
    rejectedSectionConfig() {
      return {
        name: 'Rejected',
        statusClass: 'rejected',
        tasks: this.rejectedApprovals.map(policy => this.formatPolicyForTable(policy)),
        pagination: this.pagination.rejected,
        totalCount: this.actualPolicyCounts.rejected
      };
    },
    
    // DynamicTable configuration for rejected policies
    rejectedPoliciesTableData() {
      return this.rejectedPolicies.map(policy => ({
        ApprovalId: policy.ApprovalId || policy.PolicyId,
        PolicyId: this.getPolicyId(policy),
        ItemType: policy.is_compliance ? 'Compliance' : 
                 (policy.main_policy_rejected ? 'Policy' : 'Subpolicy'),
        ItemName: policy.ExtractedData?.PolicyName || policy.ExtractedData?.ComplianceItemDescription || 'No Name',
        Description: policy.is_compliance ? 
                    (policy.ExtractedData?.ComplianceItemDescription || 'No Description') :
                    (policy.ExtractedData?.Scope || 'No Scope'),
        CreatedBy: policy.ExtractedData?.CreatedByName || 'System',
        CreatedDate: this.formatDate(policy.ExtractedData?.CreatedByDate || policy.created_at),
        RejectionReason: policy.ExtractedData?.policy_approval?.remarks || 
                        policy.ExtractedData?.compliance_approval?.remarks || 
                        policy.rejection_reason || 'No reason provided',
        Status: 'Rejected',
        originalPolicy: policy // Keep reference to original policy object
      }));
    },
    
    rejectedPoliciesColumns() {
      return [
        {
          key: 'PolicyId',
          label: 'Item ID',
          sortable: true,
          headerClass: 'policy-id-header',
          cellClass: 'policy-id-cell'
        },
        {
          key: 'ItemType',
          label: 'Type',
          sortable: true,
          type: 'status',
          headerClass: 'item-type-header',
          cellClass: 'item-type-cell'
        },
        {
          key: 'ItemName',
          label: 'Name',
          sortable: true,
          headerClass: 'item-name-header',
          cellClass: 'item-name-cell'
        },
        {
          key: 'Description',
          label: 'Description',
          sortable: false,
          headerClass: 'description-header',
          cellClass: 'description-cell'
        },
        {
          key: 'CreatedBy',
          label: 'Created By',
          sortable: true,
          headerClass: 'created-by-header',
          cellClass: 'created-by-cell'
        },
        {
          key: 'CreatedDate',
          label: 'Created Date',
          sortable: true,
          headerClass: 'created-date-header',
          cellClass: 'created-date-cell'
        },
        {
          key: 'RejectionReason',
          label: 'Rejection Reason',
          sortable: false,
          headerClass: 'rejection-reason-header',
          cellClass: 'rejection-reason-cell'
        }
      ];
    }
  }
}
</script>

<style scoped>
@import './PolicyApprover.css';

/* Completely revised modal layering with much higher z-indices */
.subpolicies-modal {
  z-index: 9000 !important;
}

.edit-subpolicy-modal {
  z-index: 10000 !important; /* Dramatically higher z-index */
  position: fixed;
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto !important; /* Force pointer events */
}

.edit-policy-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2), 0 0 0 1000px rgba(0, 0, 0, 0.3);
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  animation: fadeIn 0.3s ease-in-out;
  z-index: 10001 !important; /* Content even higher */
}

.reject-modal {
  z-index: 11000 !important; /* Highest z-index to appear on top */
}

/* Override any potential conflicting styles in the base CSS */
.policy-details-modal,
.reject-modal,
.edit-policy-modal,
.subpolicies-modal,
.edit-subpolicy-modal {
  position: fixed !important;
  z-index: auto !important; /* Let our specific z-index values take precedence */
}

/* The rest of your styling remains the same */
.edit-subpolicy-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #4b5563;
}

.edit-subpolicy-modal input,
.edit-subpolicy-modal textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.edit-subpolicy-modal input:focus,
.edit-subpolicy-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-subpolicy-modal button.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.edit-subpolicy-modal button.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Improved styles for subpolicy-inline-edit */
.subpolicy-inline-edit {
  background: #f8fafc;
  border: 2px solid #6366f1;
  border-radius: 8px;
  padding: 24px;
  margin: 15px 0;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.3s ease-out;
  transition: all 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.subpolicy-inline-edit h4 {
  margin-top: 0;
  color: #6366f1;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.subpolicy-inline-edit label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.subpolicy-inline-edit input,
.subpolicy-inline-edit textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.subpolicy-inline-edit input:focus,
.subpolicy-inline-edit textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.subpolicy-inline-edit input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

.subpolicy-inline-edit textarea {
  min-height: 100px;
  resize: vertical;
}

.subpolicy-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.cancel-btn {
  background: #e5e7eb;
  color: #4b5563;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #d1d5db;
  transform: translateY(-2px);
}

.subpolicy-status {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.subpolicy-status:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.badge.rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 12px;
  font-weight: 600;
  font-size: 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.rejection-reason {
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 12px;
  margin: 12px 0;
  color: #991b1b;
  font-size: 14px;
  border-radius: 0 4px 4px 0;
}

.badge.resubmitted {
  background-color: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  position: relative;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 5px rgba(59, 130, 246, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

/* Styles for resubmitted items */
.resubmitted-item {
  border-left: 4px solid #3b82f6 !important;
  background-color: rgba(59, 130, 246, 0.05);
  position: relative;
}

.resubmitted-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -4px;
  height: 100%;
  width: 4px;
  background-color: #3b82f6;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* Subpolicy header with better layout */
.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* Version tag styling */
.subpolicy-version {
  margin-bottom: 10px;
}

.version-tag {
  background-color: #3b82f6;
  color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-weight: 600;
  margin-right: 10px;
}

/* Edit history styling */
.edit-history {
  margin-top: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.edit-history-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-history-content {
  padding: 15px;
  background-color: #f9fafb;
}

.edit-field {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #e5e7eb;
}

.edit-field:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.field-label {
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 5px;
  font-size: 13px;
}

.field-previous {
  padding: 10px;
  background-color: #fee2e2;
  border-radius: 4px;
  margin-bottom: 10px;
  position: relative;
  text-decoration: line-through;
  color: #991b1b;
  font-size: 14px;
}

.field-value {
  padding: 10px;
  background-color: #dcfce7;
  border-radius: 4px;
  color: #166534;
  font-size: 14px;
}

/* Subpolicy content section */
.subpolicy-content {
  margin-bottom: 15px;
}

.view-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.view-button:hover {
  background-color: #2563eb;
}

/* Add styles for approved date display */
.policy-approved-date {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #22c55e;
}

.date-label {
  font-weight: 600;
  color: #065f46;
}

.date-value {
  color: #059669;
  font-family: 'Courier New', monospace;
}

.approval-status.approved {
  background-color: #dcfce7;
  color: #166534;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

/* Styles for changes summary in edit modal */
.changes-summary {
  margin: 15px 0;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  overflow: hidden;
  background-color: rgba(59, 130, 246, 0.05);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.changes-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.changes-content {
  padding: 12px 15px;
}

.change-item {
  padding: 8px 0;
  color: #4b5563;
  font-size: 14px;
  border-bottom: 1px dashed #e5e7eb;
}

.change-item:last-child {
  border-bottom: none;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-actions .resubmit-btn {
  background-color: #6366f1;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .resubmit-btn:hover:not(:disabled) {
  background-color: #4f46e5;
  transform: translateY(-2px);
}

.form-actions .resubmit-btn:disabled {
  background-color: #c7d2fe;
  cursor: not-allowed;
  color: #6366f1;
}

.form-actions .cancel-btn {
  background-color: #e5e7eb;
  color: #4b5563;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .cancel-btn:hover {
  background-color: #d1d5db;
  transform: translateY(-2px);
}

/* Improve edit modal styling */
.edit-modal {
  width: 90%;
  max-width: 700px;
  padding: 30px;
  border-radius: 12px;
}

.edit-modal h2 {
  color: #4f46e5;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #c7d2fe;
  font-size: 22px;
}

.edit-modal .form-group {
  margin-bottom: 20px;
}

.edit-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.edit-modal input,
.edit-modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.edit-modal input:focus,
.edit-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-modal textarea {
  min-height: 120px;
  resize: vertical;
}

.edit-modal input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

/* Badge for approved-only view */
.approved-only-badge {
  background-color: #10b981;
  color: white;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  margin-left: 10px;
  font-weight: 500;
  display: inline-block;
  vertical-align: middle;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

/* Policy status indicator styles */
.policy-status-indicator {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  background: #f8fafc;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.status-label {
  font-weight: 600;
  margin-right: 10px;
  color: #4b5563;
}

.status-value {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  text-align: center;
}

.status-approved {
  background-color: #10b981;
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.status-rejected {
  background-color: #ef4444;
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.status-pending {
  background-color: #f59e0b;
  color: white;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
}

/* Add these styles to your component */
.rejection-reason-section {
  margin: 15px 0;
  padding: 15px;
  background-color: #fff5f5;
  border-left: 4px solid #ef4444;
  border-radius: 0 4px 4px 0;
}

.rejection-reason-section h4 {
  color: #b91c1c;
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
}

.rejection-message {
  color: #991b1b;
  font-size: 14px;
  line-height: 1.5;
}

/* Add these styles */
.rejected-subpolicy-details {
  margin: 15px 0;
  padding: 15px;
  background-color: #fff5f5;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.status-badge.rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.rejection-reason {
  margin-top: 12px;
  padding: 10px 15px;
  background-color: #fee2e2;
  border-radius: 6px;
}

.reason-header {
  font-weight: 600;
  color: #b91c1c;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.reason-content {
  color: #991b1b;
  font-size: 14px;
  line-height: 1.5;
}

/* Add these styles */
.policy-rejection-reason {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fee2e2;
  border-radius: 4px;
  color: #991b1b;
  font-size: 14px;
}

/* Add these styles */
.rejection-reason-container {
  margin: 15px 0 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.rejection-reason-header {
  background-color: #ef4444;
  color: white;
  padding: 12px 15px;
  font-weight: 600;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rejection-reason-content {
  padding: 15px;
  background-color: #fee2e2;
  color: #991b1b;
  font-size: 14px;
  line-height: 1.6;
}
</style> 