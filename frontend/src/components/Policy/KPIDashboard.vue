<template>
  <div class="Policy-kpi-kpi-dashboard">
    <div class="Policy-kpi-dashboard-header">
      <h1>Policy KPI Dashboard</h1>
      <button class="Policy-kpi-refresh-button" @click="fetchKPIData" :class="{ 'Policy-kpi-loading': loading }">
        <i class="fas fa-sync-alt"></i>
        Refresh
      </button>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="Policy-kpi-loading-state">
      <div class="Policy-kpi-loader"></div>
      <p>Loading KPI data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="Policy-kpi-error-state">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchKPIData" class="Policy-kpi-retry-button">
        <i class="fas fa-redo"></i> Retry
      </button>
    </div>

    <!-- Content -->
    <div v-else class="Policy-kpi-dashboard-content">
      <div class="Policy-kpi-kpi-section">
        <!-- First Row of KPI Cards -->
        <div class="Policy-kpi-kpi-row">
          <!-- Active Policies KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-file-alt"></i>
              </div>
              <h3>Active Policies</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-kpi-visualization">
                <div class="Policy-kpi-circular-progress"
                  :style="{
                    '--progress-color': getProgressColor,
                    '--progress-value': progressPercentage * 3.6 + 'deg'
                  }"
                >
                  <div class="Policy-kpi-circular-progress-inner">
                    <div class="Policy-kpi-kpi-value">{{ kpiData.active_policies || 0 }}</div>
                    <div class="Policy-kpi-kpi-label">Active</div>
                  </div>
                </div>
                <div class="Policy-kpi-kpi-details">
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Total Policies</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Total number of policies in the system"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ kpiData.total_policies || 0 }}</span>
                  </div>
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Active Rate</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Percentage of total policies that are currently active"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ getUtilizationRate }}%</span>
                  </div>
                  <div class="Policy-kpi-trend-section">
                    <div class="Policy-kpi-trend-header">
                      <span class="Policy-kpi-trend-label">12 Month Trend</span>
                      <span class="Policy-kpi-trend-indicator" :class="trendDirection">
                        <i :class="[
                          'fas',
                          trendDirection === 'up' ? 'fa-arrow-up' : 
                          trendDirection === 'down' ? 'fa-arrow-down' : 
                          'fa-minus'
                        ]"></i>
                      </span>
                    </div>
                    <div class="Policy-kpi-sparkline-container">
                      <canvas id="trendChart"></canvas>
                    </div>
                  </div>
                  <div class="Policy-kpi-detail-item Policy-kpi-status-breakdown">
                    <div class="Policy-kpi-status-title">Status Breakdown</div>
                    <div class="Policy-kpi-status-row">
                      <span class="Policy-kpi-status-label">
                        <span class="Policy-kpi-status-dot Policy-kpi-active"></span>
                        Active
                      </span>
                      <span class="Policy-kpi-status-value">{{ kpiData.active_policies || 0 }}</span>
                    </div>
                    <div class="Policy-kpi-status-row">
                      <span class="Policy-kpi-status-label">
                        <span class="Policy-kpi-status-dot Policy-kpi-inactive"></span>
                        Inactive
                      </span>
                      <span class="Policy-kpi-status-value">{{ getInactivePolicies }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policy Acknowledgement Rate KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <h3>Policy Acknowledgement Rate</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-acknowledgement-table">
                <div class="Policy-kpi-table-header">
                  <span>Policy Name</span>
                  <span>Acknowledgement Rate</span>
                </div>
                <div class="Policy-kpi-table-body">
                  <template v-if="kpiData.top_acknowledged_policies">
                    <div v-for="policy in kpiData.top_acknowledged_policies" 
                         :key="policy.policy_id" 
                         class="Policy-kpi-table-row">
                      <div class="Policy-kpi-policy-info">
                        <span class="Policy-kpi-policy-name">{{ policy.policy_name }}</span>
                        <div class="Policy-kpi-policy-stats">
                          <span class="Policy-kpi-acknowledged-count">{{ policy.acknowledged_count }}</span>
                          <span class="Policy-kpi-total-users">/ {{ policy.total_users }}</span>
                        </div>
                      </div>
                      <div class="Policy-kpi-progress-container">
                        <div class="Policy-kpi-progress-bar">
                          <div class="Policy-kpi-progress-fill" 
                               :style="{ width: policy.acknowledgement_rate + '%' }"
                               :class="getAcknowledgementClass(policy.acknowledgement_rate)">
                          </div>
                        </div>
                        <span class="Policy-kpi-progress-text">{{ policy.acknowledgement_rate }}%</span>
                      </div>
                    </div>
                  </template>
                  <div v-else class="Policy-kpi-no-data">
                    No acknowledgement data available
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policy Coverage Rate KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-chart-bar"></i>
              </div>
              <h3>Policy Coverage Rate</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-coverage-container">
                <div class="Policy-kpi-coverage-overview">
                  <div class="Policy-kpi-overall-coverage">
                    <div class="Policy-kpi-overall-label">Average Coverage</div>
                    <div class="Policy-kpi-overall-value">{{ kpiData.coverage_metrics?.overall_coverage_rate || 0 }}%</div>
                  </div>
                </div>
                <div class="Policy-kpi-coverage-bars">
                  <div v-for="dept in kpiData.coverage_metrics?.department_coverage || []" 
                       :key="dept.department" 
                       class="Policy-kpi-coverage-bar-row">
                    <div class="Policy-kpi-bar-header">
                      <span class="Policy-kpi-department-name">{{ dept.department }}</span>
                      <span class="Policy-kpi-department-value">{{ dept.coverage_rate }}%</span>
                    </div>
                    <div class="Policy-kpi-bar-container">
                      <div class="Policy-kpi-bar-background"></div>
                      <div class="Policy-kpi-bar-fill" 
                           :style="{ 
                             width: dept.coverage_rate + '%',
                             backgroundColor: getCoverageColor(dept.coverage_rate)
                           }">
                      </div>
                    </div>
                    <div class="Policy-kpi-department-policies">{{ dept.total_policies }} policies</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Second Row of KPI Cards -->
        <div class="Policy-kpi-kpi-row">
          <!-- Policy Revision Rate KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-sync"></i>
              </div>
              <h3>Policy Revision Rate</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-kpi-visualization">
                <div class="Policy-kpi-donut-chart-container">
                  <canvas ref="revisionDonutChart"></canvas>
                  <div class="Policy-kpi-donut-center-text">
                    <div class="Policy-kpi-kpi-value">{{ (kpiData.revision_rate || 0).toFixed(2) }}%</div>
                    <div class="Policy-kpi-kpi-label">Revised</div>
                  </div>
                </div>
                <div class="Policy-kpi-kpi-details">
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Revised Policies</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Number of policies that have been revised"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ kpiData.revised_policies || 0 }}</span>
                  </div>
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Unchanged Policies</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Number of policies that have not been revised"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ unchangedPolicies }}</span>
                  </div>
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Time Period</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Time period for revision rate calculation"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ kpiData.measurement_period || 'Last Quarter' }}</span>
                  </div>
                  <button 
                    @click="showRevisedPolicies = true" 
                    class="Policy-kpi-drill-down-button"
                    v-if="kpiData.revised_policies > 0"
                  >
                    <i class="fas fa-list"></i>
                    View Revised Policies
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Average Policy Approval Time KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-clock"></i>
              </div>
              <h3>Average Policy Approval Time</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-kpi-visualization">
                <div class="Policy-kpi-approval-time-chart-container">
                  <canvas ref="approvalTimeChart"></canvas>
                </div>
                <div class="Policy-kpi-kpi-details">
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Overall Average</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Average time taken to approve policies"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">{{ kpiData.approval_time_metrics?.overall_average || 0 }} days</span>
                  </div>
                  <div class="Policy-kpi-detail-item">
                    <div class="Policy-kpi-detail-info">
                      <span class="Policy-kpi-detail-label">Measurement Period</span>
                      <i class="fas fa-info-circle Policy-kpi-info-icon" title="Time period for approval time calculation"></i>
                    </div>
                    <span class="Policy-kpi-detail-value">Last 12 Months</span>
                  </div>
                  <div class="Policy-kpi-trend-section">
                    <div class="Policy-kpi-trend-header">
                      <span class="Policy-kpi-trend-label">Monthly Trend</span>
                      <span class="Policy-kpi-trend-indicator" :class="approvalTimeTrendDirection">
                        <i :class="[
                          'fas',
                          approvalTimeTrendDirection === 'up' ? 'fa-arrow-up' : 
                          approvalTimeTrendDirection === 'down' ? 'fa-arrow-down' : 
                          'fa-minus'
                        ]"></i>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Policy Compliance KPI Card -->
          <div class="Policy-kpi-kpi-card">
            <div class="Policy-kpi-kpi-header">
              <div class="Policy-kpi-kpi-icon">
                <i class="fas fa-tasks"></i>
              </div>
              <h3>Policy Compliance Status</h3>
            </div>
            <div class="Policy-kpi-kpi-body">
              <div class="Policy-kpi-compliance-container">
                <div class="Policy-kpi-policy-selector">
                  <label for="policySelect">Select Policy:</label>
                  <select v-model="selectedPolicyId" @change="fetchComplianceData" id="policySelect" class="Policy-kpi-policy-dropdown">
                    <option value="">-- Select a Policy --</option>
                    <option v-for="policy in availablePolicies" :key="policy.PolicyId" :value="policy.PolicyId">
                      {{ policy.PolicyName }}
                    </option>
                  </select>
                </div>
                
                <div v-if="complianceLoading" class="Policy-kpi-compliance-loading">
                  <div class="Policy-kpi-small-loader"></div>
                  <p>Loading compliance data...</p>
                </div>
                
                <div v-else-if="complianceError" class="Policy-kpi-compliance-error">
                  <i class="fas fa-exclamation-triangle"></i>
                  <p>{{ complianceError }}</p>
                </div>
                
                <div v-else-if="complianceData && complianceData.policy_name" class="Policy-kpi-compliance-content">
                  <div class="Policy-kpi-compliance-overview">
                    <div class="Policy-kpi-policy-name">{{ complianceData.policy_name }}</div>
                    <div class="Policy-kpi-total-items">Total Items: {{ complianceData.total_compliance_items }}</div>
                  </div>
                  
                  <div class="Policy-kpi-compliance-chart">
                    <!-- Simple visible bar chart -->
                    <div class="Policy-kpi-simple-bar-chart">
                      <div class="Policy-kpi-chart-title">Compliance Distribution</div>
                      <div class="Policy-kpi-horizontal-bars">
                        <div class="Policy-kpi-chart-bar">
                          <div class="Policy-kpi-bar-info">
                            <span class="Policy-kpi-bar-name">✓ Fully Complied</span>
                            <span class="Policy-kpi-bar-percentage">{{ complianceData.compliance_stats?.fully_complied?.count || 0 }} ({{ complianceData.compliance_stats?.fully_complied?.percentage || 0 }}%)</span>
                          </div>
                          <div class="Policy-kpi-bar-track">
                            <div class="Policy-kpi-bar-progress Policy-kpi-green" 
                                 :style="{ width: (complianceData.compliance_stats?.fully_complied?.percentage || 0) + '%' }">
                            </div>
                          </div>
                        </div>
                        
                        <div class="Policy-kpi-chart-bar">
                          <div class="Policy-kpi-bar-info">
                            <span class="Policy-kpi-bar-name">△ Partially Complied</span>
                            <span class="Policy-kpi-bar-percentage">{{ complianceData.compliance_stats?.partially_complied?.count || 0 }} ({{ complianceData.compliance_stats?.partially_complied?.percentage || 0 }}%)</span>
                          </div>
                          <div class="Policy-kpi-bar-track">
                            <div class="Policy-kpi-bar-progress Policy-kpi-orange" 
                                 :style="{ width: (complianceData.compliance_stats?.partially_complied?.percentage || 0) + '%' }">
                            </div>
                          </div>
                        </div>
                        
                        <div class="Policy-kpi-chart-bar">
                          <div class="Policy-kpi-bar-info">
                            <span class="Policy-kpi-bar-name">✗ Not Complied</span>
                            <span class="Policy-kpi-bar-percentage">{{ complianceData.compliance_stats?.not_complied?.count || 0 }} ({{ complianceData.compliance_stats?.not_complied?.percentage || 0 }}%)</span>
                          </div>
                          <div class="Policy-kpi-bar-track">
                            <div class="Policy-kpi-bar-progress Policy-kpi-red" 
                                 :style="{ width: (complianceData.compliance_stats?.not_complied?.percentage || 0) + '%' }">
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="Policy-kpi-no-policy-selected">
                  <i class="fas fa-info-circle"></i>
                  <p>Please select a policy to view compliance statistics</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Revised Policies Modal -->
    <div v-if="showRevisedPolicies" class="Policy-kpi-modal">
      <div class="Policy-kpi-modal-content">
        <div class="Policy-kpi-modal-header">
          <h2>Revised Policies</h2>
          <button @click="showRevisedPolicies = false" class="Policy-kpi-close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="Policy-kpi-modal-body">
          <div class="Policy-kpi-revised-policies-stats">
            <div class="Policy-kpi-stat-item">
              <span class="Policy-kpi-stat-label">Total Revisions:</span>
              <span class="Policy-kpi-stat-value">{{ kpiData.total_revisions }}</span>
            </div>
            <div class="Policy-kpi-stat-item">
              <span class="Policy-kpi-stat-label">Policies with Multiple Revisions:</span>
              <span class="Policy-kpi-stat-value">{{ kpiData.policies_with_multiple_revisions }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

export default {
  name: 'KPIDashboard',
  setup() {
    const kpiData = ref({})
    const loading = ref(true)
    const error = ref(null)
    const revisionChart = ref(null)
    const revisionDonutChart = ref(null)
    const trendChart = ref(null)
    const showRevisedPolicies = ref(false)
    const approvalTimeChart = ref(null)
    
    // Compliance KPI related refs
    const selectedPolicyId = ref('')
    const availablePolicies = ref([])
    const complianceData = ref({})
    const complianceLoading = ref(false)
    const complianceError = ref(null)

    const progressPercentage = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return Math.min((kpiData.value.active_policies / kpiData.value.total_policies) * 100, 100)
    })

    const getUtilizationRate = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return Math.round((kpiData.value.active_policies / kpiData.value.total_policies) * 100)
    })

    const getInactivePolicies = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return kpiData.value.total_policies - (kpiData.value.active_policies || 0)
    })

    const getProgressColor = computed(() => {
      const rate = kpiData.value.revision_rate || 0
      if (rate > 66) return '#66BB6A'  // Green for high revision rate
      if (rate > 33) return '#FFA726'   // Orange for medium revision rate
      return '#2196F3'                  // Blue for low revision rate
    })

    const getAcknowledgementClass = (rate) => {
      if (rate >= 80) return 'high'
      if (rate >= 50) return 'medium'
      return 'low'
    }

    const unchangedPolicies = computed(() => {
      if (!kpiData.value.total_policies || !kpiData.value.revised_policies) return 0
      return kpiData.value.total_policies - kpiData.value.revised_policies
    })

    const getCoverageColor = (rate) => {
      if (rate >= 90) return '#66BB6A'  // Green for high coverage
      if (rate >= 70) return '#FFA726'   // Orange for medium coverage
      return '#EF5350'                   // Red for low coverage
    }

    const getBarWidth = (percentage) => {
      const value = percentage || 0
      // Ensure minimum width for visibility, but scale properly
      if (value === 0) return '0%'
      return Math.max(value, 5) + '%'
    }

    const approvalTimeTrendDirection = computed(() => {
      if (!kpiData.value?.approval_time_metrics?.monthly_averages) return 'neutral'
      const averages = kpiData.value.approval_time_metrics.monthly_averages
      if (averages.length < 2) return 'neutral'
      const first = averages[0].average_time
      const last = averages[averages.length - 1].average_time
      return last > first ? 'up' : last < first ? 'down' : 'neutral'
    })

    const updateRevisionChart = async () => {
      // Wait for the next DOM update
      await nextTick()
      
      // Check if the canvas element exists
      if (!revisionDonutChart.value) {
        console.warn('Canvas element not found')
        return
      }

      // Destroy existing chart if it exists
      if (revisionChart.value) {
        revisionChart.value.destroy()
      }

      try {
        const ctx = revisionDonutChart.value.getContext('2d')
        revisionChart.value = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Revised', 'Unchanged'],
            datasets: [{
              data: [
                kpiData.value.revised_policies || 0,
                unchangedPolicies.value
              ],
              backgroundColor: ['#2196F3', '#e9ecef'],
              borderWidth: 0,
              borderRadius: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || ''
                    const value = context.raw || 0
                    const total = kpiData.value.total_policies || 0
                    const percentage = ((value / total) * 100).toFixed(1)
                    return `${label}: ${value} (${percentage}%)`
                  }
                }
              }
            }
          }
        })
      } catch (err) {
        console.error('Error creating chart:', err)
      }
    }

    const updateApprovalTimeChart = async () => {
      await nextTick()
      
      const ctx = document.querySelector('.Policy-kpi-approval-time-chart-container canvas')
      if (!ctx) return

      // Destroy existing chart if it exists
      if (approvalTimeChart.value instanceof Chart) {
        approvalTimeChart.value.destroy()
      }

      const monthlyData = kpiData.value?.approval_time_metrics?.monthly_averages || []
      
      try {
        approvalTimeChart.value = new Chart(ctx, {
          type: 'line',
          data: {
            labels: monthlyData.map(item => item.month),
            datasets: [{
              label: 'Average Approval Time (days)',
              data: monthlyData.map(item => item.average_time),
              borderColor: '#2196F3',
              backgroundColor: 'rgba(33, 150, 243, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              fill: true,
              pointRadius: 4,
              pointHoverRadius: 6,
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                  title: (context) => {
                    return context[0].label
                  },
                  label: (context) => {
                    return `Average Time: ${context.raw} days`
                  }
                }
              }
            },
            scales: {
              x: {
                grid: {
                  display: false
                }
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Days'
                }
              }
            }
          }
        })
      } catch (err) {
        console.error('Error creating approval time chart:', err)
      }
    }

    // Watch for changes in kpiData and loading state
    watch([() => kpiData.value, loading], async ([newKpiData, isLoading]) => {
      if (!isLoading && !error.value && newKpiData) {
        try {
          await Promise.all([
            updateRevisionChart(),
            updateApprovalTimeChart()
          ])
        } catch (err) {
          console.error('Error updating charts:', err)
        }
      }
    }, { deep: true })



    // Clean up charts on component unmount
    onUnmounted(() => {
      if (approvalTimeChart.value instanceof Chart) {
        approvalTimeChart.value.destroy()
      }
      if (revisionChart.value instanceof Chart) {
        revisionChart.value.destroy()
      }
    })

    // Fetch available policies for the dropdown
    const fetchAvailablePolicies = async () => {
      try {
        const response = await axios.get('/api/policies/', {
          baseURL: 'http://localhost:8000',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        if (response.data && Array.isArray(response.data)) {
          availablePolicies.value = response.data
        }
      } catch (err) {
        console.error('Error fetching policies:', err)
      }
    }

    // Fetch compliance data for selected policy
    const fetchComplianceData = async () => {
      if (!selectedPolicyId.value) {
        complianceData.value = {}
        return
      }

      complianceLoading.value = true
      complianceError.value = null

      try {
        const response = await axios.get(`/api/policies/${selectedPolicyId.value}/compliance-stats/`, {
          baseURL: 'http://localhost:8000',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        complianceData.value = response.data
      } catch (err) {
        console.error('Error fetching compliance data:', err)
        complianceError.value = err.response?.data?.error || 'Failed to load compliance data'
      } finally {
        complianceLoading.value = false
      }
    }



    const fetchKPIData = async () => {
      loading.value = true
      error.value = null

      try {
        console.log('Fetching KPI data...')
        const response = await axios.get('/api/policy-kpis/', {
          baseURL: 'http://localhost:8000',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        console.log('KPI data received:', response.data)
        
        if (!response.data || typeof response.data !== 'object') {
          throw new Error('Invalid response format')
        }
        
        kpiData.value = response.data
        
        // Update chart after data is loaded
        await updateRevisionChart()
      } catch (err) {
        console.error('Detailed error:', err.response?.data || err.message)
        error.value = `Failed to load KPI data: ${err.response?.data?.error || err.message}`
      } finally {
        loading.value = false
      }
    }

    const sparklineData = computed(() => {
      if (!kpiData.value?.active_policies_trend) return []
      return kpiData.value.active_policies_trend.map(item => item.count).reverse()
    })

    const sparklineLabels = computed(() => {
      if (!kpiData.value?.active_policies_trend) return []
      return kpiData.value.active_policies_trend.map(item => item.month).reverse()
    })

    const trendDirection = computed(() => {
      if (!sparklineData.value.length) return 'neutral'
      const first = sparklineData.value[0]
      const last = sparklineData.value[sparklineData.value.length - 1]
      return last > first ? 'up' : last < first ? 'down' : 'neutral'
    })

    const updateTrendChart = async () => {
      await nextTick()
      
      if (trendChart.value) {
        trendChart.value.destroy()
      }

      const ctx = document.getElementById('trendChart')
      if (!ctx) return

      trendChart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: sparklineLabels.value,
          datasets: [{
            data: sparklineData.value,
            borderColor: getProgressColor.value,
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                title: (context) => {
                  return context[0].label
                },
                label: (context) => {
                  return `Active Policies: ${context.raw}`
                }
              }
            }
          },
          scales: {
            x: {
              display: false
            },
            y: {
              display: false,
              beginAtZero: true
            }
          }
        }
      })
    }

    watch(() => kpiData.value, () => {
      updateTrendChart()
    })

    onMounted(async () => {
      await Promise.all([fetchKPIData(), fetchAvailablePolicies()])
    })

    return {
      kpiData,
      loading,
      error,
      fetchKPIData,
      progressPercentage,
      getProgressColor,
      getUtilizationRate,
      getInactivePolicies,
      unchangedPolicies,
      revisionDonutChart,
      showRevisedPolicies,
      getCoverageColor,
      sparklineData,
      sparklineLabels,
      trendDirection,
      getAcknowledgementClass,
      approvalTimeChart,
      approvalTimeTrendDirection,
      // Compliance KPI related
      selectedPolicyId,
      availablePolicies,
      complianceData,
      complianceLoading,
      complianceError,
      fetchComplianceData,
      getBarWidth
    }
  }
}
</script>

<style scoped>
.Policy-kpi-kpi-dashboard {
  margin-left: 280px;
  padding: 1.5rem;
  background-color: #f8f9fa;
  min-height: 100vh;
  width: calc(100vw - 280px);
  max-width: calc(100vw - 280px);
  box-sizing: border-box;
  overflow-x: auto;
}

.Policy-kpi-dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0 1rem 1rem 0;
  border-bottom: 2px solid #e9ecef;
  width: 100%;
}

.Policy-kpi-dashboard-header h1 {
  font-size: 1.75rem;
  color: #2c3e50;
  margin: 0;
  font-weight: 600;
  text-align: left;
}

.Policy-kpi-refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2);
}

.Policy-kpi-refresh-button:hover {
  background-color: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
}

.Policy-kpi-refresh-button.Policy-kpi-loading {
  opacity: 0.8;
  cursor: not-allowed;
}

.Policy-kpi-refresh-button.Policy-kpi-loading i {
  animation: Policy-kpi-spin 1s linear infinite;
}

@keyframes Policy-kpi-spin {
  100% {
    transform: rotate(360deg);
  }
}

.Policy-kpi-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.Policy-kpi-loader {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2196F3;
  border-radius: 50%;
  animation: Policy-kpi-spin 1s linear infinite;
  margin-bottom: 1rem;
}

.Policy-kpi-error-state {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.Policy-kpi-error-state i {
  font-size: 2rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.Policy-kpi-retry-button {
  padding: 0.75rem 1.5rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem auto 0;
  font-size: 0.9rem;
}

.Policy-kpi-retry-button:hover {
  background-color: #1976D2;
  transform: translateY(-1px);
}

.Policy-kpi-dashboard-content {
  width: 100%;
  padding: 0 1rem;
}

.Policy-kpi-kpi-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.Policy-kpi-kpi-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  width: 100%;
  margin-bottom: 1.5rem;
}

.Policy-kpi-kpi-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 100%;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.Policy-kpi-kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.Policy-kpi-kpi-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.Policy-kpi-kpi-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(33, 150, 243, 0.1);
  border-radius: 8px;
}

.Policy-kpi-kpi-icon i {
  font-size: 1rem;
  color: #2196F3;
}

.Policy-kpi-kpi-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.Policy-kpi-kpi-body {
  padding: 1rem;
  flex: 1;
}

.Policy-kpi-kpi-visualization {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
  position: relative;
}

.Policy-kpi-circular-progress {
  position: relative;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: conic-gradient(
    var(--progress-color, #2196F3) var(--progress-value),
    #e9ecef var(--progress-value)
  );
}

.Policy-kpi-circular-progress-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 110px;
  height: 110px;
  background: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
}

.Policy-kpi-kpi-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 0.15rem;
  text-align: center;
  white-space: nowrap;
}

.Policy-kpi-kpi-label {
  font-size: 0.7rem;
  color: #6c757d;
  text-align: center;
}

.Policy-kpi-kpi-details {
  flex: 1;
  margin-left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.Policy-kpi-detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.Policy-kpi-detail-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.Policy-kpi-info-icon {
  color: #6c757d;
  font-size: 0.75rem;
  cursor: help;
}

.Policy-kpi-detail-label {
  font-size: 0.8rem;
  color: #6c757d;
}

.Policy-kpi-detail-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
}

.Policy-kpi-status-breakdown {
  flex-direction: column;
  gap: 0.75rem;
}

.Policy-kpi-status-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.Policy-kpi-status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.Policy-kpi-status-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
}

.Policy-kpi-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.Policy-kpi-status-dot.Policy-kpi-active {
  background-color: #2196F3;
}

.Policy-kpi-status-dot.Policy-kpi-inactive {
  background-color: #9e9e9e;
}

.Policy-kpi-status-value {
  font-weight: 600;
  color: #2c3e50;
}

.Policy-kpi-progress-bar {
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.Policy-kpi-progress {
  height: 100%;
  background-color: #2196F3;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.Policy-kpi-progress.medium {
  background-color: #FFA726;
}

.Policy-kpi-progress.high {
  background-color: #66BB6A;
}

.Policy-kpi-donut-chart-container {
  position: relative;
  width: 140px;
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.Policy-kpi-donut-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.Policy-kpi-drill-down-button {
  display: flex;
  align-items: center;
  gap: 0.1rem;
  padding: 0.18rem 0.4rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.68rem;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;
  margin-top: 0.25rem;
  min-height: 28px;
  max-width: 220px;
}

.Policy-kpi-drill-down-button:hover {
  background-color: #1976D2;
}

.Policy-kpi-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.Policy-kpi-modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.Policy-kpi-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.Policy-kpi-modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.Policy-kpi-close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
}

.Policy-kpi-close-button:hover {
  color: #2c3e50;
}

.Policy-kpi-modal-body {
  padding: 1.5rem;
}

.Policy-kpi-revised-policies-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.Policy-kpi-stat-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.Policy-kpi-stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.Policy-kpi-stat-value {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
}

.Policy-kpi-info-text {
  color: #6c757d;
  text-align: center;
  font-style: italic;
}

.Policy-kpi-coverage-container {
  padding: 0.5rem;
}

.Policy-kpi-coverage-overview {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.Policy-kpi-overall-coverage {
  text-align: center;
}

.Policy-kpi-overall-label {
  font-size: 0.7rem;
  color: #6c757d;
  margin-bottom: 0.15rem;
}

.Policy-kpi-overall-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.Policy-kpi-coverage-bars {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: 150px;
  overflow-y: auto;
  padding-right: 0.15rem;
}

.Policy-kpi-coverage-bar-row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.Policy-kpi-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.Policy-kpi-department-name {
  font-size: 0.7rem;
  color: #2c3e50;
  font-weight: 500;
}

.Policy-kpi-department-value {
  font-size: 0.7rem;
  color: #6c757d;
}

.Policy-kpi-bar-container {
  position: relative;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
}

.Policy-kpi-bar-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f5f5f5;
}

.Policy-kpi-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  transition: width 0.5s ease;
  min-width: 4px;
}

.Policy-kpi-department-policies {
  font-size: 0.65rem;
  color: #6c757d;
  text-align: right;
}

/* Custom scrollbar for coverage bars */
.Policy-kpi-coverage-bars::-webkit-scrollbar {
  width: 4px;
}

.Policy-kpi-coverage-bars::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.Policy-kpi-coverage-bars::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.Policy-kpi-coverage-bars::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.Policy-kpi-trend-section {
  margin-top: 0.35rem;
  padding-top: 0.35rem;
  border-top: 1px solid #eee;
}

.Policy-kpi-trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.15rem;
}

.Policy-kpi-trend-label {
  font-size: 0.7rem;
  color: #6c757d;
}

.Policy-kpi-trend-indicator {
  font-size: 0.65rem;
  padding: 0.1rem 0.25rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.1rem;
}

.Policy-kpi-trend-indicator.up {
  color: #28a745;
  background-color: rgba(40, 167, 69, 0.1);
}

.Policy-kpi-trend-indicator.down {
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.Policy-kpi-trend-indicator.neutral {
  color: #6c757d;
  background-color: rgba(108, 117, 125, 0.1);
}

.Policy-kpi-sparkline-container {
  height: 40px;
  width: 100%;
  margin-top: 0.5rem;
  position: relative;
}

/* Make sure the sparkline is responsive */
.Policy-kpi-sparkline-container :deep(svg) {
  width: 100%;
  height: 100%;
}

/* Acknowledgement KPI Card Styles */
.Policy-kpi-acknowledgement-table {
  width: 100%;
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
}

.Policy-kpi-table-header {
  display: grid;
  grid-template-columns: 1fr auto;
  padding: 0.35rem 0.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.7rem;
}

.Policy-kpi-table-body {
  /* max-height: 150px; */
  /* overflow-y: auto; */
}

.Policy-kpi-table-row {
  display: grid;
  grid-template-columns: 1fr auto;
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
  transition: background-color 0.2s;
}

.Policy-kpi-table-row:hover {
  background-color: #f8f9fa;
}

.Policy-kpi-policy-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.Policy-kpi-policy-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.7rem;
}

.Policy-kpi-policy-stats {
  display: flex;
  gap: 0.15rem;
  font-size: 0.65rem;
  color: #6c757d;
}

.Policy-kpi-acknowledged-count {
  font-weight: 500;
  color: #2c3e50;
}

.Policy-kpi-total-users {
  color: #6c757d;
}

.Policy-kpi-progress-container {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 100px;
}

.Policy-kpi-progress-bar {
  flex: 1;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.Policy-kpi-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.Policy-kpi-progress-fill.low {
  background-color: #dc3545;
}

.Policy-kpi-progress-fill.medium {
  background-color: #ffc107;
}

.Policy-kpi-progress-fill.high {
  background-color: #28a745;
}

.Policy-kpi-progress-text {
  min-width: 35px;
  text-align: right;
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.7rem;
}

.Policy-kpi-no-data {
  padding: 24px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

@media (max-width: 1200px) {
  .Policy-kpi-kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .Policy-kpi-dashboard-header h1 {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .Policy-kpi-kpi-dashboard {
    padding: 1rem;
  }

  .Policy-kpi-dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .Policy-kpi-dashboard-header h1 {
    font-size: 1.25rem;
  }
  
  .Policy-kpi-refresh-button {
    align-self: flex-end;
  }

  .Policy-kpi-kpi-row {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .Policy-kpi-kpi-visualization {
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.5rem;
  }

  .Policy-kpi-kpi-details {
    margin-left: 0;
    width: 100%;
  }

  .Policy-kpi-circular-progress {
    width: 100px;
    height: 100px;
  }

  .Policy-kpi-circular-progress-inner {
    width: 80px;
    height: 80px;
  }

  .Policy-kpi-circular-progress .Policy-kpi-kpi-value {
    font-size: 1.1rem;
  }

  .Policy-kpi-donut-chart-container {
    width: 100px;
    height: 100px;
  }

  .Policy-kpi-approval-time-chart-container {
    height: 140px;
  }
}

.Policy-kpi-approval-time-chart-container {
  width: 100%;
  height: 200px;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Compliance KPI Styles */
.Policy-kpi-compliance-container {
  padding: 0.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.Policy-kpi-policy-selector {
  margin-bottom: 0.75rem;
}

.Policy-kpi-policy-selector label {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.Policy-kpi-policy-dropdown {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 0.8rem;
  background-color: white;
  color: #2c3e50;
}

.Policy-kpi-policy-dropdown:focus {
  border-color: #2196F3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.Policy-kpi-compliance-loading, .Policy-kpi-compliance-error, .Policy-kpi-no-policy-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
  flex: 1;
  color: #6c757d;
}

.Policy-kpi-small-loader {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #2196F3;
  border-radius: 50%;
  animation: Policy-kpi-spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

.Policy-kpi-compliance-error {
  color: #dc3545;
}

.Policy-kpi-compliance-error i {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.Policy-kpi-compliance-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.Policy-kpi-compliance-overview {
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.Policy-kpi-policy-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.Policy-kpi-total-items {
  font-size: 0.75rem;
  color: #6c757d;
}

.Policy-kpi-compliance-chart {
  height: 200px;
  margin-bottom: 0.75rem;
  background: white;
  border-radius: 4px;
  padding: 0.5rem;
  position: relative;
  border: 1px solid #e0e0e0;
}

.Policy-kpi-compliance-chart canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.Policy-kpi-compliance-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.Policy-kpi-compliance-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.Policy-kpi-stat-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: bold;
}

.Policy-kpi-fully-complied .Policy-kpi-stat-icon {
  background-color: #4CAF50;
  color: white;
}

.Policy-kpi-partially-complied .Policy-kpi-stat-icon {
  background-color: #FF9800;
  color: white;
}

.Policy-kpi-not-complied .Policy-kpi-stat-icon {
  background-color: #F44336;
  color: white;
}

.Policy-kpi-stat-details {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.Policy-kpi-stat-count {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1;
}

.Policy-kpi-stat-label {
  font-size: 0.7rem;
  color: #6c757d;
  line-height: 1;
}

.Policy-kpi-stat-percentage {
  font-size: 0.65rem;
  color: #6c757d;
  font-style: italic;
}

/* Simple Bar Chart with guaranteed visibility */
.Policy-kpi-simple-bar-chart {
  padding: 1rem;
  width: 100%;
  background: white;
  border-radius: 4px;
}

.Policy-kpi-chart-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}

.Policy-kpi-horizontal-bars {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.Policy-kpi-chart-bar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.Policy-kpi-bar-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.Policy-kpi-bar-name {
  font-size: 0.8rem;
  font-weight: 500;
  color: #2c3e50;
}

.Policy-kpi-bar-percentage {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6c757d;
}

.Policy-kpi-bar-track {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  border: 1px solid #dee2e6;
}

.Policy-kpi-bar-progress {
  height: 100%;
  border-radius: 10px;
  transition: width 1.5s ease-in-out;
  position: relative;
  min-width: 4px;
}

.Policy-kpi-bar-progress.Policy-kpi-green {
  background: linear-gradient(90deg, #28a745, #34ce57);
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.Policy-kpi-bar-progress.Policy-kpi-orange {
  background: linear-gradient(90deg, #fd7e14, #ff922b);
  box-shadow: 0 2px 4px rgba(253, 126, 20, 0.3);
}

.Policy-kpi-bar-progress.Policy-kpi-red {
  background: linear-gradient(90deg, #dc3545, #e55865);
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
}
</style>