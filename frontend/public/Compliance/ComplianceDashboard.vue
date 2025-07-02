<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Compliance Dashboard</h1>
      <div class="header-actions">
        <button class="refresh-btn" @click="refreshData"><i class="fas fa-sync"></i></button>
        <button class="download-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <div class="metrics-grid">
      <!-- Approval Rate Card -->
      <div class="metric-card">
        <div class="metric-icon compliance-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Approval Rate</h3>
          <div class="metric-value">
            <span class="percentage">{{ dashboardData.approval_rate }}%</span>
          </div>
          <div class="metric-change">
            Based on {{ dashboardData.total_count }} compliances
          </div>
        </div>
      </div>

      <!-- Active Compliances Card -->
      <div class="metric-card">
        <div class="metric-icon policies-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="metric-content">
          <h3>Active Compliances</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.active_compliance || 0 }}</span>
          </div>
          <div class="metric-change">
            Active and Approved
          </div>
        </div>
      </div>

      <!-- Total Findings Card -->
      <div class="metric-card">
        <div class="metric-icon risk-icon">
          <i class="fas fa-list"></i>
        </div>
        <div class="metric-content">
          <h3>Total Findings</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.total_findings }}</span>
          </div>
          <div class="metric-change">
            Across all compliances
          </div>
        </div>
      </div>

      <!-- Under Review Card -->
      <div class="metric-card">
        <div class="metric-icon review-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="metric-content">
          <h3>Under Review</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.under_review }}</span>
          </div>
          <div class="metric-change">
            Pending review
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="performance-chart">
        <div class="chart-header">
          <h2>Compliance Analytics</h2>
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
                  <option value="Compliance">Compliance</option>
                </select>
              </div>
              <div class="axis-select">
                <label>Y Axis:</label>
                <select v-model="selectedYAxis" @change="fetchDashboardData">
                  <option value="Criticality">By Criticality</option>
                  <option value="Status">By Status</option>
                  <option value="ActiveInactive">By Active/Inactive</option>
                  <option value="ManualAutomatic">By Manual/Automatic</option>
                  <option value="MandatoryOptional">By Mandatory/Optional</option>
                  <option value="MaturityLevel">By Maturity Level</option>
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
          <h2>Recent Activity</h2>
          <button class="more-options" @click="refreshRecentActivities">
            <i class="fas fa-sync" :class="{ 'fa-spin': loadingActivities }"></i>
          </button>
        </div>
        <div class="activity-list">
          <div v-if="loadingActivities" class="activity-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading recent activities...</span>
          </div>
          <div v-else-if="recentActivities.length === 0" class="activity-empty">
            <i class="fas fa-inbox"></i>
            <span>No recent activities found</span>
          </div>
          <div v-else v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-details">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
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
import { complianceService } from '@/services/api'

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
  name: 'ComplianceDashboard',
  data() {
    return {
      selectedChartType: 'bar',
      selectedXAxis: 'Compliance',
      selectedYAxis: 'Criticality',
      chart: null,
      chartId: 'myChart',
      api: {
        complianceService
      },
      dashboardData: {
        status_counts: {
          approved: 0,
          active: 0,
          under_review: 0
        },
        total_count: 0,
        total_findings: 0,
        approval_rate: 0
      },
      chartData: null,
      recentActivities: [],
      loadingActivities: false,
      activityRefreshInterval: null
    }
  },
  mounted() {
    // Fetch data first, then initialize chart
    this.fetchDashboardData().then(() => {
      // Ensure chart is initialized after data is loaded
      this.$nextTick(() => {
        setTimeout(() => {
          if (!this.chart) {
            this.updateChart()
          }
        }, 200)
      })
    })
    
    this.fetchRecentActivities()
    
    // Auto-refresh activities every 5 minutes
    this.activityRefreshInterval = setInterval(() => {
      this.fetchRecentActivities()
    }, 300000) // 5 minutes
  },
  beforeUnmount() {
    this.destroyChart()
    if (this.activityRefreshInterval) {
      clearInterval(this.activityRefreshInterval)
    }
  },
  beforeRouteLeave(to, from, next) {
    this.destroyChart()
    if (this.activityRefreshInterval) {
      clearInterval(this.activityRefreshInterval)
    }
    next()
  },
  methods: {
    destroyChart() {
      try {
        if (this.chart) {
          console.log('Destroying existing chart')
          this.chart.destroy()
          this.chart = null
        }
        
        // Also clear any canvas context as backup
        const canvas = document.getElementById(this.chartId)
        if (canvas) {
          const ctx = canvas.getContext('2d')
          if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
          }
        }
      } catch (error) {
        console.error('Error destroying chart:', error)
        this.chart = null
      }
    },
    
    async fetchRecentActivities() {
      try {
        this.loadingActivities = true
        console.log('Fetching recent activities...')
        
        // Fetch different types of activities in parallel
        const [approvalsResponse, frameworksResponse] = await Promise.all([
          this.api.complianceService.getCompliancePolicyApprovals({ reviewer_id: 2 }), // Default reviewer
          this.api.complianceService.getComplianceFrameworks()
        ])
        
        let activities = []
        
        // Process policy approvals for recent activities
        if (approvalsResponse.data.success && approvalsResponse.data.data) {
          const approvals = approvalsResponse.data.data
          
          // Sort approvals by most recent first
          const sortedApprovals = approvals.sort((a, b) => {
            const dateA = new Date(a.ApprovedDate || a.ExtractedData?.CreatedByDate || '1970-01-01')
            const dateB = new Date(b.ApprovedDate || b.ExtractedData?.CreatedByDate || '1970-01-01')
            return dateB - dateA
          })
          
          // Process different types of activities
          sortedApprovals.slice(0, 10).forEach(approval => {
            const extractedData = approval.ExtractedData || {}
            const complianceTitle = extractedData.ComplianceTitle || extractedData.ComplianceItemDescription || 'Unknown Compliance'
            const createdBy = extractedData.CreatedByName || 'Unknown User'
            const version = extractedData.ComplianceVersion || '1.0'
            
            // Determine activity type based on approval status and data
            if (approval.ApprovedNot === true) {
              // Approved compliance
              activities.push({
                type: 'approved',
                icon: 'fas fa-check-circle',
                title: 'Compliance Approved',
                description: `"${this.truncateText(complianceTitle, 50)}" approved by reviewer`,
                time: this.formatRelativeTime(approval.ApprovedDate),
                metadata: {
                  complianceId: extractedData.compliance_id,
                  version: version,
                  approver: 'Reviewer'
                }
              })
            } else if (approval.ApprovedNot === false) {
              // Rejected compliance
              activities.push({
                type: 'rejected',
                icon: 'fas fa-times-circle',
                title: 'Compliance Rejected',
                description: `"${this.truncateText(complianceTitle, 50)}" needs revision`,
                time: this.formatRelativeTime(approval.ApprovedDate),
                metadata: {
                  complianceId: extractedData.compliance_id,
                  version: version,
                  reviewer: 'Reviewer'
                }
              })
            } else if (approval.ApprovedNot === null) {
              // Check if it's a deactivation request
              if (extractedData.type === 'compliance_deactivation' || extractedData.RequestType === 'Change Status to Inactive') {
                activities.push({
                  type: 'deactivation',
                  icon: 'fas fa-power-off',
                  title: 'Deactivation Request',
                  description: `Deactivation requested for compliance ID ${extractedData.compliance_id}`,
                  time: this.formatRelativeTime(extractedData.CreatedByDate),
                  metadata: {
                    complianceId: extractedData.compliance_id,
                    reason: extractedData.reason || 'No reason provided'
                  }
                })
              } else {
                // Check if it's a new version (higher version number)
                if (parseFloat(version) > 1.0) {
                  activities.push({
                    type: 'version',
                    icon: 'fas fa-code-branch',
                    title: 'New Version Created',
                    description: `Version ${version} of "${this.truncateText(complianceTitle, 40)}" by ${createdBy}`,
                    time: this.formatRelativeTime(extractedData.CreatedByDate),
                    metadata: {
                      complianceId: extractedData.compliance_id,
                      version: version,
                      creator: createdBy
                    }
                  })
                } else {
                  // New compliance under review
                  activities.push({
                    type: 'created',
                    icon: 'fas fa-plus-circle',
                    title: 'New Compliance Created',
                    description: `"${this.truncateText(complianceTitle, 50)}" created by ${createdBy}`,
                    time: this.formatRelativeTime(extractedData.CreatedByDate),
                    metadata: {
                      complianceId: extractedData.compliance_id,
                      version: version,
                      creator: createdBy
                    }
                  })
                }
              }
            }
          })
        }
        
        // Try to get additional recent compliance data from frameworks
        if (frameworksResponse.data && Array.isArray(frameworksResponse.data)) {
          // Get recent compliances from the first few subpolicies
          try {
            const framework = frameworksResponse.data[0]
            if (framework) {
              const policiesResponse = await this.api.complianceService.getCompliancePolicies(framework.id)
              if (policiesResponse.data && Array.isArray(policiesResponse.data)) {
                const policy = policiesResponse.data[0]
                if (policy) {
                  const subpoliciesResponse = await this.api.complianceService.getComplianceSubPolicies(policy.id)
                  if (subpoliciesResponse.data && Array.isArray(subpoliciesResponse.data)) {
                    const subpolicy = subpoliciesResponse.data[0]
                    if (subpolicy) {
                      const compliancesResponse = await this.api.complianceService.getCompliancesBySubPolicy(subpolicy.id)
                      if (compliancesResponse.data.success && compliancesResponse.data.data) {
                        // Process recent compliances
                        const complianceGroups = compliancesResponse.data.data
                        complianceGroups.slice(0, 3).forEach((group) => {
                          if (group && group.length > 0) {
                            const latestCompliance = group[0] // Latest version in the group
                            
                            // Avoid duplicates by checking if we already have this compliance
                            const existingActivity = activities.find(a => 
                              a.metadata?.complianceId === latestCompliance.ComplianceId
                            )
                            
                            if (!existingActivity && latestCompliance.CreatedByDate) {
                              const activityDate = new Date(latestCompliance.CreatedByDate)
                              const now = new Date()
                              const daysDiff = (now - activityDate) / (1000 * 60 * 60 * 24)
                              
                              // Only show activities from the last 30 days
                              if (daysDiff <= 30) {
                                activities.push({
                                  type: 'updated',
                                  icon: 'fas fa-edit',
                                  title: 'Compliance Updated',
                                  description: `"${this.truncateText(latestCompliance.ComplianceItemDescription || 'Compliance item', 50)}" modified`,
                                  time: this.formatRelativeTime(latestCompliance.CreatedByDate),
                                  metadata: {
                                    complianceId: latestCompliance.ComplianceId,
                                    version: latestCompliance.ComplianceVersion,
                                    creator: latestCompliance.CreatedByName
                                  }
                                })
                              }
                            }
                          }
                        })
                      }
                    }
                  }
                }
              }
            }
          } catch (error) {
            console.log('Could not fetch additional compliance data:', error.message)
            // Continue without additional data
          }
        }
        
        // Sort all activities by time (most recent first) and limit to top 10
        activities.sort((a, b) => {
          const timeA = this.parseRelativeTime(a.time)
          const timeB = this.parseRelativeTime(b.time)
          return timeA - timeB // Sort by actual time difference (smaller = more recent)
        })
        
        // Remove duplicates based on description and limit to 8 items
        const uniqueActivities = activities.filter((activity, index, self) => 
          index === self.findIndex(a => a.description === activity.description)
        ).slice(0, 8)
        
        this.recentActivities = uniqueActivities
        console.log(`Loaded ${this.recentActivities.length} recent activities`)
        
      } catch (error) {
        console.error('Error fetching recent activities:', error)
        // Set fallback activities on error
        this.recentActivities = [{
          type: 'error',
          icon: 'fas fa-exclamation-triangle',
          title: 'Unable to Load Activities',
          description: 'Please check your connection and try again',
          time: 'now'
        }]
      } finally {
        this.loadingActivities = false
      }
    },
    
    truncateText(text, maxLength) {
      if (!text) return 'Unknown'
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },
    
    formatRelativeTime(dateString) {
      if (!dateString) return 'Unknown time'
      
      try {
        const date = new Date(dateString)
        const now = new Date()
        const diffInSeconds = Math.floor((now - date) / 1000)
        
        if (diffInSeconds < 60) {
          return 'Just now'
        } else if (diffInSeconds < 3600) {
          const minutes = Math.floor(diffInSeconds / 60)
          return `${minutes} minute${minutes === 1 ? '' : 's'} ago`
        } else if (diffInSeconds < 86400) {
          const hours = Math.floor(diffInSeconds / 3600)
          return `${hours} hour${hours === 1 ? '' : 's'} ago`
        } else if (diffInSeconds < 604800) {
          const days = Math.floor(diffInSeconds / 86400)
          return `${days} day${days === 1 ? '' : 's'} ago`
        } else {
          const weeks = Math.floor(diffInSeconds / 604800)
          return `${weeks} week${weeks === 1 ? '' : 's'} ago`
        }
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Unknown time'
      }
    },
    
    parseRelativeTime(timeString) {
      // Convert relative time back to seconds for sorting
      if (timeString === 'Just now') return 0
      
      const match = timeString.match(/(\d+)\s+(minute|hour|day|week)s?\s+ago/)
      if (match) {
        const value = parseInt(match[1])
        const unit = match[2]
        
        switch (unit) {
          case 'minute': return value * 60
          case 'hour': return value * 3600
          case 'day': return value * 86400
          case 'week': return value * 604800
          default: return 999999
        }
      }
      
      return 999999 // Unknown time goes to end
    },
    
    refreshRecentActivities() {
      this.fetchRecentActivities()
    },

    async fetchDashboardData() {
      try {
        console.log('Starting fetchDashboardData...')
        console.log('Request payload:', {
          xAxis: this.selectedXAxis,
          yAxis: this.selectedYAxis
        })

        // First fetch the dashboard data
        const [dashboardResponse, analyticsResponse] = await Promise.all([
          this.api.complianceService.getComplianceDashboard(),
          this.api.complianceService.getComplianceAnalytics({
            xAxis: this.selectedXAxis,
            yAxis: this.selectedYAxis
          })
        ])

        console.log('Dashboard API Response:', dashboardResponse.data)
        console.log('Analytics API Response:', analyticsResponse.data)

        if (dashboardResponse.data.success && analyticsResponse.data.success) {
          // Update dashboard metrics
          this.dashboardData = {
            status_counts: dashboardResponse.data.data.summary.status_counts || {},
            total_count: dashboardResponse.data.data.summary.total_count || 0,
            total_findings: dashboardResponse.data.data.summary.total_findings || 0,
            approval_rate: analyticsResponse.data.dashboardData.approval_rate || 0
          }
          
          // Update chart data
          this.chartData = analyticsResponse.data.chartData
          console.log('Chart data updated:', this.chartData)
          
          // Wait for the next tick to ensure DOM is updated
          await this.$nextTick()
          this.updateChart()
        } else {
          throw new Error(dashboardResponse.data.message || analyticsResponse.data.message || 'API request failed')
        }
      } catch (error) {
        console.error('Error in fetchDashboardData:', error)
        // Set default values on error
        this.dashboardData = {
          status_counts: {
            approved: 0,
            active: 0,
            under_review: 0
          },
          total_count: 0,
          total_findings: 0,
          approval_rate: 0
        }
        this.chartData = {
          labels: ['High', 'Medium', 'Low'],
          datasets: [{
            label: 'Sample Data',
            data: [10, 12, 5],
            backgroundColor: ['rgba(244, 67, 54, 0.6)', 'rgba(255, 152, 0, 0.6)', 'rgba(76, 175, 80, 0.6)'],
            borderColor: ['#F44336', '#FF9800', '#4CAF50'],
            borderWidth: 1
          }]
        }
        await this.$nextTick()
        this.updateChart()
      }
    },
    updateChart() {
      try {
        console.log('Updating chart with type:', this.selectedChartType)
        console.log('Chart data:', this.chartData)
        
        // Destroy existing chart first
        this.destroyChart()

        // Wait a bit to ensure cleanup is complete
        setTimeout(() => {
          try {
            // Get the canvas element
            const canvas = document.getElementById(this.chartId)
            if (!canvas) {
              console.error('Chart canvas not found')
              return
            }

            // Clear the canvas context
            const ctx = canvas.getContext('2d')
            if (ctx) {
              ctx.clearRect(0, 0, canvas.width, canvas.height)
            }

            // Create the chart configuration
            const config = this.createChartConfig()
            console.log('Chart config:', config)

            // Create new chart instance
            this.chart = new ChartJS(canvas, config)
            console.log('Chart created successfully')
          } catch (innerError) {
            console.error('Error in inner chart creation:', innerError)
          }
        }, 100)
      } catch (error) {
        console.error('Error in updateChart:', error)
        this.chart = null
      }
    },
    createChartConfig() {
      if (!this.chartData || !this.chartData.labels || this.chartData.labels.length === 0) {
        console.log('No chart data available, using fallback')
        return {
          type: this.selectedChartType,
          data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
              label: 'Sample Data',
              data: [10, 12, 5],
              backgroundColor: this.selectedChartType === 'bar' ? 
                ['rgba(244, 67, 54, 0.6)', 'rgba(255, 152, 0, 0.6)', 'rgba(76, 175, 80, 0.6)'] :
                ['rgba(244, 67, 54, 0.8)', 'rgba(255, 152, 0, 0.8)', 'rgba(76, 175, 80, 0.8)'],
              borderColor: ['#F44336', '#FF9800', '#4CAF50'],
              borderWidth: 1
            }]
          },
          options: this.getChartOptions()
        }
      }

      // Create dataset with proper colors
      const dataset = {
        label: this.chartData.datasets[0]?.label || `Compliance by ${this.selectedYAxis.replace('By ', '')}`,
        data: this.chartData.datasets[0]?.data || [],
        backgroundColor: this.getBackgroundColors(),
        borderColor: this.getBorderColors(),
        borderWidth: 1
      }

      // Add line-specific properties
      if (this.selectedChartType === 'line') {
        dataset.tension = 0.1
        dataset.fill = false
        dataset.pointBackgroundColor = this.getBorderColors()
        dataset.pointBorderColor = this.getBorderColors()
        dataset.pointRadius = 4
        dataset.pointHoverRadius = 6
      }

      // Add pie/doughnut specific properties
      if (['pie', 'doughnut'].includes(this.selectedChartType)) {
        dataset.backgroundColor = this.getBackgroundColors().map(color => 
          color.replace('0.6', '0.8') // Make pie/doughnut colors more opaque
        )
      }

      return {
        type: this.selectedChartType,
        data: {
          labels: this.chartData.labels,
          datasets: [dataset]
        },
        options: this.getChartOptions()
      }
    },
    getChartOptions() {
      const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 800,
          easing: 'easeInOutQuad'
        },
        plugins: {
          legend: {
            display: true,
            position: ['pie', 'doughnut'].includes(this.selectedChartType) ? 'right' : 'top',
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 6,
            displayColors: true,
            callbacks: {
              label: (context) => {
                if (['pie', 'doughnut'].includes(this.selectedChartType)) {
                  const label = context.label || ''
                  const value = context.raw || 0
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
                return `${context.dataset.label}: ${context.raw}`
              }
            }
          }
        },
        layout: {
          padding: {
            top: 10,
            bottom: 10,
            left: 10,
            right: 10
          }
        }
      }

      // Add scales for bar and line charts
      if (['bar', 'line'].includes(this.selectedChartType)) {
        options.scales = {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 11
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
              stepSize: 1,
              precision: 0,
              font: {
                size: 11
              }
            }
          }
        }
      }

      // Special options for doughnut charts
      if (this.selectedChartType === 'doughnut') {
        options.cutout = '60%'
      }

      return options
    },
    changeChartType(newType) {
      console.log('Changing chart type from', this.selectedChartType, 'to', newType)
      
      if (this.selectedChartType === newType) {
        return
      }
      
      this.selectedChartType = newType
      
      // Use a slight delay to ensure the UI updates properly
      this.$nextTick(() => {
        setTimeout(() => {
          this.updateChart()
        }, 50)
      })
    },
    getBackgroundColors() {
      const colorMaps = {
        Criticality: {
          'High': 'rgba(244, 67, 54, 0.6)',
          'Medium': 'rgba(255, 152, 0, 0.6)',
          'Low': 'rgba(76, 175, 80, 0.6)'
        },
        Status: {
          'Approved': 'rgba(76, 175, 80, 0.6)',
          'Under Review': 'rgba(255, 152, 0, 0.6)',
          'Rejected': 'rgba(244, 67, 54, 0.6)',
          'Active': 'rgba(33, 150, 243, 0.6)'
        },
        ActiveInactive: {
          'Active': 'rgba(76, 175, 80, 0.6)',
          'Inactive': 'rgba(158, 158, 158, 0.6)'
        },
        ManualAutomatic: {
          'Manual': 'rgba(33, 150, 243, 0.6)',
          'Automatic': 'rgba(156, 39, 176, 0.6)'
        },
        MandatoryOptional: {
          'Mandatory': 'rgba(244, 67, 54, 0.6)',
          'Optional': 'rgba(255, 152, 0, 0.6)'
        },
        MaturityLevel: {
          'Initial': 'rgba(244, 67, 54, 0.6)',
          'Developing': 'rgba(255, 152, 0, 0.6)',
          'Defined': 'rgba(255, 235, 59, 0.6)',
          'Managed': 'rgba(76, 175, 80, 0.6)',
          'Optimizing': 'rgba(33, 150, 243, 0.6)'
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')][label] || 'rgba(158, 158, 158, 0.6)'
      ) || []
    },
    getBorderColors() {
      const colorMaps = {
        Criticality: {
          'High': '#F44336',
          'Medium': '#FF9800',
          'Low': '#4CAF50'
        },
        Status: {
          'Approved': '#4CAF50',
          'Under Review': '#FF9800',
          'Rejected': '#F44336',
          'Active': '#2196F3'
        },
        ActiveInactive: {
          'Active': '#4CAF50',
          'Inactive': '#9E9E9E'
        },
        ManualAutomatic: {
          'Manual': '#2196F3',
          'Automatic': '#9C27B0'
        },
        MandatoryOptional: {
          'Mandatory': '#F44336',
          'Optional': '#FF9800'
        },
        MaturityLevel: {
          'Initial': '#F44336',
          'Developing': '#FF9800',
          'Defined': '#FFEB3B',
          'Managed': '#4CAF50',
          'Optimizing': '#2196F3'
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')][label] || '#9E9E9E'
      ) || []
    },
    refreshData() {
      this.fetchDashboardData()
      this.fetchRecentActivities()
    }
  }
}
</script>

<style>
@import './ComplianceDashboard.css';

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

/* Activity loading and empty states */
.activity-loading, .activity-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: #64748b;
  font-size: 0.9rem;
}

.activity-loading i, .activity-empty i {
  font-size: 1.2rem;
}

.more-options {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.more-options:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}
</style> 