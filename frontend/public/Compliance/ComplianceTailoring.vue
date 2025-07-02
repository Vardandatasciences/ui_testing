<template>
  <div class="compliance-versioning-container">
    <div class="compliance-heading">
      <h1>Compliance Tailoring & Templating</h1>
      <div class="compliance-heading-underline"></div>
    </div>
    <div class="compliance-selection-row">
      <div class="compliance-selection-group">
        <CustomDropdown
          :config="frameworkDropdownConfig"
          v-model="selectedFrameworkId"
          :disabled="loading"
          @change="onFrameworkChange"
        />
      </div>
      <div class="compliance-selection-group">
        <CustomDropdown
          :config="policyDropdownConfig"
          v-model="selectedPolicyId"
          :disabled="!selectedFrameworkId || loading"
          @change="onPolicyChange"
        />
      </div>
      <div class="compliance-selection-group">
        <CustomDropdown
          :config="subPolicyDropdownConfig"
          v-model="selectedSubPolicyId"
          :disabled="!selectedPolicyId || loading"
          @change="onSubPolicyChange"
        />
      </div>
  
    </div>

    <div class="compliance-loading-overlay" v-if="loading">
      <div class="compliance-spinner"></div>
      <div class="compliance-loading-text">Loading data...</div>
    </div>
    
    <div v-if="error" class="compliance-error-message">
      <i class="fas fa-exclamation-triangle"></i> {{ error }}
      <button @click="refreshCurrentData" class="compliance-retry-btn">Retry</button>
    </div>

    <div v-if="selectedSubPolicy" class="compliance-table-container">
      <h3>Compliances for Selected Subpolicy</h3>
      <div v-if="loading" class="loading">Loading compliances...</div>
      <div v-else-if="complianceList.length === 0" class="no-compliances">No compliances found for this subpolicy.</div>
      <DynamicTable
        v-else
        :data="complianceList"
        :columns="tableColumns"
        :showActions="true"
      >
        <template #actions="{ row }">
          <div class="compliance-action-btn-group">
            <button @click="navigateToEdit(row)" title="Edit" class="compliance-action-btn compliance-edit-btn">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="startCopy(row)" title="Copy" class="compliance-action-btn compliance-copy-btn">
              <i class="fas fa-copy"></i>
            </button>
          </div>
        </template>
      </DynamicTable>
    </div>

    <!-- Modal removed - CopyCompliance is now a separate page -->

    <!-- Add PopupModal component at the end -->
    <PopupModal />
  </div>
</template>

<script>
import { PopupModal, PopupService } from '../../modules/popup';
import PopupMixin from './mixins/PopupMixin';
import { CompliancePopups } from './utils/popupUtils';
import { complianceService } from '@/services/api';
import CustomDropdown from '../CustomDropdown.vue';
import DynamicTable from '../DynamicTable.vue';
export default {
  name: 'ComplianceTailoring',
  components: {
    PopupModal,
    CustomDropdown,
    DynamicTable
  },
  mixins: [PopupMixin],
  data() {
    return {
      frameworks: [],
      selectedFramework: '',
      selectedFrameworkId: '',
      policies: [],
      selectedPolicy: '',
      selectedPolicyId: '',
      complianceSubPolicies: [],
      selectedSubPolicy: '',
      selectedSubPolicyId: '',
      complianceList: [],
      loading: false,
      error: null,
      frameworkDropdownConfig: {
        label: 'Framework',
        values: []
      },
      policyDropdownConfig: {
        label: 'Policy',
        values: []
      },
      subPolicyDropdownConfig: {
        label: 'Sub Policy',
        values: []
      },
      categoryOptions: {
        RiskCategory: [],
        RiskType: [],
        BusinessUnitsCovered: [],
        RiskBusinessImpact: []
      },
      tableColumns: [
        { key: 'ComplianceTitle', label: 'Title' },
        { key: 'ComplianceItemDescription', label: 'Description' },
        { key: 'Status', label: 'Status' },
        { key: 'ComplianceVersion', label: 'Version' }
      ]
    }
  },
  async created() {
    await this.loadFrameworks();
    await this.loadUsers();
    await this.loadCategoryOptions();
    
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  watch: {
    selectedFrameworkId(newId) {
      const fw = this.frameworks.find(fw => fw.id === newId);
      this.selectedFramework = fw || '';
      if (fw) {
        this.loadPolicies(fw.id);
        this.selectedPolicy = '';
        this.selectedPolicyId = '';
        this.selectedSubPolicy = '';
        this.selectedSubPolicyId = '';
        this.policies = [];
        this.complianceSubPolicies = [];
        this.complianceList = [];
      }
    },
    selectedPolicyId(newId) {
      const p = this.policies.find(p => p.id === newId);
      this.selectedPolicy = p || '';
      if (p) {
        this.loadSubPolicies(p.id);
        this.selectedSubPolicy = '';
        this.selectedSubPolicyId = '';
        this.complianceSubPolicies = [];
        this.complianceList = [];
      }
    },
    selectedSubPolicyId(newId) {
      const sp = this.complianceSubPolicies.find(sp => sp.id === newId);
      this.selectedSubPolicy = sp || '';
      if (sp) {
        this.loadCompliances();
      } else {
        this.complianceList = [];
      }
    },
  },
  computed: {
  },
  methods: {
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getComplianceFrameworks();
        console.log('Frameworks response:', response.data);
        
        let frameworksData;
        if (response.data.success && response.data.frameworks) {
          frameworksData = response.data.frameworks;
        } else if (Array.isArray(response.data)) {
          frameworksData = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
          this.error = 'Failed to load frameworks';
          return;
        }
        
        this.frameworks = frameworksData.map(fw => ({
          id: fw.id,
          name: fw.name
        }));
        
        console.log('Loaded frameworks:', this.frameworks);
        this.frameworkDropdownConfig.values = this.frameworks.map(fw => ({
          value: fw.id,
          label: fw.name
        }));
      } catch (error) {
        this.error = 'Failed to load frameworks';
        console.error('Error loading frameworks:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadPolicies(frameworkId) {
      try {
        this.loading = true;
        const response = await complianceService.getCompliancePolicies(frameworkId);
        if (response.data.success && response.data.policies) {
          this.policies = response.data.policies.map(p => ({
            id: p.id,
            name: p.name,
            applicability: p.scope || ''
          }));
          this.policyDropdownConfig.values = this.policies.map(p => ({
            value: p.id,
            label: p.name
          }));
        } else {
          console.error('Error in response:', response.data);
          this.error = 'Failed to load policies';
        }
      } catch (error) {
        this.error = 'Failed to load policies';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies(policyId) {
      try {
        this.loading = true;
        const response = await complianceService.getComplianceSubPolicies(policyId);
        console.log('SubPolicies response:', response);
        
        if (response.data.success && response.data.subpolicies) {
          console.log('SubPolicies data:', response.data.subpolicies);
          this.complianceSubPolicies = response.data.subpolicies.map(sp => ({
            id: sp.id,
            name: sp.name
          }));
          console.log('Mapped complianceSubPolicies:', this.complianceSubPolicies);
          this.subPolicyDropdownConfig.values = this.complianceSubPolicies.map(sp => ({
            value: sp.id,
            label: sp.name
          }));
        } else {
          console.error('Error in response:', response.data);
          this.error = 'Failed to load sub-policies';
        }
      } catch (error) {
        this.error = 'Failed to load sub-policies';
        console.error('SubPolicies error:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadUsers() {
      try {
        this.loading = true;
        const response = await complianceService.getUsers();
        console.log('Users API response:', response);
        
        if (response.data.success && Array.isArray(response.data.users)) {
          this.users = response.data.users;
          console.log('Loaded users:', this.users);
        } else {
          console.error('Invalid users data received:', response.data);
          this.error = 'Failed to load approvers';
        }
      } catch (error) {
        console.error('Failed to load users:', error);
        this.error = 'Failed to load approvers. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async loadCategoryOptions() {
      try {
        this.loading = true;
        
        const rcResponse = await complianceService.getCategoryBusinessUnits('RiskCategory');
        if (rcResponse.data.success) {
          this.categoryOptions.RiskCategory = rcResponse.data.data;
        }
        
        const rtResponse = await complianceService.getCategoryBusinessUnits('RiskType');
        if (rtResponse.data.success) {
          this.categoryOptions.RiskType = rtResponse.data.data;
        }
        
        const buResponse = await complianceService.getCategoryBusinessUnits('BusinessUnitsCovered');
        if (buResponse.data.success) {
          this.categoryOptions.BusinessUnitsCovered = buResponse.data.data;
        }
        
        const rbiResponse = await complianceService.getCategoryBusinessUnits('RiskBusinessImpact');
        if (rbiResponse.data.success) {
          this.categoryOptions.RiskBusinessImpact = rbiResponse.data.data;
        }
      } catch (error) {
        console.error('Failed to load category options:', error);
        PopupService.error('Failed to load dropdown options. Some features may be limited.');
      } finally {
        this.loading = false;
      }
    },
    showDropdown(field) {
      this.activeDropdown = field;
      
      this.filterOptions(field);
      
      event.stopPropagation();
    },
    handleClickOutside(event) {
      const dropdowns = document.querySelectorAll('.searchable-dropdown');
      let clickedOutside = true;
      
      dropdowns.forEach(dropdown => {
        if (dropdown.contains(event.target)) {
          clickedOutside = false;
        }
      });
      
      if (clickedOutside) {
        this.activeDropdown = null;
      }
    },
    filterOptions(field) {
      let searchTerm = '';
      
      switch (field) {
        case 'BusinessUnitsCovered':
          searchTerm = this.businessUnitSearch || '';
          break;
        case 'RiskType':
          searchTerm = this.riskTypeSearch || '';
          break;
        case 'RiskCategory':
          searchTerm = this.riskCategorySearch || '';
          break;
        case 'RiskBusinessImpact':
          searchTerm = this.riskBusinessImpactSearch || '';
          break;
      }
      
      const lowerSearchTerm = searchTerm.toLowerCase();
      this.filteredOptions[field] = this.categoryOptions[field].filter(option => 
        option.value.toLowerCase().includes(lowerSearchTerm)
      );
    },
    selectOption(field, value) {
      this.editRow[field] = value;
      
      switch (field) {
        case 'BusinessUnitsCovered':
          this.businessUnitSearch = value;
          break;
        case 'RiskType':
          this.riskTypeSearch = value;
          break;
        case 'RiskCategory':
          this.riskCategorySearch = value;
          break;
        case 'RiskBusinessImpact':
          this.riskBusinessImpactSearch = value;
          break;
      }
      
      this.activeDropdown = null;
    },
    async addNewOption(field, value) {
      if (!value || !value.trim()) return;
      
      try {
        this.loading = true;
        
        const response = await complianceService.addCategoryBusinessUnit({
          source: field,
          value: value.trim()
        });
        
        if (response.data.success) {
          const newOption = {
            id: response.data.data.id,
            value: response.data.data.value
          };
          
          this.categoryOptions[field] = [...this.categoryOptions[field], newOption];
          this.filteredOptions[field] = [...this.filteredOptions[field], newOption];
          
          this.selectOption(field, newOption.value);
          
          this.editRow[field] = newOption.value;
          
          CompliancePopups.complianceCreated({
            message: `Added new ${field} option: ${newOption.value}`
          });
          
          await this.loadCategoryOptions();
        } else {
          throw new Error(response.data.error || 'Failed to add new option');
        }
      } catch (error) {
        console.error(`Failed to add new ${field} option:`, error);
        this.error = `Failed to add new option: ${error.message || error}`;
      } finally {
        this.loading = false;
      }
    },
    async loadCompliances() {
      if (!this.selectedSubPolicy) return;
      
      try {
        this.loading = true;
        const response = await complianceService.getCompliancesByType('subpolicy', this.selectedSubPolicy.id);
        console.log('Compliances response:', response);
        
        if (response.data.success && response.data.compliances) {
          this.complianceList = response.data.compliances;
          console.log('Loaded compliances:', this.complianceList);
        } else {
          console.error('Error in response:', response.data);
          this.error = 'Failed to load compliances';
        }
      } catch (error) {
        this.error = 'Failed to load compliances';
        console.error('Compliances error:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        let date;
        if (typeof dateString === 'string') {
          if (dateString.includes('T')) {
            date = new Date(dateString);
          } else if (dateString.includes('-')) {
            const parts = dateString.split(' ')[0].split('-');
            date = new Date(parts[0], parts[1] - 1, parts[2]);
          } else if (dateString.includes('/')) {
            const parts = dateString.split(' ')[0].split('/');
            date = new Date(parts[2], parts[0] - 1, parts[1]);
          } else {
            date = new Date(dateString);
          }
        } else {
          date = new Date(dateString);
        }
        
        return date.toLocaleString();
      } catch (e) {
        console.error('Error formatting date:', e);
        return dateString;
      }
    },
    viewComplianceDetails(compliance) {
      CompliancePopups.showComplianceInfo(compliance);
    },
    getDefaultDueDate() {
      const date = new Date();
      date.setDate(date.getDate() + 7);
      return date.toISOString().split('T')[0];
    },
    navigateToEdit(compliance) {
      this.$router.push(`/compliance/edit/${compliance.ComplianceId}`);
    },
    parseMitigationSteps(mitigation) {
      if (!mitigation) return [{ description: '' }];
      
      try {
        if (typeof mitigation === 'string') {
          return [{ description: mitigation }];
        } else if (Array.isArray(mitigation)) {
          return mitigation.map(step => ({
            description: typeof step === 'string' ? step : step.description || ''
          }));
        } else if (typeof mitigation === 'object') {
          return Object.values(mitigation).map(step => ({
            description: typeof step === 'string' ? step : step.description || ''
          }));
        }
      } catch (error) {
        console.error('Error parsing mitigation steps:', error);
      }
      
      return [{ description: '' }];
    },
    addStep(row) {
      if (!row.mitigationSteps) {
        row.mitigationSteps = [];
      }
      row.mitigationSteps.push({ description: '' });
    },
    removeStep(row, index) {
      row.mitigationSteps.splice(index, 1);
      if (row.mitigationSteps.length === 0) {
        row.mitigationSteps.push({ description: '' });
      }
      this.onMitigationStepChange(row);
    },
    onMitigationStepChange(row) {
      row.mitigation = row.mitigationSteps.reduce((obj, step, index) => {
        obj[`step${index + 1}`] = step.description;
        return obj;
      }, {});
    },
    startCopy(compliance) {
      // Navigate to the copy compliance page with the compliance ID and current context
      this.$router.push({
        name: 'CopyCompliance',
        params: { id: compliance.ComplianceId },
        query: {
          frameworkId: this.selectedFramework?.id || '',
          frameworkName: this.selectedFramework?.name || '',
          policyId: this.selectedPolicy?.id || '',
          policyName: this.selectedPolicy?.name || '',
          subPolicyId: this.selectedSubPolicy?.id || '',
          subPolicyName: this.selectedSubPolicy?.name || ''
        }
      });
    },
    async handleCopySuccess() {
      await this.loadCompliances();
      CompliancePopups.complianceCreated({
        message: 'Compliance copied successfully'
      });
    },
    onFrameworkChange(option) {
      this.selectedFrameworkId = option.value;
    },
    onPolicyChange(option) {
      this.selectedPolicyId = option.value;
    },
    onSubPolicyChange(option) {
      this.selectedSubPolicyId = option.value;
    },
  }
}
</script>

<style scoped>
@import './ComplianceTailoring.css';

.rejected-compliances-section {
  margin: 2rem 24px;
  background-color: #fff8f8;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid #e6d0d0;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.1);
  position: relative;
}

.rejected-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #e6d0d0;
}

.rejected-header h3 {
  color: #c00;
  font-size: 1.2rem;
  font-weight: 600;
}

.refresh-rejected-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #dc3545;
  background-color: #fff;
  color: #dc3545;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.refresh-rejected-btn:hover {
  background-color: #dc3545;
  color: white;
}

.rejected-loading {
  margin-top: 1rem;
  text-align: center;
  color: #666;
}

.no-rejected {
  text-align: center;
  color: #666;
}

.rejected-compliances-list {
  margin-top: 1rem;
}

.rejected-compliance-item {
  background-color: white;
  border: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 4px;
  position: relative;
}

.rejected-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.badge.rejected {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.rejected-item-details {
  padding-left: 0.5rem;
  border-left: 2px solid #f0f0f0;
}

.meta-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.criticality {
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-weight: 500;
}

.criticality.high {
  background: #fee;
  color: #c00;
}

.criticality.medium {
  background: #ffd;
  color: #960;
}

.criticality.low {
  background: #efe;
  color: #060;
}

.rejected-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #d32f2f;
}

.rejection-reason {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fff0f0;
  border-left: 3px solid #ff3333;
  border-radius: 0 4px 4px 0;
  color: #c00;
  font-size: 0.9rem;
}

.edit-rejected-btn {
  margin-top: 1rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.edit-rejected-btn:hover {
  background-color: #eeeeee;
  border-color: #ccc;
}

.edit-rejected-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-rejected-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.resubmit-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.mitigation-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mitigation-step {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background: #f9f9f9;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.step-number {
  font-weight: 500;
  color: #666;
}

.remove-step-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.remove-step-btn:hover {
  background: #fee;
}

.add-step-btn {
  background: #f8f9fa;
  border: 1px dashed #ddd;
  color: #666;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.add-step-btn:hover {
  background: #fff;
  border-color: #999;
  color: #333;
}

.compliance-copy-form-grid {
  display: grid;
  gap: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.compliance-form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: start;
}

.compliance-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.compliance-form-group label {
  font-weight: 600;
  color: #495057;
}

.compliance-input,
.compliance-select {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%;
}

.compliance-input:focus,
.compliance-select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.compliance-form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.compliance-save-btn,
.compliance-cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.compliance-save-btn {
  background-color: #28a745;
  color: white;
}

.compliance-save-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.compliance-cancel-btn {
  background-color: #dc3545;
  color: white;
}

.compliance-action-btn-group {
  display: flex;
  gap: 0.5rem;
}

.compliance-action-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.compliance-edit-btn {
  background-color: #ffc107;
  color: #212529;
}

.compliance-copy-btn {
  background-color: #17a2b8;
  color: white;
}

.compliance-action-btn:hover {
  opacity: 0.8;
}

.compliance-action-btn i {
  font-size: 1rem;
}

.searchable-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ced4da;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1000;
}

.dropdown-option {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-option:hover {
  background-color: #f8f9fa;
}

.dropdown-add-option {
  padding: 8px 12px;
  border-bottom: 1px solid #ced4da;
}

.dropdown-add-btn {
  display: block;
  width: 100%;
  padding: 4px 8px;
  margin-top: 4px;
  border: none;
  background: #e9ecef;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-add-btn:hover {
  background: #dee2e6;
}

.compliance-input:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,0.25);
}

.compliance-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
</style> 