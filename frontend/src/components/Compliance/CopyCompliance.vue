<template>
  <div class="create-compliance-container">
    <!-- Header section -->
    <div class="compliance-header">
      <h2>Template Compliance Record</h2>
      <p>Create a new compliance item based on an existing one</p>
    </div>

    <!-- Message display -->
    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <div class="loading-text">Loading data...</div>
    </div>

    <!-- Target selection -->
    <div class="field-group selection-fields">
      <div class="field-group-title">Select Target Location</div>
      <div class="row-fields">
        <div class="compliance-field">
          <label for="framework">
            Framework
            <span class="required">*</span>
          </label>
          <select 
            id="framework" 
            v-model="targetFrameworkId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetFrameworkId }"
            :ref="'field_targetFrameworkId'"
            required 
            title="Select the target framework"
            disabled
          >
            <option value="" disabled>Select Framework</option>
            <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
          </select>
          <div v-if="validationErrors.targetFrameworkId" class="field-error-message">
            {{ validationErrors.targetFrameworkId }}
          </div>
        </div>
        
        <div class="compliance-field">
          <label for="policy">
            Policy
            <span class="required">*</span>
          </label>
          <select 
            id="policy" 
            v-model="targetPolicyId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetPolicyId }"
            :ref="'field_targetPolicyId'"
            required 
            :disabled="!targetFrameworkId"
          >
            <option value="" disabled>Select Policy</option>
            <option v-for="p in policies" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
          <div v-if="validationErrors.targetPolicyId" class="field-error-message">
            {{ validationErrors.targetPolicyId }}
          </div>
        </div>
        
        <div class="compliance-field">
          <label for="subpolicy">
            Sub Policy
            <span class="required">*</span>
          </label>
          <select 
            id="subpolicy" 
            v-model="targetSubPolicyId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetSubPolicyId }"
            :ref="'field_targetSubPolicyId'"
            required 
            :disabled="!targetPolicyId"
          >
            <option value="" disabled>Select Sub Policy</option>
            <option v-for="sp in subPolicies" :key="sp.id" :value="sp.id">{{ sp.name }}</option>
          </select>
          <div v-if="validationErrors.targetSubPolicyId" class="field-error-message">
            {{ validationErrors.targetSubPolicyId }}
          </div>
        </div>
      </div>
    </div>

    <!-- Copy form -->
    <div v-if="compliance" class="compliance-item-form">
      <!-- Basic compliance information -->
      <div class="field-group">
        <div class="field-group-title">Basic Information</div>
        
        <!-- Compliance Title and Type in one row -->
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Compliance Title
              <span class="required">*</span>
              <span class="field-requirements">(Minimum 5 characters)</span>
            </label>
            <input 
              v-model="compliance.ComplianceTitle" 
              class="compliance-input"
              :class="{ 'error': validationErrors.ComplianceTitle }"
              :ref="'field_ComplianceTitle'"
              placeholder="Enter compliance title"
              @input="validateFieldRealTime('ComplianceTitle')"
              @blur="validateField('ComplianceTitle')"
              required 
            />
            <div v-if="validationErrors.ComplianceTitle" class="field-error-message">
              {{ validationErrors.ComplianceTitle }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>Compliance Type</label>
            <input 
              v-model="compliance.ComplianceType" 
              class="compliance-input" 
              placeholder="Enter compliance type"
              title="Type of compliance (e.g. Regulatory, Internal, Security)"
            />
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Description
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 20 characters)</span>
          </label>
          <textarea 
            v-model="compliance.ComplianceItemDescription" 
            class="compliance-input"
            :class="{ 'error': validationErrors.ComplianceItemDescription }"
            :ref="'field_ComplianceItemDescription'"
            placeholder="Detailed description of the compliance requirement"
            @input="validateFieldRealTime('ComplianceItemDescription')"
            @blur="validateField('ComplianceItemDescription')"
            rows="3"
            required 
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.ComplianceItemDescription }">
            {{ compliance.ComplianceItemDescription?.length || 0 }}/20 min characters
          </div>
          <div v-if="validationErrors.ComplianceItemDescription" class="field-error-message">
            {{ validationErrors.ComplianceItemDescription }}
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Scope
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 15 characters)</span>
          </label>
          <textarea 
            v-model="compliance.Scope" 
            class="compliance-input"
            :class="{ 'error': validationErrors.Scope }"
            :ref="'field_Scope'"
            placeholder="Define the boundaries and extent of the compliance requirement"
            @input="validateFieldRealTime('Scope')"
            @blur="validateField('Scope')"
            rows="3"
            required
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.Scope }">
            {{ compliance.Scope?.length || 0 }}/15 min characters
          </div>
          <div v-if="validationErrors.Scope" class="field-error-message">
            {{ validationErrors.Scope }}
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Objective
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 15 characters)</span>
          </label>
          <textarea 
            v-model="compliance.Objective" 
            class="compliance-input"
            :class="{ 'error': validationErrors.Objective }"
            :ref="'field_Objective'"
            placeholder="Define the goal or purpose of this compliance requirement"
            @input="validateFieldRealTime('Objective')"
            @blur="validateField('Objective')"
            rows="3"
            required
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.Objective }">
            {{ compliance.Objective?.length || 0 }}/15 min characters
          </div>
          <div v-if="validationErrors.Objective" class="field-error-message">
            {{ validationErrors.Objective }}
          </div>
        </div>
        
        <!-- Business Units, Identifier and IsRisk in one row -->
        <div class="row-fields">
          <div class="compliance-field">
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
          
          <div class="compliance-field">
            <label>Identifier</label>
            <input 
              v-model="compliance.Identifier" 
              class="compliance-input" 
              placeholder="Auto-generated if left empty"
              title="A new identifier will be generated"
              disabled
            />
            <small>A new identifier will be generated</small>
          </div>

          <div class="compliance-field checkbox-container">
            <label style="font-weight: 500; font-size: 1rem; display: flex; align-items: center; gap: 8px;" title="Check if this compliance item represents a risk">
              <input type="checkbox" v-model="compliance.IsRisk" style="margin-right: 8px; width: auto;" />
              Is Risk
            </label>
          </div>
        </div>
      </div>

      <!-- Risk related fields - grouped together -->
      <div class="field-group risk-fields" v-if="compliance.IsRisk">
        <div class="field-group-title">Risk Information</div>
        <div class="compliance-field full-width">
          <label>
            Possible Damage
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 20 characters)</span>
          </label>
          <textarea 
            v-model="compliance.PossibleDamage" 
            class="compliance-input"
            :class="{ 'error': validationErrors.PossibleDamage }"
            :ref="'field_PossibleDamage'"
            placeholder="Describe potential damage that could occur if this risk materializes"
            @input="validateFieldRealTime('PossibleDamage')"
            @blur="validateField('PossibleDamage')"
            rows="3"
            required
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.PossibleDamage }">
            {{ compliance.PossibleDamage?.length || 0 }}/20 min characters
          </div>
          <div v-if="validationErrors.PossibleDamage" class="field-error-message">
            {{ validationErrors.PossibleDamage }}
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Mitigation
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 20 characters)</span>
          </label>
          <textarea 
            v-model="compliance.mitigation" 
            class="compliance-input"
            :class="{ 'error': validationErrors.mitigation }"
            :ref="'field_mitigation'"
            placeholder="Describe the mitigation measures for this risk"
            @input="validateFieldRealTime('mitigation')"
            @blur="validateField('mitigation')"
            rows="3"
            required
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.mitigation }">
            {{ compliance.mitigation?.length || 0 }}/20 min characters
          </div>
          <div v-if="validationErrors.mitigation" class="field-error-message">
            {{ validationErrors.mitigation }}
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Potential Risk Scenarios
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 20 characters)</span>
          </label>
          <textarea 
            v-model="compliance.PotentialRiskScenarios" 
            class="compliance-input"
            :class="{ 'error': validationErrors.PotentialRiskScenarios }"
            :ref="'field_PotentialRiskScenarios'"
            placeholder="Describe scenarios where this risk could materialize"
            @input="validateFieldRealTime('PotentialRiskScenarios')"
            @blur="validateField('PotentialRiskScenarios')"
            rows="3"
            required
          ></textarea>
          <div class="char-count" :class="{ 'error': validationErrors.PotentialRiskScenarios }">
            {{ compliance.PotentialRiskScenarios?.length || 0 }}/20 min characters
          </div>
          <div v-if="validationErrors.PotentialRiskScenarios" class="field-error-message">
            {{ validationErrors.PotentialRiskScenarios }}
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
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
          
          <div class="compliance-field">
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
          
          <div class="compliance-field">
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
        </div>
      </div>
      
      <!-- Compliance classification fields - grouped together -->
      <div class="field-group classification-fields">
        <div class="field-group-title">Classification</div>
        <div class="row-fields">
          <div class="compliance-field">
            <label>Criticality</label>
            <select 
              v-model="compliance.Criticality" 
              class="compliance-select" 
              required
              title="How critical this compliance item is to the organization"
            >
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          
          <div class="compliance-field">
            <label>Mandatory/Optional</label>
            <select 
              v-model="compliance.MandatoryOptional" 
              class="compliance-select" 
              required
              title="Whether this compliance item is mandatory or optional"
            >
              <option value="Mandatory">Mandatory</option>
              <option value="Optional">Optional</option>
            </select>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>Manual/Automatic</label>
            <select 
              v-model="compliance.ManualAutomatic" 
              class="compliance-select" 
              required
              title="Whether this compliance is checked manually or automatically"
            >
              <option value="Manual">Manual</option>
              <option value="Automatic">Automatic</option>
            </select>
          </div>
          
          <div class="compliance-field">
            <label>Applicability</label>
            <input 
              v-model="compliance.Applicability" 
              class="compliance-input" 
              placeholder="Applicability from policy"
              title="Describes where this compliance item applies"
            />
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>Severity Rating (1-10)</label>
            <input 
              type="number" 
              v-model.number="compliance.Impact" 
              @input="validateImpact"
              class="compliance-input" 
              step="0.1" 
              min="1" 
              max="10"
              title="Rate the Severity Rating from 1 (lowest) to 10 (highest)"
            />
            <span v-if="impactError" class="validation-error">
              Severity Rating must be between 1 and 10
            </span>
          </div>
          
          <div class="compliance-field">
            <label>Probability (1-10)</label>
            <input 
              type="number" 
              v-model.number="compliance.Probability" 
              @input="validateProbability"
              class="compliance-input" 
              step="0.1" 
              min="1" 
              max="10"
              title="Rate the probability from 1 (lowest) to 10 (highest)"
            />
            <span v-if="probabilityError" class="validation-error">
              Probability must be between 1 and 10
            </span>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>Maturity Level</label>
            <select 
              v-model="compliance.MaturityLevel" 
              class="compliance-select"
              title="Current maturity level of this compliance item"
            >
              <option>Initial</option>
              <option>Developing</option>
              <option>Defined</option>
              <option>Managed</option>
              <option>Optimizing</option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- Approval section -->
      <div class="field-group approval-fields">
        <div class="field-group-title">Approval Information</div>
        <!-- Approver and Approval Due Date in the same row -->
        <div class="row-fields">
          <!-- Assign Reviewer -->
          <div class="compliance-field">
            <label>Assign Reviewer</label>
            <select 
              v-model="compliance.reviewer_id" 
              class="compliance-select" 
              required
              title="Person responsible for reviewing this compliance item"
            >
              <option value="" disabled>Select Reviewer</option>
              <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                {{ user.UserName }} {{ user.email ? `(${user.email})` : '' }}
              </option>
            </select>
            <span v-if="!users.length" class="validation-error">No reviewers available</span>
          </div>
          <!-- Approval Due Date -->

        </div>
      </div>
    </div>
    
    <div class="compliance-submit-container">
      <button 
        class="compliance-submit-btn" 
        @click="validateAndSubmit"
        :disabled="loading || !canSaveCopy"
      >
        <span v-if="loading">Saving...</span>
        <span v-else>Save Copy</span>
      </button>
      <button 
        class="compliance-cancel-btn" 
        @click="cancelCopy"
        :disabled="loading"
      >
        Cancel
      </button>
    </div>
  </div>
</template>

<script>
import { complianceService } from '@/services/api';
import { CompliancePopups } from './utils/popupUtils';

export default {
  name: 'CopyCompliance',
  data() {
    return {
      compliance: null,
      users: [],
      frameworks: [],
      policies: [],
      subPolicies: [],
      targetFrameworkId: '',
      targetPolicyId: '',
      targetSubPolicyId: '',
      loading: false,
      error: null,
      successMessage: null,
      impactError: false,
      probabilityError: false,
      originalComplianceId: null,
      sourceSubPolicyId: null,
      categoryOptions: {
        BusinessUnitsCovered: [],
        RiskType: [],
        RiskCategory: [],
        RiskBusinessImpact: []
      },
      filteredOptions: {
        BusinessUnitsCovered: [],
        RiskType: [],
        RiskCategory: [],
        RiskBusinessImpact: []
      },
      businessUnitSearch: '',
      riskTypeSearch: '',
      riskCategorySearch: '',
      riskBusinessImpactSearch: '',
      activeDropdown: null,
      validationErrors: {},
      validationRules: {
        ComplianceTitle: [
          { required: true, message: 'Title is required' },
          { minLength: 5, message: 'Title must be at least 5 characters long' }
        ],
        ComplianceItemDescription: [
          { required: true, message: 'Description is required' },
          { minLength: 20, message: 'Description must be at least 20 characters long' }
        ],
        targetFrameworkId: [
          { required: true, message: 'Framework is required' }
        ],
        targetPolicyId: [
          { required: true, message: 'Policy is required' }
        ],
        targetSubPolicyId: [
          { required: true, message: 'Sub Policy is required' }
        ],
        Scope: [
          { required: true, message: 'Scope is required' },
          { minLength: 15, message: 'Scope must be at least 15 characters long' }
        ],
        Objective: [
          { required: true, message: 'Objective is required' },
          { minLength: 15, message: 'Objective must be at least 15 characters long' }
        ],
        PossibleDamage: [
          { required: true, message: 'Possible Damage is required for risks' },
          { minLength: 20, message: 'Possible Damage must be at least 20 characters long' }
        ],
        PotentialRiskScenarios: [
          { required: true, message: 'Risk Scenarios are required for risks' },
          { minLength: 20, message: 'Risk Scenarios must be at least 20 characters long' }
        ],
        ComplianceType: [
          { required: true, message: 'Compliance Type is required' }
        ],
        BusinessUnitsCovered: [
          { required: true, message: 'Business Units are required' }
        ],
        RiskType: [
          { required: true, message: 'Risk Type is required for risks' }
        ],
        RiskCategory: [
          { required: true, message: 'Risk Category is required for risks' }
        ],
        RiskBusinessImpact: [
          { required: true, message: 'Risk Business Impact is required for risks' }
        ],
        Criticality: [
          { required: true, message: 'Criticality is required' }
        ],
        MandatoryOptional: [
          { required: true, message: 'Mandatory/Optional selection is required' }
        ],
        ManualAutomatic: [
          { required: true, message: 'Manual/Automatic selection is required' }
        ],
        MaturityLevel: [
          { required: true, message: 'Maturity Level is required' }
        ],
        mitigation: [
          { required: true, message: 'Mitigation is required for risks' },
          { minLength: 20, message: 'Mitigation must be at least 20 characters long' }
        ],
        Impact: [
          { required: true, message: 'Impact is required' },
          { min: 0, max: 10, message: 'Impact must be between 0 and 10' }
        ],
        Probability: [
          { required: true, message: 'Probability is required' },
          { min: 0, max: 10, message: 'Probability must be between 0 and 10' }
        ],
        reviewer_id: [
          { required: true, message: 'Reviewer is required' }
        ]
      },
      fieldStates: {}
    }
  },
  computed: {
    canSaveCopy() {
      // Validate all required fields are filled and subpolicy is different from source
      return this.compliance && 
        this.compliance.ComplianceItemDescription &&
        this.targetFrameworkId &&
        this.targetPolicyId &&
        this.targetSubPolicyId &&
        this.targetSubPolicyId !== this.sourceSubPolicyId && // Must be different subpolicy
        this.compliance.Criticality &&
        this.compliance.MandatoryOptional &&
        this.compliance.ManualAutomatic &&
        this.compliance.Impact && 
        this.compliance.Probability && 
        this.compliance.MaturityLevel &&
        this.compliance.reviewer_id;
    }
  },
  async created() {
    // Get the compliance ID from the route params
    const complianceId = this.$route.params.id;
    if (!complianceId) {
      this.error = 'No compliance ID provided';
      return;
    }
    
    this.originalComplianceId = complianceId;
    await this.loadUsers();
    await this.loadFrameworks();
    await this.loadComplianceData(complianceId);
    await this.loadCategoryOptions();
    
    // Add click event listener to close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // Remove event listener when component is unmounted
    document.removeEventListener('click', this.handleClickOutside);
  },
  watch: {
    targetFrameworkId(newValue) {
      if (newValue) {
        this.loadPolicies(newValue);
        this.targetPolicyId = '';
        this.targetSubPolicyId = '';
        this.policies = [];
        this.subPolicies = [];
      }
    },
    targetPolicyId(newValue) {
      if (newValue) {
        this.loadSubPolicies(newValue);
        this.targetSubPolicyId = '';
        this.subPolicies = [];
        
        // Update applicability from the selected policy
        const selectedPolicy = this.policies.find(p => p.id === newValue);
        if (selectedPolicy && selectedPolicy.applicability && this.compliance) {
          this.compliance.Applicability = selectedPolicy.applicability;
        }
      }
    }
  },
  methods: {
    async loadComplianceData(complianceId) {
      try {
        this.loading = true;
        const response = await complianceService.getComplianceById(complianceId);
        
        if (response.data && response.data.success) {
          this.compliance = response.data.data;
          this.sourceSubPolicyId = this.compliance.SubPolicy;

          // Get the framework ID from the API response and set it as target
          if (response.data.data.FrameworkId) {
            this.targetFrameworkId = response.data.data.FrameworkId;
            await this.loadPolicies(response.data.data.FrameworkId);
          }
          
          // Set default reviewer if not present
          if (!this.compliance.reviewer_id && this.users.length > 0) {
            this.compliance.reviewer_id = this.users[0].UserId;
          }
          
          // Clear identifier since a new one will be generated
          this.compliance.Identifier = '';
        } else {
          this.error = 'Failed to load compliance data';
        }
      } catch (error) {
        console.error('Error loading compliance data:', error);
        this.error = 'Failed to load compliance data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async loadUsers() {
      try {
        this.loading = true;
        const response = await complianceService.getUsers();
        
        if (response.data.success && Array.isArray(response.data.users)) {
          this.users = response.data.users;
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
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getFrameworks();
        
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
      } catch (error) {
        this.error = 'Failed to load frameworks';
        console.error(error);
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
        this.subPolicies = response.data.data
          .map(sp => ({
            id: sp.SubPolicyId,
            name: sp.SubPolicyName
          }))
          // Filter out the source subpolicy to prevent copying to same subpolicy
          .filter(sp => sp.id !== this.sourceSubPolicyId);
      } catch (error) {
        this.error = 'Failed to load sub-policies';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    validateImpact(event) {
      const value = parseFloat(event.target.value);
      this.impactError = value < 1 || value > 10;
    },
    validateProbability(event) {
      const value = parseFloat(event.target.value);
      this.probabilityError = value < 1 || value > 10;
    },
    getDefaultDueDate() {
      const date = new Date();
      date.setDate(date.getDate() + 7);
      return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    },
    async submitCopy() {
      if (!this.canSaveCopy) {
        this.error = 'Please fill all required fields and select a destination.';
        return;
      }
      
      try {
        this.loading = true;
        this.error = null;
        this.successMessage = null;
        
        const cloneData = {
          ...this.compliance,
          Impact: String(this.compliance.Impact),
          Probability: String(this.compliance.Probability),
          target_subpolicy_id: this.targetSubPolicyId,
          Status: 'Under Review',
          ActiveInactive: 'Inactive',
          PermanentTemporary: this.compliance.PermanentTemporary || 'Permanent',
          ComplianceVersion: '1.0',

          reviewer_id: this.compliance.reviewer_id,
          Applicability: this.compliance.Applicability
        };

        const response = await complianceService.cloneCompliance(
          this.originalComplianceId,
          cloneData
        );

        if (response.data.success) {
          // Show success popup with the correct data structure
          CompliancePopups.complianceCloned({
            ComplianceId: response.data.compliance_id
          });
          this.successMessage = 'Compliance copied successfully!';
          
          // Navigate back to the tailoring page after a short delay
          setTimeout(() => {
            this.$router.push('/compliance/tailoring');
          }, 1500);
        } else {
          this.error = response.data.message || 'Failed to copy compliance';
        }
      } catch (error) {
        console.error('Copy error:', error);
        this.error = 'Failed to copy compliance: ' + (error.response?.data?.message || error.message);
      } finally {
        this.loading = false;
      }
    },
    cancelCopy() {
      // Navigate back to the tailoring page
      this.$router.push('/compliance/tailoring');
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
    
    // Show dropdown for a specific field
    showDropdown(field) {
      // Close any open dropdown
      this.activeDropdown = field;
      
      // Set initial filtered options based on current search term
      this.filterOptions(field);
      
      // Prevent event from bubbling up
      event.stopPropagation();
    },
    
    // Handle clicking outside of dropdowns
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
    
    // Filter dropdown options based on search term
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
    
    // Select an option from the dropdown
    selectOption(field, value) {
      // Update the compliance item with the selected value
      this.compliance[field] = value;
      
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
    
    // Add a new option to the category options
    async addNewOption(field, value) {
      try {
        const response = await complianceService.addCategoryBusinessUnit({
          source: field,
          value: value
        });
        
        if (response.data.success) {
          // Add the new option to the category options
          this.categoryOptions[field].push(response.data.data);
          
          // Select the new option
          this.selectOption(field, value);
          
          CompliancePopups.success(`Added new ${field} option: ${value}`);
        }
      } catch (error) {
        console.error(`Failed to add new ${field} option:`, error);
        CompliancePopups.error(`Failed to add new option: ${error.message || error}`);
      }
    },
    scrollToError() {
      const errorFields = Object.keys(this.validationErrors);
      if (errorFields.length > 0) {
        const firstErrorField = errorFields[0];
        const errorElement = this.$refs[`field_${firstErrorField}`];
        
        if (errorElement) {
          errorElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
          if (errorElement.focus) {
            errorElement.focus();
          }
        }
      }
    },
    validateFieldRealTime(fieldName) {
      // Skip validation for risk-related fields if IsRisk is false
      if (!this.compliance.IsRisk && 
          ['PossibleDamage', 'mitigation', 'PotentialRiskScenarios', 'RiskType', 
           'RiskCategory', 'RiskBusinessImpact'].includes(fieldName)) {
        this.validationErrors[fieldName] = '';
        this.fieldStates[fieldName] = { valid: true, warning: false, dirty: true };
        return true;
      }

      const value = this.compliance[fieldName];
      const rules = this.validationRules[fieldName];
      
      if (!rules) return true;

      // Initialize field state if not exists
      if (!this.fieldStates[fieldName]) {
        this.fieldStates[fieldName] = {
          dirty: false,
          valid: false,
          warning: false
        };
      }
      
      this.fieldStates[fieldName].dirty = true;
      
      let isValid = true;
      let showWarning = false;
      
      for (const rule of rules) {
        if (rule.required && (!value || value.toString().trim() === '')) {
          isValid = false;
          this.validationErrors[fieldName] = rule.message;
          break;
        }
        
        if (rule.minLength && value) {
          if (value.length < rule.minLength) {
            isValid = false;
            if (value.length > 0) {
              showWarning = true;
              this.validationErrors[fieldName] = `Need ${rule.minLength - value.length} more characters`;
            }
          }
        }
        
        // Numeric validation for Impact and Probability
        if ((fieldName === 'Impact' || fieldName === 'Probability') && value !== '') {
          const numValue = parseFloat(value);
          if (isNaN(numValue)) {
            isValid = false;
            this.validationErrors[fieldName] = 'Must be a valid number';
          } else if (numValue < rule.min || numValue > rule.max) {
            isValid = false;
            this.validationErrors[fieldName] = `Must be between ${rule.min} and ${rule.max}`;
          }
        }
      }
      
      this.fieldStates[fieldName].valid = isValid;
      this.fieldStates[fieldName].warning = showWarning;
      
      if (isValid) {
        this.validationErrors[fieldName] = '';
      }
      
      return isValid;
    },
    validateField(fieldName) {
      const isValid = this.validateFieldRealTime(fieldName);
      if (!isValid) {
        this.$nextTick(() => {
          this.scrollToError();
        });
      }
      return isValid;
    },
    validateAndSubmit() {
      this.validationErrors = {};
      let isValid = true;

      // Validate all fields
      Object.keys(this.validationRules).forEach(field => {
        if (!this.validateField(field)) {
          isValid = false;
        }
      });

      if (!isValid) {
        this.$nextTick(() => {
          this.scrollToError();
        });
        return;
      }

      // If valid, proceed with submission
      this.submitCopy();
    }
  }
}
</script>

<style scoped>
@import './CreateCompliance.css';

.compliance-cancel-btn {
  width: auto;
  min-width: 120px;
  padding: 0.875rem 1.75rem;
  background-color: #f1f5f9;
  color: #64748b;
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 2rem 0.5rem;
}

.compliance-cancel-btn:hover {
  background-color: #e2e8f0;
  color: #475569;
}

.compliance-submit-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-top: 2rem;
}

.compliance-submit-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

.field-error-message {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #fee2e2;
  border-radius: 4px;
  font-weight: 500;
}

.compliance-input.error,
.compliance-select.error {
  border-color: #dc2626;
  background-color: #fff5f5;
}

.compliance-input.error:focus,
.compliance-select.error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
}

.required {
  color: #dc2626;
  margin-left: 0.25rem;
}

.field-requirements {
  color: #6b7280;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.char-count {
  position: absolute;
  right: 8px;
  bottom: 8px;
  font-size: 0.75rem;
  color: #6b7280;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
}

.char-count.error {
  color: #dc2626;
}

@keyframes highlightError {
  0% {
    background-color: rgba(220, 38, 38, 0.1);
  }
  100% {
    background-color: transparent;
  }
}

.compliance-field:target {
  animation: highlightError 2s ease-out;
}

.validation-feedback {
  margin-top: 0.25rem;
}
</style> 