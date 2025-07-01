<template>
    <div class="upload-framework-container">
      <!-- Step Indicator -->
      <div class="step-indicator">
        <div class="step-item" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
          <div class="step-number">1</div>
          <div class="step-label">Upload Document</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
          <div class="step-number">2</div>
          <div class="step-label">Processing</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 3, completed: currentStep > 3 }">
          <div class="step-number">3</div>
          <div class="step-label">Content Selection</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 4, completed: currentStep > 4 }">
          <div class="step-number">4</div>
          <div class="step-label">Policy Extraction</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 5, completed: currentStep > 5 }">
          <div class="step-number">5</div>
          <div class="step-label">Review Policies</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 6, completed: currentStep > 6 }">
          <div class="step-number">6</div>
          <div class="step-label">Edit Policy Details</div>
        </div>
      </div>
  
      <!-- Back Button (shown when not on first step) -->
      <div v-if="currentStep > 1 && !isProcessing" class="back-button-container">
        <button @click="goBack" class="back-btn">
          <i class="fas fa-arrow-left"></i>
          Back
        </button>
      </div>
  
      <div class="header">
        <h1>Upload Framework</h1>
        <p>Upload framework documents to the system</p>
      </div>
  
      <div class="upload-section">
        <!-- Step 1: Upload Area -->
        <div v-if="currentStep === 1" class="upload-area" :class="{ 'drag-over': isDragOver }" 
             @drop="handleDrop" 
             @dragover.prevent="isDragOver = true" 
             @dragleave="isDragOver = false"
             @click="triggerFileInput">
          <div class="upload-content">
            <div class="upload-icon-container">
              <i class="fas fa-cloud-upload-alt upload-icon"></i>
            </div>
            <h3>Drag & Drop your framework file here</h3>
            <p>or click to browse files</p>
            <div class="supported-formats">
              <small>Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX</small>
            </div>
          </div>
          <input 
            ref="fileInput" 
            type="file" 
            @change="handleFileSelect" 
            accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
            style="display: none"
          />
        </div>
  
        <!-- OR Divider -->
        <div v-if="currentStep === 1" class="or-divider">
          <div class="divider-line"></div>
          <span class="divider-text">OR</span>
          <div class="divider-line"></div>
        </div>
  
        <!-- Load Default Data Section -->
        <div v-if="currentStep === 1" class="default-data-section">
          <div class="default-data-content">
            <div class="default-icon-container">
              <i class="fas fa-database default-icon"></i>
            </div>
            <h3>Load Default Framework Data</h3>
            <p>Use pre-loaded NIST framework data for quick testing</p>
            <button 
              @click="loadDefaultData" 
              :disabled="isLoadingDefault"
              class="load-default-btn"
            >
              <i class="fas fa-download"></i>
              {{ isLoadingDefault ? 'Loading Default Data...' : 'Load Default Data' }}
            </button>
          </div>
        </div>
  
        <!-- File Preview (Step 1) -->
        <div v-if="selectedFile && currentStep === 1" class="file-preview">
          <div class="file-info">
            <div class="file-icon-container">
              <i class="fas fa-file file-icon"></i>
            </div>
            <div class="file-details">
              <h4>{{ selectedFile.name }}</h4>
              <p>{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button @click="removeFile" class="remove-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="upload-actions">
            <button 
              @click="uploadFile" 
              :disabled="!selectedFile || isUploading"
              class="upload-btn"
            >
              <i class="fas fa-upload"></i>
              {{ isUploading ? 'Uploading...' : 'Upload Framework' }}
            </button>
          </div>
        </div>
  
        <!-- Step 2: Processing Progress Section -->
        <div v-if="currentStep === 2" class="processing-section">
          <div class="processing-header">
            <div class="processing-icon-container">
              <i class="fas fa-cog fa-spin processing-icon"></i>
            </div>
            <h3>Processing Framework Document</h3>
            <p>{{ processingStatus.message || 'Extracting document sections...' }}</p>
          </div>
          
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: processingStatus.progress + '%' }"></div>
            </div>
            <div class="progress-text">{{ processingStatus.progress || 0 }}%</div>
          </div>
          
          <div class="processing-details">
            <div class="detail-item">
              <i class="fas fa-file-pdf"></i>
              <span>File: {{ uploadedFileName }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Started: {{ processingStartTime }}</span>
            </div>
          </div>
        </div>
  
        <!-- Step 3: Content Selection Complete -->
        <div v-if="currentStep === 3" class="completion-section">
          <div class="completion-icon-container">
            <div class="success-circle">
              <i class="fas fa-check"></i>
            </div>
          </div>
          
          <div class="completion-header">
            <h3>Processing Complete!</h3>
            <p>Your framework document has been successfully processed and extracted.</p>
          </div>
          
          <div class="completion-actions">
            <button @click="viewExtractedContent" class="view-content-btn">
              <i class="fas fa-eye"></i>
              View Extracted Content
            </button>
          </div>
        </div>
  
        <!-- Step 4: Policy Extraction Progress -->
        <div v-if="currentStep === 4" class="extraction-section">
          <div class="extraction-header">
            <div class="extraction-icon-container">
              <i class="fas fa-brain fa-spin extraction-icon"></i>
            </div>
            <h3>Extracting Policy Information</h3>
            <p>{{ policyExtractionMessage }}</p>
          </div>
          
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: policyExtractionProgress + '%' }"></div>
            </div>
            <div class="progress-text">{{ policyExtractionProgress || 0 }}%</div>
          </div>
          
          <div class="extraction-details">
            <div class="detail-item">
              <i class="fas fa-file-alt"></i>
              <span>Analyzing selected sections...</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-robot"></i>
              <span>AI Processing in progress</span>
            </div>
          </div>
        </div>
  
        <!-- Step 5: Policy Review -->
        <div v-if="currentStep === 5" class="policy-review-section">
          <div class="review-header">
            <div class="review-icon-container">
              <div class="success-circle">
                <i class="fas fa-check"></i>
              </div>
            </div>
            <h3>Policy Extraction Complete!</h3>
            <p>Your policies have been successfully extracted and are ready for review.</p>
          </div>
          
          <div class="policy-summary">
            <div class="summary-card">
              <div class="summary-icon">
                <i class="fas fa-file-alt"></i>
              </div>
              <div class="summary-content">
                <h4>{{ extractedPoliciesCount }}</h4>
                <p>Policies Extracted</p>
              </div>
            </div>
            <div class="summary-card">
              <div class="summary-icon">
                <i class="fas fa-layer-group"></i>
              </div>
              <div class="summary-content">
                <h4>{{ selectedSectionsCount }}</h4>
                <p>Sections Processed</p>
              </div>
            </div>
          </div>
          
          <div class="review-actions">
            <button @click="viewPolicyExtractor" class="view-policies-btn">
              <i class="fas fa-table"></i>
              View Extracted Policies
            </button>
            <button @click="resetUpload" class="upload-another-btn">
              <i class="fas fa-plus"></i>
              Upload Another Document
            </button>
          </div>
        </div>
  
        <!-- Step 6: Policy Details & Extracted Content -->
        <div v-if="currentStep === 6" class="policy-details-section">
          <div class="details-header">
            <h3>Policy Details & Extracted Content</h3>
            <p>Review extracted policies and provide additional information in one place</p>
          </div>
          
          <div class="dynamic-forms-layout">
            <!-- Section 1: Framework Form (Always Single) -->
            <div class="form-section framework-form">
              <div class="section-header">
                <h4>Framework Information</h4>
            </div>
              <div class="form-container">
                <div class="form-group">
                  <label>TITLE:</label>
                  <input type="text" v-model="policyDetails.title" placeholder="ISO 27001" />
                </div>
                
                <div class="form-group">
                  <label>DESCRIPTION:</label>
                  <textarea v-model="policyDetails.description" placeholder="Information security, cyber security and privacy protection - Information Security Management Systems"></textarea>
              </div>
              
                <div class="form-group">
                  <label>CATEGORY:</label>
                  <input type="text" v-model="policyDetails.category" placeholder="Security" />
                </div>
                
                <div class="form-row date-row">
                <div class="form-group">
                  <label>EFFECTIVE DATE:</label>
                  <input type="date" v-model="policyDetails.effectiveDate" />
                </div>
              </div>
              
                <div class="form-row date-row">
                <div class="form-group">
                  <label>START DATE:</label>
                  <input type="date" v-model="policyDetails.startDate" />
                </div>
                  
                <div class="form-group">
                  <label>END DATE:</label>
                  <input type="date" v-model="policyDetails.endDate" />
                </div>
              </div>
              </div>
            </div>
            
            <!-- Section 2: Policy Forms with their Sub-Policies grouped together -->
            <div v-for="(sectionName, sectionIndex) in uniqueSectionNames" :key="'section-' + sectionIndex" class="policy-section-group">
              
              <!-- Policy Form for this section -->
              <div class="form-section policy-form">
                <div class="section-header">
                  <h4>Policy {{ sectionIndex + 1 }} - {{ sectionName }}</h4>
                </div>
                <div class="form-container">
                <div class="form-group">
                  <label>DOCUMENT URL:</label>
                    <input type="text" v-model="policyFormData[sectionName].documentUrl" placeholder="https://updated-url.com" />
                </div>
                  
                <div class="form-group">
                  <label>IDENTIFIER:</label>
                    <input type="text" v-model="policyFormData[sectionName].identifier" placeholder="ISO" />
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>CREATED BY:</label>
                      <input type="text" v-model="policyFormData[sectionName].createdBy" placeholder="John Doe" />
                </div>
                    
                <div class="form-group">
                  <label>REVIEWER:</label>
                      <input type="text" v-model="policyFormData[sectionName].reviewer" placeholder="Jane Smith" />
                </div>
              </div>
              
                <div class="form-group">
                  <label>POLICY NAME:</label>
                    <input type="text" v-model="policyFormData[sectionName].policyName" :placeholder="'Enter policy name for ' + sectionName" />
                </div>
                  
                <div class="form-group">
                  <label>DEPARTMENT:</label>
                    <input type="text" v-model="policyFormData[sectionName].department" placeholder="Enter department" />
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>SCOPE:</label>
                      <input type="text" v-model="policyFormData[sectionName].scope" placeholder="Enter policy scope" />
                </div>
                    
                <div class="form-group">
                  <label>APPLICABILITY:</label>
                      <input type="text" v-model="policyFormData[sectionName].applicability" placeholder="Enter applicability" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>OBJECTIVE:</label>
                      <textarea v-model="policyFormData[sectionName].objective" placeholder="Enter policy objective"></textarea>
                </div>
                    
                <div class="form-group">
                  <label>COVERAGE RATE (%):</label>
                      <input type="number" v-model="policyFormData[sectionName].coverageRate" placeholder="Enter coverage rate" min="0" max="100" />
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Sub-Policy Forms for this specific section -->
              <div v-for="(policy, policyIndex) in policies.filter(p => p.section_name === sectionName)" 
                   :key="'subpolicy-' + sectionName + '-' + policyIndex" 
                   class="form-section sub-policy-form">
                <div class="section-header">
                  <h4>Sub-Policy {{ policyIndex + 1 }} - {{ policy.Sub_policy_id || 'N/A' }}</h4>
                  <div class="policy-count">
                    <span>Related to: {{ sectionName }}</span>
                  </div>
                </div>
                
                <div class="form-container">
                  <div class="form-row">
                    <div class="form-group">
                      <label>POLICY NAME:</label>
                      <input type="text" v-model="policy.sub_policy_name" placeholder="Enter policy name" />
                    </div>
                    
                    <div class="form-group">
                      <label>POLICY IDENTIFIER:</label>
                      <input type="text" v-model="policy.Sub_policy_id" placeholder="Enter policy identifier" />
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label>DESCRIPTION:</label>
                    <textarea v-model="policy.control" placeholder="Enter policy description" rows="4"></textarea>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label>SCOPE:</label>
                      <input type="text" v-model="policy.scope" placeholder="Enter policy scope" />
                    </div>
                    
                    <div class="form-group">
                      <label>DEPARTMENT:</label>
                      <input type="text" v-model="policy.department" placeholder="Enter department" />
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label>OBJECTIVE:</label>
                      <textarea v-model="policy.objective" placeholder="Enter policy objective" rows="3"></textarea>
                    </div>
                    
                    <div class="form-group">
                      <label>APPLICABILITY:</label>
                      <input type="text" v-model="policy.applicability" placeholder="Enter applicability" />
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label>COVERAGE RATE (%):</label>
                      <input type="number" v-model="policy.coverage_rate" placeholder="Enter coverage rate" min="0" max="100" />
                    </div>
                    
                    <div class="form-group">
                      <label>RELATED CONTROLS:</label>
                      <input type="text" v-model="policy.related_controls" placeholder="Enter related controls" />
                    </div>
                  </div>
                  
                  <div class="form-row date-row">
                    <div class="form-group">
                      <label>START DATE:</label>
                      <input type="date" v-model="policy.start_date" />
                    </div>
                    
                    <div class="form-group">
                      <label>END DATE:</label>
                      <input type="date" v-model="policy.end_date" />
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label>UPLOAD DOCUMENT:</label>
                    <div class="file-upload-container">
                      <input type="file" :id="'file-' + sectionName + '-' + policyIndex" @change="handleSubPolicyFileUpload($event, policies.indexOf(policy))" accept=".pdf,.doc,.docx,.txt" />
                      <label :for="'file-' + sectionName + '-' + policyIndex" class="file-upload-btn">
                        <i class="fas fa-upload"></i>
                        Choose File
                      </label>
                      <span v-if="policy.uploaded_file" class="file-name">{{ policy.uploaded_file.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Compliance Forms for each sub-policy -->
              <div v-for="(policy, policyIndex) in policies.filter(p => p.section_name === sectionName)" 
                   :key="'compliance-' + sectionName + '-' + policyIndex" 
                   class="form-section compliance-form">
                <div class="section-header">
                  <h4>Compliance Items for {{ policy.Sub_policy_id || 'Sub-Policy ' + (policyIndex + 1) }}</h4>
                  <div class="policy-count">
                    <span>{{ complianceData[`${sectionName}_${policy.Sub_policy_id}`]?.length || 0 }} compliance items</span>
                  </div>
                  <button @click="addComplianceItem(`${sectionName}_${policy.Sub_policy_id}`)" class="add-compliance-btn">
                    <i class="fas fa-plus"></i>
                    Add Compliance
                </button>
                </div>
                
                <div class="compliance-container" v-if="complianceData[`${sectionName}_${policy.Sub_policy_id}`]">
                  <div v-for="(compliance, complianceIndex) in complianceData[`${sectionName}_${policy.Sub_policy_id}`]" 
                       :key="'compliance-item-' + complianceIndex" 
                       class="compliance-item">
                    <div class="compliance-header">
                      <div class="compliance-letter">{{ compliance.letter }})</div>
                      <div class="compliance-title">Compliance {{ complianceIndex + 1 }}</div>
                      <button v-if="complianceData[`${sectionName}_${policy.Sub_policy_id}`].length > 1" 
                              @click="removeComplianceItem(`${sectionName}_${policy.Sub_policy_id}`, complianceIndex)" 
                              class="remove-compliance-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
                    
                    <div class="compliance-form-container">
                      <div class="form-row">
                        <div class="form-group">
                          <label>COMPLIANCE NAME:</label>
                          <input type="text" v-model="compliance.name" placeholder="Enter compliance name" />
            </div>
            
                        <div class="form-group">
                          <label>STATUS:</label>
                          <select v-model="compliance.status">
                            <option value="pending">Pending</option>
                            <option value="in-progress">In Progress</option>
                            <option value="completed">Completed</option>
                            <option value="not-applicable">Not Applicable</option>
                          </select>
                </div>
              </div>
              
                      <div class="form-group">
                        <label>DESCRIPTION:</label>
                        <textarea v-model="compliance.description" placeholder="Enter compliance description" rows="3"></textarea>
                      </div>
                      
                      <div class="form-row">
                        <div class="form-group">
                          <label>ASSIGNEE:</label>
                          <input type="text" v-model="compliance.assignee" placeholder="Enter assignee name" />
                        </div>
                        
                        <div class="form-group">
                          <label>DUE DATE:</label>
                          <input type="date" v-model="compliance.dueDate" />
                        </div>
                      </div>
                      
                      <div class="form-group">
                        <label>EVIDENCE DOCUMENT:</label>
                        <div class="file-upload-container">
                          <input type="file" 
                                 :id="'compliance-file-' + sectionName + '-' + policyIndex + '-' + complianceIndex" 
                                 @change="handleComplianceFileUpload($event, `${sectionName}_${policy.Sub_policy_id}`, complianceIndex)" 
                                 accept=".pdf,.doc,.docx,.txt,.jpg,.png" />
                          <label :for="'compliance-file-' + sectionName + '-' + policyIndex + '-' + complianceIndex" class="file-upload-btn">
                            <i class="fas fa-upload"></i>
                            Upload Evidence
                          </label>
                          <span v-if="compliance.evidence" class="file-name">{{ compliance.evidence.name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Global Actions -->
            <div class="form-actions-global">
              <button @click="saveAllDetails" class="save-btn primary-btn">
                  <i class="fas fa-save"></i>
                Save All Details
                </button>
              <button @click="resetAllForms" class="reset-btn secondary-btn">
                <i class="fas fa-undo"></i>
                Reset All Forms
                </button>
            </div>
          </div>
        </div>
  
        <!-- Upload Status Messages -->
        <div v-if="uploadStatus && currentStep === 1" class="status-message" :class="uploadStatus.type">
          <i :class="uploadStatus.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
          {{ uploadStatus.message }}
        </div>
        
        <!-- Add this congratulations modal component -->
        <div v-if="showCongratulationsModal" class="congratulations-modal">
          <div class="congratulations-container">
            <div class="congratulations-header">
              <div class="congratulations-icon-container">
                <i class="fas fa-check-circle"></i>
              </div>
              <h2>Congratulations!</h2>
              <p class="congratulations-message">Your framework has been successfully added to the system.</p>
            </div>
            <div class="congratulations-content">
              <p>You have completed all the steps to add a new framework to your GRC system.</p>
              <p>Your framework is now ready to be used for compliance management.</p>
            </div>
            <div class="congratulations-actions">
              <button @click="goToPolicyDashboard" class="ok-btn">
                <i class="fas fa-check"></i>
                Go to Policy Dashboard
              </button>
            </div>
          </div>
        </div>
        
        <!-- Global Success Notification -->
        <div v-if="uploadStatus && uploadStatus.type === 'success' && currentStep > 1" class="global-notification success">
          <div class="notification-content">
            <i class="fas fa-check-circle"></i>
            <div class="notification-message">
              {{ uploadStatus.message }}
            </div>
            <button @click="uploadStatus = null" class="notification-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        <!-- Policy Edit Modal -->
        <div v-if="showPolicyDetail" class="policy-edit-modal">
          <div class="policy-edit-container">
            <div class="policy-edit-header">
              <h3>Edit Policy</h3>
              <div class="policy-edit-actions">
                <button @click="savePolicy" class="save-btn">
                  <i class="fas fa-save"></i>
                  Save
                </button>
                <button @click="closePolicyDetail" class="close-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="policy-edit-body">
              <div class="policy-field">
                <label>Section</label>
                <input type="text" v-model="currentPolicy.section_name" />
              </div>
              
              <div class="policy-field">
                <label>Control ID</label>
                <input type="text" v-model="currentPolicy.Sub_policy_id" />
              </div>
              
              <div class="policy-field">
                <label>Policy Name</label>
                <input type="text" v-model="currentPolicy.sub_policy_name" />
              </div>
              
              <div class="policy-field">
                <label>Control</label>
                <textarea v-model="currentPolicy.control" rows="8"></textarea>
              </div>
              
              <div class="policy-field">
                <label>Related Controls</label>
                <input type="text" v-model="currentPolicy.related_controls" />
              </div>
              
              <div class="policy-field">
                <label>Control Enhancements</label>
                <textarea v-model="currentPolicy.control_enhancements" rows="5"></textarea>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Content Viewer Modal -->
        <div v-if="showContentViewer" class="content-viewer-modal">
          <div class="content-viewer-container">
            <div class="content-viewer-header">
              <h3>Framework Content Viewer</h3>
              <button @click="closeContentViewer" class="close-btn">
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div class="content-viewer-body">
              <!-- Search Box -->
              <div class="search-box">
                <input type="text" v-model="searchQuery" placeholder="Search sections..." />
              </div>
              
              <!-- Section List -->
              <div class="section-list">
                <div v-for="(section, index) in filteredSections" :key="index" class="section-item">
                  <div class="section-header" @click="toggleSection(section.id)">
                    <div class="section-checkbox">
                      <input type="checkbox" v-model="section.selected" @change="updateSelection(section)" />
                      <span>{{ section.title }}</span>
                    </div>
                    <i class="fas" :class="section.expanded ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                  </div>
                  <div v-if="section.expanded" class="section-content">
                    <div v-for="(subsection, subIndex) in section.subsections" :key="subIndex" class="subsection-item">
                      <div class="subsection-checkbox">
                        <input type="checkbox" v-model="subsection.selected" @change="updateSubsectionSelection(section)" />
                        <span>{{ subsection.title }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="content-viewer-footer">
              <button @click="selectAllSections" class="select-all-btn">Select All</button>
              <button @click="deselectAllSections" class="deselect-all-btn">Deselect All</button>
              <button @click="saveSelectedSections" class="save-selection-btn">Save Selection</button>
            </div>
          </div>
        </div>
  
        <!-- Policy Extractor View (Table Only) -->
        <div v-if="showPolicyExtractor" class="policy-extractor-modal">
          <div class="policy-extractor-container">
            <div class="policy-extractor-header">
              <h3>Extracted Policies</h3>
              <div class="policy-actions">
                <button @click="saveAllPolicies" class="save-all-btn">
                  <i class="fas fa-save"></i>
                  Save All
                </button>
                <button @click="closePolicyExtractor" class="close-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="policy-extractor-body">
              <div class="policy-table-container">
                <table class="policy-table" v-if="policies.length > 0">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Control ID</th>
                      <th>Policy Name</th>
                      <th>Control</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <template v-for="(policy, index) in policies" :key="index">
                      <tr :class="{ 'expanded-row': expandedRows[index] }">
                        <td>{{ policy.section_name || 'N/A' }}</td>
                        <td>{{ policy.Sub_policy_id || 'N/A' }}</td>
                        <td>{{ policy.sub_policy_name || 'N/A' }}</td>
                        <td class="control-cell">
                          {{ policy.control ? (policy.control.length > 100 ? policy.control.substring(0, 100) + '...' : policy.control) : 'N/A' }}
                        </td>
                        <td class="actions-cell">
                          <button @click="toggleExpandRow(index)" class="view-btn">
                            <i :class="expandedRows[index] ? 'fas fa-chevron-up' : 'fas fa-eye'"></i>
                            {{ expandedRows[index] ? 'Hide' : 'View' }}
                          </button>
                          <button @click="editPolicy(policy, index)" class="edit-btn">
                            <i class="fas fa-edit"></i>
                            Edit
                          </button>
                        </td>
                      </tr>
                      <tr v-if="expandedRows[index]" class="detail-row">
                        <td colspan="5">
                          <div class="policy-details-container">
                            <div class="policy-details-section">
                              <h4>Control ID</h4>
                              <div class="detail-content">{{ policy.Sub_policy_id || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Policy Name</h4>
                              <div class="detail-content">{{ policy.sub_policy_name || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Control</h4>
                              <div class="detail-content control-content">
                                <div v-if="getFormattedControl(policy.control).length > 0">
                                  <ul>
                                    <li v-for="(point, idx) in getFormattedControl(policy.control)" :key="idx">
                                      {{ point }}
                                    </li>
                                  </ul>
                                </div>
                                <div v-else>{{ policy.control || 'N/A' }}</div>
                              </div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Related Controls</h4>
                              <div class="detail-content">{{ policy.related_controls || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Control Enhancements</h4>
                              <div class="detail-content">{{ policy.control_enhancements || 'N/A' }}</div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
                <div v-else class="no-policies-message">
                  <p>No policies found. Please try processing the document again.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onUnmounted, watch } from 'vue'
  import axios from 'axios'
  
  export default {
    name: 'UploadFramework',
    setup() {
      const selectedFile = ref(null)
      const isDragOver = ref(false)
      const isUploading = ref(false)
      const isLoadingDefault = ref(false)
      const isProcessing = ref(false)
      const processingComplete = ref(false)
      const uploadStatus = ref(null)
      const fileInput = ref(null)
      const processingStatus = ref({ progress: 0, message: '' })
      const taskId = ref(null)
      const uploadedFileName = ref('')
      const processingStartTime = ref('')
      let progressInterval = null
      
      // Step management
      const currentStep = ref(1)
      const stepHistory = ref([1])
      
      // Content viewer related
      const showContentViewer = ref(false)
      const sections = ref([])
      const searchQuery = ref('')
      
      // Policy extraction progress
      const policyExtractionComplete = ref(false)
      const policyExtractionInProgress = ref(false)
      const policyExtractionMessage = ref('')
      const policyExtractionProgress = ref(0)
  
      // Policy extractor related
      const showPolicyExtractor = ref(false)
      const policies = ref([])
      const extractedPoliciesCount = ref(0)
      const selectedSectionsCount = ref(0)
      
      // Policy detail view related
      const showPolicyDetail = ref(false)
      const currentPolicy = ref({})
      const currentPolicyIndex = ref(null)
      const isEditing = ref(false)
      
      // For expandable rows
      const expandedRows = ref({})
      
      const toggleExpandRow = (index) => {
        expandedRows.value = {
          ...expandedRows.value,
          [index]: !expandedRows.value[index]
        }
      }
      
      const getFormattedControl = (controlText) => {
        if (!controlText) {
          return []
        }
        
        // Split control text into bullet points if it contains multiple sentences or numbered items
        // Check if already has bullet points or numbered format
        if (/^\s*[\d*-]+\s+/.test(controlText)) {
          return controlText.split('\n')
            .filter(line => line.trim())
            .map(line => line.trim())
        }
        
        // Split by period followed by space or newline
        return controlText.split(/\.\s+|\.\n/)
          .filter(sentence => sentence.trim())
          .map(sentence => sentence.trim() + (sentence.endsWith('.') ? '' : '.'))
      }
  
      const filteredSections = computed(() => {
        if (!searchQuery.value) return sections.value
        
        const query = searchQuery.value.toLowerCase()
        return sections.value.filter(section => 
          section.title.toLowerCase().includes(query) ||
          section.subsections.some(sub => sub.title.toLowerCase().includes(query))
        )
      })
  
      const formattedControl = computed(() => {
        if (!currentPolicy.value || !currentPolicy.value.control) {
          return []
        }
        
        // Split control text into bullet points if it contains multiple sentences or numbered items
        const text = currentPolicy.value.control
        
        // Check if already has bullet points or numbered format
        if (/^\s*[\d*-]+\s+/.test(text)) {
          return text.split('\n')
            .filter(line => line.trim())
            .map(line => line.trim())
        }
        
        // Split by period followed by space or newline
        return text.split(/\.\s+|\.\n/)
          .filter(sentence => sentence.trim())
          .map(sentence => sentence.trim() + (sentence.endsWith('.') ? '' : '.'))
      })
  
      const goToStep = (step) => {
        if (step !== currentStep.value) {
          stepHistory.value.push(currentStep.value)
          currentStep.value = step
        }
      }
  
      const goBack = () => {
        // Always go back exactly one step, never skip steps
        currentStep.value = Math.max(1, currentStep.value - 1)
      }
  
      const triggerFileInput = () => {
        fileInput.value.click()
      }
  
      const handleFileSelect = (event) => {
        const file = event.target.files[0]
        if (file) {
          selectedFile.value = file
          uploadStatus.value = null
        }
      }
  
      const handleDrop = (event) => {
        event.preventDefault()
        isDragOver.value = false
        const file = event.dataTransfer.files[0]
        if (file) {
          selectedFile.value = file
          uploadStatus.value = null
        }
      }
  
      const removeFile = () => {
        selectedFile.value = null
        uploadStatus.value = null
        fileInput.value.value = ''
      }
  
      const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
      }
  
      const startProgressTracking = (id, onComplete = null) => {
        taskId.value = id
        let currentProgress = 0
        
        progressInterval = setInterval(async () => {
          try {
            const response = await axios.get(`/api/processing-status/${id}/`)
            
            // Simulate progressive loading if backend doesn't provide it
            if (response.data.progress !== undefined) {
              processingStatus.value = response.data
            } else {
              // Progressive simulation
              currentProgress += Math.random() * 15 + 5 // Random increment between 5-20%
              if (currentProgress > 95) currentProgress = 95
              
              processingStatus.value = {
                progress: Math.floor(currentProgress),
                message: getProgressMessage(Math.floor(currentProgress))
              }
            }
            
            if (processingStatus.value.progress >= 100) {
              clearInterval(progressInterval)
              isProcessing.value = false
              processingComplete.value = true
              
              if (onComplete) {
                // Call the provided callback instead of default behavior
                onComplete()
              } else {
                // Default behavior - go to step 3 and fetch extracted content
                goToStep(3)
                fetchExtractedContent(id)
              }
            }
          } catch (error) {
            console.error('Error fetching progress:', error)
            if (error.response?.status === 404) {
              clearInterval(progressInterval)
              isProcessing.value = false
              uploadStatus.value = {
                type: 'error',
                message: 'Processing task not found or expired'
              }
              currentStep.value = 1
            }
          }
        }, 1000) // Check every second
      }
  
      const getProgressMessage = (progress) => {
        if (progress < 20) return 'Initializing document processing...'
        if (progress < 40) return 'Extracting text content...'
        if (progress < 60) return 'Analyzing document structure...'
        if (progress < 80) return 'Identifying sections and subsections...'
        if (progress < 95) return 'Finalizing extraction...'
        return 'Processing complete!'
      }
  
      const uploadFile = async () => {
        if (!selectedFile.value) return
  
        isUploading.value = true
        uploadStatus.value = null
  
        const formData = new FormData()
        formData.append('file', selectedFile.value)
  
        try {
          const response = await axios.post('/api/upload-framework/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
  
          uploadedFileName.value = response.data.filename
          processingStartTime.value = new Date().toLocaleTimeString()
          
          if (response.data.processing && response.data.task_id) {
            // Start processing mode
            isProcessing.value = true
            goToStep(2)
            startProgressTracking(response.data.task_id)
          } else {
            // Non-PDF file, just show success
            uploadStatus.value = {
              type: 'success',
              message: `File "${response.data.filename}" uploaded successfully!`
            }
            
            setTimeout(() => {
              removeFile()
              uploadStatus.value = null
            }, 3000)
          }
  
        } catch (error) {
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Upload failed. Please try again.'
          }
        } finally {
          isUploading.value = false
        }
      }
  
      const loadDefaultData = async () => {
        isLoadingDefault.value = true
        uploadStatus.value = null
  
        try {
          const response = await axios.post('/api/load-default-data/')
  
          uploadedFileName.value = response.data.filename
          processingStartTime.value = new Date().toLocaleTimeString()
          
          if (response.data.processing && response.data.task_id) {
            // Start processing mode
            isProcessing.value = true
            taskId.value = response.data.task_id
            
            // Check if default data has pre-selected content and extracted policies
            const hasPreSelectedContent = response.data.has_pre_selected_content
            const hasPreExtractedPolicies = response.data.has_pre_extracted_policies
            
            if (hasPreExtractedPolicies) {
              // Skip all steps and go directly to step 5 (policy review)
              goToStep(5)
              // Start tracking the loading progress
              startProgressTracking(response.data.task_id, () => {
                // Once loading is complete, fetch the pre-extracted policies
                fetchExtractedPolicies()
              })
            } else if (hasPreSelectedContent) {
              // Skip to step 4 (policy extraction) since content is already selected
              goToStep(4)
              startProgressTracking(response.data.task_id, () => {
                // Once loading is complete, start policy extraction
                policyExtractionInProgress.value = true
                policyExtractionMessage.value = "Starting policy extraction with default selections..."
                policyExtractionProgress.value = 0
                pollPolicyExtractionStatus()
              })
            } else {
              // Regular flow - go to step 2 (processing)
              goToStep(2)
              startProgressTracking(response.data.task_id)
            }
          } else {
            // Show success message
            uploadStatus.value = {
              type: 'success',
              message: `Default data "${response.data.filename}" loaded successfully!`
            }
          }
  
        } catch (error) {
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to load default data. Please try again.'
          }
        } finally {
          isLoadingDefault.value = false
        }
      }
      
      const fetchExtractedContent = async (id) => {
        try {
          const response = await axios.get(`/api/get-sections/${id}/`)
          
          // Transform data for UI - only include txt_chunks files
          sections.value = response.data.map((section, index) => {
            // Filter subsections to only include txt_chunks
            const txtSubsections = section.subsections.filter(subsection => 
              subsection.name.startsWith('txt_chunks/') && subsection.name.endsWith('.txt')
            );
            
            // Clean up the subsection names to make them more readable
            const cleanedSubsections = txtSubsections.map((subsection, subIndex) => ({
              id: subIndex,
              title: subsection.name.replace('txt_chunks/extracted_', '')
                                   .replace('.txt', '')
                                   .replace(/_/g, ' '),
              originalName: subsection.name,
              content: subsection.content,
              selected: false
            }));
            
            return {
              id: index,
              title: section.name,
              selected: false,
              expanded: false,
              subsections: cleanedSubsections
            }
          }).filter(section => section.subsections.length > 0); // Only include sections with txt subsections
        } catch (error) {
          console.error('Error fetching extracted content:', error)
        }
      }
  
      const resetUpload = () => {
        selectedFile.value = null
        isProcessing.value = false
        isLoadingDefault.value = false
        processingComplete.value = false
        uploadStatus.value = null
        processingStatus.value = { progress: 0, message: '' }
        taskId.value = null
        uploadedFileName.value = ''
        processingStartTime.value = ''
        fileInput.value.value = ''
        sections.value = []
        showContentViewer.value = false
        policyExtractionComplete.value = false
        policyExtractionInProgress.value = false
        policyExtractionMessage.value = ''
        policyExtractionProgress.value = 0
        showPolicyExtractor.value = false
        policies.value = []
        extractedPoliciesCount.value = 0
        selectedSectionsCount.value = 0
        currentStep.value = 1
        stepHistory.value = [1]
      }
  
      const viewExtractedContent = () => {
        showContentViewer.value = true
      }
      
      const closeContentViewer = () => {
        // Just close the modal without changing the current step
        showContentViewer.value = false
      }
      
      const toggleSection = (sectionId) => {
        const section = sections.value.find(s => s.id === sectionId)
        if (section) {
          section.expanded = !section.expanded
        }
      }
      
      const updateSelection = (section) => {
        // Update all subsections when section is selected/deselected
        section.subsections.forEach(sub => {
          sub.selected = section.selected
        })
      }
      
      const updateSubsectionSelection = (section) => {
        // Update section based on subsection selection
        section.selected = section.subsections.every(sub => sub.selected)
      }
      
      const selectAllSections = () => {
        sections.value.forEach(section => {
          section.selected = true
          section.subsections.forEach(sub => {
            sub.selected = true
          })
        })
      }
      
      const deselectAllSections = () => {
        sections.value.forEach(section => {
          section.selected = false
          section.subsections.forEach(sub => {
            sub.selected = false
          })
        })
      }
      
      const saveSelectedSections = async () => {
        try {
          // Prepare data for selected sections
          const selectedData = sections.value
            .filter(section => section.selected || section.subsections.some(sub => sub.selected))
            .map(section => ({
              name: section.title,
              subsections: section.subsections
                .filter(sub => sub.selected)
                .map(sub => ({
                  name: sub.originalName, // Use the original name for backend reference
                  content: sub.content
                }))
            }))
            .filter(section => section.subsections.length > 0)
          
          if (selectedData.length === 0) {
            alert('No sections selected. Please select at least one item.')
            return
          }
          
          // Count selected sections
          selectedSectionsCount.value = selectedData.reduce((total, section) => total + section.subsections.length, 0)
          
          const response = await axios.post('/api/create-checked-structure/', {
            task_id: taskId.value,
            sections: selectedData
          })
          
          if (response.status === 200) {
            closeContentViewer()
            
            // Move to policy extraction step
            goToStep(4)
            policyExtractionInProgress.value = true
            policyExtractionMessage.value = "Initializing policy extraction..."
            policyExtractionProgress.value = 0
            
            // Start polling for policy extraction status
            pollPolicyExtractionStatus()
          }
        } catch (error) {
          console.error('Error saving selected sections:', error)
          alert('Error saving selected sections: ' + error.message)
        }
      }
  
      // Update the polling function with progressive loading
      const pollPolicyExtractionStatus = () => {
        let statusInterval = setInterval(async () => {
          try {
            // Use the dedicated policy extraction progress endpoint
            const response = await axios.get(`/api/policy-extraction-progress/${taskId.value}/`)
            
            // Use the actual progress from the backend
            const actualProgress = response.data.progress || 0
            const message = response.data.message || "Processing..."
            
            policyExtractionProgress.value = Math.floor(actualProgress)
            policyExtractionMessage.value = message
            
            // Check if extraction is complete
            if (actualProgress >= 100) {
              clearInterval(statusInterval)
              
              // Complete the progress
              policyExtractionProgress.value = 100
              policyExtractionMessage.value = "Policy extraction complete!"
              
              // Wait a bit then move to final step
              setTimeout(async () => {
                policyExtractionComplete.value = true
                policyExtractionInProgress.value = false
                
                // Fetch extracted policies
                await fetchExtractedPolicies()
                goToStep(5)
              }, 1000)
            }
          } catch (error) {
            console.error('Error checking extraction status:', error)
            
            // Fallback to general processing status if policy extraction endpoint fails
            try {
              const fallbackResponse = await axios.get(`/api/processing-status/${taskId.value}/`)
              
              if (fallbackResponse.data.progress >= 100) {
                clearInterval(statusInterval)
                policyExtractionProgress.value = 100
                policyExtractionMessage.value = "Policy extraction complete!"
                
                setTimeout(async () => {
                  policyExtractionComplete.value = true
                  policyExtractionInProgress.value = false
                  await fetchExtractedPolicies()
                  goToStep(5)
                }, 1000)
              }
            } catch (fallbackError) {
              console.error('Error with fallback status check:', fallbackError)
              policyExtractionInProgress.value = false
              clearInterval(statusInterval)
            }
          }
        }, 2000) // Check every 2 seconds
      }
  
      const fetchExtractedPolicies = async () => {
        try {
          const response = await axios.get(`/api/get-extracted-policies/${taskId.value}/`)
          policies.value = response.data.policies || []
          extractedPoliciesCount.value = response.data.total_policies || policies.value.length
          
          console.log('Fetched policies:', policies.value.length)
          console.log('Policies data:', policies.value)
        } catch (error) {
          console.error('Error fetching policies:', error)
          policies.value = []
          extractedPoliciesCount.value = 0
          
          // Show error message if needed
          if (error.response?.status === 404) {
            console.log('Policy data not found - extraction may still be in progress')
          }
        }
      }
  
      const viewPolicyExtractor = async () => {
        try {
          // Load policies and go to Step 6 directly
          const response = await axios.get(`/api/extracted-policies/${taskId.value}/`)
          
          if (response.data.policies) {
            policies.value = response.data.policies
            extractedPoliciesCount.value = response.data.total_policies || policies.value.length
            
            // Initialize dynamic forms based on extracted policies
            initializeDynamicForms()
            
            // Set active tab to "extracted" to show the extracted policies
            activeTab.value = 'extracted'
            
            // Go to the unified policy page (original Step 6)
            goToStep(6)
          }
        } catch (error) {
          console.error('Error loading extracted policies:', error)
          uploadStatus.value = {
            type: 'error',
            message: 'Failed to load extracted policies. Please try again.'
          }
        }
      }
  
      const initializeDynamicForms = () => {
        // Initialize policy form data for each unique section
        policyFormData.value = {}
        
        uniqueSectionNames.value.forEach(sectionName => {
          policyFormData.value[sectionName] = {
            documentUrl: '',
            identifier: '',
            createdBy: '',
            reviewer: '',
            policyName: '',
            department: '',
            scope: '',
            applicability: '',
            objective: '',
            coverageRate: 0
          }
        })
        
        console.log('Initialized policy form data:', policyFormData.value)
      }
  
      const closePolicyExtractor = () => {
        // Just close the modal without changing the current step
        showPolicyExtractor.value = false
      }
  
      const editPolicy = (policy, index) => {
        // Copy the policy for editing
        currentPolicy.value = {...policy}
        currentPolicyIndex.value = index
        
        // Show the edit modal
        showPolicyDetail.value = true
      }
      
      const startEditing = () => {
        isEditing.value = true
      }
      
      const savePolicy = async () => {
        try {
          // Update the policy in the local array
          if (currentPolicyIndex.value !== null) {
            policies.value[currentPolicyIndex.value] = {...currentPolicy.value}
          }
          
          // Save to backend
          const response = await axios.post('/api/save-single-policy/', {
            policy: currentPolicy.value,
            task_id: taskId.value
          })
          
          if (response.status === 200) {
            // Close the modal
            showPolicyDetail.value = false
            
            // Show success message
            uploadStatus.value = {
              type: 'success',
              message: `Policy "${currentPolicy.value.Sub_policy_id}" saved successfully! Files updated: ${response.data.original_file} and ${response.data.updated_file}`
            }
            
            // Clear message after 5 seconds
            setTimeout(() => {
              uploadStatus.value = null
            }, 5000)
          }
        } catch (error) {
          console.error('Error saving policy:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save policy. Please try again.'
          }
        }
      }
      
      const saveAllPolicies = async () => {
        try {
          const response = await axios.post('/api/save-policies/', {
            policies: policies.value,
            task_id: taskId.value,
            filename: `policies_${taskId.value}`
          })
          
          if (response.status === 200) {
            uploadStatus.value = {
              type: 'success',
              message: `All policies saved successfully! (${policies.value.length} policies)\nFiles updated: ${response.data.original_file} and ${response.data.updated_file}`
            }
            
            // Show notification for longer (5 seconds)
            setTimeout(() => {
              uploadStatus.value = null
            }, 5000)
          }
        } catch (error) {
          console.error('Error saving all policies:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save policies. Please try again.'
          }
        }
      }
  
      // Cleanup interval on component unmount
      onUnmounted(() => {
        if (progressInterval) {
          clearInterval(progressInterval)
        }
      })
  
      // Policy details for Step 6
      const activeTab = ref('basic')
      const policyDetails = ref({
        title: '',
        description: '',
        category: '',
        effectiveDate: '',
        startDate: '',
        endDate: ''
      })
      
      const saveBasicDetails = async () => {
        try {
          const response = await axios.post('/api/save-policy-details/', {
            task_id: taskId.value,
            details: {
              basic: {
                title: policyDetails.value.title,
                description: policyDetails.value.description,
                category: policyDetails.value.category,
                effectiveDate: policyDetails.value.effectiveDate,
                startDate: policyDetails.value.startDate,
                endDate: policyDetails.value.endDate
              }
            }
          })
          
          if (response.status === 200) {
            uploadStatus.value = {
              type: 'success',
              message: 'Basic details saved successfully!'
            }
            
            // Move to next tab
            activeTab.value = 'additional'
            
            setTimeout(() => {
              uploadStatus.value = null
            }, 3000)
          }
        } catch (error) {
          console.error('Error saving basic details:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save details. Please try again.'
          }
        }
      }
      
      const saveAdditionalDetails = async () => {
        try {
          const response = await axios.post('/api/save-policy-details/', {
            task_id: taskId.value,
            details: {
              additional: {
                documentUrl: policyDetails.value.documentUrl,
                identifier: policyDetails.value.identifier,
                createdBy: policyDetails.value.createdBy,
                reviewer: policyDetails.value.reviewer,
                policyName: policyDetails.value.policyName,
                department: policyDetails.value.department,
                scope: policyDetails.value.scope,
                applicability: policyDetails.value.applicability,
                objective: policyDetails.value.objective,
                coverageRate: policyDetails.value.coverageRate
              }
            }
          })
          
          if (response.status === 200) {
            uploadStatus.value = {
              type: 'success',
              message: 'Additional details saved successfully!'
            }
            
            // Move to next tab
            activeTab.value = 'extracted'
            
            setTimeout(() => {
              uploadStatus.value = null
            }, 3000)
          }
        } catch (error) {
          console.error('Error saving additional details:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save details. Please try again.'
          }
        }
      }
      
      // Add showCongratulationsModal to the data
      const showCongratulationsModal = ref(false)
  
      const saveAllDetails = async () => {
        try {
          // Prepare the complete data package with compliance data
          const completePackage = {
            task_id: taskId.value,
            framework_details: policyDetails.value,
            policy_forms: policyFormData.value,
            sub_policies: policies.value,
            compliance_data: complianceData.value,
            unique_sections: uniqueSectionNames.value
          }
          
          // Debug logging
          console.log('Saving complete package:', completePackage)
          console.log('Task ID:', taskId.value)
          console.log('Framework Details:', policyDetails.value)
          console.log('Policy Forms:', policyFormData.value)
          console.log('Sub Policies:', policies.value)
          console.log('Compliance Data:', complianceData.value)
          console.log('Unique Sections:', uniqueSectionNames.value)
          
          const response = await axios.post('/api/save-complete-policy-package/', completePackage)
          
          if (response.status === 200) {
            // Save was successful
            const saveResponse = response.data
            
            // Now save the framework to the database
            try {
              const dbResponse = await axios.post('/api/save-framework-to-database/', {
                task_id: taskId.value
              })
              
              if (dbResponse.status === 200) {
                // Show success message with framework information
                uploadStatus.value = {
                  type: 'success',
                  message: `Framework "${policyDetails.value.title}" has been created successfully in the database with ID: ${dbResponse.data.framework_id}
                           Created ${dbResponse.data.total_policies} policies, ${dbResponse.data.total_sub_policies} sub-policies, and ${dbResponse.data.total_compliance_items} compliance items.
                           Hierarchical JSON: ${saveResponse.hierarchical_json_file}
                           Flat Excel: ${saveResponse.flat_excel_file}`
                }
                
                // Show congratulations modal
                showCongratulationsModal.value = true
                
                // Clear the success message after a while
                setTimeout(() => {
                  uploadStatus.value = null
                }, 8000)
              } else {
                // Show success for file save, but note DB save failed
                uploadStatus.value = {
                  type: 'warning',
                  message: `Files saved successfully, but database save failed.
                           Hierarchical JSON: ${saveResponse.hierarchical_json_file}
                           Flat Excel: ${saveResponse.flat_excel_file}`
                }
              }
            } catch (dbError) {
              console.error('Error saving to database:', dbError)
              uploadStatus.value = {
                type: 'warning',
                message: `Files saved successfully, but database save failed: ${dbError.response?.data?.error || dbError.message}
                         Hierarchical JSON: ${saveResponse.hierarchical_json_file}
                         Flat Excel: ${saveResponse.flat_excel_file}`
              }
            }
          }
        } catch (error) {
          console.error('Error saving complete package:', error)
          console.error('Error response:', error.response?.data)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save package. Please try again.'
          }
        }
      }
      
      // Add function to redirect to policy dashboard
      const goToPolicyDashboard = () => {
        // Close the modal
        showCongratulationsModal.value = false
        
        // Redirect to policy dashboard
        window.location.href = '/policy-dashboard'
      }
      
      const cancelEdit = () => {
        // Just reset the form without changing tabs or navigation
        // This way the user stays on the same page
        if (activeTab.value === 'basic') {
          // Reset basic form fields
          policyDetails.value.title = ''
          policyDetails.value.description = ''
          policyDetails.value.category = ''
          policyDetails.value.effectiveDate = ''
          policyDetails.value.startDate = ''
          policyDetails.value.endDate = ''
        } else if (activeTab.value === 'additional') {
          // Reset additional form fields
          policyDetails.value.documentUrl = ''
          policyDetails.value.identifier = ''
          policyDetails.value.createdBy = ''
          policyDetails.value.reviewer = ''
          policyDetails.value.policyName = ''
          policyDetails.value.department = ''
          policyDetails.value.scope = ''
          policyDetails.value.applicability = ''
          policyDetails.value.objective = ''
          policyDetails.value.coverageRate = 0
        }
        // No tab change or navigation
      }
      
      const closePolicyDetail = () => {
        showPolicyDetail.value = false
        currentPolicy.value = {}
        currentPolicyIndex.value = null
      }
  
      const goToEditDetails = () => {
        // Navigate to Step 6 (Edit Policy Details)
        goToStep(6)
        
        // Default to the 'basic' tab
        activeTab.value = 'basic'
      }
  
      const resetExtractedForm = () => {
        // Reset the extracted form without navigating away
        activeTab.value = 'extracted'
        // Any other form reset logic can go here if needed
      }
  
      // Add this after the policyDetails ref
      const policySearchQuery = ref('');
  
      // Add this computed property for filtering policies
      const filteredPolicies = computed(() => {
        if (!policySearchQuery.value) return policies.value;
        
        const query = policySearchQuery.value.toLowerCase();
        return policies.value.filter(policy => 
          (policy.Sub_policy_id && policy.Sub_policy_id.toLowerCase().includes(query)) ||
          (policy.sub_policy_name && policy.sub_policy_name.toLowerCase().includes(query)) ||
          (policy.control && policy.control.toLowerCase().includes(query)) ||
          (policy.related_controls && policy.related_controls.toLowerCase().includes(query))
        );
      });
  
      // Dynamic forms data
      const policyFormData = ref({})
      
      // Computed properties for dynamic forms
      const uniqueSectionNames = computed(() => {
        if (!policies.value || policies.value.length === 0) return []
        const sections = [...new Set(policies.value.map(p => p.section_name).filter(name => name))]
        return sections.sort()
      })
      
      // Initialize policy form data when section names change
      const initializePolicyFormData = () => {
        const newFormData = {}
        uniqueSectionNames.value.forEach(sectionName => {
          if (!policyFormData.value[sectionName]) {
            newFormData[sectionName] = {
              documentUrl: '',
              identifier: '',
              createdBy: '',
              reviewer: '',
              policyName: '',
              department: '',
              scope: '',
              applicability: '',
              objective: '',
              coverageRate: 0
            }
          } else {
            newFormData[sectionName] = policyFormData.value[sectionName]
          }
        })
        policyFormData.value = newFormData
      }
      
      // Watch for changes in policies to initialize form data
      watch(policies, () => {
        initializePolicyFormData()
      }, { deep: true })
  
      // New methods for dynamic forms
      const handleSubPolicyFileUpload = (event, index) => {
        const file = event.target.files[0]
        if (file && policies.value[index]) {
          policies.value[index].uploaded_file = file
        }
      }
      
      const addSubPolicy = (sectionName) => {
        const newSubPolicy = {
          section_name: sectionName,
          Sub_policy_id: '',
          sub_policy_name: '',
          control: '',
          scope: '',
          department: '',
          objective: '',
          applicability: '',
          coverage_rate: 0,
          related_controls: '',
          start_date: '',
          end_date: '',
          uploaded_file: null
        }
        policies.value.push(newSubPolicy)
      }
      
      const removeSubPolicy = (index) => {
        if (policies.value.length > 1) {
          policies.value.splice(index, 1)
        }
      }
      
      const resetAllForms = () => {
        // Reset framework form
        policyDetails.value = {
          title: '',
          description: '',
          category: '',
          effectiveDate: '',
          startDate: '',
          endDate: ''
        }
        
        // Reset policy forms
        policyFormData.value = {}
        initializePolicyFormData()
        
        // Reset sub-policy forms
        policies.value.forEach(policy => {
          policy.scope = ''
          policy.department = ''
          policy.objective = ''
          policy.applicability = ''
          policy.coverage_rate = 0
          policy.start_date = ''
          policy.end_date = ''
          policy.uploaded_file = null
        })
      }
  
      // New data properties for compliance forms
      const complianceData = ref({})
      
      // Computed property to parse compliance items from control data
      const getComplianceItems = (control) => {
        // If control is empty, null or just whitespace, return empty array
        if (!control || control.trim() === '') return [];
        
        // Match any alphabetical letter followed by "." or ")" with optional whitespace
        const letterPattern = /([a-z])[.)](\s*)/gi;
        
        // Get all matches with their positions
        const matches = [];
        let match;
        while ((match = letterPattern.exec(control)) !== null) {
          matches.push({
            letter: match[1].toLowerCase(),
            index: match.index,
            matchLength: match[0].length
          });
        }
        
        // If no matches found, return single compliance item if content is meaningful
        if (matches.length === 0) {
          if (control.trim().length < 5) return []; // Don't create for very short content
          
          return [{
            id: 'compliance_1',
            letter: 'a',
            name: control.substring(0, 100) + (control.length > 100 ? '...' : ''),
            description: control,
            status: 'pending',
            assignee: '',
            dueDate: '',
            evidence: null
          }];
        }
        
        // Create items by splitting between letter markers
        const items = matches.map((match, index) => {
          const startPos = match.index + match.matchLength;
          const endPos = index < matches.length - 1 ? matches[index + 1].index : control.length;
          const content = control.substring(startPos, endPos).trim();
          
          // Only create item if content is meaningful
          if (content.length < 5) return null;
          
          return {
            id: `compliance_${index + 1}`,
            letter: match.letter,
            name: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
            description: content,
            status: 'pending',
            assignee: '',
            dueDate: '',
            evidence: null
          };
        }).filter(item => item !== null); // Filter out null items
        
        return items;
      }
      
      // Initialize compliance data for all policies
      const initializeComplianceData = () => {
        const newComplianceData = {}
        
        policies.value.forEach(policy => {
          if (!policy.control || policy.control.trim() === '') return; // Skip if no control text
          
          const policyKey = `${policy.section_name}_${policy.Sub_policy_id}`
          const complianceItems = getComplianceItems(policy.control)
          
          // Only add to compliance data if there are actual items
          if (complianceItems.length > 0) {
            newComplianceData[policyKey] = complianceItems
          }
        })
        
        complianceData.value = newComplianceData
      }
      
      // Handle compliance file upload
      const handleComplianceFileUpload = (event, policyKey, complianceIndex) => {
        const file = event.target.files[0]
        if (file && complianceData.value[policyKey] && complianceData.value[policyKey][complianceIndex]) {
          complianceData.value[policyKey][complianceIndex].evidence = file
        }
      }
      
      // Add new compliance item
      const addComplianceItem = (policyKey) => {
        if (!complianceData.value[policyKey]) {
          complianceData.value[policyKey] = []
        }
        
        const newIndex = complianceData.value[policyKey].length
        const newItem = {
          id: `compliance_${newIndex + 1}`,
          letter: String.fromCharCode(97 + newIndex),
          name: '',
          description: '',
          status: 'pending',
          assignee: '',
          dueDate: '',
          evidence: null
        }
        
        complianceData.value[policyKey].push(newItem)
      }
      
      // Remove compliance item
      const removeComplianceItem = (policyKey, index) => {
        if (complianceData.value[policyKey] && complianceData.value[policyKey].length > 1) {
          complianceData.value[policyKey].splice(index, 1)
          
          // Re-index the remaining items
          complianceData.value[policyKey].forEach((item, idx) => {
            item.letter = String.fromCharCode(97 + idx)
            item.id = `compliance_${idx + 1}`
          })
        }
      }
  
      // Watch for changes in policies to initialize compliance data
      watch(policies, () => {
        if (policies.value.length > 0) {
          initializeComplianceData()
        }
      }, { immediate: true })
  
      return {
        selectedFile,
        isDragOver,
        isUploading,
        isLoadingDefault,
        isProcessing,
        processingComplete,
        uploadStatus,
        fileInput,
        processingStatus,
        uploadedFileName,
        processingStartTime,
        showContentViewer,
        sections,
        searchQuery,
        filteredSections,
        policyExtractionComplete,
        policyExtractionInProgress,
        policyExtractionMessage,
        policyExtractionProgress,
        showPolicyExtractor,
        policies,
        extractedPoliciesCount,
        selectedSectionsCount,
        currentStep,
        triggerFileInput,
        handleFileSelect,
        handleDrop,
        removeFile,
        formatFileSize,
        uploadFile,
        loadDefaultData,
        resetUpload,
        viewExtractedContent,
        closeContentViewer,
        toggleSection,
        updateSelection,
        updateSubsectionSelection,
        selectAllSections,
        deselectAllSections,
        saveSelectedSections,
        viewPolicyExtractor,
        closePolicyExtractor,
        goBack,
        goToStep,
        showPolicyDetail,
        currentPolicy,
        currentPolicyIndex,
        isEditing,
        formattedControl,
        editPolicy,
        startEditing,
        savePolicy,
        saveAllPolicies,
        expandedRows,
        toggleExpandRow,
        getFormattedControl,
        // Add activeTab to the return values
        activeTab,
        policyDetails,
        saveBasicDetails,
        saveAdditionalDetails,
        saveAllDetails,
        cancelEdit,
        closePolicyDetail,
        goToEditDetails,
        resetExtractedForm,
        policySearchQuery,
        filteredPolicies,
        handleSubPolicyFileUpload,
        addSubPolicy,
        removeSubPolicy,
        resetAllForms,
        uniqueSectionNames,
        policyFormData,
        initializePolicyFormData,
        initializeDynamicForms,
        complianceData,
        getComplianceItems,
        initializeComplianceData,
        handleComplianceFileUpload,
        addComplianceItem,
        removeComplianceItem,
        showCongratulationsModal,
        goToPolicyDashboard
      }
    }
  }
  </script>
  
  <style scoped>
  .upload-framework-container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    font-family: 'Inter', 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
  }
  
  /* Step Indicator */
  .step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
  }
  
  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
  }
  
  .step-number {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1.1rem;
    background: #e2e8f0;
    color: #64748b;
    transition: all 0.3s ease;
  }
  
  .step-item.active .step-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  }
  
  .step-item.completed .step-number {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
  }
  
  .step-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748b;
    text-align: center;
    transition: all 0.3s ease;
  }
  
  .step-item.active .step-label {
    color: #1e293b;
    font-weight: 600;
  }
  
  .step-item.completed .step-label {
    color: #0f766e;
  }
  
  .step-divider {
    width: 80px;
    height: 2px;
    background: #e2e8f0;
    margin: 0 1rem;
    transition: all 0.3s ease;
  }
  
  .step-item.completed + .step-divider {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  }
  
  /* Back Button */
  .back-button-container {
    margin-bottom: 1.5rem;
  }
  
  .back-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .back-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  .header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  .header h1 {
    color: #1e293b;
    margin-bottom: 0.5rem;
    font-weight: 700;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .header p {
    color: #64748b;
    font-size: 1.2rem;
    font-weight: 400;
  }
  
  .upload-section {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  /* Upload Area */
  .upload-area {
    border: 3px dashed #cbd5e1;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    position: relative;
    overflow: hidden;
  }
  
  .upload-area::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .upload-area:hover::before,
  .upload-area.drag-over::before {
    opacity: 1;
  }
  
  .upload-area:hover,
  .upload-area.drag-over {
    border-color: #667eea;
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
  }
  
  .upload-content {
    position: relative;
    z-index: 1;
  }
  
  .upload-icon-container {
    margin-bottom: 2rem;
  }
  
  .upload-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: float 3s ease-in-out infinite;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  .upload-content h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 1.75rem;
  }
  
  .upload-content p {
    color: #64748b;
    margin-bottom: 2rem;
    font-size: 1.1rem;
  }
  
  .supported-formats {
    color: #94a3b8;
    font-size: 0.9rem;
    padding: 1rem;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 8px;
    display: inline-block;
  }
  
  /* File Preview */
  .file-preview {
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 16px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
  }
  
  .file-preview:hover {
    border-color: #cbd5e1;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  .file-info {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .file-icon-container {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .file-icon {
    font-size: 2rem;
    color: white;
  }
  
  .file-details h4 {
    margin: 0;
    color: #1e293b;
    font-weight: 600;
    font-size: 1.2rem;
  }
  
  .file-details p {
    margin: 0.5rem 0 0 0;
    color: #64748b;
    font-size: 1rem;
  }
  
  .remove-btn {
    margin-left: auto;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }
  
  .remove-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  }
  
  .upload-actions {
    text-align: center;
  }
  
  .upload-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .upload-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  .upload-btn:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }
  
  /* Processing Section */
  .processing-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .processing-header {
    margin-bottom: 3rem;
  }
  
  .processing-icon-container {
    margin-bottom: 2rem;
  }
  
  .processing-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .processing-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 2rem;
  }
  
  .processing-header p {
    color: #64748b;
    font-size: 1.2rem;
  }
  
  .progress-container {
    position: relative;
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .progress-bar {
    width: 100%;
    height: 12px;
    background: #e2e8f0;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2, #4facfe);
    border-radius: 20px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
  }
  
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
  
  .progress-text {
    position: absolute;
    top: -35px;
    right: 0;
    font-weight: 600;
    color: #1e293b;
    font-size: 1.1rem;
    background: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .processing-details {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }
  
  .detail-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #64748b;
    font-size: 0.95rem;
  }
  
  .detail-item i {
    color: #667eea;
    font-size: 1.3rem;
  }
  
  .detail-item.dev-mode {
    background: linear-gradient(135deg, #fff8e6 0%, #ffe7ba 100%);
    border: 1px solid #fbbf24;
    color: #854d0e;
    font-weight: 600;
  }
  
  .detail-item.dev-mode i {
    color: #d97706;
  }
  
  /* Completion Section */
  .completion-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .completion-icon-container {
    margin-bottom: 2rem;
  }
  
  .success-circle {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    color: white;
    font-size: 48px;
    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
    animation: successPulse 2s ease-in-out infinite;
  }
  
  @keyframes successPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  
  .completion-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.2rem;
  }
  
  .completion-header p {
    color: #64748b;
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto 3rem;
  }
  
  .completion-actions {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-content-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .view-content-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  /* Extraction Section */
  .extraction-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .extraction-header {
    margin-bottom: 3rem;
  }
  
  .extraction-icon-container {
    margin-bottom: 2rem;
  }
  
  .extraction-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .extraction-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 2rem;
  }
  
  .extraction-header p {
    color: #64748b;
    font-size: 1.2rem;
  }
  
  .extraction-details {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }
  
  /* Policy Review Section */
  .policy-review-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .review-header {
    margin-bottom: 3rem;
  }
  
  .review-icon-container {
    margin-bottom: 2rem;
  }
  
  .review-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.2rem;
  }
  
  .review-header p {
    color: #64748b;
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto 3rem;
  }
  
  .policy-summary {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin-bottom: 3rem;
    flex-wrap: wrap;
  }
  
  .summary-card {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    min-width: 200px;
    transition: all 0.3s ease;
  }
  
  .summary-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  }
  
  .summary-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
  }
  
  .summary-content h4 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 2rem;
  }
  
  .summary-content p {
    margin: 0.5rem 0 0 0;
    color: #64748b;
    font-weight: 500;
  }
  
  .review-actions {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-policies-btn, .upload-another-btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
  }
  
  .view-policies-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .view-policies-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  .upload-another-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .upload-another-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  /* Status Messages */
  .status-message {
    margin-top: 2rem;
    padding: 1.5rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 500;
    font-size: 1rem;
  }
  
  .status-message.success {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #065f46;
    border: 2px solid #10b981;
  }
  
  .status-message.error {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    color: #991b1b;
    border: 2px solid #ef4444;
  }
  
  /* Content Viewer Modal */
  .content-viewer-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
  }
  
  .content-viewer-container {
    background-color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }
  
  .content-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  .content-viewer-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #64748b;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .close-btn:hover {
    background: #e2e8f0;
    color: #1e293b;
    transform: scale(1.1);
  }
  
  .content-viewer-body {
    flex-grow: 1;
    overflow-y: auto;
    padding: 2rem;
    max-height: 70vh;
  }
  
  .search-box {
    margin-bottom: 2rem;
  }
  
  .search-box input {
    width: 100%;
    padding: 1rem 1.5rem;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #f8fafc;
  }
  
  .search-box input:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }
  
  .section-list {
    max-height: calc(70vh - 120px);
    overflow-y: auto;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
  }
  
  .section-item {
    border-bottom: 1px solid #e2e8f0;
  }
  
  .section-item:last-child {
    border-bottom: none;
  }
  
  .section-header {
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background-color: #f8fafc;
    transition: all 0.3s ease;
  }
  
  .section-header:hover {
    background-color: #f1f5f9;
  }
  
  .section-checkbox {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 600;
    color: #1e293b;
  }
  
  .section-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: #667eea;
  }
  
  .section-content {
    padding: 1rem 2rem 1.5rem 4rem;
    background-color: white;
  }
  
  .subsection-item {
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  
  .subsection-item:hover {
    background-color: #f8fafc;
  }
  
  .subsection-checkbox {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #475569;
    font-weight: 500;
  }
  
  .subsection-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #667eea;
  }
  
  .content-viewer-footer {
    padding: 2rem;
    border-top: 2px solid #e2e8f0;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  .select-all-btn, .deselect-all-btn, .save-selection-btn {
    padding: 0.875rem 1.5rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
  }
  
  .select-all-btn, .deselect-all-btn {
    background-color: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
  }
  
  .select-all-btn:hover, .deselect-all-btn:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
  }
  
  .save-selection-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
  
  .save-selection-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }
  
  /* Policy Extractor Modal */
  .policy-extractor-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
  }
  
  .policy-extractor-container {
    background-color: white;
    border-radius: 20px;
    width: 95%;
    max-width: 1400px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }
  
  .policy-extractor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  .policy-extractor-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }
  
  .policy-extractor-body {
    flex-grow: 1;
    overflow: hidden;
    padding: 2rem;
  }
  
  .policy-table-container {
    height: 100%;
    overflow: auto;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
  }
  
  .policy-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
  }
  
  .policy-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 1rem;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .policy-table td {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 300px;
    word-wrap: break-word;
    vertical-align: top;
  }
  
  .policy-table tr:hover {
    background-color: #f8fafc;
  }
  
  .policy-table tr:nth-child(even) {
    background-color: #fafbfc;
  }
  
  .policy-table tr:nth-child(even):hover {
    background-color: #f1f5f9;
  }
  
  /* No policies message */
  .no-policies-message {
    padding: 3rem;
    text-align: center;
    color: #64748b;
    background: #f8fafc;
    border-radius: 12px;
    border: 2px dashed #e2e8f0;
  }
  
  .no-policies-message p {
    font-size: 1.1rem;
    font-weight: 500;
    margin: 0;
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .upload-framework-container {
      padding: 1rem;
    }
    
    .step-indicator {
      flex-direction: column;
      gap: 1rem;
    }
    
    .step-divider {
      width: 2px;
      height: 40px;
      margin: 0;
    }
    
    .header h1 {
      font-size: 2rem;
    }
    
    .upload-section {
      padding: 2rem 1.5rem;
    }
    
    .processing-details,
    .extraction-details {
      flex-direction: column;
      gap: 1rem;
    }
    
    .policy-summary {
      flex-direction: column;
      align-items: center;
    }
    
    .completion-actions,
    .review-actions {
      flex-direction: column;
      align-items: center;
    }
    
    .content-viewer-footer {
      flex-direction: column;
    }
    
    .policy-table {
      font-size: 0.875rem;
    }
    
    .policy-table th,
    .policy-table td {
      padding: 1rem 0.5rem;
    }
  }
  
  .dev-quick-access {
    margin-top: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, #fff8e6 0%, #ffe7ba 100%);
    border: 1px dashed #fbbf24;
    border-radius: 10px;
    display: inline-block;
  }
  
  .load-sample-btn {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  }
  
  .load-sample-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(249, 115, 22, 0.4);
  }
  
  .dev-note {
    margin-top: 0.75rem;
    color: #854d0e;
    font-style: italic;
  }
  
  .dev-cleanup-note {
    margin-top: 0.75rem;
    padding: 0.5rem;
    border-left: 3px solid #3b82f6;
    background-color: #eff6ff;
    color: #1e40af;
    font-size: 0.85rem;
    text-align: left;
  }
  
  .dev-cleanup-note code {
    background-color: #dbeafe;
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-family: monospace;
  }
  
  /* Add this to the style section */
  .global-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    max-width: 400px;
    z-index: 2000;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    animation: slideIn 0.3s ease-out;
  }
  
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  .global-notification.success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-left: 4px solid #047857;
  }
  
  .notification-content {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    color: white;
  }
  
  .notification-content i {
    font-size: 1.2rem;
    margin-right: 0.75rem;
    margin-top: 0.2rem;
  }
  
  .notification-message {
    flex: 1;
    font-size: 0.95rem;
    white-space: pre-line;
  }
  
  .notification-close {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    padding: 0.25rem;
    font-size: 1rem;
    transition: all 0.2s ease;
  }
  
  .notification-close:hover {
    color: white;
    transform: scale(1.1);
  }
  
  /* Expandable rows */
  .expanded-row {
    background-color: #f1f5f9 !important;
  }
  
  .detail-row {
    background-color: #f8fafc;
  }
  
  .policy-details-container {
    padding: 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  .policy-details-section {
    margin-bottom: 1rem;
  }
  
  .policy-details-section h4 {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }
  
  .detail-content {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 0.95rem;
    color: #1e293b;
  }
  
  .policy-details-section .control-content {
    grid-column: 1 / -1;
    white-space: pre-line;
  }
  
  .control-content ul {
    margin: 0;
    padding-left: 1.5rem;
  }
  
  .control-content li {
    margin-bottom: 0.5rem;
  }
  
  /* Control field should span entire width */
  .policy-details-section:nth-child(3) {
    grid-column: 1 / -1;
  }
  
  /* Policy Edit Modal */
  .policy-edit-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1100;
    backdrop-filter: blur(8px);
  }
  
  .policy-edit-container {
    background-color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 900px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }
  
  .policy-edit-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  .policy-edit-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }
  
  .policy-edit-actions {
    display: flex;
    gap: 1rem;
  }
  
  .policy-edit-body {
    padding: 2rem;
    overflow-y: auto;
    max-height: calc(90vh - 90px);
  }
  
  .policy-field {
    margin-bottom: 1.5rem;
  }
  
  .policy-field label {
    display: block;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }
  
  .policy-field input,
  .policy-field textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
  }
  
  .policy-field input:focus,
  .policy-field textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  /* Action Buttons */
  .edit-btn, .view-btn, .save-btn, .save-all-btn {
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    font-size: 0.875rem;
    border: none;
  }
  
  .view-btn {
    background: #f8fafc;
    color: #1e293b;
    border: 1px solid #e2e8f0;
  }
  
  .view-btn:hover {
    background: #f1f5f9;
    transform: translateY(-1px);
  }
  
  .edit-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }
  
  .edit-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }
  
  .save-btn, .save-all-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }
  
  .save-btn:hover, .save-all-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  }
  
  .save-all-btn {
    margin-right: 1rem;
  }
  
  .policy-actions {
    display: flex;
    align-items: center;
  }
  
  .actions-cell {
    display: flex;
    gap: 0.5rem;
  }
  
  .control-cell {
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* Expandable rows */
  
  /* Policy Details Section Styles (Step 6) */
  .policy-details-section {
    padding: 2rem;
  }
  
  .details-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .details-header h3 {
    color: #1e293b;
    margin-bottom: 0.5rem;
    font-weight: 700;
    font-size: 1.8rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .details-header p {
    color: #64748b;
    font-size: 1.1rem;
  }
  
  .details-tabs {
    display: flex;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .tab {
    padding: 1rem 2rem;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
  }
  
  .tab:hover {
    color: #1e293b;
  }
  
  .tab.active {
    color: #667eea;
  }
  
  .tab.active::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #667eea, #764ba2);
  }
  
  .form-container {
    background: #f8fafc;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }
  
  .form-row {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
  }
  
  .form-group {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .form-group label {
    font-weight: 600;
    color: #475569;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }
  
  .form-group input,
  .form-group textarea {
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    background: white;
    transition: all 0.3s ease;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  .form-group textarea {
    min-height: 100px;
    resize: vertical;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
  }
  
  .save-btn, 
  .cancel-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
  }
  
  .save-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  }
  
  .save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  }
  
  .cancel-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
  }
  
  .cancel-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
  }
  
  .edit-details-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
  }
  
  .edit-details-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
  }
  
  .extracted-policies-table {
    margin-bottom: 2rem;
    max-height: 500px;
    overflow-y: auto;
    border-radius: 8px;
    border: 2px solid #e2e8f0;
  }
  
  /* Responsive Styles for Policy Details */
  @media (max-width: 768px) {
    .form-row {
      flex-direction: column;
      gap: 1rem;
    }
    
    .details-tabs {
      flex-direction: column;
      border-bottom: none;
    }
    
    .tab {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #e2e8f0;
    }
    
    .tab.active::after {
      display: none;
    }
    
    .tab.active {
      background: #f1f5f9;
      border-left: 3px solid #667eea;
    }
  }
  
  /* Add these styles to the end of the existing <style> section */
  
  /* Unified Content Container for Step 6 */
  .unified-content-container {
    display: flex;
    gap: 2rem;
    margin-top: 2rem;
  }
  
  .forms-panel {
    flex: 1;
    min-width: 300px;
    max-width: 600px;
  }
  
  .policies-panel {
    flex: 2;
    min-width: 500px;
  }
  
  .form-section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .form-section-title h4 {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
  }
  
  .policies-count {
    background: #f1f5f9;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #64748b;
  }
  
  .form-section-header {
    margin-bottom: 1rem;
  }
  
  .form-section-header h5 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #334155;
    margin: 0;
  }
  
  .basic-form,
  .additional-form {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
  }
  
  .policy-info-actions,
  .policies-actions {
    margin-top: 1.5rem;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }
  
  /* Search box for policies */
  .extracted-policies-table .search-box {
    margin-bottom: 1rem;
  }
  
  .extracted-policies-table .search-box input {
    width: 100%;
    padding: 0.8rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
  }
  
  .extracted-policies-table .search-box input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  /* Responsive styles for the unified view */
  @media (max-width: 1200px) {
    .unified-content-container {
      flex-direction: column;
    }
    
    .forms-panel,
    .policies-panel {
      max-width: 100%;
    }
  }
  
  .three-column-layout {
    display: flex;
    gap: 2rem;
  }
  
  .form-section {
    flex: 1;
    min-width: 300px;
    max-width: 600px;
  }
  
  .section-header {
    text-align: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .section-header h4 {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1e293b;
  }
  
  .form-container {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
  }
  
  .form-row.date-row {
    display: flex;
    gap: 1rem;
  }
  
  .form-group.date-group {
    flex: 1;
  }
  
  .form-group.date-group label {
    font-weight: 600;
    color: #475569;
  }
  
  .form-group.date-group input[type="date"] {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
  }
  
  .form-group.date-group input[type="date"]:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  .form-actions.policy-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .save-btn.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  .save-btn.primary-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  .secondary-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .secondary-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  .form-section.framework-form {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
  }
  
  .form-section.policy-form {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
  }
  
  .form-section.extracted-form {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
  }
  
  .form-container.search-box {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .search-box input[type="text"] {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
  }
  
  .search-box input[type="text"]:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  .search-icon {
    color: #667eea;
    font-size: 1.2rem;
  }
  
  .policy-count {
    background: #f1f5f9;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #64748b;
  }
  
  .form-section.extracted-form .form-container {
    max-height: 500px;
    overflow-y: auto;
  }
  
  .form-section.extracted-form .form-container .policy-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
  }
  
  .form-section.extracted-form .form-container .policy-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 1rem;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .form-section.extracted-form .form-container .policy-table td {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 300px;
    word-wrap: break-word;
    vertical-align: top;
  }
  
  .form-section.extracted-form .form-container .policy-table tr:hover {
    background-color: #f8fafc;
  }
  
  .form-section.extracted-form .form-container .policy-table tr:nth-child(even) {
    background-color: #fafbfc;
  }
  
  .form-section.extracted-form .form-container .policy-table tr:nth-child(even):hover {
    background-color: #f1f5f9;
  }
  
  .form-section.extracted-form .form-container .no-policies-message {
    padding: 3rem;
    text-align: center;
    color: #64748b;
    background: #f8fafc;
    border-radius: 12px;
    border: 2px dashed #e2e8f0;
  }
  
  .form-section.extracted-form .form-container .no-policies-message p {
    font-size: 1.1rem;
    font-weight: 500;
    margin: 0;
  }
  
  /* Update CSS in the existing <style> section by organizing related properties */
  
  /* Three-column layout for policy details */
  .three-column-layout {
    display: grid;
    grid-template-columns: 1fr 1fr 2fr; /* Wider right column for policy extraction table */
    gap: 1.5rem;
    margin-top: 1.5rem;
  }
  
  /* Base styles for all form sections */
  .form-section {
    display: flex;
    flex-direction: column;
    margin-bottom: 1.5rem;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
  }
  
  /* Section headers */
  .section-header {
    background: #f8fafc;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .section-header h4 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
  
  .policy-count {
    background: rgba(99, 102, 241, 0.1);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #6366f1;
  }
  
  /* Form containers */
  .form-container {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
    background: #ffffff;
  }
  
  /* Form fields and inputs */
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  .form-group label {
    display: block;
    font-weight: 600;
    font-size: 0.875rem;
    color: #475569;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
  }
  
  .form-group input[type="text"],
  .form-group input[type="number"],
  .form-group input[type="date"],
  .form-group textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.2s ease;
    background: #ffffff;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }
  
  .form-group textarea {
    min-height: 100px;
    resize: vertical;
  }
  
  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.25rem;
  }
  
  .form-row .form-group {
    flex: 1;
    margin-bottom: 0;
  }
  
  .form-row.date-row {
    display: flex;
    gap: 1rem;
  }
  
  /* Search box styling */
  .search-box {
    position: relative;
    margin-bottom: 1rem;
  }
  
  .search-box input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
    background: #ffffff;
  }
  
  .search-box .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 1rem;
  }
  
  /* Table styles */
  .extracted-policies-table {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 1.5rem;
  }
  
  .policy-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: white;
  }
  
  .policy-table th {
    background: #6366f1;
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 500;
    font-size: 0.875rem;
    position: sticky;
    top: 0;
    z-index: 10;
    text-transform: uppercase;
  }
  
  .policy-table th:first-child {
    border-top-left-radius: 8px;
  }
  
  .policy-table th:last-child {
    border-top-right-radius: 8px;
  }
  
  .policy-table td {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
    font-size: 0.875rem;
    line-height: 1.5;
    vertical-align: middle;
  }
  
  .policy-table tr:last-child td {
    border-bottom: none;
  }
  
  .policy-table .control-id-col {
    width: 12%;
  }
  
  .policy-table .policy-name-col {
    width: 20%;
  }
  
  .policy-table .control-col {
    width: 40%;
  }
  
  .policy-table .related-col {
    width: 18%;
  }
  
  .policy-table .actions-col {
    width: 10%;
    text-align: center;
  }
  
  .policy-table tr:hover {
    background-color: #f8fafc;
  }
  
  .policy-table tr.expanded-row {
    background-color: #f1f5f9;
  }
  
  .control-cell {
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .actions-cell {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .action-btn {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .view-btn.action-btn {
    background-color: #eef2ff;
    color: #6366f1;
  }
  
  .view-btn.action-btn:hover {
    background-color: #c7d2fe;
  }
  
  .edit-btn.action-btn {
    background-color: #ecfdf5;
    color: #10b981;
  }
  
  .edit-btn.action-btn:hover {
    background-color: #d1fae5;
  }
  
  /* Detail row styling */
  .detail-row {
    background-color: #f8fafc;
  }
  
  .policy-details-container {
    padding: 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  .policy-details-section {
    margin-bottom: 1rem;
  }
  
  .policy-details-section h4 {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .detail-content {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 0.875rem;
    color: #334155;
  }
  
  .policy-details-section .control-content {
    grid-column: 1 / -1;
    white-space: pre-line;
  }
  
  .control-content ul {
    margin: 0;
    padding-left: 1.5rem;
  }
  
  .control-content li {
    margin-bottom: 0.5rem;
  }
  
  /* Button styles */
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .primary-btn, .secondary-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
  }
  
  .primary-btn {
    background: #6366f1;
    color: white;
    border: none;
    box-shadow: 0 2px 5px rgba(99, 102, 241, 0.2);
  }
  
  .primary-btn:hover {
    background: #4f46e5;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
  }
  
  .secondary-btn {
    background: white;
    color: #64748b;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  }
  
  .secondary-btn:hover {
    background: #f8fafc;
    color: #334155;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  /* No policies message */
  .no-policies-message {
    padding: 3rem;
    text-align: center;
    color: #64748b;
    background: #f8fafc;
    border-radius: 8px;
    border: 2px dashed #e2e8f0;
  }
  
  .no-policies-message p {
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
  }
  
  /* Responsive styles */
  @media (max-width: 1400px) {
    .three-column-layout {
      grid-template-columns: 1fr 1fr;
    }
    
    .form-section.extracted-form {
      grid-column: span 2;
    }
  }
  
  @media (max-width: 1000px) {
    .three-column-layout {
      grid-template-columns: 1fr;
    }
    
    .form-section.extracted-form {
      grid-column: span 1;
    }
    
    .form-section {
      max-width: 100%;
    }
  }
  
  /* Three-section vertical layout for policy details */
  .three-column-layout {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    margin-top: 1.5rem;
    width: 100%;
  }
  
  /* Make each form section full width */
  .form-section {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 1.5rem;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    max-width: none; /* Remove max-width limitation */
  }
  
  /* Form containers */
  .form-container {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
    background: #ffffff;
    width: 100%;
  }
  
  /* Make inputs and form groups fill more width */
  .form-group {
    margin-bottom: 1.25rem;
    width: 100%;
  }
  
  /* Ensure all the form groups get proper width */
  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.25rem;
    width: 100%;
  }
  
  /* Make the extracted policies table wider */
  .extracted-policies-table {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 1.5rem;
    width: 100%;
  }
  
  /* Ensure the table uses all available space */
  .policy-table {
    width: 100%;
    table-layout: fixed; /* This helps with column width distribution */
  }
  
  /* Dynamic Forms Layout */
  .dynamic-forms-layout {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    width: 100%;
  }
  
  .form-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
  }
  
  .form-section:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
  
  .framework-form {
    border-left: 4px solid #10b981;
  }
  
  .policy-form {
    border-left: 4px solid #6366f1;
  }
  
  .sub-policy-form {
    border-left: 4px solid #f59e0b;
  }
  
  .section-header {
    display: flex;
    justify-content: between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f1f5f9;
  }
  
  .section-header h4 {
    color: #1e293b;
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
  }
  
  .policy-count {
    background: #f1f5f9;
    color: #64748b;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .form-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-group label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.875rem;
    transition: all 0.2s ease;
    background: #fafafa;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #6366f1;
    background: white;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  
  .date-row {
    grid-template-columns: 1fr 1fr;
  }
  
  .file-upload-container {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .file-upload-container input[type="file"] {
    display: none;
  }
  
  .file-upload-btn {
    background: #6366f1;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;
  }
  
  .file-upload-btn:hover {
    background: #4f46e5;
    transform: translateY(-1px);
  }
  
  .file-name {
    color: #10b981;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .sub-policy-actions {
    display: flex;
    justify-content: flex-start;
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }
  
  .add-sub-policy-btn {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
  }
  
  .add-sub-policy-btn:hover {
    background: #059669;
    transform: translateY(-1px);
  }
  
  .remove-sub-policy-btn {
    background: #ef4444;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
  }
  
  .remove-sub-policy-btn:hover {
    background: #dc2626;
    transform: translateY(-1px);
  }
  
  .form-actions-global {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 2rem;
    padding: 2rem;
    background: #f8fafc;
    border-radius: 16px;
    border: 2px dashed #cbd5e1;
  }
  
  .save-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }
  
  .save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  }
  
  .reset-btn {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(100, 116, 139, 0.3);
  }
  
  .reset-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(100, 116, 139, 0.4);
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }
    
    .form-actions-global {
      flex-direction: column;
    }
    
    .sub-policy-actions {
      flex-direction: column;
    }
  }
  
  /* Policy Section Group Styling */
  .policy-section-group {
    margin-bottom: 2rem;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  .policy-section-group .policy-form {
    margin-bottom: 1.5rem;
    border: 2px solid #3b82f6;
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  }
  
  .policy-section-group .sub-policy-form {
    margin-left: 2rem;
    margin-bottom: 1rem;
    border: 2px solid #10b981;
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  }
  
  .policy-section-group .sub-policy-form .section-header h4 {
    color: #065f46;
  }
  
  .policy-section-group .policy-form .section-header h4 {
    color: #1e40af;
  }
  
  /* Responsive design for smaller screens */
  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }
    
    .date-row {
      grid-template-columns: 1fr;
    }
    
    .file-upload-container {
      flex-direction: column;
      align-items: stretch;
    }
    
    .add-sub-policy-btn,
    .remove-sub-policy-btn {
      width: 100%;
      margin-top: 1rem;
    }
    
    .form-actions-global {
      flex-direction: column;
      gap: 1rem;
    }
    
    .form-actions-global .save-btn,
    .form-actions-global .reset-btn {
      width: 100%;
    }
  }
  
  /* Compliance Forms Styles */
  .compliance-form {
    background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
    border: 2px solid #4a90e2;
    border-radius: 12px;
    margin-top: 1.5rem;
  }
  
  .compliance-form .section-header {
    background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .compliance-form .section-header h4 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }
  
  .add-compliance-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .add-compliance-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
  
  .compliance-container {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .compliance-item {
    background: white;
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }
  
  .compliance-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
  }
  
  .compliance-header {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e1e8ed;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .compliance-letter {
    background: #4a90e2;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
  }
  
  .compliance-title {
    flex: 1;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .remove-compliance-btn {
    background: #dc3545;
    color: white;
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .remove-compliance-btn:hover {
    background: #c82333;
    transform: scale(1.1);
  }
  
  .compliance-form-container {
    padding: 1.5rem;
  }
  
  .compliance-form-container .form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background-color: white;
  }
  
  .compliance-form-container .form-group select:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
  }
  
  .compliance-form-container .form-group select option {
    padding: 0.5rem;
  }
  
  /* Status-based styling for select */
  .compliance-form-container .form-group select[value="completed"] {
    border-color: #28a745;
    background-color: #f8fff9;
  }
  
  .compliance-form-container .form-group select[value="in-progress"] {
    border-color: #ffc107;
    background-color: #fffdf5;
  }
  
  .compliance-form-container .form-group select[value="pending"] {
    border-color: #6c757d;
    background-color: #f8f9fa;
  }
  
  .compliance-form-container .form-group select[value="not-applicable"] {
    border-color: #dc3545;
    background-color: #fff5f5;
  }
  
  /* Responsive design for compliance forms */
  @media (max-width: 768px) {
    .compliance-form .section-header {
      flex-direction: column;
      align-items: stretch;
      text-align: center;
    }
    
    .compliance-header {
      flex-direction: column;
      text-align: center;
      gap: 0.5rem;
    }
    
    .compliance-letter {
      align-self: center;
    }
    
    .add-compliance-btn {
      width: 100%;
      justify-content: center;
    }
  }
  
  /* Enhanced hierarchical styling */
  .policy-section-group {
    border-left: 4px solid #6366f1;
    margin-bottom: 2.5rem;
  }
  
  .sub-policy-form {
    margin-left: 1.5rem;
    border-left: 4px solid #10b981;
  }
  
  .compliance-form {
    margin-left: 3rem;
    border-left: 4px solid #4a90e2;
  }
  
  /* Connection lines to show hierarchy */
  .policy-section-group:before,
  .sub-policy-form:before,
  .compliance-form:before {
    content: '';
    position: absolute;
    left: -20px;
    top: 0;
    height: 20px;
    width: 20px;
    border-bottom-left-radius: 20px;
    border-left: 2px solid #e2e8f0;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .or-divider {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 2rem 0;
    padding: 1rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .divider-line {
    flex: 1;
    height: 2px;
    background: #e2e8f0;
  }
  
  .divider-text {
    padding: 0 1rem;
    font-size: 0.9rem;
    color: #64748b;
    font-weight: 500;
  }
  
  .default-data-section {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .default-data-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .default-icon-container {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
  }
  
  .default-icon {
    font-size: 2rem;
  }
  
  .load-default-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  .load-default-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  .load-default-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  .isLoadingDefault {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* Add this congratulations modal component */
  .congratulations-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(8px);
    animation: fadeIn 0.3s ease-out;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  .congratulations-container {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 20px;
    width: 90%;
    max-width: 600px;
    padding: 3rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    animation: scaleIn 0.5s ease-out;
  }
  
  @keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }
  
  .congratulations-header {
    margin-bottom: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .congratulations-icon-container {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
    color: white;
    font-size: 48px;
    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
    animation: successPulse 2s ease-in-out infinite;
  }
  
  @keyframes successPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3); }
    50% { transform: scale(1.05); box-shadow: 0 20px 60px rgba(16, 185, 129, 0.5); }
  }
  
  .congratulations-header h2 {
    color: #10b981;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .congratulations-message {
    color: #374151;
    font-size: 1.25rem;
    font-weight: 500;
    margin: 0;
  }
  
  .congratulations-content {
    margin-bottom: 2rem;
  }
  
  .congratulations-content p {
    color: #6b7280;
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  
  .congratulations-actions {
    margin-top: 1rem;
  }
  
  .ok-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }
  
  .ok-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  }
  </style> 
  