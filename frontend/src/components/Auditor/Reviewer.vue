<template>
  <div class="reviewer-page">
    <h1 class="reviewer-title">Review Audit</h1>
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading review tasks...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchReviewTasks" class="btn-retry">Retry</button>
    </div>
    
    <div v-else-if="audits.length === 0" class="no-data">
      <p>No review tasks found</p>
    </div>
    
    <DynamicTable
      v-else
      :title="'Review Tasks'"
      :data="filteredAudits"
      :columns="columns"
      :filters="filters"
      :uniqueKey="'audit_id'"
      :showPagination="true"
      :defaultPageSize="10"
    >
      <!-- Progress Bar Cell -->
      <template #cell-completion_percentage="{ row }">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${row.completion_percentage}%` }"
            :class="getProgressClass(row.completion_percentage)"
          ></div>
        </div>
        <span class="progress-text">{{ row.completion_percentage }}%</span>
      </template>
      <!-- Policy Cell -->
      <template #cell-policy="{ row }">
        {{ row.policy || 'All Policies' }}
      </template>
      <!-- Subpolicy Cell -->
      <template #cell-subpolicy="{ row }">
        {{ row.subpolicy || 'All Subpolicies' }}
      </template>
      <!-- Review Status Cell -->
      <template #cell-review_status="{ row }">
        <select 
          v-model="row.review_status" 
          @change="updateReviewStatus(row)" 
          class="review-status-select"
          v-if="row.status === 'Under review' && row.review_status !== 'Yet to Start' && row.review_status !== 'In Review' && row.review_status !== 'Reject'"
        >
          <option value="Accept">Accept</option>
          <option value="Reject">Reject</option>
        </select>
        <span v-else-if="row.review_status === 'Yet to Start' && row.status === 'Under review'">
          <button 
            @click="startReview(row)" 
            class="btn-review"
            title="Start review process"
          >
            Start
          </button>
        </span>
        <span v-else-if="(row.review_status === 'In Review' || row.review_status === 'Reject') && row.status === 'Under review'">
          <button 
            @click="openReviewDialog(row)" 
            class="btn-review btn-in-progress"
            title="Edit review in progress"
          >
            Edit Review
          </button>
          <span v-if="row.approved_rejected === 'Rejected'" class="approved-rejected-badge rejected" style="display: block; margin-top: 5px;">
            Rejected
          </span>
        </span>
        <span v-else>{{ row.review_status }}</span>
        <span v-if="row.approved_rejected && !(row.review_status === 'Reject' && row.status === 'Under review')" class="approved-rejected-badge" :class="getApprovedRejectedClass(row.approved_rejected)">
          {{ row.approved_rejected }}
        </span>
      </template>
      <!-- Download Button Cell -->
      <template #cell-download="{ row }">
        <button 
          class="btn-download" 
          :disabled="!canDownload(row)"
          @click="downloadAuditReport(row.audit_id)" 
          title="Download Audit Report"
        >
          <i class="fas fa-download"></i> Download
        </button>
      </template>
    </DynamicTable>
  </div>
</template>

<script>
import { api } from '../../data/api';
import axios from 'axios';
import DynamicTable from '../DynamicTable.vue';

// Get the API base URL from the imported api object, or default to '/api'
const API_BASE_URL = api.baseURL || '/api';

export default {
  name: 'ReviewerPage',
  components: { DynamicTable },
  data() {
    return {
      audits: [],
      loading: true,
      error: null,
      searchQuery: '',
      statusFilter: '',
      columns: [
        { key: 'audit_id', label: 'ID' },
        { key: 'framework', label: 'Framework' },
        { key: 'policy', label: 'Policy', slot: true },
        { key: 'subpolicy', label: 'Subpolicy', slot: true },
        { key: 'auditor', label: 'Auditor' },
        { key: 'duedate', label: 'Due Date' },
        { key: 'completion_percentage', label: 'Progress', slot: true },
        { key: 'status', label: 'Audit Status' },
        { key: 'review_status', label: 'Review Status', slot: true },
        { key: 'download', label: 'Download', slot: true },
      ],
      filters: [
        {
          name: 'statusFilter',
          label: 'Filter by Status',
          type: 'select',
          values: [
            { value: '', label: 'All Statuses' },
            { value: 'Yet to Start', label: 'Yet to Start' },
            { value: 'In Review', label: 'In Review' },
            { value: 'Accept', label: 'Accepted' },
            { value: 'Reject', label: 'Rejected' },
          ],
          defaultValue: '',
          filterFunction: (row, value) => !value || row.review_status === value
        }
      ]
    };
  },
  computed: {
    filteredAudits() {
      let audits = this.audits;
      // Status filter (handled by DynamicTable filterFunction)
      // Search filter - search in framework, policy, auditor
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        audits = audits.filter(audit => {
          const searchFields = [
            audit.framework,
            audit.policy,
            audit.subpolicy,
            audit.auditor,
            audit.status,
            audit.review_status
          ].filter(Boolean).map(field => field.toLowerCase());
          return searchFields.some(field => field.includes(query));
        });
      }
      return audits;
    },
  },
  created() {
    this.fetchReviewTasks();
  },
  methods: {
    async fetchReviewTasks() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Fetching review tasks...');
        const response = await api.getMyReviews();
        this.audits = response.data.audits;
        console.log(`Fetched ${this.audits.length} review tasks`);
      } catch (error) {
        console.error('Error fetching review tasks:', error);
        this.error = error.response?.data?.error || 'Failed to load review tasks. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    getProgressClass(percentage) {
      if (percentage < 30) return 'progress-low';
      if (percentage < 70) return 'progress-medium';
      return 'progress-high';
    },
    
    getApprovedRejectedClass(status) {
      if (status === 'Approved') return 'approved';
      if (status === 'Rejected') return 'rejected';
      return '';
    },
    
    canDownload(audit) {
      // Can download if the review status is Accept
      return audit.review_status === 'Accept' || audit.status === 'ACCEPTED' || audit.status === 'APPROVED';
    },
    
    async downloadAuditReport(auditId) {
      try {
        console.log(`Downloading audit report for audit ${auditId}`);
        this.$popup.success('Generating audit report...');
        
        // Create a direct URL for the download
        const reportUrl = `${API_BASE_URL}/generate-audit-report/${auditId}/`;
        console.log(`Downloading report from URL: ${reportUrl}`);
        
        // Use window.open for direct download
        window.open(reportUrl, '_blank');
        
        // Show success message
        this.$popup.success('Report download initiated');
      } catch (error) {
        console.error('Error initiating report download:', error);
        const errorMessage = error.message || 'Failed to download report. Please try again.';
        this.$popup.error(errorMessage);
      }
    },
    
    startReview(audit) {
      // Change review status to 'In Review'
      audit.review_status = 'In Review';
      this.updateReviewStatus(audit);
      
      // Open the review dialog
      this.openReviewDialog(audit);
    },
    
    openReviewDialog(audit) {
      // Navigate to the ReviewTaskView component with the audit ID
      console.log(`Opening review for audit ${audit.audit_id}`);
      
      // If this was just updated to "Under review" status, add a query parameter
      // to indicate this is a fresh review
      const freshReview = audit.justUpdatedToUnderReview === true;
      
      if (freshReview) {
        console.log('This is a fresh review after status change, adding freshReview parameter');
        this.$router.push(`/reviewer/task/${audit.audit_id}?freshReview=true`);
      } else {
        this.$router.push(`/reviewer/task/${audit.audit_id}`);
      }
    },
    
    async updateReviewStatus(audit) {
      try {
        console.log(`Updating review status for audit ${audit.audit_id} to ${audit.review_status}`);
        
        // Flag to track if we just updated to "Under review" status
        let justUpdatedToUnderReview = false;
        
        // Check if the audit is not in 'Under review' status
        if (audit.status !== 'Under review') {
          console.log(`Audit status is currently ${audit.status}, updating to 'Under review' first`);
          
          // First update the audit status to 'Under review' using direct axios.post call
          // to avoid any method inconsistencies
          try {
            console.log(`Making direct POST request to ${API_BASE_URL}/audits/${audit.audit_id}/status/`);
            const statusResponse = await axios.post(`${API_BASE_URL}/audits/${audit.audit_id}/status/`, {
              status: 'Under review'
            });
            console.log('Status update response:', statusResponse.data);
            
            // Update the local audit object
            audit.status = 'Under review';
            audit.justUpdatedToUnderReview = true; // Add flag to the audit object
            console.log('Audit status updated to Under review');
            justUpdatedToUnderReview = true;
          } catch (statusError) {
            console.error('Error updating audit status with direct axios:', statusError);
            console.error('Status code:', statusError.response?.status);
            console.error('Error message:', statusError.response?.data || statusError.message);
            
            // Try fallback to api.js implementation
            try {
              console.log('Trying fallback to api.updateAuditStatus...');
              const fallbackResponse = await api.updateAuditStatus(audit.audit_id, {
                status: 'Under review'
              });
              console.log('Fallback status update successful:', fallbackResponse.data);
              
              // Update the local audit object
              audit.status = 'Under review';
              audit.justUpdatedToUnderReview = true;
              console.log('Audit status updated to Under review via fallback');
              justUpdatedToUnderReview = true;
            } catch (fallbackError) {
              console.error('Both direct and fallback status update methods failed:', fallbackError);
              this.$popup.error(`Failed to update audit status. Please try again later. Error: ${fallbackError.message || 'Unknown error'}`);
              throw fallbackError;
            }
          }
        }
        
        // Prompt for review comments if status is being set to Reject
        let review_comments = '';
        if (audit.review_status === 'Reject') {
          review_comments = await this.$popup.comment('Please provide rejection comments:', 'Rejection Comments');
          if (review_comments === null) {
            // User cancelled the prompt, revert the status change
            this.fetchReviewTasks();
            return;
          }
        } else if (audit.review_status === 'Accept') {
          // Optionally prompt for approval comments
          review_comments = await this.$popup.comment('Please provide any approval comments (optional):', 'Approval Comments');
          if (review_comments === null) {
            // User cancelled the prompt, revert the status change
            this.fetchReviewTasks();
            return;
          }
        }
        
        const response = await api.updateReviewStatus(audit.audit_id, {
          review_status: audit.review_status,
          review_comments: review_comments
        });
        
        console.log('Review status updated successfully:', response.data);
        
        // Update the local audit object with the comments
        audit.review_comments = review_comments;
        
        // If accepted, update audit status to Completed
        if (audit.review_status === 'Accept' && response.data.audit_status) {
          audit.status = response.data.audit_status;
        }
        
        // Show success message
        this.$popup.success('Review status updated successfully!');
        
        // If we just updated to "Under review" and the review status is "In Review",
        // automatically open the review dialog
        if (justUpdatedToUnderReview && audit.review_status === 'In Review') {
          console.log('Automatically opening review dialog after status update');
          this.openReviewDialog(audit);
        }
        
      } catch (error) {
        console.error('Error updating review status:', error);
        // Revert the status change on error
        this.fetchReviewTasks(); // Reload data from server
        this.$popup.error(error.response?.data?.error || 'Failed to update review status. Please try again.');
      }
    },
  }
};
</script>

<style scoped>
@import '../styles/theme.css';
@import './Reviewer.css';
</style>