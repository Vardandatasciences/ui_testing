<template>
  <div class="create-compliance-container">
    <!-- Header section -->
    <div class="compliance-header">
      <div class="header-content">
        <div class="header-text">
          <h2>Edit Compliance Record</h2>
          <p>Update compliance item details</p>
        </div>
        <button 
          class="back-button" 
          @click="goBack"
          title="Go back to previous page"
        >
          <i class="fas fa-arrow-left"></i>
          Back
        </button>
      </div>
    </div>

    <!-- Message display -->
    <div v-if="error" class="message error-message">
      {{ error }}
    </div>
    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <div class="loading-text">Loading data...</div>
    </div>

    <!-- Edit form -->
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
              <span class="field-requirements">(3-145 characters)</span>
            </label>
            <div class="input-wrapper">
              <input 
                v-model="compliance.ComplianceTitle" 
                class="compliance-input" 
                :class="{
                  'error': validationErrors.ComplianceTitle,
                  'warning': showWarning('ComplianceTitle'),
                  'valid': isFieldValid('ComplianceTitle')
                }"
                placeholder="Enter compliance title"
                required 
                @input="validateFieldRealTime('ComplianceTitle')"
                @blur="validateField('ComplianceTitle')"
                title="Enter the title of the compliance item"
                :ref="'field_ComplianceTitle'"
              />
              <div class="validation-indicator" v-if="compliance.ComplianceTitle">
                <span v-if="isFieldValid('ComplianceTitle')" class="valid-icon">✓</span>
                <span v-else class="invalid-icon">!</span>
              </div>
            </div>
            <div v-if="validationErrors.ComplianceTitle" class="field-error-message">
              {{ validationErrors.ComplianceTitle }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Compliance Type 
              <span class="required">*</span>
              <span class="field-requirements">(Required)</span>
            </label>
            <div class="input-wrapper">
              <input 
                v-model="compliance.ComplianceType" 
                class="compliance-input" 
                :class="{
                  'error': validationErrors.ComplianceType,
                  'valid': isFieldValid('ComplianceType')
                }"
                placeholder="Enter compliance type"
                @input="validateFieldRealTime('ComplianceType')"
                @blur="validateField('ComplianceType')"
                title="Type of compliance (e.g. Regulatory, Internal, Security)"
                :ref="'field_ComplianceType'"
              />
              <div class="validation-indicator" v-if="compliance.ComplianceType">
                <span v-if="isFieldValid('ComplianceType')" class="valid-icon">✓</span>
                <span v-else class="invalid-icon">!</span>
              </div>
            </div>
            <div v-if="validationErrors.ComplianceType" class="field-error-message">
              {{ validationErrors.ComplianceType }}
            </div>
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Compliance Description 
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 10 characters)</span>
          </label>
          <div class="input-wrapper">
            <textarea 
              v-model="compliance.ComplianceItemDescription" 
              class="compliance-input" 
              :class="{
                'error': validationErrors.ComplianceItemDescription,
                'warning': showWarning('ComplianceItemDescription'),
                'valid': isFieldValid('ComplianceItemDescription')
              }"
              placeholder="Compliance Description"
              @input="validateFieldRealTime('ComplianceItemDescription')"
              @blur="validateField('ComplianceItemDescription')"
              required 
              rows="3"
              title="Detailed description of the compliance requirement"
              :ref="'field_ComplianceItemDescription'"
            ></textarea>
            <div class="char-count" :class="{ 'error': validationErrors.ComplianceItemDescription }">
              {{ compliance.ComplianceItemDescription?.length || 0 }}/10 min characters
            </div>
            <div v-if="validationErrors.ComplianceItemDescription" class="field-error-message">
              {{ validationErrors.ComplianceItemDescription }}
            </div>
          </div>
          <div class="validation-feedback" v-if="compliance.ComplianceItemDescription">
            <div class="validation-progress">
              <div 
                class="progress-bar"
                :style="{
                  width: getValidationProgress('ComplianceItemDescription') + '%',
                  backgroundColor: getValidationColor('ComplianceItemDescription')
                }"
              ></div>
            </div>
            <span 
              :class="[
                'validation-message',
                {
                  'warning': showWarning('ComplianceItemDescription'),
                  'error': validationErrors.ComplianceItemDescription,
                  'success': isFieldValid('ComplianceItemDescription')
                }
              ]"
            >
              {{ getValidationMessage('ComplianceItemDescription') }}
            </span>
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Scope
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 15 characters)</span>
          </label>
          <div class="input-wrapper">
            <textarea 
              v-model="compliance.Scope" 
              class="compliance-input" 
              :class="{
                'error': validationErrors.Scope,
                'warning': showWarning('Scope'),
                'valid': isFieldValid('Scope')
              }"
              placeholder="Define the scope of this compliance requirement"
              @input="validateFieldRealTime('Scope')"
              @blur="validateField('Scope')"
              rows="3"
              data-field="Scope"
              required
              :ref="'field_Scope'"
            ></textarea>
            <div class="char-count" :class="{ 
              'error': validationErrors.Scope,
              'warning': showWarning('Scope')
            }">
              {{ compliance.Scope?.length || 0 }}/15 min characters
            </div>
            <div v-if="validationErrors.Scope" class="field-error-message">
              {{ validationErrors.Scope }}
            </div>
          </div>
          <div class="validation-feedback" v-if="compliance.Scope">
            <div class="validation-progress">
              <div 
                class="progress-bar"
                :style="{
                  width: getValidationProgress('Scope') + '%',
                  backgroundColor: getValidationColor('Scope')
                }"
              ></div>
            </div>
            <span 
              :class="[
                'validation-message',
                {
                  'warning': showWarning('Scope'),
                  'error': validationErrors.Scope,
                  'success': isFieldValid('Scope')
                }
              ]"
            >
              {{ getValidationMessage('Scope') }}
            </span>
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Objective
            <span class="required">*</span>
            <span class="field-requirements">(Minimum 15 characters)</span>
          </label>
          <div class="input-wrapper">
            <textarea 
              v-model="compliance.Objective" 
              class="compliance-input" 
              :class="{
                'error': validationErrors.Objective,
                'warning': showWarning('Objective'),
                'valid': isFieldValid('Objective')
              }"
              placeholder="Define the objective of this compliance requirement"
              @input="validateFieldRealTime('Objective')"
              @blur="validateField('Objective')"
              rows="3"
              data-field="Objective"
              required
              :ref="'field_Objective'"
            ></textarea>
            <div class="char-count" :class="{ 
              'error': validationErrors.Objective,
              'warning': showWarning('Objective')
            }">
              {{ compliance.Objective?.length || 0 }}/15 min characters
            </div>
            <div v-if="validationErrors.Objective" class="field-error-message">
              {{ validationErrors.Objective }}
            </div>
          </div>
          <div class="validation-feedback" v-if="compliance.Objective">
            <div class="validation-progress">
              <div 
                class="progress-bar"
                :style="{
                  width: getValidationProgress('Objective') + '%',
                  backgroundColor: getValidationColor('Objective')
                }"
              ></div>
            </div>
            <span 
              :class="[
                'validation-message',
                {
                  'warning': showWarning('Objective'),
                  'error': validationErrors.Objective,
                  'success': isFieldValid('Objective')
                }
              ]"
            >
              {{ getValidationMessage('Objective') }}
            </span>
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
                :ref="'field_BusinessUnitsCovered'"
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
            <div v-if="validationErrors.BusinessUnitsCovered" class="field-error-message">
              {{ validationErrors.BusinessUnitsCovered }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>Identifier</label>
            <input 
              v-model="compliance.Identifier" 
              class="compliance-input" 
              placeholder="Auto-generated if left empty"
              title="Unique identifier for this compliance item"
              disabled
              :ref="'field_Identifier'"
            />
            <div v-if="validationErrors.Identifier" class="field-error-message">
              {{ validationErrors.Identifier }}
            </div>
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
            <span class="field-requirements">(Minimum 10 characters)</span>
          </label>
          <div class="input-wrapper">
            <textarea 
              v-model="compliance.PossibleDamage" 
              class="compliance-input" 
              :class="{
                'error': validationErrors.PossibleDamage,
                'warning': showWarning('PossibleDamage'),
                'valid': isFieldValid('PossibleDamage')
              }"
              placeholder="Describe possible damage"
              @input="validateFieldRealTime('PossibleDamage')"
              @blur="validateField('PossibleDamage')"
              rows="3"
              :required="compliance.IsRisk"
              :ref="'field_PossibleDamage'"
            ></textarea>
            <div class="char-count" :class="{ 'error': validationErrors.PossibleDamage }">
              {{ compliance.PossibleDamage?.length || 0 }}/10 min characters
            </div>
            <div v-if="validationErrors.PossibleDamage" class="field-error-message">
              {{ validationErrors.PossibleDamage }}
            </div>
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Mitigation Steps
            <span v-if="compliance.IsRisk" class="required">*</span>
          </label>
          <div class="mitigation-steps">
            <div v-for="(step, stepIndex) in mitigationSteps" :key="stepIndex" class="mitigation-step">
              <div class="step-header">
                <span class="step-number">Step {{ stepIndex + 1 }}</span>
                <button type="button" class="remove-step-btn" @click="removeStep(stepIndex)" title="Remove this step">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <textarea
                v-model="step.description"
                @input="onMitigationStepChange"
                class="compliance-input"
                :class="{
                  'error': validationErrors.mitigation,
                  'valid': isFieldValid('mitigation')
                }"
                placeholder="Describe this mitigation step"
                rows="2"
                required
              ></textarea>
            </div>
            <button type="button" class="add-step-btn" @click="addStep" title="Add new mitigation step">
              <i class="fas fa-plus"></i> Add Step
            </button>
          </div>
          <div v-if="validationErrors.mitigation" class="error-message">
            {{ validationErrors.mitigation }}
          </div>
        </div>
        
        <div class="compliance-field full-width">
          <label>
            Potential Risk Scenarios
            <span class="field-requirements">(Recommended: 20+ characters)</span>
          </label>
          <div class="input-wrapper">
            <textarea 
              v-model="compliance.PotentialRiskScenarios" 
              class="compliance-input" 
              :class="{
                'warning': showWarning('PotentialRiskScenarios'),
                'valid': isFieldValid('PotentialRiskScenarios')
              }"
              placeholder="Describe potential risk scenarios"
              @input="validateFieldRealTime('PotentialRiskScenarios')"
              @blur="validateField('PotentialRiskScenarios')"
              rows="3"
              :ref="'field_PotentialRiskScenarios'"
            ></textarea>
            <div class="char-count">
              {{ compliance.PotentialRiskScenarios?.length || 0 }} characters
            </div>
            <div v-if="validationErrors.PotentialRiskScenarios" class="field-error-message">
              {{ validationErrors.PotentialRiskScenarios }}
            </div>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Risk Type
              <span class="required">*</span>
            </label>
            <div class="input-wrapper">
              <select 
                v-model="compliance.RiskType"
                class="compliance-input"
                :class="{
                  'error': validationErrors.RiskType,
                  'valid': isFieldValid('RiskType')
                }"
                @change="validateFieldRealTime('RiskType')"
                @blur="validateField('RiskType')"
                :ref="'field_RiskType'"
              >
                <option value="">Select Risk Type</option>
                <option value="Current">Current</option>
                <option value="Residual">Residual</option>
                <option value="Inherent">Inherent</option>
                <option value="Emerging">Emerging</option>
                <option value="Accepted">Accepted</option>
              </select>
              <div class="validation-indicator" v-if="compliance.RiskType">
                <span v-if="isFieldValid('RiskType')" class="valid-icon">✓</span>
                <span v-else class="invalid-icon">!</span>
              </div>
            </div>
            <div v-if="validationErrors.RiskType" class="field-error-message">
              {{ validationErrors.RiskType }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Risk Category
              <span class="required">*</span>
            </label>
            <div class="input-wrapper">
              <div class="searchable-dropdown">
                <input 
                  v-model="riskCategorySearch" 
                  class="compliance-input" 
                  :class="{
                    'error': validationErrors.RiskCategory,
                    'valid': isFieldValid('RiskCategory')
                  }"
                  placeholder="Search or add risk category"
                  @input="validateFieldRealTime('RiskCategory')"
                  @blur="validateField('RiskCategory')"
                  :ref="'field_RiskCategory'"
                />
                <div class="validation-indicator" v-if="compliance.RiskCategory">
                  <span v-if="isFieldValid('RiskCategory')" class="valid-icon">✓</span>
                  <span v-else class="invalid-icon">!</span>
                </div>
              </div>
            </div>
            <div v-if="validationErrors.RiskCategory" class="field-error-message">
              {{ validationErrors.RiskCategory }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Risk Business Impact
              <span class="required">*</span>
            </label>
            <div class="input-wrapper">
              <div class="searchable-dropdown">
                <input 
                  v-model="riskBusinessImpactSearch" 
                  class="compliance-input" 
                  :class="{
                    'error': validationErrors.RiskBusinessImpact,
                    'valid': isFieldValid('RiskBusinessImpact')
                  }"
                  placeholder="Search or add business impact"
                  @input="validateFieldRealTime('RiskBusinessImpact')"
                  @blur="validateField('RiskBusinessImpact')"
                  :ref="'field_RiskBusinessImpact'"
                />
                <div class="validation-indicator" v-if="compliance.RiskBusinessImpact">
                  <span v-if="isFieldValid('RiskBusinessImpact')" class="valid-icon">✓</span>
                  <span v-else class="invalid-icon">!</span>
                </div>
              </div>
            </div>
            <div v-if="validationErrors.RiskBusinessImpact" class="field-error-message">
              {{ validationErrors.RiskBusinessImpact }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Compliance classification fields - grouped together -->
      <div class="field-group classification-fields">
        <div class="field-group-title">Classification</div>
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Criticality
              <span class="required">*</span>
            </label>
            <div class="input-wrapper">
              <select 
                v-model="compliance.Criticality" 
                class="compliance-select" 
                :class="{
                  'error': validationErrors.Criticality,
                  'valid': isFieldValid('Criticality')
                }"
                @change="validateFieldRealTime('Criticality')"
                @blur="validateField('Criticality')"
                required
                :ref="'field_Criticality'"
              >
                <option value="">Select Criticality</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
              <div class="validation-indicator" v-if="compliance.Criticality">
                <span v-if="isFieldValid('Criticality')" class="valid-icon">✓</span>
                <span v-else class="invalid-icon">!</span>
              </div>
            </div>
            <div v-if="validationErrors.Criticality" class="field-error-message">
              {{ validationErrors.Criticality }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Mandatory/Optional
            </label>
            <select 
              v-model="compliance.MandatoryOptional" 
              class="compliance-select" 
              required
              title="Whether this compliance item is mandatory or optional"
              :ref="'field_MandatoryOptional'"
            >
              <option value="Mandatory">Mandatory</option>
              <option value="Optional">Optional</option>
            </select>
            <div v-if="validationErrors.MandatoryOptional" class="field-error-message">
              {{ validationErrors.MandatoryOptional }}
            </div>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Manual/Automatic
            </label>
            <select 
              v-model="compliance.ManualAutomatic" 
              class="compliance-select" 
              required
              title="Whether this compliance is checked manually or automatically"
              :ref="'field_ManualAutomatic'"
            >
              <option value="Manual">Manual</option>
              <option value="Automatic">Automatic</option>
            </select>
            <div v-if="validationErrors.ManualAutomatic" class="field-error-message">
              {{ validationErrors.ManualAutomatic }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Applicability
            </label>
            <input 
              v-model="compliance.Applicability" 
              class="compliance-input" 
              placeholder="Applicability from policy"
              title="Describes where this compliance item applies"
              :ref="'field_Applicability'"
            />
            <div v-if="validationErrors.Applicability" class="field-error-message">
              {{ validationErrors.Applicability }}
            </div>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Impact
              <span class="required">*</span>
              <span class="field-requirements">(0-10)</span>
            </label>
            <input 
              type="number" 
              v-model="compliance.Impact"
              class="compliance-input"
              :class="{ 'error': validationErrors.Impact }"
              step="0.1"
              min="0"
              max="10"
              @input="validateFieldRealTime('Impact')"
              @blur="validateField('Impact')"
              required
              :ref="'field_Impact'"
            />
            <div v-if="validationErrors.Impact" class="field-error-message">
              {{ validationErrors.Impact }}
            </div>
          </div>
          
          <div class="compliance-field">
            <label>
              Probability
              <span class="required">*</span>
              <span class="field-requirements">(0-10)</span>
            </label>
            <input 
              type="number" 
              v-model="compliance.Probability"
              class="compliance-input"
              :class="{ 'error': validationErrors.Probability }"
              step="0.1"
              min="0"
              max="10"
              @input="validateFieldRealTime('Probability')"
              @blur="validateField('Probability')"
              required
              :ref="'field_Probability'"
            />
            <div v-if="validationErrors.Probability" class="field-error-message">
              {{ validationErrors.Probability }}
            </div>
          </div>
        </div>
        
        <div class="row-fields">
          <div class="compliance-field">
            <label>
              Maturity Level
            </label>
            <select 
              v-model="compliance.MaturityLevel" 
              class="compliance-select"
              title="Current maturity level of this compliance item"
              :ref="'field_MaturityLevel'"
            >
              <option>Initial</option>
              <option>Developing</option>
              <option>Defined</option>
              <option>Managed</option>
              <option>Optimizing</option>
            </select>
            <div v-if="validationErrors.MaturityLevel" class="field-error-message">
              {{ validationErrors.MaturityLevel }}
            </div>
          </div>
          <div class="compliance-field">
            <label>
              Version Type
            </label>
            <select 
              v-model="compliance.versionType" 
              class="compliance-select" 
              required
              title="Type of version change"
              :ref="'field_versionType'"
            >
              <option value="Major">Major</option>
              <option value="Minor">Minor</option>
            </select>
            <div v-if="validationErrors.versionType" class="field-error-message">
              {{ validationErrors.versionType }}
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
            <label>Assign Reviewer <span class="required">*</span></label>
            <select 
              v-model="compliance.reviewer_id" 
              class="compliance-select" 
              :class="{ 'error': validationErrors.reviewer_id }"
              @change="validateField('reviewer_id')"
              required
              title="Person responsible for reviewing this compliance item"
              :ref="'field_reviewer_id'"
            >
              <option value="">Select Reviewer</option>
              <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                {{ user.UserName }} {{ user.email ? `(${user.email})` : '' }}
              </option>
            </select>
            <div v-if="validationErrors.reviewer_id" class="field-error-message">
              {{ validationErrors.reviewer_id }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="compliance-submit-container">
      <button 
        class="compliance-submit-btn" 
        @click="validateAndSubmit"
        :disabled="loading"
      >
        <span v-if="loading">Saving...</span>
        <span v-else>Save as New Version</span>
      </button>
      <button 
        class="compliance-cancel-btn" 
        @click="cancelEdit"
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
  name: 'EditCompliance',
  data() {
    return {
      compliance: null,
      users: [],
      loading: false,
      error: null,
      successMessage: null,
      impactError: false,
      probabilityError: false,
      originalComplianceId: null,
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
          { required: true, message: 'Compliance Title is required' },
          { minLength: 3, message: 'Title must be at least 3 characters' },
          { maxLength: 145, message: 'Title cannot exceed 145 characters' }
        ],
        ComplianceType: [
          { required: true, message: 'Compliance Type is required' }
        ],
        ComplianceItemDescription: [
          { required: true, message: 'Description is required' },
          { minLength: 10, message: 'Description must be at least 10 characters' }
        ],
        Scope: [
          { required: true, message: 'Scope is required' },
          { minLength: 15, message: 'Scope must be at least 15 characters' }
        ],
        Objective: [
          { required: true, message: 'Objective is required' },
          { minLength: 15, message: 'Objective must be at least 15 characters' }
        ],
        BusinessUnitsCovered: [
          { required: true, message: 'Business Units Covered is required' }
        ],
        Criticality: [
          { required: true, message: 'Criticality is required' }
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
        ],
        PossibleDamage: [
          { required: true, message: 'Possible Damage is required for risks' },
          { minLength: 10, message: 'Possible Damage must be at least 10 characters' }
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
        mitigation: [
          { 
            required: true, 
            message: 'At least one mitigation step is required for risks',
            validate: (value) => {
              if (!value) return false;
              if (typeof value === 'object') {
                return Object.values(value).some(step => step && step.trim().length > 0);
              }
              return value.trim().length > 0;
            }
          }
        ]
      },
      fieldStates: {}, // Track real-time validation states
      mitigationSteps: [{ description: '' }],
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
    await this.loadComplianceData(complianceId);
    await this.loadCategoryOptions();
    
    // Add click event listener to close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // Remove event listener when component is unmounted
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    async loadComplianceData(complianceId) {
      try {
        this.loading = true;
        const response = await complianceService.getComplianceById(complianceId);
        
        if (response.data && response.data.success) {
          this.compliance = {
            ...response.data.data,
            versionType: 'minor' // Set default version type
          };
          
          // Set default reviewer if not present
          if (!this.compliance.reviewer_id && this.users.length > 0) {
            this.compliance.reviewer_id = this.users[0].UserId;
          }
          
          // Initialize search fields with current values
          this.businessUnitSearch = this.compliance.BusinessUnitsCovered || '';
          this.riskTypeSearch = this.compliance.RiskType || '';
          this.riskCategorySearch = this.compliance.RiskCategory || '';
          this.riskBusinessImpactSearch = this.compliance.RiskBusinessImpact || '';
          
          // Initialize mitigation steps from loaded compliance data
          this.mitigationSteps = this.parseMitigationSteps(this.compliance.mitigation);
        } else {
          this.error = 'Failed to load compliance data';
        }
      } catch (error) {
        console.error('Error loading compliance:', error);
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
    validateField(fieldName) {
      const value = this.compliance[fieldName];
      const rules = this.validationRules[fieldName];
      
      // Reset error for this field
      this.validationErrors[fieldName] = '';
      
      // Skip validation if field is not required and empty
      if (!rules.find(rule => rule.required) && !value) {
        return true;
      }
      
      // Skip PossibleDamage validation if IsRisk is false
      if (fieldName === 'PossibleDamage' && !this.compliance.IsRisk) {
        return true;
      }
      
      for (const rule of rules) {
        // Required validation
        if (rule.required && (!value || value.toString().trim() === '')) {
          this.validationErrors[fieldName] = rule.message;
          return false;
        }
        
        // Min length validation
        if (rule.minLength && value && value.length < rule.minLength) {
          this.validationErrors[fieldName] = rule.message;
          return false;
        }
        
        // Max length validation
        if (rule.maxLength && value && value.length > rule.maxLength) {
          this.validationErrors[fieldName] = rule.message;
          return false;
        }
        
        // Min/Max number validation
        if ((rule.min !== undefined || rule.max !== undefined) && value) {
          const numValue = parseFloat(value);
          if (isNaN(numValue) || numValue < rule.min || numValue > rule.max) {
            this.validationErrors[fieldName] = rule.message;
            return false;
          }
        }
      }
      
      return true;
    },

    validateAllFields() {
      let isValid = true;
      let firstErrorField = null;
      
      // Validate all fields
      for (const fieldName in this.validationRules) {
        // Skip risk-related fields if IsRisk is false
        if (!this.compliance.IsRisk && 
            ['PossibleDamage', 'RiskType', 'RiskCategory', 'RiskBusinessImpact', 'mitigation', 'PotentialRiskScenarios']
            .includes(fieldName)) {
          continue;
        }

        if (!this.validateField(fieldName)) {
          isValid = false;
          if (!firstErrorField) {
            firstErrorField = fieldName;
          }
        }
      }

      // If validation failed, scroll to the first error
      if (firstErrorField) {
        const element = document.querySelector(`[data-field="${firstErrorField}"]`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }

      return isValid;
    },

    async submitEdit() {
      // Reset messages
      this.error = null;
      this.successMessage = null;

      // Validate all fields before submission
      if (!this.validateAllFields()) {
        this.error = 'Please fill in all required fields with valid information';
        return;
      }

      try {
        this.loading = true;
        
        // Calculate new version based on version type
        const currentVersion = parseFloat(this.compliance.ComplianceVersion) || 1.0;
        let newVersion;
        
        if (this.compliance.versionType === 'Major') {
          newVersion = Math.floor(currentVersion) + 1 + '.0';
        } else {
          const [major, minor] = currentVersion.toString().split('.');
          newVersion = `${major}.${(parseInt(minor) || 0) + 1}`;
        }
        
        // Prepare submission data
        const editData = {
          ...this.compliance,
          ComplianceVersion: newVersion,
          Status: 'Under Review',
          ActiveInactive: 'Active',
          PreviousComplianceVersionId: this.originalComplianceId
        };

        // Use the complianceService to save the edit
        const response = await complianceService.updateCompliance(this.originalComplianceId, editData);
        
        if (response.data && response.data.success) {
          CompliancePopups.complianceUpdated({
            ComplianceId: response.data.compliance_id || this.originalComplianceId,
            ComplianceVersion: newVersion,
            ComplianceItemDescription: this.compliance.ComplianceItemDescription
          });
          
          setTimeout(() => {
            this.$router.push('/compliance/tailoring');
          }, 1500);
        } else {
          this.error = response.data.message || 'Failed to update compliance';
        }
      } catch (error) {
        console.error('Error updating compliance:', error);
        this.error = 'Failed to update compliance. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      // Navigate back to the previous page
      this.$router.go(-1);
    },
    cancelEdit() {
      // Show simple confirmation before canceling
      if (confirm('Are you sure you want to cancel editing? Any unsaved changes will be lost.')) {
        this.$router.push('/compliance/tailoring');
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
        this.error = 'Failed to load dropdown options. Some features may be limited.';
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
      if (!value || !value.trim()) return;
      
      try {
        const response = await complianceService.addCategoryBusinessUnit({
          source: field,
          value: value.trim()
        });
        
        if (response.data.success) {
          // Add the new option to the category options
          const newOption = response.data.data;
          this.categoryOptions[field].push({
            id: newOption.id,
            value: newOption.value
          });
          
          // Select the new option
          this.selectOption(field, value);
          
          // Show success message
          this.successMessage = `Added new ${field} option: ${value}`;
          
          // Refresh options to ensure sync with backend
          await this.loadCategoryOptions();
        } else {
          throw new Error(response.data.error || 'Failed to add new option');
        }
      } catch (error) {
        console.error(`Failed to add new ${field} option:`, error);
        this.error = `Failed to add new option: ${error.message || error}`;
      }
    },

    validateFieldRealTime(fieldName) {
      // Skip validation for risk-related fields if IsRisk is false
      if (!this.compliance.IsRisk && ['PossibleDamage', 'mitigation', 'RiskType', 'RiskCategory', 'RiskBusinessImpact'].includes(fieldName)) {
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
      
      // Skip validation if field is not required and empty
      if (!rules.find(rule => rule.required) && !value) {
        this.validationErrors[fieldName] = '';
        this.fieldStates[fieldName].valid = true;
        this.fieldStates[fieldName].warning = false;
        return true;
      }
      
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

    isFieldValid(fieldName) {
      return this.fieldStates[fieldName]?.valid || false;
    },

    showWarning(fieldName) {
      return this.fieldStates[fieldName]?.warning || false;
    },

    getValidationProgress(fieldName) {
      const value = this.compliance[fieldName];
      const rules = this.validationRules[fieldName];
      
      if (!value || !rules) return 0;
      
      // For numeric fields (Impact, Probability)
      if (['Impact', 'Probability'].includes(fieldName)) {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          return ((numValue - 1) / 9) * 100; // Scale 1-10 to 0-100%
        }
        return 0;
      }
      
      // For select fields
      if (['Criticality', 'MaturityLevel', 'MandatoryOptional', 'ManualAutomatic'].includes(fieldName)) {
        return value ? 100 : 0;
      }
      
      // For text fields with minLength
      const minLengthRule = rules.find(r => r.minLength);
      if (minLengthRule) {
        const progress = (value.length / minLengthRule.minLength) * 100;
        return Math.min(progress, 100);
      }
      
      return value ? 100 : 0;
    },

    getValidationColor(fieldName) {
      const progress = this.getValidationProgress(fieldName);
      if (progress < 50) return '#dc2626'; // Red
      if (progress < 100) return '#f59e0b'; // Yellow
      return '#10b981'; // Green
    },

    getValidationMessage(fieldName) {
      const value = this.compliance[fieldName];
      const rules = this.validationRules[fieldName];
      
      if (!value) {
        const requiredRule = rules.find(r => r.required);
        return requiredRule ? requiredRule.message : '';
      }
      
      if (this.validationErrors[fieldName]) return this.validationErrors[fieldName];
      
      const minLengthRule = rules.find(r => r.minLength);
      if (minLengthRule && value.length < minLengthRule.minLength) {
        const remaining = minLengthRule.minLength - value.length;
        return `Need ${remaining} more character${remaining === 1 ? '' : 's'}`;
      }
      
      const maxLengthRule = rules.find(r => r.maxLength);
      if (maxLengthRule && value.length > maxLengthRule.maxLength) {
        const excess = value.length - maxLengthRule.maxLength;
        return `Exceeds maximum length by ${excess} character${excess === 1 ? '' : 's'}`;
      }
      
      const numericRule = rules.find(r => r.min !== undefined || r.max !== undefined);
      if (numericRule) {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          return 'Please enter a valid number';
        }
        if (numValue < numericRule.min) {
          return `Minimum value is ${numericRule.min}`;
        }
        if (numValue > numericRule.max) {
          return `Maximum value is ${numericRule.max}`;
        }
      }
      
      if (this.isFieldValid(fieldName)) return 'Looks good!';
      
      return '';
    },

    scrollToError() {
      // Get all fields with errors
      const errorFields = Object.keys(this.validationErrors);
      if (errorFields.length > 0) {
        // Get the first field with error
        const firstErrorField = errorFields[0];
        const errorElement = this.$refs[`field_${firstErrorField}`];
        
        if (errorElement) {
          // Scroll to the element with smooth behavior
          errorElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
          // Focus the field
          errorElement.focus();
        }
      }
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
        // Scroll to the first error
        this.$nextTick(() => {
          this.scrollToError();
        });
        return;
      }

      // If valid, proceed with submission
      this.submitForm();
    },

    submitForm() {
      this.submitEdit();
    },

    addStep() {
      this.mitigationSteps.push({ description: '' });
      this.onMitigationStepChange();
    },
    removeStep(index) {
      if (this.mitigationSteps.length > 1) {
        this.mitigationSteps.splice(index, 1);
        this.onMitigationStepChange();
      }
    },
    onMitigationStepChange() {
      // Convert mitigation steps to the format expected by the backend
      this.compliance.mitigation = this.mitigationSteps.reduce((obj, step, index) => {
        if (step.description.trim()) {
          obj[`step${index + 1}`] = step.description;
        }
        return obj;
      }, {});
      
      // Validate mitigation field
      this.validateField('mitigation');
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

.required {
  color: #dc2626;
  margin-left: 2px;
  cursor: help;
  position: relative;
}

.required:hover::after {
  content: 'This field is required';
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #1f2937;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 10;
}

.error {
  border-color: #dc2626 !important;
}

.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.compliance-input.error,
.compliance-select.error {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.compliance-input.error:focus,
.compliance-select.error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.validation-indicator {
  position: absolute;
  right: 10px;
  display: flex;
  align-items: center;
}

.valid-icon {
  color: #10b981;
  font-weight: bold;
}

.invalid-icon {
  color: #dc2626;
  font-weight: bold;
}

.field-requirements {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
  font-style: italic;
}

.validation-feedback {
  margin-top: 0.25rem;
}

.validation-progress {
  height: 2px;
  background-color: #e5e7eb;
  border-radius: 2px;
  margin-bottom: 0.25rem;
}

.progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.validation-message {
  font-size: 0.75rem;
  transition: color 0.3s ease;
}

.validation-message.warning {
  color: #f59e0b;
}

.validation-message.error {
  color: #dc2626;
}

.validation-message.success {
  color: #10b981;
}

.char-count {
  position: absolute;
  right: 10px;
  bottom: 10px;
  font-size: 0.75rem;
  color: #6b7280;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.char-count.error {
  color: #dc2626;
  font-weight: 500;
}

.char-count.warning {
  color: #f59e0b;
  font-weight: 500;
}

.compliance-input.warning {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.compliance-input.valid {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.compliance-input.warning:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 1px #f59e0b;
}

.compliance-input.valid:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 1px #10b981;
}

.searchable-dropdown {
  position: relative;
  width: 100%;
}

.searchable-dropdown .validation-indicator {
  right: 30px; /* Adjust for dropdown arrow */
}

/* Add styles for select elements */
.compliance-select {
  padding-right: 30px; /* Make room for validation indicator */
}

.compliance-select.valid {
  background-color: #f0fdf4;
  border-color: #10b981;
}

.compliance-select.error {
  background-color: #fef2f2;
  border-color: #dc2626;
}

/* Numeric input specific styles */
input[type="number"].compliance-input {
  text-align: right;
  padding-right: 30px;
}

/* Progress bar variations */
.validation-progress .progress-bar.numeric {
  transition: width 0.2s ease;
}

.validation-progress .progress-bar.select {
  transition: width 0s;
}

.validation-summary {
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #fee2e2;
  color: #dc2626;
}

.validation-summary ul {
  margin: 0.5rem 0 0 1.5rem;
  padding: 0;
}

.validation-summary li {
  margin-bottom: 0.25rem;
}

/* Update numeric input styles */
input[type="number"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  transition: border-color 0.2s ease;
}

input[type="number"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

input[type="number"].error {
  border-color: #dc2626;
}

/* Remove arrows from number inputs */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

.validation-message.error {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.field-requirements {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
}

.field-error-message {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  padding: 0.25rem 0;
}

.compliance-input.error {
  border-color: #dc2626;
  background-color: #fff5f5;
}

.compliance-input.error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
}

.input-wrapper {
  position: relative;
  width: 100%;
}

/* Highlight animation for error fields */
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

/* Make error messages more visible */
.field-error-message {
  background-color: #fee2e2;
  border-radius: 4px;
  padding: 0.5rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Add visual indicator for required fields */
.required {
  color: #dc2626;
  margin-left: 0.25rem;
}

/* Improve field requirements visibility */
.field-requirements {
  color: #6b7280;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

/* Add transition for smooth error state changes */
.compliance-input {
  transition: all 0.3s ease;
}

/* Header layout styles */
.compliance-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
}

.header-text {
  flex: 1;
}

.header-text h2 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.875rem;
  font-weight: 700;
}

.header-text p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

/* Back button styles */
.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #f8fafc;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
  margin-left: 1rem;
}

.back-button:hover {
  background-color: #e2e8f0;
  color: #1e293b;
  border-color: #94a3b8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.back-button:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.back-button i {
  font-size: 0.875rem;
}

/* Responsive design for header */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .back-button {
    align-self: flex-end;
    margin-left: 0;
  }
  
  .header-text h2 {
    font-size: 1.5rem;
  }
}
</style> 