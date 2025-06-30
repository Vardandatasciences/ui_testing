<!--
  Control Detail View
  This component displays detailed information about controls (compliances)
  when navigated to from the Control Management page.
-->

<template>
  <div class="compliance-view-container">
    <div class="compliance-header">
      <h2>{{ title }}</h2>
      <div class="compliance-actions">
        <button @click="goBack" class="compliance-back-btn">Back</button>
      </div>
    </div>

    <div v-if="loading" class="compliance-loading">
      <div class="compliance-spinner"></div>
      <p>Loading compliances...</p>
    </div>

    <div v-else-if="error" class="compliance-error">
      <p>{{ error }}</p>
      <button @click="retryLoading" class="compliance-retry-btn">Retry</button>
    </div>

    <div v-else-if="!compliances.length" class="compliance-empty">
      <p>No compliances found.</p>
    </div>

    <div v-else class="compliance-list">
      <div v-for="compliance in compliances" :key="compliance.ComplianceId" class="compliance-item">
        <div class="compliance-item-header">
          <h3>{{ compliance.ComplianceItemDescription }}</h3>
          <div class="compliance-item-meta">
            <span class="compliance-status" :class="compliance.Status.toLowerCase()">{{ compliance.Status }}</span>
            <span class="compliance-criticality" :class="compliance.Criticality.toLowerCase()">{{ compliance.Criticality }}</span>
          </div>
        </div>

        <div class="compliance-item-details">
          <div class="compliance-detail">
            <strong>Maturity Level:</strong> {{ compliance.MaturityLevel }}
          </div>
          <div class="compliance-detail">
            <strong>Type:</strong> {{ compliance.MandatoryOptional }}
          </div>
          <div class="compliance-detail">
            <strong>Implementation:</strong> {{ compliance.ManualAutomatic }}
          </div>
          <div class="compliance-detail">
            <strong>Created By:</strong> {{ compliance.CreatedByName }}
          </div>
          <div class="compliance-detail">
            <strong>Created Date:</strong> {{ compliance.CreatedByDate }}
          </div>
          <div class="compliance-detail">
            <strong>Version:</strong> {{ compliance.ComplianceVersion }}
          </div>
          <div class="compliance-detail">
            <strong>Identifier:</strong> {{ compliance.Identifier }}
          </div>
          <div class="compliance-detail">
            <strong>SubPolicy:</strong> {{ compliance.SubPolicyName }}
          </div>
          <div class="compliance-detail">
            <strong>Policy:</strong> {{ compliance.PolicyName }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref(null);
const compliances = ref([]);

const title = computed(() => {
  const name = decodeURIComponent(route.params.name || '');
  return `Compliances for ${route.params.type}: ${name}`;
});

const fetchCompliances = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const response = await axios.get(`/compliances/${route.params.type}/${route.params.id}/`);
    
    if (response.data.success) {
      compliances.value = response.data.compliances;
    } else {
      error.value = 'Failed to load compliances';
    }
  } catch (err) {
    console.error('Error fetching compliances:', err);
    error.value = 'Failed to load compliances. Please try again.';
  } finally {
    loading.value = false;
  }
};

const retryLoading = () => {
  fetchCompliances();
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  fetchCompliances();
});
</script>

<style>
.compliance-view-container {
  padding: 20px;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.compliance-back-btn {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.compliance-loading {
  text-align: center;
  padding: 40px;
}

.compliance-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.compliance-error {
  text-align: center;
  padding: 40px;
  color: #dc3545;
}

.compliance-retry-btn {
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.compliance-empty {
  text-align: center;
  padding: 40px;
  color: #666;
}

.compliance-list {
  display: grid;
  gap: 20px;
}

.compliance-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: white;
}

.compliance-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.compliance-item-header h3 {
  margin: 0;
  font-size: 1.1em;
}

.compliance-item-meta {
  display: flex;
  gap: 10px;
}

.compliance-status,
.compliance-criticality {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.compliance-status.approved { background-color: #28a745; color: white; }
.compliance-status.under-review { background-color: #ffc107; }
.compliance-status.rejected { background-color: #dc3545; color: white; }

.compliance-criticality.high { background-color: #dc3545; color: white; }
.compliance-criticality.medium { background-color: #ffc107; }
.compliance-criticality.low { background-color: #28a745; color: white; }

.compliance-item-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.compliance-detail {
  font-size: 0.9em;
}

.compliance-detail strong {
  color: #666;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 