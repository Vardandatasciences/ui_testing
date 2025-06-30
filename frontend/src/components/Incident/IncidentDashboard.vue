<template>
  <div class="incident-dashboard-wrapper">
    <!-- First row of KPI cards - Detection and Response Times -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Mean Time to Detect (MTTD)</h3>
        <div class="kpi-value">
          {{ kpiData.mttd.value }}<span class="unit">{{ kpiData.mttd.unit }}</span>
          <span :class="['value-change', kpiData.mttd.change_percentage > 0 ? 'positive' : 'negative']">
            <i :class="kpiData.mttd.change_percentage > 0 ? 'fas fa-caret-up' : 'fas fa-caret-down'"></i>
            {{ Math.abs(kpiData.mttd.change_percentage) }}%
          </span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <!-- Create dynamic path based on trend data -->
              <path v-if="kpiData.mttd.trend && kpiData.mttd.trend.length > 0"
                    :d="generateTrendPath(kpiData.mttd.trend.map(t => t.minutes))"
                    fill="none" stroke="#3498db" stroke-width="2"></path>
              
              <!-- Create dynamic data points with tooltips -->
              <template v-if="kpiData.mttd.trend && kpiData.mttd.trend.length > 0">
                <g v-for="(point, index) in getTrendPoints(kpiData.mttd.trend.map(t => t.minutes))" 
                        :key="'mttd-point-'+index"
                   class="data-point-group">
                  <circle 
                        :cx="point.x" 
                        :cy="point.y" 
                        r="3" 
                    fill="#3498db"
                    class="data-point"
                  />
                  <circle 
                    :cx="point.x" 
                    :cy="point.y" 
                    r="8" 
                    fill="transparent"
                    class="hover-area"
                    @mouseover="showTooltip($event, kpiData.mttd.trend[index])"
                    @mouseout="hideTooltip"
                  />
                </g>
              </template>
            </svg>
            <div id="chart-tooltip" class="chart-tooltip" :style="tooltipStyle">
              <div v-if="activeTooltip" class="tooltip-content">
                <div class="tooltip-header">{{ activeTooltip.month }}</div>
                <div class="tooltip-value">{{ activeTooltip.minutes }} {{ kpiData.mttd.unit }}</div>
                <div class="tooltip-details">
                  <div class="tooltip-count"><strong>Incidents:</strong> {{ activeTooltip.count || 0 }}</div>
                  <div v-if="activeTooltip.fastest && activeTooltip.count > 0"><strong>Fastest:</strong> {{ activeTooltip.fastest }} {{ kpiData.mttd.unit }}</div>
                  <div v-if="activeTooltip.slowest && activeTooltip.count > 0"><strong>Slowest:</strong> {{ activeTooltip.slowest }} {{ kpiData.mttd.unit }}</div>
                  <div v-if="!activeTooltip.count || activeTooltip.count === 0" class="tooltip-no-data">No incidents in this period</div>
                </div>
                <div v-if="activeTooltip.details && activeTooltip.details.length > 0" class="tooltip-incidents-list">
                  <div class="tooltip-list-header">Recent incidents:</div>
                  <div v-for="(incident, i) in activeTooltip.details.slice(0, 3)" :key="i" class="tooltip-incident-item">
                    <div class="tooltip-incident-title">{{ incident.title || 'Untitled Incident' }}</div>
                    <div class="tooltip-incident-time">{{ incident.minutes }} {{ kpiData.mttd.unit }}</div>
                  </div>
                  <div v-if="activeTooltip.details.length > 3" class="tooltip-more">
                    + {{ activeTooltip.details.length - 3 }} more
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="chart-months">
            <span v-for="(item, index) in kpiData.mttd.trend" :key="'mttd-month-'+index">
              {{ item.month }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
  <h3>Mean Time to Respond (MTTR)</h3>
  <div class="kpi-value">
    {{ kpiData.mttr.value.toFixed(1) }}<span class="unit">{{ kpiData.mttr.unit }}</span>
    <span :class="['value-change', kpiData.mttr.change_percentage > 0 ? 'positive' : 'negative']">
      <i :class="kpiData.mttr.change_percentage > 0 ? 'fas fa-caret-up' : 'fas fa-caret-down'"></i>
      {{ Math.abs(kpiData.mttr.change_percentage) }}%
    </span>
  </div>
  <div class="kpi-chart">
    <div class="line-chart">
      <svg viewBox="0 0 300 60" preserveAspectRatio="none">
        <!-- Dynamic trend path -->
        <path v-if="kpiData.mttr.trend && kpiData.mttr.trend.length > 0"
              :d="generateTrendPath(kpiData.mttr.trend.map(t => t.minutes))"
              fill="none" stroke="#3498db" stroke-width="2"></path>
        
        <!-- Dynamic data points with tooltips -->
        <template v-if="kpiData.mttr.trend && kpiData.mttr.trend.length > 0">
          <g v-for="(point, index) in getTrendPoints(kpiData.mttr.trend.map(t => t.minutes))" 
             :key="'mttr-point-'+index"
             class="data-point-group">
            <circle 
              :cx="point.x" 
              :cy="point.y" 
              r="3" 
              fill="#3498db"
              class="data-point"
            />
            <circle 
              :cx="point.x" 
              :cy="point.y" 
              r="8" 
              fill="transparent"
              class="hover-area"
              @mouseover="showTooltip($event, kpiData.mttr.trend[index])"
              @mouseout="hideTooltip"
            />
          </g>
        </template>
      </svg>
    </div>
    <div class="chart-months">
      <span v-for="(item, index) in kpiData.mttr.trend" :key="'mttr-month-'+index">
        {{ item.month }}
      </span>
    </div>
  </div>
</div>

      
      <div class="kpi-card">
        <h3>Mean Time to Contain (MTTC)</h3>
        <div class="kpi-value">
          {{ Number(kpiData.mttc.value).toFixed(1) }}<span class="unit">{{ kpiData.mttc.unit }}</span>
          <span :class="['value-change', kpiData.mttc.change_percentage > 0 ? 'positive' : 'negative']">
            <i :class="kpiData.mttc.change_percentage > 0 ? 'fas fa-caret-up' : 'fas fa-caret-down'"></i>
            {{ Math.abs(kpiData.mttc.change_percentage) }}%
          </span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <!-- Create dynamic path based on trend data -->
              <path v-if="kpiData.mttc.trend && kpiData.mttc.trend.length > 0"
                    :d="generateTrendPath(kpiData.mttc.trend.map(t => t.minutes))"
                fill="none" stroke="#3498db" stroke-width="2"></path>
              
              <!-- Create dynamic data points with tooltips -->
              <template v-if="kpiData.mttc.trend && kpiData.mttc.trend.length > 0">
                <g v-for="(point, index) in getTrendPoints(kpiData.mttc.trend.map(t => t.minutes))" 
                        :key="'mttc-point-'+index"
                   class="data-point-group">
                  <circle 
                        :cx="point.x" 
                        :cy="point.y" 
                        r="3" 
                    fill="#3498db"
                    class="data-point"
                  />
                  <circle 
                    :cx="point.x" 
                    :cy="point.y" 
                    r="8" 
                    fill="transparent"
                    class="hover-area"
                    @mouseover="showTooltip($event, kpiData.mttc.trend[index])"
                    @mouseout="hideTooltip"
                  />
                </g>
              </template>
            </svg>
          </div>
          <div class="chart-months">
            <span v-for="(item, index) in kpiData.mttc.trend" :key="'mttc-month-'+index">
              {{ item.month }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Second row of KPI cards - Resolution Metrics -->
    <div class="kpi-row">
      <div class="kpi-card expanded-card">
        <h3>Mean Time to Resolve (MTTRv)</h3>
        <div class="kpi-value">
          {{ kpiData.mttrv.value }}<span class="unit">{{ kpiData.mttrv.unit }}</span>
          <span class="value-change negative"><i class="fas fa-caret-down"></i>2.0%</span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,20 C25,25 50,20 75,15 C100,10 125,15 150,20 C175,25 200,20 225,15 C250,10 275,15 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="20" r="3" fill="#3498db"/>
              <circle cx="50" cy="20" r="3" fill="#3498db"/>
              <circle cx="100" cy="10" r="3" fill="#3498db"/>
              <circle cx="150" cy="20" r="3" fill="#3498db"/>
              <circle cx="200" cy="20" r="3" fill="#3498db"/>
              <circle cx="250" cy="10" r="3" fill="#3498db"/>
              <circle cx="300" cy="20" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card expanded-card">
        <h3>First Response Time</h3>
        <div class="kpi-value">
          {{ kpiData.firstResponseTime.value }}<span class="unit">{{ kpiData.firstResponseTime.unit }}</span>
          <span :class="['value-change', kpiData.firstResponseTime.change_percentage > 0 ? 'positive' : 'negative']">
            <i :class="kpiData.firstResponseTime.change_percentage > 0 ? 'fas fa-caret-up' : 'fas fa-caret-down'"></i>
            {{ Math.abs(kpiData.firstResponseTime.change_percentage) }}%
          </span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path v-if="kpiData.firstResponseTime.trend && kpiData.firstResponseTime.trend.length > 0"
                    :d="generateTrendPath(kpiData.firstResponseTime.trend.map(t => t.minutes))"
                    fill="none" stroke="#3498db" stroke-width="2"></path>
              
              <template v-if="kpiData.firstResponseTime.trend && kpiData.firstResponseTime.trend.length > 0">
                <g v-for="(point, index) in getTrendPoints(kpiData.firstResponseTime.trend.map(t => t.minutes))" 
                   :key="'first-response-point-'+index"
                   class="data-point-group">
                  <circle 
                    :cx="point.x" 
                    :cy="point.y" 
                    r="3" 
                    fill="#3498db"
                    class="data-point"
                  />
                  <circle 
                    :cx="point.x" 
                    :cy="point.y" 
                    r="8" 
                    fill="transparent"
                    class="hover-area"
                    @mouseover="showTooltip($event, kpiData.firstResponseTime.trend[index])"
                    @mouseout="hideTooltip"
                  />
                </g>
              </template>
            </svg>
          </div>
          <div class="chart-months">
            <span v-for="(item, index) in kpiData.firstResponseTime.trend" :key="'first-response-month-'+index">
              {{ item.month }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Third row of KPI cards - Incident Volume Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Number of Incidents Detected</h3>
        <div class="kpi-value">{{ kpiData.incidentsDetected.value }}</div>
        <div class="kpi-chart">
          <div class="bar-chart vertical">
            <div 
              v-for="(value, index) in kpiData.incidentsDetected.byDay" 
              :key="'incident-bar-'+index" 
              class="bar tooltip-container" 
              :style="{ height: calculateBarHeight(value, kpiData.incidentsDetected.byDay) }">
              <div class="tooltip">
                <strong>{{ kpiData.incidentsDetected.details && kpiData.incidentsDetected.details[index]?.day }}: {{ value }}</strong>
                <div v-if="value > 0" class="tooltip-incidents">
                  <div v-if="kpiData.incidentsDetected.details && kpiData.incidentsDetected.details[index]?.incidents.length > 0">
                    <div v-for="(incident, i) in kpiData.incidentsDetected.details[index]?.incidents.slice(0, 3)" :key="i" class="tooltip-incident">
                      {{ incident.title }}
                    </div>
                    <div v-if="kpiData.incidentsDetected.details && kpiData.incidentsDetected.details[index]?.incidents.length > 3">
                      + {{ kpiData.incidentsDetected.details[index]?.incidents.length - 3 }} more
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-labels">
          <span>M</span>
          <span>T</span>
          <span>W</span>
          <span>T</span>
          <span>F</span>
          <span>S</span>
          <span>S</span>
        </div>
      </div>
      
      <div class="kpi-card">
  <h3>Number of Reopened Incidents</h3>
  <div class="kpi-value">{{ kpiData.reopenedIncidents.value }}</div>
  <div class="kpi-chart">
    <div class="progress-bar">
      <div class="progress" :style="{ width: kpiData.reopenedIncidents.percentage + '%' }"></div>
    </div>
  </div>
  <div class="chart-values">
    <span>{{ kpiData.reopenedIncidents.percentage.toFixed(1) }}% of total incidents</span>
  </div>
</div>

      
      <div class="kpi-card">
  <h3>Incident Closure Rate</h3>
  <div class="kpi-value">{{ Math.round(kpiData.closureRate.value) }}<span class="unit">{{ kpiData.closureRate.unit }}</span></div>
  <div class="kpi-chart">
    <div class="progress-bar">
      <div class="progress" :style="{ width: kpiData.closureRate.value + '%' }"></div>
    </div>
  </div>
</div>

    </div>

    <!-- Fourth row of KPI cards - Quality Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>False Positive Rate</h3>
        <div class="kpi-value">
  {{ Math.round(kpiData.falsePositiveRate.value) }}<span class="unit">{{ kpiData.falsePositiveRate.unit }}</span>
</div>

        <div class="kpi-chart">
          <div class="donut-chart">
            <div class="donut-hole"></div>
            <div class="donut-chart" :style="`--percentage: ${kpiData.falsePositiveRate.value};`">
  <div class="donut-hole"></div>
</div>


          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Detection Accuracy</h3>
        <div class="kpi-value">{{ Math.round(kpiData.detectionAccuracy.value) }}<span class="unit">{{ kpiData.detectionAccuracy.unit }}</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" :style="{ width: kpiData.detectionAccuracy.value + '%' }"></div>
          </div>
        </div>
      </div>


      <div class="kpi-card">
        <h3>Cost per Incident</h3>
        <div class="kpi-value">₹{{ kpiData.costData.total_cost_k || '0' }}K</div>
        <div class="cost-breakdown">
          <div v-for="(item, index) in kpiData.costData.by_severity" :key="index" 
               class="cost-bar" :class="item.severity.toLowerCase()">
            {{ item.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- Fifth row of KPI cards - Categorization Metrics -->
    <div class="kpi-row">
      <div class="kpi-card expanded-card">
        <h3>Percentage of Incidents by Severity</h3>
        <div class="kpi-chart pie-chart-container">
          <svg viewBox="0 0 100 100" class="pie-chart-svg" style="width: 80px; height: 80px;">
            <!-- Calculate the angles for each segment -->
            <circle cx="50" cy="50" r="40" fill="white" />
            
            <!-- Low segment (green) -->
            <circle r="40" cx="50" cy="50" fill="transparent"
                    stroke="#84cc16"
                    stroke-width="40"
                    :stroke-dasharray="`${kpiData.incidentsBySeverity.low * 2.51} ${100 * 2.51 - kpiData.incidentsBySeverity.low * 2.51}`"
                    stroke-dashoffset="0"
                    transform="rotate(-90 50 50)"
                    class="pie-segment-path"
                    @mouseover="showPieTooltip($event, 'Low', kpiData.incidentsBySeverity.low)"
                    @mouseout="hidePieTooltip" />
            
            <!-- Medium segment (yellow) -->
            <circle r="40" cx="50" cy="50" fill="transparent"
                    stroke="#facc15"
                    stroke-width="40"
                    :stroke-dasharray="`${kpiData.incidentsBySeverity.medium * 2.51} ${100 * 2.51 - kpiData.incidentsBySeverity.medium * 2.51}`"
                    :stroke-dashoffset="`${(100 - kpiData.incidentsBySeverity.low) * 2.51}`"
                    transform="rotate(-90 50 50)"
                    class="pie-segment-path"
                    @mouseover="showPieTooltip($event, 'Medium', kpiData.incidentsBySeverity.medium)"
                    @mouseout="hidePieTooltip" />
            
            <!-- High segment (orange) -->
            <circle r="40" cx="50" cy="50" fill="transparent"
                    stroke="#f97316"
                    stroke-width="40"
                    :stroke-dasharray="`${kpiData.incidentsBySeverity.high * 2.51} ${100 * 2.51 - kpiData.incidentsBySeverity.high * 2.51}`"
                    :stroke-dashoffset="`${(100 - kpiData.incidentsBySeverity.low - kpiData.incidentsBySeverity.medium) * 2.51}`"
                    transform="rotate(-90 50 50)"
                    class="pie-segment-path"
                    @mouseover="showPieTooltip($event, 'High', kpiData.incidentsBySeverity.high)"
                    @mouseout="hidePieTooltip" />
          </svg>
          
          <!-- Pie chart tooltip -->
          <div id="pie-tooltip" class="pie-tooltip" :style="pieTooltipStyle">
            <div v-if="activePieTooltip" class="pie-tooltip-content">
              <div class="pie-tooltip-header">{{ activePieTooltip.severity }}</div>
              <div class="pie-tooltip-value">{{ activePieTooltip.percentage }}%</div>
              <div class="pie-tooltip-count">Count: {{ Math.round(activePieTooltip.count) }}</div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-color high"></span>High ({{ kpiData.incidentsBySeverity.high }}%)
          </div>
          <div class="legend-item">
            <span class="legend-color medium"></span>Medium ({{ kpiData.incidentsBySeverity.medium }}%)
          </div>
          <div class="legend-item">
            <span class="legend-color low"></span>Low ({{ kpiData.incidentsBySeverity.low }}%)
          </div>
        </div>
      </div>
      
      <div class="kpi-card expanded-card">
        <h3>Incident Origin Distribution</h3>
        <div class="kpi-chart small-donut-container" id="origin-chart-container">
          <!-- Use a smaller donut chart -->
          <svg viewBox="0 0 100 100" class="donut-chart-svg" style="width: 60px; height: 60px;">
            <circle cx="50" cy="50" r="40" fill="white" />
            
            <!-- Dynamically generate donut segments based on origin data -->
            <template v-if="kpiData.incidentOrigins && kpiData.incidentOrigins.length > 0">
              <template v-for="(item, index) in kpiData.incidentOrigins" :key="'origin-' + index">
                <!-- Calculate the stroke dasharray and dashoffset -->
                <circle r="25" cx="50" cy="50" fill="transparent"
                        :stroke="getOriginColor(item.origin)"
                        stroke-width="12"
                        :stroke-dasharray="`${item.percentage * 2.51} ${100 * 2.51 - item.percentage * 2.51}`"
                        :stroke-dashoffset="getStrokeDashOffset(index)"
                        transform="rotate(-90 50 50)"
                        class="donut-segment-path"
                        @mouseover="showOriginTooltip($event, item.origin, item.percentage, item.count)"
                        @mouseout="hideOriginTooltip" />
              </template>
            </template>
            
            <!-- Smaller text in the center -->
            <text x="50" y="47" text-anchor="middle" font-size="6" font-weight="bold">Total</text>
            <text x="50" y="56" text-anchor="middle" font-size="8" font-weight="bold">{{ incidentCounts.total }}</text>
          </svg>
          
          <!-- Custom tooltip for origin data -->
          <div id="origin-tooltip" class="origin-tooltip" :style="originTooltipStyle">
            <div v-if="activeOriginTooltip" class="origin-tooltip-content">
              <div class="origin-tooltip-header">{{ activeOriginTooltip.origin }}</div>
              <div class="origin-tooltip-value">{{ activeOriginTooltip.percentage }}%</div>
              <div class="origin-tooltip-count">Count: {{ activeOriginTooltip.count }}</div>
            </div>
          </div>
        </div>
        
        <!-- Compact legend with 4 colors -->
        <div class="chart-legend">
          <div v-for="(item, index) in kpiData.incidentOrigins" :key="'legend-' + index" 
               class="legend-item">
            <span class="legend-color" :style="{ backgroundColor: getOriginColor(item.origin) }"></span>
            <span class="legend-text">{{ item.origin.length > 8 ? item.origin.substring(0, 8) + '...' : item.origin }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Sixth row of KPI cards - Cost and Impact -->
    

    <!-- Seventh row of KPI cards - Root Cause Analysis -->
    <div class="kpi-row">
      <div class="kpi-card root-cause-card">
        <h3>Incident Root Cause Categories</h3>
        <div class="kpi-chart bar-chart-container">
          <div class="horizontal-bar-chart">
            <!-- Dynamically generate bars for each root cause category -->
            <div v-for="(percentage, category) in kpiData.rootCauseCategories" :key="category" class="h-bar-item">
              <div class="h-bar-label">{{ category }}</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" 
                     :style="{ width: percentage + '%' }"
                     @mouseover="showRootCauseTooltip($event, category, percentage)"
                     @mouseout="hideRootCauseTooltip"></div>
              </div>
              <div class="h-bar-value">{{ percentage }}%</div>
            </div>
              </div>
          
          <!-- Root cause tooltip -->
          <div class="root-cause-tooltip" :style="rootCauseTooltipStyle">
            <div v-if="activeRootCauseTooltip" class="root-cause-tooltip-content">
              <div class="root-cause-tooltip-header">{{ activeRootCauseTooltip.category }}</div>
              <div class="root-cause-tooltip-value">{{ activeRootCauseTooltip.percentage }}%</div>
              <div class="root-cause-tooltip-count">Count: {{ Math.round(activeRootCauseTooltip.count) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card threat-types-card">
        <h3>Volume of Incident Types</h3>
        <div class="kpi-chart bar-chart-container">
          <div class="vertical-bar-chart">
            <!-- Dynamic bars based on real data -->
            <template v-if="Array.isArray(kpiData.incidentTypes) && kpiData.incidentTypes.length > 0">
              <div v-for="(item, index) in kpiData.incidentTypes.slice(0, 5)" :key="'type-'+index" class="v-bar-item">
                <div class="v-bar-progress" 
                     :style="{ height: calculateBarHeight(item.count, kpiData.incidentTypes.map(t => t.count)) }"
                     :class="'type-color-' + (index % 5)">
                </div>
                <div class="v-bar-label">{{ item.type }}</div>
                <div class="v-bar-value">{{ item.count }}</div>
              </div>
            </template>
            <!-- Show placeholder if no data -->
            <div v-else class="no-data-message">
              No incident type data available
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- After the Seventh row of KPI cards, add new Eighth row -->
    <div class="kpi-row">
      <div class="kpi-card incident-volume-card">
        <h3>Incident Volume</h3>
        <div class="kpi-value">{{ kpiData.incidentVolume.total || 0 }}</div>
        <div class="trend-chart">
          <svg width="100%" height="80" viewBox="0 0 400 80" preserveAspectRatio="none">
            <path 
              :d="getVolumeTrendPath(kpiData.incidentVolume.trend)" 
              fill="rgba(33, 150, 243, 0.2)"
              stroke="#2196F3"
              stroke-width="2"
            />
            </svg>
          <div class="trend-labels">
            <span v-for="(point, index) in kpiData.incidentVolume.trend" :key="index">
              {{ point.day }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card escalation-rate-card">
        <h3>Incident Escalation Rate</h3>
        <div class="kpi-value">{{ kpiData.escalationRate.value || 0 }}<span class="unit">%</span></div>
        <div class="kpi-chart stacked-bar-container">
          <div class="stacked-bar">
            <div class="stacked-segment audit" 
                 :style="{width: kpiData.escalationRate.audit + '%'}"
                 @mouseover="showStackedTooltip($event, 'Audit', kpiData.escalationRate.audit)"
                 @mouseout="hideStackedTooltip">
            </div>
            <div class="stacked-segment manual" 
                 :style="{width: kpiData.escalationRate.manual + '%'}"
                 @mouseover="showStackedTooltip($event, 'Manual', kpiData.escalationRate.manual)"
                 @mouseout="hideStackedTooltip">
            </div>
          </div>
          <div class="stacked-bar-legend">
            <div class="legend-item">
              <span class="legend-color audit"></span>
              <span class="legend-label">Audit ({{ kpiData.escalationRate.audit }}%)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color manual"></span>
              <span class="legend-label">Manual ({{ kpiData.escalationRate.manual }}%)</span>
            </div>
          </div>
        </div>
        <div class="stacked-tooltip" :style="stackedTooltipStyle">
          <div v-if="activeStackedTooltip" class="stacked-tooltip-content">
            <div class="tooltip-header">{{ activeStackedTooltip.type }}</div>
            <div class="tooltip-value">{{ activeStackedTooltip.percentage }}%</div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card repeat-rate-card">
        <h3>Repeat Incident Rate</h3>
        <div class="kpi-value">{{ kpiData.repeatRate.value || 0 }}<span class="unit">%</span></div>
        <div class="kpi-chart donut-chart-container">
          <div class="donut-chart repeat-donut">
            <div class="donut-segment new" 
                 :style="{ '--start-angle': '0deg', '--end-angle': (3.6 * kpiData.repeatRate.new) + 'deg' }"></div>
            <div class="donut-segment repeat" 
                 :style="{ '--start-angle': (3.6 * kpiData.repeatRate.new) + 'deg', '--end-angle': '360deg' }"></div>
            <div class="donut-hole">
              <div class="donut-hole-text">{{ kpiData.repeatRate.value }}%</div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color new"></span>New ({{ kpiData.repeatRate.new }}%)</div>
          <div class="legend-item"><span class="legend-color repeat"></span>Repeat ({{ kpiData.repeatRate.repeat }}%)</div>
        </div>
      </div>
    </div>



    <!-- <div class="incident-count-card">
      <h3>Total Incidents</h3>
      <h2>{{ incidentCounts.total }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Pending Incidents</h3>
      <h2>{{ incidentCounts.pending }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Accepted Incidents</h3>
      <h2>{{ incidentCounts.accepted }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Rejected Incidents</h3>
      <h2>{{ incidentCounts.rejected }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Resolved Incidents</h3>
      <h2>{{ incidentCounts.resolved }}</h2>
    </div> -->

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import '../Incident/IncidentDashboard.css';
import axios from 'axios';
import { PopupService, PopupModal } from '@/modules/popup';

export default {
  name: 'IncidentDashboard',
  components: {
    PopupModal
  },
  data() {
    return {

      loading: true,
      kpiData: {
        mttd: { value: 0, unit: 'hours', trend: [], change_percentage: 0 },
        mttr: { value: 0, unit: 'hours', trend: [], change_percentage: 0 },
        mttc: { value: 0, unit: 'hours', trend: [], change_percentage: 0 },
        mttrv: { value: 0, unit: 'hours', trend: [] },
        firstResponseTime: { value: 0, unit: 'hours', trend: [] },
        escalationTime: { value: 0, unit: 'hours', trend: [] },
        incidentsDetected: { value: 0, byDay: [0, 0, 0, 0, 0, 0, 0] },
        reopenedIncidents: { value: 0, percentage: 0 },
        closureRate: { value: 0, unit: '%' },
        falsePositiveRate: { value: 0, unit: '%' },
        detectionAccuracy: { value: 0, unit: '%' },
        slaComplianceRate: { value: 0, unit: '%' },
        incidentsBySeverity: {
          high: 0, 
          medium: 0,
          low: 0
        },
        rootCauseCategories: {},
        incidentTypes: [], // Initialize as an empty array instead of an empty object
        incidentVolume: {
          total: 0,
          trend: []
        },
        escalationRate: {
          value: 0,
          audit: 0,
          manual: 0
        },
        repeatRate: {
          value: 0,
          new: 0,
          repeat: 0
        },
        incidentOrigins: [],
        averageCost: null,
        totalCost: null,
        costCount: null,
        costData: {
          total_cost: 0,
          by_severity: []
        }
      },
      incidentCounts: {
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0,
        resolved: 0
      },
      tooltipStyle: {
        display: 'none',
        left: '0px',
        top: '0px'
      },
      activeTooltip: null,
      pieTooltipStyle: {
        display: 'none',
        left: '0px',
        top: '0px'
      },
      activePieTooltip: null,
      rootCauseTooltipStyle: {
        display: 'none',
        left: '0px',
        top: '0px'
      },
      activeRootCauseTooltip: null,
      originTooltipStyle: {
        display: 'none',
        left: '0px',
        top: '0px'
      },
      activeOriginTooltip: null,
      stackedTooltipStyle: {
        display: 'none',
        left: '0px',
        top: '0px'
      },
      activeStackedTooltip: null
    }
  },
  methods: {

    async fetchKPIData() {
      try {
        this.loading = true;
        console.log("Starting to fetch KPI data");
        
        // Get MTTD data
        try {
          console.log("Fetching MTTD data from /api/incident/mttd/");
          const mttdResponse = await axios.get('/api/incident/mttd/', {
            params: { timeRange: 'all' }
          });
          
          if (mttdResponse.data) {
            const rawValue = mttdResponse.data.value;
            const parsedValue = parseFloat(rawValue);
            
            // Process trend data to ensure it's properly formatted for the chart
            const trendData = mttdResponse.data.trend.map(item => {
              return {
                month: item.month,
                minutes: parseFloat(item.minutes || 0),
                count: item.count || 0,
                fastest: item.fastest || 0,
                slowest: item.slowest || 0,
                details: item.details || []
              };
            });
            
            console.log("Processed trend data:", trendData);
            
            // Update MTTD data
            this.kpiData.mttd = {
              value: parsedValue,
              unit: mttdResponse.data.unit,
              trend: trendData,
              change_percentage: mttdResponse.data.change_percentage || 0
            };
            
            console.log("Updated MTTD in kpiData:", this.kpiData.mttd);
          }
        } catch (mttdError) {
          console.error('Error fetching MTTD data:', mttdError);
        }
        
        // Get MTTR data
        try {
      console.log("Fetching MTTR data from /api/incident/mttr/");
      const mttrResponse = await axios.get('/api/incident/mttr/', {
        params: { timeRange: 'all' }
      });

      if (mttrResponse.data) {
        const rawMTTR = mttrResponse.data.mttr; // Use correct field
        console.log("Raw MTTR value from API:", rawMTTR);

        const mttrHours = rawMTTR / 60; // Convert minutes to hours
        console.log("Converted MTTR value to hours:", mttrHours);

        const trendData = (mttrResponse.data.chart_data || []).map(item => ({
          month: item.date.substring(0, 7), // Extract YYYY-MM as month
          minutes: (item.value || 0) / 60,  // Convert trend points from minutes to hours
          count: item.count || 0
        }));

        this.kpiData.mttr = {
          value: mttrHours,
          unit: 'hours',
          trend: trendData,
          change_percentage: mttrResponse.data.change_percentage || 0
        };

        console.log("Updated MTTR in kpiData:", this.kpiData.mttr);
      }
    } catch (mttrError) {
      console.error('Error fetching MTTR data:', mttrError);
    }

        // Get MTTC data
try {
  console.log("Fetching MTTC data from /api/incident/mttc/");
  const mttcResponse = await axios.get('/api/incident/mttc/', {
    params: { timeRange: 'all' }
  });

  if (mttcResponse.data) {
            console.log("Raw MTTC response:", mttcResponse.data);
    const rawValue = mttcResponse.data.value;
            
            // Ensure value is properly parsed - important for displaying 36.9
    const parsedValue = parseFloat(rawValue);
            console.log("Parsed MTTC value:", parsedValue);
            
            // Update MTTC data
            this.kpiData.mttc = {
              value: parsedValue,
              unit: mttcResponse.data.unit || 'hours',
              trend: Array.isArray(mttcResponse.data.trend) ? mttcResponse.data.trend.map(item => ({
                month: item.month || '',
      minutes: parseFloat(item.minutes || 0),
      count: item.count || 0,
                fastest: item.fastest || 0,
                slowest: item.slowest || 0,
      details: item.details || []
              })) : [],
              change_percentage: parseFloat(mttcResponse.data.change_percentage || 0)
    };

    console.log("Updated MTTC in kpiData:", this.kpiData.mttc);
          } else {
            console.warn("MTTC response has no data");
  }
} catch (mttcError) {
  console.error('Error fetching MTTC data:', mttcError);
}

try {
  console.log("Fetching MTTRv data from /api/incident/mttrv/");
  const response = await axios.get('/api/incident/mttrv/', {
    params: { timeRange: 'all' }  // Or specify any filter if needed
  });

  if (response.data) {
    const rawValue = response.data.value;
    const parsedValue = parseFloat(rawValue);

    // Process trend if available or use empty array
    const trendData = Array.isArray(response.data.trend) ? response.data.trend.map(item => ({
      month: item.month || '',
      minutes: parseFloat(item.minutes || 0),
      count: item.count || 0,
      fastest: item.fastest || 0,
      slowest: item.slowest || 0,
      details: item.details || []
    })) : [];

    this.kpiData.mttrv = {
      value: parsedValue,
      unit: response.data.unit || 'hours',
      trend: trendData
    };

    console.log("Updated MTTRv in kpiData:", this.kpiData.mttrv);
  }
} catch (error) {
  console.error('Error fetching MTTRv data:', error);
}
  
try {
  console.log("Fetching False Positive Rate data from /api/incident/false-positive-rate/");
  const fprResponse = await axios.get('/api/incident/false-positive-rate/', {
    params: { timeRange: 'all' }
  });

  if (fprResponse.data) {
    console.log("Raw False Positive Rate response:", fprResponse.data);
    const rawValue = fprResponse.data.value;
    
    // Ensure value is properly parsed (percentage expected)
    const parsedValue = parseFloat(rawValue);
    console.log("Parsed False Positive Rate value:", parsedValue);

    // Update falsePositiveRate data in kpiData
    this.kpiData.falsePositiveRate = {
      value: parsedValue,
      unit: fprResponse.data.unit || '%',
      change_percentage: parseFloat(fprResponse.data.change_percentage || 0)
    };

    console.log("Updated falsePositiveRate in kpiData:", this.kpiData.falsePositiveRate);
  } else {
    console.warn("False Positive Rate response has no data");
  }
} catch (fprError) {
  console.error('Error fetching False Positive Rate data:', fprError);
}

        // Get Detection Accuracy data
        try {
    console.log("Fetching Detection Accuracy data from /api/incident/detection-accuracy/");
    const detectionAccuracyResponse = await axios.get('/api/incident/detection-accuracy/', {
      params: { timeRange: 'all' }
    });

    if (detectionAccuracyResponse.data) {
      console.log("Raw Detection Accuracy response:", detectionAccuracyResponse.data);
      const rawValue = detectionAccuracyResponse.data.value;
      const parsedValue = parseFloat(rawValue);

      this.kpiData.detectionAccuracy = {
        value: parsedValue,
        unit: detectionAccuracyResponse.data.unit || '%',
        change_percentage: parseFloat(detectionAccuracyResponse.data.change_percentage || 0)
      };

      console.log("Updated detectionAccuracy in kpiData:", this.kpiData.detectionAccuracy);
    } else {
      console.warn("Detection Accuracy response has no data");
    }
  } catch (error) {
    console.error('Error fetching Detection Accuracy data:', error);
  }
  try {
  console.log("Fetching Incident Closure Rate data from /api/incident/incident-closure-rate/");
  const response = await axios.get('/api/incident/incident-closure-rate/', {
    params: { timeRange: 'all' }  // or specify your date range
  });

  if (response.data) {
    console.log("Raw Incident Closure Rate response:", response.data);
    const rawValue = response.data.value;
    const parsedValue = parseFloat(rawValue);

    this.kpiData.closureRate = {
      value: parsedValue,
      unit: response.data.unit || '%',
      change_percentage: parseFloat(response.data.change_percentage || 0)
    };

    console.log("Updated closureRate in kpiData:", this.kpiData.closureRate);
  } else {
    console.warn("Incident Closure Rate response has no data");
  }
} catch (error) {
  console.error('Error fetching Incident Closure Rate data:', error);
}
        // Add this inside fetchKPIData method, along with other API calls
try {
  console.log("Fetching reopened incidents count data");
  const reopenedResponse = await axios.get('/api/incident/reopened-count/');
  
  if (reopenedResponse.data) {
    this.kpiData.reopenedIncidents.value = reopenedResponse.data.reopened_incidents || 0;
    this.kpiData.reopenedIncidents.percentage = reopenedResponse.data.percentage_reopened || 0;
  }
} catch (error) {
  console.error('Error fetching reopened incidents:', error);
}
        try {
  console.log("Fetching First Response Time data from /api/incident/first-response-time/");
  const firstResponse = await axios.get('/api/incident/first-response-time/', {
    params: { timeRange: 'all' }
  });

  if (firstResponse.data) {
    console.log("Raw First Response Time data:", firstResponse.data);
    
    const rawValue = firstResponse.data.value;
    const parsedValue = parseFloat(rawValue);
    
    const trendData = Array.isArray(firstResponse.data.trend) ? firstResponse.data.trend.map(item => ({
      month: item.month || '',
      minutes: parseFloat(item.minutes || 0),
      count: item.count || 0,
      fastest: item.fastest || 0,
      slowest: item.slowest || 0,
      details: item.details || []
    })) : [];
    
    this.kpiData.firstResponseTime = {
      value: parsedValue,
      unit: firstResponse.data.unit || 'hours',
      trend: trendData,
      change_percentage: parseFloat(firstResponse.data.change_percentage || 0)
    };

    console.log("Updated firstResponseTime in kpiData:", this.kpiData.firstResponseTime);
  }
} catch (error) {
  console.error('Error fetching First Response Time data:', error);
}

        // Get incident count data
        try {
          console.log("Fetching incident count data from /api/incident/count/");
          const countResponse = await axios.get('/api/incident/count/', {
            params: { timeRange: 'all' }
          });
          
          console.log("Incident count response:", JSON.stringify(countResponse.data));
          
          if (countResponse.data) {
            const totalCount = countResponse.data.value;
            const dayDistribution = countResponse.data.byDay;
            const dayDetails = countResponse.data.details || [];
            
            // Update incident count data
            this.kpiData.incidentsDetected = {
              value: totalCount,
              byDay: dayDistribution,
              details: dayDetails
            };
            
            console.log("Updated incident count:", this.kpiData.incidentsDetected.value);
            console.log("Day distribution:", this.kpiData.incidentsDetected.byDay);
          }
        } catch (countError) {
          console.error('Error fetching incident count data:', countError);
        }
        
        // Get incident severity distribution
        try {
          console.log("Fetching incidents by severity data");
          const severityResponse = await axios.get('/api/incident/by-severity/');
          
          if (severityResponse.data && severityResponse.data.data) {
            console.log("Raw severity response:", severityResponse.data);
            
            // Map the data to our existing format
            const severityData = {
              high: 0,
              medium: 0,
              low: 0
            };
            
            severityResponse.data.data.forEach(item => {
              const severity = item.severity.toLowerCase();
              if (severity in severityData) {
                severityData[severity] = item.percentage;
              }
            });
            
            // Update the kpiData
            this.kpiData.incidentsBySeverity = severityData;
            
            console.log("Updated incidents by severity:", this.kpiData.incidentsBySeverity);
          }
        } catch (severityError) {
          console.error('Error fetching incidents by severity:', severityError);
        }
        
        // Get root cause categories data
        try {
          console.log("Fetching incident root causes data");
          const rootCausesResponse = await axios.get('/api/incident/root-causes/');
          
          if (rootCausesResponse.data && rootCausesResponse.data.data) {
            console.log("Raw root causes response:", rootCausesResponse.data);
            
            // Convert the array data to an object
            const rootCausesData = {};
            rootCausesResponse.data.data.forEach(item => {
              rootCausesData[item.category] = item.percentage;
            });
            
            // Update the kpiData
            this.kpiData.rootCauseCategories = rootCausesData;
            
            console.log("Updated root cause categories:", this.kpiData.rootCauseCategories);
          }
        } catch (rootCausesError) {
          console.error('Error fetching incident root causes:', rootCausesError);
        }
        
        // Get incident origins data
        try {
          console.log("Fetching incident origins data");
          const originsResponse = await axios.get('/api/incident/origins/');
          
          if (originsResponse.data && originsResponse.data.data) {
            console.log("Raw origins response:", originsResponse.data);
            
            // Store the raw data for the pie chart
            this.kpiData.incidentOrigins = originsResponse.data.data;
            
            console.log("Updated incident origins:", this.kpiData.incidentOrigins);
          }
        } catch (originsError) {
          console.error('Error fetching incident origins:', originsError);
        }
        
        // Add additional API calls here for:
        // 1. First Response Time
        // 2. Time to Escalation
        // 3. Incident Volume
        // 4. Escalation Rate
        // 5. Repeat Rate
        // 6. Resolution SLA Breach Rate
        // 7. Incident Types
        
        // Get incident types data
        try {
          console.log("Fetching incident types data");
          const typesResponse = await axios.get('/api/incident/types/');
          
          if (typesResponse.data && typesResponse.data.data) {
            console.log("Raw incident types response:", typesResponse.data);
            
            // Store the raw data for the chart
            this.kpiData.incidentTypes = typesResponse.data.data;
            
            console.log("Updated incident types:", this.kpiData.incidentTypes);
          }
        } catch (typesError) {
          console.error('Error fetching incident types:', typesError);
        }
        
        // Fetch incident volume data
        try {
          const response = await axios.get('/api/incident/incident-volume/');
          this.kpiData.incidentVolume = response.data;
        } catch (error) {
          console.error('Error fetching incident volume:', error);
        }
        
        // Fetch escalation rate data
        try {
          console.log("Fetching escalation rate data");
          const response = await axios.get('/api/incident/escalation-rate/');
          if (response.data) {
            this.kpiData.escalationRate = {
              value: response.data.value || 0,
              audit: response.data.audit || 0,
              manual: response.data.manual || 0
            };
            console.log("Updated escalation rate:", this.kpiData.escalationRate);
          }
        } catch (error) {
          console.error('Error fetching escalation rate:', error);
        }
        // Fetch cost per incident data
try {
  console.log("Fetching cost per incident data");
  const costResponse = await axios.get('/api/incident/cost/');  // Use the correct endpoint

  if (costResponse.data) {
    console.log("Cost data response:", costResponse.data);

    this.kpiData.costData = {
      total_cost: costResponse.data.total_cost || 0,
      total_cost_k: costResponse.data.total_cost_k || 0,
      display_total: costResponse.data.display_total || '0',
      by_severity: Array.isArray(costResponse.data.by_severity)
        ? costResponse.data.by_severity.map(item => ({
            severity: item.severity || 'Unknown',
            cost: item.cost || 0,
            cost_k: item.cost_k || 0,
            label: item.label || item.severity
          }))
        : []
    };

    console.log("Updated costData:", this.kpiData.costData);
  }
} catch (error) {
  console.error('Error fetching cost per incident:', error);
}

        // Add this to your fetchKPIData method
        try {
          console.log("Fetching repeat rate data");
          const response = await axios.get('/api/incident/repeat-rate/');
          if (response.data) {
            this.kpiData.repeatRate = {
              value: response.data.value || 0,
              new: response.data.new || 0,
              repeat: response.data.repeat || 0
            };
            console.log("Updated repeat rate:", this.kpiData.repeatRate);
          }
        } catch (error) {
          console.error('Error fetching repeat rate:', error);
        }
        
        this.loading = false;
      } catch (error) {
        console.error('Error in fetchKPIData:', error);
        PopupService.error('Error loading dashboard data. Please try again later.');
        this.loading = false;
      }
    },
    // Fixed method to generate SVG path for trend line
    generateTrendPath(dataPoints) {
  if (!dataPoints || dataPoints.length === 0) {
    return '';
  }

  const maxValue = Math.max(...dataPoints);
  const minValue = Math.min(...dataPoints);
  const range = maxValue - minValue || 1;

  const svgWidth = 300;
  const svgHeight = 60;
  const paddingTop = 10;
  const paddingBottom = 10;
  const usableHeight = svgHeight - paddingTop - paddingBottom;

  const xStep = svgWidth / (dataPoints.length - 1 || 1);

  let path = `M0,${svgHeight - paddingBottom - ((dataPoints[0] - minValue) / range * usableHeight)}`;

  for (let i = 1; i < dataPoints.length; i++) {
    const x = i * xStep;
    const y = svgHeight - paddingBottom - ((dataPoints[i] - minValue) / range * usableHeight);
    path += ` L${x},${y}`;
  }

  return path;
},

getTrendPoints(dataPoints) {
  if (!dataPoints || dataPoints.length === 0) {
    return [];
  }

  const maxValue = Math.max(...dataPoints);
  const minValue = Math.min(...dataPoints);
  const range = maxValue - minValue || 1;

  const svgWidth = 300;
  const svgHeight = 60;
  const paddingTop = 10;
  const paddingBottom = 10;
  const usableHeight = svgHeight - paddingTop - paddingBottom;

  const xStep = svgWidth / (dataPoints.length - 1 || 1);

  return dataPoints.map((value, index) => ({
    x: index * xStep,
    y: svgHeight - paddingBottom - ((value - minValue) / range * usableHeight)
  }));
},

    fetchIncidentCounts() {
      console.log("Fetching incident counts");
      fetch('/api/incidents/counts/')
        .then(response => response.json())
        .then(data => {
          console.log("Received incident counts:", data);
          this.incidentCounts = data;
        })
        .catch(error => {
          console.error('Error fetching incident counts:', error);
        });
    },
    calculateBarHeight(value, allValues) {
      if (!allValues || allValues.length === 0 || !value) return '0%';
      const maxValue = Math.max(...allValues);
      if (maxValue === 0) return '0%';
      return `${(value / maxValue * 85)}%`;  // 85% max height for better visual
    },
    showTooltip(event, pointData) {
      // Get position relative to the chart
      const rect = event.target.closest('.line-chart').getBoundingClientRect();
      const chartWidth = rect.width;
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      
      // Determine if tooltip should appear on left or right side
      // to avoid being cut off at edges
      let x, y;
      
      // Calculate tooltip width estimate (using min-width as base)
      const estimatedWidth = 150;
      
      // Position horizontally to avoid cutoff
      if (mouseX < estimatedWidth / 2) {
        // Too close to left edge, position to the right of cursor
        x = mouseX + 10;
        this.tooltipStyle.transform = 'translateX(0)';
      } else if (mouseX > chartWidth - estimatedWidth / 2) {
        // Too close to right edge, position to the left of cursor
        x = mouseX - 10;
        this.tooltipStyle.transform = 'translateX(-100%)';
      } else {
        // Enough space on both sides, center on cursor
        x = mouseX;
        this.tooltipStyle.transform = 'translateX(-50%)';
      }
      
      // Position above cursor but not too high
      y = Math.max(5, mouseY - 70);
      
      this.tooltipStyle = {
        display: 'block',
        left: `${x}px`,
        top: `${y}px`,
        transform: this.tooltipStyle.transform,
        zIndex: 1000
      };
      
      this.activeTooltip = pointData;
    },
    hideTooltip() {
      this.tooltipStyle = {
        display: 'none',
        left: '0px',
        top: '0px'
      };
      this.activeTooltip = null;
    },
    fetchMTTR() {
      console.log("Fetching MTTR data");
      const timeRange = this.selectedTimeRange;
      fetch(`/api/incident/mttr/?timeRange=${timeRange}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log("MTTR data received:", data);
          this.mttr = data.mttr;
          this.mttrChartData = data.chart_data;
          this.mttrChangePercentage = data.change_percentage;
          this.$nextTick(() => {
            this.renderMTTRChart();
          });
        })
        .catch(error => {
          console.error("Error fetching MTTR data:", error);
        });
    },
    renderMTTRChart() {
      if (!this.mttrChartData || this.mttrChartData.length === 0) return;
      
      const svgElement = this.$refs.mttrChart;
      if (!svgElement) return;
      
      // Clear previous chart
      while (svgElement.firstChild) {
        svgElement.removeChild(svgElement.firstChild);
      }
      
      const width = 300;
      const height = 60;
      const padding = 5;
      const chartWidth = width - 2 * padding;
      const chartHeight = height - 2 * padding;
      
      // Extract values and dates
      const values = this.mttrChartData.map(item => item.value);
      const dates = this.mttrChartData.map(item => item.date);
      const counts = this.mttrChartData.map(item => item.count);
      
      // Find min and max values
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      
      // Create scale functions
      const xScale = index => padding + (index / (values.length - 1)) * chartWidth;
      const yScale = value => height - padding - ((value - minValue) / (maxValue - minValue)) * chartHeight;
      
      // Create path
      let pathData = '';
      values.forEach((value, index) => {
        const x = xScale(index);
        const y = yScale(value);
        pathData += (index === 0 ? 'M' : 'L') + x + ',' + y;
      });
      
      // Create path element
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', pathData);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', '#3498db');
      path.setAttribute('stroke-width', '2');
      svgElement.appendChild(path);
      
      // Add data points with tooltips
      values.forEach((value, index) => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        const x = xScale(index);
        const y = yScale(value);
        
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', '4');
        circle.setAttribute('fill', '#3498db');
        
        // Create tooltip data
        const date = dates[index];
        const count = counts[index];
        
        // Add tooltip event handlers
        circle.addEventListener('mouseover', (event) => {
          const tooltip = document.getElementById('mttr-tooltip');
          tooltip.innerHTML = `<strong>Date:</strong> ${date}<br><strong>MTTR:</strong> ${value} mins<br><strong>Incidents:</strong> ${count}`;
          
          // Position tooltip to avoid being cut off
          const rect = event.target.getBoundingClientRect();
          const tooltipRect = tooltip.getBoundingClientRect();
          const viewportWidth = window.innerWidth;
          
          // Calculate position to keep tooltip visible
          let leftPos = rect.left;
          if (leftPos + tooltipRect.width > viewportWidth - 20) {
            leftPos = rect.left - tooltipRect.width;
          }
          
          tooltip.style.left = `${leftPos}px`;
          tooltip.style.top = `${rect.top - tooltipRect.height - 10}px`;
          tooltip.style.display = 'block';
        });
        
        circle.addEventListener('mouseout', () => {
          document.getElementById('mttr-tooltip').style.display = 'none';
        });
        
        svgElement.appendChild(circle);
      });
    },
    refreshData() {
      this.fetchMTTD();
      this.fetchIncidentsCount();
      this.fetchMTTR(); // Add this line to fetch MTTR data
      // ... any other data fetch methods
    },
    showPieTooltip(event, severity, percentage) {
      // Calculate the count based on percentage and total incidents
      const totalIncidents = this.incidentCounts.total || 100;
      const count = (percentage / 100) * totalIncidents;
      
      // Get position relative to the chart
      const rect = event.target.closest('.pie-chart-container').getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      
      // Position tooltip
      this.pieTooltipStyle = {
        display: 'block',
        left: `${mouseX}px`,
        top: `${mouseY - 60}px`,
      };
      
      // Set tooltip content
      this.activePieTooltip = {
        severity: severity,
        percentage: percentage,
        count: count
      };
    },
    hidePieTooltip() {
      this.pieTooltipStyle = {
        display: 'none',
        left: '0px',
        top: '0px'
      };
      this.activePieTooltip = null;
    },
    showRootCauseTooltip(event, category, percentage) {
      // Calculate the count based on percentage and total incidents
      const totalIncidents = this.incidentCounts.total || 100;
      const count = (percentage / 100) * totalIncidents;
      
      // Get position relative to the bar
      const rect = event.target.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const topY = rect.top - 10;
      
      // Position tooltip
      this.rootCauseTooltipStyle = {
        display: 'block',
        left: `${centerX}px`,
        top: `${topY - 60}px`,
      };
      
      // Set tooltip content
      this.activeRootCauseTooltip = {
        category: category,
        percentage: percentage,
        count: count
      };
    },
    hideRootCauseTooltip() {
      this.rootCauseTooltipStyle = {
        display: 'none',
        left: '0px',
        top: '0px'
      };
      this.activeRootCauseTooltip = null;
    },
    getOriginColor(origin) {
      // Map specific origin types to specific colors
      const colorMap = {
        'Manual': '#ffd166',  // Amber yellow 
        'SIEM': '#118ab2',    // Teal blue
        'Unknown': '#073b4c', // Dark navy
        'Audit Finding': '#ef476f', // Coral pink
        // Add fallback colors for any other types
        'System': '#06d6a0',
        'User': '#4361ee',
        'Automated': '#ff6b6b'
      };
      
      // Return the mapped color or a default if not found
      return colorMap[origin] || '#95a5a6'; // Default gray
    },
    getStrokeDashOffset(index) {
      // Calculate the stroke-dashoffset for each segment
      // This positions each segment after the previous ones
      let offset = 0;
      for (let i = 0; i < index; i++) {
        offset += this.kpiData.incidentOrigins[i].percentage * 2.51;
      }
      return offset;
    },
    showOriginTooltip(event, origin, percentage, count) {
      try {
        // Get position relative to the chart
        const container = event.target.closest('.small-donut-container');
        if (!container) {
          console.warn('Could not find chart container for tooltip positioning');
          return;
        }
        
        const rect = container.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        
        // Position tooltip
        this.originTooltipStyle = {
          display: 'block',
          left: `${mouseX}px`,
          top: `${mouseY - 10}px`,
          zIndex: 2000 // Ensure it's above other elements
        };
        
        // Set tooltip content
        this.activeOriginTooltip = {
          origin: origin,
          percentage: percentage,
          count: count
        };
      } catch (err) {
        console.error('Error showing origin tooltip:', err);
        // Hide tooltip in case of error
        this.hideOriginTooltip();
      }
    },
    hideOriginTooltip() {
      this.originTooltipStyle = {
        display: 'none',
        left: '0px',
        top: '0px'
      };
      this.activeOriginTooltip = null;
    },
    getVolumeTrendPath(trendData) {
      if (!trendData || trendData.length === 0) return '';
      
      const width = 400;
      const height = 80;
      const margin = 5;
      
      // Find max value for scaling
      const maxCount = Math.max(...trendData.map(d => d.count), 1);
      
      // Calculate points
      const points = trendData.map((point, index) => {
        const x = margin + (index * (width - 2 * margin) / (trendData.length - 1));
        const y = height - margin - ((point.count / maxCount) * (height - 2 * margin));
        return `${x},${y}`;
      });
      
      // Create path
      const linePath = `M${points.join(' L')}`;
      
      // Add area fill
      const areaPath = `${linePath} L${width - margin},${height - margin} L${margin},${height - margin} Z`;
      
      return areaPath;
    },
    showStackedTooltip(event, type, percentage) {
      const rect = event.target.getBoundingClientRect();
      this.stackedTooltipStyle = {
        display: 'block',
        left: rect.left + (rect.width / 2) + 'px',
        top: rect.top - 40 + 'px'
      };
      
      this.activeStackedTooltip = {
        type: type,
        percentage: percentage
      };
    },
    hideStackedTooltip() {
      this.stackedTooltipStyle = {
        display: 'none',
        left: '0px',
        top: '0px'
      };
      this.activeStackedTooltip = null;
    },
    fetchIncidentCost() {
      console.log('Fetching incident cost data...');
      axios.get('/api/incident/cost/')
        .then(response => {
          console.log('Cost data received:', response.data);
          this.kpiData.costData = response.data;
        })
        .catch(error => {
          console.error('Error fetching incident cost:', error);
        });
    },
    formatCurrency(value) {
      if (!value) return '0';
      const amount = value / 1000; // Convert to K without rounding
      return amount;
    }
  },
  mounted() {
    this.fetchKPIData();
    this.fetchIncidentCounts();
    // Remove this duplicate call if it's already in fetchKPIData
    // this.fetchIncidentCost();  
  }
}
</script>

<style scoped>
/* Additional styles needed for new charts */
.pie-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
}

.pie-chart {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #e0e0e0;
  overflow: hidden;
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: 50% 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%);
}

.pie-segment.critical {
  background-color: #ef4444;
  transform: rotate(0deg);
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 1%) 0%, calc(50% + var(--segment-size) * 1%) 100%, 50% 100%);
}

.pie-segment.high {
  background-color: #f97316;
  transform: rotate(0deg);
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 1%) 0%, calc(50% + var(--segment-size) * 1%) 100%, 50% 100%);
}

.pie-segment.medium {
  background-color: #facc15;
  transform: rotate(calc(var(--segment-size-high) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 1%) 0%, calc(50% + var(--segment-size) * 1%) 100%, 50% 100%);
}

.pie-segment.low {
  background-color: #84cc16;
  transform: rotate(calc((var(--segment-size-high) + var(--segment-size-medium)) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 1%) 0%, calc(50% + var(--segment-size) * 1%) 100%, 50% 100%);
}

.pie-segment.user {
  background-color: #3498db;
}

.pie-segment.system {
  background-color: #1abc9c;
  transform: rotate(calc(var(--segment-size-user, 65%) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.automated {
  background-color: #9b59b6;
}

.pie-segment.manual {
  background-color: #e74c3c;
  transform: rotate(calc(var(--segment-size-automated, 40%) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  font-size: 0.7rem;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.legend-color {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 4px;
  border-radius: 2px;
}

.legend-color.critical { background-color: #ef4444; }
.legend-color.high { background-color: #f97316; }
.legend-color.medium { background-color: #facc15; }
.legend-color.low { background-color: #84cc16; }
.legend-color.user { background-color: #3498db; }
.legend-color.system { background-color: #1abc9c; }
.legend-color.automated { background-color: #9b59b6; }
.legend-color.manual { background-color: #e74c3c; }

.donut-chart {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(
    #ef4444 calc(var(--percentage, 0) * 1%), 
    #e0e0e0 0
  );
  margin: 0 auto;
}


.donut-hole {
  position: absolute;
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  top: 20px;
  left: 20px;
}

.donut-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  clip: rect(0px, 100px, 100px, 50px);
  background: #ef4444;
}

.root-cause-card, .threat-types-card {
  flex: 2;
}

.bar-chart-container {
  height: 200px;
  margin-top: 10px;
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.h-bar-label {
  width: 110px;
  font-size: 0.8rem;
  text-align: right;
}

.h-bar-track {
  flex: 1;
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.h-bar-progress {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.h-bar-progress:hover {
  filter: brightness(1.1);
}

.h-bar-value {
  width: 40px;
  font-size: 0.8rem;
  text-align: left;
}

.vertical-bar-chart {
  display: flex;
  height: 100%;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 30px;
}

.v-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 18%;
  position: relative;
}

.v-bar-progress {
  width: 100%;
  background: #3498db;
  border-radius: 6px 6px 0 0;
  transition: height 0.5s ease;
}

.v-bar-label {
  position: absolute;
  bottom: -25px;
  font-size: 0.8rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.v-bar-value {
  margin-bottom: 5px;
  font-size: 0.8rem;
  font-weight: bold;
}

.bar.critical { background-color: #ef4444; }
.bar.high { background-color: #f97316; }
.bar.medium { background-color: #facc15; }
.bar.low { background-color: #84cc16; }

.bar-chart.horizontal {
  flex-direction: column;
  height: auto;
}

.bar-chart.horizontal .bar {
  display: flex;
  align-items: center;
  padding-left: 8px;
  height: 20px !important;
  margin: 5px 0;
  color: white;
  font-size: 0.8rem;
  border-radius: 4px;
}

.progress.red {
  background-color: #ef4444;
}

/* Incident Volume Area Chart */
.volume-chart {
  height: 80px;
}

.area-chart {
  width: 100%;
  height: 100%;
}

.area-chart svg {
  width: 100%;
  height: 100%;
}

/* Escalation Rate Stacked Bar */
.stacked-bar-container {
  margin-top: 10px;
  width: 100%;
}

.stacked-bar {
  height: 20px;
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
}

.stacked-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.stacked-segment.audit {
  background-color: #2196F3;
}

.stacked-segment.manual {
  background-color: #9C27B0;
}

.stacked-bar-legend {
  display: flex;
  justify-content: space-around;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 4px;
  border-radius: 2px;
}

.legend-color.audit {
  background-color: #2196F3;
}

.legend-color.manual {
  background-color: #9C27B0;
}

.stacked-tooltip {
  position: absolute;
  z-index: 100;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  transform: translateX(-50%);
}

.tooltip-header {
  font-weight: bold;
}

.tooltip-value {
  text-align: center;
}

/* Repeat Incident Rate Donut */
.donut-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.repeat-donut {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #ecf0f1;
}

.donut-segment.new {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #2ecc71;
  border-radius: 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%);
  transform-origin: center;
  transform: rotate(var(--start-angle));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + 100% * cos(var(--end-angle))) calc(50% - 100% * sin(var(--end-angle))), calc(50% + 100% * cos(var(--start-angle))) calc(50% - 100% * sin(var(--start-angle))));
}

.donut-segment.repeat {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #e74c3c;
  border-radius: 50%;
  transform-origin: center;
  transform: rotate(var(--start-angle));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + 100% * cos(var(--end-angle))) calc(50% - 100% * sin(var(--end-angle))), calc(50% + 100% * cos(var(--start-angle))) calc(50% - 100% * sin(var(--start-angle))));
}

.donut-hole {
  position: absolute;
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 50%;
  top: 15px;
  left: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-hole-text {
  font-size: 1rem;
  font-weight: bold;
  color: #2c3e50;
}

.legend-color.new {
  background-color: #2ecc71;
}

.legend-color.repeat {
  background-color: #e74c3c;
}

/* Line Chart Styles */
.line-chart {
  width: 100%;
  height: 40px;
  margin-bottom: 5px;
  position: relative;
}

.line-chart svg {
  width: 100%;
  height: 100%;
}

.chart-months {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #7f8c8d;
  margin-top: 5px;
  padding: 0 5px;
}

/* Style for value change indicators */
.value-change {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  margin-left: 10px;
  vertical-align: middle;
}

.value-change.positive {
  color: #4ade80;
}

.value-change.negative {
  color: #f87171;
}

.value-change i {
  margin-right: 2px;
}

/* Update existing kpi-chart for line charts */
.kpi-chart {
  height: auto;
  position: relative;
  margin-bottom: 10px;
}

/* Add these styles to your existing styles */
.tooltip-container {
  position: relative;
}

.tooltip {
  visibility: hidden;
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(44, 62, 80, 0.95);
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.2s;
  min-width: 120px;
  text-align: left;
}

.tooltip-incidents {
  margin-top: 4px;
  font-size: 0.7rem;
}

.tooltip-incident {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.95) transparent transparent transparent;
}

.tooltip-container:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

/* Make the bars look more interactive */
.bar {
  transition: all 0.2s ease-in-out;
}

.bar:hover {
  filter: brightness(1.1);
  cursor: pointer;
}

.data-point {
  transition: r 0.2s ease;
}

.hover-area:hover + .data-point,
.hover-area:hover {
  cursor: pointer;
}

.pie-segment-path {
  cursor: pointer;
  transition: opacity 0.2s;
}

.pie-segment-path:hover {
  opacity: 0.8;
}

.pie-tooltip {
  position: absolute;
  background-color: rgba(44, 62, 80, 0.98);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  z-index: 1000;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  min-width: 120px;
  text-align: center;
  transform: translate(-50%, -100%);
}

.pie-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.98) transparent transparent transparent;
}

.pie-tooltip-header {
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.pie-tooltip-value {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 2px;
}

.pie-tooltip-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.root-cause-tooltip {
  position: absolute;
  background-color: rgba(44, 62, 80, 0.98);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  z-index: 1000;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  min-width: 120px;
  text-align: center;
  transform: translate(-50%, -100%);
}

.root-cause-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.98) transparent transparent transparent;
}

.root-cause-tooltip-header {
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.root-cause-tooltip-value {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 2px;
}

.root-cause-tooltip-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.origin-tooltip {
  position: fixed; /* Change from absolute to fixed */
  background-color: rgba(44, 62, 80, 0.98);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  z-index: 2000; /* Increase z-index */
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  min-width: 120px;
  text-align: center;
  transform: translate(-50%, -100%);
}

.origin-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.98) transparent transparent transparent;
}

.origin-tooltip-header {
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.origin-tooltip-value {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 2px;
}

.origin-tooltip-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.enhanced-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  font-size: 0.7rem;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.legend-color {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 4px;
  border-radius: 2px;
}

.legend-color.critical { background-color: #ef4444; }
.legend-color.high { background-color: #f97316; }
.legend-color.medium { background-color: #facc15; }
.legend-color.low { background-color: #84cc16; }
.legend-color.user { background-color: #3498db; }
.legend-color.system { background-color: #1abc9c; }
.legend-color.automated { background-color: #9b59b6; }
.legend-color.manual { background-color: #e74c3c; }

.donut-chart-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.donut-segment-path {
  cursor: pointer;
  transition: all 0.3s ease;
}

.donut-segment-path:hover {
  stroke-width: 22px;
  filter: brightness(1.1);
}

.origin-tooltip {
  position: fixed; /* Change from absolute to fixed */
  background-color: rgba(44, 62, 80, 0.95);
  color: white;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 0.75rem;
  z-index: 1000;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 3px 12px rgba(0,0,0,0.4);
  min-width: 140px;
  text-align: center;
  transform: translate(-50%, -100%);
}

.origin-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.95) transparent transparent transparent;
}

.origin-tooltip-header {
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.origin-tooltip-value {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.origin-tooltip-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.9);
}

.enhanced-legend {
  margin-top: 15px;
}

.enhanced-legend .legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  padding: 2px 0;
}

.enhanced-legend .legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  margin-right: 8px;
}

.enhanced-legend .legend-text {
  display: flex;
  flex-direction: column;
}

.enhanced-legend .legend-label {
  font-weight: bold;
  font-size: 0.75rem;
}

.enhanced-legend .legend-stats {
  font-size: 0.7rem;
  color: #666;
}

/* Compact styles */
.compact-card {
  flex: 1;
  margin-right: 10px;
}

.compact-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  font-size: 0.7rem;
}

.legend-item.compact-legend-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.legend-color.compact-legend-item {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 4px;
  border-radius: 2px;
}

.legend-compact-text {
  font-size: 0.7rem;
  color: #666;
}

.small-donut-container {
  height: 90px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative; /* Add this to ensure tooltips position correctly */
}

.small-donut-container .donut-hole {
  position: absolute;
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  top: 20px;
  left: 20px;
}

.small-donut-container .donut-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  clip: rect(0px, 100px, 100px, 50px);
  background: #ef4444;
}

/* Add these styles for the smaller chart */
.compact-card {
  min-height: auto;
}

.small-donut-container {
  height: 90px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.compact-legend {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4px;
  margin-top: 5px;
  font-size: 0.65rem;
}

.compact-legend-item {
  margin-right: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.legend-compact-text {
  font-size: 0.65rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Add these styles for incident type bars */
.v-bar-progress.type-color-0 { background-color: #3b82f6; }
.v-bar-progress.type-color-1 { background-color: #10b981; }
.v-bar-progress.type-color-2 { background-color: #f59e0b; }
.v-bar-progress.type-color-3 { background-color: #ef4444; }
.v-bar-progress.type-color-4 { background-color: #8b5cf6; }

.no-data-message {
  width: 100%;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  padding: 20px 0;
}

.trend-chart {
  margin-top: 10px;
  height: 100px;
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.stacked-bar-legend {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 0.7rem;
}

.legend-item.stacked-legend-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.legend-label {
  font-size: 0.7rem;
  color: #666;
}

.stacked-tooltip {
  position: absolute;
  background-color: rgba(44, 62, 80, 0.98);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  z-index: 1000;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  min-width: 120px;
  text-align: center;
  transform: translate(-50%, -100%);
}

.stacked-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(44, 62, 80, 0.98) transparent transparent transparent;
}

.stacked-tooltip-content {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.8);
}

.cost-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.cost-card h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.1rem;
  color: #333;
}

.cost-card .kpi-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 15px 0;
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cost-bar {
  padding: 6px 10px;
  border-radius: 4px;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: left;
  white-space: nowrap;
}

.cost-bar.critical {
  background-color: #ef4444;
}

.cost-bar.high {
  background-color: #f97316;
}

.cost-bar.medium {
  background-color: #facc15;
  color: #333;
}

.cost-bar.low {
  background-color: #84cc16;
}
</style> 