<template>
  <div class="create-compliance-container">
    <!-- Header section -->
    <div class="compliance-header">
      <h2>Create Compliance Record</h2>
      <p>Add new compliance items to track in your GRC system</p>
    </div>

    <!-- Popup Modal -->
    <PopupModal />

    <!-- Selection controls -->
    <div class="field-group selection-fields">
      <div class="field-group-title">Select Policy Framework</div>
      <div class="row-fields">
        <div class="compliance-field">
          <label for="framework">Framework</label>
          <select id="framework" v-model="selectedFramework" class="compliance-select" required title="Select the governance framework">
            <option value="" disabled>Select Framework</option>
            <option v-for="fw in frameworks" :key="fw.id" :value="fw">{{ fw.name }}</option>
          </select>
        </div>
        
        <div class="compliance-field">
          <label for="policy">Policy</label>
          <select id="policy" v-model="selectedPolicy" class="compliance-select" required title="Select the policy within the framework">
            <option value="" disabled>Select Policy</option>
            <option v-for="p in policies" :key="p.id" :value="p">{{ p.name }}</option>
          </select>
        </div>
        
        <div class="compliance-field">
          <label for="subpolicy">Sub Policy</label>
          <select id="subpolicy" v-model="selectedSubPolicy" class="compliance-select" required title="Select the sub-policy within the policy">
            <option value="" disabled>Select Sub Policy</option>
            <option v-for="sp in subPolicies" :key="sp.id" :value="sp">{{ sp.name }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Compliance items list with tabs -->
    <div class="compliance-list">
      <!-- Tabs navigation -->
      <div class="compliance-tabs">
        <div 
          v-for="(compliance, idx) in complianceList" 
          :key="idx" 
          class="compliance-tab" 
          :class="{ 'active-tab': activeTab === idx }"
          @click="activeTab = idx"
        >
          <span>Item #{{ idx + 1 }}</span>
          <button 
            v-if="complianceList.length > 1" 
            class="tab-remove-btn" 
            @click.stop="removeCompliance(idx)" 
            title="Remove this compliance item"
          >
            <span class="btn-icon">×</span>
          </button>
        </div>
        <button 
          class="add-tab-btn" 
          @click="addCompliance" 
          title="Add new compliance item"
        >
          <span class="btn-icon">+</span>
        </button>
      </div>

      <!-- Tab content - only show active tab -->
      <div 
        v-for="(compliance, idx) in complianceList" 
        :key="idx" 
        class="compliance-item-form"
        v-show="activeTab === idx"
      >
        <!-- Header for each compliance item -->
        <div class="item-header">
          <span class="item-number">Compliance Item #{{ idx + 1 }}</span>
        </div>

        <!-- Basic compliance information -->
        <div class="field-group">
          <div class="field-group-title">Basic Information</div>
          
          <!-- Identifier and IsRisk in one row -->
          <div class="row-fields">
            <div class="compliance-field">
              <label>Identifier</label>
              <input 
                v-model="compliance.Identifier" 
                class="compliance-input" 
                placeholder="Auto-generated if left empty"
                title="Unique identifier for this compliance item (auto-generated if left blank)"
              />
              <small>Leave empty for auto-generated identifier</small>
            </div>

            <div class="compliance-field checkbox-container">
              <label style="font-weight: 500; font-size: 1rem; display: flex; align-items: center; gap: 8px;" title="Check if this compliance item represents a risk">
                <input type="checkbox" v-model="compliance.IsRisk" @change="onFieldChange(idx, 'IsRisk', $event)" style="margin-right: 8px; width: auto;" />
                Is Risk
              </label>
            </div>
          </div>
          
          <!-- Compliance Title and Type in one row -->
          <div class="row-fields">
            <div class="compliance-field">
              <label>Compliance Title</label>
              <input 
                v-model="compliance.ComplianceTitle" 
                @input="onFieldChange(idx, 'ComplianceTitle', $event)"
                class="compliance-input" 
                placeholder="Enter compliance title"
                required 
                :maxlength="validationRules.maxLengths.ComplianceTitle"
                title="Enter the title of the compliance item"
              />
              <div v-if="compliance.validationErrors && compliance.validationErrors.ComplianceTitle" 
                   class="validation-error">
                {{ compliance.validationErrors.ComplianceTitle.join(', ') }}
              </div>
            </div>
            
            <div class="compliance-field">
              <label>Compliance Type</label>
              <input 
                v-model="compliance.ComplianceType" 
                @input="onFieldChange(idx, 'ComplianceType', $event)"
                class="compliance-input" 
                placeholder="Enter compliance type"
                required
                :maxlength="validationRules.maxLengths.ComplianceType"
                title="Type of compliance (e.g. Regulatory, Internal, Security)"
              />
              <div v-if="compliance.validationErrors && compliance.validationErrors.ComplianceType" 
                   class="validation-error">
                {{ compliance.validationErrors.ComplianceType.join(', ') }}
              </div>
            </div>
          </div>
          
          <div class="compliance-field full-width">
            <label>Compliance Description</label>
            <textarea
              v-model="compliance.ComplianceItemDescription" 
              @input="onFieldChange(idx, 'ComplianceItemDescription', $event)"
              class="compliance-input" 
              :placeholder="`Compliance Description ${idx+1}`"
              required 
              rows="3"
              :maxlength="validationRules.maxLengths.ComplianceItemDescription"
              title="Detailed description of the compliance requirement"
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.ComplianceItemDescription" 
                 class="validation-error">
              {{ compliance.validationErrors.ComplianceItemDescription.join(', ') }}
            </div>
          </div>
          
          <div class="compliance-field full-width">
            <label>Scope</label>
            <textarea 
              v-model="compliance.Scope" 
              @input="onFieldChange(idx, 'Scope', $event)"
              class="compliance-input" 
              placeholder="Enter scope information"
              rows="3"
              required
              :maxlength="validationRules.maxLengths.Scope"
              title="Define the boundaries and extent of the compliance requirement"
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.Scope" 
                 class="validation-error">
              {{ compliance.validationErrors.Scope.join(', ') }}
            </div>
          </div>
          
          <div class="compliance-field full-width">
            <label>Objective</label>
            <textarea 
              v-model="compliance.Objective" 
              @input="onFieldChange(idx, 'Objective', $event)"
              class="compliance-input" 
              placeholder="Enter objective information"
              rows="3"
              required
              :maxlength="validationRules.maxLengths.Objective"
              title="The goal or purpose of this compliance requirement"
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.Objective" 
                 class="validation-error">
              {{ compliance.validationErrors.Objective.join(', ') }}
            </div>
          </div>
          
          <!-- Business Units Covered -->
          <div class="row-fields">
            <div class="compliance-field full-width">
              <label>Business Units Covered</label>
              <div class="searchable-dropdown">
                <input 
                  v-model="businessUnitSearch[idx]" 
                  class="compliance-input" 
                  placeholder="Search or add business units"
                  title="Departments or business units affected by this compliance"
                  @focus="showDropdown(idx, 'BusinessUnitsCovered')"
                  @input="filterOptions(idx, 'BusinessUnitsCovered')"
                />
                <div v-show="activeDropdown.index === idx && activeDropdown.field === 'BusinessUnitsCovered'" class="dropdown-options">
                  <div v-if="filteredOptions.BusinessUnitsCovered.length === 0 && businessUnitSearch[idx]" class="dropdown-add-option">
                    <span>No matches found. Add new:</span>
                    <button @click="addNewOption(idx, 'BusinessUnitsCovered', businessUnitSearch[idx])" class="dropdown-add-btn">
                      + Add "{{ businessUnitSearch[idx] }}"
                    </button>
                  </div>
                  <div 
                    v-for="option in filteredOptions.BusinessUnitsCovered" 
                    :key="option.id" 
                    class="dropdown-option"
                    @click="selectOption(idx, 'BusinessUnitsCovered', option.value)"
                  >
                    {{ option.value }}
                  </div>
                </div>
              </div>
              <div v-if="compliance.validationErrors && compliance.validationErrors.BusinessUnitsCovered" 
                   class="validation-error">
                {{ compliance.validationErrors.BusinessUnitsCovered.join(', ') }}
              </div>
            </div>
          </div>
        </div>

        <!-- Risk related fields - grouped together -->
        <div class="field-group risk-fields">
          <div class="field-group-title">Risk Information</div>
          <div class="compliance-field full-width">
            <label>Possible Damage</label>
            <textarea
              v-model="compliance.PossibleDamage" 
              @input="onFieldChange(idx, 'PossibleDamage', $event)"
              class="compliance-input" 
              placeholder="Possible Damage"
              rows="3"
              required
              :maxlength="validationRules.maxLengths.PossibleDamage"
              title="Potential damage that could occur if this risk materializes" 
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.PossibleDamage" 
                 class="validation-error">
              {{ compliance.validationErrors.PossibleDamage.join(', ') }}
            </div>
          </div>
          
          <div class="compliance-field full-width">
            <label>Mitigation</label>
            <textarea
              v-model="compliance.mitigation" 
              @input="onFieldChange(idx, 'mitigation', $event)"
              class="compliance-input" 
              placeholder="Mitigation"
              rows="3"
              required
              :maxlength="validationRules.maxLengths.mitigation"
              title="Actions taken to reduce the risk or its impact" 
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.mitigation" 
                 class="validation-error">
              {{ compliance.validationErrors.mitigation.join(', ') }}
            </div>
          </div>
          
          <div class="compliance-field full-width">
            <label>Potential Risk Scenarios</label>
            <textarea 
              v-model="compliance.PotentialRiskScenarios" 
              @input="onFieldChange(idx, 'PotentialRiskScenarios', $event)"
              class="compliance-input" 
              placeholder="Describe potential risk scenarios"
              rows="3"
              required
              :maxlength="validationRules.maxLengths.PotentialRiskScenarios"
              title="Describe scenarios where this risk could materialize"
            ></textarea>
            <div v-if="compliance.validationErrors && compliance.validationErrors.PotentialRiskScenarios" 
                 class="validation-error">
              {{ compliance.validationErrors.PotentialRiskScenarios.join(', ') }}
            </div>
          </div>
          
          <div class="row-fields">
            <div class="compliance-field">
              <label>Risk Type</label>
              <div class="searchable-dropdown">
                <input 
                  v-model="riskTypeSearch[idx]" 
                  class="compliance-input" 
                  placeholder="Search or add risk type"
                  required
                  :maxlength="validationRules.maxLengths.RiskType"
                  title="Type of risk (e.g. Operational, Financial, Strategic, Compliance, Reputational)"
                  @focus="showDropdown(idx, 'RiskType')"
                  @input="filterOptions(idx, 'RiskType')"
                />
                <div v-show="activeDropdown.index === idx && activeDropdown.field === 'RiskType'" class="dropdown-options">
                  <div v-if="filteredOptions.RiskType.length === 0 && riskTypeSearch[idx]" class="dropdown-add-option">
                    <span>No matches found. Add new:</span>
                    <button @click="addNewOption(idx, 'RiskType', riskTypeSearch[idx])" class="dropdown-add-btn">
                      + Add "{{ riskTypeSearch[idx] }}"
                    </button>
                  </div>
                  <div 
                    v-for="option in filteredOptions.RiskType" 
                    :key="option.id" 
                    class="dropdown-option"
                    @click="selectOption(idx, 'RiskType', option.value)"
                  >
                    {{ option.value }}
                  </div>
                </div>
              </div>
              <div v-if="compliance.validationErrors && compliance.validationErrors.RiskType" 
                   class="validation-error">
                {{ compliance.validationErrors.RiskType.join(', ') }}
              </div>
            </div>
            
            <div class="compliance-field">
              <label>Risk Category</label>
              <div class="searchable-dropdown">
                <input 
                  v-model="riskCategorySearch[idx]" 
                  class="compliance-input" 
                  placeholder="Search or add risk category"
                  required
                  :maxlength="validationRules.maxLengths.RiskCategory"
                  title="Category of risk (e.g. People, Process, Technology, External)"
                  @focus="showDropdown(idx, 'RiskCategory')"
                  @input="filterOptions(idx, 'RiskCategory')"
                />
                <div v-show="activeDropdown.index === idx && activeDropdown.field === 'RiskCategory'" class="dropdown-options">
                  <div v-if="filteredOptions.RiskCategory.length === 0 && riskCategorySearch[idx]" class="dropdown-add-option">
                    <span>No matches found. Add new:</span>
                    <button @click="addNewOption(idx, 'RiskCategory', riskCategorySearch[idx])" class="dropdown-add-btn">
                      + Add "{{ riskCategorySearch[idx] }}"
                    </button>
                  </div>
                  <div 
                    v-for="option in filteredOptions.RiskCategory" 
                    :key="option.id" 
                    class="dropdown-option"
                    @click="selectOption(idx, 'RiskCategory', option.value)"
                  >
                    {{ option.value }}
                  </div>
                </div>
              </div>
              <div v-if="compliance.validationErrors && compliance.validationErrors.RiskCategory" 
                   class="validation-error">
                {{ compliance.validationErrors.RiskCategory.join(', ') }}
              </div>
            </div>
            
            <div class="compliance-field">
              <label>Risk Business Impact</label>
              <div class="searchable-dropdown">
                <input 
                  v-model="riskBusinessImpactSearch[idx]" 
                  class="compliance-input" 
                  placeholder="Search or add business impact"
                  required
                  :maxlength="validationRules.maxLengths.RiskBusinessImpact"
                  title="How this risk impacts business operations"
                  @focus="showDropdown(idx, 'RiskBusinessImpact')"
                  @input="filterOptions(idx, 'RiskBusinessImpact')"
                />
                <div v-show="activeDropdown.index === idx && activeDropdown.field === 'RiskBusinessImpact'" class="dropdown-options">
                  <div v-if="filteredOptions.RiskBusinessImpact.length === 0 && riskBusinessImpactSearch[idx]" class="dropdown-add-option">
                    <span>No matches found. Add new:</span>
                    <button @click="addNewOption(idx, 'RiskBusinessImpact', riskBusinessImpactSearch[idx])" class="dropdown-add-btn">
                      + Add "{{ riskBusinessImpactSearch[idx] }}"
                    </button>
                  </div>
                  <div 
                    v-for="option in filteredOptions.RiskBusinessImpact" 
                    :key="option.id" 
                    class="dropdown-option"
                    @click="selectOption(idx, 'RiskBusinessImpact', option.value)"
                  >
                    {{ option.value }}
                  </div>
                </div>
              </div>
              <div v-if="compliance.validationErrors && compliance.validationErrors.RiskBusinessImpact" 
                   class="validation-error">
                {{ compliance.validationErrors.RiskBusinessImpact.join(', ') }}
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
                @input="onFieldChange(idx, 'Impact', $event)"
                class="compliance-input" 
                step="0.1" 
                min="1" 
                max="10"
                required
                title="Rate the Severity Rating from 1 (lowest) to 10 (highest)"
              />
              <div v-if="compliance.validationErrors && compliance.validationErrors.Impact" 
                   class="validation-error">
                {{ compliance.validationErrors.Impact.join(', ') }}
              </div>
            </div>
            
            <div class="compliance-field">
              <label>Probability (1-10)</label>
              <input 
                type="number" 
                v-model.number="compliance.Probability" 
                @input="onFieldChange(idx, 'Probability', $event)"
                class="compliance-input" 
                step="0.1" 
                min="1" 
                max="10"
                required
                title="Rate the probability from 1 (lowest) to 10 (highest)"
              />
              <div v-if="compliance.validationErrors && compliance.validationErrors.Probability" 
                   class="validation-error">
                {{ compliance.validationErrors.Probability.join(', ') }}
              </div>
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
                v-model="compliance.reviewer" 
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

          </div>
        </div>
      </div>
    </div>
    
    <div class="compliance-submit-container">
      <button 
        class="compliance-submit-btn" 
        @click="submitCompliance"
        :disabled="loading"
      >
        <span v-if="loading">Saving...</span>
        <span v-else>Submit Compliance</span>
      </button>
    </div>
  </div>
</template>

<script>
import { complianceService } from '@/services/api';
import { PopupService, PopupModal } from '@/modules/popup';

export default {
  name: 'CreateCompliance',
  components: {
    PopupModal
  },
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: [],
      policies: [],
      subPolicies: [],
      users: [],
      // Dropdown options
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
      // Search terms for each dropdown
      businessUnitSearch: [],
      riskTypeSearch: [],
      riskCategorySearch: [],
      riskBusinessImpactSearch: [],
      // Active dropdown tracking
      activeDropdown: {
        index: null,
        field: null
      },
      complianceList: [
        {
          ComplianceTitle: '',
          ComplianceItemDescription: '',
          ComplianceType: '',
          Scope: '',
          Objective: '',
          BusinessUnitsCovered: '',
          Identifier: '',
          IsRisk: false,
          PossibleDamage: '',
          mitigation: '',
          PotentialRiskScenarios: '',
          RiskType: '',
          RiskCategory: '',
          RiskBusinessImpact: '',
          Criticality: 'Medium',
          MandatoryOptional: 'Mandatory',
          ManualAutomatic: 'Manual',
          Impact: 5.0,
          Probability: 5.0,
          Status: 'Under Review',
          reviewer: 2, // Default reviewer
          Applicability: '',
          // Validation errors for each field
          validationErrors: {}
        }
      ],
      loading: false,
      activeTab: 0,
      // Centralized validation patterns (allow-list approach)
      validationRules: {
        // Character set patterns
        textPattern: /^[a-zA-Z0-9\s.,!?\-_()[\]{}:;'"&%$#@+=\n\r\t]*$/,
        alphanumericPattern: /^[a-zA-Z0-9\s.\-_]*$/,
        identifierPattern: /^[a-zA-Z0-9\-_]*$/,
        
        // Field length limits
        maxLengths: {
          ComplianceTitle: 145,
          ComplianceItemDescription: 5000,
          ComplianceType: 100,
          Scope: 5000,
          Objective: 5000,
          BusinessUnitsCovered: 225,
          Identifier: 45,
          PossibleDamage: 5000,
          mitigation: 5000,
          PotentialRiskScenarios: 5000,
          RiskType: 45,
          RiskCategory: 45,
          RiskBusinessImpact: 45,
          Applicability: 45
        },
        
        // Field minimum length requirements
        minLengths: {
          ComplianceTitle: 3,
          ComplianceItemDescription: 10,
          ComplianceType: 3,
          Scope: 10,
          Objective: 10,
          BusinessUnitsCovered: 3,
          mitigation: 10,
          PossibleDamage: 10,
          PotentialRiskScenarios: 10,
          RiskType: 3,
          RiskCategory: 3,
          RiskBusinessImpact: 3
        },
        
        // Allowed choice values
        allowedChoices: {
          Criticality: ['High', 'Medium', 'Low'],
          MandatoryOptional: ['Mandatory', 'Optional'],
          ManualAutomatic: ['Manual', 'Automatic']
        },
        
        // Numeric field ranges
        numericRanges: {
          Impact: { min: 1, max: 10 },
          Probability: { min: 1, max: 10 }
        }
      }
    }
  },
  computed: {
    minDate() {
      // Get today's date in YYYY-MM-DD format for setting minimum date
      const today = new Date();
      return today.toISOString().split('T')[0];
    }
  },
  async created() {
    await this.loadFrameworks();
    await this.loadUsers();
    await this.loadCategoryOptions();
    
    // Initialize search arrays with empty strings for the first compliance item
    this.businessUnitSearch = [''];
    this.riskTypeSearch = [''];
    this.riskCategorySearch = [''];
    this.riskBusinessImpactSearch = [''];
    
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
      }
    },
    selectedPolicy(newValue) {
      if (newValue && newValue.id) {
        this.loadSubPolicies(newValue.id);
        this.selectedSubPolicy = '';
        this.subPolicies = [];
        
        // Set the applicability for all compliance items from the selected policy
        if (newValue.applicability) {
          this.complianceList.forEach(compliance => {
            compliance.Applicability = newValue.applicability;
          });
        }
      }
    }
  },
  methods: {
    // Centralized validation methods using allow-list approach
    sanitizeString(value) {
      if (typeof value !== 'string') return String(value || '');
      // Remove control characters except newline, tab, carriage return
      // eslint-disable-next-line no-control-regex
      return value.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
    },
    
    sanitizeStringForSubmission(value) {
      if (typeof value !== 'string') return String(value || '');
      // Remove control characters and trim for final submission
      // eslint-disable-next-line no-control-regex
      return value.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '').trim();
    },
    
    validateRequiredString(value, fieldName, maxLength = null, minLength = null, pattern = null) {
      const sanitized = this.sanitizeString(value);
      const trimmedValue = sanitized.trim();
      const errors = [];
      
      if (!trimmedValue || trimmedValue.length === 0) {
        errors.push(`${fieldName} is required and cannot be empty`);
      }
      
      if (minLength && trimmedValue.length > 0 && trimmedValue.length < minLength) {
        errors.push(`${fieldName} must be at least ${minLength} characters long`);
      }
      
      if (maxLength && sanitized.length > maxLength) {
        errors.push(`${fieldName} must not exceed ${maxLength} characters`);
      }
      
      if (pattern && sanitized && !pattern.test(sanitized)) {
        errors.push(`${fieldName} contains invalid characters`);
      }
      
      return { value: sanitized, errors };
    },
    
    validateOptionalString(value, fieldName, maxLength = null, pattern = null) {
      const sanitized = this.sanitizeString(value);
      const errors = [];
      
      if (maxLength && sanitized.length > maxLength) {
        errors.push(`${fieldName} must not exceed ${maxLength} characters`);
      }
      
      if (pattern && sanitized && !pattern.test(sanitized)) {
        errors.push(`${fieldName} contains invalid characters`);
      }
      
      return { value: sanitized, errors };
    },
    
    validateChoiceField(value, fieldName, allowedChoices) {
      const errors = [];
      
      if (!value || value === '') {
        errors.push(`${fieldName} is required`);
      } else if (!allowedChoices.includes(value)) {
        errors.push(`${fieldName} must be one of: ${allowedChoices.join(', ')}`);
      }
      
      return { value, errors };
    },
    
    validateNumericField(value, fieldName, min = null, max = null) {
      const errors = [];
      const numValue = parseFloat(value);
      
      if (isNaN(numValue)) {
        errors.push(`${fieldName} must be a valid number`);
      } else {
        if (min !== null && numValue < min) {
          errors.push(`${fieldName} must be at least ${min}`);
        }
        if (max !== null && numValue > max) {
          errors.push(`${fieldName} must not exceed ${max}`);
        }
      }
      
      return { value: numValue, errors };
    },
    
    validateDateField(value, fieldName) {
      const errors = [];
      
      if (!value || value === '') {
        errors.push(`${fieldName} is required`);
      } else {
        const datePattern = /^\d{4}-\d{2}-\d{2}$/;
        if (!datePattern.test(value)) {
          errors.push(`${fieldName} must be in YYYY-MM-DD format`);
        } else {
          const date = new Date(value);
          if (isNaN(date.getTime())) {
            errors.push(`${fieldName} must be a valid date`);
          } else {
            // Check if date is in the future (for approval due dates)
            const today = new Date();
            today.setHours(0, 0, 0, 0); // Reset time to compare only dates
            if (date < today) {
              errors.push(`${fieldName} must be a future date`);
            }
          }
        }
      }
      
      return { value, errors };
    },
    
    validateComplianceField(compliance, fieldName, value) {
      const rules = this.validationRules;
      let result = { value, errors: [] };
      
      switch (fieldName) {
        case 'ComplianceTitle':
          result = this.validateRequiredString(
            value, 'Compliance Title', 
            rules.maxLengths.ComplianceTitle,
            rules.minLengths.ComplianceTitle,
            rules.textPattern
          );
          break;
          
        case 'ComplianceItemDescription':
          result = this.validateRequiredString(
            value, 'Compliance Description', 
            rules.maxLengths.ComplianceItemDescription,
            rules.minLengths.ComplianceItemDescription,
            rules.textPattern
          );
          break;
          
        case 'ComplianceType':
          result = this.validateRequiredString(
            value, 'Compliance Type', 
            rules.maxLengths.ComplianceType,
            rules.minLengths.ComplianceType,
            rules.textPattern
          );
          break;
          
        case 'Scope':
          result = this.validateRequiredString(
            value, 'Scope', 
            rules.maxLengths.Scope,
            rules.minLengths.Scope,
            rules.textPattern
          );
          break;
          
        case 'Objective':
          result = this.validateRequiredString(
            value, 'Objective', 
            rules.maxLengths.Objective,
            rules.minLengths.Objective,
            rules.textPattern
          );
          break;
          
        case 'BusinessUnitsCovered':
          result = this.validateRequiredString(
            value, 'Business Units Covered', 
            rules.maxLengths.BusinessUnitsCovered,
            rules.minLengths.BusinessUnitsCovered,
            rules.textPattern
          );
          break;
          
        case 'Identifier':
          if (value && value.trim()) {
            result = this.validateOptionalString(
              value, 'Identifier', 
              rules.maxLengths.Identifier, 
              rules.identifierPattern
            );
          }
          break;
          
        case 'PossibleDamage':
          result = this.validateRequiredString(
            value, 'Possible Damage', 
            rules.maxLengths.PossibleDamage,
            rules.minLengths.PossibleDamage,
            rules.textPattern
          );
          break;
          
        case 'PotentialRiskScenarios':
          result = this.validateRequiredString(
            value, 'Potential Risk Scenarios', 
            rules.maxLengths.PotentialRiskScenarios,
            rules.minLengths.PotentialRiskScenarios,
            rules.textPattern
          );
          break;
          
        case 'RiskType':
          result = this.validateRequiredString(
            value, 'Risk Type', 
            rules.maxLengths.RiskType,
            rules.minLengths.RiskType,
            rules.textPattern
          );
          break;
          
        case 'RiskCategory':
          result = this.validateRequiredString(
            value, 'Risk Category', 
            rules.maxLengths.RiskCategory,
            rules.minLengths.RiskCategory,
            rules.textPattern
          );
          break;
          
        case 'RiskBusinessImpact':
          result = this.validateRequiredString(
            value, 'Risk Business Impact', 
            rules.maxLengths.RiskBusinessImpact,
            rules.minLengths.RiskBusinessImpact,
            rules.textPattern
          );
          break;
          
        case 'mitigation':
          result = this.validateRequiredString(
            value, 'Mitigation', 
            rules.maxLengths.mitigation,
            rules.minLengths.mitigation,
            rules.textPattern
          );
          break;
          
        case 'Applicability':
          result = this.validateOptionalString(
            value, 'Applicability', 
            rules.maxLengths.Applicability, 
            rules.textPattern
          );
          break;
          
        case 'Criticality':
          result = this.validateChoiceField(
            value, 'Criticality', 
            rules.allowedChoices.Criticality
          );
          break;
          
        case 'MandatoryOptional':
          result = this.validateChoiceField(
            value, 'Mandatory/Optional', 
            rules.allowedChoices.MandatoryOptional
          );
          break;
          
        case 'ManualAutomatic':
          result = this.validateChoiceField(
            value, 'Manual/Automatic', 
            rules.allowedChoices.ManualAutomatic
          );
          break;
          
        case 'Impact':
          result = this.validateNumericField(
            value, 'Severity Rating', 
            rules.numericRanges.Impact.min, 
            rules.numericRanges.Impact.max
          );
          break;
          
        case 'Probability':
          result = this.validateNumericField(
            value, 'Probability', 
            rules.numericRanges.Probability.min, 
            rules.numericRanges.Probability.max
          );
          break;
          

      }
      
      // Update validation errors for the field
      if (!compliance.validationErrors) {
        compliance.validationErrors = {};
      }
      
      if (result.errors.length > 0) {
        compliance.validationErrors[fieldName] = result.errors;
      } else {
        delete compliance.validationErrors[fieldName];
      }
      
      return result;
    },
    
    // Real-time validation on input
    onFieldChange(complianceIndex, fieldName, event) {
      const compliance = this.complianceList[complianceIndex];
      let value;
      
      // Handle different input types
      if (fieldName === 'IsRisk') {
        value = event.target.checked;
        compliance[fieldName] = value;
      } else {
        value = event.target.value;
        // Update the field value directly without sanitization during typing
        compliance[fieldName] = value;
        
        // Only validate for error display, don't replace the value
        this.validateComplianceField(compliance, fieldName, value);
      }
      
      // Force reactivity update
      this.$forceUpdate();
    },
    
    // Comprehensive form validation before submission
    validateAllFields() {
      let isValid = true;
      const errors = [];
      
      // Validate framework selection
      if (!this.selectedFramework || !this.selectedFramework.id) {
        errors.push('Please select a framework');
        isValid = false;
      }
      
      // Validate policy selection
      if (!this.selectedPolicy || !this.selectedPolicy.id) {
        errors.push('Please select a policy');
        isValid = false;
      }
      
      // Validate sub-policy selection
      if (!this.selectedSubPolicy || !this.selectedSubPolicy.id) {
        errors.push('Please select a sub-policy');
        isValid = false;
      }
      
      // Validate each compliance item
      this.complianceList.forEach((compliance, index) => {
        // Reset validation errors
        compliance.validationErrors = {};
        
        // Required fields validation - all fields are mandatory including risk fields
        const requiredFields = [
          'ComplianceTitle',
          'ComplianceItemDescription', 
          'ComplianceType',
          'Scope',
          'Objective',
          'BusinessUnitsCovered',
          'mitigation',
          'PossibleDamage',
          'PotentialRiskScenarios',
          'RiskType',
          'RiskCategory',
          'RiskBusinessImpact',
          'Criticality',
          'MandatoryOptional',
          'ManualAutomatic',
          'Impact',
          'Probability'
        ];
        
        // Validate reviewer selection
        if (!compliance.reviewer || compliance.reviewer === '') {
          compliance.validationErrors.reviewer_id = ['Please select a reviewer'];
          errors.push(`Please select a reviewer for item ${index + 1}`);
          isValid = false;
        }
        
        // Validate all required fields
        requiredFields.forEach(fieldName => {
          const result = this.validateComplianceField(compliance, fieldName, compliance[fieldName]);
          if (result.errors.length > 0) {
            errors.push(`Item ${index + 1}: ${result.errors.join(', ')}`);
            isValid = false;
          }
        });
        
        // Validate optional fields that have values
        const optionalFields = ['Identifier', 'Applicability'];
        optionalFields.forEach(fieldName => {
          if (compliance[fieldName] && compliance[fieldName].trim()) {
            const result = this.validateComplianceField(compliance, fieldName, compliance[fieldName]);
            if (result.errors.length > 0) {
              errors.push(`Item ${index + 1}: ${result.errors.join(', ')}`);
              isValid = false;
            }
          }
        });
      });
      
      return { isValid, errors };
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
          PopupService.error('Failed to load frameworks. Please refresh the page and try again.');
          return;
        }
        
        this.frameworks = frameworksData.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }));
      } catch (error) {
        PopupService.error('Failed to load frameworks. Please refresh the page and try again.');
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
            applicability: p.Applicability || ''
          }));
        } else {
          console.error('Error in response:', response.data);
          PopupService.error('Failed to load policies. Please try selecting a different framework.');
        }
      } catch (error) {
        PopupService.error('Failed to load policies. Please try selecting a different framework.');
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies(policyId) {
      try {
        this.loading = true;
        const response = await complianceService.getSubPolicies(policyId);
        if (response.data.success) {
          this.subPolicies = response.data.data.map(sp => ({
            id: sp.SubPolicyId,
            name: sp.SubPolicyName
          }));
        } else {
          console.error('Error in response:', response.data);
          PopupService.error('Failed to load sub-policies. Please try selecting a different policy.');
        }
      } catch (error) {
        PopupService.error('Failed to load sub-policies. Please try selecting a different policy.');
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async loadUsers() {
      try {
        this.loading = true;
        const response = await complianceService.getUsers();
        console.log('Users API response:', response); // Debug log
        
        if (response.data.success && Array.isArray(response.data.users)) {
          this.users = response.data.users.map(user => ({
            UserId: user.UserId,
            UserName: user.UserName || `User ${user.UserId}`,
            email: user.email || ''
          }));
          
          // Set default reviewer if users exist
          if (this.users.length > 0 && this.complianceList.length > 0) {
            this.complianceList[0].reviewer = this.users[0].UserId;
          }
          
          console.log('Loaded users:', this.users);
        } else {
          throw new Error('Invalid users data received');
        }
      } catch (error) {
        console.error('Failed to load users:', error);
        PopupService.error('Failed to load reviewers. Please refresh the page and try again.');
      } finally {
        this.loading = false;
      }
    },
    // Load category options from the server
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
        PopupService.error('Failed to load dropdown options. Some features may be limited.');
      } finally {
        this.loading = false;
      }
    },
    
    // Show dropdown for a specific field
    showDropdown(index, field) {
      // Close any open dropdown
      this.activeDropdown = { index, field };
      
      // Set initial filtered options based on current search term
      this.filterOptions(index, field);
      
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
        this.activeDropdown = { index: null, field: null };
      }
    },
    
    // Filter dropdown options based on search term
    filterOptions(index, field) {
      let searchTerm = '';
      
      switch (field) {
        case 'BusinessUnitsCovered':
          searchTerm = this.businessUnitSearch[index] || '';
          break;
        case 'RiskType':
          searchTerm = this.riskTypeSearch[index] || '';
          break;
        case 'RiskCategory':
          searchTerm = this.riskCategorySearch[index] || '';
          break;
        case 'RiskBusinessImpact':
          searchTerm = this.riskBusinessImpactSearch[index] || '';
          break;
      }
      
      // Filter options based on search term (case-insensitive)
      const lowerSearchTerm = searchTerm.toLowerCase();
      this.filteredOptions[field] = this.categoryOptions[field].filter(option => 
        option.value.toLowerCase().includes(lowerSearchTerm)
      );
    },
    
    // Select an option from the dropdown
    selectOption(index, field, value) {
      // Update the compliance item with the selected value
      this.complianceList[index][field] = value;
      
      // Update the search field to show the selected value
      switch (field) {
        case 'BusinessUnitsCovered':
          this.businessUnitSearch[index] = value;
          break;
        case 'RiskType':
          this.riskTypeSearch[index] = value;
          break;
        case 'RiskCategory':
          this.riskCategorySearch[index] = value;
          break;
        case 'RiskBusinessImpact':
          this.riskBusinessImpactSearch[index] = value;
          break;
      }
      
      // Close the dropdown
      this.activeDropdown = { index: null, field: null };
      
      // Validate the field
      this.validateComplianceField(this.complianceList[index], field, value);
    },
    
    // Add a new option to the category options
    async addNewOption(index, field, value) {
      if (!value || !value.trim()) return;
      
      try {
        this.loading = true;
        
        // Add the new option to the server
        const response = await complianceService.addCategoryBusinessUnit({
          source: field,
          value: value.trim()
        });
        
        if (response.data.success) {
          // Add the new option to the local options
          const newOption = response.data.data;
          this.categoryOptions[field].push({
            id: newOption.id,
            value: newOption.value
          });
          
          // Select the new option
          this.selectOption(index, field, newOption.value);
          
          PopupService.success(`Added new ${field} option: ${newOption.value}`);
        } else {
          throw new Error(response.data.error || 'Failed to add new option');
        }
      } catch (error) {
        console.error(`Failed to add new ${field} option:`, error);
        PopupService.error(`Failed to add new option: ${error.message || error}`);
      } finally {
        this.loading = false;
      }
    },
    
    addCompliance() {
      // Get applicability from the selected policy
      const policyApplicability = this.selectedPolicy ? this.selectedPolicy.applicability || '' : '';
      
      this.complianceList.push({
        ComplianceTitle: '',
        ComplianceItemDescription: '',
        ComplianceType: '',
        Scope: '',
        Objective: '',
        BusinessUnitsCovered: '',
        Identifier: '',
        IsRisk: false,
        PossibleDamage: '',
        mitigation: '',
        PotentialRiskScenarios: '',
        RiskType: '',
        RiskCategory: '',
        RiskBusinessImpact: '',
        Criticality: 'Medium',
        MandatoryOptional: 'Mandatory',
        ManualAutomatic: 'Manual',
        Impact: 5.0,
        Probability: 5.0,
        Status: 'Under Review',
        reviewer: 2, // Default reviewer
        Applicability: policyApplicability, // Set Applicability from policy
        MaturityLevel: 'Initial', // Add default MaturityLevel
        ActiveInactive: 'Active', // Add default ActiveInactive
        PermanentTemporary: 'Permanent', // Add default PermanentTemporary
        validationErrors: {}
      });
      
      // Add empty search terms for the new compliance item
      this.businessUnitSearch.push('');
      this.riskTypeSearch.push('');
      this.riskCategorySearch.push('');
      this.riskBusinessImpactSearch.push('');
      
      // Switch to the newly added tab
      this.activeTab = this.complianceList.length - 1;
    },
    removeCompliance(idx) {
      if (this.complianceList.length > 1) {
        // If removing the active tab or a tab before it, adjust the active tab
        if (idx <= this.activeTab) {
          // If removing the last tab and it's active, go to previous tab
          if (idx === this.complianceList.length - 1 && idx === this.activeTab) {
            this.activeTab = Math.max(0, idx - 1);
          } 
          // If removing a tab before the active one, decrement active tab index
          else if (idx < this.activeTab) {
            this.activeTab--;
          }
        }
        
        // Remove the compliance item
        this.complianceList.splice(idx, 1);
        
        // Remove the search terms for this item
        this.businessUnitSearch.splice(idx, 1);
        this.riskTypeSearch.splice(idx, 1);
        this.riskCategorySearch.splice(idx, 1);
        this.riskBusinessImpactSearch.splice(idx, 1);
        
        // Close any open dropdown
        this.activeDropdown = { index: null, field: null };
      }
    },

    async submitCompliance() {
      // Comprehensive validation using allow-list approach
      const validation = this.validateAllFields();
      
      if (!validation.isValid) {
        PopupService.error(validation.errors.join('\n'), 'Validation Error');
        return;
      }

      try {
        this.loading = true;
        const complianceData = this.complianceList.map(compliance => ({
          SubPolicy: this.selectedSubPolicy.id,
          ComplianceTitle: this.sanitizeStringForSubmission(compliance.ComplianceTitle),
          ComplianceItemDescription: this.sanitizeStringForSubmission(compliance.ComplianceItemDescription),
          ComplianceType: this.sanitizeStringForSubmission(compliance.ComplianceType),
          Scope: this.sanitizeStringForSubmission(compliance.Scope),
          Objective: this.sanitizeStringForSubmission(compliance.Objective),
          BusinessUnitsCovered: this.sanitizeStringForSubmission(compliance.BusinessUnitsCovered),
          Identifier: this.sanitizeStringForSubmission(compliance.Identifier) || '',
          IsRisk: Boolean(compliance.IsRisk),
          PossibleDamage: this.sanitizeStringForSubmission(compliance.PossibleDamage),
          mitigation: this.sanitizeStringForSubmission(compliance.mitigation),
          PotentialRiskScenarios: this.sanitizeStringForSubmission(compliance.PotentialRiskScenarios),
          RiskType: this.sanitizeStringForSubmission(compliance.RiskType),
          RiskCategory: this.sanitizeStringForSubmission(compliance.RiskCategory),
          RiskBusinessImpact: this.sanitizeStringForSubmission(compliance.RiskBusinessImpact),
          Criticality: compliance.Criticality,
          MandatoryOptional: compliance.MandatoryOptional,
          ManualAutomatic: compliance.ManualAutomatic,
          Impact: compliance.Impact,
          Probability: compliance.Probability,
          Status: compliance.Status,
          ComplianceVersion: "1.0",
          reviewer_id: compliance.reviewer,
          Applicability: this.sanitizeStringForSubmission(compliance.Applicability),
          MaturityLevel: compliance.MaturityLevel || 'Initial',
          ActiveInactive: compliance.ActiveInactive || 'Active',
          PermanentTemporary: compliance.PermanentTemporary || 'Permanent'
        }));

        // Submit all compliance items and collect created IDs
        const createdComplianceIds = [];
        for (const data of complianceData) {
          console.log('Submitting compliance data:', data);
          const response = await complianceService.createCompliance(data);
          console.log('Response:', response);
          
          if (!response.data.success) {
            console.error('Validation errors:', response.data.errors);
            throw new Error(JSON.stringify(response.data.errors) || 'Failed to create compliance');
          }
          
          // Extract compliance ID from response
          if (response.data.compliance && response.data.compliance.ComplianceId) {
            createdComplianceIds.push(response.data.compliance.ComplianceId);
          } else if (response.data.ComplianceId) {
            createdComplianceIds.push(response.data.ComplianceId);
          }
        }

        // Show success popup with compliance IDs
        let successMessage = 'All compliance items have been successfully saved and submitted for review!';
        if (createdComplianceIds.length > 0) {
          if (createdComplianceIds.length === 1) {
            successMessage = `Compliance item has been successfully created with ID: ${createdComplianceIds[0]} and submitted for review!`;
          } else {
            successMessage = `${createdComplianceIds.length} compliance items have been successfully created with IDs: ${createdComplianceIds.join(', ')} and submitted for review!`;
          }
        }
        PopupService.success(successMessage, 'Success');
        
        // Reset form
        this.$emit('compliance-created');
        this.complianceList = [
          {
            ComplianceTitle: '',
            ComplianceItemDescription: '',
            ComplianceType: '',
            Scope: '',
            Objective: '',
            BusinessUnitsCovered: '',
            Identifier: '',
            IsRisk: false,
            PossibleDamage: '',
            mitigation: '',
            PotentialRiskScenarios: '',
            RiskType: '',
            RiskCategory: '',
            RiskBusinessImpact: '',
            Criticality: 'Medium',
            MandatoryOptional: 'Mandatory',
            ManualAutomatic: 'Manual',
            Impact: 5.0,
            Probability: 5.0,
            Status: 'Under Review',
            reviewer: 2, // Default reviewer
            Applicability: '',
            MaturityLevel: 'Initial', // Add default MaturityLevel
            ActiveInactive: 'Active', // Add default ActiveInactive
            PermanentTemporary: 'Permanent', // Add default PermanentTemporary
            validationErrors: {}
          }
        ];
        
        // Reset active tab
        this.activeTab = 0;

        // Clear selections
        this.selectedSubPolicy = '';
        this.selectedPolicy = '';
        this.selectedFramework = '';
      } catch (error) {
        console.error('Error submitting compliance:', error);
        let errorMessage = 'Failed to submit compliance. Please check your data and try again.';
        if (error.response?.data?.errors) {
          errorMessage = Object.entries(error.response.data.errors)
            .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
            .join('\n');
        } else if (error.message) {
          try {
            const parsedError = JSON.parse(error.message);
            errorMessage = Object.entries(parsedError)
              .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
              .join('\n');
          } catch {
            errorMessage = error.message;
          }
        }
        PopupService.error(errorMessage, 'Submission Failed');
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
@import './CreateCompliance.css';

.create-compliance-container {
  font-size: 14px;  /* Base font size for the component */
}

.compliance-header h2 {
  font-size: 1.5rem;
}

.compliance-header p {
  font-size: 0.9rem;
}

.compliance-field label {
  font-size: 0.85rem;
}

.compliance-input,
.compliance-select {
  font-size: 0.9rem !important;
}

.item-number {
  font-size: 1.5rem;
}

.compliance-submit-btn {
  font-size: 0.9rem;
}

.validation-error {
  font-size: 0.75rem;
}

.compliance-field small {
  font-size: 0.75rem;
}
</style> 