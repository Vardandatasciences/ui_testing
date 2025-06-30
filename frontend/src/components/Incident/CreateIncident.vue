<template>
  <div class="incident-form-page incident">
    <div class="incident-form-page-header">
      <h1 class="incident-form-page-title">Create New Incident</h1>
    </div>

    <div class="incident-form-box">
      <div class="incident-form-box-title">
        <i class="fas fa-file-alt"></i>
        Incident Details
      </div>

      <form @submit.prevent="validateAndSubmit" class="incident-create-form">
        <!-- Incident Title and Description Section -->
        <div class="incident-title-description-section">
          <div class="section-header">
            <h3><i class="fas fa-edit"></i>Incident Overview</h3>
            <button type="button" @click="generateAnalysis" class="generate-analysis-btn">
              <i class="fas fa-magic"></i> Generate Analysis
            </button>
          </div>
          
          <div class="title-description-fields">
            <label class="field-title required">
              <span><i class="fas fa-heading"></i>Incident Title</span>
              <input 
                type="text" 
                v-model="formData.IncidentTitle" 
                @input="validateIncidentTitle"
                @blur="validateIncidentTitle"
                placeholder="e.g., Data breach in customer database, System outage in payment processing..."
                title="Provide a clear, concise title that summarizes the incident"
                required 
              />
              <div v-if="validationErrors.IncidentTitle" class="validation-error">{{ validationErrors.IncidentTitle }}</div>
            </label>

            <label class="field-description required">
              <span><i class="fas fa-align-left"></i>Description</span>
              <textarea 
                v-model="formData.Description" 
                @input="validateDescription"
                @blur="validateDescription"
                placeholder="Describe what happened in detail: What was the nature of the incident? How was it discovered? What systems or processes were affected? Include timeline if known..."
                title="Provide a detailed description of what happened, including sequence of events"
                required
              ></textarea>
              <div v-if="validationErrors.Description" class="validation-error">{{ validationErrors.Description }}</div>
            </label>
          </div>
        </div>

        <!-- Basic Information Section -->
        <label class="field-third">
          <span><i class="fas fa-tag"></i>Origin</span>
          <select v-model="formData.Origin" @change="validateOrigin" title="Select how this incident was discovered or reported" required>
            <option value="">Select Origin</option>
            <option value="Manual">Manual</option>
            <option value="Audit Finding">Audit Finding</option>
            <option value="System Generated">System Generated</option>
          </select>
          <div v-if="validationErrors.Origin" class="validation-error">{{ validationErrors.Origin }}</div>
        </label>

        <label class="field-third required">
          <span><i class="fas fa-calendar"></i>Date</span>
          <input 
            type="date" 
            v-model="formData.Date" 
            @input="validateDate"
            @blur="validateDate"
            title="Date when the incident occurred or was discovered"
            required 
          />
          <div v-if="validationErrors.Date" class="validation-error">{{ validationErrors.Date }}</div>
        </label>

        <label class="field-third required">
          <span><i class="fas fa-clock"></i>Time</span>
          <input 
            type="time" 
            v-model="formData.Time" 
            @input="validateTime"
            @blur="validateTime"
            title="Time when the incident occurred or was discovered"
            required 
          />
          <div v-if="validationErrors.Time" class="validation-error">{{ validationErrors.Time }}</div>
        </label>
        
        <label class="field-third required">
          <span><i class="fas fa-exclamation-triangle"></i>Risk Priority</span>
          <select v-model="formData.RiskPriority" @change="validateRiskPriority" class="priority-select" title="Assess the severity level of this incident" required>
            <option value="">Select Priority</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <div v-if="validationErrors.RiskPriority" class="validation-error">{{ validationErrors.RiskPriority }}</div>
        </label>
        
        <!-- Risk and Impact Section -->
        <label class="field-third required">
          <span><i class="fas fa-shield-alt"></i>Risk Category</span>
          <div class="multi-select-dropdown">
            <div class="multi-select-input" @click="toggleCategoryDropdown">
              <div class="selected-items">
                <span v-if="selectedCategories.length === 0" class="placeholder">
                  Select categories or type to add new...
                </span>
                <span v-for="category in selectedCategories" :key="category" class="selected-item">
                  {{ category }}
                  <i class="fas fa-times" @click.stop="removeCategory(category)"></i>
                </span>
              </div>
              <i class="fas fa-chevron-down dropdown-arrow" :class="{ 'rotated': showCategoryDropdown }"></i>
            </div>
            <div v-if="showCategoryDropdown" class="dropdown-panel">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="categorySearchTerm" 
                  @input="filterCategories"
                  @keydown.enter.prevent="addCustomCategory"
                  placeholder="Search categories or type new..."
                  class="search-input"
                />
                <button v-if="categorySearchTerm && !availableCategories.includes(categorySearchTerm)" 
                        type="button"
                        @click.stop="addCustomCategory" 
                        class="add-new-btn">
                  <i class="fas fa-plus"></i> Add "{{ categorySearchTerm }}"
                </button>
              </div>
              <div class="options-list">
                <div v-if="filteredCategories.length === 0 && !categorySearchTerm" class="no-options">
                  No categories available
                </div>
                <div v-for="category in filteredCategories" 
                     :key="category" 
                     class="option-item" 
                     @click="toggleCategory(category)">
                  <input type="checkbox" :checked="selectedCategories.includes(category)" />
                  <span>{{ category }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="validationErrors.RiskCategory" class="validation-error">{{ validationErrors.RiskCategory }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-radiation-alt"></i>Criticality</span>
          <select v-model="formData.Criticality" @change="validateCriticality" title="Rate the overall criticality level of this incident">
            <option value="">Select Criticality</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <div v-if="validationErrors.Criticality" class="validation-error">{{ validationErrors.Criticality }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-dollar-sign"></i>Cost of Incident</span>
          <input 
            type="text" 
            v-model="formData.CostOfIncident" 
            @input="validateCost" 
            @blur="validateCost"
            placeholder="e.g., $50,000, €25,000.50, 100000"
            title="Estimate the financial impact or cost of this incident"
          />
          <div v-if="validationErrors.CostOfIncident" class="validation-error">{{ validationErrors.CostOfIncident }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-exclamation-triangle"></i>Possible Damage</span>
          <textarea 
            v-model="formData.PossibleDamage"
            @input="validatePossibleDamage"
            @blur="validatePossibleDamage"
            placeholder="e.g., Data loss, customer trust impact, regulatory fines, business disruption, reputation damage..."
            title="Describe potential damage that could result from this incident"
          ></textarea>
          <div v-if="validationErrors.PossibleDamage" class="validation-error">{{ validationErrors.PossibleDamage }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-building"></i>Business Unit</span>
          <div class="multi-select-dropdown">
            <div class="multi-select-input" @click="toggleBusinessUnitDropdown">
              <div class="selected-items">
                <span v-if="selectedBusinessUnits.length === 0" class="placeholder">
                  Select business units or type to add new...
                </span>
                <span v-for="unit in selectedBusinessUnits" :key="unit" class="selected-item">
                  {{ unit }}
                  <i class="fas fa-times" @click.stop="removeBusinessUnit(unit)"></i>
                </span>
              </div>
              <i class="fas fa-chevron-down dropdown-arrow" :class="{ 'rotated': showBusinessUnitDropdown }"></i>
            </div>
            <div v-if="showBusinessUnitDropdown" class="dropdown-panel">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="businessUnitSearchTerm" 
                  @input="filterBusinessUnits"
                  @keydown.enter.prevent="addCustomBusinessUnit"
                  placeholder="Search business units or type new..."
                  class="search-input"
                />
                <button v-if="businessUnitSearchTerm && !availableBusinessUnits.includes(businessUnitSearchTerm)" 
                        type="button"
                        @click.stop="addCustomBusinessUnit" 
                        class="add-new-btn">
                  <i class="fas fa-plus"></i> Add "{{ businessUnitSearchTerm }}"
                </button>
              </div>
              <div class="options-list">
                <div v-if="filteredBusinessUnits.length === 0 && !businessUnitSearchTerm" class="no-options">
                  No business units available
                </div>
                <div v-for="unit in filteredBusinessUnits" 
                     :key="unit" 
                     class="option-item" 
                     @click="toggleBusinessUnit(unit)">
                  <input type="checkbox" :checked="selectedBusinessUnits.includes(unit)" />
                  <span>{{ unit }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="validationErrors.AffectedBusinessUnit" class="validation-error">{{ validationErrors.AffectedBusinessUnit }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-map-marker-alt"></i>Location</span>
          <input 
            type="text" 
            v-model="formData.GeographicLocation"
            @input="validateGeographicLocation"
            @blur="validateGeographicLocation"
            placeholder="e.g., New York Office, London Branch, Remote/Cloud, Data Center - Dallas..."
            title="Specify the geographic location where the incident occurred"
          />
          <div v-if="validationErrors.GeographicLocation" class="validation-error">{{ validationErrors.GeographicLocation }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-server"></i>Systems Involved</span>
          <input 
            type="text" 
            v-model="formData.SystemsAssetsInvolved"
            @input="validateSystemsInvolved"
            @blur="validateSystemsInvolved"
            placeholder="e.g., Customer CRM, Payment Gateway, Email Server, Database XYZ, Network Infrastructure..."
            title="List the systems, applications, or assets involved in the incident"
          />
          <div v-if="validationErrors.SystemsAssetsInvolved" class="validation-error">{{ validationErrors.SystemsAssetsInvolved }}</div>
        </label>

        <label class="field-two-thirds">
          <span><i class="fas fa-chart-line"></i>Initial Impact Assessment</span>
          <textarea 
            v-model="formData.InitialImpactAssessment"
            @input="validateInitialImpact"
            @blur="validateInitialImpact"
            placeholder="Describe the immediate and potential impacts: operational disruption, customer impact, data exposure, service availability, compliance implications..."
            title="Provide an initial assessment of the impact on business operations"
          ></textarea>
          <div v-if="validationErrors.InitialImpactAssessment" class="validation-error">{{ validationErrors.InitialImpactAssessment }}</div>
        </label>
        <!-- Response Section -->
        <label class="field-two-thirds">
          <span><i class="fas fa-shield-alt"></i>Mitigation Steps</span>
          <textarea 
            v-model="formData.Mitigation"
            @input="validateMitigation"
            @blur="validateMitigation"
            placeholder="Detail the immediate actions taken and planned mitigation steps: containment measures, system isolation, patches applied, temporary workarounds..."
            title="Describe the steps taken or planned to mitigate the incident"
          ></textarea>
          <div v-if="validationErrors.Mitigation" class="validation-error">{{ validationErrors.Mitigation }}</div>
        </label>

        <label class="field-third">
          <span><i class="fas fa-comments"></i>Comments</span>
          <textarea 
            v-model="formData.Comments"
            @input="validateComments"
            @blur="validateComments"
            placeholder="Additional observations, context, or relevant information not covered elsewhere..."
            title="Add any additional comments or observations about the incident"
          ></textarea>
          <div v-if="validationErrors.Comments" class="validation-error">{{ validationErrors.Comments }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-users"></i>Internal Contacts</span>
          <textarea 
            v-model="formData.InternalContacts"
            @input="validateInternalContacts"
            @blur="validateInternalContacts"
            placeholder="Names and roles of internal staff involved: John Smith (IT Manager), Sarah Jones (Security Lead)..."
            title="List internal team members or contacts involved in incident response"
          ></textarea>
          <div v-if="validationErrors.InternalContacts" class="validation-error">{{ validationErrors.InternalContacts }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-building"></i>External Parties</span>
          <textarea 
            v-model="formData.ExternalPartiesInvolved"
            @input="validateExternalParties"
            @blur="validateExternalParties"
            placeholder="External organizations, vendors, customers, or partners affected: ABC Vendor, Customer Portal Users, Third-party Service Provider..."
            title="Identify any external parties involved or affected by the incident"
          ></textarea>
          <div v-if="validationErrors.ExternalPartiesInvolved" class="validation-error">{{ validationErrors.ExternalPartiesInvolved }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-gavel"></i>Regulatory Bodies</span>
          <textarea 
            v-model="formData.RegulatoryBodies"
            @input="validateRegulatoryBodies"
            @blur="validateRegulatoryBodies"
            placeholder="Relevant regulatory authorities: SEC, GDPR Authority, FINRA, HIPAA, PCI DSS Council..."
            title="List regulatory bodies that need to be notified or are involved"
          ></textarea>
          <div v-if="validationErrors.RegulatoryBodies" class="validation-error">{{ validationErrors.RegulatoryBodies }}</div>
        </label>
        
        <!-- Additional Information -->
        <label class="field-two-thirds">
          <span><i class="fas fa-exclamation-circle"></i>Violated Policies/Procedures</span>
          <textarea 
            v-model="formData.RelevantPoliciesProceduresViolated"
            @input="validateViolatedPolicies"
            @blur="validateViolatedPolicies"
            placeholder="List specific policies, procedures, or standards that were violated: Data Protection Policy section 3.2, Access Control Procedure, Change Management Process..."
            title="Identify specific policies or procedures that were violated or not followed"
          ></textarea>
          <div v-if="validationErrors.RelevantPoliciesProceduresViolated" class="validation-error">{{ validationErrors.RelevantPoliciesProceduresViolated }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-times-circle"></i>Control Failures</span>
          <textarea 
            v-model="formData.ControlFailures"
            @input="validateControlFailures"
            @blur="validateControlFailures"
            placeholder="Identify failed controls: firewall misconfiguration, inadequate access controls, missing monitoring, failed backup procedures..."
            title="Describe any control failures that contributed to the incident"
          ></textarea>
          <div v-if="validationErrors.ControlFailures" class="validation-error">{{ validationErrors.ControlFailures }}</div>
        </label>
        
        <label class="field-third">
          <span><i class="fas fa-tags"></i>Incident Classification</span>
          <select v-model="formData.IncidentClassification" @change="onClassificationChange" title="Classify the type of incident for proper handling and escalation">
            <option value="">Select Classification</option>
            <option value="NonConformance">NonConformance</option>
            <option value="Control GAP">Control GAP</option>
            <option value="Risk">Risk</option>
            <option value="Issue">No Issue</option>
          </select>
        </label>

        <!-- Compliance Mapping Section (shown only when NonConformance or GAP is selected) -->
        <div v-if="showComplianceMapping" class="field-full compliance-mapping-section">
          <label class="field-full">
            <span><i class="fas fa-link"></i>Map to Existing Compliance</span>
            <div class="compliance-selector" @click.stop>
              <input 
                type="text" 
                v-model="complianceSearchTerm" 
                placeholder="Search compliances by description, policy name, or framework..."
                @input="filterCompliances"
                @focus="showDropdown = true"
                @blur="hideDropdownDelayed"
                class="compliance-search"
                title="Search and select a compliance requirement to link with this incident"
              />
              <div v-if="loadingCompliances" class="compliance-loading">
                <i class="fas fa-spinner fa-spin"></i> Loading compliances...
              </div>
              <div v-else-if="compliances.length === 0" class="no-compliances-available">
                <div class="external-risk-message">
                  <i class="fas fa-exclamation-triangle"></i>
                  <div>
                    <strong>No Compliances Available</strong>
                    <p>This incident will be saved as an <strong>External Risk</strong> since no compliance items are available in the system.</p>
                  </div>
                </div>
              </div>
              <div v-else-if="showDropdown && filteredCompliances.length > 0" class="compliance-dropdown">
                <div v-if="!complianceSearchTerm" class="compliance-info">
                  <small><i class="fas fa-info-circle"></i> Showing {{ filteredCompliances.length }} total compliances. Use search to filter results.</small>
                </div>
                <div v-else class="compliance-info">
                  <small><i class="fas fa-search"></i> Found {{ filteredCompliances.length }} compliance(s) matching "{{ complianceSearchTerm }}"</small>
                </div>
                <div class="compliance-options-container">
                  <div 
                    v-for="compliance in filteredCompliances" 
                    :key="compliance.ComplianceId"
                    @click="selectCompliance(compliance)"
                    class="compliance-option"
                    :class="{ 'selected': formData.ComplianceId === compliance.ComplianceId }"
                  >
                    <div class="compliance-checkbox">
                      <input 
                        type="radio" 
                        :id="'compliance-' + compliance.ComplianceId"
                        :value="compliance.ComplianceId"
                        :checked="formData.ComplianceId === compliance.ComplianceId"
                        @click.stop
                        @change="selectCompliance(compliance)"
                      />
                      <label :for="'compliance-' + compliance.ComplianceId" class="radio-label"></label>
                    </div>
                    <div class="compliance-content">
                      <div class="compliance-header">
                        <strong>{{ compliance.ComplianceItemDescription }}</strong>
                        <span class="compliance-criticality" :class="'criticality-' + (compliance.Criticality || 'medium').toLowerCase()">
                          {{ compliance.Criticality }}
                        </span>
                      </div>
                      <div class="compliance-details">
                        <span class="framework-name">{{ compliance.SubPolicy?.Policy?.Framework?.FrameworkName || 'No Framework' }}</span>
                        <span class="policy-name">{{ compliance.SubPolicy?.Policy?.PolicyName || 'No Policy' }}</span>
                      </div>
                      <div v-if="compliance.Mitigation" class="compliance-mitigation">
                        <small>{{ compliance.Mitigation.substring(0, 100) }}{{ compliance.Mitigation.length > 100 ? '...' : '' }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="!loadingCompliances && complianceSearchTerm && showDropdown" class="no-compliances">
                No compliances found matching "{{ complianceSearchTerm }}"
              </div>
            </div>
          </label>
          
          <!-- Selected Compliance Display -->
          <div v-if="selectedCompliance" class="selected-compliance">
            <h4><i class="fas fa-check-circle"></i> Selected Compliance</h4>
            <div class="compliance-card">
              <div class="compliance-card-header">
                <strong>{{ selectedCompliance.ComplianceItemDescription }}</strong>
                <span class="compliance-criticality" :class="'criticality-' + (selectedCompliance.Criticality || 'medium').toLowerCase()">
                  {{ selectedCompliance.Criticality }}
                </span>
              </div>
              <div class="compliance-card-body">
                <p><strong>Framework:</strong> {{ selectedCompliance.SubPolicy?.Policy?.Framework?.FrameworkName || 'N/A' }}</p>
                <p><strong>Policy:</strong> {{ selectedCompliance.SubPolicy?.Policy?.PolicyName || 'N/A' }}</p>
                <p><strong>Sub Policy:</strong> {{ selectedCompliance.SubPolicy?.SubPolicyName || 'N/A' }}</p>
                <p v-if="selectedCompliance.Mitigation"><strong>Mitigation:</strong> {{ selectedCompliance.Mitigation }}</p>
                <p v-if="selectedCompliance.PossibleDamage"><strong>Possible Damage:</strong> {{ selectedCompliance.PossibleDamage }}</p>
              </div>
              <button type="button" @click="clearCompliance" class="clear-compliance-btn">
                <i class="fas fa-times"></i> Clear Selection
              </button>
            </div>
          </div>
        </div>

        <label class="field-full">
          <span><i class="fas fa-lightbulb"></i>Lessons Learned</span>
          <textarea 
            v-model="formData.LessonsLearned"
            placeholder="What can be learned from this incident? What should be done differently next time? What processes need improvement? What preventive measures can be implemented..."
            title="Document key insights and lessons learned from this incident for future prevention"
          ></textarea>
        </label>

        <!-- Incident Classification -->
        

        <!-- Incident Status Information -->
        <div v-if="showComplianceMapping" class="incident-status-info">
          <div class="status-header">
            <i class="fas fa-info-circle"></i>
            <strong>Incident Information</strong>
          </div>
          <div class="status-details">
            <div class="status-item">
              <span class="label">Type:</span>
              <span class="value" :class="'incident-type-' + incidentType.toLowerCase().replace(/[^a-z]/g, '-')">
                {{ incidentType }}
              </span>
            </div>
            <div v-if="selectedCompliance" class="status-item">
              <span class="label">Linked Compliance:</span>
              <span class="value">{{ selectedCompliance.ComplianceItemDescription }}</span>
            </div>
            <div v-else-if="showComplianceMapping && compliances.length === 0" class="status-item">
              <span class="label">Note:</span>
              <span class="value warning">No compliance items available - saving as external risk</span>
            </div>
            <div v-else-if="showComplianceMapping" class="status-item">
              <span class="label">Note:</span>
              <span class="value">No compliance selected - will save as external risk</span>
            </div>
          </div>
        </div>

        <div class="incident-form-actions">
          <button type="button" @click="cancel" class="incident-cancel-btn">
            <i class="fas fa-times"></i> Cancel
          </button>
          <button 
            type="submit" 
            class="incident-submit-btn"
            :disabled="!isReadyToSubmit"
            :title="isReadyToSubmit ? `Create ${incidentType}` : 'Please fill in all required fields'"
          >
            <i class="fas fa-save"></i> Create {{ incidentType }}
          </button>
        </div>
      </form>
    </div>
    
    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import './CreateIncident.css'
import { PopupService, PopupModal } from '@/modules/popup'

export default {
  name: 'CreateIncident',
  components: {
    PopupModal
  },
  setup() {
    const router = useRouter()
    
    const formData = ref({
      IncidentTitle: '',
      Description: '',
      Mitigation: '',
      Date: '',
      Time: '',
      Origin: '',
      Comments: '',
      RiskCategory: '',
      RiskPriority: '',
      Status: 'Open',
      AffectedBusinessUnit: '',
      SystemsAssetsInvolved: '',
      GeographicLocation: '',
      Criticality: '',
      TimelineOfEvents: '',
      InitialImpactAssessment: '',
      InternalContacts: '',
      ExternalPartiesInvolved: '',
      RegulatoryBodies: '',
      RelevantPoliciesProceduresViolated: '',
      ControlFailures: '',
      LessonsLearned: '',
      CostOfIncident: '',
      PossibleDamage: '',
      RepeatedNot: false,
      ReopenedNot: false,
      IncidentClassification: '',
      ComplianceId: null
    })

    // Validation errors
    const validationErrors = ref({})

    // Compliance-related reactive data
    const compliances = ref([])
    const complianceSearchTerm = ref('')
    const selectedCompliance = ref(null)
    const loadingCompliances = ref(false)
    const showDropdown = ref(false)

    // Category and Business Unit dropdown data
    const availableCategories = ref([])
    const selectedCategories = ref([])
    const categorySearchTerm = ref('')
    const showCategoryDropdown = ref(false)
    const filteredCategories = ref([])

    const availableBusinessUnits = ref([])
    const selectedBusinessUnits = ref([])
    const businessUnitSearchTerm = ref('')
    const showBusinessUnitDropdown = ref(false)
    const filteredBusinessUnits = ref([])

    // Computed properties
    const showComplianceMapping = computed(() => {
      return formData.value.IncidentClassification === 'NonConformance' || 
             formData.value.IncidentClassification === 'Control GAP'
    })

    const filteredCompliances = computed(() => {
      if (!complianceSearchTerm.value) {
        return compliances.value // Show all compliances when no search term
      }
      
      return compliances.value.filter(compliance => {
        const searchLower = complianceSearchTerm.value.toLowerCase()
        return (
          compliance.ComplianceItemDescription?.toLowerCase().includes(searchLower) ||
          compliance.Identifier?.toLowerCase().includes(searchLower) ||
          compliance.SubPolicy?.Policy?.PolicyName?.toLowerCase().includes(searchLower) ||
          compliance.SubPolicy?.Policy?.Framework?.FrameworkName?.toLowerCase().includes(searchLower)
        )
      }) // Show all filtered results without limit
    })

    const incidentType = computed(() => {
      if (!showComplianceMapping.value) {
        return 'Regular Incident'
      }
      if (compliances.value.length === 0) {
        return 'External Risk'
      }
      if (selectedCompliance.value) {
        return 'Compliance-Linked Incident'
      }
      return 'External Risk'
    })

    const isReadyToSubmit = computed(() => {
      // Basic form validation - check required fields
      const hasRequiredFields = formData.value.IncidentTitle && 
                               formData.value.Description && 
                               formData.value.Date && 
                               formData.value.Time &&
                               formData.value.RiskPriority &&
                               selectedCategories.value.length > 0 // At least one category required
      
      // Check for validation errors
      const hasNoErrors = Object.keys(validationErrors.value).length === 0
      
      return hasRequiredFields && hasNoErrors
    })

    // Enhanced validation methods with security patterns
    const BUSINESS_TEXT_PATTERN = /^[a-zA-Z0-9\s\-_.,!?():;/\\@#$%&*+=<>[\]{}|~`"']*$/
    const ALPHANUMERIC_WITH_SPACES = /^[a-zA-Z0-9\s\-_.,!?()]*$/
    // More permissive pattern for categories
    const CATEGORY_PATTERN = /^[a-zA-Z0-9\s\-_.,!?()&]*$/
    const CURRENCY_PATTERN = /^[$£€]?[0-9]+(\.[0-9]{1,2})?$/

    const validateField = (value, fieldName, options = {}) => {
      const { required = false, minLength = 0, maxLength = 255, pattern = null } = options
      
      // Check if required
      if (required && (!value || value.trim() === '')) {
        return `${fieldName} is required`
      }
      
      // Skip further validation if not required and empty
      if (!required && (!value || value.trim() === '')) {
        return null
      }
      
      // Check length
      const trimmedValue = value.trim()
      if (trimmedValue.length < minLength) {
        return `${fieldName} must be at least ${minLength} characters`
      }
      
      if (trimmedValue.length > maxLength) {
        return `${fieldName} must be no more than ${maxLength} characters`
      }
      
      // Check pattern
      if (pattern && !pattern.test(trimmedValue)) {
        return `${fieldName} contains invalid characters`
      }
      
      return null
    }

    const validateCost = () => {
      const cost = formData.value.CostOfIncident
      if (cost && !CURRENCY_PATTERN.test(cost.toString().trim())) {
        validationErrors.value.CostOfIncident = "Must be a valid currency amount (e.g., $100.50, 250.75)"
      } else {
        delete validationErrors.value.CostOfIncident
      }
    }

    // Individual field validation functions
    const validateIncidentTitle = () => {
      const titleError = validateField(formData.value.IncidentTitle, 'Incident Title', {
        required: true,
        minLength: 3,
        maxLength: 255,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (titleError) {
        validationErrors.value.IncidentTitle = titleError
      } else {
        delete validationErrors.value.IncidentTitle
      }
    }

    const validateDescription = () => {
      const descError = validateField(formData.value.Description, 'Description', {
        required: true,
        minLength: 10,
        maxLength: 2000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (descError) {
        validationErrors.value.Description = descError
      } else {
        delete validationErrors.value.Description
      }
    }

    const validateOrigin = () => {
      const allowedOrigins = ['Manual', 'Audit Finding', 'System Generated']
      if (formData.value.Origin && !allowedOrigins.includes(formData.value.Origin)) {
        validationErrors.value.Origin = 'Must be one of: Manual, Audit Finding, System Generated'
      } else {
        delete validationErrors.value.Origin
      }
    }

    const validateDate = () => {
      if (!formData.value.Date) {
        validationErrors.value.Date = "Date is required"
      } else {
        delete validationErrors.value.Date
      }
      }
      
    const validateTime = () => {
      if (!formData.value.Time) {
        validationErrors.value.Time = "Time is required"
      } else {
        delete validationErrors.value.Time
      }
      }
      
    const validateRiskPriority = () => {
      const allowedPriorities = ['High', 'Medium', 'Low']
      if (!formData.value.RiskPriority) {
        validationErrors.value.RiskPriority = "Risk priority is required"
      } else if (!allowedPriorities.includes(formData.value.RiskPriority)) {
        validationErrors.value.RiskPriority = 'Must be one of: High, Medium, Low'
      } else {
        delete validationErrors.value.RiskPriority
      }
    }

    const validateRiskCategory = () => {
      // For multi-select, check if at least one category is selected
      if (selectedCategories.value.length === 0) {
        validationErrors.value.RiskCategory = 'At least one risk category is required'
      } else {
        // Validate each selected category
        const invalidCategories = selectedCategories.value.filter(category => {
          const isValid = category && category.length <= 100 && CATEGORY_PATTERN.test(category)
          return !isValid
        })
        
        if (invalidCategories.length > 0) {
          validationErrors.value.RiskCategory = 'One or more categories contain invalid characters or are too long'
        } else {
          delete validationErrors.value.RiskCategory
        }
      }
    }

    const validateCriticality = () => {
      const allowedCriticality = ['Critical', 'High', 'Medium', 'Low']
      if (formData.value.Criticality && !allowedCriticality.includes(formData.value.Criticality)) {
        validationErrors.value.Criticality = 'Must be one of: Critical, High, Medium, Low'
      } else {
        delete validationErrors.value.Criticality
      }
    }

    const validatePossibleDamage = () => {
      const damageError = validateField(formData.value.PossibleDamage, 'Possible Damage', {
        maxLength: 1000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (damageError) {
        validationErrors.value.PossibleDamage = damageError
      } else {
        delete validationErrors.value.PossibleDamage
      }
    }

    const validateBusinessUnit = () => {
      // Business units are optional, so only validate if some are selected
      if (selectedBusinessUnits.value.length > 0) {
        // Validate each selected business unit
        const invalidUnits = selectedBusinessUnits.value.filter(unit => {
          return !unit || unit.length > 100 || !ALPHANUMERIC_WITH_SPACES.test(unit)
        })
        
        if (invalidUnits.length > 0) {
          validationErrors.value.AffectedBusinessUnit = 'One or more business units contain invalid characters or are too long'
        } else {
          delete validationErrors.value.AffectedBusinessUnit
        }
      } else {
        delete validationErrors.value.AffectedBusinessUnit
      }
    }

    const validateGeographicLocation = () => {
      const locationError = validateField(formData.value.GeographicLocation, 'Geographic Location', {
        maxLength: 100,
        pattern: ALPHANUMERIC_WITH_SPACES
      })
      if (locationError) {
        validationErrors.value.GeographicLocation = locationError
      } else {
        delete validationErrors.value.GeographicLocation
      }
    }

    const validateSystemsInvolved = () => {
      const systemsError = validateField(formData.value.SystemsAssetsInvolved, 'Systems Involved', {
        maxLength: 500,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (systemsError) {
        validationErrors.value.SystemsAssetsInvolved = systemsError
      } else {
        delete validationErrors.value.SystemsAssetsInvolved
      }
    }

    const validateInitialImpact = () => {
      const impactError = validateField(formData.value.InitialImpactAssessment, 'Initial Impact Assessment', {
        maxLength: 2000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (impactError) {
        validationErrors.value.InitialImpactAssessment = impactError
      } else {
        delete validationErrors.value.InitialImpactAssessment
      }
    }

    const validateMitigation = () => {
      const mitigationError = validateField(formData.value.Mitigation, 'Mitigation Steps', {
        maxLength: 2000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (mitigationError) {
        validationErrors.value.Mitigation = mitigationError
      } else {
        delete validationErrors.value.Mitigation
      }
    }

    const validateComments = () => {
      const commentsError = validateField(formData.value.Comments, 'Comments', {
        maxLength: 1000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (commentsError) {
        validationErrors.value.Comments = commentsError
      } else {
        delete validationErrors.value.Comments
      }
    }

    const validateInternalContacts = () => {
      const contactsError = validateField(formData.value.InternalContacts, 'Internal Contacts', {
        maxLength: 500,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (contactsError) {
        validationErrors.value.InternalContacts = contactsError
      } else {
        delete validationErrors.value.InternalContacts
      }
    }

    const validateExternalParties = () => {
      const partiesError = validateField(formData.value.ExternalPartiesInvolved, 'External Parties', {
        maxLength: 500,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (partiesError) {
        validationErrors.value.ExternalPartiesInvolved = partiesError
      } else {
        delete validationErrors.value.ExternalPartiesInvolved
      }
    }

    const validateRegulatoryBodies = () => {
      const bodiesError = validateField(formData.value.RegulatoryBodies, 'Regulatory Bodies', {
        maxLength: 500,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (bodiesError) {
        validationErrors.value.RegulatoryBodies = bodiesError
      } else {
        delete validationErrors.value.RegulatoryBodies
      }
    }

    const validateViolatedPolicies = () => {
      const policiesError = validateField(formData.value.RelevantPoliciesProceduresViolated, 'Violated Policies/Procedures', {
        maxLength: 1000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (policiesError) {
        validationErrors.value.RelevantPoliciesProceduresViolated = policiesError
      } else {
        delete validationErrors.value.RelevantPoliciesProceduresViolated
      }
    }

    const validateControlFailures = () => {
      const failuresError = validateField(formData.value.ControlFailures, 'Control Failures', {
        maxLength: 1000,
        pattern: BUSINESS_TEXT_PATTERN
      })
      if (failuresError) {
        validationErrors.value.ControlFailures = failuresError
      } else {
        delete validationErrors.value.ControlFailures
      }
    }

    const validateForm = () => {
      // Run all individual validations to ensure everything is validated
      validateIncidentTitle()
      validateDescription()
      validateOrigin()
      validateDate()
      validateTime()
      validateRiskPriority()
      validateRiskCategory()
      validateCriticality()
      validateCost()
      validatePossibleDamage()
      validateBusinessUnit()
      validateGeographicLocation()
      validateSystemsInvolved()
      validateInitialImpact()
      validateMitigation()
      validateComments()
      validateInternalContacts()
      validateExternalParties()
      validateRegulatoryBodies()
      validateViolatedPolicies()
      validateControlFailures()
      
      return Object.keys(validationErrors.value).length === 0
    }

    // Methods
    const fetchCompliances = async () => {
      if (compliances.value.length > 0) return // Already loaded

      loadingCompliances.value = true
      try {
        const response = await axios.get('/api/incident-compliances/')
        if (response.data.success) {
          compliances.value = response.data.data
          console.log('Loaded compliances:', compliances.value.length)
        } else {
          console.error('Failed to fetch compliances:', response.data.message)
        }
      } catch (error) {
        console.error('Error fetching compliances:', error)
      } finally {
        loadingCompliances.value = false
      }
    }

    const onClassificationChange = () => {
      // Clear compliance selection when classification changes
      if (!showComplianceMapping.value) {
        formData.value.ComplianceId = null
        selectedCompliance.value = null
        complianceSearchTerm.value = ''
        showDropdown.value = false
      } else {
        // Load compliances when needed
        fetchCompliances()
        showDropdown.value = false // Start with dropdown closed
      }
    }

    const selectCompliance = (compliance) => {
      formData.value.ComplianceId = compliance.ComplianceId
      selectedCompliance.value = compliance
      complianceSearchTerm.value = '' // Clear search term
      showDropdown.value = false // Close dropdown
      
      // Auto-fill some fields from compliance if they're empty
      if (!formData.value.PossibleDamage && compliance.PossibleDamage) {
        formData.value.PossibleDamage = compliance.PossibleDamage
      }
      if (!formData.value.Mitigation && compliance.Mitigation) {
        formData.value.Mitigation = compliance.Mitigation
      }
      if (!formData.value.Criticality && compliance.Criticality) {
        formData.value.Criticality = compliance.Criticality
      }
      
      console.log('Selected compliance:', compliance.ComplianceId, compliance.ComplianceItemDescription)
      console.log('Dropdown closed after selection')
    }

    const clearCompliance = () => {
      formData.value.ComplianceId = null
      selectedCompliance.value = null
      complianceSearchTerm.value = ''
      showDropdown.value = false
      console.log('Compliance selection cleared')
    }

    const filterCompliances = () => {
      // Show dropdown when user starts typing
      if (complianceSearchTerm.value.length > 0) {
        showDropdown.value = true
      }
    }

    const hideDropdownDelayed = () => {
      // Add a small delay to allow click events on dropdown items to fire first
      setTimeout(() => {
        showDropdown.value = false
      }, 150)
    }

    const validateAndSubmit = async () => {
      if (!validateForm()) {
        PopupService.error('Please correct the validation errors before submitting')
        return
      }
      
      await submitForm()
    }

    const submitForm = async () => {
      try {
        // Prepare form data - include ComplianceId only if a compliance is selected
        const submissionData = { ...formData.value }
        
        // Ensure ComplianceId is null if no compliance is selected
        if (!selectedCompliance.value || !formData.value.ComplianceId) {
          submissionData.ComplianceId = null
          console.log('No compliance selected - saving as external risk')
        } else {
          console.log('Compliance selected:', selectedCompliance.value.ComplianceItemDescription)
        }
        
        console.log('Submitting incident with data:', submissionData)
        
        const response = await axios.post('/api/incidents/create/', submissionData)
        if (response.status === 201) {
          // Show success message and redirect
          PopupService.success('Incident created successfully! It has been saved to the incidents table and will be escalated to risk management when needed.')
          
          // Navigate to incidents list after a short delay to allow user to see success message
          setTimeout(() => {
            router.push('/incident/incident')
          }, 2000) // 2 second delay to show the success message
        }
      } catch (error) {
        console.error('Error creating incident:', error)
        if (error.response && error.response.data) {
          // Handle validation errors from server
          const serverErrors = error.response.data
          Object.keys(serverErrors).forEach(field => {
            validationErrors.value[field] = Array.isArray(serverErrors[field]) 
              ? serverErrors[field][0] 
              : serverErrors[field]
          })
          PopupService.error('Please correct the validation errors and try again.')
        } else {
          PopupService.error('Error creating incident. Please try again.')
        }
      }
    }

    const cancel = () => {
      // Navigate back to incidents list
      router.push('/incident/incident')
    }

    const generateAnalysis = () => {
      // TODO: Implement AI-powered analysis generation
      PopupService.info('Analysis generation feature coming soon! This will help auto-fill incident details based on the title and description.')
    }

    // Category dropdown methods
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/categories/')
        availableCategories.value = response.data
        filteredCategories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const toggleCategoryDropdown = () => {
      showCategoryDropdown.value = !showCategoryDropdown.value
      if (showCategoryDropdown.value) {
        filteredCategories.value = availableCategories.value
      }
    }

    const filterCategories = () => {
      const searchTerm = categorySearchTerm.value.toLowerCase()
      filteredCategories.value = availableCategories.value.filter(category =>
        category.toLowerCase().includes(searchTerm)
      )
    }

    const toggleCategory = (category) => {
      if (selectedCategories.value.includes(category)) {
        selectedCategories.value = selectedCategories.value.filter(c => c !== category)
      } else {
        selectedCategories.value.push(category)
      }
      updateFormDataCategories()
    }

    const removeCategory = (category) => {
      selectedCategories.value = selectedCategories.value.filter(c => c !== category)
      updateFormDataCategories()
    }

    const addCustomCategory = async () => {
      const newCategory = categorySearchTerm.value.trim()
      console.log('Adding custom category:', newCategory)
      
      if (newCategory && !availableCategories.value.some(cat => cat.toLowerCase() === newCategory.toLowerCase())) {
        try {
          console.log('Posting new category to API:', newCategory)
          const response = await axios.post('/api/categories/add/', { value: newCategory })
          console.log('API response:', response.data)
          
          const addedCategory = response.data.value || newCategory
          
          // Add to available categories if not already there
          if (!availableCategories.value.includes(addedCategory)) {
            availableCategories.value.push(addedCategory)
            console.log('Added to available categories:', addedCategory)
          }
          
          // Add to selected categories if not already selected
          if (!selectedCategories.value.includes(addedCategory)) {
            selectedCategories.value.push(addedCategory)
            console.log('Added to selected categories:', addedCategory)
          }
          
          // Clear search and update filtered list
          categorySearchTerm.value = ''
          filteredCategories.value = availableCategories.value
          
          // Update form data and trigger validation
          updateFormDataCategories()
          
          // Force clear any lingering category validation errors
          setTimeout(() => {
            if (selectedCategories.value.length > 0) {
              delete validationErrors.value.RiskCategory
              console.log('Force cleared RiskCategory validation error')
            }
          }, 100)
          
          PopupService.success(`Category "${addedCategory}" added successfully!`)
        } catch (error) {
          console.error('Error adding category:', error)
          PopupService.error('Failed to add category. Please try again.')
        }
      } else if (newCategory && availableCategories.value.some(cat => cat.toLowerCase() === newCategory.toLowerCase())) {
        // Category exists, just select it
        const existingCategory = availableCategories.value.find(cat => cat.toLowerCase() === newCategory.toLowerCase())
        console.log('Category already exists, selecting:', existingCategory)
        
        if (!selectedCategories.value.includes(existingCategory)) {
          selectedCategories.value.push(existingCategory)
          updateFormDataCategories()
        }
        categorySearchTerm.value = ''
      } else if (!newCategory) {
        console.log('Empty category name provided')
      } else {
        console.log('Category already selected:', newCategory)
      }
    }

    const updateFormDataCategories = () => {
      formData.value.RiskCategory = selectedCategories.value.join(', ')
      validateRiskCategory() // Trigger validation when categories change
    }

    // Business Unit dropdown methods
    const fetchBusinessUnits = async () => {
      try {
        const response = await axios.get('/api/business-units/')
        availableBusinessUnits.value = response.data
        filteredBusinessUnits.value = response.data
      } catch (error) {
        console.error('Error fetching business units:', error)
      }
    }

    const toggleBusinessUnitDropdown = () => {
      showBusinessUnitDropdown.value = !showBusinessUnitDropdown.value
      if (showBusinessUnitDropdown.value) {
        filteredBusinessUnits.value = availableBusinessUnits.value
      }
    }

    const filterBusinessUnits = () => {
      const searchTerm = businessUnitSearchTerm.value.toLowerCase()
      filteredBusinessUnits.value = availableBusinessUnits.value.filter(unit =>
        unit.toLowerCase().includes(searchTerm)
      )
    }

    const toggleBusinessUnit = (unit) => {
      if (selectedBusinessUnits.value.includes(unit)) {
        selectedBusinessUnits.value = selectedBusinessUnits.value.filter(u => u !== unit)
      } else {
        selectedBusinessUnits.value.push(unit)
      }
      updateFormDataBusinessUnits()
    }

    const removeBusinessUnit = (unit) => {
      selectedBusinessUnits.value = selectedBusinessUnits.value.filter(u => u !== unit)
      updateFormDataBusinessUnits()
    }

    const addCustomBusinessUnit = async () => {
      const newUnit = businessUnitSearchTerm.value.trim()
      console.log('Adding custom business unit:', newUnit)
      
      if (newUnit && !availableBusinessUnits.value.some(unit => unit.toLowerCase() === newUnit.toLowerCase())) {
        try {
          console.log('Posting new business unit to API:', newUnit)
          const response = await axios.post('/api/business-units/add/', { value: newUnit })
          console.log('API response:', response.data)
          
          const addedUnit = response.data.value || newUnit
          
          // Add to available business units if not already there
          if (!availableBusinessUnits.value.includes(addedUnit)) {
            availableBusinessUnits.value.push(addedUnit)
            console.log('Added to available business units:', addedUnit)
          }
          
          // Add to selected business units if not already selected
          if (!selectedBusinessUnits.value.includes(addedUnit)) {
            selectedBusinessUnits.value.push(addedUnit)
            console.log('Added to selected business units:', addedUnit)
          }
          
          // Clear search and update filtered list
          businessUnitSearchTerm.value = ''
          filteredBusinessUnits.value = availableBusinessUnits.value
          
          // Update form data and trigger validation
          updateFormDataBusinessUnits()
          
          // Force clear any lingering business unit validation errors
          setTimeout(() => {
            delete validationErrors.value.AffectedBusinessUnit
            console.log('Force cleared AffectedBusinessUnit validation error')
          }, 100)
          
          PopupService.success(`Business unit "${addedUnit}" added successfully!`)
        } catch (error) {
          console.error('Error adding business unit:', error)
          PopupService.error('Failed to add business unit. Please try again.')
        }
      } else if (newUnit && availableBusinessUnits.value.some(unit => unit.toLowerCase() === newUnit.toLowerCase())) {
        // Business unit exists, just select it
        const existingUnit = availableBusinessUnits.value.find(unit => unit.toLowerCase() === newUnit.toLowerCase())
        console.log('Business unit already exists, selecting:', existingUnit)
        
        if (!selectedBusinessUnits.value.includes(existingUnit)) {
          selectedBusinessUnits.value.push(existingUnit)
          updateFormDataBusinessUnits()
        }
        businessUnitSearchTerm.value = ''
      } else if (!newUnit) {
        console.log('Empty business unit name provided')
      } else {
        console.log('Business unit already selected:', newUnit)
      }
    }

    const updateFormDataBusinessUnits = () => {
      formData.value.AffectedBusinessUnit = selectedBusinessUnits.value.join(', ')
      validateBusinessUnit() // Trigger validation when business units change
    }

    // Initialize categories from existing form data
    const initializeSelectedData = () => {
      // Initialize categories if RiskCategory has existing data
      if (formData.value.RiskCategory) {
        selectedCategories.value = formData.value.RiskCategory.split(', ').filter(cat => cat.trim())
      }
      
      // Initialize business units if AffectedBusinessUnit has existing data
      if (formData.value.AffectedBusinessUnit) {
        selectedBusinessUnits.value = formData.value.AffectedBusinessUnit.split(', ').filter(unit => unit.trim())
      }
    }

    // Load compliances when component mounts if needed
    onMounted(() => {
      // Fetch categories and business units on component mount
      fetchCategories()
      fetchBusinessUnits()
      
      // Initialize selected data from existing form data
      initializeSelectedData()
      
      // Add global click listener to close dropdown when clicking outside
      const handleClickOutside = (event) => {
        const complianceSelector = document.querySelector('.compliance-selector')
        const categoryDropdown = document.querySelector('.multi-select-dropdown')
        
        if (complianceSelector && !complianceSelector.contains(event.target)) {
          showDropdown.value = false
        }
        
        // Close category and business unit dropdowns when clicking outside
        if (categoryDropdown && !event.target.closest('.multi-select-dropdown')) {
          showCategoryDropdown.value = false
          showBusinessUnitDropdown.value = false
        }
      }
      
      document.addEventListener('click', handleClickOutside)
      
      // Cleanup listener on unmount
      onUnmounted(() => {
        document.removeEventListener('click', handleClickOutside)
      })
    })

    return {
      formData,
      validationErrors,
      compliances,
      complianceSearchTerm,
      selectedCompliance,
      loadingCompliances,
      showDropdown,
      showComplianceMapping,
      filteredCompliances,
      // Category dropdown
      availableCategories,
      selectedCategories,
      categorySearchTerm,
      showCategoryDropdown,
      filteredCategories,
      // Business Unit dropdown
      availableBusinessUnits,
      selectedBusinessUnits,
      businessUnitSearchTerm,
      showBusinessUnitDropdown,
      filteredBusinessUnits,
      // Methods
      onClassificationChange,
      selectCompliance,
      clearCompliance,
      filterCompliances,
      hideDropdownDelayed,
      // Category methods
      fetchCategories,
      toggleCategoryDropdown,
      filterCategories,
      toggleCategory,
      removeCategory,
      addCustomCategory,
      updateFormDataCategories,
      // Business Unit methods
      fetchBusinessUnits,
      toggleBusinessUnitDropdown,
      filterBusinessUnits,
      toggleBusinessUnit,
      removeBusinessUnit,
      addCustomBusinessUnit,
      updateFormDataBusinessUnits,
      initializeSelectedData,
      // Debug methods
      debugValidation: () => {
        console.log('=== MANUAL DEBUG ===')
        console.log('Selected categories:', selectedCategories.value)
        console.log('Available categories:', availableCategories.value)
        console.log('Form RiskCategory:', formData.value.RiskCategory)
        console.log('Validation errors:', validationErrors.value)
        
        // Test pattern for "HEALTH RISK"
        const testCategory = "HEALTH RISK"
        console.log(`Business pattern test for "${testCategory}":`, BUSINESS_TEXT_PATTERN.test(testCategory))
        console.log(`Category pattern test for "${testCategory}":`, CATEGORY_PATTERN.test(testCategory))
        
        // Manually trigger validation
        validateRiskCategory()
        console.log('After manual validation:', validationErrors.value)
      },
      clearAllErrors: () => {
        validationErrors.value = {}
        console.log('Cleared all validation errors')
      },
      // Validation methods
      validateCost,
      validateIncidentTitle,
      validateDescription,
      validateOrigin,
      validateDate,
      validateTime,
      validateRiskPriority,
      validateRiskCategory,
      validateCriticality,
      validatePossibleDamage,
      validateBusinessUnit,
      validateGeographicLocation,
      validateSystemsInvolved,
      validateInitialImpact,
      validateMitigation,
      validateComments,
      validateInternalContacts,
      validateExternalParties,
      validateRegulatoryBodies,
      validateViolatedPolicies,
      validateControlFailures,
      validateAndSubmit,
      submitForm,
      cancel,
      generateAnalysis,
      incidentType,
      isReadyToSubmit
    }
  }
}
</script>

<style>
/* Enhanced validation styles */
.validation-error {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 4px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.validation-error::before {
  content: "⚠️";
  font-size: 12px;
}

/* Apply red border to fields with validation errors */
input:invalid, 
textarea:invalid, 
select:invalid,
input[aria-invalid="true"],
textarea[aria-invalid="true"],
select[aria-invalid="true"] {
  border-color: #e74c3c !important;
  background-color: rgba(231, 76, 60, 0.05);
  box-shadow: 0 0 0 1px rgba(231, 76, 60, 0.2);
}

/* Valid state styling */
input:valid:not(:placeholder-shown),
textarea:valid:not(:placeholder-shown),
select:valid {
  border-color: #27ae60;
  background-color: rgba(39, 174, 96, 0.05);
}

/* Focus states */
input:focus,
textarea:focus,
select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

input:focus:invalid,
textarea:focus:invalid,
select:focus:invalid {
  box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2);
}

/* Real-time validation feedback animation */
.validation-error {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Field labels for required fields */
label span::after {
  content: "";
}

label.required span::after {
  content: " *";
  color: #e74c3c;
  font-weight: bold;
}
</style>
  
  