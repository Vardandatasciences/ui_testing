<template>
  <div class="dashboard-container">
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="fetchDashboardData" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <span>Loading dashboard data...</span>
    </div>

    <div v-else>
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Policy Dashboard</h2>
      <div class="dashboard-actions">
          <button class="action-btn" @click="fetchDashboardData" title="Refresh"><i class="fas fa-sync-alt"></i></button>
          <button class="action-btn" title="Download"><i class="fas fa-download"></i></button>
        <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Policy</button> -->
      </div>
    </div>
    
    <!-- Summary Tabs -->
    <div class="summary-tabs">
      <button 
        class="summary-tab" 
        :class="{ active: activeTab === 'approval' }"
        @click="activeTab = 'approval'"
      >
        <div class="summary-tab-icon">
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="summary-tab-content">
          <div class="summary-tab-label">Approval Rate</div>
          <div class="summary-tab-value">{{ dashboardData.approval_rate }}%</div>
          <div class="summary-tab-trend positive">
            <i class="fas fa-arrow-up"></i>
            Based on {{ dashboardData.total_policies }} policies
          </div>
        </div>
      </button>
      
      <button 
        class="summary-tab" 
        :class="{ active: activeTab === 'policies' }"
        @click="activeTab = 'policies'"
      >
        <div class="summary-tab-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="summary-tab-content">
          <!-- Show Active Policies as Main Value -->
          <div class="summary-tab-label">Active Policies</div>
          <div class="summary-tab-value">{{ dashboardData.active_policies }}</div>

          <!-- Total Policies as Trend below -->
          <div class="summary-tab-trend neutral">
            <i class="fas fa-layer-group"></i>
            {{ dashboardData.total_policies }} total policies
          </div>
        </div>
      </button>


      
      <button 
        class="summary-tab" 
        :class="{ active: activeTab === 'subpolicies' }"
        @click="activeTab = 'subpolicies'"
      >
        <div class="summary-tab-icon">
          <i class="fas fa-clipboard-list"></i>
        </div>
        <div class="summary-tab-content">
          <div class="summary-tab-label">Total SubPolicies</div>
          <div class="summary-tab-value">{{ dashboardData.total_subpolicies }}</div>
          <div class="summary-tab-trend">
            <i class="fas fa-arrows-alt-h"></i>
            Across all policies
          </div>
        </div>
      </button>
      
      <button 
        class="summary-tab" 
        :class="{ active: activeTab === 'approval_time' }"
        @click="activeTab = 'approval_time'"
      >
        <div class="summary-tab-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="summary-tab-content">
          <div class="summary-tab-label">Avg. Approval Time</div>
          <div class="summary-tab-value">{{ avgApprovalTime }} days</div>
          <div class="summary-tab-trend">
            <i class="fas fa-history"></i>
            Time to approve
          </div>
        </div>
      </button>
    </div>

    <!-- Main Row: Asset Performance and Recent Activity -->
    <div class="dashboard-main-row dashboard-main-row-3col" style="display: flex; width: 100%;">
      <!-- Left: Asset Performance Card -->
      <div class="dashboard-main-col asset-performance-col" style="width: 70%;">
        <div class="chart-card tabbed-chart-card">
          <div class="card-header">
            <div class="header-left">
                <span>Policy Analytics</span>
              <div class="axis-selectors">
                <select v-model="selectedXAxis" class="axis-select">
                  <option disabled value="">Select X Axis</option>
                  <option value="framework">Framework</option>
                  <option value="policy">Policy</option>
                  <option value="subpolicy">SubPolicy</option>
                </select>
                <select v-model="selectedYAxis" class="axis-select">
                  <option disabled value="">Select Y Axis</option>
                    <option value="activeInactive">Active/Inactive</option>
                    <option value="category">Category Distribution</option>
                    <option value="status">Status Distribution</option>
                    <option value="createdByDate">Creation Date Distribution</option>
                    <option value="createdByName">Created By Distribution</option>
                    <option value="department">Department Distribution</option>
                </select>
              </div>
            </div>
            <div class="chart-tabs">
              <button
                v-for="tab in chartTypes"
                :key="tab.type"
                :class="['chart-tab-btn', { active: activeChart === tab.type }]"
                @click="activeChart = tab.type"
                :title="tab.label"
              >
                <i :class="tab.icon"></i>
              </button>
            </div>
          </div>
          <div class="chart-container">
            <LineChart v-if="activeChart === 'line'" :data="lineChartData" :options="lineChartOptions" />
            <Bar v-if="activeChart === 'bar'" :data="barChartData" :options="barChartOptions" />
            <Doughnut v-if="activeChart === 'doughnut'" :data="donutChartData" :options="donutChartOptions" />
            <Bar v-if="activeChart === 'horizontalBar'" :data="horizontalBarChartData" :options="horizontalBarChartOptions" />
          </div>
        </div>
      </div>
      
      <!-- Right: Recent Activity Card -->
      <div class="dashboard-main-col recent-activity-col" style="width: 30%;">
        <div class="activity-card">
          <div class="card-header">
            <h3>Recent Activity</h3>
            <button class="card-action"><i class="fas fa-ellipsis-v"></i></button>
          </div>
          <div class="activity-list">
              <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item">
                <div class="activity-icon">
                  <i class="fas fa-plus-circle"></i>
            </div>
              <div class="activity-content">
                  <div class="activity-title">Policy Activity</div>
                  <div class="activity-desc">{{ activity.PolicyName }}</div>
                  <div class="activity-meta">
                    <span class="activity-author">{{ activity.CreatedBy }}</span>
                    <span class="activity-time">{{ new Date(activity.CreatedDate).toLocaleDateString() }}</span>
              </div>
            </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import dashboardService from '@/services/dashboardService';
import { ref, reactive, watch, onMounted, nextTick } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar, Line as LineChart } from 'vue-chartjs'
import loanLogo from '../../assets/loan_logo1.svg'
import '@fortawesome/fontawesome-free/css/all.min.css'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'PolicyDashboard',
  components: {
    Doughnut,
    Bar,
    LineChart
  },
  setup() {
    const showPolicyDetails = ref(true)
    const selectedXAxis = ref('framework')
    const selectedYAxis = ref('category')
    const dashboardData = ref({
      total_policies: 0,
      total_subpolicies: 0,
      active_policies: 0,
      inactive_policies: 0,
      approval_rate: 0,
      policies: []
    })
    const recentActivity = ref([])
    const avgApprovalTime = ref(0)
    const statusDistribution = ref([])
    const reviewerWorkload = ref([])
    const loading = ref(true)
    const error = ref(null)
    const activeChart = ref('bar')
    const activeTab = ref('approval')

    // Fetch all dashboard data
    const fetchDashboardData = async () => {
      try {
        loading.value = true
        error.value = null

        const [
          summaryRes,
          statusRes,
          activityRes,
          approvalTimeRes,
          workloadRes
        ] = await Promise.all([
          dashboardService.getDashboardSummary(),
          dashboardService.getPolicyStatusDistribution(),
          dashboardService.getRecentPolicyActivity(),
          dashboardService.getAvgApprovalTime(),
          dashboardService.getReviewerWorkload()
        ])

        dashboardData.value = summaryRes.data
        statusDistribution.value = statusRes.data
        recentActivity.value = activityRes.data
        avgApprovalTime.value = approvalTimeRes.data.average_days
        reviewerWorkload.value = workloadRes.data

        // Update chart data with default values
        await updateChartData(selectedXAxis.value, selectedYAxis.value)
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        error.value = 'Failed to load dashboard data'
      } finally {
        loading.value = false
      }
    }

    const updateChartData = async (xAxis, yAxis) => {
      try {
        loading.value = true;
        const analyticsRes = await dashboardService.getPolicyAnalytics(xAxis, yAxis);
        const data = analyticsRes.data;
        
        // Extract labels and values with proper null handling
        const originalLabels = data.map(item => item.label || 'N/A');
        const displayLabels = data.map(item => {
          // Handle creator names
          if (yAxis === 'createdByName') {
            // Keep the original label which includes the count
            return item.label;
          }
          // Format category labels to be more readable
          if (yAxis === 'category') {
            return formatCategoryLabel(item.label || 'N/A');
          }
          return item.label || 'N/A';
        });
        
        const values = data.map(item => item.value || 0);
        
        // Force chart reactivity by creating new dataset objects
        donutChartData.labels = [...displayLabels];
        donutChartData.datasets = [{
          data: [...values],
          backgroundColor: displayLabels.map((_, i) => 
            `hsl(${(i * 360) / displayLabels.length}, 70%, 60%)`
          ),
          borderWidth: 0,
          hoverOffset: 5
        }];
        // Store original labels for tooltips
        donutChartData._originalLabels = [...originalLabels];

        barChartData.labels = [...displayLabels];
        barChartData.datasets = [{
          label: getYAxisLabel(yAxis),
          data: [...values],
          backgroundColor: displayLabels.map((_, i) => 
            `hsl(${(i * 360) / displayLabels.length}, 70%, 60%)`
          ),
          borderRadius: 4
        }];
        barChartData._originalLabels = [...originalLabels];

        horizontalBarChartData.labels = [...displayLabels];
        horizontalBarChartData.datasets = [{
          label: getYAxisLabel(yAxis),
          data: [...values],
          backgroundColor: displayLabels.map((_, i) => 
            `hsl(${(i * 360) / displayLabels.length}, 70%, 60%)`
          ),
          borderRadius: 6,
          barPercentage: 0.5,
          categoryPercentage: 0.7
        }];
        horizontalBarChartData._originalLabels = [...originalLabels];

        lineChartData.labels = [...displayLabels];
        lineChartData.datasets = [{
          label: getYAxisLabel(yAxis),
          data: [...values],
          fill: false,
          borderColor: '#4f6cff',
          tension: 0.4,
          pointBackgroundColor: '#4f6cff',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }];
        lineChartData._originalLabels = [...originalLabels];

        // Force chart update
        nextTick(() => {
          if (activeChart.value === 'line') lineChartData.datasets = [...lineChartData.datasets];
          if (activeChart.value === 'bar') barChartData.datasets = [...barChartData.datasets];
          if (activeChart.value === 'doughnut') donutChartData.datasets = [...donutChartData.datasets];
          if (activeChart.value === 'horizontalBar') horizontalBarChartData.datasets = [...horizontalBarChartData.datasets];
        });

      } catch (err) {
        console.error('Error updating chart data:', err);
        error.value = 'Failed to update chart data';
      } finally {
        loading.value = false;
      }
    };

    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], async ([newXAxis, newYAxis]) => {
      await updateChartData(newXAxis, newYAxis);
    }, { immediate: true });

    // Watch for chart type changes
    watch(activeChart, () => {
      nextTick(() => {
        updateChartData(selectedXAxis.value, selectedYAxis.value);
      });
    });

    const getYAxisLabel = (yAxis) => {
      switch(yAxis) {
        case 'activeInactive': return 'Active Items'
        case 'category': return 'Policy Categories'
        case 'status': return 'Status Distribution'
        case 'createdByDate': return 'Creation Date Distribution'
        case 'createdByName': return 'Created By Distribution'
        case 'department': return 'Department Distribution'
        default: return 'Value'
      }
    }

    // Chart tab logic
    const chartTypes = [
      { type: 'line', icon: 'fas fa-chart-line', label: 'Line' },
      { type: 'bar', icon: 'fas fa-chart-bar', label: 'Bar' },
      { type: 'doughnut', icon: 'fas fa-dot-circle', label: 'Donut' },
      { type: 'horizontalBar', icon: 'fas fa-align-left', label: 'Horizontal Bar' }
    ];
    
    // Create reactive chart data objects
    const lineChartData = reactive({
      labels: [],
      datasets: [{
        label: 'Policy Performance',
        data: [],
        fill: false,
        borderColor: '#4f6cff',
        tension: 0.4,
        pointBackgroundColor: '#4f6cff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    });
    
    const lineChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const dataIndex = context.dataIndex;
              // Use original label if available (for categories)
              let label = context.chart.data._originalLabels && 
                          context.chart.data._originalLabels[dataIndex] ? 
                          context.chart.data._originalLabels[dataIndex] : 
                          context.label || '';
                          
              const value = context.raw || 0;
              return `${label}: ${value}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            display: true,
            color: 'rgba(0,0,0,0.05)'
          },
          ticks: {
            font: { size: 11 }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: { size: 11 }
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
    
    const donutChartData = reactive({
      labels: [],
      datasets: [{
        data: [],
        backgroundColor: ['#4ade80', '#f87171', '#fbbf24'],
        borderWidth: 0,
        hoverOffset: 5
      }]
    });
    
    const donutChartOptions = {
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const dataIndex = context.dataIndex;
              // Use original label if available (for categories)
              let label = context.chart.data._originalLabels && 
                          context.chart.data._originalLabels[dataIndex] ? 
                          context.chart.data._originalLabels[dataIndex] : 
                          context.label || '';
                          
              const value = context.raw || 0;
              const dataset = context.dataset;
              const total = dataset.data.reduce((acc, val) => acc + val, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      },
      maintainAspectRatio: false,
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 1000,
        easing: 'easeOutCubic'
      }
    }
    
    const barChartData = reactive({
      labels: [],
      datasets: [{
        label: '',
        data: [],
        backgroundColor: [],
        borderRadius: 4
      }]
    });
    
    const barChartOptions = {
      plugins: { 
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const dataIndex = context.dataIndex;
              // Use original label if available (for categories)
              let label = context.chart.data._originalLabels && 
                          context.chart.data._originalLabels[dataIndex] ? 
                          context.chart.data._originalLabels[dataIndex] : 
                          context.label || '';
                          
              const value = context.raw || 0;
              return `${label}: ${value}`;
            }
          }
        }
      },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { 
          stacked: true, 
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } }
        },
        y: { 
          stacked: true, 
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }
    
    const horizontalBarChartData = reactive({
      labels: [],
      datasets: [{
        label: '',
        data: [],
        backgroundColor: [],
        borderRadius: 6,
        barPercentage: 0.5,
        categoryPercentage: 0.7
      }]
    });
    
    const horizontalBarChartOptions = {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const dataIndex = context.dataIndex;
              // Use original label if available (for categories)
              let label = context.chart.data._originalLabels && 
                          context.chart.data._originalLabels[dataIndex] ? 
                          context.chart.data._originalLabels[dataIndex] : 
                          context.label || '';
                          
              const value = context.raw || 0;
              return `${label}: ${value}`;
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } }
        }
      },
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }

    // Fetch data on component mount
    onMounted(() => {
      fetchDashboardData()
    })

    const formatCategoryLabel = (label) => {
      // For category labels which use PolicyType > PolicyCategory > PolicySubCategory format
      if (selectedYAxis.value === 'category' && label.includes(' > ')) {
        const parts = label.split(' > ');
        // If it's a full 3-part category, show just the last part with tooltip for full path
        if (parts.length === 3) {
          return parts[2]; // Return just the subcategory for display
        }
      }
      return label;
    };

    return {
      dashboardData,
      recentActivity,
      avgApprovalTime,
      loading,
      error,
      lineChartData,
      lineChartOptions,
      donutChartData,
      donutChartOptions,
      barChartData,
      barChartOptions,
      horizontalBarChartData,
      horizontalBarChartOptions,
      loanLogo,
      showPolicyDetails,
      chartTypes,
      activeChart,
      selectedXAxis,
      selectedYAxis,
      fetchDashboardData,
      activeTab
    }
  }
}
</script>

<style scoped>
@import './PolicyDashboard.css';

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4f6cff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 1rem;
  margin: 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.retry-btn {
  background-color: #b91c1c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background-color: #991b1b;
}

.chart-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.chart-tab-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #888;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}

.chart-tab-btn.active, .chart-tab-btn:hover {
  background: #eef2ff;
  color: #4f6cff;
}

.tabbed-chart-card {
  max-width: 900px;
  min-width: 480px;
  min-height: 300px;
  margin: 0 auto 32px auto;
  padding: 32px 32px 24px 32px;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  background: #fff;
}

.chart-performance-summary {
  margin-top: 18px;
  font-size: 1rem;
}

.dashboard-main-row {
  margin-top: 32px;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.activity-author {
  color: #4f6cff;
  font-weight: 500;
}
</style> 