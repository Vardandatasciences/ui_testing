<template>
  <div class="incident-details-page">
    <div class="incident-details-header">
      <router-link to="/incident/incident" class="incident-back-link">
        <span class="incident-back-arrow">←</span>
        <span class="back-text">Back to Incidents</span>
      </router-link>
    </div>

    <div v-if="loading" class="incident-loading-state">
      Loading incident details...
    </div>

    <div v-else-if="error" class="incident-error-state">
      {{ error }}
    </div>

    <div class="incident-details-content" v-else-if="incident">
      <!-- Title Section with Incident ID -->
      <div class="incident-header-section">
        <div class="incident-title-container">
          <div class="incident-title-section">
            <h1 class="incident-title">{{ incident.IncidentTitle }}</h1>
            <div class="incident-id">Incident #{{ incident?.IncidentId }}</div>
          </div>
          <div class="incident-status-container">
            <!-- Handle all possible status values -->
            <span v-if="incident.Status === 'Scheduled'" class="incident-status-badge incident-scheduled">Mitigated to Risk</span>
            <span v-else-if="incident.Status === 'Rejected'" class="incident-status-badge incident-rejected">
              {{ incident.RejectionSource === 'RISK' ? 'Rejected from Risk' : 'Rejected as Incident' }}
            </span>
            <span v-else-if="incident.Status === 'Assigned'" class="incident-status-badge incident-assigned">Assigned</span>
            <span v-else-if="incident.Status === 'Approved'" class="incident-status-badge incident-approved">Approved</span>
            <span v-else-if="incident.Status === 'Active'" class="incident-status-badge incident-active">Active</span>
            <span v-else-if="incident.Status === 'Under Review'" class="incident-status-badge incident-under-review">Under Review</span>
            <span v-else-if="incident.Status === 'Completed'" class="incident-status-badge incident-completed">Completed</span>
            <span v-else-if="incident.Status === 'Closed'" class="incident-status-badge incident-closed">Closed</span>
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
            <span :class="['incident-priority-badge', getPriorityClass(incident.RiskPriority)]">
              {{ incident.RiskPriority || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Category</span>
            <span class="incident-category-badge" :class="getRiskCategoryClass(incident.RiskCategory)">
              {{ incident.RiskCategory || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Origin</span>
            <span class="incident-origin-badge" :class="getOriginClass(incident.Origin)">
              {{ incident.Origin || 'Not Set' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Criticality</span>
            <span class="incident-detail-value">{{ incident.Criticality || 'Not Set' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Date</span>
            <span class="incident-detail-value">{{ formatDate(incident.Date) }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Time</span>
            <span class="incident-detail-value">{{ incident.Time || 'Not Set' }}</span>
          </div>
        </div>
      </div>

      <!-- Description Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Description</h2>
        <div class="incident-description-content">
          <div class="incident-detail-value incident-description-value">
            {{ incident.Description || 'No description provided' }}
          </div>
        </div>
      </div>

      <!-- Impact & Assessment Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Impact & Assessment</h2>
        <div class="incident-impact-grid">
          <div class="incident-detail-item">
            <span class="incident-detail-label">Affected Business Unit</span>
            <span class="incident-detail-value">{{ incident.AffectedBusinessUnit || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Systems/Assets Involved</span>
            <span class="incident-detail-value">{{ incident.SystemsAssetsInvolved || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Geographic Location</span>
            <span class="incident-detail-value">{{ incident.GeographicLocation || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Cost of Incident</span>
            <span class="incident-detail-value">{{ incident.CostOfIncident || 'Not specified' }}</span>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Initial Impact Assessment</span>
            <div class="incident-detail-value incident-description-style">
              {{ incident.InitialImpactAssessment || 'No assessment provided' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Possible Damage</span>
            <div class="incident-detail-value incident-description-style">
              {{ incident.PossibleDamage || 'No damage assessment provided' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline & Events Section -->
      <!-- <div class="details-section">
        <h2 class="section-title">Timeline & Events</h2>
        <div class="timeline-content">
          <div class="detail-value description-style">
            {{ incident.TimelineOfEvents || 'No timeline provided' }}
          </div>
        </div>
      </div> -->

      <!-- Contacts & Parties Section -->
      <div class="incident-details-section">
        <h2 class="incident-section-title">Contacts & Involved Parties</h2>
        <div class="incident-impact-grid">
          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Internal Contacts</span>
            <div class="incident-detail-value incident-description-style">
              {{ incident.InternalContacts || 'No internal contacts specified' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">External Parties Involved</span>
            <div class="incident-detail-value incident-description-style">
              {{ incident.ExternalPartiesInvolved || 'No external parties specified' }}
            </div>
          </div>

          <div class="incident-detail-item incident-full-width">
            <span class="incident-detail-label">Regulatory Bodies</span>
            <div class="incident-detail-value incident-description-style">
              {{ incident.RegulatoryBodies || 'No regulatory bodies involved' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Compliance & Controls Section -->
      <!-- Compliance & Controls Section -->
<div class="incident-details-section">
  <h2 class="incident-section-title">Compliance & Controls</h2>
  <div class="incident-compliance-grid">
    <div class="incident-detail-item">
      <span class="incident-detail-label">Relevant Policies/Procedures Violated</span>
      <div class="incident-detail-value incident-description-style">
        {{ incident.RelevantPoliciesProceduresViolated || 'No violations identified' }}
      </div>
    </div>

    <div class="incident-detail-item">
      <span class="incident-detail-label">Control Failures</span>
      <div class="incident-detail-value incident-description-style">
        {{ incident.ControlFailures || 'No control failures identified' }}
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
              {{ incident.Mitigation || 'No mitigation plan provided' }}
            </div>
          </div>

          <div class="incident-response-item comments-section">
            <div class="incident-section-header">
              <i class="fas fa-comments"></i>
              Comments
            </div>
            <div class="incident-section-content">
              {{ incident.Comments || 'No comments available' }}
            </div>
          </div>

          <div class="incident-response-item lessons-section">
            <div class="incident-section-header">
              <i class="fas fa-lightbulb"></i>
              Lessons Learned
            </div>
            <div class="incident-section-content">
              {{ incident.LessonsLearned || 'No lessons learned documented' }}
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
            <span :class="['incident-flag-badge', incident.RepeatedNot ? 'incident-flag-yes' : 'incident-flag-no']">
              {{ incident.RepeatedNot ? 'Yes' : 'No' }}
            </span>
          </div>

          <div class="incident-detail-item">
            <span class="incident-detail-label">Reopened Incident</span>
            <span :class="['incident-flag-badge', incident.ReopenedNot ? 'incident-flag-yes' : 'incident-flag-no']">
              {{ incident.ReopenedNot ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="incident-details-footer">
        <!-- Show status info for non-open incidents -->
        <div v-if="incident.Status === 'Scheduled'">
          <span class="incident-status-badge incident-scheduled">Mitigated to Risk</span>
        </div>
        <div v-else-if="incident.Status === 'Rejected'">
          <span class="incident-status-badge incident-rejected">
            {{ incident.RejectionSource === 'RISK' ? 'Rejected from Risk' : 'Rejected as Incident' }}
          </span>
        </div>
        <div v-else-if="incident.Status === 'Assigned'">
          <span class="incident-status-badge incident-assigned">Assigned</span>
        </div>
        <div v-else-if="incident.Status === 'Approved'">
          <span class="incident-status-badge incident-approved">Approved</span>
        </div>
        <div v-else-if="incident.Status === 'Active'">
          <span class="incident-status-badge incident-active">Active</span>
        </div>
        <div v-else-if="incident.Status === 'Under Review'">
          <span class="incident-status-badge incident-under-review">Under Review</span>
        </div>
        <div v-else-if="incident.Status === 'Completed'">
          <span class="incident-status-badge incident-completed">Completed</span>
        </div>
        <div v-else-if="incident.Status === 'Closed'">
          <span class="incident-status-badge incident-closed">Closed</span>
        </div>
        <!-- Show action buttons only for Open incidents -->
        <div v-else class="incident-action-buttons">
          <button @click="openSolveModal" class="incident-solve-btn">
            <i class="fas fa-arrow-up"></i>
            ESCALATE TO RISK
          </button>
          <button @click="openRejectModal" class="incident-no-btn">
            <i class="fas fa-times"></i>
            REJECT INCIDENT
          </button>
          <!-- Show message if no permissions -->
          <div 
            v-if="!canEscalateIncident() && !canEditIncident()" 
            class="no-permission-message"
          >
            <i class="fas fa-lock"></i>
            <span>No actions available - insufficient permissions</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import axios from 'axios';
import './IncidentDetails.css';
import { PopupService, PopupModal } from '@/modules/popup';
import { permissionMixin } from '@/mixins/permissionMixin.js';

  export default {
    name: 'IncidentDetails',
    components: {
      PopupModal
    },
    mixins: [permissionMixin],
    data() {
    return {
      incident: null,
      loading: true,
      error: null,
      
    }
  },
  async created() {
    await this.fetchIncidentDetails();
  },
  methods: {
    async fetchIncidentDetails() {
      try {
        this.loading = true;
        this.error = null;
        const incidentId = this.$route.params.id;
        console.log('Fetching incident:', incidentId);
        
        // RBAC Debug - Log user action attempt
        this.logUserAction('VIEW_INCIDENT_DETAILS', 'incident', incidentId);
        
        // Check permissions
        if (!this.canViewIncident()) {
          console.warn('❌ Permission denied for viewing incident details');
          this.error = 'You do not have permission to view incident details.';
          return;
        }
        
        console.log('✅ Permission granted for viewing incident details');
        
        // Get all incidents and filter for the one we want
        const response = await axios.get('http://localhost:8000/api/incident-incidents/');
        const allIncidents = response.data;
        
        // Find the specific incident
        this.incident = allIncidents.find(inc => inc.IncidentId.toString() === incidentId.toString());
        
        if (!this.incident) {
          throw new Error('Incident not found');
        }
        
        console.log('Fetched incident:', this.incident);
      } catch (error) {
        console.error('Failed to fetch incident details:', error);
        this.error = 'Failed to load incident details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
          openSolveModal() {
        // RBAC Debug - Log user action attempt
        this.logUserAction('ESCALATE_INCIDENT', 'incident', this.incident?.IncidentId);
        
        // Check permissions
        if (!this.canEscalateIncident()) {
          console.warn('❌ Permission denied for escalating incident');
          PopupService.error("You don't have permission to escalate incidents");
          return;
        }
        
        console.log('✅ Permission granted for escalating incident');
        
        PopupService.confirm(
          'This incident will be forwarded to the Risk module. Do you want to proceed?',
          'Forward to Risk',
          () => this.confirmSolve(),
          () => {} // Cancel action
        );
      },
      openRejectModal() {
        // RBAC Debug - Log user action attempt
        this.logUserAction('REJECT_INCIDENT', 'incident', this.incident?.IncidentId);
        
        // Check permissions
        if (!this.canEditIncident()) {
          console.warn('❌ Permission denied for rejecting incident');
          PopupService.error("You don't have permission to reject incidents");
          return;
        }
        
        console.log('✅ Permission granted for rejecting incident');
        
        PopupService.confirm(
          'Are you sure you want to reject this incident?',
          'Reject Incident',
          () => this.confirmReject(),
          () => {} // Cancel action
        );
      },
    confirmSolve() {
      // Update incident status to "Scheduled"
      axios.put(`http://localhost:8000/incidents/${this.incident.IncidentId}/status/`, {
        status: 'Scheduled'
      })
      .then(response => {
        console.log('Incident escalated to risk:', response.data);
        
        // Update local incident status
        this.incident.Status = 'Scheduled';
        
                  // Show success message and redirect to Risk module
          PopupService.success('Incident forwarded to Risk module successfully!');
          
          // Redirect to Risk module after 2 seconds
          setTimeout(() => {
            // this.$router.push('/risk');
          }, 2000);
      })
      .catch(error => {
        console.error('Error updating incident status:', error);
      });
    },
    confirmReject() {
      // Update incident status to "Rejected"
      axios.put(`http://localhost:8000/incidents/${this.incident.IncidentId}/status/`, {
        status: 'Rejected'
      })
      .then(response => {
        console.log('Incident rejected:', response.data);
        
                  // Update local incident status
          this.incident.Status = 'Rejected';
          
          // Show success message
          PopupService.success('Incident rejected successfully!');
      })
      .catch(error => {
        console.error('Error updating incident status:', error);
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