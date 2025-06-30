<template>
  <div class="incident-details-page">
    <div class="incident-details-header">
      <router-link to="/incident/audit-findings" class="incident-back-link">
        <span class="incident-back-arrow">←</span>
        <span class="back-text">Back to Audit Findings</span>
      </router-link>
    </div>

    <div v-if="loading" class="incident-loading-state">
      Loading audit finding details...
    </div>

    <div v-else-if="error" class="incident-error-state">
      {{ error }}
    </div>

    <div class="incident-details-content" v-else-if="auditFinding">
      <!-- Title Section with Audit Finding ID -->
      <div class="incident-header-section">
        <div class="incident-title-container">
          <div class="incident-title-section">
            <h1 class="incident-title">{{ auditFinding.IncidentTitle }}</h1>
            <div class="incident-id">Audit Finding #{{ auditFinding?.IncidentId }}</div>
          </div>
          <div class="incident-status-container">
            <!-- Handle all possible status values -->
            <span v-if="auditFinding.Status === 'Scheduled'" class="incident-status-badge incident-scheduled">Mitigated to Risk</span>
            <span v-else-if="auditFinding.Status === 'Rejected'" class="incident-status-badge incident-rejected">
              {{ auditFinding.RejectionSource === 'RISK' ? 'Rejected from Risk' : 'Rejected as Audit Finding' }}
            </span>
            <span v-else-if="auditFinding.Status === 'Assigned'" class="incident-status-badge incident-assigned">Assigned</span>
            <span v-else-if="auditFinding.Status === 'Approved'" class="incident-status-badge incident-approved">Approved</span>
            <span v-else-if="auditFinding.Status === 'Active'" class="incident-status-badge incident-active">Active</span>
            <span v-else-if="auditFinding.Status === 'Under Review'" class="incident-status-badge incident-under-review">Under Review</span>
            <span v-else-if="auditFinding.Status === 'Completed'" class="incident-status-badge incident-completed">Completed</span>
            <span v-else-if="auditFinding.Status === 'Closed'" class="incident-status-badge incident-closed">Closed</span>
            <span v-else class="incident-status-badge incident-open">Open</span>
          </div>
        </div>
      </div>

      <!-- Basic Information Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Basic Information</h2>
        <div class="incident-basic-info-grid">
          <div class="incident-detail-item">
            <span class="incident-detail-label">Priority</span>
            <span :class="['incident-priority-badge', getPriorityClass(auditFinding.RiskPriority)]">
              {{ auditFinding.RiskPriority || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Category</span>
            <span class="incident-category-badge" :class="getRiskCategoryClass(auditFinding.RiskCategory)">
              {{ auditFinding.RiskCategory || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Origin</span>
            <span class="incident-origin-badge" :class="getOriginClass(auditFinding.Origin)">
              {{ auditFinding.Origin || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Criticality</span>
            <span class="incident-detail-value">{{ auditFinding.Criticality || 'Not Set' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Date</span>
            <span class="incident-detail-value">{{ formatDate(auditFinding.Date) }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Time</span>
            <span class="incident-detail-value">{{ auditFinding.Time || 'Not Set' }}</span>
          </div>
        </div>
      </div>

      <!-- Description Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Description</h2>
        <div class="incident-description-content">
          <div class="incident-detail-value incident-description-value">
            {{ auditFinding.Description || 'No description provided' }}
          </div>
        </div>
      </div>

      <!-- Impact & Assessment Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Impact & Assessment</h2>
        <div class="incident-impact-grid">
          <div class="incident-detail-item">
            <span class="incident-detail-label">Affected Business Unit</span>
            <span class="incident-detail-value">{{ auditFinding.AffectedBusinessUnit || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Systems/Assets Involved</span>
            <span class="incident-detail-value">{{ auditFinding.SystemsAssetsInvolved || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Geographic Location</span>
            <span class="incident-detail-value">{{ auditFinding.GeographicLocation || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Cost of Incident</span>
            <span class="incident-detail-value">{{ auditFinding.CostOfIncident || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Initial Impact Assessment</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.InitialImpactAssessment || 'No assessment provided' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Possible Damage</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.PossibleDamage || 'No damage assessment provided' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Contacts & Parties Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Contacts & Involved Parties</h2>
        <div class="incident-impact-grid">
          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Internal Contacts</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.InternalContacts || 'No internal contacts specified' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">External Parties Involved</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.ExternalPartiesInvolved || 'No external parties specified' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Regulatory Bodies</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.RegulatoryBodies || 'No regulatory bodies involved' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Compliance & Controls Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Compliance & Controls</h2>
        <div class="incident-compliance-grid">
          <div class="incident-detail-item">
            <span class="incident-detail-label">Relevant Policies/Procedures Violated</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.RelevantPoliciesProceduresViolated || 'No violations identified' }}
            </div>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Control Failures</span>
            <div class="incident-detail-value incident-description-style">
              {{ auditFinding.ControlFailures || 'No control failures identified' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Response & Resolution Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Response & Resolution</h2>
        <div class="incident-response-grid">
          <div class="incident-response-item mitigation-section">
            <div class="incident-section-header">
              <i class="fas fa-shield-alt"></i>
              Mitigation Plan
            </div>
            <div class="incident-section-content">
              {{ auditFinding.Mitigation || 'No mitigation plan provided' }}
            </div>
          </div>

          <div class="incident-response-item comments-section">
            <div class="incident-section-header">
              <i class="fas fa-comments"></i>
              Comments
            </div>
            <div class="incident-section-content">
              {{ auditFinding.Comments || 'No comments available' }}
            </div>
          </div>

          <div class="incident-response-item lessons-section">
            <div class="incident-section-header">
              <i class="fas fa-lightbulb"></i>
              Lessons Learned
            </div>
            <div class="incident-section-content">
              {{ auditFinding.LessonsLearned || 'No lessons learned documented' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Information Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Additional Information</h2>
        <div class="incident-basic-info-grid">
          <div class="incident-detail-item">
            <span class="incident-detail-label">Repeated Incident</span>
            <span :class="['incident-flag-badge', auditFinding.RepeatedNot ? 'incident-flag-yes' : 'incident-flag-no']">
              {{ auditFinding.RepeatedNot ? 'Yes' : 'No' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Reopened Incident</span>
            <span :class="['incident-flag-badge', auditFinding.ReopenedNot ? 'incident-flag-yes' : 'incident-flag-no']">
              {{ auditFinding.ReopenedNot ? 'Yes' : 'No' }}
            </span>
          </div>

          <div class="incident-detail-item" v-if="auditFinding.ComplianceId">
            <span class="incident-detail-label">Compliance ID</span>
            <span class="incident-detail-value">{{ auditFinding.ComplianceId }}</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="incident-details-footer">
        <!-- Show status info for non-open audit findings -->
        <div v-if="auditFinding.Status === 'Scheduled'">
          <span class="incident-status-badge incident-scheduled">Mitigated to Risk</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Rejected'">
          <span class="incident-status-badge incident-rejected">
            {{ auditFinding.RejectionSource === 'RISK' ? 'Rejected from Risk' : 'Rejected as Audit Finding' }}
          </span>
        </div>
        <div v-else-if="auditFinding.Status === 'Assigned'">
          <span class="incident-status-badge incident-assigned">Assigned</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Approved'">
          <span class="incident-status-badge incident-approved">Approved</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Active'">
          <span class="incident-status-badge incident-active">Active</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Under Review'">
          <span class="incident-status-badge incident-under-review">Under Review</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Completed'">
          <span class="incident-status-badge incident-completed">Completed</span>
        </div>
        <div v-else-if="auditFinding.Status === 'Closed'">
          <span class="incident-status-badge incident-closed">Closed</span>
        </div>
        <!-- Show action buttons only for Open audit findings -->
        <div v-else class="incident-action-buttons">
          <button @click="openSolveModal" class="incident-solve-btn">
            <i class="fas fa-arrow-up"></i>
            ESCALATE TO RISK
          </button>
          <button @click="openRejectModal" class="incident-no-btn">
            <i class="fas fa-times"></i>
            REJECT AUDIT FINDING
          </button>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import axios from 'axios';
import './IncidentDetails.css'; // Reuse the same CSS
import { PopupService, PopupModal } from '@/modules/popup';

export default {
  name: 'AuditFindingDetails',
  components: {
    PopupModal
  },
  data() {
    return {
      auditFinding: null,
      loading: true,
      error: null,
    }
  },
  async created() {
    await this.fetchAuditFindingDetails();
  },
  methods: {
    async fetchAuditFindingDetails() {
      try {
        this.loading = true;
        this.error = null;
        const incidentId = this.$route.params.id;
        console.log('Fetching audit finding:', incidentId);
        
        // Use the new audit finding incident detail endpoint
        const response = await axios.get(`http://localhost:8000/api/audit-findings/incident/${incidentId}/`);
        
        if (response.data.success) {
          this.auditFinding = response.data.data;
          console.log('Fetched audit finding:', this.auditFinding);
        } else {
          throw new Error(response.data.message || 'Failed to fetch audit finding details');
        }
        
      } catch (error) {
        console.error('Failed to fetch audit finding details:', error);
        this.error = 'Failed to load audit finding details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    openSolveModal() {
      PopupService.confirm(
        'This audit finding will be forwarded to the Risk module. Do you want to proceed?',
        'Forward to Risk',
        () => this.confirmSolve(),
        () => {} // Cancel action
      );
    },
    openRejectModal() {
      PopupService.confirm(
        'Are you sure you want to reject this audit finding?',
        'Reject Audit Finding',
        () => this.confirmReject(),
        () => {} // Cancel action
      );
    },
    confirmSolve() {
      // Update audit finding status to "Scheduled"
      axios.put(`http://localhost:8000/api/incidents/${this.auditFinding.IncidentId}/status/`, {
        status: 'Scheduled'
      })
      .then(response => {
        console.log('Audit finding escalated to risk:', response.data);
        
        // Update local audit finding status
        this.auditFinding.Status = 'Scheduled';
        
        // Show success message with incident ID - same format as incidents page
        PopupService.success(`Incident ${this.auditFinding.IncidentId} escalated to Risk successfully!`);
        
        // Redirect to incidents page after 2 seconds
        setTimeout(() => {
          this.$router.push('/incident/incident');
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating audit finding status:', error);
        PopupService.error('Failed to escalate audit finding. Please try again.');
      });
    },
    confirmReject() {
      // Update audit finding status to "Rejected"
      axios.put(`http://localhost:8000/api/incidents/${this.auditFinding.IncidentId}/status/`, {
        status: 'Rejected'
      })
      .then(response => {
        console.log('Audit finding rejected:', response.data);
        
        // Update local audit finding status
        this.auditFinding.Status = 'Rejected';
        
        // Show success message with incident ID - same format as incidents page
        PopupService.success(`Incident ${this.auditFinding.IncidentId} rejected successfully!`);
        
        // Redirect to incidents page after 2 seconds
        setTimeout(() => {
          this.$router.push('/incident/incident');
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating audit finding status:', error);
        PopupService.error('Failed to reject audit finding. Please try again.');
      });
    },
    getPriorityClass(priority) {
      switch(priority?.toLowerCase()) {
        case 'high': return 'incident-priority-high';
        case 'medium': return 'incident-priority-medium';
        case 'low': return 'incident-priority-low';
        default: return '';
      }
    },
    getRiskCategoryClass(category) {
      if (!category) return '';
      const categoryLower = category.toLowerCase();
      if (categoryLower.includes('security')) return 'incident-category-security';
      if (categoryLower.includes('compliance')) return 'incident-category-compliance';
      if (categoryLower.includes('operational')) return 'incident-category-operational';
      if (categoryLower.includes('financial')) return 'incident-category-financial';
      if (categoryLower.includes('strategic')) return 'incident-category-strategic';
      return 'incident-category-other';
    },
    getOriginClass(origin) {
      const originType = origin?.toLowerCase() || '';
      if (originType.includes('manual')) return 'incident-origin-manual';
      if (originType.includes('audit')) return 'incident-origin-audit';
      if (originType.includes('siem')) return 'incident-origin-siem';
      return 'incident-origin-other';
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const [year, month, day] = dateString.split('-');
      return `${month}/${day}/${year}`;
    }
  }
}
</script> 