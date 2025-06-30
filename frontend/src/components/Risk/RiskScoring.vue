<template>
  <div class="risk-scoring-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <!-- Page Heading -->
    <div class="risk-scoring-page-heading">
      <h2>Risk Scoring</h2>
    </div>
    
    <!-- Search and Filter Bar -->
    <div class="risk-scoring-filters-wrapper">
      <Dynamicalsearch 
        v-model="searchQuery" 
        placeholder="Search..."
        @input="applyFilters"
      />
    </div>
    
    <!-- Dropdowns Above Table -->
    <div class="risk-scoring-dropdowns-wrapper">
      <CustomDropdown
        :config="statusFilterConfig"
        v-model="statusFilter"
        @change="handleStatusFilterChange"
      />
      <CustomDropdown
        :config="categoryFilterConfig"
        v-model="categoryFilter"
        @change="handleCategoryFilterChange"
      />
    </div>
    
    <div v-if="loading" class="risk-scoring-loading">
      <div class="risk-scoring-spinner"></div>
      <span>Loading risk data...</span>
    </div>
    
    <div v-else-if="error" class="risk-scoring-error-message">
      {{ error }}
    </div>
    
    <div v-else-if="filteredRiskInstances.length === 0" class="risk-scoring-no-data">
      <p>No risk instances found.</p>
    </div>
    
    <div v-else>
      <div class="risk-scoring-table-container">
        <DynamicTable
          :title="''"
          :data="filteredRiskInstances"
          :columns="tableColumns"
          :filters="[]"
          :show-checkbox="false"
          :show-actions="true"
          :show-pagination="true"
          :page-size-options="[7, 10, 20, 50]"
          :default-page-size="7"
          unique-key="RiskInstanceId"
          @filter-change="handleFilterChange"
        >
          <template #actions="{ row }">
            <div v-if="isScoringCompleted(row)" class="risk-scoring-completed" @click="viewScoringDetails(row.RiskInstanceId)">
              <span class="risk-scoring-completed-text">Scoring Completed</span>
              <span class="risk-scoring-view-icon" title="View Scoring Details">
                <i class="fas fa-eye"></i>
              </span>
            </div>
            <div v-else-if="isRiskRejected(row)" class="risk-scoring-rejected" @click="viewScoringDetails(row.RiskInstanceId)">
              <span class="risk-scoring-rejected-text">Instance Rejected</span>
              <span class="risk-scoring-view-icon" title="View Scoring Details">
                <i class="fas fa-eye"></i>
              </span>
            </div>
            <div v-else-if="!showActionButtons[row.RiskInstanceId]" class="risk-scoring-action-icons">
              <span class="risk-scoring-icon risk-scoring-accept-icon" title="Accept Risk" @click="toggleActionButtons(row.RiskInstanceId)">
                <i class="fas fa-check-circle"></i>
              </span>
              <span class="risk-scoring-icon risk-scoring-reject-icon" title="Reject Risk" @click="rejectRisk(row.RiskInstanceId)">
                <i class="fas fa-times-circle"></i>
              </span>
            </div>
            <div v-else class="risk-scoring-action-buttons">
              <CustomButton
                :config="mapScoringButtonConfig"
                @click="mapScoringRisk(row.RiskInstanceId)"
              />
            </div>
          </template>
          
          <template #cell-RiskDescription="{ value }">
            {{ truncateText(value, 50) || 'N/A' }}
          </template>
        </DynamicTable>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import './RiskScoring.css';
import { reactive } from 'vue';
import DynamicTable from '../DynamicTable.vue';
import CustomButton from '../CustomButton.vue';
import CustomDropdown from '../CustomDropdown.vue';
import Dynamicalsearch from '../Dynamicalsearch.vue';
import { PopupModal } from '@/modules/popup';

export default {
  name: 'RiskScoring',
  components: {
    DynamicTable,
    CustomButton,
    CustomDropdown,
    Dynamicalsearch,
    PopupModal
  },
  data() {
    return {
      riskInstances: [],
      filteredRiskInstances: [],
      loading: true,
      error: null,
      showActionButtons: reactive({}),
      searchQuery: '',
      statusFilter: '',
      categoryFilter: '',
      tableColumns: [
        {
          key: 'RiskInstanceId',
          label: 'Risk Instance ID',
          sortable: true,
          headerClass: 'risk-scoring-col-risk-id',
          cellClass: 'risk-scoring-col-risk-id'
        },
        {
          key: 'IncidentId',
          label: 'Incident ID',
          sortable: true,
          headerClass: 'risk-scoring-col-incident-id',
          cellClass: 'risk-scoring-col-incident-id'
        },
        {
          key: 'ComplianceId',
          label: 'Compliance ID',
          sortable: true,
          headerClass: 'risk-scoring-col-compliance-id',
          cellClass: 'risk-scoring-col-compliance-id'
        },
        {
          key: 'RiskTitle',
          label: 'Risk Title',
          sortable: true,
          headerClass: 'risk-scoring-col-risk-title',
          cellClass: 'risk-scoring-col-risk-title'
        },
        {
          key: 'Category',
          label: 'Category',
          sortable: true,
          headerClass: 'risk-scoring-col-category',
          cellClass: 'risk-scoring-col-category'
        },
        {
          key: 'RiskDescription',
          label: 'Risk Description',
          sortable: true,
          headerClass: 'risk-scoring-col-description',
          cellClass: 'risk-scoring-col-description',
          slot: true
        }
      ],
      statusFilterConfig: {
        name: 'statusFilter',
        label: 'Status',
        values: [],
        defaultValue: ''
      },
      categoryFilterConfig: {
        name: 'categoryFilter',
        label: 'Category',
        values: [],
        defaultValue: ''
      },
      mapScoringButtonConfig: {
        name: 'MAP SCORING RISK',
        className: 'risk-scoring-map-btn risk-scoring-map-btn-full',
        disabled: false
      }
    }
  },
  computed: {
    uniqueStatuses() {
      return [...new Set(this.riskInstances
        .map(risk => risk.RiskStatus)
        .filter(status => status && status.trim() !== '')
      )];
    },
    uniqueCategories() {
      return [...new Set(this.riskInstances
        .map(risk => risk.Category)
        .filter(category => category && category.trim() !== '')
      )];
    }
  },
  watch: {
    uniqueStatuses: {
      handler(newStatuses) {
        this.statusFilterConfig.values = [
          { value: '', label: 'All Status' },
          ...newStatuses.map(status => ({ value: status, label: status }))
        ];
      },
      immediate: true
    },
    uniqueCategories: {
      handler(newCategories) {
        this.categoryFilterConfig.values = [
          { value: '', label: 'All Categories' },
          ...newCategories.map(category => ({ value: category, label: category }))
        ];
      },
      immediate: true
    }
  },
  mounted() {
    this.fetchRiskInstances();
    
    // Add event listener for sidebar toggle to adjust container margin
    window.addEventListener('resize', this.handleResize);
    
    // Initial check for sidebar state
    this.handleResize();
    
    // Add Font Awesome if not already present
    if (!document.querySelector('link[href*="font-awesome"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(link);
    }
  },
  // Refresh data when component is activated (coming back from another route)
  activated() {
    console.log('RiskScoring component activated - refreshing data');
    this.fetchRiskInstances();
  },
  beforeUnmount() {
    // Clean up event listener
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    applyFilters() {
      this.filterRiskInstances();
    },
    handleStatusFilterChange(option) {
      this.statusFilter = option.value;
      this.applyFilters();
    },
    handleCategoryFilterChange(option) {
      this.categoryFilter = option.value;
      this.applyFilters();
    },
    handleFilterChange(filterData) {
      // Handle any additional filter changes from DynamicTable if needed
      console.log('Filter change:', filterData);
    },
    filterRiskInstances() {
      this.filteredRiskInstances = this.riskInstances.filter(risk => {
        // Search query filter
        const searchMatch = !this.searchQuery || 
          risk.RiskTitle?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          risk.RiskDescription?.toLowerCase().includes(this.searchQuery.toLowerCase());

        // Status filter
        const statusMatch = !this.statusFilter || risk.RiskStatus === this.statusFilter;

        // Category filter
        const categoryMatch = !this.categoryFilter || risk.Category === this.categoryFilter;

        return searchMatch && statusMatch && categoryMatch;
      });
    },
    
    // Simple response data processing
    validateResponseData(data) {
      if (!Array.isArray(data)) {
        console.error('Expected array response, got:', typeof data);
        return [];
      }
      
      return data;
    },
    
    isScoringCompleted(risk) {
      // Check if risk has RiskLikelihood, RiskImpact, and RiskExposureRating values
      // AND Appetite is 'Yes' (not rejected)
      const hasScoring = (
        risk.RiskLikelihood !== undefined && 
        risk.RiskLikelihood !== null && 
        risk.RiskImpact !== undefined && 
        risk.RiskImpact !== null && 
        risk.RiskExposureRating !== undefined && 
        risk.RiskExposureRating !== null
      );
      
      // Only show "Scoring Completed" if it has scoring AND is not rejected
      // Use case-insensitive comparison for Appetite and RiskStatus
      const appetite = (risk.Appetite || '').toLowerCase();
      const status = (risk.RiskStatus || '').toLowerCase();
      
      return hasScoring && appetite === 'yes' && status !== 'rejected';
    },
    isRiskRejected(risk) {
      // Check if risk has been rejected (Appetite is 'No' or RiskStatus is 'Rejected')
      // AND has scoring completed
      // Note: Rejected risks will not appear in the Risk Resolution screen
      const hasScoring = (
        risk.RiskLikelihood !== undefined && 
        risk.RiskLikelihood !== null && 
        risk.RiskImpact !== undefined && 
        risk.RiskImpact !== null && 
        risk.RiskExposureRating !== undefined && 
        risk.RiskExposureRating !== null
      );
      
      // Use case-insensitive comparison for Appetite and RiskStatus
      const appetite = (risk.Appetite || '').toLowerCase();
      const status = (risk.RiskStatus || '').toLowerCase();
      
      return hasScoring && (appetite === 'no' || status === 'rejected');
    },
    viewScoringDetails(riskId) {
      // Find the risk instance
      const risk = this.riskInstances.find(r => r.RiskInstanceId === riskId);
      
      console.log(`Viewing scoring details for Risk ${riskId}`);
      console.log(`Risk details: Status=${risk.RiskStatus}, Appetite=${risk.Appetite}`);
      console.log(`Display logic: isScoringCompleted=${this.isScoringCompleted(risk)}, isRiskRejected=${this.isRiskRejected(risk)}`);
      
      // Navigate to the scoring details page with the risk ID and action=view
      this.$router.push({
        path: `/risk/scoring-details/${riskId}`,
        query: { action: 'view' }
      });
    },
    fetchRiskInstances() {
      axios.get('http://localhost:8000/api/risk-instances/')
        .then(response => {
          console.log('Risk instances data received:', response.data);
          
          // Process each risk instance to ensure required fields are initialized
          this.riskInstances = response.data.map(risk => ({
            ...risk,
            RiskLikelihood: risk.RiskLikelihood || 1,
            RiskImpact: risk.RiskImpact || 1,
            RiskExposureRating: risk.RiskExposureRating || (risk.RiskLikelihood || 1) * (risk.RiskImpact || 1)
          }));
          
          this.filteredRiskInstances = [...this.riskInstances]; // Initialize filtered risks
          
          // Log risk status and appetite for debugging
          this.riskInstances.forEach(risk => {
            console.log(`Risk #${risk.RiskInstanceId}: Status=${risk.RiskStatus}, Appetite=${risk.Appetite}, Likelihood=${risk.RiskLikelihood}, Impact=${risk.RiskImpact}, Exposure=${risk.RiskExposureRating}`);
            
            // Initialize showActionButtons for each risk instance
            this.showActionButtons[risk.RiskInstanceId] = false;
          });
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error);
          this.error = `Failed to fetch risk instances: ${error.message}`;
          this.loading = false;
        });
    },
    handleResize() {
      // This method can be used to dynamically adjust the container based on sidebar state
      const container = document.querySelector('.risk-scoring-container');
      if (container) {
        // Adjust container based on window size
        if (window.innerWidth < 768) {
          container.style.marginLeft = '0';
          container.style.maxWidth = '100vw';
        } else if (window.innerWidth < 992) {
          container.style.marginLeft = '60px';
          container.style.maxWidth = 'calc(100vw - 60px)';
        } else if (window.innerWidth < 1200) {
          container.style.marginLeft = '200px';
          container.style.maxWidth = 'calc(100vw - 200px)';
        } else {
          container.style.marginLeft = '280px';
          container.style.maxWidth = 'calc(100vw - 280px)';
        }
      }
    },
    truncateText(text, maxLength) {
      if (!text) return '';
      
      // Direct truncation without sanitization
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },
    toggleActionButtons(riskId) {
      // Direct toggle without validation
      this.showActionButtons[riskId] = !this.showActionButtons[riskId];
    },
    rejectRisk(riskId) {
      // Direct navigation without validation
      console.log(`Navigating to Scoring Details for Risk ${riskId} (rejected)`);
      // Navigate to the scoring details page with the risk ID and action=reject
      this.$router.push({
        path: `/risk/scoring-details/${riskId}`,
        query: { action: 'reject' }
      });
    },
    mapScoringRisk(riskId) {
      // Direct navigation without validation
      console.log(`Navigating to Scoring Details for Risk ${riskId} (accepted)`);
      // Navigate to the scoring details page with the risk ID and action=accept
      this.$router.push({
        path: `/risk/scoring-details/${riskId}`,
        query: { action: 'accept' }
      });
    }
  }
}
</script>

<style scoped>
@import './RiskScoring.css';
</style> 