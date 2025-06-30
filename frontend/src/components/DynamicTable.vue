<template>
  <div class="dynamic-table-container">
    <!-- Filters Section - Above Table -->
    <div class="filters-section-above" v-if="filters && filters.length > 0">
      <div class="filters-container">
        <CustomDropdown
          v-for="filter in filters"
          :key="filter.name"
          :config="filter"
          v-model="filterValues[filter.name]"
          @change="handleFilterChange"
        />
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-wrapper">
      <table class="dynamic-table">
        <thead>
          <tr>
            <th v-if="showCheckbox">
              <input 
                type="checkbox" 
                :checked="allSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th 
              v-for="column in visibleColumns" 
              :key="column.key"
              :class="column.headerClass"
              :style="column.headerStyle"
            >
              <div class="column-header">
                <span>{{ column.label }}</span>
                <button 
                  v-if="column.sortable" 
                  @click="sortBy(column.key)"
                  class="sort-btn"
                >
                  <PhCaretDown v-if="sortKey === column.key && sortOrder === 'asc'" :size="12" />
                  <PhCaretUp v-else-if="sortKey === column.key && sortOrder === 'desc'" :size="12" />
                  <PhCaretUp v-else :size="12" class="sort-icon-default" />
                </button>
              </div>
            </th>
            <th v-if="showActions" class="actions-column">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in paginatedData" :key="row.id || row[uniqueKey]">
            <td v-if="showCheckbox">
              <input 
                type="checkbox" 
                :checked="selectedRows.includes(row.id || row[uniqueKey])"
                @change="toggleRowSelection(row)"
              />
            </td>
            <td 
              v-for="column in visibleColumns" 
              :key="column.key"
              :class="column.cellClass"
              :style="column.cellStyle"
            >
              <component 
                v-if="column.component"
                :is="column.component"
                :row="row"
                :column="column"
                :value="row[column.key]"
              />
              <template v-else-if="column.slot">
                <slot :name="`cell-${column.key}`" :row="row" :column="column" :value="row[column.key]">
                  {{ row[column.key] }}
                </slot>
              </template>
              <template v-else>
                <div v-if="column.type === 'image'" class="image-cell">
                  <img :src="row[column.key]" :alt="column.altKey ? row[column.altKey] : ''" />
                  <span v-if="column.showText">{{ row[column.textKey] }}</span>
                </div>
                <div v-else-if="column.type === 'status'" class="status-cell">
                  <span :class="['status', getStatusClass(row[column.key])]">
                    {{ row[column.key] }}
                  </span>
                </div>
                <div v-else-if="column.type === 'progress'" class="progress-cell">
                  <div class="progress-bar-container">
                    <div 
                      class="progress-bar"
                      :class="getProgressBarColorClass(row[column.key])"
                      :style="{ width: row[column.key] + '%' }"
                    ></div>
                  </div>
                  <span class="progress-value">{{ row[column.key] }}%</span>
                </div>
                <div v-else-if="column.type === 'actions'" class="actions-cell">
                  <button class="action-dots">...</button>
                </div>
                <span v-else>{{ row[column.key] }}</span>
              </template>
            </td>
            <td v-if="showActions" class="actions-column">
              <slot name="actions" :row="row">
                <button class="action-dots">...</button>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Section -->
    <div class="pagination-container" v-if="showPagination">
      <div class="results-info">
        Results: {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, filteredData.length) }} of {{ filteredData.length }}
      </div>
      <div class="items-per-page-selector">
        <select v-model="itemsPerPage" @change="currentPage = 1">
          <option v-for="option in pageSizeOptions" :key="option" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div class="pagination-controls">
        <button @click="prevPage" :disabled="currentPage === 1">&lt;</button>
        <template v-for="page in paginationNumbers" :key="page">
          <button 
            v-if="typeof page === 'number'" 
            @click="changePage(page)" 
            :class="{ active: currentPage === page }"
          >
            {{ page }}
          </button>
          <span v-else class="ellipsis">...</span>
        </template>
        <button @click="nextPage" :disabled="currentPage === totalPages">&gt;</button>
      </div>
    </div>
  </div>
</template>

<script>
import { PhCaretDown, PhCaretUp } from '@phosphor-icons/vue';
import CustomDropdown from './CustomDropdown.vue';
import CustomButton from './CustomButton.vue';
import './styles/theme.css';

export default {
  name: 'DynamicTable',
  components: {
    PhCaretDown,
    PhCaretUp,
    CustomDropdown,
    CustomButton
  },
  props: {
  // Table configuration
  data: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  },
  uniqueKey: {
    type: String,
    default: 'id'
  },
  
  // Header configuration
  filters: {
    type: Array,
    default: () => []
  },
  
  // Table features
  showCheckbox: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  
  // Pagination configuration
  pageSizeOptions: {
    type: Array,
    default: () => [7, 10, 20, 50]
  },
  defaultPageSize: {
    type: Number,
    default: 7
  }
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: this.defaultPageSize,
      selectedRows: [],
      filterValues: {},
      sortKey: '',
      sortOrder: 'asc'
    }
  },
  computed: {
    visibleColumns() {
      return this.columns.filter(column => !column.hidden);
    },
    filteredData() {
      let filtered = [...this.data];
  
  // Apply filters
      Object.entries(this.filterValues).forEach(([filterName, value]) => {
    if (value && value !== 'all') {
          const filter = this.filters.find(f => f.name === filterName);
      if (filter && filter.filterFunction) {
        filtered = filtered.filter(row => filter.filterFunction(row, value));
      }
    }
  });
  
  // Apply sorting
      if (this.sortKey) {
    filtered.sort((a, b) => {
          const aVal = a[this.sortKey];
          const bVal = b[this.sortKey];
      
          if (aVal < bVal) return this.sortOrder === 'asc' ? -1 : 1;
          if (aVal > bVal) return this.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }
  
  return filtered;
    },
    totalPages() {
      return Math.ceil(this.filteredData.length / this.itemsPerPage);
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredData.slice(start, end);
    },
    allSelected() {
      return this.selectedRows.length === this.paginatedData.length && this.paginatedData.length > 0;
    },
    paginationNumbers() {
  const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    pages.push(1);
    if (current > 3) {
      pages.push('...');
    }
    
    let start = Math.max(2, current - 1);
    let end = Math.min(total - 1, current + 1);

    if (current <= 2) {
      start = 2;
      end = 3;
    }

    if (current >= total - 1) {
      start = total - 2;
      end = total - 1;
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    if (current < total - 2) {
      pages.push('...');
    }
    pages.push(total);
  }
  return pages.filter((v, i, a) => a.indexOf(v) === i);
    }
  },
  watch: {
    data: {
      handler() {
        this.currentPage = 1;
      },
      deep: true
    }
  },
  mounted() {
    // Initialize filter values
    this.filters.forEach(filter => {
      this.filterValues[filter.name] = filter.defaultValue || '';
    });
  },
  methods: {
    handleFilterChange(filter) {
      this.currentPage = 1;
      this.$emit('filter-change', { filter, values: this.filterValues });
    },
    toggleRowSelection(row) {
      const rowId = row[this.uniqueKey];
      const index = this.selectedRows.indexOf(rowId);
  
  if (index > -1) {
        this.selectedRows.splice(index, 1);
  } else {
        this.selectedRows.push(rowId);
      }
      
      this.$emit('row-select', { row, selected: this.selectedRows });
    },
    toggleSelectAll() {
      if (this.allSelected) {
        this.selectedRows = [];
  } else {
        this.selectedRows = this.paginatedData.map(row => row[this.uniqueKey]);
      }
      
      this.$emit('select-all', { selected: this.selectedRows, allSelected: this.allSelected });
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
  } else {
        this.sortKey = key;
        this.sortOrder = 'asc';
      }
      
      this.$emit('sort-change', { key: this.sortKey, order: this.sortOrder });
    },
    changePage(page) {
      this.currentPage = page;
      this.$emit('page-change', page);
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.$emit('page-change', this.currentPage);
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.$emit('page-change', this.currentPage);
      }
    },
    getStatusClass(status) {
  const statusMap = {
    'On rent': 'status-on-rent',
    'On sell': 'status-on-sell',
    'Renovation': 'status-renovation',
    'On Construction': 'status-on-construction',
    'Active': 'status-active',
    'Inactive': 'status-inactive',
    'Pending': 'status-pending',
    'Approved': 'status-approved',
    'Rejected': 'status-rejected'
  };
  return statusMap[status] || '';
    },
    getProgressBarColorClass(value) {
  if (value > 60) return 'progress-bar-success';
  if (value > 30) return 'progress-bar-warning';
  if (value > 0) return 'progress-bar-danger';
  return 'progress-bar-default';
    }
  }
}
</script>

<style scoped>
.dynamic-table-container {
  /* background: var(--dynamic-table-container-bg); */
  border-radius: 8px;
  /* box-shadow: var(--dynamic-table-container-shadow); */
  overflow: hidden;
  font-family: var(--font-family, inherit);
}

/* Filters Section Above Table */
.filters-section-above {
  padding: 0 24px 16px 24px;
  display: flex;
  align-items: flex-start;
  box-shadow: none;
  border-radius: 0;
  background: none;
  border: none;
}

.filters-container {
  display: flex;
  gap: 16px;
  flex-wrap: nowrap;
  align-items: flex-start;
  box-shadow: none;
  border-radius: 0;
  background: none;
  border: none;
  padding: 0;
  margin: 0;
}

.filters-container > * {
  flex: 0 0 auto;
  min-width: 180px;
  max-width: 400px;
  width: auto;
  margin-right: 0;
  margin-bottom: 0;
}

.filters-container .filter-btn, .filters-container .CustomDropdown {
  min-width: 180px;
  max-width: 320px;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 40px;
  line-height: 40px;
  display: flex;
  align-items: center;
}

.filters-container .dropdown-value {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  display: inline-block;
}

.table-wrapper {
  /* overflow-x: auto; */
}

.dynamic-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg, #fff);
  font-family: var(--font-family, inherit);
}

.dynamic-table th,
.dynamic-table .column-header,
.dynamic-table .sort-btn {
  background: none !important;
  border: none !important;
  box-shadow: none !important;
}

.dynamic-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: var(--dynamic-table-header-text, #333);
  border-bottom: 1px solid var(--dynamic-table-border-color, #dee2e6);
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--dynamic-table-header-bg, none) !important;
  font-family: var(--font-family, inherit);
}

.dynamic-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--dynamic-table-row-border-color, #f1f3f4);
  font-size: 14px;
  color: var(--dynamic-table-row-text-color, #333);
  font-family: var(--font-family, inherit);
}

/* First Column Styling - Black Color */
.dynamic-table td:first-child {
  color: #1a1a1a;
  font-weight: 600;
}

.dynamic-table tbody tr:hover {
  background: var(--dynamic-table-row-hover-bg, #f8f9fa);
}

.column-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-btn {
  cursor: pointer;
  background: none !important;
  border: none !important;
  outline: none !important;
  padding: 2px;
  color: var(--dynamic-table-sort-btn-color, #6b7280);
  transition: color 0.2s;
}

.sort-btn:hover {
  color: var(--dynamic-table-sort-btn-hover-color, #374151);
}

.sort-icon-default {
  opacity: 0.3;
}

.image-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.image-cell img {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  object-fit: cover;
}

.status-cell .status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  font-family: var(--font-family, inherit);
}

.status-on-rent {
  background: var(--status-on-rent-bg, #dbeafe);
  color: var(--status-on-rent-text, #1e40af);
}

.status-on-sell {
  background: var(--status-on-sell-bg, #fef3c7);
  color: var(--status-on-sell-text, #d97706);
}

.status-renovation {
  background: var(--status-renovation-bg, #fce7f3);
  color: var(--status-renovation-text, #be185d);
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar-container {
  flex: 1;
  height: 8px;
  background: var(--progress-bar-container-bg, #e5e7eb);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-bar-success {
  background-color: var(--progress-bar-success-bg, #10b981);
}
.progress-bar-warning {
  background-color: var(--progress-bar-warning-bg, #f59e0b);
}
.progress-bar-danger {
  background-color: var(--progress-bar-danger-bg, #ef4444);
}
.progress-bar-default {
  background-color: var(--progress-bar-default-bg, #6b7280);
}

.progress-value {
  font-size: 12px;
  color: #6b7280;
  min-width: 30px;
  text-align: right;
}

.actions-cell {
  text-align: center;
}

.action-dots {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: #6b7280;
  transition: background-color 0.2s;
}

.action-dots:hover {
  background: #f3f4f6;
}

.actions-column {
  width: 80px;
  text-align: center;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--dynamic-table-border-color, #dee2e6);
  background: var(--dynamic-table-pagination-bg, #f9fafb);
  font-family: var(--font-family, inherit);
}

.results-info {
  font-size: 14px;
  color: var(--dynamic-table-pagination-text-color, #6b7280);
}

.items-per-page-selector select {
  padding: 6px 12px;
  border: 1px solid var(--dynamic-table-pagination-btn-border, #d1d5db);
  border-radius: 6px;
  background: var(--dynamic-table-pagination-btn-bg, white);
  font-size: 14px;
  color: var(--dynamic-table-pagination-btn-text, #374151);
  font-family: var(--font-family, inherit);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-controls button {
  padding: 6px 12px;
  border: 1px solid var(--dynamic-table-pagination-btn-border, #d1d5db);
  background: var(--dynamic-table-pagination-btn-bg, white);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--dynamic-table-pagination-btn-text, #374151);
  transition: all 0.2s;
  font-family: var(--font-family, inherit);
}

.pagination-controls button:hover:not(:disabled) {
  background: var(--dynamic-table-pagination-btn-hover-bg, #f3f4f6);
  border-color: #9ca3af;
}

.pagination-controls button.active {
  background: var(--dynamic-table-pagination-btn-active-bg, #7B6FDD);
  border-color: var(--dynamic-table-pagination-btn-active-bg, #7B6FDD);
  color: var(--dynamic-table-pagination-btn-active-text, white);
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ellipsis {
  padding: 6px 8px;
  color: var(--dynamic-table-pagination-text-color, #6b7280);
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
    gap: 12px;
  }
  
  .filters-container {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 900px) {
  .filters-section-above {
    flex-direction: column;
    align-items: stretch;
  }
  .filters-container {
    flex-wrap: wrap;
    gap: 12px;
  }
  .filters-container > * {
    max-width: 100%;
  }
}

.dynamic-table .dropdown-menu {
  z-index: 99999 !important;
  position: absolute !important;
}
/* .table-wrapper {
  overflow: visible !important;
} */
</style> 