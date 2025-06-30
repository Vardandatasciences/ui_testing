<template>
  <div class="risk-view-container">
    <PopupModal />
    
    <div class="risk-view-header">
      <h2 class="risk-view-title"><i class="fas fa-exclamation-triangle risk-view-icon"></i> Risk Details</h2>
      <button class="risk-view-back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back to Risk Register
      </button>
    </div>

    <div class="risk-view-details-card" v-if="risk">
      <div class="risk-view-details-top">
        <div class="risk-view-id-section">
          <span class="risk-view-id-label">Risk ID:</span>
          <span class="risk-view-id-value">{{ risk.RiskId }}</span>
        </div>
        <div class="risk-view-meta">
          <div class="risk-view-category">{{ risk.Category }}</div>
          <div class="risk-view-criticality" :class="getCriticalityClass(risk.Criticality)">{{ risk.Criticality }}</div>
        </div>
      </div>

      <div class="risk-view-title-section">
        <h3>{{ risk.RiskTitle }}</h3>
        <div class="risk-view-compliance-section">
          <span class="risk-view-compliance-label">Compliance ID:</span>
          <span class="risk-view-compliance-value">{{ risk.ComplianceId || 'N/A' }}</span>
        </div>
      </div>

      <div class="risk-view-content">
        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Description:</h4>
            <div class="risk-view-section-content">{{ risk.RiskDescription || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Business Impact:</h4>
            <div class="risk-view-section-content">{{ risk.BusinessImpact || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Possible Damage:</h4>
            <div class="risk-view-section-content">{{ risk.PossibleDamage || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Likelihood:</h4>
            <div class="risk-view-section-content">{{ risk.RiskLikelihood || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Impact:</h4>
            <div class="risk-view-section-content">{{ risk.RiskImpact || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Exposure Rating:</h4>
            <div class="risk-view-section-content">{{ risk.RiskExposureRating || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Priority:</h4>
            <div class="risk-view-section-content">{{ risk.RiskPriority || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Risk Mitigation:</h4>
            <div class="risk-view-section-content">{{ risk.RiskMitigation || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Created At:</h4>
            <div class="risk-view-section-content">{{ formatDate(risk.CreatedAt) }}</div>
          </div>
          <div class="risk-view-content-column">
            <!-- Empty column for alignment -->
          </div>
        </div>
      </div>
    </div>

    <div v-else class="risk-view-no-data">
      Loading risk details or no risk found...
    </div>
  </div>
</template>

<script>
import './ViewRisk.css'
import axios from 'axios'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'ViewRisk',
  components: {
    PopupModal
  },
  data() {
    return {
      risk: null
    }
  },
  created() {
    this.fetchRiskDetails()
  },
  methods: {
    fetchRiskDetails() {
      const riskId = this.$route.params.id
      if (!riskId) {
        this.$router.push('/risk/riskregister-list')
        return
      }

      axios.get(`http://localhost:8000/api/risks/${riskId}/`)
        .then(response => {
          this.risk = response.data
        })
        .catch(error => {
          console.error('Error fetching risk details:', error)
        })
    },
    getCriticalityClass(criticality) {
      if (!criticality) return ''
      criticality = criticality.toLowerCase()
      if (criticality === 'critical') return 'risk-view-priority-critical'
      if (criticality === 'high') return 'risk-view-priority-high'
      if (criticality === 'medium') return 'risk-view-priority-medium'
      if (criticality === 'low') return 'risk-view-priority-low'
      return ''
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString()
    },
    goBack() {
      this.$router.push('/risk/riskregister-list')
    }
  }
}
</script> 