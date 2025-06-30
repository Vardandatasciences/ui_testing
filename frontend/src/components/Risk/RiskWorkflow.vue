<template>
  <div class="risk-workflow-container">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <!-- Show tasks view when not viewing any workflows -->
    <div v-if="!showMitigationWorkflow && !showReviewerWorkflow">
      <!-- Toggle buttons for Risk Resolution and Risk Workflow -->
      <div class="risk-workflow-toggle-buttons">
        <button 
          class="risk-workflow-toggle-button" 
          @click="navigateTo('resolution')"
        >
          Risk Resolution
        </button>
        <button 
          class="risk-workflow-toggle-button active" 
          @click="navigateTo('workflow')"
        >
          Risk Workflow
        </button>
      </div>
      
      <div class="risk-workflow-user-filter">
        <label for="user-select">Select User:</label>
        <div v-if="loading && users.length === 0" class="risk-workflow-loading-indicator">Loading users...</div>
        <select id="user-select" v-model="selectedUserId" @change="fetchData" class="risk-workflow-user-dropdown" :disabled="loading && users.length === 0">
          <option value="">All Users</option>
          <option v-for="user in users" :key="user.user_id" :value="user.user_id">
            {{ user.user_name }} {{ user.department ? `(${user.department})` : '' }}
          </option>
        </select>
      </div>
      
      <!-- Tabs for User Tasks and Reviewer Tasks -->
      <div class="risk-workflow-tabs">
        <div 
          class="risk-workflow-tab" 
          :class="{ 'active': activeTab === 'user' }" 
          @click="activeTab = 'user'"
        >
          My Tasks
        </div>
        <div 
          class="risk-workflow-tab" 
          :class="{ 'active': activeTab === 'reviewer' }" 
          @click="activeTab = 'reviewer'"
        >
          Reviewer Tasks
        </div>
      </div>
      
      <div v-if="loading" class="risk-workflow-loading">
        Loading data...
      </div>
      
      <div v-else-if="error" class="risk-workflow-error-message">
        {{ error }}
      </div>
      
      <!-- User Tasks Section -->
      <div v-if="activeTab === 'user'">
        <div v-if="!selectedUserId" class="risk-workflow-no-data">
          <p>Please select a user to view their assigned risks.</p>
        </div>
        <div v-else-if="userRisks.length === 0" class="risk-workflow-no-data">
          <p>No risks assigned to this user.</p>
        </div>
        <div v-else>
          <div v-for="(risks, status) in groupedUserRisks" :key="status">
            <CollapsibleTable
              :sectionConfig="{ name: status, statusClass: status.toLowerCase().replace(/\s+/g, '-'), tasks: risks }"
              :tableHeaders="[
                { key: 'RiskInstanceId', label: 'RiskID' },
                { key: 'Origin', label: 'Origin' },
                { key: 'Category', label: 'Category' },
                { key: 'Criticality', label: 'Criticality' },
                { key: 'RiskDescription', label: 'Risk Description' },
                { key: 'RiskStatus', label: 'Status' },
                { key: 'actions', label: 'Actions' }
              ]"
              :isExpanded="expandedSections[`user_${status}`] !== false"
              @toggle="() => handleUserSectionToggle(status)"
              @taskClick="(task) => viewMitigations(task.RiskInstanceId)"
            />
          </div>
        </div>
      </div>
      
      <!-- Reviewer Tasks Section -->
      <div v-if="activeTab === 'reviewer'">
        <div v-if="!selectedUserId" class="risk-workflow-no-data">
          <p>Please select a user to view their reviewer tasks.</p>
        </div>
        <div v-else-if="reviewerTasks.length === 0" class="risk-workflow-no-data">
          <p>No review tasks assigned to this user.</p>
        </div>
        <div v-else>
          <div v-for="(tasks, status) in groupedReviewerTasks" :key="status">
            <CollapsibleTable
              :sectionConfig="{ name: status, statusClass: status.toLowerCase().replace(/\s+/g, '-'), tasks: tasks }"
              :tableHeaders="[
                { key: 'RiskInstanceId', label: 'RiskID' },
                { key: 'Origin', label: 'Origin' },
                { key: 'Category', label: 'Category' },
                { key: 'Criticality', label: 'Criticality' },
                { key: 'RiskDescription', label: 'Risk Description' },
                { key: 'RiskStatus', label: 'Status' },
                { key: 'actions', label: 'Actions' }
              ]"
              :isExpanded="expandedSections[`reviewer_${status}`] !== false"
              @toggle="() => handleReviewerSectionToggle(status)"
              @taskClick="(task) => reviewMitigations(task)"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Risk Mitigation Workflow view (Full screen instead of modal) -->
    <div v-if="showMitigationWorkflow" class="risk-workflow-fullscreen">
      <div class="risk-workflow-back-to-tasks">
        <button @click="closeMitigationModal" class="risk-workflow-back-btn" title="Back to tasks">
          <i class="fas fa-arrow-left"></i>
        </button>
      </div>
      
      <div v-if="loadingMitigations" class="risk-workflow-loading">
        <div class="risk-workflow-spinner"></div>
        <span>Loading mitigation steps...</span>
      </div>
      <div v-else-if="!mitigationSteps.length" class="risk-workflow-no-data">
        No mitigation steps found for this risk.
      </div>
      <div v-else class="risk-workflow-simplified-workflow">
        <!-- Vertical timeline with connected steps -->
        <div class="risk-workflow-timeline">
          <div 
            v-for="(step, index) in mitigationSteps" 
            :key="index" 
            class="risk-workflow-timeline-step"
            :class="{
              'completed': step.status === 'Completed',
              'active': isStepActive(index),
              'locked': isStepLocked(index),
              'approved': step.approved === true,
              'rejected': step.approved === false
            }"
            :style="{ '--step-index': index }"
          >
            <!-- Step circle with number -->
            <div class="risk-workflow-step-circle">
              <span v-if="step.status === 'Completed'"><i class="fas fa-check"></i></span>
              <span v-else>{{ step.title.replace('Step ', '') }}</span>
            </div>
            
            <!-- Step content -->
            <div class="step-box">
              <h3>{{ step.description }}</h3>
              
              <!-- Add submission dates when available -->
              <div v-if="step.user_submitted_date" class="submission-date user-date">
                <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(step.user_submitted_date) }}
              </div>
              <div v-if="step.reviewer_submitted_date" class="submission-date reviewer-date">
                <i class="fas fa-clock"></i> Reviewed: {{ formatDateTime(step.reviewer_submitted_date) }}
              </div>
              
              <!-- Status indicators -->
              <div v-if="step.approved === true" class="status-tag approved">
                <i class="fas fa-check-circle"></i> Approved
              </div>
              <div v-else-if="step.approved === false" class="status-tag rejected">
                <i class="fas fa-times-circle"></i> Rejected
                <div v-if="step.remarks" class="remarks">
                  <strong>Feedback:</strong> {{ step.remarks }}
                </div>
              </div>
              <div v-else-if="step.status === 'Completed'" class="status-tag completed">
                <i class="fas fa-check"></i> Completed
              </div>
              <div v-else-if="isStepActive(index)" class="status-tag active">
                <i class="fas fa-circle-notch fa-spin"></i> In Progress
              </div>
              <div v-else class="status-tag locked">
                <i class="fas fa-lock"></i> Locked
              </div>
              
                <!-- Add status control with complete button -->
  <div v-if="!step.approved && !isStepLocked(index)" class="risk-workflow-status-control">
    <button 
      @click="completeStep(index)" 
      class="risk-workflow-complete-btn"
      :class="{ 'active': step.status === 'Completed' }"
      v-if="step.status !== 'Completed'"
    >
      <i class="fas fa-check"></i> Mark as Complete
    </button>
    <button 
      @click="resetStep(index)" 
      class="risk-workflow-reset-btn"
      v-else
    >
      <i class="fas fa-undo"></i> Reset
    </button>
  </div>
  
  <!-- Add comments section for each mitigation step -->
  <div v-if="!isStepLocked(index)" class="step-inputs">
    <div class="input-group">
      <label for="step-comments"><i class="fas fa-comment"></i> Comments:</label>
      <textarea 
        id="step-comments" 
        v-model="step.comments" 
        placeholder="Add your comments about this mitigation step..."
        rows="4"
      ></textarea>
    </div>
    
    <!-- Display existing comments if available -->
    <div v-if="step.comments" class="comments-display">
      <h4><i class="fas fa-comment-alt"></i> Your Comments</h4>
      <p>{{ step.comments }}</p>
    </div>
  </div>
            </div>
          </div>
        </div>
        
        <!-- Update the mitigation-questionnaire div in the mitigation modal -->
        <div class="mitigation-questionnaire">
          <h3>Risk Mitigation Questionnaire</h3>
          
          <!-- Add questionnaire status indicator -->
          <div v-if="questionnaireReviewed" class="questionnaire-status" :class="{ 'approved': questionnaireApproved, 'rejected': !questionnaireApproved }">
            <i class="fas" :class="questionnaireApproved ? 'fa-check-circle' : 'fa-times-circle'"></i>
            {{ questionnaireApproved ? 'Approved' : 'Revision Required' }}
            
            <!-- Add submission dates when available -->
            <div v-if="formDetails.user_submitted_date" class="submission-date user-date">
              <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(formDetails.user_submitted_date) }}
            </div>
            <div v-if="formDetails.reviewer_submitted_date" class="submission-date reviewer-date">
              <i class="fas fa-clock"></i> Reviewed: {{ formatDateTime(formDetails.reviewer_submitted_date) }}
            </div>
          </div>
          
          <p class="questionnaire-note">Please complete all fields to proceed with submission</p>
          
          <div class="question-group">
            <label for="cost-input"><span class="question-number">1</span> What is the cost for this mitigation?</label>
            <input id="cost-input" type="number" v-model="formDetails.cost" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter the cost..." />
          </div>
          <div class="question-group">
            <label for="impact-input"><span class="question-number">2</span> What is the impact for this mitigation?</label>
            <input id="impact-input" type="number" v-model="formDetails.impact" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter the impact..." />
          </div>
          <div class="question-group">
            <label for="financial-impact-input"><span class="question-number">3</span> What is the financial impact for this mitigation?</label>
            <input id="financial-impact-input" type="number" v-model="formDetails.financialImpact" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter the financial impact..." />
          </div>
          <div class="question-group">
            <label for="reputational-impact-input"><span class="question-number">4</span> What is the reputational impact for this mitigation?</label>
            <textarea id="reputational-impact-input" v-model="formDetails.reputationalImpact" :disabled="!allStepsCompleted || questionnaireApproved" placeholder="Describe the reputational impact..."></textarea>
          </div>
          <div class="question-group">
            <label for="operational-impact-input"><span class="question-number">5</span> What is the Operational Impact for this mitigation?</label>
            <input id="operational-impact-input" type="number" v-model="formDetails.operationalImpact" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter the operational impact..." />
          </div>
          <div class="question-group">
            <label for="financial-loss-input"><span class="question-number">6</span> What is the Financial Loss for this mitigation?</label>
            <input id="financial-loss-input" type="number" v-model="formDetails.financialLoss" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter the financial loss..." />
          </div>
          <div class="question-group">
            <label for="system-downtime-input"><span class="question-number">7</span> What is the expected system downtime (hrs) if this risk occurs?</label>
            <input id="system-downtime-input" type="number" v-model="formDetails.systemDowntime" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter expected downtime in hours..." />
          </div>
          <div class="question-group">
            <label for="recovery-time-input"><span class="question-number">8</span> How long did it take to recover last time (hrs)?</label>
            <input id="recovery-time-input" type="number" v-model="formDetails.recoveryTime" :disabled="!allStepsCompleted || questionnaireApproved" min="0" placeholder="Enter recovery time in hours..." />
          </div>
          <div class="question-group">
            <label for="recurrence-possible-input"><span class="question-number">9</span> Is it possible that this risk will recur again?</label>
            <select id="recurrence-possible-input" v-model="formDetails.recurrencePossible" :disabled="!allStepsCompleted || questionnaireApproved">
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="Unknown">Unknown</option>
            </select>
          </div>
          <div class="question-group">
            <label for="improvement-initiative-input"><span class="question-number">10</span> Is this an Improvement Initiative which will prevent the future recurrence of said risk?</label>
            <select id="improvement-initiative-input" v-model="formDetails.improvementInitiative" :disabled="!allStepsCompleted || questionnaireApproved">
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="Unknown">Unknown</option>
            </select>
          </div>
          
          <!-- Add to the mitigation-questionnaire div, after the questionnaire fields -->
          <div v-if="questionnaireRejected" class="questionnaire-feedback">
            <h4><i class="fas fa-exclamation-circle"></i> Reviewer Feedback</h4>
            <p>{{ questionnaireRemarks }}</p>
          </div>
        </div>
        
        <!-- Update the submission-area div to check for questionnaire completion -->
        <div class="submission-area" :class="{ 'ready': canSubmit }">
          <h3>Submit Mitigation</h3>
          
          <div v-if="selectedReviewer" class="reviewer-info">
            <p><strong>Assigned Reviewer:</strong> {{ getUserName(selectedReviewer) }}</p>
          </div>
          
          <button 
            @click="submitForReview" 
            class="submit-btn" 
          >
            <i class="fas fa-paper-plane"></i> Submit for Review
          </button>
          
          <!-- Hidden warning messages -->
          <div v-if="false" class="submit-message">
            <i class="fas fa-info-circle"></i>
            Complete all mitigation steps before submitting
          </div>
          
          <div v-if="false" class="submit-message">
            <i class="fas fa-info-circle"></i>
            Complete the questionnaire before submitting
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reviewer Workflow view (Full screen instead of modal) -->
    <div v-if="showReviewerWorkflow" class="reviewer-workflow-fullscreen">
      <div class="back-to-tasks">
        <button @click="closeReviewerModal" class="back-btn" title="Back to tasks">
          <i class="fas fa-arrow-left"></i>
        </button>
      </div>
      
      <h1>Review Risk Mitigations</h1>
      
      <div v-if="loadingMitigations" class="loading">
        <div class="spinner"></div>
        <span>Loading mitigation data...</span>
      </div>
      <div v-else>
        <div class="risk-summary">
          <h3>{{ currentReviewTask?.RiskDescription || 'Risk #' + currentReviewTask?.RiskInstanceId }}</h3>
          <p><strong>ID:</strong> {{ currentReviewTask?.RiskInstanceId }}</p>
          <p><strong>Submitted By:</strong> {{ getUserName(currentReviewTask?.UserId) }}</p>
        </div>
        
        <div v-if="reviewCompleted" class="review-status-banner" :class="{ 'approved': reviewApproved, 'rejected': !reviewApproved }">
          <div v-if="reviewApproved" class="status-message">
            <i class="fas fa-check-circle"></i> This risk has been approved
          </div>
          <div v-else class="status-message">
            <i class="fas fa-times-circle"></i> Feedback sent to user for revision
          </div>
        </div>
        
        <!-- Mitigation review list with split view design -->
        <div class="mitigation-review-list">
          <!-- Add version dropdown above mitigation items -->
          <div class="global-version-dropdown" :class="{ 'loading': loadingVersions }">
            <label for="global-version-select">Select Version to Compare:</label>
            <select 
              id="global-version-select" 
              v-model="globalSelectedVersion" 
              @change="onGlobalVersionChange"
              class="global-version-select"
              :disabled="loadingVersions || allVersionNames.length === 0"
            >
              <option value="">Select a version</option>
              <option 
                v-for="version in allVersionNames" 
                :key="version" 
                :value="version"
              >
                {{ version }}
              </option>
            </select>
            <div v-if="allVersionNames.length === 0 && !loadingVersions" class="no-versions-message">
              <i class="fas fa-info-circle"></i> No previous versions available
            </div>
          </div>

          <div 
            v-for="(mitigation, id) in mitigationReviewData" 
            :key="id" 
            class="mitigation-review-item"
            :data-id="id"
          >
            <!-- Mitigation header with status badge -->
            <div class="mitigation-heading">
              <h4>Mitigation #{{ id }}</h4>
              
              <!-- Status badge -->
              <div v-if="mitigation.approved !== undefined" 
                  class="mitigation-status-badge" 
                  :class="{ 
                    'approved': mitigation.approved === true, 
                    'rejected': mitigation.approved === false,
                    'pending': mitigation.approved === undefined
                  }">
                <i class="fas" :class="{
                  'fa-check-circle': mitigation.approved === true,
                  'fa-times-circle': mitigation.approved === false,
                  'fa-clock': mitigation.approved === undefined
                }"></i>
                {{ mitigation.approved === true ? 'Approved' : 
                   mitigation.approved === false ? 'Rejected' : 'Pending Review' }}
              </div>
            </div>
            
            <!-- Split view container -->
            <div class="mitigation-split-content">
              <!-- Previous version (left side) -->
              <div class="mitigation-previous">
                <div class="version-label">
                  Previous Versions
                  <!-- Debug info -->
                  <div style="font-size: 10px; color: #999; margin-top: 2px;">
                    Total Versions: {{ allVersions.length }}, Selected: {{ selectedVersions[id] || 'None' }}
                  </div>
                </div>
                
                <!-- Show selected version data from dropdown -->
                <div v-if="selectedVersions[id] && getSelectedVersionData(id, selectedVersions[id])" class="mitigation-content">
                  <h5>Description</h5>
                  <p>{{ getSelectedVersionData(id, selectedVersions[id]).description || 'No description available' }}</p>
                  
                  <!-- Version metadata section -->
                  <div class="metadata-section">
                    <h5>Metadata</h5>
                    <div class="metadata-item">
                      <div class="metadata-label">Version:</div>
                      <div class="metadata-value">{{ selectedVersions[id] }}</div>
                    </div>
                    <div class="metadata-item">
                      <div class="metadata-label">Status:</div>
                      <div class="metadata-value">{{ getSelectedVersionData(id, selectedVersions[id]).status || 'Not specified' }}</div>
                    </div>
                    <div v-if="getSelectedVersionData(id, selectedVersions[id]).user_submitted_date" class="metadata-item">
                      <div class="metadata-label">Submitted:</div>
                      <div class="metadata-value">{{ formatDateTime(getSelectedVersionData(id, selectedVersions[id]).user_submitted_date) }}</div>
                    </div>
                    <div v-if="getSelectedVersionData(id, selectedVersions[id]).approved !== undefined" class="metadata-item">
                      <div class="metadata-label">Review Status:</div>
                      <div class="metadata-value">
                        <span :class="{ 'text-success': getSelectedVersionData(id, selectedVersions[id]).approved, 'text-danger': getSelectedVersionData(id, selectedVersions[id]).approved === false }">
                          {{ getSelectedVersionData(id, selectedVersions[id]).approved === true ? 'Approved' : 
                             getSelectedVersionData(id, selectedVersions[id]).approved === false ? 'Rejected' : 'Pending' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Version comments -->
                  <div v-if="getSelectedVersionData(id, selectedVersions[id]).comments" class="comments-section">
                    <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                    <p class="comments-text">{{ getSelectedVersionData(id, selectedVersions[id]).comments }}</p>
                  </div>
                  
                  <!-- Version evidence -->
                  <div v-if="getSelectedVersionData(id, selectedVersions[id]).fileData" class="evidence-section">
                    <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                    <a :href="getSelectedVersionData(id, selectedVersions[id]).fileData" download :filename="getSelectedVersionData(id, selectedVersions[id]).fileName" class="evidence-link">
                      <i class="fas fa-download"></i> {{ getSelectedVersionData(id, selectedVersions[id]).fileName }}
                    </a>
                  </div>
                  
                  <!-- Version decision -->
                  <div v-if="getSelectedVersionData(id, selectedVersions[id]).approved !== undefined" class="decision-tag" 
                       :class="{ 
                         'approved': getSelectedVersionData(id, selectedVersions[id]).approved === true, 
                         'rejected': getSelectedVersionData(id, selectedVersions[id]).approved === false 
                       }">
                    <i class="fas" :class="{
                      'fa-check-circle': getSelectedVersionData(id, selectedVersions[id]).approved === true,
                      'fa-times-circle': getSelectedVersionData(id, selectedVersions[id]).approved === false
                    }"></i>
                    {{ getSelectedVersionData(id, selectedVersions[id]).approved ? 'Approved' : 'Rejected' }}
                  </div>
                  
                  <!-- Show reviewer remarks if rejected -->
                  <div v-if="getSelectedVersionData(id, selectedVersions[id]).approved === false && getSelectedVersionData(id, selectedVersions[id]).remarks" class="remarks-section">
                    <h5><i class="fas fa-exclamation-triangle"></i> Reviewer Feedback</h5>
                    <p class="remarks-text">{{ getSelectedVersionData(id, selectedVersions[id]).remarks }}</p>
                  </div>
                  
                  <!-- Add reviewer feedback section - always show if available -->
                  <div v-if="getSelectedVersionData(id, selectedVersions[id]).reviewer_feedback" class="reviewer-feedback-section">
                    <h5><i class="fas fa-comment-dots"></i> Reviewer Feedback</h5>
                    <p class="reviewer-feedback-text">{{ getSelectedVersionData(id, selectedVersions[id]).reviewer_feedback }}</p>
                  </div>
                </div>
                
                <!-- Empty state for no version selected -->
                <div v-else class="mitigation-empty">
                  <i class="fas fa-history"></i>
                  <p>Select a version from the dropdown above to compare</p>
                </div>
              </div>
              
              <!-- Current version (right side) - This should show the LATEST version -->
              <div class="mitigation-current">
                <div class="version-label">
                  Latest Version
                  <div style="font-size: 10px; color: #666; margin-top: 2px;">
                    {{ getCurrentVersionLabel() }}
                  </div>
                </div>
                
                <div class="mitigation-content">
                  <h5>Description</h5>
                  <p>{{ mitigation.description || 'No description available' }}</p>
                  
                  <!-- Current metadata -->
                  <div class="metadata-section">
                    <h5>Metadata</h5>
                    <div class="metadata-item">
                      <div class="metadata-label">Version:</div>
                      <div class="metadata-value">{{ currentReviewTask?.version || 'Current' }}</div>
                    </div>
                    <div class="metadata-item">
                      <div class="metadata-label">Status:</div>
                      <div class="metadata-value">{{ mitigation.status || 'Not specified' }}</div>
                    </div>
                    <div v-if="mitigation.user_submitted_date" class="metadata-item">
                      <div class="metadata-label">Submitted:</div>
                      <div class="metadata-value">{{ formatDateTime(mitigation.user_submitted_date) }}</div>
                    </div>
                    <div v-if="mitigation.reviewer_submitted_date" class="metadata-item">
                      <div class="metadata-label">Reviewed:</div>
                      <div class="metadata-value">{{ formatDateTime(mitigation.reviewer_submitted_date) }}</div>
                    </div>
                    <div v-if="mitigation.approved !== undefined" class="metadata-item">
                      <div class="metadata-label">Review Status:</div>
                      <div class="metadata-value">
                        <span :class="{ 'text-success': mitigation.approved, 'text-danger': mitigation.approved === false }">
                          {{ mitigation.approved === true ? 'Approved' : 
                             mitigation.approved === false ? 'Rejected' : 'Pending' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Current comments -->
                  <div v-if="mitigation.comments" class="comments-section">
                    <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                    <p class="comments-text">{{ mitigation.comments }}</p>
                  </div>
                  
                  <!-- Current evidence -->
                  <div v-if="mitigation.fileData" class="evidence-section">
                    <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                    <a :href="mitigation.fileData" download :filename="mitigation.fileName" class="evidence-link">
                      <i class="fas fa-download"></i> {{ mitigation.fileName }}
                    </a>
                  </div>
                  
                  <!-- Current decision -->
                  <div v-if="mitigation.approved !== undefined" class="decision-tag" 
                       :class="{ 
                         'approved': mitigation.approved === true, 
                         'rejected': mitigation.approved === false 
                       }">
                    <i class="fas" :class="{
                      'fa-check-circle': mitigation.approved === true,
                      'fa-times-circle': mitigation.approved === false
                    }"></i>
                    {{ mitigation.approved ? 'Approved' : 'Rejected' }}
                  </div>
                  
                  <!-- Show current reviewer remarks if rejected -->
                  <div v-if="mitigation.approved === false && mitigation.remarks" class="remarks-section">
                    <h5><i class="fas fa-exclamation-triangle"></i> Reviewer Feedback</h5>
                    <p class="remarks-text">{{ mitigation.remarks }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Approval controls section -->
            <div class="approval-controls">
              <!-- Only show approval buttons if not yet approved or rejected -->
              <div v-if="mitigation.approved !== true && mitigation.approved !== false && !reviewCompleted" class="approval-buttons">
                <button 
                  @click="approveMitigation(id, true)" 
                  class="approve-btn"
                >
                  <i class="fas fa-check"></i> Approve
                </button>
                <button 
                  @click="approveMitigation(id, false)" 
                  class="reject-btn"
                >
                  <i class="fas fa-times"></i> Reject
                </button>
              </div>
              
              <!-- Show remarks field only when rejected -->
              <div v-if="mitigation.approved === false && !reviewCompleted" class="remarks-field">
                <label for="remarks">Feedback (required for rejection):</label>
                <textarea 
                  id="remarks" 
                  v-model="mitigation.remarks" 
                  class="remarks-input" 
                  placeholder="Provide feedback explaining why this mitigation was rejected..."
                ></textarea>
                
                <!-- Add a button to save remarks -->
                <button @click="updateRemarks(id)" class="save-remarks-btn">
                  <i class="fas fa-save"></i> Save Feedback
                </button>
                
                <!-- Allow changing decision -->
                <button @click="approveMitigation(id, true)" class="change-decision-btn">
                  <i class="fas fa-exchange-alt"></i> Change to Approve
                </button>
              </div>
              
              <!-- Show status and action buttons for approved items -->
              <div v-if="mitigation.approved === true && !reviewCompleted" class="approved-actions">
                <button @click="approveMitigation(id, false)" class="change-decision-btn">
                  <i class="fas fa-exchange-alt"></i> Change to Reject
                </button>
              </div>
              
              <!-- Show remarks if already rejected and submitted -->
              <div v-if="mitigation.approved === false && reviewCompleted && mitigation.remarks" class="reviewer-remarks-display">
                <h5><i class="fas fa-comment-exclamation"></i> Rejection Feedback</h5>
                <p>{{ mitigation.remarks }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Form details review section -->
        <div class="form-details-review">
          <h4>Risk Mitigation Questionnaire</h4>
          
          <!-- Add status badge at the top -->
          <div v-if="formDetails.approved !== undefined" class="approval-status" :class="{ 
            'approved': formDetails.approved, 
            'rejected': formDetails.approved === false 
          }">
            <i class="fas" :class="formDetails.approved ? 'fa-check-circle' : 'fa-times-circle'"></i>
            {{ formDetails.approved ? 'Questionnaire Approved' : 'Revisions Requested' }}
          </div>
          
          <!-- Add submission dates when available -->
          <div class="submission-dates">
            <div v-if="formDetails.user_submitted_date" class="submission-date user-date">
              <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(formDetails.user_submitted_date) }}
            </div>
            <div v-if="formDetails.reviewer_submitted_date" class="submission-date reviewer-date">
              <i class="fas fa-check-circle"></i> Reviewed: {{ formatDateTime(formDetails.reviewer_submitted_date) }}
            </div>
          </div>
          

          
          <!-- Modified form-split-content sections to include edit functionality -->
          <div class="form-split-content">
            <div class="form-field-label"><h5>1. What is the cost for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('cost') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('cost') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.cost || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <!-- Repeat similar pattern for other questions -->
          <div class="form-split-content">
            <div class="form-field-label"><h5>2. What is the impact for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('impact') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('impact') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.impact || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <div class="form-split-content">
            <div class="form-field-label"><h5>3. What is the financial impact for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('financialImpact') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('financialImpact') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.financialImpact || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <div class="form-split-content">
            <div class="form-field-label"><h5>4. What is the reputational impact for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('reputationalImpact') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('reputationalImpact') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.reputationalImpact || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <div class="form-split-content">
            <div class="form-field-label"><h5>5. What is the Operational Impact for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('operationalImpact') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('operationalImpact') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.operationalImpact || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <div class="form-split-content">
            <div class="form-field-label"><h5>6. What is the Financial Loss for this mitigation?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('financialLoss') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('financialLoss') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.financialLoss || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <div class="form-split-content">
            <div class="form-field-label"><h5>7. What is the expected system downtime (hrs) if this risk occurs?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('systemDowntime') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('systemDowntime') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.systemDowntime || 'Not specified' }}</p>
              </div>
            </div>
          </div>
          <div class="form-split-content">
            <div class="form-field-label"><h5>8. How long did it take to recover last time (hrs)?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('recoveryTime') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('recoveryTime') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.recoveryTime || 'Not specified' }}</p>
              </div>
            </div>
          </div>
          <div class="form-split-content">
            <div class="form-field-label"><h5>9. Is it possible that this risk will recur again?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('recurrencePossible') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('recurrencePossible') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.recurrencePossible || 'Not specified' }}</p>
              </div>
            </div>
          </div>
          <div class="form-split-content">
            <div class="form-field-label"><h5>10. Is this an Improvement Initiative which will prevent the future recurrence of said risk?</h5></div>
            <div class="form-field-split">
              <div class="form-field-previous" v-if="previousFormDetails">
                <div class="version-label">Previous Version</div>
                <p>{{ getPreviousFormDetail('improvementInitiative') }}</p>
              </div>
              <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged('improvementInitiative') }">
                <div class="version-label">Current Version</div>
                <p>{{ formDetails.improvementInitiative || 'Not specified' }}</p>
              </div>
            </div>
          </div>
          
          <!-- Add questionnaire approval controls -->
          <div class="questionnaire-approval" v-if="!reviewCompleted">
            <div v-if="formDetails.approved === undefined" class="approval-buttons">
              <button @click="approveQuestionnaire(true)" class="approve-btn">
                <i class="fas fa-check"></i> Approve Questionnaire
              </button>
              <button @click="approveQuestionnaire(false)" class="reject-btn">
                <i class="fas fa-times"></i> Request Revisions
              </button>
            </div>
            
            <div v-if="formDetails.approved === true" class="approval-status approved">
              <i class="fas fa-check-circle"></i> Questionnaire Approved
              <button @click="approveQuestionnaire(false)" class="change-decision-btn">
                <i class="fas fa-exchange-alt"></i> Change to Reject
              </button>
            </div>
            
            <div v-if="formDetails.approved === false" class="approval-status rejected">
              <i class="fas fa-times-circle"></i> Revisions Requested
              
              <div class="remarks-field">
                <label for="questionnaire-remarks">Feedback (required):</label>
                <textarea 
                  id="questionnaire-remarks" 
                  v-model="formDetails.remarks" 
                  class="remarks-input" 
                  placeholder="Provide feedback on the questionnaire..."
                ></textarea>
                
                <div class="approval-actions">
                  <button @click="saveQuestionnaireRemarks" class="save-remarks-btn">
                    <i class="fas fa-save"></i> Save Feedback
                  </button>
                  
                  <button @click="approveQuestionnaire(true)" class="change-decision-btn">
                    <i class="fas fa-exchange-alt"></i> Change to Approve
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="review-actions">
          <button 
            class="submit-review-btn" 
            :disabled="reviewCompleted" 
            @click="submitReview(true)"
          >
            <i class="fas fa-check-double"></i> Approve Risk
          </button>
          <button 
            class="reject-review-btn" 
            :disabled="reviewCompleted" 
            @click="submitReview(false)"
          >
            <i class="fas fa-comment-dots"></i> Send Feedback to User
          </button>
          
          <div v-if="reviewCompleted" class="review-complete-notice">
            This review has been completed
          </div>
          
          <div v-else-if="false" class="review-warning">
            <i class="fas fa-exclamation-circle"></i>
            You must approve or reject each mitigation before submitting
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CollapsibleTable from '../CollapsibleTable.vue';
import { PopupModal } from '@/modules/popup';
import './RiskWorkflow.css'; // Import the CSS file

export default {
  name: 'UserTasks',
  components: {
    CollapsibleTable,
    PopupModal
  },
  data() {
    return {
      userRisks: [],
      reviewerTasks: [],
      users: [],
      selectedUserId: '',
      loading: true,
      error: null,
      showMitigationWorkflow: false,
      showReviewerWorkflow: false,
      loadingMitigations: false,
      mitigationSteps: [],
      selectedRiskId: null,
      selectedReviewer: '',
      activeTab: 'user',
      showReviewerModal: false,
      mitigationReviewData: {},
      currentReviewTask: null,
      userNotifications: [],
      reviewCompleted: false,
      reviewApproved: false,
      formDetails: {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: '',
        operationalImpact: '',
        financialLoss: '',
        systemDowntime: '',
        recoveryTime: '',
        recurrencePossible: '',
        improvementInitiative: '',
        approved: undefined,
        remarks: '',
        user_submitted_date: null,
        reviewer_submitted_date: null
      },
      previousVersions: {},
      previousFormDetails: null,
      showQuestionnaire: false,
      questionnaireDetails: null,
      // New data properties for version management
      allVersions: [],
      selectedVersions: {},
      loadingVersions: false,
      versionData: {},
      showVersionDropdowns: true,
      globalSelectedVersion: '',
      allVersionNames: [],
      // Add state for tracking expanded sections
      expandedSections: {},
    }
  },
  computed: {
    userCount() {
      console.log('Current users in data:', this.users.length, this.users);
      return this.users.length;
    },
    allStepsCompleted() {
      const stepsToCheck = this.mitigationSteps.filter(step => Boolean(step.approved) !== true);
      return stepsToCheck.length > 0 && 
             stepsToCheck.every(step => step.status === 'Completed');
    },
    canSubmit() {
      // Always return true to enable the submission button
      return true;
    },
    canSubmitReview() {
      // Always return true to enable the review submission buttons
      return true;
    },
    questionnaireReviewed() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             (this.latestReview.risk_form_details.approved === true || 
              this.latestReview.risk_form_details.approved === false);
    },
    questionnaireApproved() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             this.latestReview.risk_form_details.approved === true;
    },
    questionnaireRejected() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             this.latestReview.risk_form_details.approved === false;
    },
    questionnaireRemarks() {
      if (this.latestReview && 
          this.latestReview.risk_form_details && 
          this.latestReview.risk_form_details.remarks) {
        return this.latestReview.risk_form_details.remarks;
      }
      return '';
    },
    filteredVersions() {
      // Filter out the current review task version
      return this.allVersions.filter(version => 
        version.version !== this.currentReviewTask?.version
      );
    },
    groupedUserRisks() {
      // Group userRisks by RiskStatus for CollapsibleTable
      const groups = {};
      this.userRisks.forEach(risk => {
        const status = risk.RiskStatus || 'Not Assigned';
        if (!groups[status]) groups[status] = [];
        groups[status].push(risk);
      });
      return groups;
    },
    groupedReviewerTasks() {
      const groups = {};
      this.reviewerTasks.forEach(task => {
        const status = task.RiskStatus || 'Not Assigned';
        if (!groups[status]) groups[status] = [];
        groups[status].push(task);
      });
      return groups;
    },
  },
  mounted() {
    // Fetch users immediately when component mounts
    this.fetchUsers();
    
    // Set a small delay to ensure the DOM is fully rendered
    setTimeout(() => {
      // Force a re-render of the dropdown
      if (this.users.length === 0) {
        this.fetchUsers();
      }
    }, 500);
  },
  methods: {
    fetchUsers() {
      console.log('Fetching users...');
      this.loading = true;
      
      // Try both endpoints to ensure we get users data
      axios.get('http://localhost:8000/api/custom-users/')
        .then(response => {
          console.log('User data received:', response.data);
          if (Array.isArray(response.data) && response.data.length > 0) {
            this.users = response.data;
            this.loading = false;
          } else {
            // If custom-users returns empty, try the users-for-dropdown endpoint
            return axios.get('http://localhost:8000/api/users-for-dropdown/');
          }
        })
        .then(response => {
          if (response && response.data) {
            console.log('User data from dropdown endpoint:', response.data);
            this.users = response.data;
          }
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching users:', error);
          this.error = `Failed to fetch users: ${error.message}`;
          this.loading = false;
        });
    },
    fetchData() {
      if (!this.selectedUserId) {
        this.userRisks = [];
        this.reviewerTasks = [];
        return;
      }
      
      this.loading = true;
      
      // Only fetch user risks and reviewer tasks, not notifications
      Promise.all([
        axios.get(`http://localhost:8000/api/user-risks/${this.selectedUserId}/`),
        axios.get(`http://localhost:8000/api/reviewer-tasks/${this.selectedUserId}/`)
      ])
      .then(([userResponse, reviewerResponse]) => {
        this.userRisks = userResponse.data;
        this.reviewerTasks = reviewerResponse.data;
        
        // Add last submitted date to user risks by fetching latest review
        this.userRisks.forEach((risk, index) => {
          axios.get(`http://localhost:8000/api/latest-review/${risk.RiskInstanceId}/`)
            .then(response => {
              if (response.data && response.data.user_submitted_date) {
                // Create a new array with the updated risk object
                const updatedRisks = [...this.userRisks];
                updatedRisks[index] = {
                  ...risk,
                  last_submitted: response.data.user_submitted_date
                };
                this.userRisks = updatedRisks;
              } else if (response.data && response.data.submission_date) {
                // Create a new array with the updated risk object
                const updatedRisks = [...this.userRisks];
                updatedRisks[index] = {
                  ...risk,
                  last_submitted: response.data.submission_date
                };
                this.userRisks = updatedRisks;
              }
            })
            .catch(error => {
              console.error(`Error fetching latest review for risk ${risk.RiskInstanceId}:`, error);
            });
        });
        
        console.log('User risks:', this.userRisks); // Log to verify data
        
        // Add notification icons based on risk status directly
        this.userRisks.forEach(risk => {
          if (risk.RiskStatus === 'Revision Required') {
            risk.hasNotification = true;
            risk.approved = false;
          } else if (risk.RiskStatus === 'Approved') {
            risk.hasNotification = true;
            risk.approved = true;
          }
        });
        
        this.loading = false;
        this.error = null;
        // Initialize expanded sections after data is loaded
        this.$nextTick(() => {
          this.initializeExpandedSections();
        });
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        this.error = `Failed to fetch data: ${error.message}`;
        this.loading = false;
      });
    },
    getUserName(userId) {
      const user = this.users.find(u => u.user_id == userId);
      return user ? user.user_name : 'Unknown';
    },
    startWork(riskId) {
      this.loading = true;
      console.log(`Starting work on risk ID: ${riskId}`);
      
      // Ensure we're sending the correct data format
      const requestData = {
        risk_id: riskId,
        status: 'Work In Progress'
      };
      
      console.log('Sending request data:', requestData);
      
      // Update mitigation status instead of risk status
      axios.post('http://localhost:8000/api/update-mitigation-status/', requestData)
        .then(response => {
          console.log('Status updated:', response.data);
          // Update the local risk status
          const index = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
          if (index !== -1) {
            this.userRisks[index].MitigationStatus = 'Work In Progress';
          }
          this.loading = false;
        })
        .catch(error => {
          console.error('Error updating status:', error);
          console.error('Error response:', error.response ? error.response.data : 'No response data');
          this.error = `Failed to update status: ${error.message}`;
          this.loading = false;
        });
    },
    completeMitigation(riskId) {
      this.loading = true;
      axios.post('http://localhost:8000/api/update-mitigation-status/', {
        risk_id: riskId,
        status: 'Completed'
      })
      .then(response => {
        console.log('Status updated:', response.data);
        // Update the local risk status
        const index = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
        if (index !== -1) {
          this.userRisks[index].MitigationStatus = 'Completed';
          this.userRisks[index].RiskStatus = 'Approved'; // Also update risk status
        }
        this.loading = false;
        this.$popup.success('Mitigation marked as completed!');
      })
      .catch(error => {
        console.error('Error updating status:', error);
        this.error = `Failed to update status: ${error.message}`;
        this.loading = false;
      });
    },
    viewMitigations(riskId) {
      this.selectedRiskId = riskId;
      this.loadingMitigations = true;
      this.showMitigationWorkflow = true; // Show workflow in full screen
      
      // First, get the basic mitigation steps
      axios.get(`http://localhost:8000/api/risk-mitigations/${riskId}/`)
        .then(response => {
          console.log('Mitigations received:', response.data);
          this.mitigationSteps = this.parseMitigations(response.data);
          
          // Get the risk form details
          axios.get(`http://localhost:8000/api/risk-form-details/${riskId}/`)
            .then(formResponse => {
              console.log('Form details received:', formResponse.data);
              // Ensure all form values are strings
              this.formDetails = {
                cost: String(formResponse.data.cost || ''),
                impact: String(formResponse.data.impact || ''),
                financialImpact: String(formResponse.data.financialImpact || ''),
                reputationalImpact: String(formResponse.data.reputationalImpact || ''),
                operationalImpact: String(formResponse.data.operationalImpact || ''),
                financialLoss: String(formResponse.data.financialLoss || ''),
                systemDowntime: String(formResponse.data.systemDowntime || ''),
                recoveryTime: String(formResponse.data.recoveryTime || ''),
                recurrencePossible: formResponse.data.recurrencePossible || '',
                improvementInitiative: formResponse.data.improvementInitiative || '',
                approved: formResponse.data.approved,
                remarks: formResponse.data.remarks || '',
                reviewer_id: formResponse.data.reviewer_id || '',
                reviewer: formResponse.data.reviewer || '',
                user_submitted_date: formResponse.data.user_submitted_date || formResponse.data.submission_date,
                reviewer_submitted_date: formResponse.data.reviewer_submitted_date
              };
              
              // Get the latest R version from risk_approval table to get approval status
              axios.get(`http://localhost:8000/api/latest-review/${riskId}/`)
                .then(reviewResponse => {
                  const reviewData = reviewResponse.data;
                  console.log('Latest review data:', reviewData);
                  
                  // Store the latest review
                  this.latestReview = reviewData;
                  
                  // Update form details with submission dates from the review data
                  if (reviewData && reviewData.risk_form_details) {
                    this.formDetails = {
                      ...this.formDetails,
                      approved: reviewData.risk_form_details.approved,
                      remarks: reviewData.risk_form_details.remarks || '',
                      user_submitted_date: reviewData.user_submitted_date || reviewData.submission_date,
                      reviewer_submitted_date: reviewData.reviewer_submitted_date || reviewData.review_date
                    };
                  }
                  
                  if (reviewData && reviewData.mitigations) {
                    // Create new steps array with proper boolean values for approved
                    const updatedSteps = [];
                    
                    // Process each mitigation from the review data
                    Object.keys(reviewData.mitigations).forEach(stepId => {
                      const mitigation = reviewData.mitigations[stepId];
                      
                      // Ensure approved is a proper boolean value if it exists, otherwise leave it undefined
                      let isApproved = undefined;
                      if ('approved' in mitigation) {
                        isApproved = mitigation.approved === true || mitigation.approved === "true";
                      }
                      
                      updatedSteps.push({
                        title: `Step ${stepId}`,
                        description: mitigation.description,
                        status: mitigation.status || 'Completed',
                        approved: isApproved,  // This could be undefined, true, or false
                        remarks: mitigation.remarks || '',
                        comments: mitigation.comments || '',
                        fileData: mitigation.fileData,
                        fileName: mitigation.fileName,
                        user_submitted_date: mitigation.user_submitted_date,  // Add user submission date
                        reviewer_submitted_date: mitigation.reviewer_submitted_date  // Add reviewer submission date
                      });
                    });
                    
                    // Replace the mitigation steps with the properly formatted data
                    this.mitigationSteps = updatedSteps;
                  }
                  
                  // Check if a reviewer is already assigned
                  axios.get(`http://localhost:8000/api/get-assigned-reviewer/${riskId}/`)
                    .then(reviewerResponse => {
                      console.log('Reviewer response:', reviewerResponse.data);
                      if (reviewerResponse.data && reviewerResponse.data.reviewer_name) {
                        // Always use reviewer_id if available
                        if (reviewerResponse.data.reviewer_id) {
                          this.selectedReviewer = reviewerResponse.data.reviewer_id;
                          console.log(`Using reviewer ID: ${this.selectedReviewer}`);
                        } else {
                          this.selectedReviewer = reviewerResponse.data.reviewer_name;
                          console.log(`No reviewer ID available, using name: ${this.selectedReviewer}`);
                        }
                      } else {
                        // If no reviewer is assigned yet, show a message
                        // this.$popup.warning('No reviewer has been assigned to this risk yet. Please contact your administrator.');
                        this.selectedReviewer = '';
                      }
                      this.loadingMitigations = false;
                      
                      // Show the questionnaire section by default
                      this.showQuestionnaire = true;
                    })
                    .catch(error => {
                      console.error('Error fetching assigned reviewer:', error);
                      this.$popup.error('Could not fetch reviewer information. Please try again later.');
                      this.selectedReviewer = '';
                      this.loadingMitigations = false;
                      
                      // Show the questionnaire section by default
                      this.showQuestionnaire = true;
                    });
                })
                .catch(error => {
                  console.error('Error fetching latest review:', error);
                  this.loadingMitigations = false;
                  
                  // Show the questionnaire section by default
                  this.showQuestionnaire = true;
                });
            })
            .catch(error => {
              console.error('Error fetching form details:', error);
              // Continue with default empty form details
              this.formDetails = {
                cost: '',
                impact: '',
                financialImpact: '',
                reputationalImpact: '',
                operationalImpact: '',
                financialLoss: '',
                systemDowntime: '',
                recoveryTime: '',
                recurrencePossible: '',
                improvementInitiative: '',
                approved: undefined,
                remarks: ''
              };
              this.loadingMitigations = false;
              
              // Show the questionnaire section by default
              this.showQuestionnaire = true;
            });
        })
        .catch(error => {
          console.error('Error fetching mitigations:', error);
          this.mitigationSteps = [];
          this.loadingMitigations = false;
          
          // Show the questionnaire section by default
          this.showQuestionnaire = true;
        });
    },
    fetchLatestReviewerData(riskId) {
      axios.get(`http://localhost:8000/api/latest-review/${riskId}/`)
        .then(response => {
          console.log('Latest review data:', response.data);
          
          if (response.data && response.data.mitigations) {
            // Update our mitigation steps with approval status and remarks
            const reviewData = response.data;
            
            this.mitigationSteps.forEach((step, index) => {
              const stepNumber = step.title.replace('Step ', '') || (index + 1).toString();
              if (reviewData.mitigations[stepNumber]) {
                const reviewInfo = reviewData.mitigations[stepNumber];
                step.approved = reviewInfo.approved;
                step.remarks = reviewInfo.remarks || '';
                
                // If this mitigation was already reviewed and had attached data
                if (reviewInfo.comments) step.comments = reviewInfo.comments;
                if (reviewInfo.fileData) {
                  step.fileData = reviewInfo.fileData;
                  step.fileName = reviewInfo.fileName;
                }
              }
            });
          }
          
          this.loadingMitigations = false;
        })
        .catch(error => {
          console.error('Error fetching review data:', error);
          this.loadingMitigations = false;
        });
    },
    parseMitigations(data) {
      // Handle the numbered object format like {"1": "Step 1 text", "2": "Step 2 text", ...}
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        // Check if it's a numbered format
        const keys = Object.keys(data);
        if (keys.length > 0 && !isNaN(Number(keys[0]))) {
          const steps = [];
          // Sort keys numerically
          keys.sort((a, b) => Number(a) - Number(b));
          
          for (const key of keys) {
            steps.push({
              title: `Step ${key}`,
              description: data[key],
              status: 'Not Started'
            });
          }
          
          // Add these lines after creating steps
          for (const step of steps) {
            step.comments = step.comments || '';
            step.fileData = step.fileData || null;
            step.fileName = step.fileName || null;
          }
          return steps;
        }
      }
      
      // If it's already an array, return it
      if (Array.isArray(data)) {
        return data;
      }
      
      // If data is a string, try to parse it as JSON
      if (typeof data === 'string') {
        try {
          const parsedData = JSON.parse(data);
          // Check if the parsed data matches the numbered format
          if (parsedData && typeof parsedData === 'object' && !Array.isArray(parsedData)) {
            return this.parseMitigations(parsedData); // Recursively call to handle the parsed object
          }
          return Array.isArray(parsedData) ? parsedData : [parsedData];
        } catch (e) {
          console.error('Error parsing mitigation JSON:', e);
          return [{ title: 'Mitigation', description: data }];
        }
      }
      
      // Default fallback - create a single step with the data
      return [{ title: 'Mitigation', description: 'No detailed mitigation steps available' }];
    },
    closeMitigationModal() {
      this.showMitigationWorkflow = false;
      this.mitigationSteps = [];
      this.selectedRiskId = null;
    },
    updateStepStatus(index, status) {
      console.log(`Updating step ${index + 1} status to ${status}`);
      
      // Update the step status locally
      this.mitigationSteps[index].status = status;
      
      // If all steps are completed, we don't need to update the backend yet
      // It will be sent when the user submits for review
    },
    submitForReview() {
      // Check if all required fields are filled
      const requiredFields = ['cost', 'impact', 'financialImpact', 'reputationalImpact', 
                             'operationalImpact', 'financialLoss', 'systemDowntime',
                             'recoveryTime', 'recurrencePossible', 'improvementInitiative'];
      
      const missingFields = requiredFields.filter(field => !this.formDetails[field]);
      
      if (missingFields.length > 0) {
        this.$popup.warning('Please complete all questionnaire fields before submitting');
        return;
      }
      
      const formData = {
        risk_id: this.selectedRiskId,
        reviewer_id: this.selectedReviewer,
        risk_form_details: this.formDetails,
        user_id: this.selectedUserId,
        create_approval_record: true,
        mitigations: this.mitigationSteps.reduce((obj, step, index) => {
          obj[index + 1] = {
            description: step.description,
            status: step.status,
            comments: step.comments || '',
            fileData: step.fileData,
            fileName: step.fileName
          };
          return obj;
        }, {})
      };
      
      axios.post('http://localhost:8000/api/assign-reviewer/', formData)
        .then(() => {
          this.$popup.success('Risk submitted for review successfully!');
          this.closeMitigationModal();
        })
        .catch(error => {
          console.error('Error submitting for review:', error);
          this.$popup.error('Failed to submit for review. Please try again.');
        });
    },
    closeReviewerModal() {
      this.showReviewerWorkflow = false;
      this.currentReviewTask = null;
      this.mitigationReviewData = {};
      this.previousVersions = {};
      this.previousFormDetails = null;
      this.reviewCompleted = false;
      this.reviewApproved = false;
      // Reset version-related data
      this.allVersions = [];
      this.selectedVersions = {};
      this.versionData = {};
      this.loadingVersions = false;
    },
    approveMitigation(id, approved) {
      // Don't use this.$set directly - modify the object properly for Vue reactivity
      
      // Create a new object with all existing properties
      const updatedMitigation = {
        ...this.mitigationReviewData[id],
        approved: approved,
        reviewer_submitted_date: new Date().toISOString()
      };
      
      // If approved, clear any existing remarks
      if (approved) {
        updatedMitigation.remarks = '';
      }
      
      // Update the entire object at once (Vue will detect this change)
      this.mitigationReviewData = {
        ...this.mitigationReviewData,
        [id]: updatedMitigation
      };
      
      // Find the mitigation element and update visual feedback
      const mitigationElement = document.querySelector(`.mitigation-review-item[data-id="${id}"]`);
      if (mitigationElement) {
        // Update visual feedback
        const statusBadge = mitigationElement.querySelector('.mitigation-status-badge');
        if (statusBadge) {
          statusBadge.className = `mitigation-status-badge ${approved ? 'approved' : 'rejected'}`;
          statusBadge.innerHTML = approved ? 
            '<i class="fas fa-check-circle"></i> Approved' : 
            '<i class="fas fa-times-circle"></i> Rejected';
        }
      }
    },
    submitReview(approved) {
      if (!approved && !this.formDetails.remarks.trim()) {
        this.$popup.warning('Please provide remarks for rejection');
        return;
      }
      
      const reviewData = {
        risk_instance_id: this.currentReviewTask.RiskInstanceId,
        approved: approved,
        remarks: this.formDetails.remarks,
        reviewer_id: this.selectedUserId
      };
      
      axios.post('http://localhost:8000/api/submit-review/', reviewData)
        .then(() => {
          this.$popup.success(`Risk ${approved ? 'approved' : 'rejected'} successfully!`);
          this.closeReviewerWorkflow();
        })
        .catch(error => {
          console.error('Error submitting review:', error);
          this.$popup.error('Failed to submit review. Please try again.');
        });
    },
    updateRemarks(id) {
      if (!this.mitigationReviewData[id].remarks.trim()) {
        this.$popup.warning('Please provide remarks for rejection');
        return;
      }
      
      // Create a new object with spread operator to trigger reactivity
      this.mitigationReviewData = {
        ...this.mitigationReviewData
      };
      
      // Show visual confirmation
      console.log(`Mitigation ${id} remarks updated successfully`);
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        this.$popup.error('File size exceeds 5MB limit');
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('risk_instance_id', this.selectedRiskId);
      
      axios.post('http://localhost:8000/api/upload-evidence/', formData)
        .then(() => {
          this.$popup.success('File uploaded successfully');
          // Refresh mitigation steps to show new evidence
          this.fetchMitigationSteps(this.selectedRiskId);
        })
        .catch(error => {
          console.error('Error uploading file:', error);
          this.$popup.error('Error uploading file. Please try again.');
        });
    },
    fetchReviewerComments(riskId) {
      axios.get(`http://localhost:8000/api/reviewer-comments/${riskId}/`)
        .then(response => {
          // Find the risk in the userRisks array and add the reviewer comments
          const riskIndex = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
          if (riskIndex !== -1) {
            // Create a new array with the updated risk object
            const updatedRisks = [...this.userRisks];
            updatedRisks[riskIndex] = {
              ...this.userRisks[riskIndex],
              reviewerComments: response.data
            };
            this.userRisks = updatedRisks;
          }
        })
        .catch(error => {
          console.error('Error fetching reviewer comments:', error);
        });
    },
    getStatusClass(status) {
      if (!status) return '';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('approved')) return 'status-approved';
      if (statusLower.includes('revision required by user')) return 'status-revision-user';
      if (statusLower.includes('revision required by reviewer')) return 'status-revision-reviewer';
      if (statusLower.includes('revision')) return 'status-revision';
      if (statusLower.includes('under review')) return 'status-review';
      if (statusLower.includes('progress')) return 'status-progress';
      return '';
    },
    // Complete a step
    completeStep(index) {
      this.mitigationSteps[index].status = 'Completed';
      this.mitigationSteps[index].user_submitted_date = new Date().toISOString();
      this.$popup.success('Mitigation marked as completed!');
    },
    
    // Reset a step to not completed
    resetStep(index) {
      this.mitigationSteps[index].status = 'In Progress';
    },
    isStepActive(index) {
      // A step is active if all previous steps are completed
      // and this step is not completed or is rejected
      if (this.mitigationSteps[index].approved === false) return true;
      
      for (let i = 0; i < index; i++) {
        if (this.mitigationSteps[i].status !== 'Completed') return false;
      }
      
      return this.mitigationSteps[index].status !== 'Completed';
    },
    
    isStepLocked(index) {
      // A step is locked if any previous step is not completed
      if (index === 0) return false; // First step is never locked
      
      for (let i = 0; i < index; i++) {
        if (this.mitigationSteps[i].status !== 'Completed') return true;
      }
      
      return false;
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set';
      
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getDueStatusClass(dateString) {
      if (!dateString) return '';
      
      const dueDate = new Date(dateString);
      const today = new Date();
      
      // Reset the time part for accurate day comparison
      dueDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      
      const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0) return 'risk-workflow-overdue';
      if (daysLeft <= 3) return 'risk-workflow-urgent';
      if (daysLeft <= 7) return 'risk-workflow-warning';
      return 'risk-workflow-on-track';
    },
    getDueStatusText(dateString) {
      if (!dateString) return '';
      
      const dueDate = new Date(dateString);
      const today = new Date();
      
      // Reset the time part for accurate day comparison
      dueDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      
      const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0) return `(Delayed by ${Math.abs(daysLeft)} days)`;
      if (daysLeft === 0) return '(Due today)';
      if (daysLeft === 1) return '(Due tomorrow)';
      return `(${daysLeft} days left)`;
    },
    getMitigationStatusClass(status) {
      if (!status) return '';
      
      const statusLower = status.toLowerCase();
      if (statusLower.includes('completed')) return 'risk-workflow-status-completed';
      if (statusLower.includes('progress')) return 'risk-workflow-status-progress';
      if (statusLower.includes('revision')) return 'risk-workflow-status-revision';
      if (statusLower.includes('yet to start')) return 'risk-workflow-status-not-started';
      return '';
    },
    hasApprovalVersion(task) {
      // Check if we have extracted info, which means there's a version
      try {
        if (task.ExtractedInfo) {
          const extractedInfo = JSON.parse(task.ExtractedInfo);
          return extractedInfo && extractedInfo.version;
        }
      } catch (error) {
        console.error('Error checking approval version:', error);
      }
      return false;
    },
    isQuestionnaireComplete() {
      // Always return true to enable the submission
      return true;
    },
    validateQuestionnaire() {
      // This will be called on each input to ensure sequential completion
    },
    async reviewMitigations(task) {
      // if (!task.ReviewerId) {
      //   this.$popup.warning('No reviewer has been assigned to this risk yet. Please contact your administrator.');
      //   return;
      // }
      axios.get(`http://localhost:8000/api/custom-users/${task.ReviewerId}/`)
        .then(response => {
          this.selectedReviewer = response.data;
          this.showReviewerWorkflow = true;
          this.currentReviewTask = task;
          this.fetchMitigationSteps(task.RiskInstanceId);
        })
        .catch(error => {
          console.error('Error fetching reviewer:', error);
          this.$popup.error('Could not fetch reviewer information. Please try again later.');
        });
    },
    approveQuestionnaire(approved) {
      // Update approval status
      this.formDetails.approved = approved;
      
      // Add timestamp for reviewer
      this.formDetails.reviewer_submitted_date = new Date().toISOString();
      
      // If rejecting, ensure there's a remarks field
      if (!approved && !this.formDetails.remarks) {
        this.formDetails.remarks = '';
      }
      
      // If approving, clear any remarks
      if (approved) {
        this.formDetails.remarks = '';
      }
    },
    saveQuestionnaireRemarks() {
      // Validate that remarks are provided when rejecting
      if (this.formDetails.approved === false && !this.formDetails.remarks.trim()) {
        this.$popup.warning('Please provide feedback for the questionnaire');
        return;
      }
      
      // Show confirmation to the user
      this.$popup.success('Questionnaire feedback saved');
    },
    // Format date and time
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch (error) {
        return 'Invalid Date';
      }
    },
    // Extract submission date from task
    getSubmissionDate(task) {
      try {
        if (task.ExtractedInfo) {
          const extractedInfo = JSON.parse(task.ExtractedInfo);
          return extractedInfo.user_submitted_date || extractedInfo.submission_date;
        }
      } catch (error) {
        console.error('Error parsing submission date:', error);
      }
      return null;
    },
    getPreviousMitigation(id) {
      // Check if we have previous versions stored
      if (!this.previousVersions || !this.previousVersions[id]) {
        return null;
      }
      return this.previousVersions[id];
    },
    getPreviousFormDetail(field) {
      if (!this.previousFormDetails) {
        return null;
      }
      return this.previousFormDetails[field] || 'Not specified';
    },
    // Add this method to check if form field has changed
    hasFormFieldChanged(field) {
      if (!this.previousFormDetails) {
        return false;
      }
      
      const prevValue = this.previousFormDetails[field] || '';
      const currentValue = this.formDetails[field] || '';
      
      return prevValue !== currentValue;
    },
    getFieldLabel(field) {
      const labels = {
        'cost': 'Cost for Mitigation',
        'impact': 'Impact for Mitigation',
        'financialImpact': 'Financial Impact',
        'reputationalImpact': 'Reputational Impact'
      };
      return labels[field] || field;
    },
    fetchQuestionnaire(riskInstanceId) {
      axios.get(`http://localhost:8000/api/risk-instances/${riskInstanceId}/`)
        .then(response => {
          let details = response.data.RiskFormDetails;
          if (typeof details === 'string') {
            try { details = JSON.parse(details); } catch { details = {}; }
          }
          this.questionnaireDetails = this.mapRiskFormDetails(details);
          this.showQuestionnaire = true;
        });
    },
    mapRiskFormDetails(details) {
      if (!details) return {
        cost: '', impact: '', financialImpact: '', reputationalImpact: '', operationalImpact: '', financialLoss: '', systemDowntime: '', recoveryTime: '', recurrencePossible: '', improvementInitiative: ''
      };
      function normalizeYN(val) {
        if (!val) return '';
        if (typeof val === 'string') {
          if (val.toLowerCase() === 'yes') return 'Yes';
          if (val.toLowerCase() === 'no') return 'No';
          if (val.toLowerCase() === 'unknown') return 'Unknown';
        }
        return val;
      }
      return {
        cost: details.cost ?? '',
        impact: details.impact ?? '',
        financialImpact: details.financialImpact ?? details.financialimpact ?? '',
        reputationalImpact: details.reputationalImpact ?? details.reputationalimpact ?? '',
        operationalImpact: details.operationalImpact ?? details.operationalimpact ?? '',
        financialLoss: details.financialLoss ?? details.financialloss ?? '',
        systemDowntime: details.systemDowntime ?? details.expecteddowntime ?? '',
        recoveryTime: details.recoveryTime ?? details.recoverytime ?? '',
        recurrencePossible: normalizeYN(details.recurrencePossible ?? details.riskrecurrence),
        improvementInitiative: normalizeYN(details.improvementInitiative ?? details.improvementinitiative)
      };
    },
    navigateTo(screen) {
      // Remove active class from all buttons
      const buttons = document.querySelectorAll('.toggle-button');
      buttons.forEach(button => button.classList.remove('active'));
      
      // Add active class to the clicked button
      const clickedButton = Array.from(buttons).find(button => 
        button.textContent.trim().toLowerCase().includes(screen)
      );
      if (clickedButton) clickedButton.classList.add('active');
      
      // Navigate to the appropriate screen
      switch(screen) {
        case 'resolution':
          this.$router.push('/risk/resolution');
          break;
        case 'workflow':
          // Already on workflow page
          break;
      }
    },
    // New methods for version management
    async onGlobalVersionChange() {
      // Apply the selected version to all mitigations
      console.log('Global version changed to:', this.globalSelectedVersion);
      
      if (!this.globalSelectedVersion) {
        console.log('No version selected, clearing selections');
        // Clear all selections
        this.selectedVersions = {};
        return;
      }
      
      // Show loading state
      this.loadingVersions = true;
      
      try {
        // Update all mitigation items with the selected version
        const riskId = this.currentReviewTask?.RiskInstanceId || this.selectedRiskId;
        
        // Fetch version details once for all mitigations
        console.log('Fetching version details for:', this.globalSelectedVersion);
        const response = await fetch(`http://localhost:8000/api/risk/${riskId}/version/${this.globalSelectedVersion}/`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const versionDetails = await response.json();
        console.log('Received version details:', versionDetails);
        
        if (versionDetails.success && versionDetails.version_data && versionDetails.version_data.ExtractedInfo) {
          let extractedInfo;
          try {
            extractedInfo = typeof versionDetails.version_data.ExtractedInfo === 'string' 
              ? JSON.parse(versionDetails.version_data.ExtractedInfo) 
              : versionDetails.version_data.ExtractedInfo;
          } catch (error) {
            console.error('Error parsing ExtractedInfo:', error);
            extractedInfo = { mitigations: {}, risk_form_details: {} };
          }
          
          // Process each mitigation
          Object.keys(this.mitigationReviewData).forEach(id => {
            // Update the selected version
            this.selectedVersions = {
              ...this.selectedVersions,
              [id]: this.globalSelectedVersion
            };
            
            // Get the mitigation data for this specific ID
            const mitigationData = extractedInfo.mitigations?.[id] || {};
            
            // Extract reviewer feedback from remarks or other fields
            let reviewerFeedback = '';
            
            // Check for remarks field first
            if (mitigationData.remarks) {
              reviewerFeedback = mitigationData.remarks;
            } 
            // Check for reviewer_feedback field if exists
            else if (mitigationData.reviewer_feedback) {
              reviewerFeedback = mitigationData.reviewer_feedback;
            }
            // Check if there's feedback in the version data itself
            else if (versionDetails.version_data.ReviewerFeedback) {
              reviewerFeedback = versionDetails.version_data.ReviewerFeedback;
            }
            // Check if there's feedback in the ExtractedInfo
            else if (extractedInfo.reviewer_feedback) {
              reviewerFeedback = extractedInfo.reviewer_feedback;
            }
            
            // Store the version data
            const versionKey = `${id}_${this.globalSelectedVersion}`;
            this.versionData = {
              ...this.versionData,
              [versionKey]: {
                ...mitigationData,
                version: this.globalSelectedVersion,
                RiskInstanceId: versionDetails.version_data.RiskInstanceId,
                UserId: versionDetails.version_data.UserId,
                ApproverId: versionDetails.version_data.ApproverId,
                Date: versionDetails.version_data.Date,
                formatted_date: versionDetails.version_data.formatted_date,
                approved: versionDetails.version_data.ApprovedRejected === 'Approved' ? true : 
                         versionDetails.version_data.ApprovedRejected === 'Rejected' ? false : undefined,
                reviewer_feedback: reviewerFeedback
              }
            };
          });
          
          console.log('Updated version data for all mitigations');
        }
      } catch (error) {
        console.error('Error in global version change:', error);
        this.$popup.error('Failed to load version data. Please try again.');
      } finally {
        this.loadingVersions = false;
      }
    },
    
    async fetchAllVersions() {
      // Only fetch versions for reviewer workflow, not for user mitigation workflow
      if (!this.showReviewerWorkflow) {
        console.log('Not in reviewer workflow, skipping version fetch');
        return;
      }
      
      const riskId = this.currentReviewTask?.RiskInstanceId || this.selectedRiskId;
      
      if (!riskId) {
        console.log('No risk ID available for fetching versions');
        return;
      }
      
      console.log(`\n=== FETCHING ALL VERSIONS ===`);
      console.log(`Risk ID: ${riskId}`);
      console.log(`API URL: http://localhost:8000/api/risk/${riskId}/versions/`);
      console.log(`Current mitigation review data keys:`, Object.keys(this.mitigationReviewData));
      
      this.loadingVersions = true;
      
      try {
        console.log('Making API call...');
        const response = await fetch(`http://localhost:8000/api/risk/${riskId}/versions/`);
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
        }
        
        const responseData = await response.json();
        console.log(`Full API Response:`, responseData);
        console.log(`Response type:`, typeof responseData);
        console.log(`Response keys:`, Object.keys(responseData || {}));
        
        // Handle the response structure properly
        const versions = responseData.versions || responseData || [];
        console.log(`Extracted versions:`, versions);
        console.log(`Total versions received:`, versions.length);
        console.log(`Versions array type:`, Array.isArray(versions));
        
        // Extract version names directly from the response if available
        if (responseData.version_names && Array.isArray(responseData.version_names)) {
          // Filter only R versions
          this.allVersionNames = responseData.version_names.filter(version => 
            version && version.toString().startsWith('R')
          );
          console.log(`Using filtered R version_names from API response:`, this.allVersionNames);
        } else {
          // Fall back to extracting from versions array
          this.allVersionNames = versions
            .map(v => v.version)
            .filter(version => version && version.toString().startsWith('R'));
          console.log(`Extracted filtered R version names from versions array:`, this.allVersionNames);
        }
        
        if (versions && versions.length > 0) {
          this.allVersions = versions;
          console.log(`Set allVersions to:`, this.allVersions);
          
          // Log details for each version
          versions.forEach((version, index) => {
            console.log(`Version ${index + 1}:`, {
              version: version.version,
              RiskInstanceId: version.RiskInstanceId,
              UserId: version.UserId,
              ApproverId: version.ApproverId,
              Date: version.Date,
              ApprovedRejected: version.ApprovedRejected,
              mitigationCount: version.mitigations ? Object.keys(version.mitigations).length : 0,
              formDetailsCount: version.risk_form_details ? Object.keys(version.risk_form_details).length : 0
            });
          });
          
          // Initialize selectedVersions for each mitigation (don't auto-select any version)
          Object.keys(this.mitigationReviewData).forEach(mitigationId => {
            if (!this.selectedVersions[mitigationId]) {
              // Replace this.$set with direct assignment
              this.selectedVersions = {
                ...this.selectedVersions,
                [mitigationId]: ''
              };
            }
          });
          
          console.log('Final selectedVersions state:', this.selectedVersions);
          console.log('Final allVersions length:', this.allVersions.length);
          console.log('Final allVersionNames:', this.allVersionNames);
          
        } else {
          console.log('No versions found or empty array');
          console.log('Setting allVersions to empty array');
          this.allVersions = [];
          this.allVersionNames = [];
        }
        
      } catch (error) {
        console.error('ERROR fetching versions:', error);
        console.error('Error type:', error.constructor.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
        this.allVersions = [];
        this.allVersionNames = [];
      } finally {
        this.loadingVersions = false;
        console.log('fetchAllVersions completed. Final allVersions length:', this.allVersions.length);
        console.log('Final allVersionNames:', this.allVersionNames);
      }
    },
    async fetchVersionDetails(riskId, version) {
      console.log(`\n=== FETCH VERSION DETAILS ===`);
      console.log(`Risk ID: ${riskId}`);
      console.log(`Version: ${version}`);
      
      try {
        const response = await axios.get(`http://localhost:8000/api/risk/${riskId}/version/${version}/`);
        console.log('API Response:', response.data);
        
        if (response.data.success) {
          console.log('Version data successfully retrieved');
          console.log('Version data keys:', Object.keys(response.data.version_data));
          
          if (response.data.version_data.ExtractedInfo) {
            console.log('ExtractedInfo keys:', Object.keys(response.data.version_data.ExtractedInfo));
            if (response.data.version_data.ExtractedInfo.mitigations) {
              console.log('Available mitigations:', Object.keys(response.data.version_data.ExtractedInfo.mitigations));
            }
          }
          
          return response.data.version_data.ExtractedInfo || response.data.version_data;
        } else {
          console.log('API returned success: false');
          return null;
        }
      } catch (error) {
        console.error(`Error fetching version ${version}:`, error);
        console.error('Error response:', error.response?.data);
        return null;
      }
    },
    async onVersionChange(mitigationId, selectedVersion) {
      console.log('Version changed for mitigation:', mitigationId, 'to version:', selectedVersion);
      
      if (!selectedVersion) {
        console.log('No version selected, clearing data');
        return;
      }
      
      // Check if we already have the data for this version
      const versionKey = `${mitigationId}_${selectedVersion}`;
      if (this.versionData[versionKey]) {
        console.log('Version data already loaded for:', versionKey);
        return;
      }
      
      try {
        const riskId = this.currentReviewTask?.RiskInstanceId || this.selectedRiskId;
        console.log('Fetching version details for:', selectedVersion, 'with risk ID:', riskId);
        const response = await fetch(`http://localhost:8000/api/risk/${riskId}/version/${selectedVersion}/`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const versionDetails = await response.json();
        console.log('Received version details:', versionDetails);
        
        // Parse the version data and store it
        if (versionDetails.success && versionDetails.version_data && versionDetails.version_data.ExtractedInfo) {
          let extractedInfo;
          try {
            extractedInfo = typeof versionDetails.version_data.ExtractedInfo === 'string' 
              ? JSON.parse(versionDetails.version_data.ExtractedInfo) 
              : versionDetails.version_data.ExtractedInfo;
          } catch (error) {
            console.error('Error parsing ExtractedInfo:', error);
            extractedInfo = { mitigations: {}, risk_form_details: {} };
          }
          
          // Find the mitigation data for this specific mitigation ID
          const mitigationData = extractedInfo.mitigations[mitigationId] || {};
          console.log('Mitigation data for', mitigationId, ':', mitigationData);
          
          // Extract reviewer feedback from remarks or other fields
          let reviewerFeedback = '';
          
          // Check for remarks field first
          if (mitigationData.remarks) {
            reviewerFeedback = mitigationData.remarks;
          } 
          // Check for reviewer_feedback field if exists
          else if (mitigationData.reviewer_feedback) {
            reviewerFeedback = mitigationData.reviewer_feedback;
          }
          // Check if there's feedback in the version data itself
          else if (versionDetails.version_data.ReviewerFeedback) {
            reviewerFeedback = versionDetails.version_data.ReviewerFeedback;
          }
          // Check if there's feedback in the ExtractedInfo
          else if (extractedInfo.reviewer_feedback) {
            reviewerFeedback = extractedInfo.reviewer_feedback;
          }
          
          console.log('Extracted reviewer feedback:', reviewerFeedback);
          
          // Store the version data using the correct field names
          this.versionData = {
            ...this.versionData,
            [versionKey]: {
              ...mitigationData,
              version: selectedVersion,
              RiskInstanceId: versionDetails.version_data.RiskInstanceId,
              UserId: versionDetails.version_data.UserId,
              ApproverId: versionDetails.version_data.ApproverId,
              Date: versionDetails.version_data.Date,
              formatted_date: versionDetails.version_data.formatted_date,
              approved: versionDetails.version_data.ApprovedRejected === 'Approved' ? true : 
                       versionDetails.version_data.ApprovedRejected === 'Rejected' ? false : undefined,
              reviewer_feedback: reviewerFeedback
            }
          };
          
          console.log('Stored version data:', this.versionData[versionKey]);
        }
        
      } catch (error) {
        console.error('Error fetching version details:', error);
        // Show user-friendly error message if toast is available
        if (this.$toast) {
          this.$toast.error('Failed to load version details. Please try again.');
        } else {
          console.error('Failed to load version details. Please try again.');
        }
      }
    },
    getVersionDisplayData(mitigationId, selectedVersion) {
      if (selectedVersion === 'current') {
        return this.mitigationReviewData[mitigationId];
      }
      return this.versionData[`${mitigationId}_${selectedVersion}`] || {};
    },
    getVersionOptions() {
      const options = [{ value: 'current', label: 'Current Version' }];
      
      // Add all available versions (excluding the current one)
      this.allVersions.forEach(version => {
        if (version.version !== this.currentReviewTask?.version) {
          options.push({
            value: version.version,
            label: `Version ${version.version} (${this.formatDateTime(version.formatted_date)})`
          });
        }
      });
      
      return options;
    },
    getAllVersionsExceptCurrent() {
      if (!this.allVersions || this.allVersions.length === 0) {
        return [];
      }
      
      // Get the current version from the review task
      let currentVersion = null;
      
      // Try to determine current version from the review task
      if (this.currentReviewTask && this.currentReviewTask.ExtractedInfo) {
        try {
          const extractedInfo = typeof this.currentReviewTask.ExtractedInfo === 'string' 
            ? JSON.parse(this.currentReviewTask.ExtractedInfo)
            : this.currentReviewTask.ExtractedInfo;
          
          if (extractedInfo.version) {
            currentVersion = extractedInfo.version;
          }
        } catch (error) {
          console.error('Error parsing current task ExtractedInfo:', error);
        }
      }
      
      // If we couldn't determine the current version, assume it's the latest one
      if (!currentVersion && this.allVersions.length > 0) {
        // Sort versions and take the latest
        const sortedVersions = [...this.allVersions].sort((a, b) => {
          // Extract numeric part from version (e.g., "R1" -> 1, "U2" -> 2)
          const getVersionNumber = (version) => {
            const match = version.match(/\d+/);
            return match ? parseInt(match[0]) : 0;
          };
          return getVersionNumber(b.version) - getVersionNumber(a.version);
        });
        currentVersion = sortedVersions[0].version;
      }
      
      console.log('Current version identified as:', currentVersion);
      console.log('All versions:', this.allVersions.map(v => v.version));
      
      // Filter out the current version
      const filteredVersions = this.allVersions.filter(version => version.version !== currentVersion);
      console.log('Filtered versions (excluding current):', filteredVersions.map(v => v.version));
      
      return filteredVersions;
    },
    getSelectedVersionData(id, selectedVersion) {
      return this.versionData[`${id}_${selectedVersion}`] || {};
    },
    getCurrentVersionLabel() {
      if (!this.allVersions || this.allVersions.length === 0) {
        return 'Current';
      }
      
      // Get the current version from the review task
      let currentVersion = null;
      
      // Try to determine current version from the review task
      if (this.currentReviewTask && this.currentReviewTask.ExtractedInfo) {
        try {
          const extractedInfo = typeof this.currentReviewTask.ExtractedInfo === 'string' 
            ? JSON.parse(this.currentReviewTask.ExtractedInfo)
            : this.currentReviewTask.ExtractedInfo;
          
          if (extractedInfo.version) {
            currentVersion = extractedInfo.version;
          }
        } catch (error) {
          console.error('Error parsing current task ExtractedInfo:', error);
        }
      }
      
      // If we couldn't determine the current version, assume it's the latest one
      if (!currentVersion && this.allVersions.length > 0) {
        // Sort versions and take the latest
        const sortedVersions = [...this.allVersions].sort((a, b) => {
          // Extract numeric part from version (e.g., "R1" -> 1, "U2" -> 2)
          const getVersionNumber = (version) => {
            const match = version.match(/\d+/);
            return match ? parseInt(match[0]) : 0;
          };
          return getVersionNumber(b.version) - getVersionNumber(a.version);
        });
        currentVersion = sortedVersions[0].version;
      }
      
      // Find the current version data
      const currentVersionData = this.allVersions.find(version => version.version === currentVersion);
      
      if (currentVersionData && currentVersionData.formatted_date) {
        return `Version ${currentVersion} (${this.formatDateTime(currentVersionData.formatted_date)})`;
      } else if (currentVersionData && currentVersionData.Date) {
        return `Version ${currentVersion} (${this.formatDateTime(currentVersionData.Date)})`;
      } else {
        return `Version ${currentVersion || 'Current'}`;
      }
    },
    getVersionStatus(version) {
      // Determine status based on version data
      if (version.ApprovedRejected === 'Approved') {
        return 'Approved';
      } else if (version.ApprovedRejected === 'Rejected') {
        return 'Rejected';
      } else if (version.approved === true) {
        return 'Approved';
      } else if (version.approved === false) {
        return 'Rejected';
      } else {
        return 'Pending';
      }
    },
    handleUserTaskClick(task) {
      // Handle user task click - pass the RiskInstanceId to viewMitigations
      this.viewMitigations(task.RiskInstanceId);
    },
    handleReviewerTaskClick(task) {
      // Handle reviewer task click - pass the full task object to reviewMitigations
      this.reviewMitigations(task);
    },
    handleUserSectionToggle(status) {
      // Toggle the expanded state for user task sections
      const key = `user_${status}`;
      this.expandedSections[key] = !this.expandedSections[key];
    },
    handleReviewerSectionToggle(status) {
      // Toggle the expanded state for reviewer task sections
      const key = `reviewer_${status}`;
      this.expandedSections[key] = !this.expandedSections[key];
    },
    initializeExpandedSections() {
      // Initialize all sections as expanded by default
      this.expandedSections = {};
      
      // Set user sections as expanded
      Object.keys(this.groupedUserRisks).forEach(status => {
        this.expandedSections[`user_${status}`] = true;
      });
      
      // Set reviewer sections as expanded
      Object.keys(this.groupedReviewerTasks).forEach(status => {
        this.expandedSections[`reviewer_${status}`] = true;
      });
    },
    submitQuestionnaireFeedback() {
      if (!this.formDetails.remarks.trim()) {
        this.$popup.warning('Please provide feedback for the questionnaire');
        return;
      }
      
      const feedbackData = {
        risk_instance_id: this.currentReviewTask.RiskInstanceId,
        feedback: this.formDetails.remarks,
        reviewer_id: this.selectedUserId
      };
      
      axios.post('http://localhost:8000/api/questionnaire-feedback/', feedbackData)
        .then(() => {
          this.$popup.success('Questionnaire feedback saved');
          this.formDetails.remarks = '';
        })
        .catch(error => {
          console.error('Error saving feedback:', error);
          this.$popup.error('Failed to save feedback. Please try again.');
        });
    },
    loadVersionData() {
      this.loadingVersions = true;
      axios.get(`http://localhost:8000/api/risk-versions/${this.currentReviewTask.RiskInstanceId}/`)
        .then(response => {
          this.versionData = response.data;
          this.loadingVersions = false;
        })
        .catch(error => {
          console.error('Error loading version data:', error);
          this.$popup.error('Failed to load version data. Please try again.');
          this.loadingVersions = false;
        });
    },
  }
}
</script>

<style scoped>
@import './RiskWorkflow.css';

/* Add additional styles for the section title */
.section-title {
  margin: 20px 0;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
}

/* Enhance the toggle buttons styling */
.toggle-buttons {
  display: flex;
  background: #f8f9fa;
  border-radius: 50px;
  overflow: hidden;
  width: fit-content;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin: 30px auto;
}

.toggle-button {
  padding: 12px 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #555;
  transition: all 0.3s ease;
  position: relative;
  outline: none;
  min-width: 180px;
  text-align: center;
}

.toggle-button:not(:last-child) {
  border-right: 1px solid #eee;
}

.toggle-button:hover {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.toggle-button.active {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
}

/* Update due status styling to be more visible */
.due-status {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.due-status.overdue {
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.due-status.urgent {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.due-status.warning {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.due-status.on-track {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
  padding: 2px 8px;
  background-color: #f5f5f5;
  border-radius: 10px;
}

/* Add styles for mitigation status badges */
.mitigation-status.status-completed {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status.status-progress {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.mitigation-status.status-revision {
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.mitigation-status.status-not-started {
  background-color: #f5f5f5;
  color: #8c8c8c;
  border: 1px solid #d9d9d9;
}

.complete-btn {
  background-color: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.complete-btn:hover {
  background-color: #73d13d;
}

/* Add these new styles for submission dates */
.submission-date {
  font-size: 12px;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  width: fit-content;
}

.submission-date.user-date {
  background-color: #e6f7ff;
  color: #1890ff;
}

.submission-date.reviewer-date {
  background-color: #f6ffed;
  color: #52c41a;
}

.edit-questionnaire-section {
  margin-bottom: 20px;
}

.edit-questionnaire-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.edit-questionnaire-btn:hover {
  background-color: #45a049;
}

.edit-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 5px;
}

.edit-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.save-changes-btn {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-edit-btn {
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Add these new styles for status badges */
.status-revision-user, .status-revision-reviewer, .status-approved, .status-review, .status-revision, .status-progress {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
  margin-right: 5px;
}

/* Add these new styles for status badges */
.status-revision-user {
  background-color: #fff2e8;
  color: #fa541c;
  border: 1px solid #ffbb96;
}

.status-revision-reviewer {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-approved {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-review {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-revision {
  background-color: #fff2e8;
  color: #fa541c;
  border: 1px solid #ffbb96;
}

.status-progress {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #d3d4d6;
}

/* Version dropdown styles */
.version-dropdown {
  margin-top: 8px;
  margin-bottom: 8px;
}

.version-select {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}

.version-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.version-label {
  display: flex;
  flex-direction: column;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.version-label .version-dropdown {
  font-weight: normal;
}

/* Loading state for version dropdown */
.version-select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Enhanced mitigation content styling for better version comparison */
.mitigation-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Version comparison highlighting */
.version-changed {
  background-color: #fff7e6;
  border-left: 3px solid #faad14;
  padding-left: 8px;
  margin-left: -8px;
}

.version-added {
  background-color: #f6ffed;
  border-left: 3px solid #52c41a;
  padding-left: 8px;
  margin-left: -8px;
}

.version-removed {
  background-color: #fff1f0;
  border-left: 3px solid #f5222d;
  padding-left: 8px;
  margin-left: -8px;
  opacity: 0.7;
}

/* Version comparison styles */
.version-dropdown {
  margin-top: 8px;
}

.version-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  color: #333;
}

.version-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.version-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  font-size: 16px;
}

.metadata-section {
  margin: 16px 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.metadata-item {
  display: flex;
  margin-bottom: 8px;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.metadata-label {
  font-weight: 600;
  min-width: 120px;
  color: #6c757d;
  font-size: 14px;
}

.metadata-value {
  color: #495057;
  font-size: 14px;
}

.comments-section, .evidence-section, .remarks-section {
  margin: 16px 0;
  padding: 12px;
  border-radius: 6px;
}

.comments-section {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.evidence-section {
  background-color: #f3e5f5;
  border-left: 4px solid #9c27b0;
}

.remarks-section {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.comments-text, .remarks-text {
  margin: 8px 0 0 0;
  font-style: italic;
  color: #495057;
}

.evidence-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  margin-top: 8px;
}

.evidence-link:hover {
  text-decoration: underline;
}

.decision-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  margin: 16px 0;
}

.decision-tag.approved {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.decision-tag.rejected {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.mitigation-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6c757d;
  text-align: center;
}

.mitigation-empty i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.mitigation-empty p {
  margin: 0;
  font-style: italic;
}

.text-success {
  color: #28a745 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.global-version-dropdown {
  margin: 0 0 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.global-version-dropdown label {
  font-weight: 600;
  color: #495057;
  min-width: 180px;
}

.global-version-select {
  flex: 1;
  min-width: 250px;
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  color: #495057;
  cursor: pointer;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.global-version-select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.global-version-select:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

/* Add loading indicator for version dropdown */
.global-version-dropdown.loading::after {
  content: "Loading...";
  margin-left: 10px;
  font-style: italic;
  color: #6c757d;
}

/* Add version badge styling */
.version-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #e9ecef;
  color: #495057;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 10px;
}

.version-badge i {
  margin-right: 5px;
  font-size: 10px;
}

.no-versions-message {
  margin-left: 15px;
  color: #6c757d;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 8px;
}

.no-versions-message i {
  color: #17a2b8;
}

.reviewer-feedback-section {
  margin: 16px 0;
  padding: 12px;
  border-radius: 6px;
  background-color: #fff3e0;
  border-left: 4px solid #ff9800;
}

.reviewer-feedback-section h5 {
  color: #e65100;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reviewer-feedback-section h5 i {
  font-size: 16px;
}

.reviewer-feedback-text {
  margin: 8px 0 0 0;
  font-style: italic;
  color: #5d4037;
  line-height: 1.5;
}
</style>