<template>
  <div class="version-list-container">
    <div class="version-list-header">
      <h2 class="version-list-heading">Compliance Version List</h2>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-group">
        <label>Framework:</label>
        <select v-model="selectedFramework" @change="loadPolicies" class="select">
          <option value="">Select Framework</option>
          <option v-for="framework in frameworks" 
                  :key="framework.FrameworkId" 
                  :value="framework.FrameworkId">
            {{ framework.FrameworkName }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Policy:</label>
        <select v-model="selectedPolicy" @change="loadSubPolicies" :disabled="!selectedFramework" class="select">
          <option value="">Select Policy</option>
          <option v-for="policy in policies" 
                  :key="policy.PolicyId" 
                  :value="policy.PolicyId">
            {{ policy.PolicyName }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Sub Policy:</label>
        <select v-model="selectedSubPolicy" @change="loadCompliances" :disabled="!selectedPolicy" class="select">
          <option value="">Select Sub Policy</option>
          <option v-for="subPolicy in subPolicies" 
                  :key="subPolicy.SubPolicyId" 
                  :value="subPolicy.SubPolicyId">
            {{ subPolicy.SubPolicyName }}
          </option>
        </select>
      </div>

      <!-- Search Bar -->
      <div class="search-bar-container">
        <input
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          class="search-input"
          placeholder="Search..."
        />
        <button class="search-btn" @click="handleSearch">
          <svg height="20" width="20" viewBox="0 0 20 20" fill="none">
            <circle cx="9" cy="9" r="7" stroke="white" stroke-width="2"/>
            <line x1="14.2" y1="14.2" x2="18" y2="18" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Grouped Compliance Table -->
    <div class="table-container" v-if="groupedCompliances.length > 0">
      <div v-for="(group, groupIndex) in groupedCompliances" :key="groupIndex" class="compliance-group">
        <div class="group-header">
          <h3>Compliance ID: {{ group[0].Identifier }}</h3>
          <div class="group-description">{{ group[0].ComplianceItemDescription }}</div>
        </div>
        
        <div class="table-wrapper">
          <table class="compliance-table">
            <thead>
              <tr>
                <th>Version</th>
                <th>Status</th>
                <th>Active/Inactive</th>
                <th>Created By</th>
                <th>Created Date</th>
                <th>Previous Version</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="compliance in group" 
                  :key="compliance.ComplianceId"
                  :class="{ 'active-version': compliance.ActiveInactive === 'Active' }">
                <td>{{ compliance.ComplianceVersion }}</td>
                <td>{{ compliance.Status }}</td>
                <td>
                  <div class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :id="'toggle-' + compliance.ComplianceId"
                      :checked="compliance.ActiveInactive === 'Active'"
                      @change="toggleActiveStatus(compliance)"
                      :disabled="compliance.Status !== 'Approved'"
                    >
                    <label :for="'toggle-' + compliance.ComplianceId"></label>
                  </div>
                </td>
                <td>{{ compliance.CreatedByName || 'N/A' }}</td>
                <td>{{ formatDate(compliance.CreatedByDate) }}</td>
                <td>{{ getPreviousVersionDisplay(compliance) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else-if="selectedSubPolicy" class="no-data">
      No compliances found for the selected criteria
    </div>
    
    <!-- Deactivation Dialog -->
    <div v-if="showDeactivationDialog" class="deactivation-dialog-overlay">
      <div class="deactivation-dialog">
        <h3>Deactivate Compliance</h3>
        <p>Please provide a reason for deactivating this compliance:</p>
        <textarea 
          v-model="deactivationReason" 
          class="deactivation-reason-input"
          placeholder="Enter reason for deactivation">
        </textarea>
        <div class="deactivation-options">
          <label>
            <input type="checkbox" v-model="cascadeToPolicies">
            Apply to related policies
          </label>
          <div class="affected-count" v-if="cascadeToPolicies">
            {{ affectedPoliciesCount || 0 }} policies will be affected
          </div>
        </div>
        <div class="deactivation-actions">
          <button @click="cancelDeactivation" class="cancel-btn">Cancel</button>
          <button @click="submitDeactivation" class="submit-btn">OK</button>
        </div>
      </div>
    </div>
    
    <!-- Deactivation Confirmation Dialog -->
    <div v-if="showDeactivationConfirmation" class="deactivation-dialog-overlay">
      <div class="deactivation-dialog">
        <h3>Deactivation Request Submitted</h3>
        <p>Your request to deactivate this compliance item has been submitted successfully and is awaiting approval.</p>
        <p>The compliance will remain active until an approver reviews and accepts this request.</p>
        <div class="approval-info">
          <i class="fas fa-info-circle"></i>
          <span>You can check the status of this request in the Compliance Approver interface.</span>
        </div>
        <div class="deactivation-actions">
          <button @click="closeDeactivationConfirmation" class="submit-btn">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { complianceService } from '@/services/api';

export default {
  name: 'ComplianceVersionList',
  data() {
    return {
      frameworks: [],
      policies: [],
      subPolicies: [],
      compliances: [],
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      loading: false,
      searchQuery: '',
      showDeactivationDialog: false,
      deactivationReason: '',
      cascadeToPolicies: true,
      affectedPoliciesCount: 0,
      complianceToDeactivate: null,
      showDeactivationConfirmation: false
    }
  },
  computed: {
    groupedCompliances() {
      let filtered = this.compliances;
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(c =>
          (c.Identifier && c.Identifier.toLowerCase().includes(q)) ||
          (c.ComplianceItemDescription && c.ComplianceItemDescription.toLowerCase().includes(q))
        );
      }
      const groups = {};
      filtered.forEach(compliance => {
        if (!groups[compliance.Identifier]) {
          groups[compliance.Identifier] = [];
        }
        groups[compliance.Identifier].push(compliance);
      });
      // Sort each group by version number (descending)
      return Object.values(groups).map(group => {
        return group.sort((a, b) => {
          const versionA = parseFloat(a.ComplianceVersion);
          const versionB = parseFloat(b.ComplianceVersion);
          return versionB - versionA;
        });
      });
    }
  },
  mounted() {
    this.loadFrameworks();
  },
  methods: {
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getFrameworks();
        
        // Handle both response formats: direct array or success wrapper
        if (response.data.success) {
          this.frameworks = response.data.data;
        } else if (Array.isArray(response.data)) {
          this.frameworks = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
        }
      } catch (error) {
        console.error('Error loading frameworks:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadPolicies() {
      if (!this.selectedFramework) {
        this.policies = [];
        this.selectedPolicy = '';
        return;
      }
      try {
        this.loading = true;
        const response = await complianceService.getPolicies(this.selectedFramework);
        if (response.data.success) {
          this.policies = response.data.data;
        } else if (Array.isArray(response.data)) {
          this.policies = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
        }
        this.selectedPolicy = '';
        this.selectedSubPolicy = '';
      } catch (error) {
        console.error('Error loading policies:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies() {
      if (!this.selectedPolicy) {
        this.subPolicies = [];
        this.selectedSubPolicy = '';
        return;
      }
      try {
        this.loading = true;
        const response = await complianceService.getSubPolicies(this.selectedPolicy);
        if (response.data.success) {
          this.subPolicies = response.data.data;
        } else if (Array.isArray(response.data)) {
          this.subPolicies = response.data;
        } else {
          console.error('Unexpected response format:', response.data);
        }
        this.selectedSubPolicy = '';
      } catch (error) {
        console.error('Error loading subpolicies:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadCompliances() {
      if (!this.selectedSubPolicy) {
        this.compliances = [];
        return;
      }
      try {
        this.loading = true;
        console.log(`Loading compliances for subpolicy ID: ${this.selectedSubPolicy}`);
        
        // Use the compliance service instead of direct axios
        const response = await complianceService.getCompliancesBySubPolicy(this.selectedSubPolicy);
        console.log('Compliance API response:', response.data);
        
        if (response.data.success) {
          // Check the structure of the response data
          if (Array.isArray(response.data.data)) {
            // If it's a direct array or nested array - flatten it in case it's nested
            this.compliances = response.data.data.flat();
          } else if (response.data.compliances && Array.isArray(response.data.compliances)) {
            // If it's stored in a 'compliances' field
            this.compliances = response.data.compliances;
          } else {
            console.error('Unexpected data structure:', response.data);
            this.compliances = [];
          }
          
          // Debug: Check if PreviousComplianceVersionId is present in any compliance records
          if (this.compliances.length > 0) {
            console.log('First compliance record:', this.compliances[0]);
            console.log('PreviousComplianceVersionId exists:', 
              this.compliances.some(c => c.PreviousComplianceVersionId !== undefined));
            
            // Log all compliance keys to verify what's available
            console.log('Compliance record keys:', Object.keys(this.compliances[0]));
            
            // Adapt the previous version property if needed
            this.compliances = this.compliances.map(c => {
              // If PreviousVersionId exists but PreviousComplianceVersionId doesn't
              if (c.PreviousVersionId !== undefined && c.PreviousComplianceVersionId === undefined) {
                return {
                  ...c,
                  PreviousComplianceVersionId: c.PreviousVersionId
                };
              }
              return c;
            });
          } else {
            console.log('No compliances returned from API');
          }
        } else {
          console.error('Error in response:', response.data);
        }
      } catch (error) {
        console.error('Error loading compliances:', error);
      } finally {
        this.loading = false;
      }
    },
    async toggleActiveStatus(compliance) {
      if (compliance.Status !== 'Approved') {
        alert('Only approved compliances can be toggled');
        return;
      }
      
      // If trying to deactivate, show the deactivation dialog
      if (compliance.ActiveInactive === 'Active') {
        this.complianceToDeactivate = compliance;
        this.deactivationReason = '';
        this.cascadeToPolicies = true;
        this.showDeactivationDialog = true;
        // Reset the checkbox state to maintain consistency with actual status
        document.getElementById(`toggle-${compliance.ComplianceId}`).checked = true;
        return;
      }
      
      // Otherwise proceed with normal toggle for activation
      try {
        this.loading = true;
        const response = await complianceService.toggleComplianceVersion(compliance.ComplianceId);
        
        if (response.data.success) {
          await this.loadCompliances();
        } else {
          alert(response.data.message || 'Error toggling compliance status');
        }
      } catch (error) {
        console.error('Error toggling compliance status:', error);
        alert('Error toggling compliance status');
      } finally {
        this.loading = false;
      }
    },
    async submitDeactivation() {
      if (!this.complianceToDeactivate) return;
      
      if (!this.deactivationReason.trim()) {
        alert('Please provide a reason for deactivation');
        return;
      }
      
      try {
        this.loading = true;
        console.log('Submitting deactivation request for compliance:', this.complianceToDeactivate.ComplianceId);
        
        const response = await complianceService.deactivateCompliance(
          this.complianceToDeactivate.ComplianceId, 
          {
            reason: this.deactivationReason,
            cascade_to_policies: this.cascadeToPolicies,
            user_id: 1, // Default to admin user - in a real app, get from auth context
            reviewer_id: 2 // Default reviewer ID - should be configurable in a real app
          }
        );
        
        if (response.data.success) {
          this.showDeactivationDialog = false;
          
          // Show the confirmation dialog with enhanced information
          this.showDeactivationConfirmation = true;
          
          // Refresh the data to show pending status
          await this.loadCompliances();
          
          console.log('Deactivation request submitted successfully with approval ID:', response.data.approval_id);
        } else {
          alert(response.data.message || 'Error submitting deactivation request');
        }
      } catch (error) {
        console.error('Error submitting deactivation request:', error);
        const errorMessage = error.response?.data?.message || error.message || 'Error submitting deactivation request';
        alert(`Error: ${errorMessage}`);
      } finally {
        this.loading = false;
      }
    },
    cancelDeactivation() {
      this.showDeactivationDialog = false;
      this.complianceToDeactivate = null;
    },
    closeDeactivationConfirmation() {
      this.showDeactivationConfirmation = false;
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString();
    },
    getPreviousVersionDisplay(compliance) {
      if (!compliance.PreviousComplianceVersionId) return 'None';
      
      // Find the previous version in all compliances to get its version number
      const prevVersion = this.compliances.find(c => 
        c.ComplianceId === compliance.PreviousComplianceVersionId);
      
      if (prevVersion) {
        return `v${prevVersion.ComplianceVersion}`;
      }
      
      // If we can't find the previous version in the loaded compliances,
      // at least show the ID
      return `ID: ${compliance.PreviousComplianceVersionId}`;
    },
    handleSearch() {
      // Filtering is handled reactively in computed property
    }
  }
}
</script>

<style scoped>
@import './ComplianceVersioning.css';

/* Add styles for deactivation dialog */
.deactivation-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.deactivation-dialog {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.deactivation-dialog h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.deactivation-reason-input {
  width: 100%;
  min-height: 80px;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.deactivation-options {
  margin-bottom: 20px;
}

.affected-count {
  margin-top: 5px;
  font-size: 0.9em;
  color: #666;
}

.deactivation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 15px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  padding: 8px 15px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.approval-info {
  margin: 15px 0;
  padding: 10px 15px;
  background-color: #e8f0fe;
  border-left: 4px solid #4285f4;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.approval-info i {
  color: #4285f4;
  font-size: 18px;
}
</style> 