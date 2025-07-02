<template>
  <div :class="['sidebar', { collapsed: isCollapsed }]">
    <div class="sidebar-header">
      <div class="logo-container">
        <div class="logo-wrapper" @click="navigate('/home')">
          <img :src="logo" alt="GRC Logo" class="logo-image" />
          <span v-if="!isCollapsed" class="logo-text">GRC</span>
        </div>
        <button v-if="!isCollapsed" class="toggle" @click="toggleCollapse">
          {{ isCollapsed ? '»' : '«' }}
        </button>
      </div>
    </div>

    <nav class="menu">
      <!-- Policy Section -->
      <div @click="toggleSubmenu('policy')" class="menu-item has-submenu" :class="{'expanded': openMenus.policy}">
        <i class="fas fa-file-alt icon"></i>
        <span v-if="!isCollapsed">Policy</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.policy" class="submenu">
        <!-- 1. Policy Creation -->
        <div @click="toggleSubmenu('policyCreation')" class="menu-item has-submenu" :class="{'expanded': openMenus.policyCreation}">
          <i class="fas fa-plus-square icon"></i>
          <span>Policy Creation</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.policyCreation" class="submenu">
          <div class="menu-item" @click="navigate('/create-policy/create')">
            <i class="fas fa-plus icon"></i>
            <span>Create Policy</span>
          </div>
          <!-- <div class="menu-item" @click="navigate('/create-policy/framework')">
            <i class="fas fa-sitemap icon"></i>
            <span>Create Framework</span>
          </div> -->
          <div class="menu-item" @click="navigate('/create-policy/upload-framework')">
            <i class="fas fa-upload icon"></i>
            <span>Upload Framework</span>
          </div>
          <div class="menu-item" @click="navigate('/create-policy/tailoring')">
            <i class="fas fa-edit icon"></i>
            <span>Tailoring & Templating</span>
          </div>
          <div class="menu-item" @click="navigate('/create-policy/versioning')">
            <i class="fas fa-code-branch icon"></i>
            <span>Versioning</span>
          </div>
        </div>

        <!-- 2. Policies List -->
        <div @click="toggleSubmenu('policiesList')" class="menu-item has-submenu" :class="{'expanded': openMenus.policiesList}">
          <i class="fas fa-list icon"></i>
          <span>Policies List</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.policiesList" class="submenu">
          <div class="menu-item" @click="navigate('/policies-list/all')">
            <i class="fas fa-list-alt icon"></i>
            <span>All Policies</span>
          </div>
          <div class="menu-item" @click="navigate('/tree-policies')">
            <i class="fas fa-sitemap icon"></i>
            <span>Tree Policies</span>
          </div>
        </div>
        
        <div @click="navigate('/framework-explorer')" class="menu-item">
            <i class="fas fa-cubes icon"></i>
            <span>Framework Explorer</span>
          </div>

        <!-- 3. Policy Approval -->
        <div class="menu-item" @click="navigate('/policy/approval')">
          <i class="fas fa-check-circle icon"></i>
          <span>Policy Approval</span>
        </div>
        <div class="menu-item" @click="navigate('/framework-approval')">
          <i class="fas fa-check-circle icon"></i>
          <span>Framework Approval</span>
        </div>
        <div class="menu-item" @click="navigate('/framework-status-changes')">
          <i class="fas fa-exchange-alt icon"></i>
          <span>Status Change Requests</span>
        </div>

        <!-- 4. Performance Analysis -->
        <div @click="toggleSubmenu('performanceAnalysis')" class="menu-item has-submenu" :class="{'expanded': openMenus.performanceAnalysis}">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.performanceAnalysis" class="submenu">
          <div class="menu-item" @click="navigate('/policy/performance/kpis')">
            <i class="fas fa-chart-bar icon"></i>
            <span>KPIs Analysis</span>
          </div>
          <div class="menu-item" @click="navigate('/policy/performance/dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>User Dashboard</span>
          </div>
        </div>
      </div>
      
<!-- Compliance Section -->
      <div @click="toggleSubmenu('compliances')" class="menu-item has-submenu" :class="{'expanded': openMenus.compliances}">
        <i class="fas fa-check-circle icon"></i>
        <span v-if="!isCollapsed">Compliance</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.compliances" class="submenu">
        <!-- 1. Compliance List -->
        <div @click="toggleSubmenu('complianceList')" class="menu-item has-submenu" :class="{'expanded': openMenus.complianceList}">
          <i class="fas fa-list icon"></i>
          <span>Compliance List</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.complianceList" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/list')">
            <i class="fas fa-shield-alt icon"></i>
            <span>Control Management</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/audit-status')">
            <i class="fas fa-tasks icon"></i>
            <span>Compliance Audit Management</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/approver')">
            <i class="fas fa-check-double icon"></i>
            <span>Compliance Approval</span>
          </div>
        </div>

        <!-- 2. Compliance Creation -->
        <div @click="toggleSubmenu('complianceCreation')" class="menu-item has-submenu" :class="{'expanded': openMenus.complianceCreation}">
          <i class="fas fa-plus-square icon"></i>
          <span>Compliance Creation</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.complianceCreation" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/create')">
            <i class="fas fa-plus icon"></i>
            <span>Create Compliance</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/tailoring')">
            <i class="fas fa-edit icon"></i>
            <span>Tailoring & Templating</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/versioning')">
            <i class="fas fa-code-branch icon"></i>
            <span>Versioning</span>
          </div>
        </div>

        <!-- 3. Performance Analysis -->
        <div @click="toggleSubmenu('compliancePerformance')" class="menu-item has-submenu" :class="{'expanded': openMenus.compliancePerformance}">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.compliancePerformance" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/user-dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>Compliance Dashboard</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/kpi-dashboard')">
            <i class="fas fa-chart-bar icon"></i>
            <span>Compliance KPI</span>
          </div>
        </div>
      </div>


      <!-- Risk Section -->
      <div @click="toggleSubmenu('risk')" class="menu-item has-submenu" :class="{'expanded': openMenus.risk}">
        <i class="fas fa-exclamation-triangle icon"></i>
        <span v-if="!isCollapsed">Risk</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.risk" class="submenu">
        
        
        <!-- Risk Register with nested submenu -->
        <div @click="toggleSubmenu('riskRegister')" class="menu-item has-submenu" :class="{'expanded': openMenus.riskRegister}">
          <i class="fas fa-clipboard-list icon"></i>
          <span>Risk Register</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.riskRegister" class="submenu nested-submenu">
          <div class="menu-item" @click="navigate('/risk/riskregister-list')">
            <i class="fas fa-list icon"></i>
            <span>Risk Register List</span>
          </div>
          <div class="menu-item" @click="navigate('/risk/create-risk')">
            <i class="fas fa-plus icon"></i>
            <span>Create Risk</span>
          </div>
          <div class="menu-item" @click="navigate('/risk/tailoring')">
            <i class="fas fa-edit icon"></i>
            <span>Tailoring Existing Risk</span>
          </div>
        </div>
        
        <!-- Risk Instances with nested submenu -->
        <div @click="toggleSubmenu('riskInstances')" class="menu-item has-submenu" :class="{'expanded': openMenus.riskInstances}">
          <i class="fas fa-th-list icon"></i>
          <span>Risk Instances</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.riskInstances" class="submenu nested-submenu">
          <div class="menu-item" @click="navigate('/risk/riskinstances-list')">
            <i class="fas fa-list icon"></i>
            <span>Risk Instances List</span>
          </div>
          <div class="menu-item" @click="navigate('/risk/create-instance')">
            <i class="fas fa-plus icon"></i>
            <span>Create Instance</span>
          </div>
          <div class="menu-item" @click="navigate('/risk/scoring')">
            <i class="fas fa-chart-line icon"></i>
            <span>Risk Scoring</span>
          </div>
        </div>
        
        <!-- Risk Handling section -->
        <div @click="navigate('/risk/resolution')" class="menu-item">
          <i class="fas fa-cogs icon"></i>
          <span>Risk Handling</span>
        </div>

        <!-- Risk Analytics with collapsible submenu -->
        <div @click="toggleSubmenu('riskAnalytics')" class="menu-item has-submenu" :class="{'expanded': openMenus.riskAnalytics}">
          <i class="fas fa-chart-bar icon"></i>
          <span>Risk Analytics</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.riskAnalytics" class="submenu nested-submenu">
          <div class="menu-item" @click="navigate('/risk/riskdashboard')">
            <i class="fas fa-th-large icon"></i>
            <span>Dashboard</span>
          </div>
          <div class="menu-item" @click="navigate('/risk/riskkpi')">
            <i class="fas fa-chart-pie icon"></i>
            <span>KPI Dashboard</span>
          </div>
        </div>
      </div>
      <!-- Auditor Section -->
      <div @click="toggleSubmenu('auditor')" class="menu-item has-submenu" :class="{'expanded': openMenus.auditor}">
        <i class="fas fa-user-tie icon"></i>
        <span v-if="!isCollapsed">Auditor</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.auditor" class="submenu">
        <div class="menu-item" @click="navigate('/auditor/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Audits</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/assign')">
          <i class="fas fa-check-square icon"></i>
          <span>Assign Audit</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reviews')">
          <i class="fas fa-tasks icon"></i>
          <span>Review Audits</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reports')">
          <i class="fas fa-file-alt icon"></i>
          <span>Audit Reports</span>
        </div>
        <div @click="toggleSubmenu('performance')" class="menu-item has-submenu" :class="{'expanded': openMenus.performance}">
          <i class="fas fa-chart-bar icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.performance" class="submenu">
          <div class="menu-item" @click="navigate('/auditor/performance/kpi')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>KPIs Analysis</span>
          </div>
          <div class="menu-item" @click="navigate('/auditor/performance/userdashboard')">
            <i class="fas fa-chart-line icon"></i>
            <span>Dashboard</span>
          </div>
        </div>
      </div>


      <!-- Incident Section -->
      <div @click="toggleSubmenu('incident')" class="menu-item has-submenu" :class="{'expanded': openMenus.incident}">
        <i class="fas fa-exclamation-circle icon"></i>
        <span v-if="!isCollapsed">Incident</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.incident" class="submenu">
        <div @click="toggleSubmenu('incidentManagement')" class="menu-item has-submenu" :class="{'expanded': openMenus.incidentManagement}">
          <i class="fas fa-clipboard-list icon"></i>
          <span>Incident Management</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.incidentManagement" class="submenu">
          <div class="menu-item" @click="navigate('/incident/incident')">
            <i class="fas fa-list icon"></i>
            <span>Incident List</span>
          </div>
          <div class="menu-item" @click="navigate('/incident/create')">
            <i class="fas fa-plus icon"></i>
            <span>Create Incident</span>
          </div>
          <!-- Audit Findings List -->
          <div class="menu-item" @click="navigate('/incident/audit-findings')">
            <i class="fas fa-search icon"></i>
            <span>Audit Findings</span>
          </div>
          <!-- User Tasks -->
          <div class="menu-item" @click="navigate('/incident/user-tasks')">
            <i class="fas fa-user-check icon"></i>
            <span>User Tasks</span>
          </div>
        </div>
        <div @click="toggleSubmenu('incidentPerformance')" class="menu-item has-submenu" :class="{'expanded': openMenus.incidentPerformance}">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.incidentPerformance" class="submenu">
          <div class="menu-item" @click="navigate('/incident/dashboard')">
            <i class="fas fa-chart-pie icon"></i>
            <span>KPIs Analysis</span>
          </div>
          <div class="menu-item" @click="navigate('/incident/performance/dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>Dashboard</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="bottom-section">
      <!-- Notifications Tab -->
      <div @click="navigate('/notifications')" class="notification-menu-item">
        <i class="fas fa-bell icon bell-theme"></i>
        <span v-if="!isCollapsed">Notifications</span>
        <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
        <audio ref="notifAudio" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" preload="auto"></audio>
      </div>
      
      <!-- Theme Menu -->
      <div @click="toggleThemeMenu" class="theme-menu-item">
        <i class="fas fa-palette icon"></i>
        <span v-if="!isCollapsed">Theme</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-down theme-arrow" :class="{ 'rotated': themeMenuOpen }"></i>
      </div>
      
      <!-- Theme Options -->
      <div v-if="!isCollapsed && themeMenuOpen" class="theme-submenu">
        <div class="theme-option" @click="setTheme('light')" :class="{ 'active': currentTheme === 'light' }">
          <div class="theme-preview light-theme"></div>
          <span>Light</span>
          <i v-if="currentTheme === 'light'" class="fas fa-check theme-check"></i>
        </div>
        <div class="theme-option" @click="setTheme('dark')" :class="{ 'active': currentTheme === 'dark' }">
          <div class="theme-preview dark-theme"></div>
          <span>Dark</span>
          <i v-if="currentTheme === 'dark'" class="fas fa-check theme-check"></i>
        </div>
        <div class="theme-option" @click="setTheme('blue')" :class="{ 'active': currentTheme === 'blue' }">
          <div class="theme-preview blue-theme"></div>
          <span>Blue</span>
          <i v-if="currentTheme === 'blue'" class="fas fa-check theme-check"></i>
        </div>
      </div>

      <!-- User Profile -->
      <div class="bottom-profile">
        <i class="fas fa-user icon"></i>
        <span v-if="!isCollapsed">{{ username }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import logo from '../../assets/grc_logo1.png'
import '@fortawesome/fontawesome-free/css/all.min.css'

export default {
  name: 'PolicySidebar',
  setup() {
    const router = useRouter()
    const isCollapsed = ref(false)
    const themeMenuOpen = ref(false)
    const currentTheme = ref('light')
    const unreadCount = ref(0)
    const username = ref('User')
    let prevUnreadCount = 0
    let pollInterval = null
    const notifAudio = ref(null)
    
    const openMenus = ref({
      policy: false,
      policyCreation: false,
      policiesList: false,
      performanceAnalysis: false,
      compliance: false,
      risk: false,
      riskRegister: false,
      riskInstances: false,
      riskAnalytics: false,
      auditor: false,
      incident: false,
      incidentManagement: false,
      incidentPerformance: false,
      dashboard: false,
      complianceDashboard: false,
      policyManagement: false,
      createPolicy: false,
      performance: false,
      auditFindings: false,
      compliances: false,
      compliancesView: false,
      complianceCreation: false,
      complianceList: false,
      compliancePerformance: false
    })

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value
    }

    const toggleSubmenu = (section) => {
      openMenus.value[section] = !openMenus.value[section]
    }

    const toggleThemeMenu = () => {
      themeMenuOpen.value = !themeMenuOpen.value
    }

    const setTheme = (theme) => {
      currentTheme.value = theme
      document.documentElement.setAttribute('data-theme', theme)
      localStorage.setItem('selected-theme', theme)
      themeMenuOpen.value = false
    }

    const handleDashboardClick = () => {
      toggleSubmenu('dashboard')
      if (!openMenus.value.dashboard) {
        router.push('/policy/dashboard')
      }
    }

    const navigate = (path) => {
      router.push(path)
    }

    // Poll unread notifications every 10 seconds
    const fetchUnreadCount = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/get-notifications/?user_id=default_user');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success') {
            const count = (data.notifications || []).filter(n => n.status && !n.status.isRead).length;
            if (count > prevUnreadCount && prevUnreadCount !== 0) {
              // Play sound only if new notification arrives (not on first load)
              if (notifAudio.value) notifAudio.value.play();
            }
            unreadCount.value = count;
            prevUnreadCount = count;
          }
        }
      } catch (e) {
        // Ignore errors
      }
    }

    // Get logged in username
    const fetchUsername = async () => {
      try {
        // Assuming you store the username in localStorage after login
        const storedUsername = localStorage.getItem('username')
        if (storedUsername) {
          username.value = storedUsername
        } else {
          // If not in localStorage, try to fetch from API
          const response = await fetch('http://localhost:8000/api/current-user/')
          if (response.ok) {
            const data = await response.json()
            if (data.username) {
              username.value = data.username
              localStorage.setItem('username', data.username)
            }
          }
        }
      } catch (e) {
        console.error('Error fetching username:', e)
      }
    }

    onMounted(() => {
      fetchUnreadCount();
      fetchUsername();
      pollInterval = setInterval(fetchUnreadCount, 10000);
      const savedTheme = localStorage.getItem('selected-theme') || 'light'
      setTheme(savedTheme)
    })
    onUnmounted(() => {
      if (pollInterval) clearInterval(pollInterval)
    })

    return {
      isCollapsed,
      openMenus,
      themeMenuOpen,
      currentTheme,
      logo,
      username,
      toggleCollapse,
      toggleSubmenu,
      toggleThemeMenu,
      setTheme,
      navigate,
      handleDashboardClick,
      unreadCount,
      notifAudio
    }
  }
}
</script>

<style scoped>
/* Import the existing CSS file */
@import './sidebar.css';

/* Notification tab style */
.notification-menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}
.notification-menu-item:hover {
  background: #f0f4ff;
}
.notification-menu-item .icon {
  margin-right: 12px;
  font-size: 1.2rem;
  color: #575757 !important;
}
.bell-theme {
  color:  #646464 !important;
}
.notification-badge {
  position: absolute;
  top: 2px;
  left: 28px;
  background:  #ff3e3e !important;
  color: #fff;
  border-radius: 50%;
  font-size: 0.8rem;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 1px 4px rgba(25, 118, 210, 0.18);
  z-index: 2;
}
</style> 