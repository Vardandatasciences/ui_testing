<template>
  <div class="copy-compliance-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="header-text">
            <h1>Copy Compliance Record</h1>
            <p>Create a new compliance item based on the selected one. Target location is auto-populated from current context.</p>
          </div>
          <button @click="goBack" class="back-button">
            <i class="fas fa-arrow-left"></i>
            Back
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content with Scroll -->
    <div class="page-content">
      <div class="content-container">

    <!-- Message display -->
    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <div class="loading-text">Loading compliance data...</div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="message error-message">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
    </div>

    <!-- Target selection -->
    <div class="field-group selection-fields">
      <div class="field-group-title">Target Location</div>
      <div class="selection-info">
        <i class="fas fa-info-circle"></i>
        Framework is auto-selected from your current context. You can choose different Policy and Sub Policy as the target location.
      </div>
      <div class="row-fields">
        <div class="compliance-field">
          <label for="framework">
            Framework
            <span class="required">*</span>
            <span class="field-status auto-selected">Auto-selected</span>
          </label>
          <select 
            id="framework" 
            v-model="targetFrameworkId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetFrameworkId }"
            :ref="'field_targetFrameworkId'"
            required 
            title="Target framework (auto-selected)"
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
            <span class="field-status selectable">Selectable</span>
          </label>
          <select 
            id="policy" 
            v-model="targetPolicyId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetPolicyId }"
            :ref="'field_targetPolicyId'"
            required 
            title="Select target policy"
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
            <span class="field-status selectable">Selectable</span>
          </label>
          <select 
            id="subpolicy" 
            v-model="targetSubPolicyId" 
            class="compliance-select"
            :class="{ 'error': validationErrors.targetSubPolicyId }"
            :ref="'field_targetSubPolicyId'"
            required 
            title="Select target sub-policy"
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
      localSourceSubPolicyId: null,
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
      // Validate all required fields are filled
      const isValid = this.compliance && 
        this.compliance.ComplianceItemDescription &&
        this.targetFrameworkId &&
        this.targetPolicyId &&
        this.targetSubPolicyId &&
        this.compliance.Criticality &&
        this.compliance.MandatoryOptional &&
        this.compliance.ManualAutomatic &&
        this.compliance.Impact && 
        this.compliance.Probability && 
        this.compliance.MaturityLevel &&
        this.compliance.reviewer_id;
        
      // Only log every 10th check to avoid spam
      if (Math.random() < 0.1) {
        console.log('🔍 canSaveCopy check:', {
          isValid,
          targetFrameworkId: this.targetFrameworkId,
          targetPolicyId: this.targetPolicyId,
          targetSubPolicyId: this.targetSubPolicyId,
          hasCompliance: !!this.compliance,
          hasDescription: !!this.compliance?.ComplianceItemDescription,
          hasCriticality: !!this.compliance?.Criticality,
          hasReviewer: !!this.compliance?.reviewer_id
        });
      }
      
      return isValid;
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
    await this.loadComplianceData(complianceId);
    
    await this.loadUsers();
    await this.loadCategoryOptions();
    
    // Use passed context from route query or load frameworks
    await this.initializeFromContext();
    
    // Set default reviewer if not present
    if (this.compliance && !this.compliance.reviewer_id && this.users.length > 0) {
      this.compliance.reviewer_id = this.users[0].UserId;
    }
    
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
        console.log('Framework changed to:', newValue); // Debug log
        this.validationErrors.targetFrameworkId = ''; // Clear validation error
        this.loadPolicies(newValue);
        this.targetPolicyId = '';
        this.targetSubPolicyId = '';
        this.policies = [];
        this.subPolicies = [];
      }
    },
    targetPolicyId(newValue) {
      if (newValue) {
        console.log('Policy changed to:', newValue); // Debug log
        this.validationErrors.targetPolicyId = ''; // Clear validation error
        this.loadSubPolicies(newValue);
        this.targetSubPolicyId = '';
        this.subPolicies = [];
        
        // Update applicability from the selected policy
        const selectedPolicy = this.policies.find(p => p.id === newValue);
        if (selectedPolicy && selectedPolicy.applicability && this.compliance) {
          this.compliance.Applicability = selectedPolicy.applicability;
          console.log('Updated applicability:', this.compliance.Applicability); // Debug log
        }
      }
    },
    targetSubPolicyId(newValue) {
      if (newValue) {
        console.log('Sub-policy changed to:', newValue); // Debug log
        this.validationErrors.targetSubPolicyId = ''; // Clear validation error
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
          this.localSourceSubPolicyId = this.compliance.SubPolicy;

          console.log('Loaded compliance data:', this.compliance); // Debug log

          // Store framework and policy information for auto-population
          this.compliance.FrameworkId = response.data.data.FrameworkId;
          this.compliance.PolicyId = response.data.data.PolicyId;
          
          console.log('Framework ID:', this.compliance.FrameworkId, 'Policy ID:', this.compliance.PolicyId); // Debug log
          
          // Set default reviewer if not present
          if (!this.compliance.reviewer_id && this.users.length > 0) {
            this.compliance.reviewer_id = this.users[0].UserId;
          }
          
          // Clear identifier since a new one will be generated
          this.compliance.Identifier = '';

          // Format mitigation data if needed
          this.compliance.mitigation = this.formatMitigationData(this.compliance.mitigation);
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
    
    // Format mitigation data to ensure it's in the expected JSON format
    formatMitigationData(mitigation) {
      console.log('Formatting mitigation data:', mitigation);
      
      // If empty, return empty object
      if (!mitigation) return {};
      
      // If already an object, format it properly
      if (typeof mitigation === 'object' && mitigation !== null) {
        // Check if it's already in the numbered format
        if (Object.keys(mitigation).some(key => !isNaN(parseInt(key)))) {
          console.log('Mitigation is already in numbered format');
          return mitigation;
        }
        
        // Convert to numbered format
        const formattedMitigation = {};
        // Use Object.values instead since we only need the values
        Object.values(mitigation).forEach((value, index) => {
          formattedMitigation[(index + 1).toString()] = value;
        });
        
        console.log('Converted object mitigation to numbered format:', formattedMitigation);
        return formattedMitigation;
      }
      
      // If it's a string, try to parse as JSON first
      if (typeof mitigation === 'string') {
        try {
          if (mitigation.trim().startsWith('{')) {
            const parsedMitigation = JSON.parse(mitigation);
            console.log('Parsed mitigation JSON:', parsedMitigation);
            
            // If parsed successfully and it's an object, format it
            if (typeof parsedMitigation === 'object' && parsedMitigation !== null) {
              return this.formatMitigationData(parsedMitigation);
            }
          }
        } catch (e) {
          console.log('Failed to parse mitigation as JSON:', e);
        }
        
        // If parsing failed or it's not JSON, use as single step
        if (mitigation.trim()) {
          console.log('Using mitigation string as single step');
          return { "1": mitigation.trim() };
        }
      }
      
      // Default empty object
      return {};
    },
    async initializeFromContext() {
      try {
        const query = this.$route.query;
        console.log('=== INITIALIZING FROM CONTEXT ==='); // Debug log
        console.log('Route query:', query); // Debug log
        console.log('Current route params:', this.$route.params); // Debug log
        
        // Check if we have context from the parent page
        if (query.frameworkId && query.frameworkName) {
          console.log('✓ Using context from parent page'); // Debug log
          console.log('Framework context:', {
            id: query.frameworkId,
            name: query.frameworkName
          }); // Debug log
          
          // Set up frameworks array with the current framework
          this.frameworks = [{
            id: parseInt(query.frameworkId),
            name: query.frameworkName
          }];
          
          // Set target framework
          this.targetFrameworkId = parseInt(query.frameworkId);
          console.log('Set targetFrameworkId:', this.targetFrameworkId, typeof this.targetFrameworkId);
          
          // Load policies for this framework
          await this.loadPolicies(parseInt(query.frameworkId));
          
          // Set target policy if available
          if (query.policyId && query.policyName) {
            this.targetPolicyId = parseInt(query.policyId);
            console.log('Set targetPolicyId:', this.targetPolicyId, typeof this.targetPolicyId);
          }
          
          // Load sub-policies if we have a policy
          if (query.policyId) {
            await this.loadSubPolicies(parseInt(query.policyId));
            
            // Set target sub-policy if available
            if (query.subPolicyId && query.subPolicyName) {
              this.targetSubPolicyId = parseInt(query.subPolicyId);
              console.log('Set targetSubPolicyId:', this.targetSubPolicyId, typeof this.targetSubPolicyId);
            }
          }
          
          console.log('Context initialized:', {
            framework: this.targetFrameworkId,
            policy: this.targetPolicyId,
            subPolicy: this.targetSubPolicyId
          });
          
          // Force reactivity update
          this.$forceUpdate();
          
          // Clear any validation errors for target fields
          this.validationErrors.targetFrameworkId = '';
          this.validationErrors.targetPolicyId = '';
          this.validationErrors.targetSubPolicyId = '';
          
          console.log('Cleared validation errors for target fields');
          
        } else {
          // Fall back to loading all frameworks
          console.log('✗ No context provided, loading all frameworks'); // Debug log
          console.log('Missing context items:', {
            frameworkId: !!query.frameworkId,
            frameworkName: !!query.frameworkName,
            policyId: !!query.policyId,
            subPolicyId: !!query.subPolicyId
          }); // Debug log
          await this.loadFrameworks();
          await this.autoPopulateTargetFields();
        }
      } catch (error) {
        console.error('Error initializing from context:', error);
        this.error = 'Failed to initialize page context. Please try again.';
      }
    },
    
    async autoPopulateTargetFields() {
      if (!this.compliance) return;
      
      try {
        console.log('Auto-populating target fields...'); // Debug log
        
        // Auto-select framework from source compliance
        if (this.compliance.FrameworkId) {
          this.targetFrameworkId = this.compliance.FrameworkId;
          console.log('Set target framework ID:', this.targetFrameworkId); // Debug log
          
          await this.loadPolicies(this.compliance.FrameworkId);
          
          // Pre-populate policy but don't force it - user can change
          if (this.compliance.PolicyId) {
            this.targetPolicyId = this.compliance.PolicyId;
            console.log('Set target policy ID:', this.targetPolicyId); // Debug log
            
            await this.loadSubPolicies(this.compliance.PolicyId);
            
            // Pre-populate sub-policy but don't force it - user can change
            if (this.compliance.SubPolicy) {
              this.targetSubPolicyId = this.compliance.SubPolicy;
              console.log('Set target sub-policy ID:', this.targetSubPolicyId); // Debug log
            }
          }
        }
      } catch (error) {
        console.error('Error auto-populating target fields:', error);
        this.error = 'Failed to auto-populate target fields. Please select manually.';
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
        this.error = null; // Clear any previous errors
        
        const response = await complianceService.getComplianceFrameworks();
        
        console.log('Frameworks API URL: /api/compliance/frameworks/'); // Debug log
        console.log('Frameworks response:', response.data); // Debug log
        
        // Handle both response formats: direct array or success wrapper
        let frameworksData;
        if (response.data.success && response.data.frameworks) {
          frameworksData = response.data.frameworks;
        } else if (Array.isArray(response.data)) {
          frameworksData = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
          this.error = 'Failed to load frameworks - invalid response format';
          this.frameworks = [];
          return;
        }
        
        this.frameworks = frameworksData.map(fw => ({
          id: fw.id,
          name: fw.name
        }));
        
        console.log('Processed frameworks:', this.frameworks); // Debug log
        
        if (this.frameworks.length === 0) {
          console.warn('No frameworks found');
          this.error = 'No frameworks available';
        }
      } catch (error) {
        this.error = `Failed to load frameworks: ${error.response?.data?.message || error.message || 'Unknown error'}`;
        console.error('Framework loading error:', error);
        console.error('Error response:', error.response);
        this.frameworks = [];
      } finally {
        this.loading = false;
      }
    },
    async loadPolicies(frameworkId) {
      try {
        this.loading = true;
        this.error = null; // Clear any previous errors
        
        const response = await complianceService.getCompliancePolicies(frameworkId);
        
        console.log(`Policies API URL: /api/compliance/frameworks/${frameworkId}/policies/list/`); // Debug log
        console.log('Policies response for framework', frameworkId, ':', response.data); // Debug log
        
        if (response.data.success && response.data.policies) {
          this.policies = response.data.policies.map(p => ({
            id: p.id,
            name: p.name,
            applicability: p.scope || p.Applicability || '' // Store the Applicability field
          }));
          
          console.log('Processed policies:', this.policies); // Debug log
          
          if (this.policies.length === 0) {
            console.warn('No policies found for framework:', frameworkId);
          }
        } else {
          console.error('Error in response:', response.data);
          this.error = 'Failed to load policies for the selected framework';
          this.policies = [];
        }
      } catch (error) {
        this.error = `Failed to load policies: ${error.response?.data?.message || error.message || 'Unknown error'}`;
        console.error('Policy loading error:', error);
        console.error('Error response:', error.response);
        this.policies = [];
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies(policyId) {
      try {
        this.loading = true;
        this.error = null; // Clear any previous errors
        
        const response = await complianceService.getComplianceSubPolicies(policyId);
        
        console.log(`Sub-policies API URL: /api/compliance/policies/${policyId}/subpolicies/`); // Debug log
        console.log('Sub-policies response for policy', policyId, ':', response.data); // Debug log
        
        if (response.data.success && response.data.subpolicies) {
          this.subPolicies = response.data.subpolicies
            .map(sp => ({
              id: sp.id,
              name: sp.name
            }));
            
          console.log('Processed sub-policies:', this.subPolicies); // Debug log
          
          if (this.subPolicies.length === 0) {
            console.warn('No sub-policies found for policy:', policyId);
          }
        } else {
          console.error('Error in response:', response.data);
          this.error = 'Failed to load sub-policies for the selected policy';
          this.subPolicies = [];
        }
      } catch (error) {
        this.error = `Failed to load sub-policies: ${error.response?.data?.message || error.message || 'Unknown error'}`;
        console.error('Sub-policy loading error:', error);
        console.error('Error response:', error.response);
        this.subPolicies = [];
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
      date.setDate(date.getDate() + 7); // 7 days from now
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
        
        console.log('🚀 Preparing clone data...');
        console.log('Original compliance:', this.compliance);
        console.log('Target SubPolicy ID:', this.targetSubPolicyId);
        
        // Format mitigation data as JSON object using our helper function
        const formattedMitigation = this.formatMitigationData(this.compliance.mitigation);
        
        console.log('📋 Formatted mitigation:', formattedMitigation);
        
        const cloneData = {
          // Basic compliance fields
          ComplianceTitle: this.compliance.ComplianceTitle || '',
          ComplianceItemDescription: this.compliance.ComplianceItemDescription || '',
          ComplianceType: this.compliance.ComplianceType || '',
          Scope: this.compliance.Scope || '',
          Objective: this.compliance.Objective || '',
          BusinessUnitsCovered: this.compliance.BusinessUnitsCovered || '',
          
          // Risk fields
          IsRisk: Boolean(this.compliance.IsRisk),
          PossibleDamage: this.compliance.PossibleDamage || '',
          mitigation: formattedMitigation, // Using the formatted JSON object
          PotentialRiskScenarios: this.compliance.PotentialRiskScenarios || '',
          RiskType: this.compliance.RiskType || '',
          RiskCategory: this.compliance.RiskCategory || '',
          RiskBusinessImpact: this.compliance.RiskBusinessImpact || '',
          
          // Classification fields
          Criticality: this.compliance.Criticality || 'Medium',
          MandatoryOptional: this.compliance.MandatoryOptional || 'Mandatory',
          ManualAutomatic: this.compliance.ManualAutomatic || 'Manual',
          Impact: String(this.compliance.Impact || 5.0),
          Probability: String(this.compliance.Probability || 5.0),
          MaturityLevel: this.compliance.MaturityLevel || 'Initial',
          
          // Target location - CRITICAL: Make sure both field names are included
          SubPolicy: this.targetSubPolicyId,
          target_subpolicy_id: this.targetSubPolicyId,
          
          // Status fields
          Status: 'Under Review',
          ActiveInactive: 'Inactive',
          ComplianceVersion: '1.0',
          PermanentTemporary: this.compliance.PermanentTemporary || 'Permanent',
          
          // Reviewer
          reviewer_id: this.compliance.reviewer_id,
          reviewer: this.compliance.reviewer_id, // Support both field names
          
          // Other fields
          Applicability: this.compliance.Applicability || '',
          Identifier: '', // Will be auto-generated
          CreatedByName: (this.compliance.reviewer_id || this.compliance.reviewer).toString(),
          
          // Ensure all dates are properly formatted
          ApprovalDueDate: this.getDefaultDueDate(),
          
          // Add any missing fields that might be required by backend
          ComplianceId: null, // Will be auto-generated
          FrameworkId: null, // Not needed for clone
          PolicyId: null // Not needed for clone
        };

        console.log('📦 Clone data prepared:', cloneData);
        console.log('🔑 Key fields check:');
        console.log('- SubPolicy:', cloneData.SubPolicy);
        console.log('- target_subpolicy_id:', cloneData.target_subpolicy_id);
        console.log('- reviewer_id:', cloneData.reviewer_id);
        console.log('- ApprovalDueDate:', cloneData.ApprovalDueDate);

        const response = await complianceService.cloneCompliance(
          this.originalComplianceId,
          cloneData
        );

        console.log('📬 Clone response:', response.data);

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
        console.error('Error response:', error.response);
        this.error = 'Failed to copy compliance: ' + (error.response?.data?.message || error.message);
      } finally {
        this.loading = false;
      }
    },
    cancelCopy() {
      // Navigate back to tailoring page
      this.$router.push('/compliance/tailoring');
    },
    
    goBack() {
      // Navigate back to tailoring page with current context
      const query = this.$route.query;
      if (query.frameworkId && query.policyId && query.subPolicyId) {
        // Go back to tailoring page (it will handle context restoration)
        this.$router.push('/compliance/tailoring');
      } else {
        // Generic back navigation
        if (window.history.length > 1) {
          this.$router.go(-1);
        } else {
          this.$router.push('/compliance/tailoring');
        }
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
      const errorFields = Object.keys(this.validationErrors).filter(field => this.validationErrors[field]);
      console.log('📍 Scrolling to error for fields:', errorFields);
      
      if (errorFields.length > 0) {
        const firstErrorField = errorFields[0];
        console.log('🎯 First error field:', firstErrorField);
        
        // Handle target fields differently since they don't have refs with field_ prefix
        let errorElement;
        if (firstErrorField.startsWith('target')) {
          const fieldMap = {
            'targetFrameworkId': 'framework',
            'targetPolicyId': 'policy', 
            'targetSubPolicyId': 'subpolicy'
          };
          errorElement = document.getElementById(fieldMap[firstErrorField]);
        } else {
          errorElement = this.$refs[`field_${firstErrorField}`];
        }
        
        if (errorElement) {
          console.log('✅ Found error element, scrolling...');
          errorElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
          if (errorElement.focus) {
            errorElement.focus();
          }
        } else {
          console.log('❌ Error element not found for:', firstErrorField);
          // Fallback: scroll to target location section
          const targetSection = document.querySelector('.selection-fields');
          if (targetSection) {
            targetSection.scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            });
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
      console.log('🚀 Starting validation and submit');
      console.log('Current target values:', {
        framework: this.targetFrameworkId,
        policy: this.targetPolicyId,
        subPolicy: this.targetSubPolicyId
      });
      
      this.validationErrors = {};
      let isValid = true;

      // Validate target fields first - these don't use the standard validation rules
      if (!this.targetFrameworkId) {
        this.validationErrors.targetFrameworkId = 'Framework is required';
        isValid = false;
      }
      
      if (!this.targetPolicyId) {
        this.validationErrors.targetPolicyId = 'Policy is required';
        isValid = false;
      }
      
      if (!this.targetSubPolicyId) {
        this.validationErrors.targetSubPolicyId = 'Sub Policy is required';
        isValid = false;
      }

      // Validate other fields using the standard validation rules
      Object.keys(this.validationRules).forEach(field => {
        // Skip target fields as we've already validated them above
        if (!field.startsWith('target')) {
          if (!this.validateField(field)) {
            isValid = false;
          }
        }
      });

      console.log('📋 Validation result:', {
        isValid,
        validationErrors: this.validationErrors
      });

      if (!isValid) {
        console.log('❌ Validation failed, scrolling to error');
        this.$nextTick(() => {
          this.scrollToError();
        });
        return;
      }

      console.log('✅ Validation passed, submitting...');
      // If valid, proceed with submission
      this.submitCopy();
    }
  }
}
</script>

<style scoped>
/* Page Layout */
.copy-compliance-page {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  margin-left: 280px;
}

/* Header Styles */
.page-header {
  background-color: white;
  color: #1f2937;
  padding: 1.5rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #111827;
}

.header-text p {
  margin: 0;
  font-size: 1rem;
  color: #6b7280;
}

.back-button {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.back-button:hover {
  background-color: #e5e7eb;
  color: #111827;
  transform: translateY(-1px);
}

/* Main Content */
.page-content {
  flex: 1;
  padding: 2rem 0;
  overflow-y: auto;
  max-height: calc(100vh - 120px);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 1.1rem;
  margin-top: 1rem;
}

/* Messages */
.message {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  font-weight: 500;
}

.success-message {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.error-message {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.error-message i {
  margin-right: 0.5rem;
}

/* Field Groups */
.field-group {
  margin-bottom: 2rem;
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.field-group-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3b82f6;
}

.selection-fields {
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
}

.risk-fields {
  background-color: #fefce8;
  border: 1px solid #fde047;
}

.classification-fields {
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
}

.approval-fields {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
}

/* Form Fields */
.row-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.compliance-field {
  display: flex;
  flex-direction: column;
  position: relative;
}

.compliance-field label {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.compliance-input,
.compliance-select {
  padding: 0.875rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background-color: white;
}

.compliance-input:focus,
.compliance-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.compliance-input:disabled,
.compliance-select:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
  border-color: #d1d5db;
  opacity: 0.7;
}

.compliance-select:not(:disabled) {
  background-color: white;
  cursor: pointer;
}

.full-width {
  grid-column: 1 / -1;
}

/* Character Count */
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

/* Checkbox Container */
.checkbox-container {
  display: flex;
  align-items: center;
  padding-top: 1.75rem;
}

/* Selection Info */
.selection-info {
  background-color: #dbeafe;
  border: 1px solid #60a5fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #1e40af;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.selection-info i {
  color: #3b82f6;
  font-size: 1.25rem;
}

/* Searchable Dropdowns */
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: 4px;
}

.dropdown-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.dropdown-option:hover {
  background-color: #f8fafc;
}

.dropdown-option:last-child {
  border-bottom: none;
}

.dropdown-add-option {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.dropdown-add-btn {
  display: block;
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  border: 1px dashed #9ca3af;
  background: white;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-add-btn:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
  color: #3b82f6;
}

/* Submit Container */
.compliance-submit-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  width: 100%;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.compliance-submit-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.compliance-submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

.compliance-submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.compliance-cancel-btn {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #cbd5e1;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.compliance-cancel-btn:hover {
  background-color: #e2e8f0;
  color: #475569;
  transform: translateY(-1px);
}

/* Error Styles */
.compliance-input.error,
.compliance-select.error {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.compliance-input.error:focus,
.compliance-select.error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.field-error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background-color: #fef2f2;
  border-radius: 6px;
  font-weight: 500;
}

.required {
  color: #dc2626;
  margin-left: 0.25rem;
}

.field-requirements {
  color: #6b7280;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  font-weight: 400;
}

.field-status {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.field-status.auto-selected {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fbbf24;
}

.field-status.selectable {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #22c55e;
}

/* Responsive Design */
@media (max-width: 768px) {
  .copy-compliance-page {
    margin-left: 0;
  }
  
  .page-header {
    padding: 1.5rem 0;
  }
  
  .header-content {
    padding: 0 1rem;
  }
  
  .header-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-text h1 {
    font-size: 1.5rem;
  }
  
  .content-container {
    margin: 0 1rem;
    padding: 1.5rem;
  }
  
  .row-fields {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .compliance-submit-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .compliance-submit-btn,
  .compliance-cancel-btn {
    width: 100%;
  }
}

/* Smooth Scrolling */
.page-content {
  scroll-behavior: smooth;
}

/* Custom Scrollbar */
.page-content::-webkit-scrollbar {
  width: 8px;
}

.page-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.page-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.page-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.validation-error {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  font-weight: 500;
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
</style>