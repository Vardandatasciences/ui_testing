<template>
  <div class="risk-instance-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <div class="risk-instance-card">
      <div class="risk-instance-header">
        <h2>Create Risk Instance</h2>
      </div>
      
      <!-- Updated validation error summary with encoding -->
      <div v-if="activeValidationErrors.length > 0" class="validation-error-summary">
        <h4>Please fix the following errors:</h4>
        <ul>
          <li v-for="error in activeValidationErrors" :key="error.field">
            {{ encodeForHTML(error.error) }}
          </li>
        </ul>
      </div>
      
      <form @submit.prevent="submitInstance" class="risk-instance-form">
        <div class="form-group field-full" :class="{ 'has-error': validationErrors.RiskId }">
          <label for="riskId"><i class="fas fa-id-badge"></i> Risk ID</label>
          <div class="risk-instance-dropdown-container">
            <input 
              type="text" 
              id="riskId" 
              v-model="selectedRiskIdText" 
              placeholder="Enter or select risk ID"
              @focus="showRiskDropdown = true"
              readonly
              :class="{ 'invalid': validationErrors.RiskId }"
            >
            <button type="button" class="risk-instance-dropdown-toggle" @click="toggleRiskDropdown">
              <i class="fas fa-chevron-down"></i>
            </button>
            
            <div v-if="showRiskDropdown" class="risk-instance-dropdown">
              <div class="risk-instance-dropdown-search">
                <input 
                  type="text" 
                  v-model="riskSearchQuery" 
                  placeholder="Search risks..." 
                  @input="filterRisks"
                  @click.stop
                >
              </div>
              <div class="risk-instance-dropdown-list" v-if="loadingRisks">
                <div class="loading-spinner">Loading risks...</div>
              </div>
              <div class="risk-instance-dropdown-list" v-else-if="filteredRisks.length === 0">
                <div class="no-results">No risks found</div>
              </div>
              <div class="risk-instance-dropdown-list" v-else>
                <div 
                  v-for="risk in validFilteredRisks" 
                  :key="risk.RiskId" 
                  class="risk-instance-item"
                  @click="selectRisk(risk)"
                >
                  <div class="risk-instance-item-checkbox">
                    <input 
                      type="checkbox" 
                      :id="'risk-' + risk.RiskId" 
                      :checked="newInstance.RiskId === risk.RiskId"
                      @click.stop="selectRisk(risk)"
                    >
                  </div>
                  <div class="risk-instance-item-content">
                    <div class="risk-instance-item-header">
                      <span class="risk-instance-id">ID: {{ risk.RiskId }}</span>
                      <span :class="'risk-instance-criticality ' + (risk.Criticality || 'unknown').toLowerCase()">
                        {{ encodeForHTML(risk.Criticality || 'Unknown') }}
                      </span>
                      <span class="risk-instance-category">
                        {{ encodeForHTML(risk.Category || 'No Category') }}
                      </span>
                    </div>
                    <div class="risk-instance-item-title">
                      {{ encodeForHTML(risk.RiskTitle || 'No Title') }}
                    </div>
                    <div class="risk-instance-item-description">
                      {{ truncateText(risk.RiskDescription, 100) }}
                    </div>
                    <div v-if="risk.PossibleDamage" class="risk-instance-item-damage">
                      <strong>Possible Damage:</strong> {{ truncateText(risk.PossibleDamage, 80) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <span v-if="validationErrors.RiskId" class="validation-error-message">
            {{ encodeForHTML(validationErrors.RiskId) }}
          </span>
        </div>
        
        <div class="form-section">
          <div class="form-group" :class="{ 'has-error': validationErrors.Criticality }">
            <label for="criticality"><i class="fas fa-exclamation-triangle"></i> Criticality</label>
            <select 
              id="criticality" 
              class="priority-select" 
              v-model="newInstance.Criticality"
              @focus="handleFocus('criticality')"
              @blur="handleBlur('criticality')"
              :class="{ 'invalid': validationErrors.Criticality }"
            >
              <option value="">Select Criticality</option>
              <option v-for="criticality in validationRules.ALLOWED_CRITICALITY" 
                      :key="criticality" 
                      :value="criticality">{{ criticality }}</option>
            </select>
            <span v-if="validationErrors.Criticality" class="validation-error-message">
              {{ encodeForHTML(validationErrors.Criticality) }}
            </span>
          </div>
          
          <div class="form-group">
            <label for="category"><i class="fas fa-tag"></i> Category</label>
            <div class="risk-instance-category-container">
              <div class="risk-instance-category-dropdown">
                <div class="risk-instance-selected-category" @click="toggleCategoryDropdown">
                  <span v-if="!selectedCategory">Select Category</span>
                  <span v-else>{{ selectedCategory }}</span>
                  <i class="fas fa-chevron-down"></i>
                </div>
                <div v-if="showCategoryDropdown" class="risk-instance-category-options">
                  <div class="risk-instance-category-search">
                    <input 
                      type="text" 
                      v-model="categorySearch" 
                      placeholder="Search categories..."
                      @click.stop
                    >
                    <button type="button" class="risk-instance-add-category-btn" @click.stop.prevent="showAddCategoryModal = true">
                      <i class="fas fa-plus"></i> Add New
                    </button>
                  </div>
                  <div class="risk-instance-category-list">
                    <div 
                      v-for="category in filteredCategories" 
                      :key="category.id" 
                      class="risk-instance-category-item"
                      @click.stop="selectCategory(category)"
                    >
                      <input 
                        type="radio" 
                        :checked="selectedCategory === category.value"
                        @click.stop="selectCategory(category)"
                      >
                      <span>{{ category.value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.Appetite }">
            <label for="appetite"><i class="fas fa-balance-scale"></i> Appetite</label>
            <select 
              id="appetite" 
              v-model="newInstance.Appetite"
              @focus="handleFocus('appetite')"
              @blur="handleBlur('appetite')"
              @change="onAppetiteChange()"
              :class="{ 'invalid': validationErrors.Appetite }"
            >
              <option v-for="appetite in validationRules.ALLOWED_APPETITE" 
                      :key="appetite" 
                      :value="appetite">{{ appetite }}</option>
            </select>
            <span v-if="validationErrors.Appetite" class="validation-error-message">
              {{ encodeForHTML(validationErrors.Appetite) }}
            </span>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskLikelihood }">
            <label for="riskLikelihood"><i class="fas fa-chart-line"></i> Risk Likelihood</label>
            <input 
              type="number" 
              step="1" 
              :min="validationRules.RISK_LIKELIHOOD_RANGE.min" 
              :max="validationRules.RISK_LIKELIHOOD_RANGE.max" 
              id="riskLikelihood" 
              v-model.number="newInstance.RiskLikelihood" 
              :placeholder="`Enter value (${validationRules.RISK_LIKELIHOOD_RANGE.min}-${validationRules.RISK_LIKELIHOOD_RANGE.max})`"
              @focus="handleFocus('riskLikelihood')"
              @blur="handleBlur('riskLikelihood')"
              @input="calculateRiskExposureRating"
              :class="{ 'invalid': validationErrors.RiskLikelihood }"
            >
            <span v-if="validationErrors.RiskLikelihood" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskLikelihood) }}
            </span>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskImpact }">
            <label for="riskImpact"><i class="fas fa-bolt"></i> Risk Impact</label>
            <input 
              type="number" 
              step="1" 
              :min="validationRules.RISK_IMPACT_RANGE.min" 
              :max="validationRules.RISK_IMPACT_RANGE.max" 
              id="riskImpact" 
              v-model.number="newInstance.RiskImpact" 
              :placeholder="`Enter value (${validationRules.RISK_IMPACT_RANGE.min}-${validationRules.RISK_IMPACT_RANGE.max})`"
              @focus="handleFocus('riskImpact')"
              @blur="handleBlur('riskImpact')"
              @input="calculateRiskExposureRating"
              :class="{ 'invalid': validationErrors.RiskImpact }"
            >
            <span v-if="validationErrors.RiskImpact" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskImpact) }}
            </span>
          </div>
          
          <div class="form-group">
            <label for="riskExposureRating"><i class="fas fa-thermometer-half"></i> Risk Exposure Rating (Likelihood × Impact)</label>
            <input type="number" readonly id="riskExposureRating" v-model.number="newInstance.RiskExposureRating" class="readonly-input"
              @focus="handleFocus('riskExposureRating')"
              @blur="handleBlur('riskExposureRating')"
            >
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskPriority }">
            <label for="riskPriority"><i class="fas fa-flag"></i> Risk Priority</label>
            <select 
              id="riskPriority" 
              class="priority-select" 
              v-model="newInstance.RiskPriority"
              @focus="handleFocus('riskPriority')"
              @blur="handleBlur('riskPriority')"
              :class="{ 'invalid': validationErrors.RiskPriority }"
            >
              <option value="">Select Priority</option>
              <option v-for="priority in validationRules.ALLOWED_RISK_PRIORITY" 
                      :key="priority" 
                      :value="priority">{{ priority }}</option>
            </select>
            <span v-if="validationErrors.RiskPriority" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskPriority) }}
            </span>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskResponseType }">
            <label for="riskResponseType"><i class="fas fa-shield-alt"></i> Response Type</label>
            <select 
              id="riskResponseType" 
              v-model="newInstance.RiskResponseType"
              @focus="handleFocus('riskResponseType')"
              @blur="handleBlur('riskResponseType')"
              :class="{ 'invalid': validationErrors.RiskResponseType }"
            >
              <option value="">Select Response Type</option>
              <option v-for="type in validationRules.ALLOWED_RISK_RESPONSE_TYPE" 
                      :key="type" 
                      :value="type">{{ type }}</option>
            </select>
            <span v-if="validationErrors.RiskResponseType" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskResponseType) }}
            </span>
          </div>
          
          <div class="form-group">
            <label for="riskOwner"><i class="fas fa-user"></i> Risk Owner</label>
            <div class="risk-instance-user-dropdown-container">
              <input 
                type="text" 
                id="riskOwner" 
                v-model="selectedOwnerText" 
                placeholder="Select risk owner"
                @focus="showUserDropdown = true"
                readonly
              >
              <button type="button" class="risk-instance-dropdown-toggle" @click="toggleUserDropdown">
                <i class="fas fa-chevron-down"></i>
              </button>
              
              <div v-if="showUserDropdown" class="risk-instance-user-dropdown">
                <div class="risk-instance-user-dropdown-search">
                  <input 
                    type="text" 
                    v-model="userSearchQuery" 
                    placeholder="Search users..." 
                    @input="filterUsers"
                    @click.stop
                  >
                </div>
                <div class="risk-instance-user-dropdown-list" v-if="loadingUsers">
                  <div class="loading-spinner">Loading users...</div>
                </div>
                <div class="risk-instance-user-dropdown-list" v-else-if="filteredUsers.length === 0">
                  <div class="no-results">No users found</div>
                </div>
                <div class="risk-instance-user-dropdown-list" v-else>
                  <div 
                    v-for="user in filteredUsers" 
                    :key="user.UserId" 
                    class="risk-instance-user-item"
                    @click="selectUser(user)"
                  >
                    <div class="risk-instance-user-item-checkbox">
                      <input 
                        type="checkbox" 
                        :id="'user-' + user.UserId" 
                        :checked="newInstance.RiskOwner === user.UserName"
                        @click.stop="selectUser(user)"
                      >
                    </div>
                    <div class="risk-instance-user-item-content">
                      <div class="risk-instance-user-item-name">{{ user.UserName }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="riskStatus"><i class="fas fa-info-circle"></i> Risk Status</label>
            <select id="riskStatus" v-model="newInstance.RiskStatus"
              @focus="handleFocus('riskStatus')"
              @blur="handleBlur('riskStatus')"
            >
              <option value="Not Assigned">Not Assigned</option>
              <option value="Assigned">Assigned</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskTitle }">
            <label for="riskTitle"><i class="fas fa-heading"></i> Risk Title</label>
            <input 
              type="text" 
              id="riskTitle" 
              v-model="newInstance.RiskTitle" 
              placeholder="Enter risk title"
              :class="{ 'invalid': validationErrors.RiskTitle }"
              @focus="handleFocus('riskTitle')"
              @blur="handleBlur('riskTitle')"
            >
            <span v-if="validationErrors.RiskTitle" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskTitle) }}
            </span>
          </div>
          
          <div class="form-group">
            <label for="businessImpact"><i class="fas fa-briefcase"></i> Business Impact</label>
            <div class="risk-instance-business-impact-container">
              <div class="risk-instance-business-impact-dropdown">
                <div class="risk-instance-selected-impacts" @click="toggleBusinessImpactDropdown">
                  <span v-if="selectedBusinessImpacts.length === 0">Select Business Impacts</span>
                  <span v-else>{{ selectedBusinessImpacts.length }} impact(s) selected</span>
                  <i class="fas fa-chevron-down"></i>
                </div>
                <div v-if="showBusinessImpactDropdown" class="risk-instance-business-impact-options">
                  <div class="risk-instance-business-impact-header">
                    <div class="risk-instance-business-impact-search">
                      <input 
                        type="text" 
                        v-model="businessImpactSearch" 
                        placeholder="Search impacts..."
                        @click.stop
                      >
                      <button type="button" class="risk-instance-add-impact-btn" @click.stop.prevent="showAddImpactModal = true">
                        <i class="fas fa-plus"></i> Add New
                      </button>
                    </div>
                  </div>
                  <div class="risk-instance-business-impact-list">
                    <div 
                      v-for="impact in filteredBusinessImpacts" 
                      :key="impact.id" 
                      class="risk-instance-business-impact-item"
                      @click.stop="toggleBusinessImpact(impact)"
                    >
                      <input 
                        type="checkbox" 
                        :checked="isBusinessImpactSelected(impact)"
                        @click.stop="toggleBusinessImpact(impact)"
                      >
                      <span>{{ impact.value }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="risk-instance-selected-impacts-display">
                <div 
                  v-for="impact in selectedBusinessImpacts" 
                  :key="impact.id" 
                  class="risk-instance-selected-impact-tag"
                >
                  {{ encodeForHTML(impact.value) }}
                  <i class="fas fa-times" @click="toggleBusinessImpact(impact)"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Add Business Impact Modal -->
          <div v-if="showAddImpactModal" class="risk-instance-modal-overlay" @click.self="showAddImpactModal = false">
            <div class="risk-instance-modal-content" @click.stop>
              <h3>Add New Business Impact</h3>
              <form @submit.prevent="addNewBusinessImpact" class="risk-instance-modal-form">
                <div class="risk-instance-modal-form-group">
                  <label>Impact Description</label>
                  <input 
                    type="text" 
                    v-model="newBusinessImpact" 
                    placeholder="Enter new business impact"
                    @keyup.enter.prevent="addNewBusinessImpact"
                    autofocus
                  >
                </div>
                <div class="risk-instance-modal-actions">
                  <button type="button" class="risk-instance-cancel-btn" @click.prevent="showAddImpactModal = false">Cancel</button>
                  <button type="submit" class="risk-instance-add-btn" :disabled="!newBusinessImpact.trim()">
                    Add
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Add Category Modal -->
          <div v-if="showAddCategoryModal" class="risk-instance-modal-overlay" @click.self="showAddCategoryModal = false">
            <div class="risk-instance-modal-content" @click.stop>
              <h3>Add New Category</h3>
              <form @submit.prevent="addNewCategory" class="risk-instance-modal-form">
                <div class="risk-instance-modal-form-group">
                  <label>Category Name</label>
                  <input 
                    type="text" 
                    v-model="newCategory" 
                    placeholder="Enter new category"
                    @keyup.enter.prevent="addNewCategory"
                    autofocus
                  >
                </div>
                <div class="risk-instance-modal-actions">
                  <button type="button" class="risk-instance-cancel-btn" @click.prevent="showAddCategoryModal = false">Cancel</button>
                  <button type="submit" class="risk-instance-add-btn" :disabled="!newCategory.trim()">
                    Add Category
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.Origin }">
            <label for="origin"><i class="fas fa-globe"></i> Origin</label>
            <select 
              id="origin" 
              v-model="newInstance.Origin" 
              class="risk-scoring-form-select"
              @focus="handleFocus('origin')"
              @blur="handleBlur('origin')"
              :class="{ 'invalid': validationErrors.Origin }"
            >
              <option value="">Select Origin</option>
              <option v-for="origin in validationRules.ALLOWED_ORIGIN" 
                      :key="origin" 
                      :value="origin">{{ origin }}</option>
            </select>
            <span v-if="validationErrors.Origin" class="validation-error-message">
              {{ encodeForHTML(validationErrors.Origin) }}
            </span>
          </div>
          
          <div class="form-group">
            <label for="complianceId"><i class="fas fa-hashtag"></i> Compliance ID</label>
            <div class="risk-instance-compliance-dropdown-container">
              <input 
                type="text" 
                id="complianceId" 
                v-model="selectedComplianceIdText" 
                placeholder="Enter or select compliance ID"
                @focus="showComplianceDropdown = true"
                readonly
              >
              <button type="button" class="risk-instance-dropdown-toggle" @click="toggleComplianceDropdown">
                <i class="fas fa-chevron-down"></i>
              </button>
              
              <div v-if="showComplianceDropdown" class="risk-instance-compliance-dropdown">
                <div class="risk-instance-compliance-dropdown-search">
                  <input 
                    type="text" 
                    v-model="complianceSearchQuery" 
                    placeholder="Search compliances..." 
                    @input="filterCompliances"
                    @click.stop
                  >
                </div>
                <div class="risk-instance-compliance-dropdown-list" v-if="loadingCompliances">
                  <div class="loading-spinner">Loading compliances...</div>
                </div>
                <div class="risk-instance-compliance-dropdown-list" v-else-if="filteredCompliances.length === 0">
                  <div class="no-results">No compliances found</div>
                </div>
                <div class="risk-instance-compliance-dropdown-list" v-else>
                  <div 
                    v-for="compliance in filteredCompliances" 
                    :key="compliance.ComplianceId" 
                    class="risk-instance-compliance-item"
                    @click="selectCompliance(compliance)"
                  >
                    <div class="risk-instance-compliance-item-checkbox">
                      <input 
                        type="checkbox" 
                        :id="'compliance-' + compliance.ComplianceId" 
                        :checked="newInstance.ComplianceId === compliance.ComplianceId"
                        @click.stop="selectCompliance(compliance)"
                      >
                    </div>
                    <div class="risk-instance-compliance-item-content">
                      <div class="risk-instance-compliance-item-header">
                        <span class="risk-instance-compliance-id">ID: {{ compliance.ComplianceId }}</span>
                        <span :class="'risk-instance-compliance-criticality ' + (compliance.Criticality ? compliance.Criticality.toLowerCase() : '')">
                          {{ encodeForHTML(compliance.Criticality || 'No Criticality') }}
                        </span>
                      </div>
                      <div class="risk-instance-compliance-item-description">
                        {{ truncateText(compliance.ComplianceItemDescription, 100) || 'No description available' }}
                      </div>
                      <div v-if="compliance.PossibleDamage" class="risk-instance-compliance-item-damage">
                        <strong>Possible Damage:</strong> {{ truncateText(compliance.PossibleDamage, 80) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group" :class="{ 'has-error': validationErrors.RiskType }">
            <label for="riskType"><i class="fas fa-cubes"></i> Risk Type</label>
            <select 
              id="riskType" 
              v-model="newInstance.RiskType"
              @focus="handleFocus('riskType')"
              @blur="handleBlur('riskType')"
              :class="{ 'invalid': validationErrors.RiskType }"
            >
              <option v-for="type in validationRules.ALLOWED_RISK_TYPE" 
                      :key="type" 
                      :value="type">{{ type }}</option>
            </select>
            <span v-if="validationErrors.RiskType" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskType) }}
            </span>
          </div>
        </div>
        
        <div class="form-section text-areas-section">
          <div class="form-group field-full" :class="{ 'has-error': validationErrors.RiskDescription }">
            <label for="riskDescription"><i class="fas fa-align-left"></i> Risk Description</label>
            <textarea 
              id="riskDescription" 
              v-model="newInstance.RiskDescription" 
              placeholder="Describe the risk..."
              rows="3"
              :class="{ 'invalid': validationErrors.RiskDescription }"
              @focus="handleFocus('riskDescription')"
              @blur="handleBlur('riskDescription')"
            ></textarea>
            <span v-if="validationErrors.RiskDescription" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskDescription) }}
            </span>
          </div>
          
          <div class="form-group field-full" :class="{ 'has-error': validationErrors.PossibleDamage }">
            <label for="possibleDamage"><i class="fas fa-exclamation-circle"></i> Possible Damage</label>
            <textarea 
              id="possibleDamage" 
              v-model="newInstance.PossibleDamage" 
              placeholder="Describe possible damage..."
              rows="2"
              :class="{ 'invalid': validationErrors.PossibleDamage }"
              @focus="handleFocus('possibleDamage')"
              @blur="handleBlur('possibleDamage')"
            ></textarea>
            <span v-if="validationErrors.PossibleDamage" class="validation-error-message">
              {{ encodeForHTML(validationErrors.PossibleDamage) }}
            </span>
          </div>
          
          <div class="form-group field-full" :class="{ 'has-error': validationErrors.RiskResponseDescription }">
            <label for="riskResponseDescription"><i class="fas fa-reply"></i> Response Description</label>
            <textarea 
              id="riskResponseDescription" 
              v-model="newInstance.RiskResponseDescription" 
              placeholder="Describe the response strategy..."
              rows="2"
              :class="{ 'invalid': validationErrors.RiskResponseDescription }"
              @focus="handleFocus('riskResponseDescription')"
              @blur="handleBlur('riskResponseDescription')"
            ></textarea>
            <span v-if="validationErrors.RiskResponseDescription" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskResponseDescription) }}
            </span>
          </div>
          
          <div class="form-group field-full" :class="{ 'has-error': validationErrors.RiskMitigation }">
            <label for="riskMitigation"><i class="fas fa-shield-virus"></i> Risk Mitigation</label>
            <textarea 
              id="riskMitigation" 
              v-model="newInstance.RiskMitigation" 
              placeholder="Describe mitigation actions..."
              rows="2"
              :class="{ 'invalid': validationErrors.RiskMitigation }"
              @focus="handleFocus('riskMitigation')"
              @blur="handleBlur('riskMitigation')"
            ></textarea>
            <span v-if="validationErrors.RiskMitigation" class="validation-error-message">
              {{ encodeForHTML(validationErrors.RiskMitigation) }}
            </span>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="risk-instance-btn-cancel" @click="resetForm">Clear</button>
          <button type="submit" class="risk-instance-btn-submit">Create</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'CreateRiskInstance',
  components: {
    PopupModal
  },
  props: {
    riskId: {
      type: [String, Number],
      default: null
    },
    incidentId: {
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      validationRules: {
        ALLOWED_CRITICALITY: ['Critical', 'High', 'Medium', 'Low'],
        ALLOWED_RISK_PRIORITY: ['High', 'Medium', 'Low'],
        ALLOWED_ORIGIN: ['Manual', 'SIEM', 'AuditFindings'],
        ALLOWED_RISK_TYPE: ['Current', 'Residual', 'Inherent', 'Emerging', 'Accept'],
        ALLOWED_APPETITE: ['Yes', 'No'],
        ALLOWED_RISK_RESPONSE_TYPE: ['Mitigate', 'Avoid', 'Accept', 'Transfer'],
        RISK_LIKELIHOOD_RANGE: { min: 1, max: 10 },
        RISK_IMPACT_RANGE: { min: 1, max: 10 },
        TEXT_PATTERN: /^[A-Za-z0-9\s.,;:!?'"()\-_[\]]{0,}$/
      },
      validationErrors: {
        Criticality: '',
        RiskPriority: '',
        Origin: '',
        RiskType: '',
        Appetite: '',
        RiskResponseType: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskTitle: '',
        RiskDescription: '',
        PossibleDamage: '',
        RiskResponseDescription: '',
        RiskMitigation: ''
      },
      newInstance: {
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: 'Yes',
        RiskDescription: '',
        RiskLikelihood: 1,
        RiskImpact: 1,
        RiskExposureRating: 1,
        RiskPriority: '',
        RiskResponseType: 'Mitigation',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Not Assigned',
        UserId: 1,
        RiskId: null,
        IncidentId: null,
        RiskTitle: '',
        BusinessImpact: '',
        Origin: '',
        MitigationDueDate: null,
        MitigationStatus: null,
        MitigationCompletedDate: null,
        ReviewerCount: null,
        RecurrenceCount: 1,
        RiskFormDetails: null,
        ModifiedMitigations: null,
        ComplianceId: '',
        RiskType: 'Current'
      },
      businessImpacts: [],
      selectedBusinessImpacts: [],
      showBusinessImpactDropdown: false,
      businessImpactSearch: '',
      showAddImpactModal: false,
      newBusinessImpact: '',

      // Category dropdown properties
      categories: [],
      selectedCategory: '',
      showCategoryDropdown: false,
      categorySearch: '',
      showAddCategoryModal: false,
      newCategory: '',
      // Existing properties
      risks: [],
      filteredRisks: [],
      riskSearchQuery: '',
      showRiskDropdown: false,
      loadingRisks: false,
      selectedRiskIdText: '',
      
      isDebugging: false,
      testResults: [],
      selectedOwnerText: '',
      showUserDropdown: false,
      loadingUsers: false,
      userSearchQuery: '',
      filteredUsers: [],
      users: [],
      selectedComplianceIdText: '',
      showComplianceDropdown: false,
      loadingCompliances: false,
      complianceSearchQuery: '',
      filteredCompliances: [],
      compliances: []
    }
  },
  computed: {
    validFilteredRisks() {
      return this.filteredRisks.filter(risk => risk && risk.RiskId);
    },
    filteredBusinessImpacts() {
      if (!this.businessImpactSearch) {
        return this.businessImpacts;
      }
      const search = this.businessImpactSearch.toLowerCase();
      return this.businessImpacts.filter(impact => 
        impact.value.toLowerCase().includes(search)
      );
    },
    filteredCategories() {
      if (!this.categorySearch) {
        return this.categories;
      }
      const search = this.categorySearch.toLowerCase();
      return this.categories.filter(category => 
        category.value.toLowerCase().includes(search)
      );
    },
    activeValidationErrors() {
      return Object.entries(this.validationErrors)
        .filter(entry => entry[1])
        .map(([field, error]) => ({
          field,
          error
        }));
    }
  },
  mounted() {
    // Initialize Risk Exposure Rating
    this.calculateRiskExposureRating();
    
    // Always prefer props, but fallback to route query if not set
    if (this.riskId !== null && this.riskId !== undefined) {
      this.newInstance.RiskId = this.riskId;
      this.updateSelectedRiskIdText();
    } else if (this.$route.query.riskId) {
      this.newInstance.RiskId = this.$route.query.riskId;
      this.updateSelectedRiskIdText();
    }

    if (this.incidentId !== null && this.incidentId !== undefined) {
      this.newInstance.IncidentId = this.incidentId;
    } else if (this.$route.query.incidentId) {
      this.newInstance.IncidentId = this.$route.query.incidentId;
    }

    // Fetch data from API
    this.fetchRisks();
    this.fetchUsers();
    this.fetchCompliances();
    this.fetchBusinessImpacts();
    this.fetchCategories();

    // Add click event listener to close dropdowns when clicking outside
    document.addEventListener('click', this.closeRiskDropdown);
    document.addEventListener('click', this.closeUserDropdown);
    document.addEventListener('click', this.closeComplianceDropdown);
    document.addEventListener('click', this.closeBusinessImpactDropdown);

    // Optionally, log for debugging
    console.log('CreateRiskInstance mounted with:', {
      riskId: this.newInstance.RiskId,
      incidentId: this.newInstance.IncidentId
    });
  },
  beforeUnmount() {
    // Remove event listeners when component is unmounted
    document.removeEventListener('click', this.closeRiskDropdown);
    document.removeEventListener('click', this.closeUserDropdown);
    document.removeEventListener('click', this.closeComplianceDropdown);
    document.removeEventListener('click', this.closeBusinessImpactDropdown);
  },
  methods: {
    fetchRisks() {
      this.loadingRisks = true;
      
      // API endpoint for fetching risks for dropdown
      const API_ENDPOINT = 'http://127.0.0.1:8000/api/risks-for-dropdown/';
      
      fetch(API_ENDPOINT)
        .then(response => {
          if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          // Filter out any invalid risk objects
          this.risks = (data || []).filter(risk => risk && risk.RiskId);
          this.filteredRisks = [...this.risks];
          this.loadingRisks = false;
          
          // If a risk ID is already selected, update the text
          if (this.newInstance.RiskId) {
            this.updateSelectedRiskIdText();
          }
        })
        .catch(error => {
          console.error('Error fetching risks:', error);
          this.loadingRisks = false;
          this.risks = [];
          this.filteredRisks = [];
        });
    },
    filterRisks() {
      if (!this.riskSearchQuery) {
        this.filteredRisks = [...this.risks].filter(risk => risk && risk.RiskId);
        return;
      }
      
      const query = this.sanitizeHTML(this.riskSearchQuery.toLowerCase());
      this.filteredRisks = this.risks.filter(risk => 
        risk && risk.RiskId && (
          (risk.RiskId && risk.RiskId.toString().includes(query)) ||
          (risk.RiskTitle && this.sanitizeHTML(risk.RiskTitle.toLowerCase()).includes(query)) ||
          (risk.Category && this.sanitizeHTML(risk.Category.toLowerCase()).includes(query)) ||
          (risk.RiskDescription && this.sanitizeHTML(risk.RiskDescription.toLowerCase()).includes(query))
        )
      );
    },
    selectRisk(risk) {
      this.newInstance.RiskId = risk.RiskId;
      this.selectedRiskIdText = `Risk ID: ${risk.RiskId}`;
      this.showRiskDropdown = false;
      
      // Optionally pre-fill other fields based on the selected risk
      if (risk.RiskTitle) this.newInstance.RiskTitle = risk.RiskTitle;
      if (risk.Criticality) this.newInstance.Criticality = risk.Criticality;
      if (risk.Category) this.newInstance.Category = risk.Category;
      if (risk.PossibleDamage) this.newInstance.PossibleDamage = risk.PossibleDamage;
      if (risk.RiskDescription) this.newInstance.RiskDescription = risk.RiskDescription;
    },
    toggleRiskDropdown() {
      this.showRiskDropdown = !this.showRiskDropdown;
      if (this.showRiskDropdown) {
        this.riskSearchQuery = '';
        this.filterRisks();
      }
    },
    closeRiskDropdown(event) {
      // Check if the click was outside the dropdown
      const dropdown = document.querySelector('.risk-instance-dropdown-container');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showRiskDropdown = false;
      }
    },
    updateSelectedRiskIdText() {
      if (this.newInstance.RiskId) {
        const selectedRisk = this.risks.find(risk => risk.RiskId === parseInt(this.newInstance.RiskId));
        if (selectedRisk) {
          this.selectedRiskIdText = `Risk ID: ${selectedRisk.RiskId}`;
        } else {
          this.selectedRiskIdText = `Risk ID: ${this.newInstance.RiskId}`;
        }
      } else {
        this.selectedRiskIdText = '';
      }
    },
    truncateText(text, maxLength) {
      if (!text) return '';
      const sanitizedText = this.sanitizeHTML(text);
      return sanitizedText.length > maxLength ? sanitizedText.substring(0, maxLength) + '...' : sanitizedText;
    },
    calculateRiskExposureRating() {
      // Get the current values of RiskLikelihood and RiskImpact
      const likelihood = parseInt(this.newInstance.RiskLikelihood) || 0;
      const impact = parseInt(this.newInstance.RiskImpact) || 0;
      
      // Calculate the Risk Exposure Rating as the product
      // Only set a value if both likelihood and impact are provided
      if (likelihood > 0 && impact > 0) {
        this.newInstance.RiskExposureRating = likelihood * impact;
      } else {
        this.newInstance.RiskExposureRating = null;
      }
    },
    onAppetiteChange() {
      // When Appetite changes to No, update RiskStatus to Rejected
      if (this.newInstance.Appetite === 'No') {
        this.newInstance.RiskStatus = 'Rejected';
        console.log('Appetite set to No: Updated RiskStatus to Rejected');
      }
    },
    testBackendConnection() {
      this.isDebugging = true;
      this.testResults = [];
      
      const endpoints = [
        'http://127.0.0.1:8000/api/risk-instances/', // Confirmed working endpoint (highest priority)
        'http://localhost:8000/api/risk-instances/',
        'http://localhost:8080/api/risk-instances/',
        'http://localhost:8080/risk-instances/',
        'http://127.0.0.1:8000/risk-instances/',
        'http://localhost:8000/risk-instances/'
      ];
      
      this.testResults.push('Testing API endpoints in order of priority...');
      this.testResults.push(`Primary endpoint: ${endpoints[0]} (confirmed working in browser)`);
      
      const testEndpoint = (index) => {
        if (index >= endpoints.length) {
          // Testing complete
          this.testResults.push('All tests completed.');
          return;
        }
        
        const endpoint = endpoints[index];
        this.testResults.push(`Testing: ${endpoint}`);
        
        fetch(endpoint, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => {
          if (!response.ok) {
            return response.text().then(() => {
              this.testResults.push(`❌ ${endpoint} - Status: ${response.status}`);
              // Continue testing the next endpoint
              testEndpoint(index + 1);
            });
          }
          return response.json().then((data) => {
            this.testResults.push(`✅ ${endpoint} - Connected successfully`);
            this.testResults.push(`Found ${data.length || 0} risk instances in the database`);
            testEndpoint(index + 1);
          });
        })
        .catch(error => {
          this.testResults.push(`❌ ${endpoint} - Error: ${error.message}`);
          testEndpoint(index + 1);
        });
      };
      
      // Start testing endpoints
      testEndpoint(0);
    },
    validateChoiceField(value, fieldName, allowedValues) {
      if (!value) {
        this.validationErrors[fieldName] = `${fieldName} is required`;
        return false;
      }
      if (!allowedValues.includes(value)) {
        this.validationErrors[fieldName] = `Invalid ${fieldName}. Must be one of: ${allowedValues.join(', ')}`;
        return false;
      }
      this.validationErrors[fieldName] = '';
      return true;
    },

    validateNumericField(value, fieldName, min, max) {
      const numValue = parseInt(value);
      if (isNaN(numValue)) {
        this.validationErrors[fieldName] = `${fieldName} must be a number`;
        return false;
      }
      if (numValue < min || numValue > max) {
        this.validationErrors[fieldName] = `${fieldName} must be between ${min} and ${max}`;
        return false;
      }
      this.validationErrors[fieldName] = '';
      return true;
    },

    validateTextField(value, fieldName, required = false) {
      const sanitizedValue = this.sanitizeHTML(value);
      if (!sanitizedValue && required) {
        this.validationErrors[fieldName] = `${fieldName} is required`;
        return false;
      }
      if (sanitizedValue && !this.validationRules.TEXT_PATTERN.test(sanitizedValue)) {
        this.validationErrors[fieldName] = `${fieldName} contains invalid characters`;
        return false;
      }
      this.validationErrors[fieldName] = '';
      return true;
    },

    validateForm() {
      let isValid = true;

      // Validate choice fields
      isValid = this.validateChoiceField(this.newInstance.Criticality, 'Criticality', this.validationRules.ALLOWED_CRITICALITY) && isValid;
      isValid = this.validateChoiceField(this.newInstance.RiskPriority, 'RiskPriority', this.validationRules.ALLOWED_RISK_PRIORITY) && isValid;
      isValid = this.validateChoiceField(this.newInstance.Origin, 'Origin', this.validationRules.ALLOWED_ORIGIN) && isValid;
      isValid = this.validateChoiceField(this.newInstance.RiskType, 'RiskType', this.validationRules.ALLOWED_RISK_TYPE) && isValid;
      isValid = this.validateChoiceField(this.newInstance.Appetite, 'Appetite', this.validationRules.ALLOWED_APPETITE) && isValid;
      isValid = this.validateChoiceField(this.newInstance.RiskResponseType, 'RiskResponseType', this.validationRules.ALLOWED_RISK_RESPONSE_TYPE) && isValid;

      // Validate numeric fields
      isValid = this.validateNumericField(this.newInstance.RiskLikelihood, 'RiskLikelihood', 
        this.validationRules.RISK_LIKELIHOOD_RANGE.min, this.validationRules.RISK_LIKELIHOOD_RANGE.max) && isValid;
      isValid = this.validateNumericField(this.newInstance.RiskImpact, 'RiskImpact',
        this.validationRules.RISK_IMPACT_RANGE.min, this.validationRules.RISK_IMPACT_RANGE.max) && isValid;

      // Validate text fields
      isValid = this.validateTextField(this.newInstance.RiskTitle, 'RiskTitle', true) && isValid;
      isValid = this.validateTextField(this.newInstance.RiskDescription, 'RiskDescription', true) && isValid;
      isValid = this.validateTextField(this.newInstance.PossibleDamage, 'PossibleDamage', false) && isValid;
      isValid = this.validateTextField(this.newInstance.RiskResponseDescription, 'RiskResponseDescription', false) && isValid;
      isValid = this.validateTextField(this.newInstance.RiskMitigation, 'RiskMitigation', false) && isValid;

      return isValid;
    },

    submitInstance() {
      // Clear all previous validation errors
      Object.keys(this.validationErrors).forEach(key => {
        this.validationErrors[key] = '';
      });

      // Validate form before submission
      if (!this.validateForm()) {
        console.error('Form validation failed', this.validationErrors);
        // Show validation errors to user
        this.$nextTick(() => {
          const firstErrorField = Object.keys(this.validationErrors).find(key => this.validationErrors[key]);
          if (firstErrorField) {
            const element = document.getElementById(firstErrorField.toLowerCase());
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'center' });
              element.focus();
            }
          }
        });
        return;
      }

      try {
        this.submitRiskInstance();
      } catch (error) {
        console.error('Error submitting form:', error);
      }
    },
    submitRiskInstance() {
      const submissionData = {};
      
      // Sanitize all string values before submission
      Object.keys(this.newInstance).forEach(key => {
        if (this.newInstance[key] !== '' && this.newInstance[key] !== null) {
          if (typeof this.newInstance[key] === 'string') {
            submissionData[key] = this.sanitizeHTML(this.newInstance[key]);
          } else {
            submissionData[key] = this.newInstance[key];
          }
        }
      });
      
      // Handle business impact specially
      if (this.selectedBusinessImpacts.length > 0) {
        submissionData.BusinessImpact = this.selectedBusinessImpacts
          .map(i => this.sanitizeHTML(i.value))
          .join(', ');
      }
      
      // Set RiskOwner if available
      if (this.selectedOwnerText) {
        submissionData.RiskOwner = this.sanitizeHTML(this.selectedOwnerText);
      }

      // Set MitigationStatus to null instead of an invalid value
      if (!submissionData.MitigationStatus || submissionData.MitigationStatus === 'Not Started') {
        submissionData.MitigationStatus = null;
      }
      
      // Use axios with proper content-type and CSRF token if applicable
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      
      const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      };
      
      if (csrfToken) {
        headers['X-CSRF-TOKEN'] = csrfToken;
      }

      axios.post('http://localhost:8000/api/risk-instances/', submissionData, { headers })
        .then(response => {
          console.log('Risk instance created successfully:', response.data);
          this.$popup.success('Risk instance created successfully!');
          this.resetForm();
        })
        .catch(error => {
          console.error('Error creating risk instance:', error);
          let errorMessage = 'Unknown error occurred';
          
          if (error.response && error.response.data) {
            if (error.response.data.error) {
              errorMessage = error.response.data.error;
            } else if (error.response.data.message) {
              errorMessage = error.response.data.message;
            } else if (typeof error.response.data === 'string') {
              errorMessage = error.response.data;
            } else {
              errorMessage = JSON.stringify(error.response.data);
            }
          } else if (error.message) {
            errorMessage = error.message;
          }
          
          this.$popup.error('Error: ' + errorMessage);
        });
    },
    resetForm() {
      this.newInstance = {
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: 'Yes',
        RiskDescription: '',
        RiskLikelihood: 1,
        RiskImpact: 1,
        RiskExposureRating: 1,
        RiskPriority: '',
        RiskResponseType: 'Mitigation',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Not Assigned',
        UserId: 1,
        RiskId: null,
        IncidentId: null,
        RiskTitle: '',
        BusinessImpact: '',
        Origin: '',
        MitigationDueDate: null,
        MitigationStatus: null,
        MitigationCompletedDate: null,
        ReviewerCount: null,
        RecurrenceCount: 1,
        RiskFormDetails: null,
        ModifiedMitigations: null,
        ComplianceId: '',
        RiskType: 'Current'
      };
      
      // Reset other form-related data
      this.selectedRiskIdText = '';
      this.selectedOwnerText = '';
      this.selectedComplianceIdText = '';
      this.selectedBusinessImpacts = [];
      this.showBusinessImpactDropdown = false;
      this.businessImpactSearch = '';
      this.showAddImpactModal = false;
      this.newBusinessImpact = '';
      
      // Reset category selection
      this.selectedCategory = '';
      
      this.calculateRiskExposureRating();
    },
    // Simplified focus/blur handlers without unused parameters
    handleFocus() {
      // Keep empty for now, might be needed for future functionality
    },
    handleBlur() {
      // Keep empty for now, might be needed for future functionality
    },
    fetchUsers() {
      this.loadingUsers = true;
      
      // API endpoint for fetching users for dropdown
      const API_ENDPOINT = 'http://127.0.0.1:8000/api/users-for-dropdown/';
      
      fetch(API_ENDPOINT)
        .then(response => {
          if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          this.users = data;
          this.filteredUsers = [...data];
          this.loadingUsers = false;
        })
        .catch(error => {
          console.error('Error fetching users:', error);
          this.loadingUsers = false;
          this.filteredUsers = [];
        });
    },
    filterUsers() {
      if (!this.userSearchQuery) {
        this.filteredUsers = [...this.users];
        return;
      }
      
      const query = this.sanitizeHTML(this.userSearchQuery.toLowerCase());
      this.filteredUsers = this.users.filter(user => 
        (user.UserName && user.UserName.toLowerCase().includes(query))
      );
    },
    selectUser(user) {
      this.selectedOwnerText = user.UserName;
      this.newInstance.RiskOwner = user.UserName;
      this.showUserDropdown = false;
      
      // Set the UserId field
      if (user.UserId) this.newInstance.UserId = user.UserId;
    },
    toggleUserDropdown() {
      this.showUserDropdown = !this.showUserDropdown;
      if (this.showUserDropdown) {
        this.userSearchQuery = '';
        this.fetchUsers();
      }
    },
    closeUserDropdown(event) {
      // Check if the click was outside the dropdown
      const dropdown = document.querySelector('.risk-instance-user-dropdown-container');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showUserDropdown = false;
      }
    },
    fetchCompliances() {
      this.loadingCompliances = true;
      
      // API endpoint for fetching compliances for dropdown
      const API_ENDPOINT = 'http://127.0.0.1:8000/api/compliances-for-dropdown/';
      
      fetch(API_ENDPOINT)
        .then(response => {
          if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          this.compliances = data;
          this.filteredCompliances = [...data];
          this.loadingCompliances = false;
        })
        .catch(error => {
          console.error('Error fetching compliances:', error);
          this.loadingCompliances = false;
          this.compliances = [];
          this.filteredCompliances = [];
        });
    },
    filterCompliances() {
      if (!this.complianceSearchQuery) {
        this.filteredCompliances = [...this.compliances];
        return;
      }
      
      const query = this.sanitizeHTML(this.complianceSearchQuery.toLowerCase());
      this.filteredCompliances = this.compliances.filter(compliance => 
        (compliance.ComplianceId && compliance.ComplianceId.toString().includes(query)) ||
        (compliance.ComplianceItemDescription && compliance.ComplianceItemDescription.toLowerCase().includes(query))
      );
    },
    selectCompliance(compliance) {
      this.selectedComplianceIdText = `Compliance ID: ${compliance.ComplianceId}`;
      this.showComplianceDropdown = false;
      
      // Optionally pre-fill other fields based on the selected compliance
      if (compliance.ComplianceItemDescription) this.newInstance.RiskDescription = compliance.ComplianceItemDescription;
      if (compliance.PossibleDamage) this.newInstance.PossibleDamage = compliance.PossibleDamage;
      if (compliance.ComplianceId) this.newInstance.ComplianceId = compliance.ComplianceId;
    },
    toggleComplianceDropdown() {
      this.showComplianceDropdown = !this.showComplianceDropdown;
      if (this.showComplianceDropdown) {
        this.complianceSearchQuery = '';
        this.fetchCompliances();
      }
    },
    closeComplianceDropdown(event) {
      // Check if the click was outside the dropdown
      const dropdown = document.querySelector('.risk-instance-compliance-dropdown-container');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showComplianceDropdown = false;
      }
    },
    // Business Impact Methods
    async fetchBusinessImpacts() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/business-impacts/');
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === 'success') {
          this.businessImpacts = data.data;
        }
      } catch (error) {
        console.error('Error fetching business impacts:', error);
      }
    },

    toggleBusinessImpactDropdown() {
      this.showBusinessImpactDropdown = !this.showBusinessImpactDropdown;
      if (this.showBusinessImpactDropdown) {
        this.businessImpactSearch = '';
        document.addEventListener('click', this.closeBusinessImpactDropdown);
      } else {
        document.removeEventListener('click', this.closeBusinessImpactDropdown);
      }
    },

    closeBusinessImpactDropdown(event) {
      const dropdown = document.querySelector('.risk-instance-business-impact-dropdown');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showBusinessImpactDropdown = false;
        document.removeEventListener('click', this.closeBusinessImpactDropdown);
      }
    },

    toggleBusinessImpact(impact) {
      const index = this.selectedBusinessImpacts.findIndex(i => i.id === impact.id);
      if (index === -1) {
        this.selectedBusinessImpacts.push(impact);
      } else {
        this.selectedBusinessImpacts.splice(index, 1);
      }
      this.newInstance.BusinessImpact = this.selectedBusinessImpacts.map(i => i.value).join(', ');
    },

    isBusinessImpactSelected(impact) {
      return this.selectedBusinessImpacts.some(i => i.id === impact.id);
    },

    async addNewBusinessImpact(event) {
      // Prevent default form submission
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      // Don't proceed if input is empty
      if (!this.newBusinessImpact.trim()) {
        return;
      }
      
      try {
        console.log('Adding new business impact:', this.newBusinessImpact);
        
        const response = await fetch('http://127.0.0.1:8000/api/business-impacts/add/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            value: this.newBusinessImpact.trim()
          })
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
          console.log('Successfully added business impact:', data.data);
          this.businessImpacts.push(data.data);
          this.toggleBusinessImpact(data.data);
          this.showAddImpactModal = false;
          this.newBusinessImpact = '';
        } else {
          throw new Error('Failed to add business impact: ' + (data.message || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error adding new business impact:', error);
        this.$popup.error('Failed to add new business impact: ' + error.message);
      }
    },

    // Category Methods
    async fetchCategories() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/risk-categories/');
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === 'success') {
          this.categories = data.data;
        }
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    },

    toggleCategoryDropdown() {
      this.showCategoryDropdown = !this.showCategoryDropdown;
      if (this.showCategoryDropdown) {
        this.categorySearch = '';
      }
    },

    selectCategory(category) {
      this.selectedCategory = category.value;
      this.newInstance.Category = category.value;
      this.showCategoryDropdown = false;
    },

    async addNewCategory(event) {
      // Prevent default form submission
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      // Don't proceed if input is empty
      if (!this.newCategory.trim()) {
        return;
      }
      
      try {
        console.log('Adding new category:', this.newCategory);
        
        const response = await fetch('http://127.0.0.1:8000/api/risk-categories/add/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            value: this.newCategory.trim()
          })
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
          console.log('Successfully added category:', data.data);
          this.categories.push(data.data);
          this.selectCategory(data.data);
          this.showAddCategoryModal = false;
          this.newCategory = '';
        } else {
          throw new Error('Failed to add category: ' + (data.message || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error adding new category:', error);
        this.$popup.error('Failed to add new category: ' + error.message);
      }
    },

    // Add sanitization utilities
    sanitizeHTML(value) {
      if (!value) return '';
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\\/g, '&#x5C;')
        .replace(/`/g, '&#x60;');
    },
    
    encodeForHTML(str) {
      return this.sanitizeHTML(str);
    },

    encodeForJavaScript(str) {
      if (!str) return '';
      return String(str)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/`/g, '\\`')
        .replace(/\//g, '\\/')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t')
        .replace(/\f/g, '\\f')
        .replace(/<\/script>/ig, '<\\/script>');
    }
  }
}
</script>

<style lang="css" scoped>
/* Import the CSS file */
@import url('./CreateRiskInstance.css');

/* Override any conflicting styles */
.risk-instance-container {
  padding: 20px !important;
  background: transparent !important;
  min-height: calc(100vh - 40px) !important;
  width: calc(100% - 250px) !important;
  box-sizing: border-box !important;
  position: relative !important;
  margin-left: 250px !important;
}

.risk-instance-card {
  background: transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 24px !important;
  width: 100% !important;
}

.risk-instance-header {
  margin-bottom: 24px !important;
}

.risk-instance-header h2 {
  color: var(--form-gray-900) !important;
  font-size: 1.8rem !important;
  font-weight: 600 !important;
  margin: 0 !important;
  padding-bottom: 8px !important;
}

.risk-instance-form {
  display: flex !important;
  flex-direction: column !important;
  gap: 24px !important;
}

.form-section {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr) !important;
  gap: 16px !important;
  width: 100% !important;
  background: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 0 !important;
}

.form-group {
  display: flex !important;
  flex-direction: column !important;
  gap: 2px !important;
  margin-bottom: 4px !important;
}

.form-group label {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: var(--form-gray-700) !important;
  margin-bottom: 3px !important;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 10px !important;
  border: 1px solid var(--form-gray-300) !important;
  border-left: 3px solid var(--form-primary) !important;
  border-radius: 6px !important;
  font-size: 0.85rem !important;
  font-family: inherit !important;
  resize: none !important;
  transition: all 0.3s ease !important;
  background-color: var(--form-gray-100) !important;
  width: 100% !important;
  box-sizing: border-box !important;
  height: 36px !important;
}

/* Ensure form actions are properly styled */
.form-actions {
  display: flex !important;
  justify-content: flex-end !important;
  gap: 15px !important;
  margin-top: 24px !important;
}

.risk-instance-btn-submit,
.risk-instance-btn-cancel {
  padding: 8px 24px !important;
  border-radius: 6px !important;
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
}

.risk-instance-btn-submit {
  background: var(--form-primary) !important;
  color: white !important;
  border: none !important;
}

.risk-instance-btn-cancel {
  background: white !important;
  color: var(--form-gray-700) !important;
  border: 1px solid var(--form-gray-300) !important;
}

/* Ensure dropdowns are properly styled */
.risk-instance-dropdown {
  position: absolute !important;
  z-index: 1000 !important;
}

/* Responsive design overrides */
@media (max-width: 1200px) {
  .form-section {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .form-section {
    grid-template-columns: 1fr !important;
  }
  
  .risk-instance-container {
    padding: 12px !important;
  }
}
</style>

