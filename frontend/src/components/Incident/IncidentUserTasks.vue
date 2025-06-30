<template>
    <div class="workflow-container incident-workflow-container user-tasks-container">
      <!-- Show tasks view when not viewing any workflows -->
      <div v-if="!showMitigationWorkflow && !showReviewerWorkflow">
        <div class="incident-form-page-header">
          <h2 class="incident-form-page-title">User Task Management</h2>
        </div>
        
        <div class="user-filter">
          <div class="filter-group">
            <CustomDropdown 
              :config="userDropdownConfig" 
              v-model="selectedUserId" 
              @change="onUserChange"
            />
          </div>
          <div class="filter-group">
            <CustomDropdown 
              :config="statusDropdownConfig" 
              v-model="selectedStatus" 
              @change="onStatusChange"
            />
          </div>
        </div>
        
        <!-- Tabs for User Tasks and Reviewer Tasks -->
        <div class="tabs">
          <div 
            class="tab" 
            :class="{ 'active': activeTab === 'user' }" 
            @click="activeTab = 'user'"
          >
            My Tasks ({{ userIncidents.length }})
          </div>
          <div 
            class="tab" 
            :class="{ 'active': activeTab === 'reviewer' }" 
            @click="switchToReviewerTab"
          >
            Reviewer Tasks ({{ reviewerTasks.length }})
          </div>
        </div>
        
        
        
        <div v-if="loading" class="loading">
          Loading data...
        </div>
        
        <div v-else-if="error" class="error-message">
          {{ error }}
        </div>
        
        <!-- User Tasks Section -->
        <div v-if="activeTab === 'user'">
          <div v-if="!selectedUserId" class="no-data">
            <p>Please select a user to view their assigned tasks.</p>
          </div>
          <div v-else-if="userIncidents.length === 0" class="no-data">
            <p>No tasks assigned to this user.</p>
          </div>
          <div v-else>
            <!-- Collapsible Tables for User Incidents -->
            <div v-for="(sectionConfig, status) in userIncidentSections" :key="status">
              <CollapsibleTable
                :section-config="sectionConfig"
                :table-headers="tableHeaders"
                :is-expanded="expandedSections[status] !== false"
                @toggle="toggleSection(status)"
                @add-task="handleAddTask(status)"
                @task-click="handleTaskClick"
              />
            </div>
          </div>
        </div>
        
        <!-- Reviewer Tasks Section -->
        <div v-if="activeTab === 'reviewer'" class="reviewer-tasks-section">
          <div v-if="!selectedUserId" class="no-data">
            <p>Please select a user to view their reviewer tasks.</p>
          </div>
          <div v-else-if="reviewerTasks.length === 0" class="no-data">
            <p>No review tasks assigned to this user.</p>
            <p><small>Debug: reviewerTasks array length: {{ reviewerTasks.length }}</small></p>
            <p><small>Debug: selectedUserId: {{ selectedUserId }}</small></p>
          </div>
          <div v-else>
            <!-- Collapsible Tables for Reviewer Tasks -->
            <div v-for="(sectionConfig, status) in reviewerTaskSections" :key="status">
              <CollapsibleTable
                :section-config="sectionConfig"
                :table-headers="reviewerTableHeaders"
                :is-expanded="expandedSections[status] !== false"
                @toggle="toggleSection(status)"
                @add-task="handleAddTask(status)"
                @task-click="handleTaskClick"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Incident Mitigation Workflow view (Full screen instead of modal) -->
      <div v-if="showMitigationWorkflow" class="workflow-fullscreen">
        <div class="back-to-tasks">
          <button @click="closeMitigationModal" class="back-btn" title="Back to tasks">
            <i class="fas fa-arrow-left"></i>
          </button>
        </div>
        
        <h1>{{ isAuditFinding ? 'Audit Finding' : 'Incident' }} Mitigation Workflow</h1>
        
        <!-- Rejection Banner for Rejected Incidents -->
        <div v-if="isIncidentRejected" class="rejection-banner">
          <div class="rejection-banner-content">
            <div class="rejection-banner-icon">⚠️</div>
            <div class="rejection-banner-text">
              <h3>This incident has been rejected and requires resubmission</h3>
              <p>The reviewer has rejected your submission. Please review the feedback below, update the required information, and resubmit for review.</p>
            </div>
          </div>
        </div>
        
        <div v-if="loadingMitigations" class="loading">
          <div class="spinner"></div>
          <span>Loading mitigation steps...</span>
        </div>
        <div v-else-if="!mitigationSteps.length" class="no-data">
          No mitigation steps found for this incident.
        </div>
        <div v-else class="simplified-workflow">
          <!-- Vertical timeline with connected steps -->
          <div class="timeline">
            <div 
              v-for="(step, index) in mitigationSteps" 
              :key="index" 
              class="timeline-step"
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
              <div class="step-circle">
                <span v-if="step.status === 'Completed'"><i class="fas fa-check"></i></span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              
              <!-- Step content -->
              <div class="step-box">
                <h3>{{ step.description }}</h3>
                
                <!-- Show approval status for approved steps -->
                <div v-if="step.approved === true" class="approval-indicator approved">
                  <i class="fas fa-check-circle"></i> This step has been approved by the reviewer
                </div>
                
                <!-- Show rejection status for rejected steps -->
                <div v-if="step.approved === false" class="approval-indicator rejected">
                  <i class="fas fa-times-circle"></i> This step was rejected by the reviewer and needs to be updated
                  <div v-if="step.remarks" class="rejection-remarks">
                    <strong>Reviewer Feedback:</strong> {{ step.remarks }}
                  </div>
                </div>
                
                <!-- Show pending status -->
                <div v-if="step.approved === null && step.status === 'Completed'" class="approval-indicator pending">
                  <i class="fas fa-clock"></i> This step is completed and awaiting reviewer approval
                </div>
                
                <!-- Add submission dates when available -->
                <div v-if="step.user_submitted_date" class="submission-date user-date">
                  <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(step.user_submitted_date) }}
                </div>
                <div v-if="step.reviewer_submitted_date" class="submission-date reviewer-date">
                  <i class="fas fa-clock"></i> Reviewed: {{ formatDateTime(step.reviewer_submitted_date) }}
                </div>
                
                <!-- Only show step inputs for rejected steps or steps that haven't been reviewed yet -->
                <div v-if="step.approved === false || step.approved === null" class="step-inputs">
                  <!-- Previous Comments Display (if any) -->
                  <div v-if="step.previousComments && step.previousComments.trim()" class="previous-comments-display">
                    <h4><i class="fas fa-history"></i> Previous Comments</h4>
                    <div class="previous-comments-content">
                      {{ step.previousComments }}
                    </div>
                  </div>
                  
                  <!-- Comments section -->
                  <div class="input-group">
                    <label for="comments">{{ step.previousComments && step.previousComments.trim() ? 'Add New Comments:' : 'Comments:' }}</label>
                    <textarea 
                      id="comments" 
                      v-model="step.comments" 
                      :placeholder="step.previousComments && step.previousComments.trim() ? 'Add additional comments about this mitigation step...' : 'Add your comments about this mitigation step...'"
                      rows="3"
                    ></textarea>
                  </div>
                  
                  <!-- File upload section -->
                  <div class="file-upload">
                    <label class="upload-btn">
                      <i class="fas fa-upload"></i> Upload Evidence
                      <input type="file" @change="handleFileUpload($event, index)" accept=".pdf,.doc,.docx,.jpg,.png">
                    </label>
                    <div v-if="step.uploading" class="file-uploading">
                      <i class="fas fa-spinner fa-spin"></i> Uploading...
                    </div>
                    <div v-else-if="step.fileName" class="file-name">
                      <i class="fas fa-file"></i> {{ step.fileName }}
                    </div>
                  </div>
                  
                  <!-- Status control -->
                  <div class="status-control">
                    <button 
                      @click="updateStepStatus(index, 'Completed')" 
                      class="complete-btn"
                      :class="{ 'active': step.status === 'Completed' }"
                    >
                      <i class="fas fa-check"></i> Mark as Complete
                    </button>
                  </div>
                </div>
                
                <!-- Show read-only information for approved steps -->
                <div v-else class="step-readonly">
                  <div v-if="step.previousComments || step.comments" class="comments-display">
                    <h4><i class="fas fa-comment"></i> Comments</h4>
                    <p>{{ step.previousComments || step.comments }}</p>
                  </div>
                  
                  <div v-if="step.fileName" class="file-display">
                    <h4><i class="fas fa-file"></i> Evidence</h4>
                    <a :href="step['aws-file_link']" :download="step.fileName" target="_blank">
                      <i class="fas fa-download"></i> {{ step.fileName }}
                    </a>
                  </div>
                  
                  <div class="approved-status-display">
                    <i class="fas fa-lock"></i> This mitigation has been approved and is locked for editing
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Show assessment feedback if incident was rejected due to assessment -->
          <div v-if="assessmentFeedbackForUser && !assessmentFeedbackForUser.approved" class="assessment-rejection-notice">
            <h3><i class="fas fa-exclamation-triangle"></i> Assessment Requires Revision</h3>
            <p>The reviewer has rejected your assessment and provided the following feedback:</p>
            <div class="assessment-rejection-feedback">
              <strong>Reviewer's Feedback:</strong>
              <p>{{ assessmentFeedbackForUser.remarks }}</p>
            </div>
            <p>Please review the feedback and update your assessment by completing the questionnaire again.</p>
          </div>

          <!-- Questionnaire appears when all mitigations are completed -->
          <div v-if="allStepsCompleted && !showQuestionnaire" class="completion-notice">
            <h3>All Mitigation Steps Completed!</h3>
            <p>Please complete the incident assessment questionnaire to finalize your submission.</p>
            <button @click="showQuestionnaire = true" class="show-questionnaire-btn">
              <i class="fas fa-clipboard-list"></i> Complete Assessment
            </button>
          </div>

          <!-- Questionnaire Section -->
          <div v-if="showQuestionnaire" class="questionnaire-section">
            <h3>Incident Assessment Questionnaire</h3>
            
            <div class="questionnaire-form">
              <!-- Question 1: Cost -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">1</span>
                  What is the total cost for implementing this mitigation? (Optional)
                </label>
                <div class="input-with-prefix">
                  <span class="currency-prefix">$</span>
                  <input 
                    type="number" 
                    v-model="questionnaireData.cost" 
                    placeholder="Enter amount (e.g., 5000.50) - Include all direct and indirect costs for implementation"
                    class="question-input currency-input"
                    min="0"
                    step="0.01"
                    @input="validateCurrencyInput('cost', $event)"
                  />
                </div>
                <small class="field-hint">Include labor, materials, technology, and any third-party costs</small>
              </div>

              <!-- Question 2: Impact -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">2</span>
                  What is the overall impact level of this incident? (Optional)
                </label>
                <select v-model="questionnaireData.impact" class="question-select">
                  <option value="">Select impact level...</option>
                  <option value="Very Low">Very Low - Minimal disruption, easily contained</option>
                  <option value="Low">Low - Minor disruption, limited scope</option>
                  <option value="Medium">Medium - Moderate disruption, manageable impact</option>
                  <option value="High">High - Significant disruption, widespread impact</option>
                  <option value="Very High">Very High - Severe disruption, critical impact</option>
                </select>
                <small class="field-hint">Consider operational, business, and stakeholder impact</small>
              </div>

              <!-- Question 3: Financial Impact -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">3</span>
                  What is the financial impact scale of this incident? (Optional)
                </label>
                <select v-model="questionnaireData.financialImpact" class="question-select">
                  <option value="">Select financial impact level...</option>
                  <option value="Very Low">Very Low - Under $1,000 in losses/costs</option>
                  <option value="Low">Low - $1,000 - $10,000 in losses/costs</option>
                  <option value="Medium">Medium - $10,000 - $100,000 in losses/costs</option>
                  <option value="High">High - $100,000 - $1,000,000 in losses/costs</option>
                  <option value="Very High">Very High - Over $1,000,000 in losses/costs</option>
                </select>
                <small class="field-hint">Include direct losses, opportunity costs, and recovery expenses</small>
              </div>

              <!-- Question 4: Reputational Impact -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">4</span>
                  What is the reputational impact scale of this incident? (Optional)
                </label>
                <select v-model="questionnaireData.reputationalImpact" class="question-select">
                  <option value="">Select reputational impact level...</option>
                  <option value="Very Low">Very Low - Minimal or no reputational damage</option>
                  <option value="Low">Low - Minor reputational concerns, limited visibility</option>
                  <option value="Medium">Medium - Moderate reputational impact, some stakeholder concern</option>
                  <option value="High">High - Significant reputational damage, widespread attention</option>
                  <option value="Very High">Very High - Severe reputational crisis, major media coverage</option>
                </select>
                <small class="field-hint">Consider impact on brand, customer trust, media coverage, and stakeholder confidence</small>
              </div>

              <!-- Question 5: Operational Impact -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">5</span>
                  What is the operational impact scale of this incident? (Optional)
                </label>
                <select v-model="questionnaireData.operationalImpact" class="question-select">
                  <option value="">Select operational impact level...</option>
                  <option value="Very Low">Very Low - Minimal disruption, normal operations maintained</option>
                  <option value="Low">Low - Minor disruption, limited service impact</option>
                  <option value="Medium">Medium - Moderate disruption, some services affected</option>
                  <option value="High">High - Significant disruption, major service interruption</option>
                  <option value="Very High">Very High - Severe disruption, critical systems down</option>
                </select>
                <small class="field-hint">Consider disruptions to processes, services, productivity, and normal operations</small>
              </div>

              <!-- Question 6: Financial Loss -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">6</span>
                  What is the estimated financial loss from this incident? (Optional)
                </label>
                <div class="input-with-prefix">
                  <span class="currency-prefix">$</span>
                  <input 
                    type="number" 
                    v-model="questionnaireData.financialLoss" 
                    placeholder="Enter total loss amount (e.g., 25000.00) - Include revenue loss, fines, penalties, and recovery costs"
                    class="question-input currency-input"
                    min="0"
                    step="0.01"
                    @input="validateCurrencyInput('financialLoss', $event)"
                  />
                </div>
                <small class="field-hint">Include revenue loss, regulatory fines, penalties, legal costs, and recovery expenses</small>
              </div>

              <!-- Question 7: System Downtime -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">7</span>
                  What is the expected system downtime if this incident occurs again? (Optional)
                </label>
                <div class="input-with-suffix">
                  <input 
                    type="number" 
                    v-model="questionnaireData.systemDowntime" 
                    placeholder="Enter hours (e.g., 8.5) - Total time systems would be unavailable"
                    class="question-input hours-input"
                    min="0"
                    step="0.5"
                    @input="validateHoursInput('systemDowntime', $event)"
                  />
                  <span class="hours-suffix">hours</span>
                </div>
                <small class="field-hint">Estimate total time systems/services would be unavailable (decimals allowed, e.g., 2.5 hours)</small>
              </div>

              <!-- Question 8: Recovery Time -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">8</span>
                  How long did it take to recover from this incident? (Optional)
                </label>
                <div class="input-with-suffix">
                  <input 
                    type="number" 
                    v-model="questionnaireData.recoveryTime" 
                    placeholder="Enter hours (e.g., 12.0) - Time from incident detection to full recovery"
                    class="question-input hours-input"
                    min="0"
                    step="0.5"
                    @input="validateHoursInput('recoveryTime', $event)"
                  />
                  <span class="hours-suffix">hours</span>
                </div>
                <small class="field-hint">Time from incident detection to complete restoration of normal operations (decimals allowed)</small>
              </div>

              <!-- Question 9: Risk Recurrence -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">9</span>
                  Is it possible that this incident will recur again? (Optional)
                </label>
                <select v-model="questionnaireData.riskRecurrence" class="question-select">
                  <option value="">Select likelihood...</option>
                  <option value="yes">Yes - High likelihood of recurrence</option>
                  <option value="maybe">Maybe - Possible but uncertain recurrence</option>
                  <option value="no">No - Very unlikely to recur</option>
                </select>
                <small class="field-hint">Consider if root causes have been addressed and preventive measures are in place</small>
              </div>

              <!-- Question 10: Improvement Initiative -->
              <div class="question-group">
                <label class="question-label">
                  <span class="question-number">10</span>
                  Is this mitigation an improvement initiative that will prevent future recurrence? (Optional)
                </label>
                <select v-model="questionnaireData.improvementInitiative" class="question-select">
                  <option value="">Select prevention level...</option>
                  <option value="yes">Yes - Completely prevents recurrence</option>
                  <option value="partially">Partially - Reduces likelihood of recurrence</option>
                  <option value="no">No - Does not prevent recurrence</option>
                </select>
                <small class="field-hint">Assess whether this mitigation addresses root causes and prevents similar incidents</small>
              </div>
            </div>

            <div class="questionnaire-actions">
              <button @click="showQuestionnaire = false" class="cancel-questionnaire-btn">
                <i class="fas fa-times"></i> Cancel
              </button>
              <button 
                @click="submitIncidentAssessment" 
                class="submit-assessment-btn"
                :disabled="!isQuestionnaireValid"
              >
                <i class="fas fa-check-circle"></i> Submit Assessment
              </button>
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
        
        <h1>Review Incident Mitigations</h1>
        
        <div v-if="loadingMitigations" class="loading">
          <div class="spinner"></div>
          <span>Loading mitigation data...</span>
        </div>
        <div v-else>
          <div class="incident-summary">
            <h3>{{ currentReviewTask?.Title || 'Incident #' + currentReviewTask?.id }}</h3>
            <p><strong>ID:</strong> {{ currentReviewTask?.id }}</p>
            <p><strong>Submitted By:</strong> {{ getUserName(currentReviewTask?.AssignerId) }}</p>
          </div>
          
          <!-- Questionnaire Review Section -->
          <div v-if="questionnaireReviewData" class="questionnaire-review-section">
            <h3>Assessment Questionnaire</h3>
            <div class="questionnaire-review-grid">
              <div class="questionnaire-item" v-if="questionnaireReviewData.cost">
                <label>Cost for Mitigation:</label>
                <p>{{ questionnaireReviewData.cost }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.impact">
                <label>Impact:</label>
                <p>{{ questionnaireReviewData.impact }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.financialImpact">
                <label>Financial Impact:</label>
                <p>{{ questionnaireReviewData.financialImpact }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.reputationalImpact">
                <label>Reputational Impact Scale:</label>
                <p>{{ questionnaireReviewData.reputationalImpact }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.operationalImpact">
                <label>Operational Impact Scale:</label>
                <p>{{ questionnaireReviewData.operationalImpact }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.financialLoss">
                <label>Financial Loss:</label>
                <p>{{ questionnaireReviewData.financialLoss }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.systemDowntime">
                <label>Expected System Downtime (hrs):</label>
                <p>{{ questionnaireReviewData.systemDowntime }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.recoveryTime">
                <label>Recovery Time (hrs):</label>
                <p>{{ questionnaireReviewData.recoveryTime }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.riskRecurrence">
                <label>Risk Recurrence Possibility:</label>
                <p>{{ questionnaireReviewData.riskRecurrence }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.improvementInitiative">
                <label>Improvement Initiative:</label>
                <p>{{ questionnaireReviewData.improvementInitiative }}</p>
              </div>
              
              <div class="questionnaire-item" v-if="questionnaireReviewData.submittedAt">
                <label>Submitted At:</label>
                <p>{{ formatDateTime(questionnaireReviewData.submittedAt) }}</p>
              </div>
            </div>
            
            <!-- Assessment Approval Section -->
            <div v-if="!reviewCompleted" class="assessment-approval-section">
              <h4>Assessment Review</h4>
              <div class="assessment-controls">
                <button 
                  @click="approveAssessment(true)" 
                  class="approve-assessment-btn"
                  :class="{ 'active': assessmentFeedback.approved === true }"
                >
                  <i class="fas fa-check-circle"></i> Approve Assessment
                </button>
                <button 
                  @click="approveAssessment(false)" 
                  class="reject-assessment-btn"
                  :class="{ 'active': assessmentFeedback.approved === false }"
                >
                  <i class="fas fa-times-circle"></i> Reject Assessment
                </button>
              </div>
              
              <!-- Assessment feedback text area for rejection -->
              <div v-if="assessmentFeedback.approved === false" class="assessment-feedback-section">
                <label for="assessment-feedback">Assessment Feedback (required for rejection):</label>
                <textarea 
                  id="assessment-feedback"
                  v-model="assessmentFeedback.remarks" 
                  class="assessment-feedback-input"
                  placeholder="Provide detailed feedback about why the assessment was rejected..."
                  rows="4"
                ></textarea>
              </div>
            </div>
            
            <!-- Show assessment feedback if review is completed -->
            <div v-if="reviewCompleted && assessmentFeedback.approved !== undefined" class="assessment-status-display">
              <h4>Assessment Status</h4>
              <div class="assessment-status" :class="{ 'approved': assessmentFeedback.approved, 'rejected': !assessmentFeedback.approved }">
                <i class="fas" :class="assessmentFeedback.approved ? 'fa-check-circle' : 'fa-times-circle'"></i>
                {{ assessmentFeedback.approved ? 'Assessment Approved' : 'Assessment Rejected' }}
              </div>
              <div v-if="!assessmentFeedback.approved && assessmentFeedback.remarks" class="assessment-feedback-display">
                <strong>Feedback:</strong> {{ assessmentFeedback.remarks }}
              </div>
            </div>
          </div>
          
          <div v-if="reviewCompleted" class="review-status-banner" :class="{ 'approved': reviewApproved, 'rejected': !reviewApproved }">
            <div v-if="reviewApproved" class="status-message">
              <i class="fas fa-check-circle"></i> This incident has been approved
            </div>
            <div v-else class="status-message">
              <i class="fas fa-times-circle"></i> This incident was rejected and is awaiting revision
            </div>
          </div>
          
          <!-- Mitigation review list with split view design -->
          <div class="mitigation-review-list">
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
                  <div class="version-label">Previous Version</div>
                  
                  <div v-if="getPreviousMitigation(id)" class="mitigation-content">
                    <h5>Description</h5>
                    <p>{{ getPreviousMitigation(id).description || 'No description available' }}</p>
                    
                    <!-- Previous comments -->
                    <div v-if="getPreviousMitigation(id).comments" class="comments-section">
                      <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                      <p class="comments-text">{{ getPreviousMitigation(id).comments }}</p>
                    </div>
                    
                    <!-- Previous evidence -->
                    <div v-if="getPreviousMitigation(id)['aws-file_link']" class="evidence-section">
                      <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                      <a :href="getPreviousMitigation(id)['aws-file_link']" download :filename="getPreviousMitigation(id).fileName" class="evidence-link">
                        <i class="fas fa-download"></i> {{ getPreviousMitigation(id).fileName }}
                      </a>
                    </div>
                  </div>
                  
                  <!-- Empty state for no previous version -->
                  <div v-else class="mitigation-empty">
                    <i class="fas fa-history"></i>
                    <p>No previous version available</p>
                  </div>
                </div>
                
                <!-- Current version (right side) -->
                <div class="mitigation-current">
                  <div class="version-label">Current Version</div>
                  
                  <div class="mitigation-content">
                    <h5>Description</h5>
                    <p>{{ mitigation.description }}</p>
                    
                    <!-- Current comments -->
                    <div v-if="mitigation.comments" class="comments-section">
                      <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                      <p class="comments-text">{{ mitigation.comments }}</p>
                    </div>
                    
                    <!-- Current evidence -->
                    <div v-if="mitigation['aws-file_link']" class="evidence-section">
                      <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                      <a :href="mitigation['aws-file_link']" download :filename="mitigation.fileName" class="evidence-link">
                        <i class="fas fa-download"></i> {{ mitigation.fileName }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Approval controls section -->
              <div class="approval-controls">
                <!-- Only show approval buttons if not yet approved or rejected AND not already completed -->
                <div v-if="mitigation.approved !== true && mitigation.approved !== false && !reviewCompleted" class="approval-buttons">
                  <button 
                    @click="approveMitigation(id, true)" 
                    class="approve-btn"
                  >
                    <i class="fas fa-check-double"></i> Approve
                  </button>
                  <button 
                    @click="approveMitigation(id, false)" 
                    class="reject-btn"
                  >
                    <i class="fas fa-ban"></i> Reject
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
                
                <!-- Show read-only status for approved items -->
                <div v-if="mitigation.approved === true" class="approved-readonly">
                  <div class="readonly-notice">
                    <i class="fas fa-lock"></i> This mitigation was previously approved and is read-only
                  </div>
                  <!-- Only allow changing decision if review is not completed -->
                  <div v-if="!reviewCompleted" class="approved-actions">
                    <button @click="approveMitigation(id, false)" class="change-decision-btn">
                      <i class="fas fa-exchange-alt"></i> Change to Reject
                    </button>
                  </div>
                </div>
                
                <!-- Show remarks if already rejected and submitted -->
                <div v-if="mitigation.approved === false && reviewCompleted && mitigation.remarks" class="reviewer-remarks-display">
                  <h5><i class="fas fa-comment-exclamation"></i> Rejection Feedback</h5>
                  <p>{{ mitigation.remarks }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="review-actions">
            <button 
              class="submit-review-btn" 
              :disabled="!canSubmitReview || reviewCompleted" 
              @click="submitReview(true)"
            >
              <i class="fas fa-check-double"></i> Approve Incident
            </button>
            <button 
              class="reject-review-btn" 
              :disabled="!canSubmitReview || reviewCompleted" 
              @click="submitReview(false)"
            >
              <i class="fas fa-ban"></i> Reject Incident
            </button>
            
            <div v-if="reviewCompleted" class="review-complete-notice">
              This review has been completed
            </div>
            
            <div v-else-if="!canSubmitReview" class="review-warning">
              <i class="fas fa-exclamation-circle"></i>
              You must approve or reject each mitigation and the assessment before submitting
            </div>
          </div>
        </div>
      </div>
      
      <!-- Popup Modal -->
      <PopupModal />
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { PopupService, PopupModal } from '@/modules/popup';
  import CustomDropdown from '@/components/CustomDropdown.vue';
  import CollapsibleTable from '@/components/CollapsibleTable.vue';
  import './IncidentUserTask.css'; // Import the CSS file
  
  export default {
    name: 'IncidentUserTasks',
    components: {
      PopupModal,
      CustomDropdown,
      CollapsibleTable
    },
    data() {
      return {
        userIncidents: [],
        reviewerTasks: [],
        users: [],
        selectedUserId: '',
        selectedStatus: '',
        loading: true,
        error: null,
        showMitigationWorkflow: false,
        showReviewerWorkflow: false,
        loadingMitigations: false,
        mitigationSteps: [],
        selectedIncidentId: null,
        activeTab: 'user',
        mitigationReviewData: {},
        currentReviewTask: null,
        reviewCompleted: false,
        reviewApproved: false,
        previousVersions: {},
        showQuestionnaire: false,
        questionnaireReviewData: {},
        assessmentFeedback: {},
        assessmentFeedbackForUser: null,
        questionnaireData: {
          cost: '',
          impact: '',
          financialImpact: '',
          reputationalImpact: '',
          operationalImpact: '',
          financialLoss: '',
          systemDowntime: '',
          recoveryTime: '',
          riskRecurrence: '',
          improvementInitiative: ''
        },
        // Dropdown configurations
        userDropdownConfig: {
          label: 'User',
          values: [],
          defaultValue: 'All Users'
        },
        statusDropdownConfig: {
          label: 'Status',
          values: [
            { value: '', label: 'All Statuses' },
            { value: 'Assigned', label: 'Assigned' },
            { value: 'In Progress', label: 'In Progress' },
            { value: 'Under Review', label: 'Under Review' },
            { value: 'Pending Review', label: 'Pending Review' },
            { value: 'Rejected', label: 'Rejected' },
            { value: 'Approved', label: 'Approved' }
          ],
          defaultValue: 'All Statuses'
        },
        // Collapsible table configurations
        expandedSections: {},
        tableHeaders: [
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'title', label: 'Title', width: '200px' },
          { key: 'origin', label: 'Origin', width: '120px' },
          { key: 'priority', label: 'Priority', width: '100px' },
          { key: 'dueDate', label: 'Due Date', width: '120px' },
          { key: 'actions', label: 'Actions', width: '120px', className: 'actions-column' }
        ],
        reviewerTableHeaders: [
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'title', label: 'Title', width: '200px' },
          { key: 'origin', label: 'Origin', width: '120px' },
          { key: 'priority', label: 'Priority', width: '100px' },
          { key: 'assignedBy', label: 'Assigned By', width: '120px' },
          { key: 'actions', label: 'Actions', width: '120px', className: 'actions-column' }
        ]
      }
    },
    computed: {
      allStepsCompleted() {
        // Only check rejected or unreviewed steps, ignore approved ones
        const stepsToCheck = this.mitigationSteps.filter(step => step.approved === false || step.approved === null);
        return stepsToCheck.length > 0 && 
               stepsToCheck.every(step => step.status === 'Completed');
      },
      canSubmitReview() {
        const mitigationsValid = Object.values(this.mitigationReviewData).every(m => 
          m.approved === true || (m.approved === false && m.remarks && m.remarks.trim() !== '')
        );
        
        const assessmentValid = this.assessmentFeedback.approved !== undefined && 
          (this.assessmentFeedback.approved === true || 
           (this.assessmentFeedback.approved === false && this.assessmentFeedback.remarks && this.assessmentFeedback.remarks.trim() !== ''));
        
        return mitigationsValid && assessmentValid;
      },
      hasRejectedOrNewSteps() {
        return this.mitigationSteps.some(step => step.approved === false || step.approved === null);
      },
      rejectedStepsCompleted() {
        const rejectedOrNewSteps = this.mitigationSteps.filter(step => step.approved === false || step.approved === null);
        return rejectedOrNewSteps.length > 0 && 
               rejectedOrNewSteps.every(step => step.status === 'Completed');
      },
      isQuestionnaireValid() {
        // All fields are optional, so always return true
        return true;
      },
      isAuditFinding() {
        const task = this.userIncidents.find(t => t.id === this.selectedIncidentId);
        return task && task.itemType === 'audit_finding';
      },
      isIncidentRejected() {
        const task = this.userIncidents.find(t => t.id === this.selectedIncidentId);
        return task && task.Status === 'Rejected';
      },
      currentIncidentDetails() {
        return this.userIncidents.find(t => t.id === this.selectedIncidentId) || {};
      },
      // Filtered incidents based on selected status
      filteredUserIncidents() {
        if (!this.selectedStatus) {
          return this.userIncidents;
        }
        return this.userIncidents.filter(incident => incident.Status === this.selectedStatus);
      },
      // Collapsible table sections for user incidents
      userIncidentSections() {
        const sections = {};
        
        // Group incidents by status
        const groupedIncidents = {};
        this.filteredUserIncidents.forEach(incident => {
          const status = incident.Status || 'Not Assigned';
          if (!groupedIncidents[status]) {
            groupedIncidents[status] = [];
          }
          groupedIncidents[status].push(incident);
        });

        // Convert each status group to CollapsibleTable format
        Object.keys(groupedIncidents).forEach(status => {
          const statusConfig = this.getStatusConfig(status);
          sections[status] = {
            name: status,
            statusClass: statusConfig.statusClass,
            tasks: groupedIncidents[status].map(incident => {
              return {
                incidentId: incident.id,
                id: incident.id,
                title: incident.Title,
                origin: incident.Origin || 'MANUAL',
                priority: `<span class="priority-badge ${(incident.Priority || 'unknown').toLowerCase()}">${incident.Priority || 'Unknown'}</span>`,
                dueDate: this.formatDate(incident.MitigationDueDate),
                actions: incident.id // Pass the ID for the View Details button
              };
            })
          };
        });

        return sections;
      },
      // Collapsible table sections for reviewer tasks
      reviewerTaskSections() {
        const sections = {};
        
        // Group reviewer tasks by status
        const groupedTasks = {};
        this.reviewerTasks.forEach(task => {
          const status = task.Status || 'Unknown';
          if (!groupedTasks[status]) {
            groupedTasks[status] = [];
          }
          groupedTasks[status].push(task);
        });

        // Convert each status group to CollapsibleTable format
        Object.keys(groupedTasks).forEach(status => {
          const statusConfig = this.getStatusConfig(status);
          sections[status] = {
            name: status,
            statusClass: statusConfig.statusClass,
            tasks: groupedTasks[status].map(task => {
              return {
                incidentId: task.id,
                id: task.id,
                title: task.Title,
                origin: task.Origin || 'MANUAL',
                priority: `<span class="priority-badge ${(task.Priority || 'unknown').toLowerCase()}">${task.Priority || 'Unknown'}</span>`,
                assignedBy: this.getUserName(task.AssignerId),
                actions: task.id // Pass the ID for the Review button
              };
            })
          };
        });

        return sections;
      }
    },
          mounted() {
        this.fetchUsers();
        this.initializeFromQuery();
      },
    methods: {
      fetchUsers() {
        axios.get('http://localhost:8000/api/custom-users/')
          .then(response => {
            console.log('User data received:', response.data);
            this.users = response.data;
            
            // Populate user dropdown configuration
            this.userDropdownConfig.values = [
              { value: '', label: 'All Users' },
              ...this.users.map(user => ({
                value: user.UserId,
                label: `${user.UserName} (${user.role})`
              }))
            ];
            
            this.loading = false;
          })
          .catch(error => {
            console.error('Error fetching users:', error);
            this.error = `Failed to fetch users: ${error.message}`;
            this.loading = false;
          });
      },
      switchToReviewerTab() {
        console.log('Switching to reviewer tab');
        this.activeTab = 'reviewer';
        if (this.selectedUserId) {
          console.log('Refreshing data for reviewer tab');
          this.fetchData();
        }
      },
      fetchData() {
        if (!this.selectedUserId) {
          this.userIncidents = [];
          this.reviewerTasks = [];
          return;
        }
        
        this.loading = true;
        
        // Fetch both incidents and audit findings for the user
        Promise.all([
          axios.get(`http://localhost:8000/api/user-incidents/${this.selectedUserId}/`),
          axios.get(`http://localhost:8000/api/user-audit-findings/${this.selectedUserId}/`),
          axios.get(`http://localhost:8000/api/incident-reviewer-tasks/${this.selectedUserId}/`),
          axios.get(`http://localhost:8000/api/audit-finding-reviewer-tasks/${this.selectedUserId}/`)
        ])
        .then(([incidentsResponse, auditFindingsResponse, incidentReviewerResponse, auditReviewerResponse]) => {
          // Combine incidents and audit findings
          const incidents = incidentsResponse.data || [];
          const auditFindings = auditFindingsResponse.data || [];
          
          // Mark each item with its type for easier identification
          const markedIncidents = incidents.map(item => ({ ...item, itemType: 'incident' }));
          const markedAuditFindings = auditFindings.map(item => ({ ...item, itemType: 'audit_finding' }));
          
          // Combine and deduplicate by ID
          const combinedUserTasks = [...markedIncidents, ...markedAuditFindings];
          const uniqueUserTasks = combinedUserTasks.filter((task, index, array) => 
            index === array.findIndex(t => t.id === task.id)
          );
          this.userIncidents = uniqueUserTasks;
          
          // Combine reviewer tasks
          const incidentReviewerTasks = incidentReviewerResponse.data || [];
          const auditReviewerTasks = auditReviewerResponse.data || [];
          
          const markedIncidentReviewerTasks = incidentReviewerTasks.map(item => ({ ...item, itemType: 'incident' }));
          const markedAuditReviewerTasks = auditReviewerTasks.map(item => ({ ...item, itemType: 'audit_finding' }));
          
          // Combine and deduplicate reviewer tasks by ID
          const combinedReviewerTasks = [...markedIncidentReviewerTasks, ...markedAuditReviewerTasks];
          const uniqueReviewerTasks = combinedReviewerTasks.filter((task, index, array) => 
            index === array.findIndex(t => t.id === task.id)
          );
          this.reviewerTasks = uniqueReviewerTasks;
          
          console.log('Combined user tasks:', this.userIncidents);
          console.log('Combined reviewer tasks:', this.reviewerTasks);
          console.log('Debug - Incident reviewer tasks:', incidentReviewerTasks);
          console.log('Debug - Audit reviewer tasks:', auditReviewerTasks);
          console.log('Debug - Final reviewerTasks length:', this.reviewerTasks.length);
          
          this.loading = false;
          this.error = null;
        })
        .catch(error => {
          console.error('Error fetching data:', error);
          this.error = `Failed to fetch data: ${error.message}`;
          this.loading = false;
        });
      },
      getUserName(userId) {
        const user = this.users.find(u => u.UserId == userId);
        return user ? user.UserName : 'Unknown';
      },
      viewMitigations(incidentId) {
        // Find the task to determine if it's an audit finding or incident
        const task = this.userIncidents.find(t => t.id === incidentId);
        const isAuditFinding = task && task.itemType === 'audit_finding';
        
        this.selectedIncidentId = incidentId;
        this.loadingMitigations = true;
        this.showMitigationWorkflow = true;
        this.assessmentFeedbackForUser = null;
        
        // Use appropriate endpoints based on task type
        const mitigationsEndpoint = isAuditFinding
          ? `http://localhost:8000/api/audit-finding-mitigations/${incidentId}/`
          : `http://localhost:8000/api/incident-mitigations/${incidentId}/`;
          
        const reviewEndpoint = isAuditFinding
          ? `http://localhost:8000/api/audit-finding-review-data/${incidentId}/`
          : `http://localhost:8000/api/incident-review-data/${incidentId}/`;
        
        // Get the mitigation steps and assessment feedback
        Promise.all([
          axios.get(mitigationsEndpoint),
          axios.get(reviewEndpoint)
        ])
        .then(([mitigationsResponse, reviewResponse]) => {
          console.log(`${isAuditFinding ? 'Audit finding' : 'Incident'} mitigations received:`, mitigationsResponse.data);
          console.log(`${isAuditFinding ? 'Audit finding' : 'Incident'} review data received:`, reviewResponse.data);
          
          // Debug the raw mitigation data
          if (mitigationsResponse.data && mitigationsResponse.data.mitigations) {
            console.log('DEBUG: Raw mitigations from backend:', mitigationsResponse.data.mitigations);
            Object.keys(mitigationsResponse.data.mitigations).forEach(key => {
              const mitigation = mitigationsResponse.data.mitigations[key];
              console.log(`DEBUG: Mitigation ${key} raw data:`, mitigation);
            });
          }
          
          this.mitigationSteps = this.parseMitigations(mitigationsResponse.data);
          
          // Check for assessment feedback from reviewer
          if (reviewResponse.data && reviewResponse.data.assessment_feedback) {
            this.assessmentFeedbackForUser = reviewResponse.data.assessment_feedback;
          }
          
          // Pre-fill questionnaire data if previous data exists
          if (mitigationsResponse.data.previous_assessment_data && 
              Object.keys(mitigationsResponse.data.previous_assessment_data).length > 0) {
            this.questionnaireData = {
              ...this.questionnaireData,
              ...mitigationsResponse.data.previous_assessment_data
            };
          }
          
          this.loadingMitigations = false;
        })
        .catch(error => {
          console.error(`Error fetching ${isAuditFinding ? 'audit finding' : 'incident'} data:`, error);
          this.mitigationSteps = [];
          this.assessmentFeedbackForUser = null;
          this.loadingMitigations = false;
        });
      },
      parseMitigations(response) {
        // Handle the new enhanced response format
        if (response && response.mitigations) {
          const mitigations = response.mitigations;
          const keys = Object.keys(mitigations);
          const steps = [];
          
          // Sort keys numerically
          keys.sort((a, b) => Number(a) - Number(b));
          
          for (const key of keys) {
            const mitigation = mitigations[key];
            
            // Handle both old and new format
            let description, approved, remarks, status;
            if (typeof mitigation === 'string') {
              // Old format - just a string description
              description = mitigation;
              approved = null;
              remarks = null;
              status = 'Not Started';
            } else {
              // New format - object with feedback
              description = mitigation.description || mitigation;
              approved = mitigation.approved;
              remarks = mitigation.remarks;
              status = mitigation.status || 'Not Started';
            }
            
            console.log(`DEBUG: Parsing mitigation ${key} - approved: ${approved}, remarks: ${remarks}, description: ${description}`);
            
            steps.push({
              title: `Step ${key}`,
              description: description,
              status: status,
              approved: approved,
              remarks: remarks,
              previousComments: mitigation.comments || '',
              comments: '', // Start with empty for new comments
              'aws-file_link': mitigation['aws-file_link'] || null,
              fileName: mitigation.fileName || null
            });
          }
          return steps;
        }
        
        // Handle legacy format or direct mitigation data
        const data = response.mitigations || response;
        
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
                status: 'Not Started',
                approved: null,
                remarks: null,
                comments: '',
                'aws-file_link': null,
                fileName: null
              });
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
            if (parsedData && typeof parsedData === 'object' && !Array.isArray(parsedData)) {
              return this.parseMitigations({ mitigations: parsedData });
            }
            return Array.isArray(parsedData) ? parsedData : [parsedData];
          } catch (e) {
            console.error('Error parsing mitigation JSON:', e);
            return [{ title: 'Mitigation', description: data, approved: null, remarks: null }];
          }
        }
        
        // Default fallback
        return [{ title: 'Mitigation', description: 'No detailed mitigation steps available', approved: null, remarks: null }];
      },
      closeMitigationModal() {
        this.showMitigationWorkflow = false;
        this.mitigationSteps = [];
        this.selectedIncidentId = null;
        this.showQuestionnaire = false;
        
        // Reset questionnaire data
        this.questionnaireData = {
          cost: '',
          impact: '',
          financialImpact: '',
          reputationalImpact: '',
          operationalImpact: '',
          financialLoss: '',
          systemDowntime: '',
          recoveryTime: '',
          riskRecurrence: '',
          improvementInitiative: ''
        };
      },
      updateStepStatus(index, status) {
        console.log(`Updating step ${index + 1} status to ${status}`);
        
        // Prevent editing of approved steps
        if (this.mitigationSteps[index].approved === true) {
          PopupService.warning('This mitigation step has been approved by the reviewer and cannot be modified.');
          return;
        }
        
        // Only allow updates to rejected or unreviewed steps
        if (this.mitigationSteps[index].approved === false || this.mitigationSteps[index].approved === null) {
          this.mitigationSteps[index].status = status;
        }
      },
      submitIncidentAssessment() {
        // Find the task to determine if it's an audit finding or incident
        const task = this.userIncidents.find(t => t.id === this.selectedIncidentId);
        const isAuditFinding = task && task.itemType === 'audit_finding';
        
        this.loading = true;
        
        // Prepare the mitigation data
        const mitigationData = {};
        this.mitigationSteps.forEach((step, index) => {
          const stepNumber = (index + 1).toString();
          
          // Combine previous comments with new comments
          let combinedComments = '';
          const hasPreviousComments = step.previousComments && step.previousComments.trim();
          const hasNewComments = step.comments && step.comments.trim();
          
          if (hasPreviousComments && hasNewComments) {
            combinedComments = `Previous: ${step.previousComments.trim()}\n\nNew: ${step.comments.trim()}`;
          } else if (hasPreviousComments) {
            combinedComments = step.previousComments.trim();
          } else if (hasNewComments) {
            combinedComments = step.comments.trim();
          }
          
          mitigationData[stepNumber] = {
            description: step.description,
            status: step.status || 'Completed',
            comments: combinedComments,
            "aws-file_link": step['aws-file_link'],
            fileName: step.fileName,
            approved: step.approved, // Include approval status
            remarks: step.remarks    // Include reviewer remarks
          };
        });
        
        // Prepare questionnaire data for assessment
        const extractedInfo = {
          cost: this.questionnaireData.cost || '',
          impact: this.questionnaireData.impact || '',
          financialImpact: this.questionnaireData.financialImpact || '',
          reputationalImpact: this.questionnaireData.reputationalImpact || '',
          operationalImpact: this.questionnaireData.operationalImpact || '',
          financialLoss: this.questionnaireData.financialLoss || '',
          systemDowntime: this.questionnaireData.systemDowntime || '',
          recoveryTime: this.questionnaireData.recoveryTime || '',
          riskRecurrence: this.questionnaireData.riskRecurrence || '',
          improvementInitiative: this.questionnaireData.improvementInitiative || '',
          mitigations: mitigationData,
          submittedAt: new Date().toISOString()
        };
        
        // Use appropriate endpoint based on task type
        const submitEndpoint = isAuditFinding
          ? 'http://localhost:8000/api/submit-audit-finding-assessment/'
          : 'http://localhost:8000/api/submit-incident-assessment/';
        
        axios.post(submitEndpoint, {
          incident_id: this.selectedIncidentId,
          user_id: this.selectedUserId,
          extracted_info: extractedInfo
        })
        .then(response => {
          console.log(`${isAuditFinding ? 'Audit finding' : 'Incident'} assessment submitted:`, response.data);
          this.loading = false;
          this.closeMitigationModal();
          PopupService.success(`${isAuditFinding ? 'Audit finding' : 'Incident'} assessment submitted for review successfully!`);
          
          // Refresh the tasks list
          this.fetchData();
        })
        .catch(error => {
          console.error(`Error submitting ${isAuditFinding ? 'audit finding' : 'incident'} assessment:`, error);
          this.loading = false;
          PopupService.error('Failed to submit assessment. Please try again.');
        });
      },
      closeReviewerModal() {
        this.showReviewerWorkflow = false;
        this.currentReviewTask = null;
        this.mitigationReviewData = {};
        this.previousVersions = {};
        this.reviewCompleted = false;
        this.reviewApproved = false;
      },
      approveMitigation(id, approved) {
        const updatedMitigation = {
          ...this.mitigationReviewData[id],
          approved: approved,
          reviewer_submitted_date: new Date().toISOString()
        };
        
        if (approved) {
          updatedMitigation.remarks = '';
        }
        
        this.mitigationReviewData = {
          ...this.mitigationReviewData,
          [id]: updatedMitigation
        };
      },
      approveAssessment(approved) {
        this.assessmentFeedback = {
          approved: approved,
          remarks: approved ? '' : this.assessmentFeedback.remarks || ''
        };
        
        console.log('Assessment feedback updated:', this.assessmentFeedback);
      },
      submitReview(approved) {
        if (!this.canSubmitReview) {
          PopupService.warning('Please complete the review of all mitigations');
          return;
        }
        
        const isAuditFinding = this.currentReviewTask && this.currentReviewTask.itemType === 'audit_finding';
        this.loading = true;
        
        // Prepare mitigation feedback for backend
        const mitigationFeedback = {};
        Object.keys(this.mitigationReviewData).forEach(id => {
          const mitigation = this.mitigationReviewData[id];
          mitigationFeedback[id] = {
            approved: mitigation.approved,
            remarks: mitigation.remarks || null
          };
        });
        
        const reviewData = {
          incident_id: this.currentReviewTask.id,
          approved: approved,
          reviewer_id: this.selectedUserId, // This is the reviewer performing the review
          mitigation_feedback: mitigationFeedback,
          assessment_feedback: this.assessmentFeedback
        };
        
        // For audit findings, add overall_decision parameter
        if (isAuditFinding) {
          reviewData.overall_decision = approved ? 'approved' : 'rejected';
        }
        
        console.log(`Submitting ${isAuditFinding ? 'audit finding' : 'incident'} review with mitigation feedback:`, reviewData);
        
        // Use appropriate endpoint based on task type
        const reviewEndpoint = isAuditFinding
          ? 'http://localhost:8000/api/complete-audit-finding-review/'
          : 'http://localhost:8000/api/complete-incident-review/';
        
        axios.post(reviewEndpoint, reviewData)
          .then(response => {
            console.log(`${isAuditFinding ? 'Audit finding' : 'Incident'} review completed:`, response.data);
            this.loading = false;
            
            // Remove this task from the list
            const index = this.reviewerTasks.findIndex(t => t.id === this.currentReviewTask.id);
            if (index !== -1) {
              this.reviewerTasks.splice(index, 1);
            }
            
            this.reviewCompleted = true;
            this.reviewApproved = approved;
            
            PopupService.success(`${isAuditFinding ? 'Audit finding' : 'Incident'} ${approved ? 'approved' : 'rejected'} successfully!`);
            
            setTimeout(() => {
              this.closeReviewerModal();
            }, 2500);
          })
          .catch(error => {
            console.error(`Error completing ${isAuditFinding ? 'audit finding' : 'incident'} review:`, error);
            this.loading = false;
            PopupService.error('Failed to submit review. Please try again.');
          });
      },
      updateRemarks(id) {
        if (!this.mitigationReviewData[id].remarks.trim()) {
                      PopupService.warning('Please provide remarks for rejection');
          return;
        }
        
        this.mitigationReviewData = {
          ...this.mitigationReviewData
        };
        
        console.log(`Mitigation ${id} remarks updated successfully`);
      },
      handleFileUpload(event, index) {
        const file = event.target.files[0];
        if (!file) return;
        
        if (file.size > 5 * 1024 * 1024) {
          PopupService.error('File size exceeds 5MB limit');
          event.target.value = '';
          return;
        }
        
        // Show loading indicator
        this.mitigationSteps[index].uploading = true;
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('incidentId', this.selectedIncidentId);
        formData.append('mitigationNumber', index + 1);
        
        axios.post('http://localhost:8000/api/upload-file/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        .then(response => {
          console.log('File processed successfully:', response.data);
          
          if (response.data.success) {
            this.mitigationSteps[index]['aws-file_link'] = response.data.file_url;
            this.mitigationSteps[index].fileName = file.name;
            
            PopupService.success('File uploaded successfully');
          } else {
            PopupService.error('Error uploading file: ' + response.data.error);
          }
        })
        .catch(error => {
          console.error('Error processing file:', error);
          if (error.response && error.response.data && error.response.data.error) {
            PopupService.error('Error uploading file: ' + error.response.data.error);
          } else {
            PopupService.error('Error uploading file. Please try again.');
          }
        })
        .finally(() => {
          this.mitigationSteps[index].uploading = false;
        });
      },
      reviewMitigations(task) {
        const isAuditFinding = task && task.itemType === 'audit_finding';
        console.log(`Starting reviewMitigations with ${isAuditFinding ? 'audit finding' : 'incident'} task:`, task);
        
        this.currentReviewTask = task;
        this.selectedIncidentId = task.id;
        this.loadingMitigations = true;
        this.showReviewerWorkflow = true;
        this.previousVersions = {};
        this.assessmentFeedback = {};
        
        // Use appropriate endpoint based on task type
        const reviewEndpoint = isAuditFinding
          ? `http://localhost:8000/api/audit-finding-review-data/${task.id}/`
          : `http://localhost:8000/api/incident-review-data/${task.id}/`;
        
        // Get review data (includes questionnaire, previous versions, and assessment feedback)
        axios.get(reviewEndpoint)
          .then(response => {
            console.log(`${isAuditFinding ? 'Audit finding' : 'Incident'} review data:`, response.data);
            
            if (response.data) {
              this.mitigationReviewData = response.data.mitigations || {};
              this.questionnaireReviewData = response.data.questionnaire_data || {};
              this.previousVersions = response.data.previous_versions || {};
              
              // Load existing assessment feedback if review is completed
              if (response.data.assessment_feedback) {
                this.assessmentFeedback = response.data.assessment_feedback;
              }
              
              const isCompleted = response.data.approval_entry?.review_completed;
              this.reviewCompleted = isCompleted;
              this.reviewApproved = response.data.approval_entry?.approved_rejected === 'Approved';
              
              this.loadingMitigations = false;
            } else {
              this.mitigationReviewData = {};
              this.questionnaireReviewData = {};
              this.previousVersions = {};
              this.assessmentFeedback = {};
              this.loadingMitigations = false;
            }
          })
          .catch(error => {
            console.error(`Error fetching ${isAuditFinding ? 'audit finding' : 'incident'} review data:`, error);
            this.mitigationReviewData = {};
            this.questionnaireReviewData = {};
            this.previousVersions = {};
            this.assessmentFeedback = {};
            this.loadingMitigations = false;
          });
      },
      formatDateTime(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
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
        
        dueDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        
        const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft < 0) return 'overdue';
        if (daysLeft <= 3) return 'urgent';
        if (daysLeft <= 7) return 'warning';
        return 'on-track';
      },
      getDueStatusText(dateString) {
        if (!dateString) return '';
        
        const dueDate = new Date(dateString);
        const today = new Date();
        
        dueDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        
        const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft < 0) return `(Delayed by ${Math.abs(daysLeft)} days)`;
        if (daysLeft === 0) return '(Due today)';
        if (daysLeft === 1) return '(Due tomorrow)';
        return `(${daysLeft} days left)`;
      },
      getPreviousMitigation(id) {
        if (!this.previousVersions || typeof this.previousVersions !== 'object') {
          return null;
        }
        
        if (!this.previousVersions[id]) {
          return null;
        }
        
        return this.previousVersions[id];
      },
      isStepActive(index) {
        const step = this.mitigationSteps[index];
        return step.approved === false || step.approved === null;
      },
      
      isStepLocked(index) {
        const step = this.mitigationSteps[index];
        return step.approved === true;
      },
      isOverdue(dateString) {
        if (!dateString) return false;
        const dueDate = new Date(dateString);
        const today = new Date();
        dueDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        return dueDate < today;
      },
      initializeFromQuery() {
        // Initialize from query parameters if provided
        const query = this.$route.query;
        if (query.userId) {
          this.selectedUserId = query.userId;
        }
        if (query.taskId) {
          this.viewMitigations(query.taskId);
        }
        if (query.mode === 'reviewer' && query.taskId) {
          // Switch to reviewer tab and open reviewer workflow
          this.activeTab = 'reviewer';
          this.$nextTick(() => {
            const task = { id: query.taskId };
            this.reviewMitigations(task);
          });
        }
      },
      
      // Client-side validation methods for questionnaire
      validateCurrencyInput(fieldName, event) {
        const value = event.target.value;
        
        // Allow empty values (optional fields)
        if (!value || value === '') return;
        
        // Remove any non-numeric characters except decimal point
        const numericValue = value.replace(/[^0-9.]/g, '');
        
        // Validate format
        const currencyPattern = /^[0-9]+(\.[0-9]{0,2})?$/;
        if (!currencyPattern.test(numericValue)) {
          event.target.setCustomValidity('Please enter a valid amount (e.g., 1000.50)');
        } else {
          const amount = parseFloat(numericValue);
          if (amount < 0) {
            event.target.setCustomValidity('Amount cannot be negative');
          } else if (amount > 999999999.99) {
            event.target.setCustomValidity('Amount exceeds maximum allowed value');
          } else {
            event.target.setCustomValidity('');
          }
        }
        
        // Update the model with cleaned value
        this.questionnaireData[fieldName] = numericValue;
      },
      
      validateHoursInput(fieldName, event) {
        const value = event.target.value;
        
        // Allow empty values (optional fields)
        if (!value || value === '') return;
        
        // Validate format
        const hoursPattern = /^[0-9]+(\.[0-9]{0,2})?$/;
        if (!hoursPattern.test(value)) {
          event.target.setCustomValidity('Please enter a valid number of hours (e.g., 8.5)');
        } else {
          const hours = parseFloat(value);
          if (hours < 0) {
            event.target.setCustomValidity('Hours cannot be negative');
          } else if (hours > 8760) {
            event.target.setCustomValidity('Hours exceeds reasonable maximum (8760 = 1 year)');
          } else {
            event.target.setCustomValidity('');
          }
        }
      },
      // Get status configuration for styling
      getStatusConfig(status) {
        switch (status) {
          case 'Assigned':
          case 'Open':
            return { statusClass: 'pending' };
          case 'In Progress':
          case 'Under Review':
          case 'Pending Review':
            return { statusClass: 'in-progress' };
          case 'Approved':
          case 'Completed':
          case 'Closed':
            return { statusClass: 'completed' };
          case 'Rejected':
            return { statusClass: 'rejected' };
          default:
            return { statusClass: 'pending' };
        }
      },
      // Handle user dropdown change
      onUserChange(option) {
        this.selectedUserId = option.value;
        this.fetchData();
      },
      // Handle status dropdown change
      onStatusChange(option) {
        this.selectedStatus = option.value;
      },
      // Toggle section expansion
      toggleSection(status) {
        this.expandedSections[status] = !this.expandedSections[status];
      },
      // Handle add task (not used in this context but required by CollapsibleTable)
      handleAddTask(status) {
        console.log('Add task for status:', status);
      },
      // Handle task click (view details)
      handleTaskClick(taskId) {
        if (this.activeTab === 'user') {
          this.viewMitigations(taskId);
        } else {
          const task = this.reviewerTasks.find(t => t.id === taskId);
          if (task) {
            this.reviewMitigations(task);
          }
        }
      },
    }
  }
  </script>
  
  <style scoped>
  @import './IncidentUserTask.css';
  </style> 