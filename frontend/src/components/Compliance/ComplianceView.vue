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
        <button class="compliance-export-btn" @click="exportData">
          <i class="fas fa-download"></i> Export
        </button>
        <button @click="goBack" class="compliance-back-btn">
          <i class="fas fa-arrow-left"></i> Back
        </button>
      </div>
    </div>

    <div v-if="loading" class="compliance-loading">
      <div class="compliance-spinner"></div>
      <p>Loading controls...</p>
    </div>

    <div v-else-if="error" class="compliance-error">
      <p>{{ error }}</p>
      <button @click="retryLoading" class="compliance-retry-btn">Retry</button>
    </div>

    <div v-else>
      <!-- Search and Filter Section -->
      <div class="controls-filter-section">
        <div class="search-container">
          <Dynamicalsearch
            v-model="searchQuery"
            placeholder="Search controls..."
            @search="filterControls"
          />
        </div>
        <div class="dropdowns-row">
          <CustomDropdown
            :config="statusDropdownConfig"
            v-model="statusFilter"
            @change="filterControls"
            class="filter-dropdown"
          />
          <CustomDropdown
            :config="criticalityDropdownConfig"
            v-model="criticalityFilter"
            @change="filterControls"
            class="filter-dropdown"
          />
          <CustomDropdown
            :config="maturityDropdownConfig"
            v-model="maturityFilter"
            @change="filterControls"
            class="filter-dropdown"
          />
        </div>
      </div>

      <!-- Table View -->
      <div class="controls-table-container">
        <DynamicTable
          :data="filteredControls"
          :columns="tableColumns"
          uniqueKey="ComplianceId"
          :showPagination="true"
          :showActions="true"
        >
          <template #actions="{ row }">
            <button class="action-btn view" @click="showControlDetails(row)">
              <i class="fas fa-eye"></i>
            </button>
            <button v-if="row.IsRisk" class="action-btn risk" title="Risk Identified">
              <i class="fas fa-exclamation-triangle"></i>
            </button>
          </template>
        </DynamicTable>
      </div>

      <!-- Control Details Modal -->
      <div v-if="selectedControl" class="modal-overlay" @click="closeControlDetails">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Control Details</h3>
            <button class="modal-close" @click="closeControlDetails">&times;</button>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Title:</label>
                  <span>{{ selectedControl.ComplianceTitle }}</span>
                </div>
                <div class="detail-item">
                  <label>ID:</label>
                  <span>{{ selectedControl.Identifier }}</span>
                </div>
                <div class="detail-item">
                  <label>Status:</label>
                  <span :class="['status-badge', getStatusClass(selectedControl.Status)]">
                    {{ selectedControl.Status }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>Criticality:</label>
                  <span :class="['criticality-badge', getCriticalityClass(selectedControl.Criticality)]">
                    {{ selectedControl.Criticality }}
                  </span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Description</h4>
              <p>{{ selectedControl.ComplianceItemDescription }}</p>
            </div>

            <div class="detail-section">
              <h4>Implementation Details</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Type:</label>
                  <span>{{ selectedControl.MandatoryOptional }}</span>
                </div>
                <div class="detail-item">
                  <label>Implementation:</label>
                  <span>{{ selectedControl.ManualAutomatic }}</span>
                </div>
                <div class="detail-item">
                  <label>Maturity Level:</label>
                  <span>{{ selectedControl.MaturityLevel }}</span>
                </div>
              </div>
            </div>

            <div v-if="selectedControl.IsRisk" class="detail-section risk-section">
              <h4>Risk Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Possible Damage:</label>
                  <p>{{ selectedControl.PossibleDamage }}</p>
                </div>
                <div class="detail-item">
                  <label>Mitigation:</label>
                  <p>{{ selectedControl.mitigation }}</p>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Hierarchy</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Framework:</label>
                  <span>{{ selectedControl.FrameworkName }}</span>
                </div>
                <div class="detail-item">
                  <label>Policy:</label>
                  <span>{{ selectedControl.PolicyName }}</span>
                </div>
                <div class="detail-item">
                  <label>SubPolicy:</label>
                  <span>{{ selectedControl.SubPolicyName }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { complianceService } from '../../services/api';
import Dynamicalsearch from '../Dynamicalsearch.vue';
import CustomDropdown from '../CustomDropdown.vue';
import DynamicTable from '../DynamicTable.vue';

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref(null);
const compliances = ref([]);
const selectedControl = ref(null);

// Filter and Sort state
const searchQuery = ref('');
const statusFilter = ref('');
const criticalityFilter = ref('');
const maturityFilter = ref('');
const sortKey = ref('Identifier');
const sortOrder = ref('asc');

const title = computed(() => {
  const name = decodeURIComponent(route.params.name || '');
  const type = route.params.type.charAt(0).toUpperCase() + route.params.type.slice(1);
  return `Controls for ${type}: ${name}`;
});

// Dropdown configs
const statusDropdownConfig = {
  name: 'Status',
  label: 'Status',
  values: [
    { value: '', label: 'All Statuses' },
    { value: 'Under Review', label: 'Under Review' },
    { value: 'Approved', label: 'Approved' },
    { value: 'Rejected', label: 'Rejected' }
  ]
};
const criticalityDropdownConfig = {
  name: 'Criticality',
  label: 'Criticality',
  values: [
    { value: '', label: 'All Criticality' },
    { value: 'High', label: 'High' },
    { value: 'Medium', label: 'Medium' },
    { value: 'Low', label: 'Low' }
  ]
};
const maturityDropdownConfig = {
  name: 'MaturityLevel',
  label: 'Maturity Level',
  values: [
    { value: '', label: 'All Maturity Levels' },
    { value: 'Initial', label: 'Initial' },
    { value: 'Developing', label: 'Developing' },
    { value: 'Defined', label: 'Defined' },
    { value: 'Managed', label: 'Managed' },
    { value: 'Optimizing', label: 'Optimizing' }
  ]
};

// Table columns for DynamicTable
const tableColumns = [
  { key: 'Identifier', label: 'ID', sortable: true },
  { key: 'ComplianceTitle', label: 'Title', sortable: true },
  { key: 'Status', label: 'Status', sortable: true },
  { key: 'Criticality', label: 'Criticality', sortable: true },
  { key: 'MaturityLevel', label: 'Maturity Level', sortable: true },
  { key: 'MandatoryOptional', label: 'Type', sortable: true },
  { key: 'ManualAutomatic', label: 'Implementation', sortable: true },
  { key: 'CreatedByDate', label: 'Created Date', sortable: true }
];

// Sorting and Filtering
const filteredControls = computed(() => {
  let result = [...compliances.value];

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(control => 
      (control.ComplianceTitle?.toLowerCase().includes(query) ||
      control.ComplianceItemDescription?.toLowerCase().includes(query) ||
      control.Identifier?.toLowerCase().includes(query))
    );
  }

  // Apply status filter
  if (statusFilter.value) {
    result = result.filter(control => control.Status === statusFilter.value);
  }

  // Apply criticality filter
  if (criticalityFilter.value) {
    result = result.filter(control => control.Criticality === criticalityFilter.value);
  }

  // Apply maturity filter
  if (maturityFilter.value) {
    result = result.filter(control => control.MaturityLevel === maturityFilter.value);
  }

  // Apply sorting
  result.sort((a, b) => {
    let aVal = a[sortKey.value] || '';
    let bVal = b[sortKey.value] || '';
    if (sortKey.value === 'CreatedByDate') {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    } else {
      aVal = typeof aVal === 'string' ? aVal.toLowerCase() : aVal;
      bVal = typeof bVal === 'string' ? bVal.toLowerCase() : bVal;
    }
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
  return result;
});

const filterControls = () => {
  // The filtering is handled by the computed property
};

const getStatusClass = (status) => {
  const statusLower = status?.toLowerCase() || '';
  if (statusLower.includes('review')) return 'status-review';
  if (statusLower.includes('approved')) return 'status-approved';
  if (statusLower.includes('rejected')) return 'status-rejected';
  return 'status-default';
};

const getCriticalityClass = (criticality) => {
  const criticalityLower = criticality?.toLowerCase() || '';
  return `criticality-${criticalityLower}`;
};

const showControlDetails = (control) => {
  selectedControl.value = control;
};

const closeControlDetails = () => {
  selectedControl.value = null;
};

const retryLoading = () => {
  fetchCompliances();
};

const goBack = () => {
  router.back();
};

const exportData = () => {
  // TODO: Implement export functionality
  console.log('Export functionality to be implemented');
};

const fetchCompliances = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await complianceService.getCompliancesByType(
      route.params.type,
      route.params.id
    );
    if (response.data.success) {
      compliances.value = response.data.compliances.map(compliance => ({
        ...compliance,
        CreatedByDate: compliance.CreatedByDate ? new Date(compliance.CreatedByDate).toLocaleDateString() : 'N/A',
        category: compliance.Criticality || 'Not Specified',
        name: compliance.ComplianceTitle || compliance.ComplianceItemDescription,
        description: compliance.ComplianceItemDescription,
        title: compliance.ComplianceTitle,
        maturityLevel: compliance.MaturityLevel || 'Not Specified',
        version: compliance.ComplianceVersion,
        mandatoryOptional: compliance.MandatoryOptional || 'Not Specified',
        manualAutomatic: compliance.ManualAutomatic || 'Not Specified'
      }));
    } else {
      error.value = response.data.message || 'Failed to load controls';
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load controls. Please try again.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCompliances();
});
</script>

<style scoped>
/* Main Container */
.compliance-view-container {
  padding: 24px;
  margin-left: 280px;
  width: calc(100% - 280px);
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
  background-color: #f8fafc;
}

/* Header Section */
.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 0 4px;
}

.compliance-header h2 {
  color: #1f2937;
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0;
}

.compliance-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.compliance-export-btn,
.compliance-back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.compliance-export-btn {
  background-color: #3b82f6;
  color: white;
}

.compliance-export-btn:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.compliance-back-btn {
  background-color: #6b7280;
  color: white;
}

.compliance-back-btn:hover {
  background-color: #4b5563;
  transform: translateY(-1px);
}

/* Loading and Error States */
.compliance-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.compliance-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.compliance-error {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.compliance-retry-btn {
  background-color: #dc2626;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

/* Filter Section */
.controls-filter-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #e5e7eb;
}

.search-container {
  margin-bottom: 20px;
}

.dropdowns-row {
  display: flex;
  align-items: center;
  gap: 50px;
  flex-wrap: wrap;
}

.filter-dropdown {
  min-width: 180px;
  max-width: 220px;
  flex: 1;
}

/* Ensure dropdowns have consistent styling */
.filter-dropdown :deep(.dropdown-container) {
  width: 100%;
}

.filter-dropdown :deep(.dropdown-select) {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: white;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  transition: all 0.2s ease;
}

.filter-dropdown :deep(.dropdown-select):focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-dropdown :deep(.dropdown-select):hover {
  border-color: #d1d5db;
}

.filter-dropdown :deep(.dropdown-label) {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

/* Table Container */
.controls-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.controls-table {
  width: 100%;
  border-collapse: collapse;
}

.controls-table th,
.controls-table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.controls-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.controls-table th.active {
  color: #3b82f6;
}

.controls-table th:hover {
  background: #f3f4f6;
}

.controls-table th i {
  margin-left: 6px;
  font-size: 12px;
}

.controls-table tbody tr {
  transition: background-color 0.2s ease;
}

.controls-table tbody tr:hover {
  background: #f8fafc;
}

.control-title {
  color: #3b82f6;
  cursor: pointer;
  font-weight: 500;
}

.control-title:hover {
  text-decoration: underline;
  color: #2563eb;
}

/* Badge Styles */
.status-badge,
.criticality-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  display: inline-block;
}

/* Status badges */
.status-review { 
  background-color: #fef3c7; 
  color: #92400e; 
  border: 1px solid #f59e0b;
}
.status-approved { 
  background-color: #dcfce7; 
  color: #166534; 
  border: 1px solid #22c55e;
}
.status-rejected { 
  background-color: #fee2e2; 
  color: #991b1b; 
  border: 1px solid #ef4444;
}
.status-default { 
  background-color: #f3f4f6; 
  color: #4b5563; 
  border: 1px solid #9ca3af;
}

/* Criticality badges */
.criticality-high { 
  background-color: #fee2e2; 
  color: #991b1b; 
  border: 1px solid #ef4444;
}
.criticality-medium { 
  background-color: #fef3c7; 
  color: #92400e; 
  border: 1px solid #f59e0b;
}
.criticality-low { 
  background-color: #dcfce7; 
  color: #166534; 
  border: 1px solid #22c55e;
}

/* Action Buttons */
.action-column {
  white-space: nowrap;
}

.action-btn {
  padding: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 8px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn.view {
  background: #e5e7eb;
  color: #4b5563;
}

.action-btn.view:hover {
  background: #d1d5db;
  transform: translateY(-1px);
}

.action-btn.risk {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn.risk:hover {
  background: #fecaca;
  transform: translateY(-1px);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 700;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #374151;
  background: #e5e7eb;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.detail-item span,
.detail-item p {
  color: #1f2937;
  font-weight: 500;
  line-height: 1.5;
}

.risk-section {
  background: linear-gradient(135deg, #fff1f2 0%, #fef2f2 100%);
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #ef4444;
}

.risk-section h4 {
  color: #991b1b;
  border-bottom-color: #fecaca;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .compliance-view-container {
    margin-left: 200px;
    width: calc(100% - 200px);
    padding: 16px;
  }
  
  .dropdowns-row {
    gap: 16px;
  }
  
  .filter-dropdown {
    min-width: 150px;
    max-width: 180px;
  }
}

@media (max-width: 768px) {
  .compliance-view-container {
    margin-left: 0;
    width: 100%;
    padding: 12px;
  }
  
  .compliance-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .compliance-header h2 {
    font-size: 1.5rem;
  }
  
  .dropdowns-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-dropdown {
    min-width: 100%;
    max-width: 100%;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .controls-table th,
  .controls-table td {
    padding: 12px 16px;
  }
  
  .modal-content {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }
  
  .modal-header,
  .modal-body {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .compliance-view-container {
    padding: 8px;
  }
  
  .controls-filter-section {
    padding: 16px;
  }
  
  .compliance-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .compliance-export-btn,
  .compliance-back-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>