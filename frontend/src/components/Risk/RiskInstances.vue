<template>
  <div class="risk-instance-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <div class="risk-instance-header-row">
      <h2 class="risk-instance-title">Risk Instances</h2>
    </div>
    
    <!-- Filters Section - Search bar on top, dropdowns below -->
    <div class="risk-instance-filters-section">
      <!-- Search bar row -->
      <div class="risk-instance-search-row">
        <Dynamicalsearch 
          v-model="searchQuery" 
          placeholder="Search risk instances..."
          @input="applyFilters"
        />
      </div>
      
      <!-- Dropdowns row -->
      <div class="risk-instance-dropdowns-row">
        <CustomDropdown
          :config="criticalityFilter"
          v-model="selectedCriticality"
          @change="applyFilters"
        />
        <CustomDropdown
          :config="statusFilter"
          v-model="selectedStatus"
          @change="applyFilters"
        />
        <CustomDropdown
          :config="categoryFilter"
          v-model="selectedCategory"
          @change="applyFilters"
        />
        <CustomDropdown
          :config="priorityFilter"
          v-model="selectedPriority"
          @change="applyFilters"
        />
      </div>
    </div>
    
    <!-- Dynamic Table -->
    <DynamicTable
      :title="''"
      :data="filteredInstances"
      :columns="tableColumns"
      :filters="[]"
      :show-checkbox="false"
      :show-actions="true"
      :show-pagination="true"
      :default-page-size="10"
      unique-key="RiskInstanceId"
      @row-select="handleRowSelect"
    >
      <!-- Custom cell slots for badges and styling -->
      <template #cell-Origin>
        <span class="risk-instance-origin-badge">MANUAL</span>
      </template>
      
      <template #cell-Category="{ row }">
        <span class="risk-instance-category-badge">{{ row.Category }}</span>
      </template>
      
      <template #cell-Criticality="{ row }">
        <span :class="'risk-instance-priority-' + (row.Criticality ? row.Criticality.toLowerCase() : 'low')">
          {{ row.Criticality || 'Low' }}
        </span>
      </template>
      
      <template #cell-RiskStatus="{ row }">
        <span :class="'risk-instance-status-' + (row.RiskStatus ? row.RiskStatus.toLowerCase().replace(/\s+/g, '-') : 'open')">
          {{ row.RiskStatus || 'Open' }}
        </span>
      </template>
      
      <template #actions="{ row }">
        <button @click="viewInstanceDetails(row.RiskInstanceId)" class="risk-instance-view-btn">
          View Instance
        </button>
      </template>
    </DynamicTable>
  </div>
</template>

<script>
import axios from 'axios'
import DynamicTable from '../DynamicTable.vue'
import Dynamicalsearch from '../Dynamicalsearch.vue'
import CustomDropdown from '../CustomDropdown.vue'
import { PopupModal } from '@/modules/popup'
import '../Risk/RiskInstances.css'

export default {
  name: 'RiskInstances',
  components: {
    DynamicTable,
    Dynamicalsearch,
    CustomDropdown,
    PopupModal
  },
  data() {
    return {
      instances: [],
      selectedCriticality: '',
      selectedStatus: '',
      selectedCategory: '',
      selectedPriority: '',
      searchQuery: '',
      showAddForm: false,
      newInstance: {
        RiskId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Open',
        UserId: 1
      }
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.instances.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueStatus() {
      return [...new Set(this.instances.map(i => i.RiskStatus).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.instances.map(i => i.Category).filter(Boolean))]
    },
    uniquePriority() {
      return [...new Set(this.instances.map(i => i.RiskPriority).filter(Boolean))]
    },
    filteredInstances() {
      let filtered = this.instances.filter(i =>
        (!this.selectedCriticality || i.Criticality === this.selectedCriticality) &&
        (!this.selectedStatus || i.RiskStatus === this.selectedStatus) &&
        (!this.selectedCategory || i.Category === this.selectedCategory) &&
        (!this.selectedPriority || i.RiskPriority === this.selectedPriority)
      )
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(instance => 
          (instance.RiskDescription && instance.RiskDescription.toLowerCase().includes(query)) ||
          (instance.RiskId && instance.RiskId.toString().includes(query)) ||
          (instance.Category && instance.Category.toLowerCase().includes(query)) ||
          (instance.RiskStatus && instance.RiskStatus.toLowerCase().includes(query)) ||
          (instance.Criticality && instance.Criticality.toLowerCase().includes(query))
        )
      }
      
      // Transform data for DynamicTable
      return filtered.map(instance => ({
        ...instance,
        Origin: 'MANUAL', // Add Origin field for the table
        RiskId: instance.RiskId || 'N/A',
        Category: instance.Category || 'N/A',
        Criticality: instance.Criticality || 'Low',
        RiskStatus: instance.RiskStatus || 'Open',
        RiskDescription: instance.RiskDescription || 'No description available'
      }))
    },
    // Filter configurations for CustomDropdown components
    criticalityFilter() {
      return {
        name: 'criticality',
        label: 'Criticality',
        values: [
          { value: '', label: 'All Criticality' },
          ...this.uniqueCriticality.map(c => ({ value: c, label: c }))
        ],
        defaultValue: ''
      }
    },
    statusFilter() {
      return {
        name: 'status',
        label: 'Status',
        values: [
          { value: '', label: 'All Status' },
          ...this.uniqueStatus.map(s => ({ value: s, label: s }))
        ],
        defaultValue: ''
      }
    },
    categoryFilter() {
      return {
        name: 'category',
        label: 'Category',
        values: [
          { value: '', label: 'All Category' },
          ...this.uniqueCategory.map(cat => ({ value: cat, label: cat }))
        ],
        defaultValue: ''
      }
    },
    priorityFilter() {
      return {
        name: 'priority',
        label: 'Priority',
        values: [
          { value: '', label: 'All Priority' },
          ...this.uniquePriority.map(p => ({ value: p, label: p }))
        ],
        defaultValue: ''
      }
    },
    // Table columns configuration for DynamicTable
    tableColumns() {
      return [
        {
          key: 'RiskId',
          label: 'Risk ID',
          sortable: true,
          headerClass: 'risk-instance-id',
          cellClass: 'risk-instance-id'
        },
        {
          key: 'Origin',
          label: 'Origin',
          sortable: true,
          cellClass: 'risk-instance-origin-cell',
          slot: true
        },
        {
          key: 'Category',
          label: 'Category',
          sortable: true,
          cellClass: 'risk-instance-category-cell',
          slot: true
        },
        {
          key: 'Criticality',
          label: 'Criticality',
          sortable: true,
          cellClass: 'risk-instance-criticality-cell',
          slot: true
        },
        {
          key: 'RiskStatus',
          label: 'Risk Status',
          sortable: true,
          cellClass: 'risk-instance-status-cell',
          slot: true
        },
        {
          key: 'RiskDescription',
          label: 'Risk Description',
          sortable: true,
          cellClass: 'risk-instance-description-cell'
        }
      ]
    }
  },
  mounted() {
    this.fetchInstances()
  },
  methods: {
    applyFilters() {
      // Filter logic is handled in computed properties
    },
    
    sanitizeQueryParams(params) {
      const processed = {}
      
      for (const [key, value] of Object.entries(params)) {
        if (value === null || value === undefined || value === '') continue
        processed[key] = value
      }
      
      return processed
    },
    
    fetchInstances() {
      axios.get('http://localhost:8000/api/risk-instances')
        .then(response => {
          this.instances = response.data
          console.log('Fetched risk instances:', this.instances.length)
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error)
          this.tryAlternativeEndpoint()
        })
    },
    
    tryAlternativeEndpoint() {
      console.log('Trying alternative endpoint...')
      axios.get('http://localhost:8000/api/risk-instances')
        .then(response => {
          this.instances = response.data
          console.log('Fetched risk instances from alternative endpoint:', this.instances.length)
        })
        .catch(error => {
          console.error('Error with alternative endpoint:', error)
        })
    },
    
    validateResponseData(data) {
      if (!Array.isArray(data)) {
        console.error('Expected array response, got:', typeof data)
        return []
      }
      
      return data
    },
    
    viewInstanceDetails(instanceId) {
      this.$router.push(`/view-instance/${instanceId}`)
    },
    
    handleRowSelect(data) {
      console.log('Row selected:', data)
    },
    
    submitInstance() {
      const formData = {
        RiskId: parseInt(this.newInstance.RiskId) || null,
        Criticality: this.newInstance.Criticality,
        PossibleDamage: this.newInstance.PossibleDamage,
        Category: this.newInstance.Category,
        Appetite: this.newInstance.Appetite,
        RiskDescription: this.newInstance.RiskDescription,
        RiskLikelihood: parseFloat(this.newInstance.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.newInstance.RiskImpact) || 0,
        RiskExposureRating: this.newInstance.RiskExposureRating ? 
          parseFloat(this.newInstance.RiskExposureRating) : null,
        RiskPriority: this.newInstance.RiskPriority,
        RiskResponseType: this.newInstance.RiskResponseType,
        RiskResponseDescription: this.newInstance.RiskResponseDescription,
        RiskMitigation: this.newInstance.RiskMitigation,
        RiskOwner: this.newInstance.RiskOwner,
        RiskStatus: this.newInstance.RiskStatus,
        UserId: parseInt(this.newInstance.UserId) || null
      }
      
      axios.post('http://localhost:8000/api/risk-instances/', formData)
        .then(response => {
          this.instances.push(response.data)
          
          this.newInstance = {
            RiskId: null,
            Criticality: '',
            PossibleDamage: '',
            Category: '',
            Appetite: '',
            RiskDescription: '',
            RiskLikelihood: '',
            RiskImpact: '',
            RiskExposureRating: '',
            RiskPriority: '',
            RiskResponseType: '',
            RiskResponseDescription: '',
            RiskMitigation: '',
            RiskOwner: '',
            RiskStatus: 'Open',
            UserId: 1
          }
          
          this.showAddForm = false
          this.$popup.success('Risk instance added successfully!')
        })
        .catch(error => {
          console.error('Error adding risk instance:', error.response?.data || error.message)
          this.$popup.error('Error adding risk instance. Please check your data and try again.')
        })
    }
  }
}
</script>