<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Incident Dashboard</h1>
      <div class="header-actions">
        <button class="refresh-btn" @click="refreshData"><i class="fas fa-sync"></i></button>
        <button class="download-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>
    
    <div class="metrics-grid">
      <!-- Total Incidents Card -->
      <div class="metric-card">
        <div class="metric-icon incident-icon">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Total Incidents</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.total_count || 0 }}</span>
          </div>
          <div class="metric-change">
            {{ dashboardData.change_percentage > 0 ? '+' : '' }}{{ dashboardData.change_percentage }}% from last period
          </div>
        </div>
      </div>
    
      <!-- Open Incidents Card -->
      <div class="metric-card">
        <div class="metric-icon open-icon">
          <i class="fas fa-clipboard-list"></i>
        </div>
        <div class="metric-content">
          <h3>Open Incidents</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.scheduled || 0 }}</span>
          </div>
          <div class="metric-change">
            Awaiting resolution
          </div>
        </div>
      </div>
        
      <!-- Rejected Card -->
      <div class="metric-card">
        <div class="metric-icon rejected-icon">
          <i class="fas fa-ban"></i>
        </div>
        <div class="metric-content">
          <h3>Rejected</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.rejected || 0 }}</span>
          </div>
          <div class="metric-change">
            Rejected incidents
          </div>
        </div>
      </div>
    
                <!-- Approved Card -->
      <div class="metric-card">
        <div class="metric-icon approved-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Approved</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.approved || 0 }}</span>
          </div>
          <div class="metric-change">
            Approved incidents
          </div>
        </div>
      </div>
    </div>
    
    <div class="dashboard-content">
      <div class="performance-chart">
        <div class="chart-header">
          <h2>Incident Analytics</h2>
          <div class="chart-controls">
            <div class="chart-type-icons">
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'bar' }"
                @click="changeChartType('bar')"
                title="Bar Chart"
              >
                <i class="fas fa-chart-bar"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'line' }"
                @click="changeChartType('line')"
                title="Line Chart"
              >
                <i class="fas fa-chart-line"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'pie' }"
                @click="changeChartType('pie')"
                title="Pie Chart"
              >
                <i class="fas fa-chart-pie"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'doughnut' }"
                @click="changeChartType('doughnut')"
                title="Doughnut Chart"
              >
                <i class="fas fa-circle-notch"></i>
              </button>
            </div>
            <div class="axis-controls">
              <div class="axis-select">
                <label>X Axis:</label>
                <select v-model="selectedXAxis" @change="fetchDashboardData">
                  <option value="Time">Incidents</option>
                </select>
              </div>
              <div class="axis-select">
                <label>Y Axis:</label>
                <select v-model="selectedYAxis" @change="fetchDashboardData">
                  <option value="Status">By Status</option>
                  <option value="Origin">By Origin</option>
                  <option value="RiskCategory">By Risk Category</option>
                  <option value="RiskPriority">By Risk Priority</option>
                  <option value="Repeated">By Repeated Status</option>
                  <option value="CostImpact">By Cost (₹)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="myChart"></canvas>
        </div>
      </div>
      
      <div class="recent-activity">
        <div class="activity-header">
          <h2>Recent Incidents</h2>
          <button class="more-options"><i class="fas fa-ellipsis-v"></i></button>
        </div>
        <div class="activity-list">
          <div v-for="(incident, index) in recentIncidents" :key="index" class="activity-item">
            <div class="activity-icon" :class="incident.priority_class">
              <i :class="incident.icon"></i>
            </div>
            <div class="activity-details">
              <h4>{{ incident.IncidentTitle }}</h4>
              <p>{{ truncateDescription(incident.Description, 100) }}</p>
              <div class="activity-meta">
                <span class="activity-tag origin-tag">{{ incident.origin_text }}</span>
                <span v-if="incident.status_class" class="activity-tag status-tag" :class="incident.status_class">{{ incident.Status }}</span>
                <span class="activity-time">{{ formatDate(incident.CreatedAt) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import '@fortawesome/fontawesome-free/css/all.min.css'
import { incidentService } from '@/services/api'
import { PopupModal } from '@/modules/popup'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'IncidentPerformanceDashboard',
  components: {
    PopupModal
  },
  data() {
    return {
      selectedChartType: 'bar',
      selectedXAxis: 'Time',
      selectedYAxis: 'Severity',
      chart: null,
      chartId: 'myChart',
      api: {
        incidentService
      },
      dashboardData: {
        status_counts: {
          scheduled: 0,
          approved: 0,
          resolved: 0,
          rejected: 0
        },
        total_count: 0,
        change_percentage: 0,
        resolution_rate: 0
      },
      chartData: null,
      recentIncidents: []
    }
  },
  mounted() {
    this.fetchDashboardData()
    this.fetchRecentIncidents()
  },
  beforeUnmount() {
    this.destroyChart()
  },
  beforeRouteLeave(to, from, next) {
    this.destroyChart()
    next()
  },
  methods: {
    destroyChart() {
      if (this.chart) {
        this.chart.destroy()
        this.chart = null
      }
    },
    async fetchRecentIncidents() {
      try {
        const response = await this.api.incidentService.getRecentIncidents(3)
        if (response.data && response.data.success) {
          this.recentIncidents = response.data.incidents.map(incident => {
            // Add priority class and icon based on severity
            let priorityClass = 'medium'
            let icon = 'fas fa-exclamation-triangle'
            
            if (incident.RiskPriority) {
              const priority = incident.RiskPriority.toLowerCase();
              if (priority.includes('high')) {
                priorityClass = 'high'
                icon = 'fas fa-radiation'
              } else if (priority.includes('low')) {
                priorityClass = 'low'
                icon = 'fas fa-info-circle'
              }
            }
            
            // Add status class
            let statusClass = '';
            if (incident.Status) {
              const status = incident.Status.toLowerCase();
              if (status.includes('rejected')) {
                statusClass = 'rejected';
              } else if (status.includes('approved')) {
                statusClass = 'approved';
              } else if (status.includes('scheduled')) {
                statusClass = 'scheduled';
              }
            }
            
            // Add origin info
            let originText = incident.Origin || 'Unknown';
            
            return {
              ...incident,
              priority_class: priorityClass,
              status_class: statusClass,
              icon: icon,
              origin_text: originText
            }
          })
        } else {
          console.error('Failed to fetch recent incidents')
          this.recentIncidents = []
        }
      } catch (error) {
        console.error('Error fetching recent incidents:', error)
        this.recentIncidents = []
      }
    },
    async fetchDashboardData() {
      try {
        console.log('Starting fetchDashboardData for incidents...')
        console.log('Request payload:', {
          xAxis: this.selectedXAxis,
          yAxis: this.selectedYAxis
        })

        // First fetch the dashboard data
        let dashboardResponse, analyticsResponse
        
        try {
          dashboardResponse = await this.api.incidentService.getIncidentDashboard()
          console.log('Incident Dashboard API Response:', dashboardResponse.data)
        } catch (err) {
          console.error('Error fetching dashboard data:', err)
          throw new Error(`Dashboard fetch failed: ${err.message}`)
        }
        
        try {
          analyticsResponse = await this.api.incidentService.getIncidentAnalytics({
            xAxis: this.selectedXAxis,
            yAxis: this.selectedYAxis
          })
          console.log('Incident Analytics API Response:', analyticsResponse.data)
        } catch (err) {
          console.error('Error fetching analytics data:', err)
          throw new Error(`Analytics fetch failed: ${err.message}`)
        }

        // Check if we got valid responses
        if (!dashboardResponse.data) {
          console.error('Dashboard response data is null or undefined')
          throw new Error('Invalid dashboard response')
        }

        if (!analyticsResponse.data) {
          console.error('Analytics response data is null or undefined')
          throw new Error('Invalid analytics response')
        }

        if (dashboardResponse.data.success && analyticsResponse.data.success) {
          // Validate that the summary data exists
          if (!dashboardResponse.data.data || !dashboardResponse.data.data.summary) {
            console.error('Dashboard response does not contain expected data structure', dashboardResponse.data)
            throw new Error('Invalid dashboard data structure')
          }

          // Validate that chart data exists
          if (!analyticsResponse.data.chartData) {
            console.error('Analytics response does not contain expected chartData', analyticsResponse.data)
            throw new Error('Invalid analytics data structure')
          }

          // Update dashboard metrics with detailed logging
          const summary = dashboardResponse.data.data.summary
          console.log('Dashboard summary data:', summary)
          
          this.dashboardData = {
            status_counts: summary.status_counts || {},
            total_count: summary.total_count || 0,
            change_percentage: summary.change_percentage || 0,
            resolution_rate: summary.resolution_rate || 0
          }
          
          console.log('Updated dashboard data:', this.dashboardData)
          
          // Update chart data
          this.chartData = analyticsResponse.data.chartData
          console.log('Updated chart data:', this.chartData)
          
          // Wait for the next tick to ensure DOM is updated
          await this.$nextTick()
          this.updateChart()
        } else {
          // Log the error message from the API
          const errorMessage = dashboardResponse.data.message || analyticsResponse.data.message || 'API request failed'
          console.error('API Error:', errorMessage)
          throw new Error(errorMessage)
        }
      } catch (error) {
        console.error('Error in fetchDashboardData:', error)
        
        // Set default values on error
        this.dashboardData = {
          status_counts: {
            scheduled: 0,
            approved: 0,
            rejected: 0
          },
          total_count: 0,
          change_percentage: 0,
          resolution_rate: 0
        }
        this.chartData = {
          labels: [],
          datasets: [{
            label: 'Error Loading Data',
            data: [],
            backgroundColor: 'rgba(244, 67, 54, 0.6)',
            borderColor: '#F44336',
            borderWidth: 1
          }]
        }
        await this.$nextTick()
        this.updateChart()
      }
    },
    updateChart() {
      try {
        // Destroy existing chart
        this.destroyChart()

        // Get the canvas element
        const canvas = document.getElementById(this.chartId)
        if (!canvas) {
          console.error('Chart canvas not found')
          return
        }

        // Create the chart configuration
        const config = this.createChartConfig()

        // Create new chart instance
        this.chart = new ChartJS(canvas, config)
      } catch (error) {
        console.error('Error in updateChart:', error)
        this.chart = null
      }
    },
    createChartConfig() {
      if (!this.chartData) {
        return {
          type: this.selectedChartType,
          data: {
            labels: [],
            datasets: [{
              label: 'No Data',
              data: [],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: '#ccc',
              borderWidth: 1
            }]
          },
          options: this.getChartOptions()
        }
      }

      // Check if we have multiple datasets (time-based X-axis with Y-axis dimension)
      const hasMultipleDatasets = Array.isArray(this.chartData.datasets) && this.chartData.datasets.length > 1;
      
      let datasets;
      
      if (hasMultipleDatasets) {
        // Use the datasets as provided by the backend
        datasets = this.chartData.datasets.map((dataset, index) => {
          const colors = this.getColorForIndex(index);
          return {
            ...dataset,
            backgroundColor: colors.backgroundColor,
            borderColor: colors.borderColor,
            borderWidth: 1,
            tension: this.selectedChartType === 'line' ? 0.1 : undefined,
            fill: this.selectedChartType === 'line' ? false : undefined
          };
        });
      } else {
        // Single dataset with custom colors based on y-axis
        const dataset = {
          ...this.chartData.datasets[0],
          backgroundColor: this.getBackgroundColors(),
          borderColor: this.getBorderColors(),
          borderWidth: 1
        };

        if (this.selectedChartType === 'line') {
          dataset.tension = 0.1;
          dataset.fill = false;
        }
        
        datasets = [dataset];
      }

      return {
        type: this.selectedChartType,
        data: {
          labels: this.chartData.labels,
          datasets: datasets
        },
        options: this.getChartOptions()
      }
    },
    
    // Helper method to get color for multiple datasets
    getColorForIndex(index) {
      const colors = [
        { backgroundColor: 'rgba(255, 99, 132, 0.6)', borderColor: 'rgb(255, 99, 132)' },
        { backgroundColor: 'rgba(54, 162, 235, 0.6)', borderColor: 'rgb(54, 162, 235)' },
        { backgroundColor: 'rgba(255, 206, 86, 0.6)', borderColor: 'rgb(255, 206, 86)' },
        { backgroundColor: 'rgba(75, 192, 192, 0.6)', borderColor: 'rgb(75, 192, 192)' },
        { backgroundColor: 'rgba(153, 102, 255, 0.6)', borderColor: 'rgb(153, 102, 255)' },
        { backgroundColor: 'rgba(255, 159, 64, 0.6)', borderColor: 'rgb(255, 159, 64)' },
        { backgroundColor: 'rgba(199, 199, 199, 0.6)', borderColor: 'rgb(199, 199, 199)' }
      ];
      
      // Use modulo to cycle through colors if we have more datasets than colors
      return colors[index % colors.length];
    },
    getChartOptions() {
      const hasMultipleDatasets = this.chartData && 
                                  this.chartData.datasets && 
                                  this.chartData.datasets.length > 1;

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500,
          easing: 'easeInOutQuad'
        },
        plugins: {
          legend: {
            display: ['pie', 'doughnut'].includes(this.selectedChartType) || hasMultipleDatasets,
            position: 'top'
          },
          tooltip: {
            enabled: true,
            callbacks: {
              label: (context) => {
                // Special handling for cost impact when it's numeric
                if (this.selectedYAxis === 'CostImpact') {
                  // Check if label is numeric
                  if (!isNaN(parseFloat(context.label))) {
                    const label = 'Cost: ₹' + context.label;
                    const value = context.raw || 0;
                    return `${label} - ${value} incidents`;
                  }
                }
                
                if (['pie', 'doughnut'].includes(this.selectedChartType)) {
                  const label = context.label || ''
                  const value = context.raw || 0
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
                // For multiple datasets, show both dataset name and value
                if (hasMultipleDatasets) {
                  const label = context.dataset.label || ''
                  const value = context.raw || 0
                  return `${label}: ${value}`
                }
                return `Count: ${context.raw}`
              }
            }
          }
        }
      }

      if (['bar', 'line'].includes(this.selectedChartType)) {
        options.scales = {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0
            }
          }
        }
        
        // Special handling for CostImpact when it's the X-axis
        if (this.selectedYAxis === 'CostImpact' && this.chartData && this.chartData.labels) {
          // Check if labels are numeric (cost values)
          const isNumeric = this.chartData.labels.some(label => !isNaN(parseFloat(label)));
          
          if (isNumeric) {
            // Format x-axis labels with currency symbol
            options.scales.x = {
              ticks: {
                callback: function(value) {
                  return '₹' + this.getLabelForValue(value);
                }
              }
            }
          }
        }
        
        // For stacked bar charts when using multiple datasets with time-based x-axis
        if (this.selectedChartType === 'bar' && 
            hasMultipleDatasets &&
            ['Date', 'Month', 'Quarter'].includes(this.selectedXAxis)) {
          options.scales.x = {
            stacked: true,
            ...(options.scales.x || {})
          }
          options.scales.y.stacked = true
        }
      }

      return options
    },
    changeChartType(newType) {
      if (this.selectedChartType === newType) {
        return
      }
      
      this.selectedChartType = newType
      this.$nextTick(() => {
        this.updateChart()
      })
    },
    getBackgroundColors() {
      const colorMaps = {
        Severity: {
          'High': 'rgba(244, 67, 54, 0.6)',
          'Medium': 'rgba(255, 152, 0, 0.6)',
          'Low': 'rgba(76, 175, 80, 0.6)'
        },
        Status: {
          'Scheduled': 'rgba(255, 152, 0, 0.6)',
          'Approved': 'rgba(76, 175, 80, 0.6)',
          'Rejected': 'rgba(244, 67, 54, 0.6)'
        },
        Origin: {
          'Manual': 'rgba(33, 150, 243, 0.6)',
          'SIEM': 'rgba(156, 39, 176, 0.6)',
          'Audit Finding': 'rgba(255, 193, 7, 0.6)',
          'Other': 'rgba(121, 85, 72, 0.6)'
        },
        RiskCategory: {
          'Security': 'rgba(244, 67, 54, 0.6)',
          'Compliance': 'rgba(156, 39, 176, 0.6)',
          'Operational': 'rgba(255, 152, 0, 0.6)',
          'Financial': 'rgba(33, 150, 243, 0.6)',
          'Strategic': 'rgba(76, 175, 80, 0.6)',
          'Reputational': 'rgba(121, 85, 72, 0.6)'
        },
        RiskPriority: {
          'High': 'rgba(244, 67, 54, 0.6)',
          'Medium': 'rgba(255, 152, 0, 0.6)',
          'Low': 'rgba(76, 175, 80, 0.6)'
        },
        Repeated: {
          'Repeated': 'rgba(244, 67, 54, 0.6)',
          'Not Repeated': 'rgba(76, 175, 80, 0.6)'
        },
        CostImpact: {
          'Low': 'rgba(76, 175, 80, 0.6)',
          'Medium': 'rgba(255, 152, 0, 0.6)',
          'High': 'rgba(244, 67, 54, 0.6)',
          'Unknown': 'rgba(158, 158, 158, 0.6)'
        }
      }

      // Special handling for CostImpact when it's numeric
      if (this.selectedYAxis === 'CostImpact' && this.chartData && this.chartData.labels) {
        // Check if labels are numeric (cost ranges)
        const isNumeric = this.chartData.labels.some(label => !isNaN(parseFloat(label)));
        
        if (isNumeric) {
          // Generate gradient colors based on value
          return this.chartData.labels.map(label => {
            const value = parseFloat(label);
            // Create color based on value (green for low, red for high)
            if (value < 500) {
              return 'rgba(76, 175, 80, 0.6)'; // Green for low cost
            } else if (value < 2000) {
              return 'rgba(255, 152, 0, 0.6)'; // Orange for medium cost
            } else {
              return 'rgba(244, 67, 54, 0.6)'; // Red for high cost
            }
          });
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')] 
          ? colorMaps[this.selectedYAxis.replace('By ', '')][label] || 'rgba(158, 158, 158, 0.6)'
          : 'rgba(158, 158, 158, 0.6)'
      ) || []
    },
    getBorderColors() {
      const colorMaps = {
        Severity: {
          'High': '#F44336',
          'Medium': '#FF9800',
          'Low': '#4CAF50'
        },
        Status: {
          'Scheduled': '#FF9800',
          'Approved': '#4CAF50',
          'Rejected': '#F44336'
        },
        Origin: {
          'Manual': '#2196F3',
          'SIEM': '#9C27B0',
          'Audit Finding': '#FFC107',
          'Other': '#795548'
        },
        RiskCategory: {
          'Security': '#F44336',
          'Compliance': '#9C27B0',
          'Operational': '#FF9800',
          'Financial': '#2196F3',
          'Strategic': '#4CAF50',
          'Reputational': '#795548'
        },
        RiskPriority: {
          'High': '#F44336',
          'Medium': '#FF9800',
          'Low': '#4CAF50'
        },
        Repeated: {
          'Repeated': '#F44336',
          'Not Repeated': '#4CAF50'
        },
        CostImpact: {
          'Low': '#4CAF50',
          'Medium': '#FF9800',
          'High': '#F44336',
          'Unknown': '#9E9E9E'
        }
      }

      // Special handling for CostImpact when it's numeric
      if (this.selectedYAxis === 'CostImpact' && this.chartData && this.chartData.labels) {
        // Check if labels are numeric (cost ranges)
        const isNumeric = this.chartData.labels.some(label => !isNaN(parseFloat(label)));
        
        if (isNumeric) {
          // Generate gradient colors based on value
          return this.chartData.labels.map(label => {
            const value = parseFloat(label);
            // Create color based on value (green for low, red for high)
            if (value < 500) {
              return '#4CAF50'; // Green for low cost
            } else if (value < 2000) {
              return '#FF9800'; // Orange for medium cost
            } else {
              return '#F44336'; // Red for high cost
            }
          });
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')] 
          ? colorMaps[this.selectedYAxis.replace('By ', '')][label] || '#9E9E9E'
          : '#9E9E9E'
      ) || []
    },
    refreshData() {
      this.fetchDashboardData()
      this.fetchRecentIncidents()
    },
    truncateDescription(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      
      // Check if it's today
      const today = new Date();
      if (date.toDateString() === today.toDateString()) {
        return 'Today, ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      }
      
      // Check if it's yesterday
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday, ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      }
      
      // Otherwise return relative time
      const diffTime = Math.abs(today - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 7) {
        return diffDays + ' days ago';
      } else {
        return date.toLocaleDateString();
      }
    }
  }
}
</script>

<style>
@import './IncidentPerformanceDashboard.css';

.chart-controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.chart-type-icons {
  display: flex;
  gap: 8px;
  padding: 4px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chart-type-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-type-btn:hover {
  background-color: #e2e8f0;
  color: #1e293b;
}

.chart-type-btn.active {
  background-color: #4CAF50;
  color: white;
}

.chart-type-btn i {
  font-size: 1.1rem;
}

.axis-controls {
  display: flex;
  gap: 16px;
}

.axis-select {
  display: flex;
  align-items: center;
  gap: 8px;
}

.axis-select label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.axis-select select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #1e293b;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.axis-select select:hover {
  border-color: #94a3b8;
}

.axis-select select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.chart-type-select {
  display: none;
}

.metric-icon.incident-icon {
  background-color: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.metric-icon.open-icon {
  background-color: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}

.metric-icon.mttd-icon {
  background-color: rgba(33, 150, 243, 0.15);
  color: #2196f3;
}

.metric-icon.rejected-icon {
  background-color: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.metric-icon.approved-icon {
  background-color: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.activity-icon.high {
  background-color: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.activity-icon.medium {
  background-color: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}

.activity-icon.low {
  background-color: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.activity-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
  align-items: center;
}

.activity-tag {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.origin-tag {
  background-color: rgba(33, 150, 243, 0.1);
  color: #2196f3;
}

.status-tag {
  background-color: rgba(158, 158, 158, 0.1);
  color: #9e9e9e;
}

.status-tag.scheduled {
  background-color: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.status-tag.approved {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.status-tag.rejected {
  background-color: rgba(244, 67, 54, 0.1);
  color: #f44336;
}
</style>