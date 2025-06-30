<template>
  <div class="kpi-container">
    <!-- FIRST ROW: Severity of Issues -->
    <div class="kpi-row">
      <!-- Severity of Issues Card -->
      <div class="kpi-card-wrapper" style="flex: 1; min-width: 500px;">
        <v-card 
          :loading="severityLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Period Selector -->
              <div class="period-selector">
                <button 
                  v-for="p in ['month', 'quarter', 'year']" 
                  :key="p"
                  class="period-button"
                  :class="{ active: severityPeriod === p }"
                  @click="changeSeverityPeriod(p)"
                >
                  {{ p.charAt(0).toUpperCase() + p.slice(1) }}
                </button>
              </div>
              
                            <!-- Severity Bar Chart -->
              <div class="severity-chart">
                <div v-for="(item, index) in severityMetrics.severity_distribution" :key="index" class="severity-bar">
                  <div class="severity-label">{{ formatSeverityLabel(item.severity) }}</div>
                  <div class="severity-bar-container">
                    <div 
                      class="severity-bar-fill" 
                      :style="{ 
                        width: getBarWidth(item.count, severityMetrics.total_issues), 
                        backgroundColor: item.color 
                      }"
                    ></div>
                    <span class="severity-bar-value">{{ item.count }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-3 text-center">Severity of Issues</div>
              
              <!-- Summary info -->
              <div class="target-info">
                <div class="target-label">Most common: {{ formatSeverityLabel(severityMetrics.most_common) || 'None' }}</div>
                <div class="target-label" v-if="severityMetrics.major_count > 0">
                  <span class="critical-count">{{ severityMetrics.major_count }}</span> Major, 
                  <span class="high-count">{{ severityMetrics.minor_count }}</span> Minor issues
                </div>
                <div class="target-label" v-else>No major issues found</div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="severityError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ severityError }}
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- SECOND ROW: Audit Cycle Time, Time to Close Findings, Non-Compliance Issues -->
    <div class="kpi-row">
      <!-- Audit Cycle Time Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="cycleTimeLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Framework Selector -->
              <div class="filter-dropdown">
                <select 
                  v-model="selectedCycleFrameworkId" 
                  @change="changeCycleFramework"
                  class="filter-select"
                >
                  <option value="">All Frameworks</option>
                  <option 
                    v-for="framework in cycleFrameworks" 
                    :key="framework.id" 
                    :value="framework.id"
                  >
                    {{ framework.name }}
                  </option>
                </select>
              </div>

              <!-- Time Badge -->
              <div class="time-badge" :class="getEfficiencyClass">
                {{ cycleTimeMetrics.overall_avg_days || 0 }}
                <span class="time-unit">days</span>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-4 text-center">Audit Cycle Time</div>
              
              <!-- Target info -->
              <div class="target-info">
                <div class="target-label">Target: {{ cycleTimeMetrics.target_days || 30 }} days</div>
                <div class="efficiency-badge" :class="getEfficiencyClass">
                  {{ cycleTimeMetrics.efficiency || 'N/A' }}
                </div>
              </div>
              
              <!-- Line Chart for Monthly Cycle Time -->
              <div v-if="cycleTimeMonthlyData.length > 0" class="trend-chart-container">
                <div class="chart-title">Monthly Cycle Time Trend</div>
                <div class="line-chart">
                  <!-- Background grid lines -->
                  <div class="chart-grid">
                    <div v-for="(val, index) in getCycleTimeYAxisValues" 
                         :key="index" 
                         class="chart-grid-line" 
                         :style="{ bottom: `${(val/cycleTimeChartMax) * 100}%` }">
                    </div>
                  </div>
                  
                  <!-- Y-axis labels -->
                  <div class="chart-y-axis">
                    <div v-for="(val, index) in getCycleTimeYAxisValues" 
                         :key="index" 
                         class="chart-y-label" 
                         :style="{ bottom: `${(val/cycleTimeChartMax) * 100}%` }">
                      {{ val }}
                    </div>
                  </div>
                  
                  <!-- Threshold line -->
                  <div class="threshold-line" 
                       :style="{ bottom: `${(cycleTimeMetrics.target_days/cycleTimeChartMax) * 100}%` }">
                  </div>
                  
                  <!-- The data points -->
                  <div 
                    v-for="(point, index) in cycleTimeMonthlyData" 
                    :key="index"
                    class="chart-point"
                    :class="{ 'point-above-threshold': point.avg_cycle_days > cycleTimeMetrics.target_days }"
                    :style="{ 
                      left: `${(index / (cycleTimeMonthlyData.length - 1)) * 100}%`,
                      bottom: `${(point.avg_cycle_days / cycleTimeChartMax) * 100}%`
                    }"
                    :title="`${point.month}: ${point.avg_cycle_days} days`"
                    @mouseover="showCycleTimeTooltip(index, $event)"
                    @mouseleave="hideCycleTimeTooltip()"
                  ></div>
                  
                  <!-- The connecting lines -->
                  <div
                    v-for="(point, index) in cycleTimeMonthlyData.slice(0, -1)" 
                    :key="`line-${index}`"
                    class="chart-line"
                    :class="{ 'line-above-threshold': isLineAboveThreshold(index) }"
                    :style="getCycleTimeLineStyle(index)"
                  ></div>
                  
                  <!-- Tooltip -->
                  <div 
                    v-if="cycleTimeTooltipVisible" 
                    class="chart-tooltip"
                    :style="cycleTimeTooltipStyle"
                  >
                    <div class="tooltip-month">{{ cycleTimeTooltipData.month }}</div>
                    <div class="tooltip-rate">{{ cycleTimeTooltipData.avg_cycle_days }} days</div>
                    <div class="tooltip-threshold" v-if="cycleTimeTooltipData.avg_cycle_days > cycleTimeMetrics.target_days">
                      {{ cycleTimeTooltipData.avg_cycle_days - cycleTimeMetrics.target_days }} days above target
                    </div>
                    <div class="tooltip-threshold good" v-else>
                      {{ cycleTimeMetrics.target_days - cycleTimeTooltipData.avg_cycle_days }} days below target
                    </div>
                  </div>
                </div>
                
                <!-- X-axis labels -->
                <div class="chart-labels">
                  <div 
                    v-for="(point, index) in cycleTimeMonthlyData" 
                    :key="`label-${index}`"
                    class="chart-label"
                    :style="{ 
                      left: `${(index / (cycleTimeMonthlyData.length - 1)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }"
                  >
                    {{ getShortMonth(point.month) }}
                  </div>
                </div>
                
                <!-- Legend -->
                <div class="chart-legend">
                  <div class="legend-item">
                    <div class="legend-color cycle-time-color"></div>
                    <div class="legend-label">Cycle Time</div>
                  </div>
                  <div class="legend-item">
                    <div class="legend-color threshold-color"></div>
                    <div class="legend-label">Target ({{ cycleTimeMetrics.target_days }} days)</div>
                  </div>
                </div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="cycleTimeError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ cycleTimeError }}
          </v-card-text>
        </v-card>
      </div>

      <!-- Time to Close Findings Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="timeToCloseLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Period Selector -->
              <div class="period-selector">
                <button 
                  v-for="p in ['month', 'quarter', 'year']" 
                  :key="p"
                  class="period-button"
                  :class="{ active: timeToClosePeriod === p }"
                  @click="changeTimeToClosePeriod(p)"
                >
                  {{ p.charAt(0).toUpperCase() + p.slice(1) }}
                </button>
              </div>

              <!-- Toggle for Number/Percentage View -->
              <div class="view-toggle-container mt-2">
                <button 
                  class="view-toggle-button"
                  :class="{ active: timeToCloseViewMode === 'number' }"
                  @click="timeToCloseViewMode = 'number'"
                >
                  Days
                </button>
                <button 
                  class="view-toggle-button"
                  :class="{ active: timeToCloseViewMode === 'percentage' }"
                  @click="timeToCloseViewMode = 'percentage'"
                >
                  Percentage
                </button>
              </div>

              <!-- Flip Card Container -->
              <div class="flip-card-container" @click="toggleTimeToCloseFlip">
                <div class="flip-card" :class="{ 'flipped': timeToCloseFlipped }">
                  <!-- Front Side (Chart) -->
                  <div class="flip-card-front">
              <div class="time-to-close-container">
                      <div class="left-section" style="width: 100%;">
                  <!-- Close Time Badge -->
                  <div class="time-badge" :class="getCloseTimeClass">
                          <template v-if="timeToCloseViewMode === 'number'">
                    {{ timeToCloseMetrics.avg_close_days || 0 }}
                    <span class="time-unit">days</span>
                          </template>
                          <template v-else>
                            {{ getTimeToClosePercentage }}%
                          </template>
                  </div>
                  
                  <!-- Title -->
                  <div class="text-h6 mt-3 text-center">Time to Close</div>
                  
                  <!-- Target info -->
                  <div class="target-info">
                    <div class="target-label">Target: {{ timeToCloseMetrics.target_days || 14 }} days</div>
                    <div class="efficiency-badge" :class="getCloseTimeClass">
                      {{ timeToCloseMetrics.efficiency || 'N/A' }}
                    </div>
                  </div>
                  
                  <!-- Trend Line Chart for Monthly Close Time -->
                  <div v-if="timeToCloseMonthlyTrend.length > 0" class="close-time-chart-container">
                    <div class="chart-title">Monthly Trend</div>
                    <div class="line-chart close-time-chart">
                      <!-- Background grid lines -->
                      <div class="chart-grid">
                        <div v-for="(val, index) in getCloseTimeYAxisValues" 
                             :key="index" 
                             class="chart-grid-line" 
                             :style="{ bottom: `${(val/closeTimeChartMax) * 100}%` }">
                        </div>
                      </div>
                      
                      <!-- Y-axis labels -->
                      <div class="chart-y-axis">
                        <div v-for="(val, index) in getCloseTimeYAxisValues" 
                             :key="index" 
                             class="chart-y-label" 
                             :style="{ bottom: `${(val/closeTimeChartMax) * 100}%` }">
                                <template v-if="timeToCloseViewMode === 'number'">
                          {{ val }}
                                </template>
                                <template v-else>
                                  {{ Math.round((val / timeToCloseMetrics.target_days) * 100) }}%
                                </template>
                        </div>
                      </div>
                      
                      <!-- Threshold line -->
                      <div class="threshold-line" 
                           :style="{ bottom: `${(timeToCloseMetrics.target_days/closeTimeChartMax) * 100}%` }">
                      </div>
                      
                      <!-- The data points -->
                      <div 
                        v-for="(point, index) in timeToCloseMonthlyTrend" 
                        :key="index"
                        class="chart-point"
                        :class="{ 'point-above-threshold': point.avg_close_days > timeToCloseMetrics.target_days }"
                        :style="{ 
                          left: `${(index / (timeToCloseMonthlyTrend.length - 1)) * 100}%`,
                          bottom: `${(point.avg_close_days / closeTimeChartMax) * 100}%`
                        }"
                        :title="`${point.month}: ${point.avg_close_days} days`"
                        @mouseover="showCloseTimeTooltip(index, $event)"
                        @mouseleave="hideCloseTimeTooltip()"
                      ></div>
                      
                      <!-- The connecting lines -->
                      <div
                        v-for="(point, index) in timeToCloseMonthlyTrend.slice(0, -1)" 
                        :key="`line-${index}`"
                        class="chart-line"
                        :class="{ 'line-above-threshold': isCloseTimeLineAboveThreshold(index) }"
                        :style="getCloseTimeLineStyle(index)"
                      ></div>
                      
                      <!-- Tooltip -->
                      <div 
                        v-if="closeTimeTooltipVisible" 
                        class="chart-tooltip"
                        :style="closeTimeTooltipStyle"
                      >
                        <div class="tooltip-month">{{ closeTimeTooltipData.month }}</div>
                              <div class="tooltip-rate">
                                <template v-if="timeToCloseViewMode === 'number'">
                                  {{ closeTimeTooltipData.avg_close_days }} days
                                </template>
                                <template v-else>
                                  {{ Math.round((closeTimeTooltipData.avg_close_days / timeToCloseMetrics.target_days) * 100) }}%
                                </template>
                              </div>
                        <div class="tooltip-threshold" v-if="closeTimeTooltipData.avg_close_days > timeToCloseMetrics.target_days">
                          {{ closeTimeTooltipData.avg_close_days - timeToCloseMetrics.target_days }} days above target
                        </div>
                        <div class="tooltip-threshold good" v-else>
                          {{ timeToCloseMetrics.target_days - closeTimeTooltipData.avg_close_days }} days below target
                        </div>
                      </div>
                    </div>
                    
                    <!-- X-axis labels -->
                    <div class="chart-labels close-time-labels">
                      <div 
                        v-for="(point, index) in timeToCloseMonthlyTrend" 
                        :key="`label-${index}`"
                        class="chart-label"
                        :style="{ 
                          left: `${(index / (timeToCloseMonthlyTrend.length - 1)) * 100}%`,
                          transform: 'translateX(-50%)'
                        }"
                      >
                        {{ getShortMonth(point.month) }}
                      </div>
                    </div>
                  </div>
                </div>

                      <!-- Right section with Top Oldest Open Findings removed -->
                    </div>
                    
                    <!-- Click to flip instruction -->
                    <div class="flip-instruction">
                      <v-icon small class="mr-1">mdi-flip-horizontal</v-icon>
                      Click to view detailed table
                    </div>
                  </div>
                  
                  <!-- Back Side (Table) -->
                  <div class="flip-card-back">
                    <div class="time-to-close-table-container">
                      <div class="section-title">Time to Close Details</div>
                      
                      <!-- Combined Findings Table -->
                      <div class="findings-table-container">
                        <table class="findings-table full-width">
                        <thead>
                          <tr>
                              <th>Month</th>
                              <th>Avg Days</th>
                              <th>Target</th>
                              <th>Variance</th>
                              <th>Closed</th>
                              <th>Total</th>
                              <th>Rate</th>
                          </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(point, index) in timeToCloseMonthlyTrend" :key="index"
                                :class="{'critical-age': point.avg_close_days > timeToCloseMetrics.target_days * 1.5, 
                                        'warning-age': point.avg_close_days > timeToCloseMetrics.target_days && point.avg_close_days <= timeToCloseMetrics.target_days * 1.5,
                                        'good-age': point.avg_close_days <= timeToCloseMetrics.target_days}">
                              <td>{{ point.month }}</td>
                              <td>{{ point.avg_close_days.toFixed(1) }}</td>
                              <td>{{ timeToCloseMetrics.target_days }}</td>
                              <td :class="{'negative-variance': point.avg_close_days > timeToCloseMetrics.target_days, 
                                          'positive-variance': point.avg_close_days <= timeToCloseMetrics.target_days}">
                                {{ (point.avg_close_days - timeToCloseMetrics.target_days).toFixed(1) }}
                              </td>
                              <td>{{ point.closed_count || 0 }}</td>
                              <td>{{ point.total_count || 0 }}</td>
                              <td>{{ point.closure_rate ? point.closure_rate.toFixed(1) + '%' : 'N/A' }}</td>
                          </tr>
                        </tbody>
                          <tfoot>
                            <tr class="summary-row">
                              <td><strong>Overall</strong></td>
                              <td><strong>{{ timeToCloseMetrics.avg_close_days.toFixed(1) }}</strong></td>
                              <td><strong>{{ timeToCloseMetrics.target_days }}</strong></td>
                              <td :class="{'negative-variance': timeToCloseMetrics.avg_close_days > timeToCloseMetrics.target_days, 
                                          'positive-variance': timeToCloseMetrics.avg_close_days <= timeToCloseMetrics.target_days}">
                                <strong>{{ (timeToCloseMetrics.avg_close_days - timeToCloseMetrics.target_days).toFixed(1) }}</strong>
                              </td>
                              <td><strong>{{ timeToCloseMetrics.closed_count || 0 }}</strong></td>
                              <td><strong>{{ timeToCloseMetrics.total_count || 0 }}</strong></td>
                              <td><strong>{{ timeToCloseMetrics.closure_rate ? timeToCloseMetrics.closure_rate.toFixed(1) + '%' : 'N/A' }}</strong></td>
                            </tr>
                          </tfoot>
                      </table>
                      </div>
                    </div>
                    
                    <!-- Click to flip back instruction -->
                    <div class="flip-instruction">
                      <v-icon small class="mr-1">mdi-flip-horizontal</v-icon>
                      Click to view chart
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="timeToCloseError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ timeToCloseError }}
          </v-card-text>
        </v-card>
      </div>

      <!-- Non-Compliance Issues Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="issuesLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Period Selector -->
                <div class="period-selector">
                  <button 
                    v-for="p in ['month', 'quarter', 'year']" 
                    :key="p"
                    class="period-button"
                    :class="{ active: issuesPeriod === p }"
                    @click="changeIssuesPeriod(p)"
                  >
                    {{ p.charAt(0).toUpperCase() + p.slice(1) }}
                  </button>
                </div>

              <!-- Severity Filter -->
              <div class="severity-filter">
                  <button 
                  v-for="s in ['all', 'major', 'minor', 'none']" 
                    :key="s"
                    class="severity-button"
                    :class="{ active: issuesSeverity === s }"
                    @click="changeIssuesSeverity(s)"
                  >
                    {{ s.charAt(0).toUpperCase() + s.slice(1) }}
                  </button>
              </div>
              
              <!-- Issues Count Badge -->
              <div class="issues-badge" :class="getIssuesTrendClass">
                {{ issuesMetrics.total_count || 0 }}
                <span v-if="issuesMetrics.trend_direction !== 'stable'" class="trend-indicator">
                  <v-icon size="small" :color="getIssuesTrendColor">
                    {{ issuesMetrics.trend_direction === 'up' ? 'mdi-arrow-up' : 'mdi-arrow-down' }}
                  </v-icon>
                  {{ Math.abs(issuesMetrics.trend_percentage) }}%
                </span>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-3 text-center">Non-Compliance Issues</div>
              
              <!-- Severity Breakdown -->
              <div class="severity-breakdown">
                <div class="severity-item">
                  <div class="severity-name">Major:</div>
                  <div class="severity-count">{{ getSeverityCount('Major') }}</div>
                </div>
                <div class="severity-item">
                  <div class="severity-name">Minor:</div>
                  <div class="severity-count">{{ getSeverityCount('Minor') }}</div>
                </div>
                <div class="severity-item">
                  <div class="severity-name">None:</div>
                  <div class="severity-count">{{ getSeverityCount('None') }}</div>
                </div>
              </div>
              
              <!-- Top impacted area if available -->
              <div class="text-body-2 mt-1 text-center" v-if="issuesMetrics.top_areas && issuesMetrics.top_areas.length">
                Top area: {{ issuesMetrics.top_areas[0].compliance_name }} ({{ issuesMetrics.top_areas[0].count }} issues)
              </div>
              <div class="text-body-2 mt-1 text-center" v-else>
                No top areas identified
              </div>
              
              <!-- Monthly Trend Bar Chart -->
              <div v-if="issuesMetrics.monthly_trend && issuesMetrics.monthly_trend.length" class="issues-monthly-chart">
                <div class="chart-title">Monthly Trend</div>
                <div class="monthly-trend-simple">
                  <div 
                    v-for="(month, index) in issuesMetrics.monthly_trend.slice(-2)" 
                    :key="index" 
                    class="month-item"
                  >
                    <div class="month-name">{{ getShortMonth(month.month) }}</div>
                    <div class="month-count">{{ month.count }}</div>
                  </div>
                </div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="issuesError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ issuesError }}
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- THIRD ROW: Closure Rate, Evidence Collection, Report Timeline -->
    <div class="kpi-row">
      <!-- Closure Rate Card -->
      <!-- Findings Closure Rate Card removed and merged with Time to Close -->

      <!-- Evidence Collection Completion Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="evidenceLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Audit selector if needed -->
              <div v-if="auditOptions.length > 0" class="audit-selector">
                <select 
                  v-model="selectedAuditId" 
                  class="audit-select"
                  @change="changeSelectedAudit"
                >
                  <option value="">All Audits</option>
                  <option 
                    v-for="audit in auditOptions" 
                    :key="audit.id" 
                    :value="audit.id"
                  >
                    Audit #{{ audit.id }} - {{ audit.name }}
                  </option>
                </select>
              </div>
              
              <!-- Circular Progress for Evidence Completion -->
              <div class="gauge-container">
                <v-progress-circular
                  :model-value="evidenceMetrics.completion_percentage || 0"
                  :size="130"
                  :width="15"
                  :color="getEvidenceColor"
                  class="gauge-chart"
                >
                  {{ evidenceMetrics.completion_percentage || 0 }}%
                </v-progress-circular>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-3 text-center">Evidence Collection</div>
              
              <!-- Count info -->
              <div class="target-info">
                <div class="target-label">{{ evidenceMetrics.evidence_collected || 0 }} of {{ evidenceMetrics.total_findings || 0 }} findings have evidence</div>
                <div class="efficiency-badge" :class="getEvidenceClass">
                  {{ evidenceMetrics.rating || 'N/A' }}
                </div>
              </div>
              
              <!-- Top Audits with Evidence if not filtered -->
              <div v-if="!selectedAuditId && evidenceBreakdown.length > 0" class="evidence-audits">
                <div class="evidence-audits-title">Top Audits by Evidence Completion</div>
                <div class="evidence-audit-list">
                  <div 
                    v-for="(audit, index) in evidenceBreakdown.slice(0, 3)" 
                    :key="index"
                    class="evidence-audit-item"
                    @click="selectedAuditId = audit.audit_id; changeSelectedAudit()"
                  >
                    <div class="evidence-audit-name">Audit #{{ audit.audit_id }}</div>
                    <div class="evidence-audit-framework">{{ audit.framework_name }}</div>
                    <div class="evidence-audit-progress">
                      <div class="progress-bar-container">
                        <div 
                          class="progress-bar-fill"
                          :style="{ width: `${audit.completion_percentage}%`, backgroundColor: getProgressColor(audit.completion_percentage) }"
                        ></div>
                      </div>
                      <span class="progress-text">{{ audit.completion_percentage }}%</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Evidence Details if filtered by audit -->
              <div v-if="selectedAuditId && evidenceDetails.length > 0" class="evidence-details">
                <div class="evidence-details-title">Evidence Details</div>
                <div class="evidence-detail-summary">
                  <div class="evidence-detail-count">{{ getEvidenceDetailStats.withEvidence }} with evidence</div>
                  <div class="evidence-detail-count">{{ getEvidenceDetailStats.withoutEvidence }} without evidence</div>
                </div>
                <button class="view-all-button" @click="showEvidenceModal = true">
                  View All Evidence
                </button>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="evidenceError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ evidenceError }}
          </v-card-text>
        </v-card>
      </div>

      <!-- Report Timeliness Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="timelinessLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Period Selector -->
              <div class="period-selector">
                <button 
                  v-for="p in ['month', 'quarter', 'year']" 
                  :key="p"
                  class="period-button"
                  :class="{ active: timelinessPeriod === p }"
                  @click="changeTimelinessPeriod(p)"
                >
                  {{ p.charAt(0).toUpperCase() + p.slice(1) }}
                </button>
              </div>
              
              <!-- Large Percentage Display instead of donut chart -->
              <div class="percentage-display" :style="{ color: getTimelinessColor }">
                <span class="percentage-value">{{ timelinessMetrics.percent_on_time || 0 }}%</span>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-3 text-center">Report Timeliness</div>
              
              <!-- Summary info -->
              <div class="target-info">
                <div class="target-label">{{ timelinessMetrics.on_time_count || 0 }} of {{ timelinessMetrics.total_reports || 0 }} reports on time</div>
                <div class="efficiency-badge" :class="getTimelinessClass">
                  {{ timelinessMetrics.rating || 'N/A' }}
                </div>
              </div>
              
              <!-- Avg Days Difference -->
              <div class="text-body-2 mt-1 text-center">
                {{ timelinessMetrics.avg_days_difference > 0 ? 'Avg ' + timelinessMetrics.avg_days_difference + ' days late' : 'Avg ' + Math.abs(timelinessMetrics.avg_days_difference) + ' days early' }}
              </div>
              
              <!-- Histogram -->
              <div class="histogram-container" v-if="timelinessHistogram.length > 0">
                <div class="histogram-title">Report Submission Timeliness</div>
                <div class="histogram-chart">
                  <div 
                    v-for="(bar, index) in timelinessHistogram" 
                    :key="index"
                    class="histogram-bar"
                    :title="`${bar.label}: ${bar.count} reports (${bar.percentage}%)`"
                    @mouseover="showHistogramTooltip(bar, $event)"
                    @mouseleave="hideHistogramTooltip()"
                  >
                    <div 
                      class="histogram-bar-fill"
                      :style="{ 
                        height: getBarHeight(bar.percentage), 
                        backgroundColor: bar.color 
                      }"
                    ></div>
                    <div class="histogram-bar-label">{{ bar.label }}</div>
                    <div class="histogram-bar-count">{{ bar.count }}</div>
                  </div>
                </div>
              </div>
              
              <!-- Late Reports Button -->
              <button 
                v-if="timelinessLateReports.length > 0"
                class="view-late-button"
                @click="showLateReportsModal = true"
              >
                View {{ timelinessLateReports.length }} Late Reports
              </button>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="timelinessError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ timelinessError }}
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- FOURTH ROW: Compliance Readiness, Audit Completion -->
    <div class="kpi-row">
      <!-- Compliance Readiness Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="readinessLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Filter controls -->
              <div class="filter-controls" v-if="readinessFrameworks.length > 0 || readinessPolicies.length > 0">
                <div class="filter-selectors">
                  <div class="filter-dropdown" v-if="readinessFrameworks.length > 0">
                    <select 
                      v-model="selectedFrameworkId" 
                      @change="changeFramework(selectedFrameworkId)"
                      class="filter-select"
                    >
                      <option value="">All Frameworks</option>
                      <option 
                        v-for="framework in readinessFrameworks" 
                        :key="framework.framework_id" 
                        :value="framework.framework_id"
                      >
                        {{ framework.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="filter-dropdown" v-if="readinessPolicies.length > 0">
                    <select 
                      v-model="selectedPolicyId" 
                      @change="changePolicy(selectedPolicyId)"
                      class="filter-select"
                    >
                      <option value="">All Policies</option>
                      <option 
                        v-for="policy in readinessPolicies" 
                        :key="policy.policy_id" 
                        :value="policy.policy_id"
                      >
                        {{ policy.name }}
                      </option>
                    </select>
                  </div>
                </div>
                
                <button 
                  v-if="selectedFrameworkId || selectedPolicyId"
                  @click="resetFilters" 
                  class="reset-filter-button"
                >
                  Reset Filters
                </button>
              </div>
              
              <!-- Gauge Chart -->
              <div class="gauge-container">
                <v-progress-circular
                  :model-value="readinessMetrics.readiness_percentage || 0"
                  :size="150"
                  :width="15"
                  :color="readinessMetrics.color || 'info'"
                  class="gauge-chart"
                >
                  {{ readinessMetrics.readiness_percentage || 0 }}%
                </v-progress-circular>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-4 text-center">Compliance Readiness</div>
              
              <!-- Description -->
              <div class="target-info">
                <div class="target-label">
                  {{ readinessMetrics.implemented_count || 0 }} of {{ readinessMetrics.total_defined || 0 }} controls implemented
                </div>
                <div class="efficiency-badge" :class="getReadinessClass">
                  {{ readinessMetrics.rating || 'N/A' }}
                </div>
              </div>
              
              <!-- Framework/Policy info if filtered -->
              <div v-if="selectedFrameworkId || selectedPolicyId" class="filter-info">
                <div class="filter-name">
                  {{ selectedFrameworkId ? 
                     'Framework: ' + (readinessFrameworks.find(f => f.framework_id == selectedFrameworkId)?.name || '') : 
                     'Policy: ' + (readinessPolicies.find(p => p.policy_id == selectedPolicyId)?.name || '') }}
                </div>
              </div>
              
              <!-- View breakdown button -->
              <button 
                v-if="!selectedFrameworkId && !selectedPolicyId && readinessFrameworks.length > 0"
                class="view-breakdown-button"
                @click="showFrameworksModal = true"
              >
                View Framework Breakdown
              </button>
              
              <!-- Criticality Breakdown -->
              <div v-if="readinessCriticality.length > 0" class="criticality-breakdown">
                <div class="breakdown-title">Breakdown by Criticality</div>
                <div class="criticality-bars">
                  <div 
                    v-for="(item, index) in readinessCriticality" 
                    :key="index"
                    class="criticality-bar-item"
                  >
                    <div class="criticality-label">{{ item.criticality }}</div>
                    <div class="progress-bar-container">
                      <div 
                        class="progress-bar-fill"
                        :style="{ 
                          width: `${item.readiness_percentage}%`, 
                          backgroundColor: getCriticalityColor(item.criticality) 
                        }"
                      ></div>
                      <span class="progress-text">{{ item.readiness_percentage }}%</span>
                    </div>
                    <div class="criticality-counts">
                      {{ item.implemented_count }} / {{ item.total_defined }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="readinessError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ readinessError }}
          </v-card-text>
        </v-card>
      </div>

      <!-- Audit Completion Card -->
      <div class="kpi-card-wrapper">
        <v-card 
          :loading="auditLoading" 
          class="kpi-card"
          elevation="2"
        >
          <v-card-item>
            <div class="d-flex flex-column align-center pa-4">
              <!-- Period Selector -->
              <div class="period-selector">
                <button 
                  v-for="p in ['day', 'week', 'month', 'year']" 
                  :key="p"
                  class="period-button"
                  :class="{ active: period === p }"
                  @click="changePeriod(p)"
                >
                  {{ p.charAt(0).toUpperCase() + p.slice(1) }}
                </button>
              </div>
              
              <!-- Gauge Chart -->
              <div class="gauge-container">
                <v-progress-circular
                  :model-value="auditMetrics.completion_percentage || 0"
                  :size="150"
                  :width="15"
                  :color="getCompletionColor"
                  class="gauge-chart"
                >
                  {{ auditMetrics.completion_percentage || 0 }}%
                </v-progress-circular>
              </div>
              
              <!-- Title -->
              <div class="text-h6 mt-4 text-center">Audit Completion</div>
              
              <!-- Metrics Grid -->
              <div class="metrics-grid">
                <div class="metric-item">
                  <div class="metric-value">{{ auditMetrics.total_audits || 0 }}</div>
                  <div class="metric-label">Planned</div>
                </div>
                <div class="metric-item">
                  <div class="metric-value">{{ auditMetrics.completed_audits || 0 }}</div>
                  <div class="metric-label">Completed</div>
                </div>
              </div>
              
              <!-- Bar Chart for Monthly Comparison -->
              <div v-if="auditMonthlyData.length > 0" class="bar-chart-container">
                <div class="chart-title">Monthly Audit Completion</div>
                <div class="bar-chart">
                  <div class="chart-y-axis">
                    <div 
                      v-for="(val, index) in getYAxisValues" 
                      :key="index" 
                      class="y-axis-label" 
                      :style="{ bottom: `${(val/chartMax) * 100}%` }"
                    >
                      {{ val }}
                    </div>
                  </div>
                  
                  <div class="bar-groups-container">
                    <div 
                      v-for="(month, index) in auditMonthlyData" 
                      :key="index" 
                      class="bar-group"
                    >
                      <!-- Planned Bar -->
                      <div class="bar-container">
                        <div 
                          class="bar planned-bar" 
                          :style="{ 
                            height: `${(month.planned / chartMax) * 100}%`,
                            opacity: month.planned > 0 ? 1 : 0.3
                          }"
                          :title="`Planned: ${month.planned}`"
                        ></div>
                      </div>
                      
                      <!-- Completed Bar -->
                      <div class="bar-container">
                        <div 
                          class="bar completed-bar" 
                          :style="{ 
                            height: `${(month.completed / chartMax) * 100}%`,
                            opacity: month.completed > 0 ? 1 : 0.3
                          }"
                          :title="`Completed: ${month.completed}`"
                        ></div>
                      </div>
                      
                      <!-- Month Label -->
                      <div class="month-label">{{ month.month }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- Legend -->
                <div class="chart-legend">
                  <div class="legend-item">
                    <div class="legend-color planned-color"></div>
                    <div class="legend-label">Planned</div>
                  </div>
                  <div class="legend-item">
                    <div class="legend-color completed-color"></div>
                    <div class="legend-label">Completed</div>
                  </div>
                </div>
              </div>
            </div>
          </v-card-item>

          <!-- Error message -->
          <v-card-text v-if="auditError" class="error-text">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            {{ auditError }}
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- Modals and other components remain unchanged -->
    <!-- Evidence Details Modal -->
    <v-dialog
      v-model="showEvidenceModal"
      max-width="800px"
    >
      <v-card>
        <v-card-title class="modal-title">
          Evidence Details for Audit #{{ selectedAuditId }}
          <v-spacer></v-spacer>
          <v-btn
            icon
            @click="showEvidenceModal = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <div class="evidence-modal-content">
            <div class="evidence-filter">
              <label class="filter-label">Show:</label>
              <div class="filter-buttons">
                <button 
                  class="filter-button" 
                  :class="{ active: evidenceFilter === 'all' }"
                  @click="evidenceFilter = 'all'"
                >
                  All
                </button>
                <button 
                  class="filter-button" 
                  :class="{ active: evidenceFilter === 'with' }"
                  @click="evidenceFilter = 'with'"
                >
                  With Evidence
                </button>
                <button 
                  class="filter-button" 
                  :class="{ active: evidenceFilter === 'without' }"
                  @click="evidenceFilter = 'without'"
                >
                  Without Evidence
                </button>
              </div>
            </div>
            
            <div class="evidence-list">
              <div 
                v-for="(item, index) in filteredEvidenceDetails" 
                :key="index"
                class="evidence-item"
                :class="{ 'has-evidence': item.has_evidence }"
              >
                <div class="evidence-item-header">
                  <div class="evidence-item-id">Finding #{{ item.finding_id }} (Compliance #{{ item.compliance_id }})</div>
                  <div class="evidence-status" :class="{ 'status-positive': item.has_evidence, 'status-negative': !item.has_evidence }">
                    {{ item.has_evidence ? 'Evidence Provided' : 'No Evidence' }}
                  </div>
                </div>
                <div v-if="item.has_evidence" class="evidence-content">
                  <div class="evidence-text">{{ item.evidence }}</div>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Histogram Tooltip -->
    <div 
      v-if="histogramTooltipVisible" 
      class="histogram-tooltip"
      :style="histogramTooltipStyle"
    >
      <div class="tooltip-title">{{ histogramTooltipData.label }}</div>
      <div class="tooltip-count">{{ histogramTooltipData.count }} reports</div>
      <div class="tooltip-percentage">{{ histogramTooltipData.percentage }}% of total</div>
    </div>
    
    <!-- Late Reports Modal -->
    <v-dialog
      v-model="showLateReportsModal"
      max-width="800px"
    >
      <v-card>
        <v-card-title class="modal-title">
          Late Audit Reports
          <v-spacer></v-spacer>
          <v-btn
            icon
            @click="showLateReportsModal = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <div class="late-reports-content">
            <div class="late-reports-list">
              <div 
                v-for="(report, index) in timelinessLateReports" 
                :key="index"
                class="late-report-item"
              >
                <div class="late-report-header">
                  <div class="late-report-id">Audit #{{ report.audit_id }}</div>
                  <div class="late-report-days" :class="getLatenessSeverityClass(report.days_late)">
                    {{ report.days_late }} days late
                  </div>
                </div>
                <div class="late-report-details">
                  <div class="late-report-framework">{{ report.framework_name }}</div>
                  <div class="late-report-dates">
                    <span class="late-report-due">Due: {{ report.due_date }}</span>
                    <span class="late-report-completed">Completed: {{ report.completion_date }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Frameworks Breakdown Modal -->
    <v-dialog
      v-model="showFrameworksModal"
      max-width="800px"
    >
      <v-card>
        <v-card-title class="modal-title">
          Framework Compliance Readiness
          <v-spacer></v-spacer>
          <v-btn
            icon
            @click="showFrameworksModal = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <div class="frameworks-modal-content">
            <div class="frameworks-list">
              <div 
                v-for="(framework, index) in readinessFrameworks" 
                :key="index"
                class="framework-item"
                @click="changeFramework(framework.framework_id); showFrameworksModal = false"
              >
                <div class="framework-item-header">
                  <div class="framework-name">{{ framework.name }}</div>
                  <div class="framework-percentage">
                    {{ framework.readiness_percentage }}%
                  </div>
                </div>
                <div class="framework-progress">
                  <div class="progress-bar-container">
                    <div 
                      class="progress-bar-fill"
                      :style="{ 
                        width: `${framework.readiness_percentage}%`, 
                        backgroundColor: getReadinessColor(framework.readiness_percentage) 
                      }"
                    ></div>
                  </div>
                </div>
                <div class="framework-counts">
                  {{ framework.implemented_count }} of {{ framework.total_defined }} controls implemented
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import './KpiAnalysis.css';

// Audit completion state
const auditLoading = ref(false);
const auditError = ref(null);
const period = ref('month');
const auditMetrics = ref({
  total_audits: 0,
  completed_audits: 0,
  completion_percentage: 0,
  monthly_breakdown: []
});
const auditMonthlyData = ref([]);
const chartMax = ref(5);

// Computed for bar chart
const getYAxisValues = computed(() => {
  const max = chartMax.value;
  const step = Math.ceil(max / 4); // 4 steps on y-axis
  const values = [];
  for (let i = 0; i <= max; i += step) {
    values.push(i);
  }
  return values;
});

// Audit cycle time state
const cycleTimeLoading = ref(false);
const cycleTimeError = ref(null);
const selectedCycleFrameworkId = ref('');
const cycleFrameworks = ref([]);
const cycleTimeMetrics = ref({
  overall_avg_days: 0,
  target_days: 30,
  efficiency: 'N/A',
  monthly_breakdown: []
});
const cycleTimeMonthlyData = ref([]);
const cycleTimeChartMax = ref(50);  // Default max value for y-axis
const cycleTimeTooltipVisible = ref(false);
const cycleTimeTooltipStyle = ref({});
const cycleTimeTooltipData = ref({
  month: '',
  avg_cycle_days: 0
});

// Finding rate state
const findingRateLoading = ref(false);
const findingRateError = ref(null);
const findingPeriod = ref('year');
const findingRateMetrics = ref({
  avg_findings_per_audit: 0,
  low_threshold: 2,
  high_threshold: 5,
  rating: 'N/A',
  top_audits: []
});

// Time to close findings state
const timeToCloseLoading = ref(false);
const timeToCloseError = ref(null);
const timeToClosePeriod = ref('year');
const timeToCloseViewMode = ref('number'); // 'number' or 'percentage'
const timeToCloseFlipped = ref(false); // For flip card animation
const timeToCloseMetrics = ref({
  avg_close_days: 0,
  target_days: 14,
  efficiency: 'N/A',
  oldest_findings: [],
  monthly_trend: [],
  closed_count: 0, // Added from closure rate
  total_count: 0,  // Added from closure rate
  closure_rate: 0  // Added from closure rate
});
const timeToCloseMonthlyTrend = ref([]);
const closeTimeChartMax = ref(50);  // Default max value for y-axis
const closeTimeTooltipVisible = ref(false);
const closeTimeTooltipStyle = ref({});
const closeTimeTooltipData = ref({
  month: '',
  avg_close_days: 0
});

// Audit Pass Rate state removed

// Non-Compliance Issues state
const issuesLoading = ref(false);
const issuesError = ref(null);
const issuesPeriod = ref('year');
const issuesSeverity = ref('all');
const issuesMetrics = ref({
  total_count: 0,
  trend_direction: 'stable',
  trend_percentage: 0,
  selected_severity: 'all',
  severity_breakdown: [],
  top_areas: [],
  monthly_trend: []
});

// Severity state
const severityLoading = ref(false);
const severityError = ref(null);
const severityPeriod = ref('year');
const severityMetrics = ref({
  severity_distribution: [],
  total_issues: 0,
  most_common: null,
  major_count: 0,
  minor_count: 0
});

// Closure Rate state removed - merged with Time to Close

// Evidence state
const evidenceLoading = ref(false);
const evidenceError = ref(null);
const evidenceMetrics = ref({
  completion_percentage: 0,
  evidence_collected: 0,
  total_findings: 0,
  rating: 'N/A',
  color: 'info'
});
const evidenceBreakdown = ref([]);
const evidenceDetails = ref([]);
const selectedAuditId = ref('');
const auditOptions = ref([]);
const evidenceFilter = ref('all');
const showEvidenceModal = ref(false);

// Report Timeliness state
const timelinessLoading = ref(false);
const timelinessError = ref(null);
const timelinessPeriod = ref('year');
const timelinessMetrics = ref({
  percent_on_time: 0,
  on_time_count: 0,
  total_reports: 0,
  avg_days_difference: 0
});
const timelinessHistogram = ref([]);
const timelinessLateReports = ref([]);

// Histogram tooltip state
const histogramTooltipVisible = ref(false);
const histogramTooltipStyle = ref({});
const histogramTooltipData = ref({
  label: '',
  count: 0,
  percentage: 0
});

// Show late reports modal
const showLateReportsModal = ref(false);

// Compliance Readiness state
const readinessLoading = ref(false);
const readinessError = ref(null);
const readinessMetrics = ref({
  total_defined: 0,
  implemented_count: 0,
  readiness_percentage: 0,
  rating: 'N/A',
  color: 'info'
});
const readinessFrameworks = ref([]);
const readinessPolicies = ref([]);
const readinessCriticality = ref([]);
const selectedFrameworkId = ref('');
const selectedPolicyId = ref('');
const showFrameworksModal = ref(false);

// Computed properties
const getCompletionColor = computed(() => {
  const percentage = auditMetrics.value.completion_percentage || 0;
  if (percentage >= 80) return 'success';
  if (percentage >= 50) return 'warning';
  return 'error';
});

const getEfficiencyClass = computed(() => {
  const avgDays = cycleTimeMetrics.value.overall_avg_days || 0;
  const targetDays = cycleTimeMetrics.value.target_days || 30;
  
  if (avgDays <= targetDays) return 'efficiency-good';
  if (avgDays <= targetDays * 1.5) return 'efficiency-warning';
  return 'efficiency-poor';
});

// Removed unused computed property

const getCloseTimeClass = computed(() => {
  const efficiency = timeToCloseMetrics.value.efficiency || '';
  
  if (efficiency === 'Good') return 'close-time-good';
  if (efficiency === 'Fair') return 'close-time-fair';
  return 'close-time-poor';
});

// Pass Rate computed properties removed

const getIssuesTrendClass = computed(() => {
  const direction = issuesMetrics.value.trend_direction || 'stable';
  
  if (direction === 'down') return 'issues-trend-good';
  if (direction === 'up') return 'issues-trend-bad';
  return 'issues-trend-neutral';
});

const getIssuesTrendColor = computed(() => {
  const direction = issuesMetrics.value.trend_direction || 'stable';
  
  if (direction === 'down') return 'success';
  if (direction === 'up') return 'error';
  return 'info';
});

const getBarWidth = (count, total) => {
  return `${(count / total) * 100}%`;
};

// Closure Rate computed properties removed - merged with Time to Close

const getEvidenceColor = computed(() => {
  const percentage = evidenceMetrics.value.completion_percentage || 0;
  if (percentage >= 80) return 'success';
  if (percentage >= 50) return 'warning';
  return 'error';
});

const getEvidenceClass = computed(() => {
  const rating = evidenceMetrics.value.rating || '';
  
  if (rating === 'Excellent') return 'evidence-excellent';
  if (rating === 'Good') return 'evidence-good';
  if (rating === 'Fair') return 'evidence-fair';
  return 'evidence-poor';
});

// Computed properties for evidence card
const getEvidenceDetailStats = computed(() => {
  const withEvidence = evidenceDetails.value.filter(item => item.has_evidence).length;
  const withoutEvidence = evidenceDetails.value.length - withEvidence;
  
  return {
    withEvidence,
    withoutEvidence
  };
});

const filteredEvidenceDetails = computed(() => {
  if (evidenceFilter.value === 'all') {
    return evidenceDetails.value;
  } else if (evidenceFilter.value === 'with') {
    return evidenceDetails.value.filter(item => item.has_evidence);
  } else { // 'without'
    return evidenceDetails.value.filter(item => !item.has_evidence);
  }
});

const getTimelinessColor = computed(() => {
  return timelinessMetrics.value.color || 'info';
});

const getTimelinessClass = computed(() => {
  const rating = timelinessMetrics.value.rating || '';
  
  if (rating === 'Excellent') return 'timeliness-excellent';
  if (rating === 'Good') return 'timeliness-good';
  if (rating === 'Fair') return 'timeliness-fair';
  return 'timeliness-poor';
});

// Computed for cycle time chart
const getCycleTimeYAxisValues = computed(() => {
  const max = cycleTimeChartMax.value;
  const step = Math.ceil(max / 5); // 5 steps on y-axis
  const values = [];
  for (let i = 0; i <= max; i += step) {
    values.push(i);
  }
  return values;
});

// Computed for close time chart
const getCloseTimeYAxisValues = computed(() => {
  const max = closeTimeChartMax.value;
  const step = Math.ceil(max / 4); // 4 steps on y-axis for better spacing
  const values = [];
  for (let i = 0; i <= max; i += step) {
    values.push(i);
  }
  return values;
});

// Methods
const fetchAuditMetrics = async () => {
  auditLoading.value = true;
  auditError.value = null;
  
  try {
    const response = await axios.get(`http://localhost:8000/api/kpi/audit-completion/?period=${period.value}`);
    if (response.data.success && response.data.data) {
      auditMetrics.value = response.data.data.metrics;
      auditMonthlyData.value = response.data.data.monthly_breakdown || [];
      chartMax.value = response.data.data.chart_max || 5;
    } else {
      throw new Error(response.data.message || 'Failed to fetch audit metrics');
    }
  } catch (err) {
    console.error('Error fetching audit metrics:', err);
    auditError.value = 'Failed to load audit metrics';
  } finally {
    auditLoading.value = false;
  }
};

const fetchCycleTimeMetrics = async () => {
  cycleTimeLoading.value = true;
  cycleTimeError.value = null;
  
  try {
    let url = 'http://localhost:8000/api/kpi/audit-cycle-time/';
    if (selectedCycleFrameworkId.value) {
      url += `?framework_id=${selectedCycleFrameworkId.value}`;
    }
    
    const response = await axios.get(url);
    if (response.data.success && response.data.data) {
      cycleTimeMetrics.value = response.data.data.metrics;
      
      // Save frameworks for the dropdown
      cycleFrameworks.value = response.data.data.frameworks || [];
      
      // Process monthly data for chart
      cycleTimeMonthlyData.value = response.data.data.monthly_breakdown || [];
      
      // Calculate chart max based on data
      if (cycleTimeMonthlyData.value.length > 0) {
        const maxCycleTime = Math.max(
          ...cycleTimeMonthlyData.value.map(item => item.avg_cycle_days), 
          cycleTimeMetrics.value.target_days
        );
        // Add some padding to the top
        cycleTimeChartMax.value = Math.ceil(maxCycleTime * 1.2);
      }
    } else {
      throw new Error(response.data.message || 'Failed to fetch cycle time metrics');
    }
  } catch (err) {
    console.error('Error fetching cycle time metrics:', err);
    cycleTimeError.value = 'Failed to load cycle time data';
  } finally {
    cycleTimeLoading.value = false;
  }
};

const fetchFindingRateMetrics = async () => {
  findingRateLoading.value = true;
  findingRateError.value = null;
  
  try {
    const response = await axios.get(`http://localhost:8000/api/kpi/finding-rate/?period=${findingPeriod.value}`);
    if (response.data.success && response.data.data) {
      findingRateMetrics.value = response.data.data.metrics;
      findingRateMetrics.value.top_audits = response.data.data.top_audits || [];
    } else {
      throw new Error(response.data.message || 'Failed to fetch finding rate metrics');
    }
  } catch (err) {
    console.error('Error fetching finding rate metrics:', err);
    findingRateError.value = 'Failed to load finding rate data';
  } finally {
    findingRateLoading.value = false;
  }
};

const fetchTimeToCloseMetrics = async () => {
  timeToCloseLoading.value = true;
  timeToCloseError.value = null;
  
  try {
    // Fetch both time to close and closure rate metrics in parallel
    const [timeToCloseResponse, closureRateResponse] = await Promise.all([
      axios.get(`http://localhost:8000/api/kpi/time-to-close/?period=${timeToClosePeriod.value}`),
      axios.get(`http://localhost:8000/api/kpi/closure-rate/?period=${timeToClosePeriod.value}`)
    ]);
    
    if (timeToCloseResponse.data.success && timeToCloseResponse.data.data) {
      // Set time to close metrics
      timeToCloseMetrics.value = timeToCloseResponse.data.data.metrics;
      timeToCloseMetrics.value.oldest_findings = timeToCloseResponse.data.data.oldest_findings || [];
      
      // Process monthly trend data for chart
      timeToCloseMonthlyTrend.value = timeToCloseResponse.data.data.monthly_trend || [];
      
      // Calculate chart max based on data with additional padding
      if (timeToCloseMonthlyTrend.value.length > 0) {
        const maxCloseTime = Math.max(
          ...timeToCloseMonthlyTrend.value.map(item => item.avg_close_days), 
          timeToCloseMetrics.value.target_days
        );
        // Add 25% padding to the top to prevent lines from extending beyond
        closeTimeChartMax.value = Math.ceil(maxCloseTime * 1.25);
      }
      
      // Add closure rate data to the time to close metrics
      if (closureRateResponse.data.success && closureRateResponse.data.data) {
        const closureMetrics = closureRateResponse.data.data.metrics;
        timeToCloseMetrics.value.closed_count = closureMetrics.closed_count || 0;
        timeToCloseMetrics.value.total_count = closureMetrics.opened_count || 0;
        timeToCloseMetrics.value.closure_rate = closureMetrics.closure_rate || 0;
        
        // Merge closure rate data into monthly trend
        const closureTrend = closureRateResponse.data.data.monthly_trend || [];
        
        // Map closure rate data into time to close monthly trend
        if (timeToCloseMonthlyTrend.value.length > 0 && closureTrend.length > 0) {
          timeToCloseMonthlyTrend.value = timeToCloseMonthlyTrend.value.map(item => {
            const matchingClosureItem = closureTrend.find(c => c.month === item.month);
            if (matchingClosureItem) {
              return {
                ...item,
                closed_count: matchingClosureItem.closed_count || 0,
                total_count: matchingClosureItem.opened_count || 0,
                closure_rate: matchingClosureItem.rate || 0
              };
            }
            return item;
          });
        }
      }
    } else {
      throw new Error(timeToCloseResponse.data.message || 'Failed to fetch time to close metrics');
    }
  } catch (err) {
    console.error('Error fetching time to close metrics:', err);
    timeToCloseError.value = 'Failed to load time to close data';
  } finally {
    timeToCloseLoading.value = false;
  }
};

// fetchPassRateMetrics function removed

const fetchIssuesMetrics = async () => {
  issuesLoading.value = true;
  issuesError.value = null;
  
  try {
    const response = await axios.get(`http://localhost:8000/api/kpi/non-compliance-issues/?period=${issuesPeriod.value}&severity=${issuesSeverity.value}`);
    if (response.data.success && response.data.data) {
      issuesMetrics.value = response.data.data.metrics;
      issuesMetrics.value.severity_breakdown = response.data.data.severity_breakdown || [];
      issuesMetrics.value.top_areas = response.data.data.top_areas || [];
      issuesMetrics.value.monthly_trend = response.data.data.monthly_trend || [];
    } else {
      throw new Error(response.data.message || 'Failed to fetch issues metrics');
    }
  } catch (err) {
    console.error('Error fetching issues metrics:', err);
    issuesError.value = 'Failed to load issues data';
  } finally {
    issuesLoading.value = false;
  }
};

const fetchSeverityMetrics = async () => {
  severityLoading.value = true;
  severityError.value = null;
  
  try {
    const response = await axios.get(`http://localhost:8000/api/kpi/severity-distribution/?period=${severityPeriod.value}`);
    if (response.data.success && response.data.data) {
      severityMetrics.value = response.data.data.metrics;
      severityMetrics.value.severity_distribution = response.data.data.severity_distribution || [];
    } else {
      throw new Error(response.data.message || 'Failed to fetch severity metrics');
    }
  } catch (err) {
    console.error('Error fetching severity metrics:', err);
    severityError.value = 'Failed to load severity data';
  } finally {
    severityLoading.value = false;
  }
};

// fetchClosureRateMetrics function removed - merged with fetchTimeToCloseMetrics

const fetchEvidenceMetrics = async () => {
  evidenceLoading.value = true;
  evidenceError.value = null;
  
  try {
    let url = 'http://localhost:8000/api/kpi/evidence-completion/';
    if (selectedAuditId.value) {
      url += `?audit_id=${selectedAuditId.value}`;
    }
    
    const response = await axios.get(url);
    if (response.data.success && response.data.data) {
      evidenceMetrics.value = response.data.data.metrics;
      evidenceBreakdown.value = response.data.data.audit_breakdown || [];
      evidenceDetails.value = response.data.data.evidence_details || [];
      
      // Load audit options if not already loaded
      if (auditOptions.value.length === 0 && evidenceBreakdown.value.length > 0) {
        auditOptions.value = evidenceBreakdown.value.map(audit => ({
          id: audit.audit_id,
          name: audit.framework_name || 'Unknown Framework'
        }));
      }
    } else {
      throw new Error(response.data.message || 'Failed to fetch evidence metrics');
    }
  } catch (err) {
    console.error('Error fetching evidence metrics:', err);
    evidenceError.value = 'Failed to load evidence data';
  } finally {
    evidenceLoading.value = false;
  }
};

const getProgressColor = (percentage) => {
  if (percentage >= 90) return '#4CAF50'; // Green
  if (percentage >= 70) return '#3f51b5'; // Indigo
  if (percentage >= 50) return '#FF9800'; // Orange
  return '#f44336'; // Red
};

const changePeriod = async (newPeriod) => {
  period.value = newPeriod;
  await fetchAuditMetrics();
};

const changeCycleFramework = async () => {
  await fetchCycleTimeMetrics();
};

const changeTimeToClosePeriod = async (newPeriod) => {
  timeToClosePeriod.value = newPeriod;
  await fetchTimeToCloseMetrics();
};

const toggleTimeToCloseFlip = () => {
  timeToCloseFlipped.value = !timeToCloseFlipped.value;
};

const changeIssuesPeriod = async (newPeriod) => {
  issuesPeriod.value = newPeriod;
  await fetchIssuesMetrics();
};

const changeIssuesSeverity = async (newSeverity) => {
  issuesSeverity.value = newSeverity;
  await fetchIssuesMetrics();
};

const changeSeverityPeriod = async (newPeriod) => {
  severityPeriod.value = newPeriod;
  await fetchSeverityMetrics();
};

const changeSelectedAudit = async () => {
  await fetchEvidenceMetrics();
};

// getChartLineStyle function removed - no longer needed for closure rate

const getShortMonth = (monthStr) => {
  // Extract just the month abbreviation from "Jan 2025" format
  return monthStr ? monthStr.split(' ')[0] : '';
};

// showTooltip and hideTooltip functions removed - no longer needed for closure rate

const getBarHeight = (percentage) => {
  return `${percentage}%`;
};

const showHistogramTooltip = (bar, event) => {
  histogramTooltipData.value = {
    label: bar.label,
    count: bar.count,
    percentage: bar.percentage
  };
  
  // Position the tooltip near the bar but not on top of it
  const rect = event.target.getBoundingClientRect();
  histogramTooltipStyle.value = {
    left: `${rect.left + window.scrollX + 10}px`,
    top: `${rect.top + window.scrollY - 70}px`
  };
  
  histogramTooltipVisible.value = true;
};

const hideHistogramTooltip = () => {
  histogramTooltipVisible.value = false;
};

const getLatenessSeverityClass = (daysLate) => {
  if (daysLate <= 0) return 'late-report-early';
  if (daysLate <= 7) return 'late-report-on-time';
  if (daysLate <= 14) return 'late-report-late';
  return 'late-report-very-late';
};

const fetchTimelinessMetrics = async () => {
  timelinessLoading.value = true;
  timelinessError.value = null;
  
  try {
    const response = await axios.get(`http://localhost:8000/api/kpi/report-timeliness/?period=${timelinessPeriod.value}`);
    if (response.data.success && response.data.data) {
      timelinessMetrics.value = response.data.data.metrics;
      timelinessHistogram.value = response.data.data.histogram || [];
      timelinessLateReports.value = response.data.data.late_reports || [];
    } else {
      throw new Error(response.data.message || 'Failed to fetch timeliness metrics');
    }
  } catch (err) {
    console.error('Error fetching timeliness metrics:', err);
    timelinessError.value = 'Failed to load timeliness data';
  } finally {
    timelinessLoading.value = false;
  }
};

const changeTimelinessPeriod = async (newPeriod) => {
  timelinessPeriod.value = newPeriod;
  await fetchTimelinessMetrics();
};

const fetchReadinessMetrics = async () => {
  readinessLoading.value = true;
  readinessError.value = null;
  
  try {
    let url = 'http://localhost:8000/api/kpi/compliance-readiness/';
    if (selectedFrameworkId.value) {
      url += `?framework_id=${selectedFrameworkId.value}`;
    } else if (selectedPolicyId.value) {
      url += `?policy_id=${selectedPolicyId.value}`;
    }
    
    const response = await axios.get(url);
    if (response.data.success && response.data.data) {
      readinessMetrics.value = response.data.data.metrics;
      readinessFrameworks.value = response.data.data.frameworks || [];
      readinessPolicies.value = response.data.data.policies || [];
      readinessCriticality.value = response.data.data.criticality_breakdown || [];
    } else {
      throw new Error(response.data.message || 'Failed to fetch readiness metrics');
    }
  } catch (err) {
    console.error('Error fetching readiness metrics:', err);
    readinessError.value = 'Failed to load readiness data';
  } finally {
    readinessLoading.value = false;
  }
};

const changeFramework = async (frameworkId) => {
  selectedFrameworkId.value = frameworkId;
  selectedPolicyId.value = ''; // Reset policy selection
  await fetchReadinessMetrics();
};

const changePolicy = async (policyId) => {
  selectedPolicyId.value = policyId;
  selectedFrameworkId.value = ''; // Reset framework selection
  await fetchReadinessMetrics();
};

const resetFilters = async () => {
  selectedFrameworkId.value = '';
  selectedPolicyId.value = '';
  await fetchReadinessMetrics();
};

const getReadinessClass = computed(() => {
  const rating = readinessMetrics.value.rating || '';
  
  if (rating === 'Excellent') return 'readiness-excellent';
  if (rating === 'Good') return 'readiness-good';
  if (rating === 'Fair') return 'readiness-fair';
  return 'readiness-poor';
});

const getReadinessColor = (percentage) => {
  if (percentage >= 90) return '#4CAF50';  // Green
  if (percentage >= 75) return '#3f51b5';  // Indigo
  if (percentage >= 50) return '#FF9800';  // Orange
  return '#f44336';  // Red
};

const getCriticalityColor = (criticality) => {
  switch (criticality) {
    case 'Critical': return '#d32f2f';  // Deep red
    case 'High': return '#f44336';      // Red
    case 'Medium': return '#FF9800';    // Orange
    case 'Low': return '#4caf50';       // Green
    default: return '#9e9e9e';          // Grey
  }
};

const getCycleTimeLineStyle = (index) => {
  const startPoint = cycleTimeMonthlyData.value[index];
  const endPoint = cycleTimeMonthlyData.value[index + 1];
  
  if (!startPoint || !endPoint) return {};
  
  const x1 = (index / (cycleTimeMonthlyData.value.length - 1)) * 100;
  const y1 = (startPoint.avg_cycle_days / cycleTimeChartMax.value) * 100;
  const x2 = ((index + 1) / (cycleTimeMonthlyData.value.length - 1)) * 100;
  const y2 = (endPoint.avg_cycle_days / cycleTimeChartMax.value) * 100;
  
  const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
  
  return {
    width: `${length}%`,
    left: `${x1}%`,
    bottom: `${y1}%`,
    transform: `rotate(${angle}deg)`,
    transformOrigin: 'left bottom'
  };
};

const isLineAboveThreshold = (index) => {
  const startPoint = cycleTimeMonthlyData.value[index];
  const endPoint = cycleTimeMonthlyData.value[index + 1];
  
  if (!startPoint || !endPoint) return false;
  
  // Line is above threshold if either endpoint is above
  return startPoint.avg_cycle_days > cycleTimeMetrics.value.target_days || 
         endPoint.avg_cycle_days > cycleTimeMetrics.value.target_days;
};

const showCycleTimeTooltip = (index, event) => {
  const point = cycleTimeMonthlyData.value[index];
  if (!point) return;
  
  cycleTimeTooltipData.value = {
    month: point.month,
    avg_cycle_days: point.avg_cycle_days
  };
  
  // Position the tooltip near the point but not on top of it
  const rect = event.target.getBoundingClientRect();
  cycleTimeTooltipStyle.value = {
    left: `${rect.left + window.scrollX + 10}px`,
    top: `${rect.top + window.scrollY - 70}px`
  };
  
  cycleTimeTooltipVisible.value = true;
};

const hideCycleTimeTooltip = () => {
  cycleTimeTooltipVisible.value = false;
};

const getCloseTimeLineStyle = (index) => {
  const startPoint = timeToCloseMonthlyTrend.value[index];
  const endPoint = timeToCloseMonthlyTrend.value[index + 1];
  
  if (!startPoint || !endPoint) return {};
  
  const x1 = (index / (timeToCloseMonthlyTrend.value.length - 1)) * 100;
  const y1 = (startPoint.avg_close_days / closeTimeChartMax.value) * 100;
  const x2 = ((index + 1) / (timeToCloseMonthlyTrend.value.length - 1)) * 100;
  const y2 = (endPoint.avg_close_days / closeTimeChartMax.value) * 100;
  
  const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
  
  return {
    width: `${length}%`,
    left: `${x1}%`,
    bottom: `${y1}%`,
    transform: `rotate(${angle}deg)`,
    transformOrigin: 'left bottom'
  };
};

const isCloseTimeLineAboveThreshold = (index) => {
  const startPoint = timeToCloseMonthlyTrend.value[index];
  const endPoint = timeToCloseMonthlyTrend.value[index + 1];
  
  if (!startPoint || !endPoint) return false;
  
  return startPoint.avg_close_days > timeToCloseMetrics.value.target_days || 
         endPoint.avg_close_days > timeToCloseMetrics.value.target_days;
};

const showCloseTimeTooltip = (index, event) => {
  const point = timeToCloseMonthlyTrend.value[index];
  if (!point) return;
  
  closeTimeTooltipData.value = {
    month: point.month,
    avg_close_days: point.avg_close_days
  };
  
  // Position the tooltip near the point but not on top of it
  const rect = event.target.getBoundingClientRect();
  closeTimeTooltipStyle.value = {
    left: `${rect.left + window.scrollX + 10}px`,
    top: `${rect.top + window.scrollY - 70}px`
  };
  
  closeTimeTooltipVisible.value = true;
};

const hideCloseTimeTooltip = () => {
  closeTimeTooltipVisible.value = false;
};

// Initialize data
onMounted(() => {
  fetchAuditMetrics();
  fetchCycleTimeMetrics();
  fetchFindingRateMetrics();
  fetchTimeToCloseMetrics();
  // fetchPassRateMetrics removed
  fetchIssuesMetrics();
  fetchSeverityMetrics();
  // fetchClosureRateMetrics removed - merged with Time to Close
  fetchEvidenceMetrics();
  fetchTimelinessMetrics();
  fetchReadinessMetrics();
});

const formatSeverityLabel = (severity) => {
  if (severity === 'Unspecified') {
    return 'NA';
  }
  return severity;
};

const getTimeToClosePercentage = computed(() => {
  const avg = timeToCloseMetrics.value.avg_close_days || 0;
  const target = timeToCloseMetrics.value.target_days || 14;
  
  if (avg <= 0 || target <= 0) return 0;
  
  // Calculate percentage: lower is better, so we invert the ratio
  // If avg days is equal to target, that's 100%
  // If avg days is double the target, that's 50%
  const percentage = Math.min(200, Math.max(0, (target / avg) * 100));
  return Math.round(percentage);
});

const getSeverityCount = (severity) => {
  return issuesMetrics.value.severity_breakdown.find(item => item.severity === severity)?.count || 0;
};
</script>
