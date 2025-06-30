<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Auditor Dashboard</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Policy</button> -->
      </div>
    </div>
    
    <!-- Performance Summary Cards -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-clipboard-check"></i></div>
        <div class="summary-content">
          <div class="summary-label">Audit Completion Rate</div>
          <div class="summary-value">
            <span :class="{ 'positive': auditCompletionData.is_positive_change, 'negative': !auditCompletionData.is_positive_change }">
              {{ auditCompletionData.is_positive_change ? '+' : '-' }}{{ Math.abs(auditCompletionData.current_month_rate).toFixed(1) }}%
            </span> 
            <span class="period">this month</span>
          </div>
          <div class="summary-trend" :class="{ 'positive': auditCompletionData.is_positive_change, 'negative': !auditCompletionData.is_positive_change }">
            {{ auditCompletionData.is_positive_change ? '+' : '-' }}{{ Math.abs(auditCompletionData.change_in_rate).toFixed(2) }}% vs last month
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-tasks"></i></div>
        <div class="summary-content">
          <div class="summary-label">Total Audits</div>
          <div class="summary-value">{{ totalAuditsData.total_current_month }}</div>
          <div class="summary-trend" :class="{ 'positive': totalAuditsData.is_positive_change, 'negative': !totalAuditsData.is_positive_change }">
            {{ totalAuditsData.is_positive_change ? '+' : '-' }}{{ Math.abs(totalAuditsData.change_in_total) }} this month
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-hourglass-half"></i></div>
        <div class="summary-content">
          <div class="summary-label">Open Audits</div>
          <div class="summary-value">{{ openAuditsData.open_this_week }}</div>
          <div class="summary-trend" :class="{ 'positive': openAuditsData.is_improvement, 'negative': !openAuditsData.is_improvement }">
            {{ openAuditsData.is_improvement ? '+' : '-' }}{{ Math.abs(openAuditsData.change_in_open) }} since last week
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-check-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Completed Audits</div>
          <div class="summary-value">{{ completedAuditsData.this_week_count }}</div>
          <div class="summary-trend" :class="{ 'positive': completedAuditsData.is_improvement, 'negative': !completedAuditsData.is_improvement }">
            {{ completedAuditsData.is_improvement ? '+' : '' }}{{ completedAuditsData.change_in_completed }} this week
          </div>
        </div>
      </div>
    </div>

    <!-- Main Row: Asset Performance and Recent Activity -->
    <div class="dashboard-main-row dashboard-main-row-3col">
      <!-- Left: Asset Performance Card -->
      <div class="dashboard-main-col asset-performance-col">
        <div class="chart-card tabbed-chart-card">
          <div class="card-header">
            <span class="chart-title">Audit performance</span>
            
            <div class="chart-controls">
              <div class="axis-selectors">
                <select v-model="selectedXAxis" class="axis-select" :disabled="isLoading">
                  <option value="time">Time</option>
                  <option value="frameworks">Frameworks</option>
                  <option value="categories">Categories</option>
                  <option value="status">Status</option>
                </select>
                <select v-model="selectedYAxis" class="axis-select" :disabled="isLoading">
                  <option value="completion">Performance</option>
                  <option value="compliance">Compliance Rate</option>
                  <option value="findings">Finding Count</option>
                </select>
              </div>
              
              <div class="chart-tabs">
                <button 
                  v-for="tab in chartTypes"
                  :key="tab.type"
                  :class="['chart-tab-btn', { active: activeChart === tab.type }]"
                  @click="activeChart = tab.type"
                  :title="tab.label"
                  :disabled="isLoading"
                >
                  <i :class="tab.icon"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="chart-container">
            <div v-if="isLoading" class="chart-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Loading chart data...</span>
            </div>
            <LineChart v-else-if="activeChart === 'line'" :data="lineChartData" :options="lineChartOptions" />
            <Bar v-else-if="activeChart === 'bar'" :data="barChartData" :options="barChartOptions" />
            <Doughnut v-else-if="activeChart === 'doughnut'" :data="donutChartData" :options="donutChartOptions" />
            <Bar v-else-if="activeChart === 'horizontalBar'" :data="horizontalBarChartData" :options="horizontalBarChartOptions" />
          </div>
        </div>
      </div>

      <!-- Right: Recent Activity Card -->
      <div class="dashboard-main-col recent-activity-col">
        <div class="activity-card">
          <div class="card-header">
            <h3>Recent Audit Activity</h3>
            <button class="card-action" @click="fetchRecentActivities">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoadingActivities }"></i>
            </button>
          </div>
          <div v-if="isLoadingActivities && isEmpty(recentActivities)" class="activity-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading activities...</span>
          </div>
          <div v-else-if="isEmpty(filteredActivities)" class="activity-empty">
            <p>No recent activities found</p>
          </div>
          <div v-else class="activity-list">
            <div 
              v-for="(activity, index) in filteredActivities" 
              :key="index" 
              class="activity-item"
            >
              <div :class="['activity-icon', getActivityIconClass(activity.type)]">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title || 'Activity' }}</div>
                <div class="activity-desc">{{ activity.description || 'No description available' }}</div>
                <div class="activity-time">{{ activity.time_ago || 'Recently' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import '@fortawesome/fontawesome-free/css/all.min.css'
import axios from 'axios'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'AuditorDashboard',
  components: {
    Doughnut,
    Bar,
    LineChart: Line
  },
  setup() {
    // Loading state
    const isLoading = ref(false)
    const isLoadingActivities = ref(false)

    // Audit Completion Rate data
    const auditCompletionData = reactive({
      current_month_rate: 0,
      previous_month_rate: 0,
      change_in_rate: 0,
      is_positive_change: true
    })

    // Total Audits data
    const totalAuditsData = reactive({
      total_current_month: 0,
      total_previous_month: 0,
      change_in_total: 0,
      is_positive_change: true
    })

    // Open Audits data
    const openAuditsData = reactive({
      open_this_week: 0,
      open_last_week: 0,
      change_in_open: 0,
      percent_change: 0,
      is_improvement: true
    })

    // Completed Audits data
    const completedAuditsData = reactive({
      this_week_count: 0,
      last_week_count: 0,
      change_in_completed: 0,
      percent_change: 0,
      is_improvement: true
    })

    // Chart Data Objects
    const chartData = reactive({
      // Time series data
      completion_trend: [],
      compliance_trend: [],
      finding_trend: [],
      
      // Framework data
      framework_performance: [],
      
      // Category data
      category_performance: [],
      
      // Status data
      status_distribution: {}
    })

    // Recent activities data
    const recentActivities = ref([])

    // Fetch Audit Completion Rate data
    const fetchAuditCompletionRate = async () => {
      try {
        const response = await axios.get('/api/dashboard/audit-completion-rate/')
        if (response.data) {
          auditCompletionData.current_month_rate = response.data.current_month_rate
          auditCompletionData.previous_month_rate = response.data.previous_month_rate
          auditCompletionData.change_in_rate = response.data.change_in_rate
          auditCompletionData.is_positive_change = response.data.is_positive_change
        }
      } catch (error) {
        console.error('Error fetching audit completion rate:', error)
      }
    }

    // Fetch Total Audits data
    const fetchTotalAudits = async () => {
      try {
        const response = await axios.get('/api/dashboard/total-audits/')
        if (response.data) {
          totalAuditsData.total_current_month = response.data.total_current_month
          totalAuditsData.total_previous_month = response.data.total_previous_month
          totalAuditsData.change_in_total = response.data.change_in_total
          totalAuditsData.is_positive_change = response.data.is_positive_change
        }
      } catch (error) {
        console.error('Error fetching total audits:', error)
      }
    }

    // Fetch Open Audits data
    const fetchOpenAudits = async () => {
      try {
        const response = await axios.get('/api/dashboard/open-audits/')
        if (response.data) {
          openAuditsData.open_this_week = response.data.open_this_week
          openAuditsData.open_last_week = response.data.open_last_week
          openAuditsData.change_in_open = response.data.change_in_open
          openAuditsData.percent_change = response.data.percent_change
          openAuditsData.is_improvement = response.data.is_improvement
        }
      } catch (error) {
        console.error('Error fetching open audits:', error)
      }
    }

    // Fetch Completed Audits data
    const fetchCompletedAudits = async () => {
      try {
        const response = await axios.get('/api/dashboard/completed-audits/')
        if (response.data) {
          completedAuditsData.this_week_count = response.data.this_week_count
          completedAuditsData.last_week_count = response.data.last_week_count
          completedAuditsData.change_in_completed = response.data.change_in_completed
          completedAuditsData.percent_change = response.data.percent_change
          completedAuditsData.is_improvement = response.data.is_improvement
        }
      } catch (error) {
        console.error('Error fetching completed audits:', error)
      }
    }

    // Fetch Chart Data
    const fetchChartData = async () => {
      // Update charts with default data first to ensure something is displayed
      updateChartData(selectedXAxis.value, selectedYAxis.value)
      
      try {
        // Fetch completion trend data
        try {
          const completionTrendResponse = await axios.get('/api/dashboard/audit-completion-trend/')
          if (completionTrendResponse.data) {
            chartData.completion_trend = completionTrendResponse.data
          }
        } catch (error) {
          console.error('Error fetching completion trend data:', error)
        }

        // Fetch compliance trend data
        try {
          const complianceTrendResponse = await axios.get('/api/dashboard/audit-compliance-trend/')
          if (complianceTrendResponse.data) {
            chartData.compliance_trend = complianceTrendResponse.data
          }
        } catch (error) {
          console.error('Error fetching compliance trend data:', error)
        }

        // Fetch finding trend data
        try {
          const findingTrendResponse = await axios.get('/api/dashboard/audit-finding-trend/')
          if (findingTrendResponse.data) {
            chartData.finding_trend = findingTrendResponse.data
          }
        } catch (error) {
          console.error('Error fetching finding trend data:', error)
        }

        // Fetch framework performance data
        try {
          const frameworkResponse = await axios.get('/api/dashboard/framework-performance/')
          if (frameworkResponse.data) {
            chartData.framework_performance = frameworkResponse.data
          }
        } catch (error) {
          console.error('Error fetching framework performance data:', error)
        }

        // Fetch category performance data
        try {
          const categoryResponse = await axios.get('/api/dashboard/category-performance/')
          if (categoryResponse.data) {
            chartData.category_performance = categoryResponse.data
          }
        } catch (error) {
          console.error('Error fetching category performance data:', error)
        }

        // Fetch status distribution data
        try {
          const statusResponse = await axios.get('/api/dashboard/status-distribution/')
          if (statusResponse.data) {
            chartData.status_distribution = statusResponse.data
          }
        } catch (error) {
          console.error('Error fetching status distribution data:', error)
        }
        
      } catch (error) {
        console.error('Error fetching chart data:', error)
      } finally {
        // Always update charts at the end with whatever data we have
        updateChartData(selectedXAxis.value, selectedYAxis.value)
      }
    }

    // Fetch recent activities
    const fetchRecentActivities = async () => {
      isLoadingActivities.value = true
      try {
        const response = await axios.get('/api/dashboard/recent-audit-activities/')
        if (response.data) {
          recentActivities.value = response.data
        } else {
          recentActivities.value = []
        }
      } catch (error) {
        console.error('Error fetching recent activities:', error)
        
        // Add default activities for better user experience even when API fails
        recentActivities.value = [
          {
            type: 'completed',
            audit_id: 0,
            title: 'Sample Activity',
            description: 'Recent activities will appear here',
            time_ago: 'Recently'
          },
          {
            type: 'review',
            audit_id: 0,
            title: 'Review Activity',
            description: 'Sample review activity',
            time_ago: 'Recently'
          },
          {
            type: 'due',
            audit_id: 0,
            title: 'Due Date Approaching',
            description: 'Sample upcoming deadline',
            time_ago: 'Soon'
          }
        ]
      } finally {
        isLoadingActivities.value = false
      }
    }

    // Refresh all dashboard data
    const refreshData = async () => {
      isLoading.value = true
      try {
        await Promise.all([
          fetchAuditCompletionRate(),
          fetchTotalAudits(),
          fetchOpenAudits(),
          fetchCompletedAudits(),
          fetchChartData(),
          fetchRecentActivities()
        ])
      } catch (error) {
        console.error('Error refreshing dashboard data:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Fetch data on component mount
    onMounted(() => {
      refreshData()
    })

    const selectedXAxis = ref('time')
    const selectedYAxis = ref('completion')
    
    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], ([newXAxis, newYAxis]) => {
      // Set loading state
      isLoading.value = true
      
      // Update chart data based on selected axes
      setTimeout(() => {
        updateChartData(newXAxis, newYAxis)
        isLoading.value = false
      }, 300) // Short delay for better UX
    })

    // --- CHART DATA HANDLING ---
    const updateChartData = (xAxis, yAxis) => {
      // Get proper labels and data based on x-axis and y-axis selection
      const { labels, datasets } = getChartDataConfig(xAxis, yAxis)
      
      // Update Line Chart
      lineChartData.labels = labels
      lineChartData.datasets = [{
        label: getYAxisLabel(yAxis),
        data: datasets[0].data,
        fill: false,
        borderColor: '#4f6cff',
        tension: 0.4,
        pointBackgroundColor: '#4f6cff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]

      // Update Bar Chart
      barChartData.labels = labels
      if (datasets.length > 1) {
        // Use multiple datasets for stacked bars
        barChartData.datasets = datasets.map(dataset => ({
          ...dataset,
          stack: 'Stack 0',
          borderRadius: 4
        }))
      } else {
        // Use single dataset with multiple colors if available
        barChartData.datasets = [{
          label: getYAxisLabel(yAxis),
          data: datasets[0].data,
          backgroundColor: datasets[0].backgroundColor || '#4ade80',
          borderRadius: 4
        }]
      }

      // Update Donut Chart
      donutChartData.labels = labels
      // For donut charts, we need to ensure each slice has its own color
      const colors = datasets[0].multipleColors || 
        ['#4ade80', '#fbbf24', '#f87171', '#60a5fa', '#a78bfa', '#c084fc', '#f472b6', '#fb7185', '#34d399', '#38bdf8']
      
      donutChartData.datasets = [{
        data: datasets[0].data,
        backgroundColor: Array.isArray(datasets[0].backgroundColor) ? 
          datasets[0].backgroundColor : 
          datasets[0].data.map((_, i) => colors[i % colors.length]),
        borderWidth: 0,
        hoverOffset: 5
      }]

      // Update Horizontal Bar Chart
      horizontalBarChartData.labels = labels
      
      // For horizontal bars, we either show all datasets or just the first one
      if (xAxis === 'status' || datasets.length === 1) {
        horizontalBarChartData.datasets = [{
          label: getYAxisLabel(yAxis),
          data: datasets[0].data,
          backgroundColor: Array.isArray(datasets[0].backgroundColor) ? 
            datasets[0].backgroundColor : 
            datasets[0].data.map((_, i) => colors[i % colors.length]),
          borderRadius: 6,
          barPercentage: 0.5,
          categoryPercentage: 0.7
        }]
      } else {
        // Use multiple datasets for stacked horizontal bars
        horizontalBarChartData.datasets = datasets.map(dataset => ({
          ...dataset,
          borderRadius: 6,
          barPercentage: 0.5,
          categoryPercentage: 0.7
        }))
      }
    }

    // Get the appropriate data configuration based on x and y axis selections
    const getChartDataConfig = (xAxis, yAxis) => {
      // Default configuration
      let labels = []
      let datasets = []
      
      // Handle Time axis (historical trends)
      if (xAxis === 'time') {
        // Use default labels if data isn't available yet
        labels = chartData.completion_trend.length > 0 
          ? chartData.completion_trend.map(item => item.month)
          : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        
        if (yAxis === 'completion') {
          // Completion rate trend
          const data = chartData.completion_trend.length > 0
            ? chartData.completion_trend.map(item => item.completion_rate)
            : [65, 70, 75, 78, 82, 85, 88] // Default data
          
          datasets = [{
            label: 'Completion Rate',
            data: data,
            backgroundColor: '#4ade80'
          }]
        } else if (yAxis === 'compliance') {
          // Compliance rate trend
          const data = chartData.compliance_trend.length > 0
            ? chartData.compliance_trend.map(item => item.compliance_rate)
            : [92, 90, 88, 86, 89, 91, 93] // Default data
          
          datasets = [{
            label: 'Compliance Rate',
            data: data,
            backgroundColor: '#60a5fa'
          }]
        } else if (yAxis === 'findings') {
          // Finding count trends (major and minor)
          const majorData = chartData.finding_trend.length > 0
            ? chartData.finding_trend.map(item => item.major_findings)
            : [5, 4, 6, 8, 6, 5, 6] // Default data
          
          const minorData = chartData.finding_trend.length > 0
            ? chartData.finding_trend.map(item => item.minor_findings)
            : [10, 8, 12, 14, 10, 9, 11] // Default data
          
          datasets = [
            {
              label: 'Major Findings',
              data: majorData,
              backgroundColor: '#f87171'
            },
            {
              label: 'Minor Findings',
              data: minorData,
              backgroundColor: '#fbbf24'
            }
          ]
        }
      }
      
      // Handle Frameworks axis
      else if (xAxis === 'frameworks') {
        // Use default frameworks if data isn't available yet
        const frameworkData = chartData.framework_performance.length > 0
          ? chartData.framework_performance
          : [
              { framework: 'ISO 27001', framework_id: 1, completion_rate: 65, completed: 12, in_progress: 3, yet_to_start: 2 },
              { framework: 'NIST 800-53', framework_id: 2, completion_rate: 70, completed: 10, in_progress: 4, yet_to_start: 1 },
              { framework: 'GDPR', framework_id: 3, completion_rate: 75, completed: 8, in_progress: 6, yet_to_start: 2 },
              { framework: 'PCI DSS', framework_id: 4, completion_rate: 82, completed: 14, in_progress: 2, yet_to_start: 1 },
              { framework: 'HIPAA', framework_id: 5, completion_rate: 78, completed: 9, in_progress: 5, yet_to_start: 3 }
            ]
        
        labels = frameworkData.map(item => item.framework)
        
        if (yAxis === 'completion') {
          // Framework completion rates
          const completionData = frameworkData.map(item => item.completion_rate)
          const colors = ['#4ade80', '#60a5fa', '#fbbf24', '#f87171', '#a78bfa', '#c084fc', '#f472b6']
          
          datasets = [{
            label: 'Completion Rate',
            data: completionData,
            backgroundColor: '#4ade80',
            borderColor: '#4f6cff',
            tension: 0.4,
            pointBackgroundColor: '#4f6cff',
            // For donut/horizontal bar, we want individual colors
            multipleColors: colors
          }]
        } else if (yAxis === 'compliance' || yAxis === 'findings') {
          // For stacked view showing completed/in progress/yet to start
          datasets = [
            {
              label: 'Completed',
              data: frameworkData.map(item => item.completed),
              backgroundColor: '#4ade80',
              stack: 'Stack 0',
              borderRadius: 4
            },
            {
              label: 'In Progress',
              data: frameworkData.map(item => item.in_progress),
              backgroundColor: '#fbbf24',
              stack: 'Stack 0',
              borderRadius: 4
            },
            {
              label: 'Yet To Start',
              data: frameworkData.map(item => item.yet_to_start),
              backgroundColor: '#f87171',
              stack: 'Stack 0',
              borderRadius: 4
            }
          ]
        }
      }
      
      // Handle Categories axis
      else if (xAxis === 'categories') {
        // Use default categories if data isn't available yet
        const categoryData = chartData.category_performance.length > 0
          ? chartData.category_performance
          : [
              { category: 'Information Security', completion_rate: 86, total: 25, completed: 21 },
              { category: 'Data Protection', completion_rate: 92, total: 18, completed: 16 },
              { category: 'Risk Assessment', completion_rate: 78, total: 15, completed: 12 },
              { category: 'Access Control', completion_rate: 84, total: 20, completed: 17 },
              { category: 'Change Management', completion_rate: 73, total: 12, completed: 9 }
            ]
        
        labels = categoryData.map(item => item.category)
        const colors = ['#4ade80', '#60a5fa', '#fbbf24', '#f87171', '#a78bfa', '#c084fc', '#f472b6']
        
        if (yAxis === 'completion' || yAxis === 'compliance') {
          // Category completion rates
          const completionData = categoryData.map(item => item.completion_rate)
          
          datasets = [{
            label: 'Completion Rate',
            data: completionData,
            backgroundColor: '#4ade80',
            borderColor: '#4f6cff',
            tension: 0.4,
            pointBackgroundColor: '#4f6cff',
            // For donut/horizontal bar, we want individual colors
            multipleColors: colors
          }]
        } else if (yAxis === 'findings') {
          // Show completed vs total
          datasets = [
            {
              label: 'Completed',
              data: categoryData.map(item => item.completed),
              backgroundColor: '#4ade80',
              stack: 'Stack 0',
              borderRadius: 4
            },
            {
              label: 'Remaining',
              data: categoryData.map(item => item.total - item.completed),
              backgroundColor: '#fbbf24',
              stack: 'Stack 0',
              borderRadius: 4
            }
          ]
        }
      }
      
      // Handle Status axis
      else if (xAxis === 'status') {
        // Use default status data if not available yet
        const statusData = Object.keys(chartData.status_distribution).length > 0
          ? chartData.status_distribution
          : {
              completed: 53,
              in_progress: 32,
              yet_to_start: 15,
              completed_percent: 53,
              in_progress_percent: 32,
              yet_to_start_percent: 15
            }
        
        labels = ['Completed', 'In Progress', 'Yet To Start']
        
        const data = [
          statusData.completed_percent || 0, 
          statusData.in_progress_percent || 0, 
          statusData.yet_to_start_percent || 0
        ]
        
        datasets = [{
          label: 'Distribution',
          data: data,
          backgroundColor: ['#4ade80', '#fbbf24', '#f87171']
        }]
      }
      
      return { labels, datasets }
    }

    const getYAxisLabel = (yAxis) => {
      switch(yAxis) {
        case 'completion': return 'Completion Rate'
        case 'compliance': return 'Compliance Rate'
        case 'findings': return 'Finding Count'
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
    const activeChart = ref('line');
    
    // Line Chart Data
    const lineChartData = reactive({
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      datasets: [{
        label: 'Audit Completion Rate',
        data: [65, 70, 75, 78, 82, 85, 88],
        fill: false,
        borderColor: '#4f6cff',
        tension: 0.4,
        pointBackgroundColor: '#4f6cff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    })
    
    // Line Chart Options
    const lineChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { 
          display: true,
          position: 'top',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            font: { size: 11 }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          bodyFont: { size: 12 },
          titleFont: { size: 13, weight: 'bold' }
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
            font: { size: 11 },
            maxRotation: 45,
            minRotation: 0
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
    
    // Donut Chart Data
    const donutChartData = reactive({
      labels: ['Completed', 'In Progress', 'Yet To Start'],
      datasets: [{
        data: [53, 32, 15],
        backgroundColor: ['#4ade80', '#fbbf24', '#f87171'],
        borderWidth: 0,
        hoverOffset: 5
      }]
    })
    
    // Donut Chart Options
    const donutChartOptions = {
      cutout: '70%',
      plugins: {
        legend: { 
          display: true,
          position: 'right',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            font: { size: 11 }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          bodyFont: { size: 12 },
          titleFont: { size: 13, weight: 'bold' }
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
    
    // Bar Chart Data
    const barChartData = reactive({
      labels: ['ISO 27001', 'NIST 800-53'],
      datasets: [
        {
          label: 'Completed',
          data: [12, 10],
          backgroundColor: '#4ade80',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'In Progress',
          data: [3, 4],
          backgroundColor: '#fbbf24',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Yet To Start',
          data: [2, 1],
          backgroundColor: '#f87171',
          stack: 'Stack 0',
          borderRadius: 4
        }
      ]
    })
    
    // Bar Chart Options
    const barChartOptions = {
      plugins: { 
        legend: { 
          display: true,
          position: 'top',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            font: { size: 11 }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          bodyFont: { size: 12 },
          titleFont: { size: 13, weight: 'bold' }
        }
      },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { 
          stacked: true, 
          grid: { display: false },
          ticks: { 
            color: '#222', 
            font: { size: 10 },
            maxRotation: 45,
            minRotation: 0
          }
        },
        y: { 
          stacked: true, 
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } },
          beginAtZero: true
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }
    
    // Horizontal Bar Chart Data
    const horizontalBarChartData = reactive({
      labels: [
        'Information Security',
        'Data Protection',
        'Risk Assessment',
        'Access Control',
        'Change Management'
      ],
      datasets: [{
        label: 'Completion Rate (%)',
        data: [86, 92, 78, 84, 73],
        backgroundColor: '#4ade80',
        borderRadius: 6,
        barPercentage: 0.5,
        categoryPercentage: 0.7
      }]
    })
    
    // Horizontal Bar Chart Options
    const horizontalBarChartOptions = {
      indexAxis: 'y',
      plugins: {
        legend: { 
          display: true,
          position: 'top',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            font: { size: 11 }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          bodyFont: { size: 12 },
          titleFont: { size: 13, weight: 'bold' }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } },
          stacked: true
        },
        y: {
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } },
          stacked: true
        }
      },
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }

    // Helper function to get activity icon
    const getActivityIcon = (type) => {
      switch(type) {
        case 'completed': return 'fas fa-check-circle'
        case 'review': return 'fas fa-sync-alt'
        case 'due': return 'fas fa-exclamation-circle'
        default: return 'fas fa-info-circle'
      }
    }

    // Helper function to get activity icon class
    const getActivityIconClass = (type) => {
      switch(type) {
        case 'completed': return ''
        case 'review': return 'update'
        case 'due': return 'alert'
        default: return ''
      }
    }

    // Helper function to safely check if an array is empty
    const isEmpty = (arr) => {
      return !arr || !Array.isArray(arr) || arr.length === 0;
    }

    // Computed property for filtered activities
    const filteredActivities = computed(() => {
      if (!recentActivities.value || !Array.isArray(recentActivities.value)) {
        return [];
      }
      return recentActivities.value.filter(activity => activity !== null && activity !== undefined);
    })

    return {
      isLoading,
      isLoadingActivities,
      auditCompletionData,
      totalAuditsData,
      openAuditsData,
      completedAuditsData,
      chartData,
      recentActivities,
      refreshData,
      fetchRecentActivities,
      getActivityIcon,
      getActivityIconClass,
      isEmpty,
      lineChartData,
      lineChartOptions,
      donutChartData,
      donutChartOptions,
      barChartData,
      barChartOptions,
      horizontalBarChartData,
      horizontalBarChartOptions,
      chartTypes,
      activeChart,
      selectedXAxis,
      selectedYAxis,
      filteredActivities
    }
  }
}
</script>

<style scoped>
@import './UserDashboard.css';
.chart-tabs {
  display: flex;
  gap: 8px;
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
.chart-tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}
.chart-loading i {
  font-size: 2rem;
  margin-bottom: 12px;
  color: #4f6cff;
}
.axis-select:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.activity-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.activity-loading,
.activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
  text-align: center;
}
.activity-loading i {
  font-size: 2rem;
  margin-bottom: 12px;
  color: #4f6cff;
}
.activity-list {
  max-height: 400px;
  overflow-y: auto;
  flex-grow: 1;
}
.activity-item {
  padding: 16px;
  display: flex;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}
.activity-item:last-child {
  border-bottom: none;
}
.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #4f6cff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}
.activity-icon.update {
  background: #fbbf24;
}
.activity-icon.alert {
  background: #f87171;
}
.activity-content {
  flex-grow: 1;
}
.activity-title {
  font-weight: 500;
  margin-bottom: 4px;
}
.activity-desc {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 4px;
}
.activity-time {
  color: #888;
  font-size: 0.8rem;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}
.card-action {
  background: none;
  border: none;
  font-size: 1rem;
  color: #888;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
}
.card-action:hover {
  background: #eef2ff;
  color: #4f6cff;
}
.dashboard-header, .dashboard-heading {
  /* Removed animation and animation-related classes */
}
.dashboard-container {
  /* Ensure container fits the page, no content cut off, but keep margin-left for sidebar */
  overflow-x: auto;
  box-sizing: border-box;
}
</style> 