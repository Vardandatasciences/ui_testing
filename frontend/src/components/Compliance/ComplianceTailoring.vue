<template>
  <div class="compliance-versioning-container">
    <div class="compliance-heading">
      <h1>Compliance Tailoring & Templating</h1>
      <div class="heading-underline"></div>
    </div>
    <div class="compliance-selection-row">
      <div class="compliance-selection-group">
        <select v-model="selectedFramework" class="compliance-select">
          <option disabled value="">Select Framework</option>
          <option v-for="fw in frameworks" :key="fw.id" :value="fw">{{ fw.name }}</option>
        </select>
      </div>
      <div class="compliance-selection-group">
        <select v-model="selectedPolicy" class="compliance-select" :disabled="!selectedFramework">
          <option disabled value="">Select Policy</option>
          <option v-for="p in policies" :key="p.id" :value="p">{{ p.name }}</option>
        </select>
      </div>
      <div class="compliance-selection-group">
        <select v-model="selectedSubPolicy" class="compliance-select" :disabled="!selectedPolicy">
          <option disabled value="">Select Sub Policy</option>
          <option v-for="sp in subPolicies" :key="sp.id" :value="sp">{{ sp.name }}</option>
        </select>
      </div>
      <button @click="refreshCurrentData" class="compliance-refresh-btn" title="Refresh Data">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
      </button>
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
      <div v-else-if="subPolicyCompliances.length === 0" class="no-compliances">No compliances found for this subpolicy.</div>
      <table v-else class="compliance-table">
        <thead>
          <tr>
            <th>Description</th>
            <th>Possible Damage</th>
            <th>Mitigation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(compliance, idx) in subPolicyCompliances" :key="compliance.ComplianceId">
            <!-- If in edit mode, show the full form -->
            <template v-if="editIdx === idx">
              <td colspan="4">
                <form @submit.prevent="confirmEdit" class="compliance-edit-form-grid">
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Description</label>
                      <input v-model="editRow.ComplianceItemDescription" class="compliance-input" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Is Risk</label>
                      <select v-model="editRow.IsRisk" class="compliance-select">
                        <option :value="true">Yes</option>
                        <option :value="false">No</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Possible Damage</label>
                      <input v-model="editRow.PossibleDamage" class="compliance-input" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Mitigation</label>
                      <input v-model="editRow.mitigation" class="compliance-input" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Criticality</label>
                      <select v-model="editRow.Criticality" class="compliance-select">
                        <option>High</option>
                        <option>Medium</option>
                        <option>Low</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Mandatory/Optional</label>
                      <select v-model="editRow.MandatoryOptional" class="compliance-select">
                        <option>Mandatory</option>
                        <option>Optional</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Manual/Automatic</label>
                      <select v-model="editRow.ManualAutomatic" class="compliance-select">
                        <option>Manual</option>
                        <option>Automatic</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Impact (1-10)</label>
                      <input type="number" v-model.number="editRow.Impact" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Maturity Level</label>
                      <select v-model="editRow.MaturityLevel">
                        <option>Initial</option>
                        <option>Developing</option>
                        <option>Defined</option>
                        <option>Managed</option>
                        <option>Optimizing</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Version Type</label>
                      <select v-model="editRow.versionType" class="compliance-select" required>
                        <option value="major">Major</option>
                        <option value="minor">Minor</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Potential Risk Scenarios</label>
                      <textarea v-model="editRow.PotentialRiskScenarios" class="compliance-input" placeholder="Describe potential risk scenarios" rows="3"></textarea>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Risk Type</label>
                      <div class="searchable-dropdown">
                        <input 
                          v-model="riskTypeSearch" 
                          class="compliance-input" 
                          placeholder="Search or add risk type"
                          title="Type of risk (e.g. Operational, Financial, Strategic)"
                          @focus="showDropdown('RiskType')"
                          @input="filterOptions('RiskType')"
                        />
                        <div v-show="activeDropdown === 'RiskType'" class="dropdown-options">
                          <div v-if="filteredOptions.RiskType.length === 0 && riskTypeSearch" class="dropdown-add-option">
                            <span>No matches found. Add new:</span>
                            <button @click="addNewOption('RiskType', riskTypeSearch)" class="dropdown-add-btn">
                              + Add "{{ riskTypeSearch }}"
                            </button>
                          </div>
                          <div 
                            v-for="option in filteredOptions.RiskType" 
                            :key="option.id" 
                            class="dropdown-option"
                            @click="selectOption('RiskType', option.value)"
                          >
                            {{ option.value }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="compliance-form-group">
                      <label>Risk Category</label>
                      <div class="searchable-dropdown">
                        <input 
                          v-model="riskCategorySearch" 
                          class="compliance-input" 
                          placeholder="Search or add risk category"
                          title="Category of risk (e.g. People, Process, Technology)"
                          @focus="showDropdown('RiskCategory')"
                          @input="filterOptions('RiskCategory')"
                        />
                        <div v-show="activeDropdown === 'RiskCategory'" class="dropdown-options">
                          <div v-if="filteredOptions.RiskCategory.length === 0 && riskCategorySearch" class="dropdown-add-option">
                            <span>No matches found. Add new:</span>
                            <button @click="addNewOption('RiskCategory', riskCategorySearch)" class="dropdown-add-btn">
                              + Add "{{ riskCategorySearch }}"
                            </button>
                          </div>
                          <div 
                            v-for="option in filteredOptions.RiskCategory" 
                            :key="option.id" 
                            class="dropdown-option"
                            @click="selectOption('RiskCategory', option.value)"
                          >
                            {{ option.value }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Risk Business Impact</label>
                      <div class="searchable-dropdown">
                        <input 
                          v-model="riskBusinessImpactSearch" 
                          class="compliance-input" 
                          placeholder="Search or add business impact"
                          title="How this risk impacts business operations"
                          @focus="showDropdown('RiskBusinessImpact')"
                          @input="filterOptions('RiskBusinessImpact')"
                        />
                        <div v-show="activeDropdown === 'RiskBusinessImpact'" class="dropdown-options">
                          <div v-if="filteredOptions.RiskBusinessImpact.length === 0 && riskBusinessImpactSearch" class="dropdown-add-option">
                            <span>No matches found. Add new:</span>
                            <button @click="addNewOption('RiskBusinessImpact', riskBusinessImpactSearch)" class="dropdown-add-btn">
                              + Add "{{ riskBusinessImpactSearch }}"
                            </button>
                          </div>
                          <div 
                            v-for="option in filteredOptions.RiskBusinessImpact" 
                            :key="option.id" 
                            class="dropdown-option"
                            @click="selectOption('RiskBusinessImpact', option.value)"
                          >
                            {{ option.value }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="compliance-form-group">
                      <label>Applicability</label>
                      <input v-model="editRow.Applicability" class="compliance-input" placeholder="Applicability" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Approver</label>
                      <select v-model="editRow.reviewer_id" class="compliance-select" required>
                        <option disabled value="">Select Approver</option>
                        <option v-for="user in users" :key="user.UserId" :value="user.UserId">{{ user.UserName }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Business Units Covered</label>
                      <div class="searchable-dropdown">
                        <input 
                          v-model="businessUnitSearch" 
                          class="compliance-input" 
                          placeholder="Search or add business units"
                          title="Departments or business units affected by this compliance"
                          @focus="showDropdown('BusinessUnitsCovered')"
                          @input="filterOptions('BusinessUnitsCovered')"
                        />
                        <div v-show="activeDropdown === 'BusinessUnitsCovered'" class="dropdown-options">
                          <div v-if="filteredOptions.BusinessUnitsCovered.length === 0 && businessUnitSearch" class="dropdown-add-option">
                            <span>No matches found. Add new:</span>
                            <button @click="addNewOption('BusinessUnitsCovered', businessUnitSearch)" class="dropdown-add-btn">
                              + Add "{{ businessUnitSearch }}"
                            </button>
                          </div>
                          <div 
                            v-for="option in filteredOptions.BusinessUnitsCovered" 
                            :key="option.id" 
                            class="dropdown-option"
                            @click="selectOption('BusinessUnitsCovered', option.value)"
                          >
                            {{ option.value }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="compliance-form-actions">
                    <button type="submit">Save as New Version</button>
                    <button type="button" @click="cancelEdit">Cancel</button>
                  </div>
                </form>
              </td>
            </template>
            <!-- If in copy mode, show the copy form inline -->
            <template v-else-if="copyIdx === idx">
              <td colspan="4">
                <form @submit.prevent="confirmCopy" class="compliance-edit-form-grid">
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Description</label>
                      <input v-model="copyRow.ComplianceItemDescription" class="compliance-input" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Is Risk</label>
                      <select v-model="copyRow.IsRisk" class="compliance-select">
                        <option :value="true">Yes</option>
                        <option :value="false">No</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Possible Damage</label>
                      <input v-model="copyRow.PossibleDamage" class="compliance-input" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Mitigation</label>
                      <input v-model="copyRow.mitigation" class="compliance-input" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Criticality</label>
                      <select v-model="copyRow.Criticality" class="compliance-select">
                        <option>High</option>
                        <option>Medium</option>
                        <option>Low</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Mandatory/Optional</label>
                      <select v-model="copyRow.MandatoryOptional" class="compliance-select">
                        <option>Mandatory</option>
                        <option>Optional</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Manual/Automatic</label>
                      <select v-model="copyRow.ManualAutomatic" class="compliance-select">
                        <option>Manual</option>
                        <option>Automatic</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Impact (1-10)</label>
                      <input type="number" v-model.number="copyRow.Impact" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Maturity Level</label>
                      <select v-model="copyRow.MaturityLevel">
                        <option>Initial</option>
                        <option>Developing</option>
                        <option>Defined</option>
                        <option>Managed</option>
                        <option>Optimizing</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Version Type</label>
                      <select v-model="copyRow.versionType" class="compliance-select" required>
                        <option value="major">Major</option>
                        <option value="minor">Minor</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Potential Risk Scenarios</label>
                      <textarea v-model="copyRow.PotentialRiskScenarios" class="compliance-input" placeholder="Describe potential risk scenarios" rows="3"></textarea>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Risk Type</label>
                      <input v-model="copyRow.RiskType" class="compliance-input" placeholder="Enter risk type" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Risk Category</label>
                      <input v-model="copyRow.RiskCategory" class="compliance-input" placeholder="Enter risk category" />
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Risk Business Impact</label>
                      <input v-model="copyRow.RiskBusinessImpact" class="compliance-input" placeholder="Enter business impact" />
                    </div>
                    <div class="compliance-form-group">
                      <label>Applicability</label>
                      <input v-model="copyRow.Applicability" class="compliance-input" placeholder="Applicability" />
                    </div>
                  </div>
                  <div class="compliance-form-row framework-policy-row">
                    <div class="compliance-form-group">
                      <label>Framework</label>
                      <select v-model="copyTarget.frameworkId" disabled>
                        <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Policy</label>
                      <select v-model="copyTarget.policyId" :disabled="!copyTarget.frameworkId">
                        <option disabled value="">Select Policy</option>
                        <option v-for="p in copyPolicies" :key="p.id" :value="p.id">{{ p.name }}</option>
                      </select>
                    </div>
                    <div class="compliance-form-group">
                      <label>Sub Policy</label>
                      <select v-model="copyTarget.subPolicyId" :disabled="!copyTarget.policyId">
                        <option disabled value="">Select Sub Policy</option>
                        <option v-for="sp in filteredCopySubPolicies" :key="sp.id" :value="sp.id">{{ sp.name }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>Approver</label>
                      <select v-model="copyRow.reviewer_id" class="compliance-select" required>
                        <option disabled value="">Select Approver</option>
                        <option v-for="user in users" :key="user.UserId" :value="user.UserId">{{ user.UserName }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="compliance-form-row">
                    <div class="compliance-form-group">
                      <label>&nbsp;</label>
                      <div>
                        <button type="submit" :disabled="!canSaveCopy">Save Copy</button>
                        <button type="button" @click="cancelCopy">Cancel</button>
                      </div>
                    </div>
                    <div v-if="copyError" class="copy-error">{{ copyError }}</div>
                  </div>
                </form>
              </td>
            </template>
            <!-- Normal view: only 3 fields + actions -->
            <template v-else>
              <td>{{ compliance.ComplianceItemDescription || 'No description available' }}</td>
              <td>{{ compliance.PossibleDamage || 'No damage information' }}</td>
              <td>{{ compliance.mitigation || compliance.Mitigation || 'No mitigation details' }}</td>
              <td>
                <div class="compliance-action-btn-group">
                  <button @click="navigateToEdit(compliance)" title="Edit" class="compliance-action-btn compliance-edit-btn"><i class="fas fa-edit"></i></button>
                  <button @click="navigateToCopy(compliance)" title="Copy" class="compliance-action-btn compliance-copy-btn"><i class="fas fa-copy"></i></button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add PopupModal component at the end -->
    <PopupModal />
  </div>
</template>

<script>
import { PopupModal } from '../../modules/popup';
import PopupMixin from './mixins/PopupMixin';
import { CompliancePopups } from './utils/popupUtils';
import { complianceService } from '@/services/api';

export default {
  name: 'ComplianceTailoring',
  components: {
    PopupModal
  },
  mixins: [PopupMixin],
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: [],
      policies: [],
      subPolicies: [],
      subPolicyCompliances: [],
      loading: false,
      error: null,
      editIdx: null,
      editRow: {},
      // Copy inline state
      copyIdx: null,
      copyRow: {},
      copyTarget: { frameworkId: '', policyId: '', subPolicyId: '' },
      copyPolicies: [],
      copySubPolicies: [],
      copyError: '',
      sourceSubPolicyId: null, // Track source subpolicy
      users: [], // Add users array for storing the list of users
      // Category options
      categoryOptions: {
        BusinessUnitsCovered: [],
        RiskType: [],
        RiskCategory: [],
        RiskBusinessImpact: []
      },
      // Filtered options for dropdowns
      filteredOptions: {
        BusinessUnitsCovered: [],
        RiskType: [],
        RiskCategory: [],
        RiskBusinessImpact: []
      },
      // Search terms for dropdowns
      businessUnitSearch: '',
      riskTypeSearch: '',
      riskCategorySearch: '',
      riskBusinessImpactSearch: '',
      // Active dropdown tracking
      activeDropdown: null,
    }
  },
  async created() {
    await this.loadFrameworks();
    await this.loadUsers();
    await this.loadCategoryOptions();
    
    // Add click event listener to close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // Remove event listener when component is unmounted
    document.removeEventListener('click', this.handleClickOutside);
  },
  watch: {
    selectedFramework(newValue) {
      if (newValue && newValue.id) {
        this.loadPolicies(newValue.id);
        this.selectedPolicy = '';
        this.selectedSubPolicy = '';
        this.policies = [];
        this.subPolicies = [];
        this.subPolicyCompliances = [];
      }
    },
    selectedPolicy(newValue) {
      if (newValue && newValue.id) {
        this.loadSubPolicies(newValue.id);
        this.selectedSubPolicy = '';
        this.subPolicies = [];
        this.subPolicyCompliances = [];
        
        // If editing or cloning, update the applicability from the selected policy
        if (this.editIdx !== null && this.editRow) {
          this.editRow.Applicability = newValue.applicability || '';
        }
        if (this.copyIdx !== null && this.copyRow) {
          this.copyRow.Applicability = newValue.applicability || '';
        }
      }
    },
    selectedSubPolicy: {
      handler: async function(newValue) {
        if (newValue && newValue.id) {
          await this.loadCompliances();
        } else {
          this.subPolicyCompliances = [];
        }
      },
      immediate: true
    },
    'copyTarget.frameworkId': 'copyTarget_frameworkId',
    'copyTarget.policyId': 'copyTarget_policyId'
  },
  computed: {
    canSaveCopy() {
      // Validate all required fields are filled and subpolicy is different from source
      return this.copyRow.ComplianceItemDescription &&
        this.copyTarget.frameworkId &&
        this.copyTarget.policyId &&
        this.copyTarget.subPolicyId &&
        this.copyTarget.subPolicyId !== this.sourceSubPolicyId && // Must be different subpolicy
        this.copyRow.Criticality &&
        this.copyRow.MandatoryOptional &&
        this.copyRow.ManualAutomatic &&
        this.copyRow.Impact && 
        this.copyRow.Probability && 
        this.copyRow.MaturityLevel &&
        this.copyRow.reviewer_id; // Add reviewer validation
      // Note: PotentialRiskScenarios, RiskType, RiskCategory, and RiskBusinessImpact are optional fields
    },
    filteredCopySubPolicies() {
      // Filter out the source subpolicy from the dropdown to prevent copying to same subpolicy
      if (!this.copySubPolicies || !this.sourceSubPolicyId) {
        return this.copySubPolicies || [];
      }
      
      return this.copySubPolicies.filter(sp => {
        return sp.id !== this.sourceSubPolicyId;
      });
    }
  },
  methods: {
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getFrameworks();
        console.log('Frameworks response:', response.data);
        
        // Handle both response formats: direct array or success wrapper
        let frameworksData;
        if (response.data.success) {
          frameworksData = response.data.data;
        } else if (Array.isArray(response.data)) {
          frameworksData = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
          this.error = 'Failed to load frameworks';
          return;
        }
        
        this.frameworks = frameworksData.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }));
        
        console.log('Loaded frameworks:', this.frameworks);
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
        const response = await complianceService.getPolicies(frameworkId);
        if (response.data.success) {
          this.policies = response.data.data.map(p => ({
            id: p.PolicyId,
            name: p.PolicyName,
            applicability: p.Applicability || '' // Store the Applicability field
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
        const response = await complianceService.getSubPolicies(policyId);
        console.log('SubPolicies response:', response.data);
        
        if (response.data.success) {
          console.log('SubPolicies data:', response.data.data);
          this.subPolicies = response.data.data.map(sp => ({
            id: sp.SubPolicyId,
            name: sp.SubPolicyName
          }));
          console.log('Mapped subPolicies:', this.subPolicies);
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
        
        // Load business units
        const buResponse = await complianceService.getCategoryBusinessUnits('BusinessUnitsCovered');
        if (buResponse.data.success) {
          this.categoryOptions.BusinessUnitsCovered = buResponse.data.data;
        }
        
        // Load risk types
        const rtResponse = await complianceService.getCategoryBusinessUnits('RiskType');
        if (rtResponse.data.success) {
          this.categoryOptions.RiskType = rtResponse.data.data;
        }
        
        // Load risk categories
        const rcResponse = await complianceService.getCategoryBusinessUnits('RiskCategory');
        if (rcResponse.data.success) {
          this.categoryOptions.RiskCategory = rcResponse.data.data;
        }
        
        // Load risk business impacts
        const rbiResponse = await complianceService.getCategoryBusinessUnits('RiskBusinessImpact');
        if (rbiResponse.data.success) {
          this.categoryOptions.RiskBusinessImpact = rbiResponse.data.data;
        }
      } catch (error) {
        console.error('Failed to load category options:', error);
        CompliancePopups.error('Failed to load dropdown options. Some features may be limited.');
      } finally {
        this.loading = false;
      }
    },
    showDropdown(field) {
      // Close any open dropdown
      this.activeDropdown = field;
      
      // Set initial filtered options based on current search term
      this.filterOptions(field);
      
      // Prevent event from bubbling up
      event.stopPropagation();
    },
    handleClickOutside(event) {
      // Check if click is outside any dropdown
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
      
      // Filter options based on search term (case-insensitive)
      const lowerSearchTerm = searchTerm.toLowerCase();
      this.filteredOptions[field] = this.categoryOptions[field].filter(option => 
        option.value.toLowerCase().includes(lowerSearchTerm)
      );
    },
    selectOption(field, value) {
      // Update the edit row with the selected value
      this.editRow[field] = value;
      
      // Update the search field to show the selected value
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
      
      // Close the dropdown
      this.activeDropdown = null;
    },
    async addNewOption(field, value) {
      if (!value || !value.trim()) return;
      
      try {
        this.loading = true;
        
        // Add the new option to the server
        const response = await complianceService.addCategoryBusinessUnit({
          source: field,
          value: value.trim()
        });
        
        if (response.data.success) {
          // Add the new option to the local options and filtered options
          const newOption = {
            id: response.data.data.id,
            value: response.data.data.value
          };
          
          this.categoryOptions[field] = [...this.categoryOptions[field], newOption];
          this.filteredOptions[field] = [...this.filteredOptions[field], newOption];
          
          // Select the new option
          this.selectOption(field, newOption.value);
          
          // Update the editRow with the new value
          this.editRow[field] = newOption.value;
          
          // Show success message using CompliancePopups
          CompliancePopups.complianceCreated({
            message: `Added new ${field} option: ${newOption.value}`
          });
          
          // Refresh the category options to ensure sync with backend
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
    startEdit(compliance, idx) {
      this.editIdx = idx;
      this.editRow = { ...compliance };
      
      // Initialize search fields with current values
      this.businessUnitSearch = compliance.BusinessUnitsCovered || '';
      this.riskTypeSearch = compliance.RiskType || '';
      this.riskCategorySearch = compliance.RiskCategory || '';
      this.riskBusinessImpactSearch = compliance.RiskBusinessImpact || '';
    },
    cancelEdit() {
      this.editIdx = null;
      this.editRow = {};
      
      // Clear search fields
      this.businessUnitSearch = '';
      this.riskTypeSearch = '';
      this.riskCategorySearch = '';
      this.riskBusinessImpactSearch = '';
      
      // Close any open dropdown
      this.activeDropdown = null;
    },
    async saveEdit(compliance) {
      try {
        this.loading = true;
        await this.$nextTick();
        
        // Use the popup confirmation instead of the confirm dialog
        this.confirmEditCompliance(compliance, async () => {
          // Calculate new version based on version type
          const currentVersion = parseFloat(compliance.ComplianceVersion) || 1.0;
          let newVersion;
          
          if (this.editRow.versionType === 'major') {
            // For major version, increment the base number and set decimal to 0
            const baseVersion = Math.floor(currentVersion);
            newVersion = (baseVersion + 1).toFixed(1);
          } else {
            // For minor version, add 0.1 to the current version
            newVersion = (currentVersion + 0.1).toFixed(1);
          }
          
          // Always set new versions to Under Review and Inactive
          this.editRow = {
            ...this.editRow,
            ComplianceVersion: newVersion,
            Status: 'Under Review',
            ActiveInactive: 'Inactive',
            PreviousComplianceVersionId: compliance.ComplianceId,
            reviewer_id: this.editRow.reviewer_id // Include the selected reviewer ID
          };
          
          console.log("Creating new compliance version:", this.editRow);
          
          // Use the complianceService instead of direct axios
          const response = await complianceService.editCompliance(compliance.ComplianceId, this.editRow);
          console.log("Edited compliance response:", response);
          
          if (response.data && response.data.success) {
            // Show success popup with more details
            CompliancePopups.complianceUpdated({
              ComplianceId: response.data.compliance_id || compliance.ComplianceId,
              ComplianceVersion: newVersion,
              ComplianceItemDescription: this.editRow.ComplianceItemDescription || compliance.ComplianceItemDescription
            });

            // Show additional info popup with details about what changed
            CompliancePopups.notify(
              `Changes made:\n` +
              `- Description: ${this.editRow.ComplianceItemDescription}\n` +
              `- Is Risk: ${this.editRow.IsRisk ? 'Yes' : 'No'}\n` +
              `- Possible Damage: ${this.editRow.PossibleDamage}\n` +
              `- Mitigation: ${this.editRow.mitigation}\n` +
              `\nNew version ${newVersion} has been created and sent for review.`,
              'info',
              'Edit Details',
              5000 // Show for 5 seconds
            );
          } else {
            // Show error popup
            CompliancePopups.operationFailed('save compliance', response.data.message || 'Failed to save changes');
          }
          
          this.editIdx = null;
          this.editRow = {};
          
          // Refresh compliances
          await this.refreshCurrentData();
        });
        this.loading = false;
      } catch (error) {
        console.error('Edit error:', error);
        CompliancePopups.operationFailed('save changes', error.response?.data?.message || error.message);
        this.loading = false;
      }
    },
    // Copy modal logic
    async openCopyInline(idx, compliance) {
      this.editIdx = null; // Cancel edit mode if active
      this.copyIdx = idx;
      
      // Get the policy's applicability if available
      const policyApplicability = this.selectedPolicy ? this.selectedPolicy.applicability : '';
      
      this.copyRow = { 
        ...compliance,
        reviewer_id: compliance.reviewer_id || (this.users.length > 0 ? this.users[0].UserId : ''), // Set default reviewer
        // Set applicability from compliance or use policy's applicability as default
        Applicability: compliance.Applicability || policyApplicability || '',
        // Initialize new risk fields
        PotentialRiskScenarios: compliance.PotentialRiskScenarios || '',
        RiskType: compliance.RiskType || '',
        RiskCategory: compliance.RiskCategory || '',
        RiskBusinessImpact: compliance.RiskBusinessImpact || '',
        versionType: 'minor' // Set default version type
      };
      this.sourceSubPolicyId = this.selectedSubPolicy.id; // Store the source subpolicy ID
      
      // Initialize the target with current framework but empty policy/subpolicy
      this.copyTarget = { 
        frameworkId: this.selectedFramework.id, // Lock to current framework
        policyId: '', 
        subPolicyId: '' 
      };
      
      // Pre-load policies for the current framework
        await this.copyTarget_frameworkId(this.copyTarget.frameworkId);
      
      this.copyError = '';
    },
    cancelCopy() {
      this.copyIdx = null;
      this.copyRow = {};
      this.sourceSubPolicyId = null; // Reset source subpolicy ID
      this.copyTarget = { frameworkId: '', policyId: '', subPolicyId: '' };
      this.copyPolicies = [];
      this.copySubPolicies = [];
      this.copyError = '';
    },
    async confirmCopy() {
      if (!this.canSaveCopy) {
        this.copyError = 'Please fill all required fields and select a destination.';
        return;
      }
      
      try {
        this.loading = true;
        this.copyError = '';
        await this.$nextTick();

        // Calculate version based on version type
        const currentVersion = parseFloat(this.subPolicyCompliances[this.copyIdx].ComplianceVersion) || 1.0;
        let newVersion;
        
        if (this.copyRow.versionType === 'major') {
          // For major version, increment the base number and set decimal to 0
          const baseVersion = Math.floor(currentVersion);
          newVersion = (baseVersion + 1).toFixed(1);
        } else {
          // For minor version, add 0.1 to the current version
          newVersion = (currentVersion + 0.1).toFixed(1);
        }

        const cloneData = {
          ...this.copyRow,
          Impact: String(this.copyRow.Impact),
          Probability: String(this.copyRow.Probability),
          target_subpolicy_id: this.copyTarget.subPolicyId,
          Status: 'Under Review',
          ActiveInactive: 'Inactive',
          PermanentTemporary: this.copyRow.PermanentTemporary || 'Permanent',
          ComplianceVersion: newVersion,
          reviewer_id: this.copyRow.reviewer_id, // Include reviewer_id
          Applicability: this.copyRow.Applicability // Include Applicability
        };

        // Use confirm popup for cloning
        this.confirmCloneCompliance({
          ComplianceItemDescription: this.copyRow.ComplianceItemDescription
        }, async () => {
        const response = await complianceService.cloneCompliance(
          this.subPolicyCompliances[this.copyIdx].ComplianceId,
          cloneData
        );

        if (response.data.success) {
          this.cancelCopy();
            // Show success popup instead of alert
            CompliancePopups.complianceCloned({
              ComplianceId: response.data.compliance_id,
              ComplianceVersion: '1.0'
            });
          // Refresh compliances
          await this.refreshCurrentData();
        } else {
          this.copyError = response.data.message || 'Failed to copy compliance';
            this.showErrorPopup(this.copyError);
        }
        });
      } catch (error) {
        console.error('Copy error:', error);
        this.copyError = 'Failed to copy compliance: ' + (error.response?.data?.message || error.message);
        this.showErrorPopup(this.copyError);
      } finally {
        this.loading = false;
      }
    },
    // Watchers for copy dropdowns
    async copyTarget_frameworkId(newValue) {
      if (newValue) {
        try {
          const response = await complianceService.getPolicies(newValue);
          if (response.data && response.data.data) {
            this.copyPolicies = response.data.data.map(p => ({ 
              id: p.PolicyId, 
              name: p.PolicyName,
              applicability: p.Applicability || '' // Store the Applicability field
            }));
          } else {
            console.error("Unexpected response format from getPolicies:", response);
            this.copyPolicies = [];
          }
          this.copyTarget.policyId = '';
          this.copyTarget.subPolicyId = '';
          this.copySubPolicies = [];
        } catch (error) {
          console.error("Error fetching policies for framework:", error);
          this.copyError = "Failed to load policies for the selected framework";
          this.copyPolicies = [];
        }
      }
    },
    async copyTarget_policyId(newValue) {
      if (newValue) {
        try {
          // Load subpolicies for the selected policy
          const response = await complianceService.getSubPolicies(newValue);
          if (response.data && response.data.data) {
            this.copySubPolicies = response.data.data.map(sp => ({ id: sp.SubPolicyId, name: sp.SubPolicyName }));
          } else {
            console.error("Unexpected response format from getSubPolicies:", response);
            this.copySubPolicies = [];
          }
          this.copyTarget.subPolicyId = '';
          
          // Find the selected policy to get its applicability
          const selectedPolicy = this.copyPolicies.find(p => p.id === newValue);
          if (selectedPolicy && selectedPolicy.applicability) {
            // Update the applicability in the copy form
            this.copyRow.Applicability = selectedPolicy.applicability;
          }
        } catch (error) {
          console.error("Error fetching subpolicies for policy:", error);
          this.copyError = "Failed to load subpolicies for the selected policy";
          this.copySubPolicies = [];
        }
      }
    },
    async refreshCurrentData() {
      try {
        this.loading = true;
        this.error = null;
        
        await this.loadFrameworks();
        await this.loadUsers(); // Also refresh users list
        
        if (this.selectedFramework && this.selectedFramework.id) {
          await this.loadPolicies(this.selectedFramework.id);
          
          if (this.selectedPolicy && this.selectedPolicy.id) {
            await this.loadSubPolicies(this.selectedPolicy.id);
            
            if (this.selectedSubPolicy && this.selectedSubPolicy.id) {
              await this.loadCompliances();
            }
          }
        }
      } catch (error) {
        this.error = 'Failed to refresh data';
        console.error('Error refreshing data:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadCompliances() {
      try {
        this.loading = true;
        this.subPolicyCompliances = [];
        if (this.selectedSubPolicy && this.selectedSubPolicy.id) {
          console.log('Loading compliances for subpolicy ID:', this.selectedSubPolicy.id);
          
          // Use the compliance service to get the data
          const response = await complianceService.getCompliancesBySubPolicy(this.selectedSubPolicy.id);
          console.log('Compliances API response:', response);
          
          // Process the response data based on its structure
          if (response.data && response.data.success && Array.isArray(response.data.data)) {
            // Handle nested array structure
            const flattenedCompliances = [];
            
            // Check if we have a nested array or a flat array
            if (response.data.data.length > 0 && Array.isArray(response.data.data[0])) {
              // It's a nested array structure - flatten it
              response.data.data.forEach(group => {
                if (Array.isArray(group) && group.length > 0) {
                  flattenedCompliances.push(group[0]); // Take the most recent version
                }
              });
              this.subPolicyCompliances = flattenedCompliances;
            } else {
              // It's already a flat array
              this.subPolicyCompliances = response.data.data;
            }
          } else if (response.data && Array.isArray(response.data)) {
            // Direct array in response
            this.subPolicyCompliances = response.data;
          } else if (response.data && typeof response.data === 'object') {
            // Try to extract data from response object
            if (response.data.data && Array.isArray(response.data.data)) {
              this.subPolicyCompliances = response.data.data;
            } else if (response.data.compliances && Array.isArray(response.data.compliances)) {
              this.subPolicyCompliances = response.data.compliances;
            } else {
              // Try to extract compliances from object values
              const extractedData = Object.values(response.data).filter(
                item => item && typeof item === 'object' && item.ComplianceId
              );
              
              if (extractedData.length > 0) {
                this.subPolicyCompliances = extractedData;
              } else {
                console.warn('Could not extract compliances from response:', response.data);
                this.subPolicyCompliances = [];
              }
            }
          } else {
            console.warn('Unexpected response format:', response);
            this.subPolicyCompliances = [];
          }
          
          console.log('Processed compliances:', this.subPolicyCompliances);
        }
      } catch (error) {
        this.error = 'Failed to load compliances';
        // Show error popup
        this.showErrorPopup('Failed to load compliances: ' + (error.response?.data?.message || error.message));
        console.error('Error loading compliances:', error);
      } finally {
        this.loading = false;
      }
    },
    // Format date
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        // Handle different date formats
        let date;
        if (typeof dateString === 'string') {
          // Try different date formats
          if (dateString.includes('T')) {
            // ISO format
            date = new Date(dateString);
          } else if (dateString.includes('-')) {
            // YYYY-MM-DD format
            const parts = dateString.split(' ')[0].split('-');
            date = new Date(parts[0], parts[1] - 1, parts[2]);
          } else if (dateString.includes('/')) {
            // MM/DD/YYYY format
            const parts = dateString.split(' ')[0].split('/');
            date = new Date(parts[2], parts[0] - 1, parts[1]);
          } else {
            date = new Date(dateString);
          }
        } else {
          date = new Date(dateString);
        }
        
        // Format the date
        return date.toLocaleString();
      } catch (e) {
        console.error('Error formatting date:', e);
        return dateString; // Return the original string if parsing fails
      }
    },
    // Add a new method to view compliance details in a popup
    viewComplianceDetails(compliance) {
      CompliancePopups.showComplianceInfo(compliance);
    },
    // Helper method to generate a default due date (7 days from now)
    getDefaultDueDate() {
      const date = new Date();
      date.setDate(date.getDate() + 7);
      return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    },
    navigateToEdit(compliance) {
      // Navigate to the edit page with the compliance ID
      this.$router.push(`/compliance/edit/${compliance.ComplianceId}`);
    },
    navigateToCopy(compliance) {
      // Navigate to the copy page with the compliance ID
      this.$router.push(`/compliance/copy/${compliance.ComplianceId}`);
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
</style> 