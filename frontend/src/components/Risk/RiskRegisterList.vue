<template>
  <div class="risk-register-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <div class="risk-register-header-row">
      <h2 class="risk-register-title"> Risk Register List</h2>
    </div>
    
    <!-- Dynamic Search and Filters Row -->
    <div class="risk-register-filters-row">
      <div class="risk-register-filter-group">
        <Dynamicalsearch 
          v-model="searchQuery" 
          placeholder="Search risks..."
        />
        <CustomDropdown
          :config="criticalityFilter"
          v-model="selectedCriticality"
          @change="handleFilterChange"
        />
        <CustomDropdown
          :config="categoryFilter"
          v-model="selectedCategory"
          @change="handleFilterChange"
        />
      </div>
    </div>

    <!-- Dynamic Table -->
    <DynamicTable
      :title="''"
      :data="tableData"
      :columns="tableColumns"
      :filters="[]"
      :show-checkbox="false"
      :show-actions="true"
      :show-pagination="true"
      :default-page-size="10"
      unique-key="RiskId"
      @filter-change="handleFilterChange"
      @sort-change="handleSortChange"
      @page-change="handlePageChange"
    >
      <template #cell-Category="{ row }">
        <div class="risk-register-category-badge">{{ row.Category }}</div>
      </template>
      <template #cell-Criticality="{ row }">
        <div :class="getCriticalityClass(row.Criticality)">{{ row.Criticality }}</div>
      </template>
      <template #actions="{ row }">
        <button @click="viewRiskDetails(row.RiskId)" class="risk-register-view-btn">
          View Risk
        </button>
      </template>
    </DynamicTable>
  </div>
</template>

<script>
import './RiskRegisterList.css'
import axios from 'axios'
import DynamicTable from '../DynamicTable.vue'
import Dynamicalsearch from '../Dynamicalsearch.vue'
import CustomDropdown from '../CustomDropdown.vue'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'RiskRegisterList',
  components: {
    DynamicTable,
    Dynamicalsearch,
    CustomDropdown,
    PopupModal
  },
  data() {
    return {
      risks: [],
      selectedCriticality: '',
      selectedCategory: '',
      searchQuery: '',
      loading: false,
      // Filter configurations for CustomDropdown
      criticalityFilter: {
        name: 'criticality',
        label: 'Criticality',
        values: [],
        defaultValue: ''
      },
      categoryFilter: {
        name: 'category',
        label: 'Category',
        values: [],
        defaultValue: ''
      },
      // Table columns configuration
      tableColumns: [
        {
          key: 'RiskId',
          label: 'Risk ID',
          sortable: true,
          cellClass: 'risk-register-id'
        },
        {
          key: 'ComplianceId',
          label: 'Compliance ID',
          sortable: true
        },
        {
          key: 'Category',
          label: 'Category',
          sortable: true,
          slot: true
        },
        {
          key: 'Criticality',
          label: 'Criticality',
          sortable: true,
          slot: true
        },
        {
          key: 'RiskType',
          label: 'Risk Type',
          sortable: true
        },
        {
          key: 'RiskTitle',
          label: 'Risk Title',
          sortable: true
        }
      ]
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.risks.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.risks.map(i => i.Category).filter(Boolean))]
    },

    filteredRisks() {
      let filtered = this.risks
      
      // Search filter - add type checking to prevent toLowerCase error
      if (this.searchQuery && typeof this.searchQuery === 'string' && this.searchQuery.trim() !== '') {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(risk =>
          (risk.RiskTitle && risk.RiskTitle.toLowerCase().includes(query)) ||
          (risk.RiskDescription && risk.RiskDescription.toLowerCase().includes(query)) ||
          (risk.Category && risk.Category.toLowerCase().includes(query)) ||
          (risk.Criticality && risk.Criticality.toLowerCase().includes(query))
        )
      }
      
      // Criticality filter
      if (this.selectedCriticality) {
        filtered = filtered.filter(risk => risk.Criticality === this.selectedCriticality)
      }
      
      // Category filter
      if (this.selectedCategory) {
        filtered = filtered.filter(risk => risk.Category === this.selectedCategory)
      }
      
      return filtered
    },
    
    // Transform data for DynamicTable with proper status formatting
    tableData() {
      return this.filteredRisks.map(risk => ({
        ...risk,
        RiskType: risk.RiskType || 'N/A'
      }))
    }
  },
  watch: {
    searchQuery() {
      // Reset to first page when search changes
    },
    selectedCriticality() {
      // Reset to first page when filter changes
    },
    selectedCategory() {
      // Reset to first page when filter changes
    }
  },
  mounted() {
    this.fetchRisks()
  },
  methods: {
    fetchRisks() {
      this.loading = true
      
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          this.risks = response.data
          this.updateFilterOptions()
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching risks:', error)
          this.loading = false
        })
    },
    
    updateFilterOptions() {
      // Update criticality filter options
      const criticalityOptions = this.uniqueCriticality.map(c => ({
        value: c,
        label: c
      }))
      this.criticalityFilter.values = [
        { value: '', label: 'All Criticality' },
        ...criticalityOptions
      ]
      
      // Update category filter options
      const categoryOptions = this.uniqueCategory.map(cat => ({
        value: cat,
        label: cat
      }))
      this.categoryFilter.values = [
        { value: '', label: 'All Category' },
        ...categoryOptions
      ]
    },
    
    handleSearch(value) {
      this.searchQuery = value
    },
    
    handleFilterChange(filter) {
      if (filter.name === 'criticality') {
        this.selectedCriticality = filter.value
      } else if (filter.name === 'category') {
        this.selectedCategory = filter.value
      }
    },
    
    handleSortChange(sortInfo) {
      // Handle sorting if needed
      console.log('Sort changed:', sortInfo)
    },
    
    handlePageChange(page) {
      // Handle page change if needed
      console.log('Page changed:', page)
    },
    
    viewRiskDetails(riskId) {
      this.$router.push(`/view-risk/${riskId}`)
    },

    getCriticalityClass(criticality) {
      if (!criticality || typeof criticality !== 'string') return ''
      
      criticality = criticality.toLowerCase()
      if (criticality === 'critical') return 'risk-register-priority-critical'
      if (criticality === 'high') return 'risk-register-priority-high'
      if (criticality === 'medium') return 'risk-register-priority-medium'
      if (criticality === 'low') return 'risk-register-priority-low'
      return ''
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      
      const date = new Date(dateString)
      return date.toLocaleDateString()
    }
  }
}
</script> 