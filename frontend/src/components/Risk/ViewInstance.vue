<template>
  <div class="risk-view-instance-container">
    <PopupModal />
    
    <div class="risk-view-instance-header">
      <h2 class="risk-view-instance-title"><i class="fas fa-exclamation-triangle risk-view-instance-icon"></i> Risk Instance Details</h2>
      <button class="risk-view-instance-back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back to Risk Instances
      </button>
    </div>

    <div class="risk-view-instance-details-card" v-if="instance">
      <div class="risk-view-instance-details-header">
        <div class="risk-view-instance-id-section">
          <span class="risk-view-instance-id-label">Risk ID:</span>
          <span class="risk-view-instance-id-value">{{ instance.RiskId }}</span>
          <span class="risk-view-instance-id-label">Instance ID:</span>
          <span class="risk-view-instance-id-value">{{ instance.RiskInstanceId }}</span>
        </div>
        <div class="risk-view-instance-meta">
          <div class="risk-view-instance-meta-item">
            <span class="risk-view-instance-origin-badge">MANUAL</span>
          </div>
          <div class="risk-view-instance-meta-item">
            <span class="risk-view-instance-category-badge">{{ instance.Category }}</span>
          </div>
          <div class="risk-view-instance-meta-item">
            <span :class="'risk-view-instance-priority-' + instance.Criticality.toLowerCase()">
              {{ instance.Criticality }}
            </span>
          </div>
          <div class="risk-view-instance-meta-item">
            <span :class="'risk-view-instance-status-' + (instance.RiskStatus ? instance.RiskStatus.toLowerCase().replace(/\s+/g, '-') : 'open')">
              {{ instance.RiskStatus || 'Open' }}
            </span>
          </div>
        </div>
      </div>

      <div class="risk-view-instance-details-grid">
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Description:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskDescription }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Category:</span>
          <span class="risk-view-instance-detail-value">{{ instance.Category }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Criticality:</span>
          <span class="risk-view-instance-detail-value" :class="'risk-view-instance-priority-' + instance.Criticality.toLowerCase()">
            {{ instance.Criticality }}
          </span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Status:</span>
          <span class="risk-view-instance-detail-value" :class="'risk-view-instance-status-' + (instance.RiskStatus ? instance.RiskStatus.toLowerCase().replace(/\s+/g, '-') : 'open')">
            {{ instance.RiskStatus || 'Open' }}
          </span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Possible Damage:</span>
          <span class="risk-view-instance-detail-value">{{ instance.PossibleDamage || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Risk Appetite:</span>
          <span class="risk-view-instance-detail-value">{{ instance.Appetite || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Likelihood:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskLikelihood || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Impact:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskImpact || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Exposure Rating:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskExposureRating || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Priority:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskPriority || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Response Type:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskResponseType || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Response Description:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskResponseDescription || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Mitigation:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskMitigation || 'Not specified' }}</span>
        </div>
        <div class="risk-view-instance-detail-item">
          <span class="risk-view-instance-detail-label">Risk Owner:</span>
          <span class="risk-view-instance-detail-value">{{ instance.RiskOwner || 'Not assigned' }}</span>
        </div>
      </div>
    </div>

    <div v-else class="risk-view-instance-no-data">
      Loading instance details or no instance found...
    </div>
  </div>
</template>

<script>
import './ViewInstance.css'
import axios from 'axios'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'ViewInstance',
  components: {
    PopupModal
  },
  data() {
    return {
      instance: null
    }
  },
  created() {
    this.fetchInstanceDetails()
  },
  methods: {
    fetchInstanceDetails() {
      const instanceId = this.$route.params.id
      if (!instanceId) {
        this.$router.push('/risk/riskinstances-list')
        return
      }

      axios.get(`http://localhost:8000/api/risk-instances/${instanceId}/`)
        .then(response => {
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error fetching risk instance details:', error)
          // Try alternative endpoint if the first one fails
          this.tryAlternativeEndpoint(instanceId)
        })
    },
    tryAlternativeEndpoint(instanceId) {
      axios.get(`http://localhost:8000/risk-instances/${instanceId}/`)
        .then(response => {
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error with alternative endpoint:', error)
        })
    },
    goBack() {
      this.$router.push('/risk/riskinstances-list')
    }
  }
}
</script> 