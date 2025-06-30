<template>
  <div class="tailoring-container" @click="closeAllEntityDropdowns">
    <h2 class="page-title">Policy Tailoring & Templating</h2>
    
    <!-- Framework Dropdown -->
    <div class="dropdown-container">
      <div v-if="!showPolicyDropdown" class="filter-group">
        <label for="frameworkSelect">SELECT FRAMEWORK</label>
        <div class="select-wrapper">
          <select id="frameworkSelect" v-model="selectedFramework" @change="onFrameworkDropdown" title="Select a framework to tailor and customize">
            <option value="" disabled selected>Select a framework</option>
            <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
              {{ framework.name }}
            </option>
          </select>
        </div>
        <p class="helper-text framework-note">
          <i class="fas fa-info-circle"></i>
          Only internal, approved, and active frameworks are available for tailoring
        </p>
        <button class="switch-btn" @click="switchToPolicy" title="Switch to copying individual policies instead of entire frameworks">Switch to Policy Dropdown</button>
      </div>
    </div>
    <!-- Policy Dropdown -->
    <div v-if="showPolicyDropdown" class="filter-group">
      <label for="policySelect">Select Policy</label>
      <div class="select-wrapper">
        <select id="policySelect" v-model="selectedPolicy" @change="onPolicyDropdown" title="Select a policy to copy to a target framework">
          <option value="" disabled selected>Select a policy</option>
          <option v-for="(policy, idx) in policyOptions" :key="idx" :value="idx">
            {{ policy.title }}
          </option>
        </select>
      </div>
      <button v-if="selectedPolicy === ''" class="switch-btn" @click="switchToFramework" title="Switch back to copying entire frameworks">Switch to Framework Dropdown</button>
    </div>

    <div v-if="showStepper" class="stepper-container">
      <div class="stepper">
        <div class="stepper-tabs-scroll">
          <div
            v-for="(tab, idx) in stepTabs"
            :key="tab.key"
            :class="['step', { active: stepIndex === idx }]"
            @click="stepIndex = idx"
            :title="`Navigate to ${tab.label} section`"
          >
            {{ tab.label }}
            <span
              v-if="idx !== 0"
              class="tab-close"
              @click.stop="closeTab(idx)"
              style="margin-left: 8px; cursor: pointer;"
              title="Close this policy tab"
            >X</span>
          </div>
        </div>
        <button v-if="stepTabs.length > 1 && !showPolicyDropdown" class="add-btn add-policy-btn" @click="addPolicy" title="Add a new policy to this framework">+ Add Policy</button>
      </div>
      <div class="step-content">
        <!-- Framework Form - Only show when not in policy mode -->
        <div v-if="stepIndex === 0 && !showPolicyDropdown">
          <form class="form-section" @submit.prevent="submitFrameworkForm">
            <div class="form-row">
              <div class="form-group">
                <label>Title:</label>
                <input type="text" v-model="frameworkData.title" required title="Enter a descriptive name for your tailored framework" />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="frameworkData.description" required title="Provide a detailed description of the framework's purpose and scope"></textarea>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Category:</label>
                <input type="text" v-model="frameworkData.category" required title="Specify the category or domain this framework belongs to (e.g., Cybersecurity, Financial)" />
              </div>
              <div class="form-group">
                <label>Start Date:</label>
                <input type="date" v-model="frameworkData.startDate" required title="Select when this framework becomes effective" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>End Date:</label>
                <input type="date" v-model="frameworkData.endDate" required title="Select when this framework expires or needs review" />
              </div>
              <div class="form-group">
                <label>Document URL:</label>
                <div class="input-with-icon" title="Upload a supporting document for this framework">
                  <input
                    type="url"
                    v-model="frameworkData.docURL"
                    placeholder="URL will appear here"
                    readonly
                    title="The document URL will appear here after upload"
                  />
                  <button type="button" class="browse-btn" @click="() => $refs.frameworkFileInput.click()" title="Browse and upload a framework document">Browse</button>
                  <input type="file" ref="frameworkFileInput" style="display:none" @change="onFrameworkFileChange" />
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Identifier:
                  <span v-if="isInternalFramework()" class="auto-generated-label">
                    (Auto-generated)
                  </span>
                </label>
                <input type="text" v-model="frameworkData.identifier" :readonly="isInternalFramework()" required title="Enter a unique identifier or code for this framework" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Created By</label>
                <select v-model="frameworkData.createdByName" required title="Select the person responsible for creating this framework">
                  <option value="">Select Creator</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Reviewer</label>
                <select v-model="frameworkData.reviewer" required title="Select the person who will review and approve this framework">
                  <option value="">Select Reviewer</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
            </div>
          </form>
        </div>
        <!-- Policy Form -->
        <div v-else>
          <form class="form-section policy-form" @submit.prevent="submitFrameworkForm">
            <h3 class="form-title">Policy Details</h3>
            <!-- Add Framework Selection Dropdown -->
            <div v-if="showPolicyDropdown" class="form-group span-full">
              <label>Select Target Framework</label>
              <select v-model="selectedFramework" class="framework-select" required title="Choose the framework where you want to copy this policy">
                <option value="">Select a framework</option>
                <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
                  {{ framework.name }}
                </option>
              </select>
              <p class="helper-text">Select the framework where you want to copy this policy</p>
            </div>
            <!-- Policy Forms Container -->
            <!-- Show only the selected policy form in framework copy mode -->
            <div v-if="!showPolicyDropdown && stepIndex > 0 && policiesData[stepIndex - 1]" class="policy-form-container">
              <div class="policy-header">
                <h4>Policy {{ stepIndex }}</h4>
                <div class="policy-actions">
                  <button 
                    type="button" 
                    class="exclude-btn" 
                    :class="{ 'excluded': policiesData[stepIndex - 1].exclude }"
                    @click="togglePolicyExclusion(stepIndex - 1)"
                    :title="policiesData[stepIndex - 1].exclude ? 'Click to include this policy in the framework' : 'Click to exclude this policy from the framework'"
                  >
                    {{ policiesData[stepIndex - 1].exclude ? 'Excluded' : 'Exclude' }}
                  </button>
                  <button 
                    type="button" 
                    class="remove-btn" 
                    @click="removePolicyFromCopy(stepIndex - 1)"
                    title="Remove this policy from the framework completely"
                  >
                    Remove Policy
                  </button>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Title</label>
                  <input type="text" v-model="policiesData[stepIndex - 1].title" @input="handlePolicyTitleChange(stepIndex - 1)" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter policy title" title="Enter a clear and descriptive name for this policy" />
                </div>
                <div class="form-group">
                  <label>Description</label>
                  <textarea v-model="policiesData[stepIndex - 1].description" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter policy description" title="Provide a comprehensive description of what this policy covers"></textarea>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Policy Type</label>
                  <div class="searchable-select">
                    <input
                      type="text"
                      placeholder="Search or enter new policy type"
                      v-model="policiesData[stepIndex - 1].PolicyType"
                      @input="handlePolicyTypeChange(stepIndex - 1, $event.target.value)"
                      list="policyTypes"
                      :disabled="policiesData[stepIndex - 1].exclude"
                      title="Select or enter the type/category of this policy (e.g., Security, Operational, Financial)"
                    />
                    <datalist id="policyTypes">
                      <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                    </datalist>
                  </div>
                </div>
                <div class="form-group">
                  <label>Policy Category</label>
                  <div class="searchable-select">
                    <input
                      type="text"
                      placeholder="Search or enter new category"
                      v-model="policiesData[stepIndex - 1].PolicyCategory"
                      @input="handlePolicyCategoryChange(stepIndex - 1, $event.target.value)"
                      list="policyCategories"
                      :disabled="!policiesData[stepIndex - 1].PolicyType || policiesData[stepIndex - 1].exclude"
                      title="Select or enter a more specific category within the policy type"
                    />
                    <datalist id="policyCategories">
                      <option v-for="cat in getCategoriesForType(policiesData[stepIndex - 1].PolicyType)" :key="cat" :value="cat">{{ cat }}</option>
                    </datalist>
                  </div>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Policy Sub Category</label>
                  <div class="searchable-select">
                    <input
                      type="text"
                      placeholder="Search or enter new sub category"
                      v-model="policiesData[stepIndex - 1].PolicySubCategory"
                      @input="handlePolicySubCategoryChange(stepIndex - 1, $event.target.value)"
                      list="policySubCategories"
                      :disabled="!policiesData[stepIndex - 1].PolicyCategory || policiesData[stepIndex - 1].exclude"
                      title="Select or enter a detailed sub-category for precise policy classification"
                    />
                    <datalist id="policySubCategories">
                      <option v-for="sub in getSubCategoriesForCategory(policiesData[stepIndex - 1].PolicyType, policiesData[stepIndex - 1].PolicyCategory)" :key="sub" :value="sub">{{ sub }}</option>
                    </datalist>
                  </div>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Objective</label>
                  <textarea v-model="policiesData[stepIndex - 1].objective" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter policy objective" title="Describe the main goals and objectives this policy aims to achieve"></textarea>
                </div>
                <div class="form-group">
                  <label>Scope</label>
                  <textarea v-model="policiesData[stepIndex - 1].scope" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter policy scope" title="Define the boundaries and areas covered by this policy"></textarea>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Department</label>
                  <input type="text" v-model="policiesData[stepIndex - 1].department" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter department" title="Specify the department or business unit responsible for this policy" />
                </div>
                <div class="form-group">
                  <label>Applicability</label>
                  <input type="text" v-model="policiesData[stepIndex - 1].applicability" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter applicability" title="Define who or what this policy applies to (e.g., all employees, specific roles, systems)" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date</label>
                  <input type="date" v-model="policiesData[stepIndex - 1].startDate" :required="!policiesData[stepIndex - 1].exclude" title="Select when this policy becomes effective" />
                </div>
                <div class="form-group">
                  <label>End Date</label>
                  <input type="date" v-model="policiesData[stepIndex - 1].endDate" :required="!policiesData[stepIndex - 1].exclude" title="Select when this policy expires or needs review" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Document URL</label>
                  <div class="input-with-icon" title="Upload a supporting document for this policy">
                    <input
                      type="url"
                      v-model="policiesData[stepIndex - 1].docURL"
                      placeholder=" URL will appear here"
                      readonly
                      title="The document URL will appear here after upload"
                    />
                    <button type="button" class="browse-btn" @click="triggerPolicyFileInput(stepIndex - 1)" title="Browse and upload a policy document">Browse</button>
                    <input type="file" :ref="'policyFileInput' + (stepIndex - 1)" style="display:none" @change="e => onPolicyFileChange(e, stepIndex - 1)" />
                  </div>
                </div>
                <div class="form-group">
                  <label>Identifier
                    <span v-if="isInternalFramework()" class="auto-generated-label">
                      (Auto-generated)
                    </span>
                  </label>
                  <input type="text" v-model="policiesData[stepIndex - 1].identifier" :readonly="isInternalFramework()" :required="!policiesData[stepIndex - 1].exclude" placeholder="Enter identifier" title="Enter a unique identifier or code for this policy" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Coverage Rate (%)</label>
                  <input 
                    type="number" 
                    v-model="policiesData[stepIndex - 1].coverageRate" 
                    min="0" 
                    max="100" 
                    step="0.01" 
                    placeholder="Enter coverage rate"
                    :required="!policiesData[stepIndex - 1].exclude"
                    title="Enter the percentage of coverage this policy provides (0-100%)"
                  />
                </div>
              </div>

              <!-- Entities Multi-Select -->
              <div class="form-row">
                <div class="form-group entities-group">
                  <label>Applicable Entities</label>
                  <div class="entities-multi-select" @click.stop>
                    <div class="entities-dropdown">
                      <div 
                        class="selected-entities" 
                        :class="{ active: policiesData[stepIndex - 1].showEntitiesDropdown }"
                        @click="toggleEntitiesDropdown(stepIndex - 1)"
                      >
                        <div class="entity-content">
                          <span v-if="isAllEntitiesSelected(stepIndex - 1)" class="entity-tag all-tag">
                            All Locations
                          </span>
                          <span v-else-if="getSelectedEntitiesCount(stepIndex - 1) === 0" class="placeholder">
                            Select entities...
                          </span>
                          <span v-else class="entity-count">
                            {{ getSelectedEntitiesCount(stepIndex - 1) }} location(s) selected
                          </span>
                        </div>
                        <i class="fas fa-chevron-down dropdown-arrow"></i>
                      </div>
                      <div v-if="policiesData[stepIndex - 1].showEntitiesDropdown" class="entities-options">
                        <div 
                          v-for="entity in entities" 
                          :key="entity.id" 
                          :class="['entity-option', { 'all-option': entity.id === 'all' }]"
                          @click="selectEntity(stepIndex - 1, entity.id)"
                        >
                          <input 
                            type="checkbox" 
                            :checked="entity.id === 'all' ? isAllEntitiesSelected(stepIndex - 1) : getSelectedEntityIds(stepIndex - 1).includes(entity.id)"
                            @change="handleEntitySelection(stepIndex - 1, entity.id, $event.target.checked)"
                            @click.stop
                          />
                          <span class="entity-label">{{ entity.label }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="subpolicies-section">
                <h4>Sub Policies</h4>
                <div class="subpolicies-row">
                  <div v-for="(sub, subIdx) in policiesData[stepIndex - 1].subPolicies" :key="subIdx" class="subpolicy-card">
                    <div class="subpolicy-header">
                      <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                      <div class="subpolicy-actions">
                        <button 
                          type="button" 
                          class="exclude-btn" 
                          :class="{ 'excluded': sub.exclude }"
                          @click="toggleSubPolicyExclusion(stepIndex - 1, subIdx)"
                          :title="sub.exclude ? 'Click to include this sub-policy' : 'Click to exclude this sub-policy'"
                        >
                          {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                        </button>
                        <button 
                          type="button" 
                          class="remove-btn" 
                          @click="removeSubPolicy(stepIndex - 1, subIdx)"
                          title="Remove this sub-policy completely"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Title</label>
                      <input type="text" v-model="sub.title" @input="handleSubPolicyTitleChange(stepIndex - 1, subIdx)" required :disabled="sub.exclude" placeholder="Enter sub-policy title" title="Enter a descriptive name for this sub-policy" />
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Description</label>
                      <textarea v-model="sub.description" required :disabled="sub.exclude" placeholder="Enter sub-policy description" title="Provide a detailed description of this sub-policy"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Control</label>
                      <textarea v-model="sub.control" required :disabled="sub.exclude" placeholder="Enter control details" title="Describe the specific controls or measures implemented by this sub-policy"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Identifier
                        <span v-if="isInternalFramework()" class="auto-generated-label">
                          (Auto-generated)
                        </span>
                      </label>
                      <input type="text" v-model="sub.identifier" :readonly="isInternalFramework()" required :disabled="sub.exclude" placeholder="Enter identifier" title="Enter a unique identifier or code for this sub-policy" />
                    </div>
                  </div>
                </div>
                <button type="button" class="add-btn" @click="addSubPolicy(stepIndex - 1)" title="Add a new sub-policy to this policy">+ Add Sub Policy</button>
              </div>
            </div>
            <!-- Policy Dropdown Mode: show all policies as before -->
            <div v-if="showPolicyDropdown">
              <div v-if="showPolicyDropdown && policiesData[stepIndex]" class="policy-form-container">
                <div class="policy-header">
                  <h4>Policy {{ stepIndex + 1 }}</h4>
                  <div class="policy-actions">
                    <button 
                      type="button" 
                      class="exclude-btn" 
                      :class="{ 'excluded': policiesData[stepIndex].exclude }"
                      @click="togglePolicyExclusion(stepIndex)"
                      :title="policiesData[stepIndex].exclude ? 'Click to include this policy' : 'Click to exclude this policy'"
                    >
                      {{ policiesData[stepIndex].exclude ? 'Excluded' : 'Exclude' }}
                    </button>
                    <button 
                      type="button" 
                      class="remove-btn" 
                      @click="removePolicyFromCopy(stepIndex)"
                      title="Remove this policy completely"
                    >
                      Remove Policy
                    </button>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Title</label>
                    <input type="text" v-model="policiesData[stepIndex].title" @input="handlePolicyTitleChange(stepIndex)" :required="!policiesData[stepIndex].exclude" placeholder="Enter policy title" title="Enter a clear and descriptive name for this policy" />
                  </div>
                  <div class="form-group">
                    <label>Description</label>
                    <textarea v-model="policiesData[stepIndex].description" :required="!policiesData[stepIndex].exclude" placeholder="Enter policy description" title="Provide a comprehensive description of what this policy covers"></textarea>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Policy Type</label>
                    <div class="searchable-select">
                      <input
                        type="text"
                        placeholder="Search or enter new policy type"
                        v-model="policiesData[stepIndex].PolicyType"
                        @input="handlePolicyTypeChange(stepIndex, $event.target.value)"
                        list="policyTypes"
                        :disabled="policiesData[stepIndex].exclude"
                        title="Select or enter the type/category of this policy (e.g., Security, Operational, Financial)"
                      />
                      <datalist id="policyTypes">
                        <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                      </datalist>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>Policy Category</label>
                    <div class="searchable-select">
                      <input
                        type="text"
                        placeholder="Search or enter new category"
                        v-model="policiesData[stepIndex].PolicyCategory"
                        @input="handlePolicyCategoryChange(stepIndex, $event.target.value)"
                        list="policyCategories"
                        :disabled="!policiesData[stepIndex].PolicyType || policiesData[stepIndex].exclude"
                        title="Select or enter a more specific category within the policy type"
                      />
                      <datalist id="policyCategories">
                        <option v-for="cat in getCategoriesForType(policiesData[stepIndex].PolicyType)" :key="cat" :value="cat">{{ cat }}</option>
                      </datalist>
                    </div>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Policy Sub Category</label>
                    <div class="searchable-select">
                      <input
                        type="text"
                        placeholder="Search or enter new sub category"
                        v-model="policiesData[stepIndex].PolicySubCategory"
                        @input="handlePolicySubCategoryChange(stepIndex, $event.target.value)"
                        list="policySubCategories"
                        :disabled="!policiesData[stepIndex].PolicyCategory || policiesData[stepIndex].exclude"
                        title="Select or enter a detailed sub-category for precise policy classification"
                      />
                      <datalist id="policySubCategories">
                        <option v-for="sub in getSubCategoriesForCategory(policiesData[stepIndex].PolicyType, policiesData[stepIndex].PolicyCategory)" :key="sub" :value="sub">{{ sub }}</option>
                      </datalist>
                    </div>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Objective</label>
                    <textarea v-model="policiesData[stepIndex].objective" :required="!policiesData[stepIndex].exclude" placeholder="Enter policy objective" title="Describe the main goals and objectives this policy aims to achieve"></textarea>
                  </div>
                  <div class="form-group">
                    <label>Scope</label>
                    <textarea v-model="policiesData[stepIndex].scope" :required="!policiesData[stepIndex].exclude" placeholder="Enter policy scope" title="Define the boundaries and areas covered by this policy"></textarea>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Department</label>
                    <input type="text" v-model="policiesData[stepIndex].department" :required="!policiesData[stepIndex].exclude" placeholder="Enter department" title="Specify the department or business unit responsible for this policy" />
                  </div>
                  <div class="form-group">
                    <label>Applicability</label>
                    <input type="text" v-model="policiesData[stepIndex].applicability" :required="!policiesData[stepIndex].exclude" placeholder="Enter applicability" title="Define who or what this policy applies to (e.g., all employees, specific roles, systems)" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Start Date</label>
                    <input type="date" v-model="policiesData[stepIndex].startDate" :required="!policiesData[stepIndex].exclude" title="Select when this policy becomes effective" />
                  </div>
                  <div class="form-group">
                    <label>End Date</label>
                    <input type="date" v-model="policiesData[stepIndex].endDate" :required="!policiesData[stepIndex].exclude" title="Select when this policy expires or needs review" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Document URL</label>
                    <div class="input-with-icon" title="Upload a supporting document for this policy">
                      <input
                        type="url"
                        v-model="policiesData[stepIndex].docURL"
                        placeholder=" URL will appear here"
                        readonly
                        title="The document URL will appear here after upload"
                      />
                      <button type="button" class="browse-btn" @click="triggerPolicyFileInput(stepIndex)" title="Browse and upload a policy document">Browse</button>
                      <input type="file" :ref="'policyFileInput' + stepIndex" style="display:none" @change="e => onPolicyFileChange(e, stepIndex)" />
                    </div>
                  </div>
                  <div class="form-group">
                    <label>Identifier
                      <span v-if="isInternalFramework()" class="auto-generated-label">
                        (Auto-generated)
                      </span>
                    </label>
                    <input type="text" v-model="policiesData[stepIndex].identifier" :readonly="isInternalFramework()" :required="!policiesData[stepIndex].exclude" placeholder="Enter identifier" title="Enter a unique identifier or code for this policy" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Coverage Rate (%)</label>
                    <input 
                      type="number" 
                      v-model="policiesData[stepIndex].coverageRate" 
                      min="0" 
                      max="100" 
                      step="0.01" 
                      placeholder="Enter coverage rate"
                      :required="!policiesData[stepIndex].exclude"
                      title="Enter the percentage of coverage this policy provides (0-100%)"
                    />
                  </div>
                </div>

                <!-- Entities Multi-Select -->
                <div class="form-row">
                  <div class="form-group entities-group">
                    <label>Applicable Entities</label>
                    <div class="entities-multi-select" @click.stop>
                      <div class="entities-dropdown">
                        <div 
                          class="selected-entities" 
                          :class="{ active: policiesData[stepIndex].showEntitiesDropdown }"
                          @click="toggleEntitiesDropdown(stepIndex)"
                        >
                          <div class="entity-content">
                            <span v-if="isAllEntitiesSelected(stepIndex)" class="entity-tag all-tag">
                              All Locations
                            </span>
                            <span v-else-if="getSelectedEntitiesCount(stepIndex) === 0" class="placeholder">
                              Select entities...
                            </span>
                            <span v-else class="entity-count">
                              {{ getSelectedEntitiesCount(stepIndex) }} location(s) selected
                            </span>
                          </div>
                          <i class="fas fa-chevron-down dropdown-arrow"></i>
                        </div>
                        <div v-if="policiesData[stepIndex].showEntitiesDropdown" class="entities-options">
                          <div 
                            v-for="entity in entities" 
                            :key="entity.id" 
                            :class="['entity-option', { 'all-option': entity.id === 'all' }]"
                            @click="selectEntity(stepIndex, entity.id)"
                          >
                            <input 
                              type="checkbox" 
                              :checked="entity.id === 'all' ? isAllEntitiesSelected(stepIndex) : getSelectedEntityIds(stepIndex).includes(entity.id)"
                              @change="handleEntitySelection(stepIndex, entity.id, $event.target.checked)"
                              @click.stop
                            />
                            <span class="entity-label">{{ entity.label }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="showPolicyDropdown" class="form-row">
                  <div class="form-group">
                    <label>Created By</label>
                    <select v-model="policiesData[stepIndex].createdByName" :required="!policiesData[stepIndex].exclude" title="Select the person responsible for creating this policy">
                      <option value="">Select Creator</option>
                      <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                        {{ user.UserName }}
                      </option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Reviewer</label>
                    <select v-model="policiesData[stepIndex].reviewer" :required="!policiesData[stepIndex].exclude" title="Select the person who will review and approve this policy">
                      <option value="">Select Reviewer</option>
                      <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                        {{ user.UserName }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="subpolicies-section">
                  <h4>Sub Policies</h4>
                  <div class="subpolicies-row">
                    <div v-for="(sub, subIdx) in policiesData[stepIndex].subPolicies" :key="subIdx" class="subpolicy-card">
                      <div class="subpolicy-header">
                        <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                        <div class="subpolicy-actions">
                          <button 
                            type="button" 
                            class="exclude-btn" 
                            :class="{ 'excluded': sub.exclude }"
                            @click="toggleSubPolicyExclusion(stepIndex, subIdx)"
                            :title="sub.exclude ? 'Click to include this sub-policy' : 'Click to exclude this sub-policy'"
                          >
                            {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                          </button>
                          <button 
                            type="button" 
                            class="remove-btn" 
                            @click="removeSubPolicy(stepIndex, subIdx)"
                            title="Remove this sub-policy completely"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                      <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Title</label>
                        <input type="text" v-model="sub.title" @input="handleSubPolicyTitleChange(stepIndex, subIdx)" required :disabled="sub.exclude" placeholder="Enter sub-policy title" title="Enter a descriptive name for this sub-policy" />
                      </div>
                      <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Description</label>
                        <textarea v-model="sub.description" required :disabled="sub.exclude" placeholder="Enter sub-policy description" title="Provide a detailed description of this sub-policy"></textarea>
                      </div>
                      <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Control</label>
                        <textarea v-model="sub.control" required :disabled="sub.exclude" placeholder="Enter control details" title="Describe the specific controls or measures implemented by this sub-policy"></textarea>
                      </div>
                      <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Identifier
                          <span v-if="isInternalFramework()" class="auto-generated-label">
                            (Auto-generated)
                          </span>
                        </label>
                        <input type="text" v-model="sub.identifier" :readonly="isInternalFramework()" required :disabled="sub.exclude" placeholder="Enter identifier" title="Enter a unique identifier or code for this sub-policy" />
                      </div>
                    </div>
                  </div>
                  <button type="button" class="add-btn" @click="addSubPolicy(stepIndex)" title="Add a new sub-policy to this policy">+ Add Sub Policy</button>
                </div>
              </div>
            </div>
            <button class="create-btn" type="submit" :title="showPolicyDropdown ? 'Copy the selected policy to the target framework' : 'Create the tailored framework with all policies'">
              {{ showPolicyDropdown ? 'Copy Policy' : 'Create Framework' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, getCurrentInstance } from 'vue'
import axios from 'axios'
import { PopupService, PopupModal } from '@/modules/popus'

const API_BASE_URL = 'http://localhost:8000/api'

export default {
  name: 'PolicyTailoring',
  components: {
    PopupModal
  },
  setup() {
    const selectedFramework = ref('')
    const selectedPolicy = ref('')
    const showStepper = ref(false)
    const showPolicyDropdown = ref(false)
    const stepIndex = ref(0)
    const loading = ref(false)
    const error = ref(null)

    const frameworks = ref([])
    const policyOptions = ref([])
    const users = ref([])

    const frameworkData = ref({
      title: '',
      description: '',
      category: '',
      startDate: '',
      endDate: '',
      docURL: '',
      identifier: '',
      createdByName: '',
      reviewer: ''
    })

    const policiesData = ref([{
      title: '',
      description: '',
      objective: '',
      scope: '',
      department: '',
      applicability: '',
      startDate: '',
      endDate: '',
      docURL: '',
      identifier: '',
      coverageRate: null,
      Entities: [],
      showEntitiesDropdown: false,
      subPolicies: []
    }])

    const frameworkFileName = ref('');
    const { proxy } = getCurrentInstance();

    const policyCategories = ref([])
    const policyTypes = ref([])
    const entities = ref([])

    // Add new reactive ref for tracking existing framework identifiers
    const existingFrameworkIdentifiers = ref([])

    const onFrameworkFileChange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        frameworkFileName.value = file.name;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('userId', users.value[0]?.UserId || 'default');
        formData.append('fileName', file.name);
        formData.append('type', 'framework');
        formData.append('frameworkName', frameworkData.value.title);

        try {
          const uploadResponse = await axios.post('http://localhost:3000/api/upload', formData);
          if (uploadResponse.data.success) {
            frameworkData.value.docURL = uploadResponse.data.file.url;
          }
        } catch (err) {
          PopupService.error('Failed to upload framework document', 'Upload Error');
        }
      }
    };

    const onPolicyFileChange = async (e, idx) => {
      const file = e.target.files[0];
      if (file) {
        policiesData.value[idx].fileName = file.name;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('userId', users.value[0]?.UserId || 'default');
        formData.append('fileName', file.name);
        formData.append('type', 'policy');
        formData.append('policyName', policiesData.value[idx].title);

        try {
          const uploadResponse = await axios.post('http://localhost:3000/api/upload', formData);
          if (uploadResponse.data.success) {
            policiesData.value[idx].docURL = uploadResponse.data.file.url;
          }
        } catch (err) {
          PopupService.error('Failed to upload policy document', 'Upload Error');
        }
      }
    };

    // Add identifier generation functions
    const generateFrameworkIdentifier = async (frameworkName) => {
      if (!frameworkName || frameworkName.length < 4) return ''
      
      const prefix = frameworkName.substring(0, 4).toUpperCase()
      let counter = 1
      let identifier = `${prefix}${counter}`
      
      // Check against existing identifiers
      while (existingFrameworkIdentifiers.value.includes(identifier)) {
        counter++
        identifier = `${prefix}${counter}`
      }
      
      return identifier
    }

    const generatePolicyIdentifier = (policyName) => {
      if (!policyName) return ''
      
      // Split by spaces and take first letter of each word
      const words = policyName.split(' ').filter(word => word.length > 0)
      return words.map(word => word.charAt(0).toUpperCase()).join('')
    }

    const generateSubPolicyIdentifier = (policyIdentifier, subPolicyIndex) => {
      if (!policyIdentifier) return ''
      return `${policyIdentifier}-${subPolicyIndex + 1}`
    }

    // Fetch existing framework identifiers
    const fetchExistingFrameworkIdentifiers = async () => {
      try {
        // Use include_all_for_identifiers parameter to get ALL frameworks regardless of status
        // This ensures truly unique identifier generation
        const response = await axios.get(`${API_BASE_URL}/frameworks/`, {
          params: { include_all_for_identifiers: 'true' }
        })
        existingFrameworkIdentifiers.value = response.data.map(fw => fw.Identifier).filter(id => id)
      } catch (err) {
        console.error('Error fetching existing framework identifiers:', err)
      }
    }

    // Helper function to check if current context is for internal framework
    const isInternalFramework = () => {
      if (showPolicyDropdown.value) {
        // In policy dropdown mode, check if the selected target framework is internal
        if (selectedFramework.value) {
          const response = frameworks.value.find(fw => fw.id === selectedFramework.value)
          return response?.internalExternal === 'Internal'
        }
        return false
      } else {
        // In framework mode, check if the source framework is internal
        if (selectedFramework.value) {
          const response = frameworks.value.find(fw => fw.id === selectedFramework.value)
          return response?.internalExternal === 'Internal'
        }
        // For new frameworks being created in tailoring, they are typically internal
        return true
      }
    }

    // Auto-generate framework identifier when framework title changes
    const autoGenerateFrameworkIdentifier = async () => {
      if (isInternalFramework() && frameworkData.value.title) {
        const generatedId = await generateFrameworkIdentifier(frameworkData.value.title)
        frameworkData.value.identifier = generatedId
      } else if (!isInternalFramework()) {
        // Clear identifier for external frameworks
        frameworkData.value.identifier = ''
      }
    }

    // Auto-generate policy identifiers
    const autoGeneratePolicyIdentifiers = (policyIndex) => {
      const policy = policiesData.value[policyIndex]
      if (!policy) return

      if (isInternalFramework() && policy.title) {
        const generatedId = generatePolicyIdentifier(policy.title)
        policy.identifier = generatedId

        // Auto-generate subpolicy identifiers
        if (policy.subPolicies) {
          policy.subPolicies.forEach((subpolicy, subIndex) => {
            if (subpolicy.title) {
              subpolicy.identifier = generateSubPolicyIdentifier(generatedId, subIndex)
            }
          })
        }
      } else if (!isInternalFramework()) {
        // Clear identifiers for external frameworks
        policy.identifier = ''
        if (policy.subPolicies) {
          policy.subPolicies.forEach((subpolicy) => {
            subpolicy.identifier = ''
          })
        }
      }
    }

    // Auto-generate subpolicy identifier when subpolicy title changes
    const autoGenerateSubPolicyIdentifier = (policyIndex, subPolicyIndex) => {
      const policy = policiesData.value[policyIndex]
      const subpolicy = policy?.subPolicies?.[subPolicyIndex]
      if (!policy || !subpolicy) return

      if (isInternalFramework()) {
        // Ensure policy has identifier first
        if (policy.title && !policy.identifier) {
          autoGeneratePolicyIdentifiers(policyIndex)
        }
        
        // Generate subpolicy identifier if policy has identifier
        if (policy.identifier) {
          subpolicy.identifier = generateSubPolicyIdentifier(policy.identifier, subPolicyIndex)
        }
      } else if (!isInternalFramework()) {
        // Clear identifier for external frameworks
        subpolicy.identifier = ''
      }
    }

    // Watch for changes to auto-generate identifiers
    watch(() => frameworkData.value.title, autoGenerateFrameworkIdentifier)

    // Watch for framework selection changes to update all identifiers
    watch(() => selectedFramework.value, () => {
      // Re-generate all identifiers when framework selection changes
      if (frameworkData.value.title) {
        autoGenerateFrameworkIdentifier()
      }
      
      policiesData.value.forEach((policy, policyIndex) => {
        if (policy.title) {
          autoGeneratePolicyIdentifiers(policyIndex)
        }
      })
    })

    // Fetch frameworks for dropdown
    const fetchFrameworks = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        // Filter for only Internal, Approved, and Active frameworks for tailoring
        frameworks.value = response.data
          .filter(fw => 
            fw.InternalExternal === 'Internal' && 
            fw.Status === 'Approved' && 
            fw.ActiveInactive === 'Active'
          )
          .map(fw => ({
            id: fw.FrameworkId,
            name: fw.FrameworkName,
            internalExternal: fw.InternalExternal
          }))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        PopupService.error('Failed to fetch frameworks', 'Loading Error')
      }
    }

    // Fetch framework details when selected
    const onFrameworkDropdown = async () => {
      if (!selectedFramework.value) return
      
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/${selectedFramework.value}/`)
        
        // Populate framework data
        frameworkData.value = {
          title: response.data.FrameworkName,
          description: response.data.FrameworkDescription,
          category: response.data.Category,
          startDate: response.data.StartDate,
          endDate: response.data.EndDate,
          docURL: response.data.DocURL,
          identifier: response.data.Identifier,
          createdByName: response.data.CreatedByName,
          reviewer: response.data.Reviewer
        }

        // Populate policies data
        policiesData.value = response.data.policies.map(p => ({
          id: p.PolicyId,
          title: p.PolicyName,
          description: p.PolicyDescription,
          objective: p.Objective,
          scope: p.Scope,
          department: p.Department,
          applicability: p.Applicability,
          startDate: p.StartDate,
          endDate: p.EndDate,
          docURL: p.DocURL,
          identifier: p.Identifier,
          coverageRate: p.CoverageRate || null,
          Entities: p.Entities || [],
          showEntitiesDropdown: false,
          subPolicies: p.subpolicies.map(sp => ({
            id: sp.SubPolicyId,
            title: sp.SubPolicyName,
            description: sp.Description,
            control: sp.Control,
            identifier: sp.Identifier
          }))
        }))

        showStepper.value = true
        stepIndex.value = 0
        showPolicyDropdown.value = false
        selectedPolicy.value = ''
      } catch (err) {
        console.error('Error fetching framework details:', err)
        PopupService.error('Failed to fetch framework details', 'Loading Error')
      } finally {
        loading.value = false
      }
    }

    // Fetch policies for dropdown
    const fetchPolicies = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/policies/`)
        // Check if response.data has a policies property and filter for Approved and Active policies
        const policiesData = response.data.policies || response.data
        policyOptions.value = policiesData
          .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
          .map(p => ({
            id: p.PolicyId,
            title: p.PolicyName,
            description: p.PolicyDescription
          }))
      } catch (err) {
        console.error('Error fetching policies:', err)
        PopupService.error('Failed to fetch policies', 'Loading Error')
      } finally {
        loading.value = false
      }
    }

    // Fetch policy details when selected
    const onPolicyDropdown = async () => {
      if (selectedPolicy.value === '') return
      
      try {
        loading.value = true
        const selectedPolicyData = policyOptions.value[selectedPolicy.value]
        if (!selectedPolicyData?.id) {
          throw new Error('Invalid policy selection')
        }

        const response = await axios.get(`${API_BASE_URL}/policies/${selectedPolicyData.id}/`)
        
        // Verify policy is Approved and Active
        if (response.data.Status !== 'Approved' || response.data.ActiveInactive !== 'Active') {
          throw new Error('Only Approved and Active policies can be copied')
        }
        
        // Reset framework selection
        selectedFramework.value = ''
        
        // Populate single policy data
        policiesData.value = [{
          id: response.data.PolicyId,
          title: response.data.PolicyName,
          description: response.data.PolicyDescription,
          objective: response.data.Objective || '',
          scope: response.data.Scope || '',
          department: response.data.Department || '',
          applicability: response.data.Applicability || '',
          startDate: response.data.StartDate || '',
          endDate: response.data.EndDate || '',
          docURL: response.data.DocURL || '',
          identifier: response.data.Identifier || '',
          coverageRate: response.data.CoverageRate || null,
          Entities: response.data.Entities || [],
          showEntitiesDropdown: false,
          // Filter for only Approved and Active subpolicies
          subPolicies: (response.data.subpolicies || [])
            .filter(sp => sp.Status === 'Approved')
            .map(sp => ({
              id: sp.SubPolicyId,
              title: sp.SubPolicyName,
              description: sp.Description,
              control: sp.Control || '',
              identifier: sp.Identifier || ''
            }))
        }]

        showStepper.value = true
        stepIndex.value = 0 // Show policy details immediately
        showPolicyDropdown.value = true

        // Fetch available frameworks for the target selection
        await selectTargetFramework()
      } catch (err) {
        console.error('Error fetching policy details:', err)
        PopupService.error(err.message || 'Failed to fetch policy details', 'Loading Error')
        policiesData.value = []
      } finally {
        loading.value = false
      }
    }

    // Update the selectTargetFramework function to filter out the current framework
    const selectTargetFramework = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        
        // Filter out inactive frameworks and sort by name
        frameworks.value = response.data
          .filter(fw => fw.ActiveInactive === 'Active')
          .map(fw => ({
            id: fw.FrameworkId,
            name: fw.FrameworkName,
            internalExternal: fw.InternalExternal
          }))
          .sort((a, b) => a.name.localeCompare(b.name))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        PopupService.error('Failed to fetch frameworks', 'Loading Error')
      } finally {
        loading.value = false
      }
    }

    // Add watch for framework selection
    watch(selectedFramework, (newValue) => {
      if (newValue && showPolicyDropdown.value) {
        error.value = null // Clear any previous errors
      }
    })

    const switchToPolicy = () => {
      showPolicyDropdown.value = true
      selectedFramework.value = ''
      showStepper.value = false
      policiesData.value = []
      frameworkData.value = {
        title: '',
        description: '',
        category: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: ''
      }
      fetchPolicies() // Fetch policies when switching to policy view
    }

    const switchToFramework = () => {
      showPolicyDropdown.value = false
      selectedPolicy.value = ''
      showStepper.value = false
      policiesData.value = []
      frameworkData.value = { title: '', description: '' }
      fetchFrameworks()
    }

    const addPolicy = () => {
      policiesData.value.push({
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        coverageRate: null,
        subPolicies: [],
        exclude: false,
        PolicyType: '',
        PolicyCategory: '',
        PolicySubCategory: '',
        Entities: [],
        showEntitiesDropdown: false
      })
      stepIndex.value = policiesData.value.length // Go to new policy tab
      
      // Auto-generate identifier for new policy only if it's an internal framework
      const newPolicyIndex = policiesData.value.length - 1
      if (isInternalFramework()) {
        // Add a small delay to ensure the policy form is rendered
        setTimeout(() => {
          autoGeneratePolicyIdentifiers(newPolicyIndex)
        }, 100)
      }
    }

    const removePolicy = (idx) => {
      // If this is an existing policy, mark it for exclusion in the API request
      if (policiesData.value[idx].id) {
        policiesData.value[idx].exclude = true
      } else {
        // If it's a new policy, remove it from the array
        policiesData.value.splice(idx, 1)
      }
      if (stepIndex.value > idx) stepIndex.value--
      if (stepIndex.value >= stepTabs.value.length) stepIndex.value = stepTabs.value.length - 1
    }

    const toggleSubPolicyExclusion = (policyIdx, subIdx) => {
      const subPolicy = policiesData.value[policyIdx].subPolicies[subIdx]
      subPolicy.exclude = !subPolicy.exclude
    }

    const removeSubPolicy = (policyIdx, subIdx) => {
      const subPolicy = policiesData.value[policyIdx].subPolicies[subIdx]
      if (subPolicy.id) {
        // If this is an existing subpolicy, mark it for exclusion
        subPolicy.exclude = true
      } else {
        // If it's a new subpolicy, remove it from the array
        policiesData.value[policyIdx].subPolicies.splice(subIdx, 1)
      }
    }

    const addSubPolicy = (policyIdx) => {
      policiesData.value[policyIdx].subPolicies.push({
        title: '',
        description: '',
        control: '',
        identifier: '',
        exclude: false,
        Status: 'Under Review',
        CreatedByName: policiesData.value[policyIdx].createdByName || '',
        CreatedByDate: new Date().toISOString().split('T')[0],
        PermanentTemporary: ''
      })
      
      // Auto-generate identifier for the newly added subpolicy only if it's an internal framework
      const newSubPolicyIndex = policiesData.value[policyIdx].subPolicies.length - 1
      if (isInternalFramework()) {
        // Ensure policy identifier is generated first if policy has a title
        const policy = policiesData.value[policyIdx]
        if (policy.title && !policy.identifier) {
          autoGeneratePolicyIdentifiers(policyIdx)
        }
        
        // Then generate subpolicy identifier
        autoGenerateSubPolicyIdentifier(policyIdx, newSubPolicyIndex)
      }
    }

    const closeTab = (idx) => {
      if (idx === 0) return // Don't close framework tab
      removePolicy(idx - 1)
    }

    // Add these methods in the setup function
    const addPolicyToCopy = () => {
      const newPolicy = {
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        coverageRate: null,
        subPolicies: [],
        exclude: false,
        PolicyType: '',
        PolicyCategory: '',
        PolicySubCategory: '',
        Entities: [],
        showEntitiesDropdown: false
      };
      policiesData.value.push(newPolicy);
      stepIndex.value = policiesData.value.length - 1;
    }

    const removePolicyFromCopy = (index) => {
      try {
        // Create a new array to ensure reactivity
        const updatedPolicies = [...policiesData.value];
        
        if (updatedPolicies[index]?.id) {
          // For existing policies, mark for exclusion
          updatedPolicies[index] = {
            ...updatedPolicies[index],
            exclude: true
          };
        } else {
          // For new policies, remove from array
          updatedPolicies.splice(index, 1);
        }
        
        // Update the reactive reference
        policiesData.value = updatedPolicies;
        
        // Update step index if needed
        if (stepIndex.value >= updatedPolicies.length) {
          stepIndex.value = Math.max(0, updatedPolicies.length - 1);
        }
      } catch (error) {
        console.error('Error removing policy:', error);
      }
    }

    // Update togglePolicyExclusion function
    const togglePolicyExclusion = async (index) => {
      try {
        console.log('Toggling policy exclusion for index:', index);
        console.log('Current policy state:', policiesData.value[index]);
        
        const updatedPolicies = [...policiesData.value];
        updatedPolicies[index] = {
          ...updatedPolicies[index],
          exclude: !updatedPolicies[index].exclude
        };
        
        console.log('Updated policy state:', updatedPolicies[index]);
        console.log('Policy excluded:', updatedPolicies[index].exclude);
        
        policiesData.value = updatedPolicies;
      } catch (error) {
        console.error('Error toggling policy exclusion:', error);
      }
    }

    // Update submitFrameworkForm function
    const submitFrameworkForm = async () => {
      try {
        loading.value = true;
        console.log('Starting form submission...');
        console.log('Current policies data:', policiesData.value);

        // Save any new policy categories first
        await saveNewPolicyCategories();

        // Validation: Each policy must have at least one non-excluded subpolicy
        for (const policy of policiesData.value) {
          if (!policy.subPolicies || policy.subPolicies.length === 0) {
            PopupService.error('Each policy must have at least one subpolicy.', 'Validation Error');
            loading.value = false;
            return;
          }
          
          // Check if all subpolicies are excluded
          const activeSubPolicies = policy.subPolicies.filter(sp => !sp.exclude);
          if (activeSubPolicies.length === 0) {
            PopupService.error('Each policy must have at least one active (non-excluded) subpolicy. Please add a new subpolicy or un-exclude an existing one.', 'Validation Error');
            loading.value = false;
            return;
          }
        }

        if (showPolicyDropdown.value) {
          console.log('Processing policy copy mode...');
          // Create new tailored policies using the new endpoint
          for (const policy of policiesData.value) {
            // Skip excluded policies
            if (policy.exclude) {
              console.log('Skipping excluded policy:', {
                id: policy.id,
                title: policy.title
              });
              continue;
            }

            // Prepare subpolicies data for the new endpoint
            const subpolicies = policy.subPolicies
              .filter(sp => !sp.exclude) // Only include non-excluded subpolicies
              .map(sp => ({
                SubPolicyName: sp.title,
                Description: sp.description,
                Control: sp.control,
                Identifier: sp.identifier,
                Status: 'Under Review',
                PermanentTemporary: ''
              }));

            const policyData = {
              PolicyName: policy.title,
              TargetFrameworkId: parseInt(selectedFramework.value),
              PolicyDescription: policy.description,
              StartDate: policy.startDate,
              EndDate: policy.endDate,
              Department: policy.department,
              Applicability: policy.applicability,
              DocURL: policy.docURL || '',
              Scope: policy.scope,
              Objective: policy.objective,
              Identifier: policy.identifier,
              CreatedByName: policy.createdByName,
              Reviewer: policy.reviewer,
              CoverageRate: policy.coverageRate,
              PermanentTemporary: '',
              PolicyType: policy.PolicyType,
              PolicyCategory: policy.PolicyCategory,
              PolicySubCategory: policy.PolicySubCategory,
              Entities: policy.Entities || [],
              subpolicies: subpolicies
            }

            // Always use the create tailored policy endpoint for consistent approval workflow
            await axios.post(`${API_BASE_URL}/tailoring/create-policy/`, policyData);
          }
          
          // Show success message with correct count
          const activePolicies = policiesData.value.filter(p => !p.exclude).length;
          console.log('Submission complete. Active policies:', activePolicies);
          PopupService.success(
            `Successfully processed ${activePolicies} policy/policies to framework "${frameworks.value.find(f => f.id === selectedFramework.value)?.name || 'Unknown'}". The policies are now available for approval in the Policy Approver dashboard.`,
            'Policies Copied'
          );
        } else {
          console.log('Processing framework creation mode...');
          // Create new tailored framework using the new endpoint
          const tailoredFrameworkData = {
            title: frameworkData.value.title,
            description: frameworkData.value.description,
            category: frameworkData.value.category,
            effectiveDate: frameworkData.value.effectiveDate,
            startDate: frameworkData.value.startDate,
            endDate: frameworkData.value.endDate,
            docURL: frameworkData.value.docURL,
            identifier: frameworkData.value.identifier,
            createdByName: frameworkData.value.createdByName,
            reviewer: frameworkData.value.reviewer,
            policies: policiesData.value.map(p => ({
              title: p.title,
              description: p.description,
              objective: p.objective,
              scope: p.scope,
              department: p.department,
              applicability: p.applicability,
              startDate: p.startDate,
              endDate: p.endDate,
              docURL: p.docURL || '',
              identifier: p.identifier,
              createdByName: p.createdByName,
              reviewer: p.reviewer,
              coverageRate: p.coverageRate,
              exclude: !!p.exclude,
              status: p.exclude ? 'Excluded' : 'Under Review',
              PolicyType: p.PolicyType,
              PolicyCategory: p.PolicyCategory,
              PolicySubCategory: p.PolicySubCategory,
              Entities: p.Entities || [],
              subPolicies: p.subPolicies.map(sp => ({
                title: sp.title,
                description: sp.description,
                control: sp.control,
                identifier: sp.identifier,
                exclude: !!sp.exclude,
                status: sp.exclude ? 'Excluded' : 'Under Review'
              }))
            }))
          };

          console.log('Submitting tailored framework data:', tailoredFrameworkData);
          const result = await axios.post(`${API_BASE_URL}/tailoring/create-framework/`, tailoredFrameworkData);
          console.log('Tailored framework creation response:', result.data);
          
          PopupService.success(
            `Successfully created framework "${result.data.FrameworkName}" with ID: ${result.data.FrameworkId}. The framework is now available for approval in the Framework Approver dashboard.`,
            'Framework Created'
          );
        }

        // Reset form after successful submission
        resetForm();
      } catch (err) {
        console.error('Error in form submission:', err);
        handleError(err);
      } finally {
        loading.value = false;
      }
    }

    // Add helper function to reset form
    const resetForm = () => {
      showStepper.value = false
      selectedFramework.value = ''
      selectedPolicy.value = ''
      policiesData.value = [{
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
              docURL: '',
      identifier: '',
      coverageRate: null,
      Entities: [],
      showEntitiesDropdown: false,
      subPolicies: []
    }]
      frameworkData.value = {
        title: '',
        description: '',
        category: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: ''
      }
    }

    // Add helper function to handle errors
    const handleError = (err) => {
      console.error('Error submitting form:', err)
      const errorMessage = err.response?.data?.error || err.response?.data?.details?.error || 'Failed to submit form'
      PopupService.error(errorMessage, 'Submission Error')
      console.log('Full error details:', {
        error: err.response?.data,
        status: err.response?.status,
        headers: err.response?.headers
      })
    }

    // Computed property for step tabs - show only policy tab in policy mode
    const stepTabs = computed(() => {
      if (showPolicyDropdown.value) {
        // One tab per policy in copy mode
        return policiesData.value.map((p, i) => ({ key: `policy${i+1}`, label: `Policy ${i+1}` }))
      }
      return [
        { key: 'framework', label: 'Framework' },
        ...policiesData.value.map((p, i) => ({ key: `policy${i+1}`, label: `Policy ${i+1}` }))
      ]
    })

    // Add function to fetch users
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/policy-users/`)
        users.value = response.data
      } catch (err) {
        console.error('Error fetching users:', err)
        PopupService.error('Failed to fetch users', 'Loading Error')
      }
    }

    // Fetch policy categories
    const fetchPolicyCategories = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/policy-categories/`)
        policyCategories.value = response.data
        policyTypes.value = [...new Set(policyCategories.value.map(cat => cat.PolicyType).filter(Boolean))]
      } catch (err) {
        console.error('Error fetching policy categories:', err)
        PopupService.error('Failed to fetch policy categories', 'Loading Error')
      } finally {
        loading.value = false
      }
    }

    const getCategoriesForType = (policyType) => {
      if (!policyType) return []
      return [...new Set(policyCategories.value.filter(cat => cat.PolicyType === policyType).map(cat => cat.PolicyCategory).filter(Boolean))]
    }
    const getSubCategoriesForCategory = (policyType, policyCategory) => {
      if (!policyType || !policyCategory) return []
      return [...new Set(policyCategories.value.filter(cat => cat.PolicyType === policyType && cat.PolicyCategory === policyCategory).map(cat => cat.PolicySubCategory).filter(Boolean))]
    }

    const handlePolicyTypeChange = (idx, value) => {
      policiesData.value[idx].PolicyType = value
      policiesData.value[idx].PolicyCategory = ''
      policiesData.value[idx].PolicySubCategory = ''
    }
    const handlePolicyCategoryChange = (idx, value) => {
      policiesData.value[idx].PolicyCategory = value
      policiesData.value[idx].PolicySubCategory = ''
    }
    const handlePolicySubCategoryChange = (idx, value) => {
      policiesData.value[idx].PolicySubCategory = value
    }

    // Handle policy title changes to auto-generate identifiers
    const handlePolicyTitleChange = (policyIndex) => {
      if (isInternalFramework()) {
        // Small delay to ensure the model is updated
        setTimeout(() => {
          autoGeneratePolicyIdentifiers(policyIndex)
        }, 10)
      }
    }

    // Handle subpolicy title changes to auto-generate identifiers
    const handleSubPolicyTitleChange = (policyIndex, subPolicyIndex) => {
      if (isInternalFramework()) {
        // Small delay to ensure the model is updated
        setTimeout(() => {
          autoGenerateSubPolicyIdentifier(policyIndex, subPolicyIndex)
        }, 10)
      }
    }

    // Add function to save new policy categories before form submission
    const saveNewPolicyCategories = async () => {
      try {
        console.log('Checking for new policy categories to save...');
        const newCombinations = [];
        
        // Process all policies to find new category combinations
        for (const policy of policiesData.value) {
          if (policy.exclude) {
            continue;
          }
          
          const type = policy.PolicyType?.trim();
          const category = policy.PolicyCategory?.trim();
          const subcategory = policy.PolicySubCategory?.trim();
          
          // Skip if any part of the combination is missing
          if (!type || !category || !subcategory) {
            continue;
          }
          
          // Check if this combination exists in our local data
          const exists = policyCategories.value.some(pc => 
            pc.PolicyType === type && 
            pc.PolicyCategory === category && 
            pc.PolicySubCategory === subcategory
          );
          
          if (!exists) {
            console.log(`Found new combination: ${type} > ${category} > ${subcategory}`);
            newCombinations.push({
              PolicyType: type,
              PolicyCategory: category,
              PolicySubCategory: subcategory
            });
          }
        }
        
        // Save new combinations to the database
        if (newCombinations.length > 0) {
          console.log(`Saving ${newCombinations.length} new policy category combinations...`);
          
          for (const combination of newCombinations) {
            await axios.post(`${API_BASE_URL}/policy-categories/save/`, combination);
          }
          
          // Refresh policy categories after saving
          await fetchPolicyCategories();
          console.log('Policy categories refreshed');
        } else {
          console.log('No new policy category combinations to save');
        }
      } catch (err) {
        console.error('Error saving policy categories:', err);
      }
    };

    // Fetch entities
    const fetchEntities = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/entities/`)
        entities.value = response.data.entities || []
      } catch (err) {
        console.error('Error fetching entities:', err)
        PopupService.error('Failed to fetch entities', 'Loading Error')
      }
    }

    // Entity handling functions
    const isAllEntitiesSelected = (idx) => {
      return policiesData.value[idx].Entities === 'all'
    }

    const getSelectedEntityIds = (idx) => {
      const entities = policiesData.value[idx].Entities
      if (entities === 'all') {
        return ['all']
      }
      return Array.isArray(entities) ? entities.filter(id => id !== 'all') : []
    }

    const getSelectedEntitiesCount = (idx) => {
      const entities = policiesData.value[idx].Entities
      if (entities === 'all') {
        return 0 // Don't count when 'all' is selected
      }
      return Array.isArray(entities) ? entities.filter(id => id !== 'all').length : 0
    }

    const toggleEntitiesDropdown = (idx) => {
      // Close all other dropdowns first
      policiesData.value.forEach((policy, index) => {
        if (index !== idx) {
          policy.showEntitiesDropdown = false
        }
      })
      
      // Initialize showEntitiesDropdown if it doesn't exist
      if (policiesData.value[idx].showEntitiesDropdown === undefined) {
        policiesData.value[idx].showEntitiesDropdown = false
      }
      policiesData.value[idx].showEntitiesDropdown = !policiesData.value[idx].showEntitiesDropdown
    }

    const handleEntitySelection = (idx, entityId, isChecked) => {
      console.log('handleEntitySelection called:', { idx, entityId, isChecked })
      let selectedEntities = getSelectedEntityIds(idx)
      console.log('Current selected entities:', selectedEntities)
      
      if (entityId === 'all') {
        if (isChecked) {
          // If 'All' is selected, clear other selections and set to 'all'
          policiesData.value[idx].Entities = 'all'
          console.log('Set entities to "all"')
        } else {
          // If 'All' is unchecked, clear selection
          policiesData.value[idx].Entities = []
          console.log('Cleared entities')
        }
      } else {
        // If a specific entity is selected
        if (isChecked) {
          // Remove 'all' if it was selected and add the specific entity
          if (selectedEntities.includes('all')) {
            selectedEntities = []
          }
          if (!selectedEntities.includes(entityId)) {
            selectedEntities.push(entityId)
          }
        } else {
          // Remove the entity from selection
          selectedEntities = selectedEntities.filter(id => id !== entityId && id !== 'all')
        }
        policiesData.value[idx].Entities = selectedEntities
        console.log('Updated entities to:', selectedEntities)
      }
      
      console.log('Final policy entities:', policiesData.value[idx].Entities)
    }

    const selectEntity = (idx, entityId) => {
      const currentEntities = policiesData.value[idx].Entities
      
      let isSelected = false
      if (entityId === 'all') {
        isSelected = currentEntities === 'all'
      } else {
        isSelected = Array.isArray(currentEntities) && currentEntities.includes(entityId)
      }
      
      handleEntitySelection(idx, entityId, !isSelected)
    }

    const closeAllEntityDropdowns = () => {
      policiesData.value.forEach(policy => {
        policy.showEntitiesDropdown = false
      })
    }

    // Modify onMounted to fetch users
    onMounted(() => {
      fetchFrameworks()
      fetchUsers()
      fetchPolicyCategories()
      fetchExistingFrameworkIdentifiers()
      fetchEntities()
    })

    // Add this method to safely trigger the file input
    const triggerPolicyFileInput = (idx) => {
      const refItem = proxy.$refs['policyFileInput' + idx];
      if (refItem) {
        (Array.isArray(refItem) ? refItem[0] : refItem).click();
      }
    };

    return {
      selectedFramework,
      selectedPolicy,
      frameworks,
      showStepper,
      showPolicyDropdown,
      stepIndex,
      stepTabs,
      frameworkData,
      policiesData,
      policyOptions,
      loading,
      error,
      onFrameworkDropdown,
      onPolicyDropdown,
      switchToPolicy,
      switchToFramework,
      addPolicy,
      removePolicy,
      addSubPolicy,
      removeSubPolicy,
      closeTab,
      submitFrameworkForm,
      toggleSubPolicyExclusion,
      users,
      addPolicyToCopy,
      removePolicyFromCopy,
      togglePolicyExclusion,
      frameworkFileName,
      onFrameworkFileChange,
      onPolicyFileChange,
      triggerPolicyFileInput,
      policyCategories,
      policyTypes,
      fetchPolicyCategories,
      getCategoriesForType,
      getSubCategoriesForCategory,
      handlePolicyTypeChange,
      handlePolicyCategoryChange,
      handlePolicySubCategoryChange,
      handlePolicyTitleChange,
      handleSubPolicyTitleChange,
      generateFrameworkIdentifier,
      generatePolicyIdentifier,
      generateSubPolicyIdentifier,
      autoGenerateFrameworkIdentifier,
      autoGeneratePolicyIdentifiers,
      autoGenerateSubPolicyIdentifier,
      isInternalFramework,
      entities,
      fetchEntities,
      isAllEntitiesSelected,
      getSelectedEntityIds,
      getSelectedEntitiesCount,
      toggleEntitiesDropdown,
      handleEntitySelection,
      selectEntity,
      closeAllEntityDropdowns
    }
  }
}
</script>

<style scoped>
/* Add loading and error styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* Add new styles */
.framework-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 4px;
}

.framework-select:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.helper-text {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  margin-bottom: 0;
}

/* Keep existing styles */
@import './Tailoring.css';

/* Import popup styles */
@import '@/modules/popup/styles.css';

/* Import popup styles */
@import '@/modules/popus/styles.css';

/* Add new styles */
.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subpolicy-actions {
  display: flex;
  gap: 10px;
}

.exclude-btn {
  padding: 4px 8px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.exclude-btn.excluded {
  background-color: #ffebee;
  color: #d32f2f;
  border-color: #d32f2f;
}

.excluded {
  opacity: 0.6;
  background-color: #f5f5f5;
}

.remove-btn {
  padding: 4px 8px;
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #d32f2f;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn:hover {
  background-color: #d32f2f;
  color: white;
}

/* Add these styles */
select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 4px;
}

select:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* Policy form container specific styles */
.policy-form-container {
  background: #f8fafc;
  padding: 24px;
  border-radius: 12px;
  margin-top: 24px;
  border: 2px solid #e2e8f0;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* Form row inside policy container */
.policy-form-container .form-row {
  display: flex;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding: 0 10px;
  flex-wrap: wrap;
}

/* Form group inside policy container */
.policy-form-container .form-group {
  flex: 1 1 0;
  min-width: 220px;
  margin-bottom: 15px;
  box-sizing: border-box;
}

/* Input fields inside policy container */
.policy-form-container .form-group input,
.policy-form-container .form-group textarea,
.policy-form-container .form-group select {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 8px 12px;
  font-size: 14px;
}

/* Remove policy button */
.policy-form-container .remove-btn {
  padding: 4px 12px;
  font-size: 12px;
  height: 28px;
  background: transparent;
  border: 1px solid #e74c3c;
  color: #e74c3c;
}

/* Add responsive styles */
@media screen and (max-width: 768px) {
  .policy-form-container .form-group {
    flex: 1 1 100%;
    max-width: 100%;
  }
  
  .policy-form-container .form-row {
    gap: 10px;
  }
}

/* Add new styles for policy actions */
.policy-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.exclude-btn {
  padding: 4px 12px;
  font-size: 12px;
  height: 28px;
  background: transparent;
  border: 1px solid #2575fc;
  color: #2575fc;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.exclude-btn.excluded {
  background: #ffebee;
  color: #d32f2f;
  border-color: #d32f2f;
}

.exclude-btn:hover {
  background: #2575fc;
  color: white;
}

.exclude-btn.excluded:hover {
  background: #d32f2f;
  color: white;
}

.input-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}
.input-with-icon input[type='url'] {
  flex: 1;
}
.input-with-icon button {
  margin-left: 8px;
}

/* Stepper container and horizontal scroll */
.stepper-container {
  position: relative;
  width: 100%;
  overflow: visible;
}

.stepper {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  padding: 24px 32px;
  border-radius: 16px 16px 0 0;
  gap: 12px;
}

.stepper-tabs-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  flex: 1 1 auto;
  min-width: 0;
  white-space: nowrap;
  scrollbar-width: thin;
  scrollbar-color: #2575fc #e2e8f0;
}

.stepper-tabs-scroll::-webkit-scrollbar {
  height: 8px;
}
.stepper-tabs-scroll::-webkit-scrollbar-thumb {
  background: #2575fc;
  border-radius: 4px;
}
.stepper-tabs-scroll::-webkit-scrollbar-track {
  background: #e2e8f0;
  border-radius: 4px;
}

.add-policy-btn {
  flex: 0 0 auto;
  margin-left: 16px;
  position: static;
  z-index: 1;
}
</style> 