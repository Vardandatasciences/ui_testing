import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import PolicyApprover from '../components/Policy/PolicyApprover.vue'
import AllPolicies from '../components/Policy/AllPolicies.vue'
// import AssignAudit from '../components/Auditor/AssignAudit.vue'
import ActivePolicies from '../components/Policy/ActivePolicies.vue'
import Framework from '../components/Policy/Framework.vue'
import Tailoring from '../components/Policy/Tailoring.vue'
import Versioning from '../components/Policy/Versioning.vue'
import TreePolicies from '../components/Policy/TreePolicies.vue'
// import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import FrameworkExplorer from '../components/Policy/FrameworkExplorer.vue'
import FrameworkPolicies from '../components/Policy/FrameworkPolicies.vue'
import KPIDashboard from '../components/Policy/KPIDashboard.vue'
import FrameworkApprover from '../components/Framework/FrameworkApprover.vue'
import StatusChangeRequests from '../components/Policy/StatusChangeRequests.vue'

import AssignAudit from '../components/Auditor/AssignAudit.vue'
import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
import Reviewer from '../components/Auditor/Reviewer.vue'
import TaskView from '../components/Auditor/TaskView.vue'
import ReviewTaskView from '../components/Auditor/ReviewTaskView.vue'
import ReviewConfirmation from '../components/Auditor/ReviewConfirmation.vue'
import AuditReport from '../components/Auditor/AuditReport.vue'
import PerformanceAnalysis from '../components/Auditor/PerformanceAnalysis.vue'
import KPIAnalysis from '../components/PerformanceAnalysis/KpiAnalysis.vue'
import PerformanceDashboard from '../components/Auditor/UserDashboard.vue'

// import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
// import Reviewer from '../components/Auditor/Reviewer.vue'
import CreateIncident from '../components/Incident/CreateIncident.vue'
import IncidentDashboard from '../components/Incident/IncidentDashboard.vue'
import IncidentManagement from '../components/Incident/Incident.vue'
import IncidentDetails from '@/components/Incident/IncidentDetails.vue'
import AuditFindings from '@/components/Incident/AuditFindings.vue'
import AuditFindingDetails from '@/components/Incident/AuditFindingDetails.vue'


// import UserTasks from '../components/Incident/UserTasks.vue'
import IncidentUserTasks from '../components/Incident/IncidentUserTasks.vue'
// import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
// import CrudCompliance from '../components/Compliance/CrudCompliance.vue'
// import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'

import Audits from '../components/Auditor/Audits.vue'

// import AllCompliance from '../components/Compliance/AllCompliance.vue'
// import ComplianceDashboard from '../components/Compliance/ComplianceDashboard.vue'
import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
// import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
// import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'
// import ComplianceVersionList from '../components/Compliance/ComplianceVersionList.vue'
 







import EditCompliance from '../components/Compliance/EditCompliance.vue'
import CopyCompliance from '../components/Compliance/CopyCompliance.vue'
import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'
import AllCompliance from '../components/Compliance/AllCompliance.vue'
import Compliances from '../components/Compliance/Compliances.vue'
import ComplianceView from '../components/Compliance/ComplianceView.vue'
import ComplianceAuditView from '../components/Compliance/ComplianceAuditView.vue'
import ComplianceDashboard from '../components/Compliance/ComplianceDashboard.vue'
import ComplianceTailoring from '../components/Compliance/ComplianceTailoring.vue'
import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import ComplianceKPI from '../components/Compliance/ComplianceKPI.vue'
import PopupDemo from '../components/Compliance/PopupDemo.vue'
import UploadFramework from '../components/Policy/UploadFramework.vue'




import CreateRisk from '../components/Risk/CreateRisk.vue'
import RiskRegisterList from '../components/Risk/RiskRegisterList.vue'
import RiskDashboard from '../components/Risk/RiskDashboard.vue'
import RiskInstances from '../components/Risk/RiskInstances.vue'
import CreateRiskInstance from '../components/Risk/CreateRiskInstance.vue'
import RiskWorkflow from '../components/Risk/RiskWorkflow.vue'
import TailoringRisk from '../components/Risk/TailoringRisk.vue'
import RiskKPI from '../components/Risk/RiskKPI.vue'
import RiskScoring from '../components/Risk/RiskScoring.vue'
import ScoringDetails from '../components/Risk/ScoringDetails.vue'
import RiskResolution from '../components/Risk/RiskResolution.vue'
import ViewRisk from '../components/Risk/ViewRisk.vue'
import ViewInstance from '../components/Risk/ViewInstance.vue'

import LoginView from '../components/Login/LoginView.vue'
import HomeView from '../components/Login/HomeView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: () => {
      const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
      return isAuthenticated ? '/home' : '/login'
    }
  },
  {
    path: '/policy/dashboard',
    name: 'PolicyDashboard',
    component: PolicyDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/policy/performance',
    name: 'PerformancePage',
    component: PerformancePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/policy/approver',
    name: 'PolicyApprover',
    component: PolicyApprover,
    meta: { requiresAuth: true }
  },
  {
    path: '/policies-list/all',
    name: 'AllPolicies',
    component: AllPolicies,
    meta: { requiresAuth: true }
  },
  {
    path: '/policies-list/active',
    name: 'ActivePolicies',
    component: ActivePolicies,
    meta: { requiresAuth: true }
  },
  {
    path: '/create-policy/create',
    name: 'CreatePolicy',
    component: CreatePolicy,
    meta: { requiresAuth: true }
  },
  {
    path: '/create-policy/framework',
    name: 'Framework',
    component: Framework,
    meta: { requiresAuth: true }
  },
  {
    path: '/create-policy/tailoring',
    name: 'Tailoring',
    component: Tailoring,
    meta: { requiresAuth: true }
  },
  {
    path: '/create-policy/versioning',
    name: 'Versioning',
    component: Versioning,
    meta: { requiresAuth: true }
  },
  {
    path: '/tree-policies',
    name: 'TreePolicies',
    component: TreePolicies,
    meta: { requiresAuth: true }
  },
  {
    path: '/compliance/create',
    name: 'CreateCompliance',
    component: CreateCompliance
  },
  {
    path: '/incident/user-tasks',
    name: 'IncidentUserTasks',
    component: IncidentUserTasks
  },
  // {
  //   path: '/compliance/versioning',
  //   name: 'ComplianceVersioning',
  //   component: ComplianceVersioning
  // },
  {
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },
  // {
  //   path: '/compliance/version-list',
  //   name: 'ComplianceVersionList',
  //   component: ComplianceVersionList
  // },
  // {
  //   path: '/compliance/list',
  //   name: 'AllCompliance',
  //   component: AllCompliance
  // },
 
  {
    path: '/auditor/dashboard',
    name: 'AuditorDashboard',
    component: () => import('../components/Auditor/AuditorDashboard.vue')
  },
  {
    path: '/auditor/assign',
    name: 'AssignAudit',
    component: AssignAudit
  },
  {
    path: '/auditor/reviews',
    name: 'ReviewAudits',
    component: Reviewer
  },
  {
    path: '/auditor/reviewer',
    name: 'AuditorReviewer',
    component: Reviewer
  },
  {
    path: '/audit/:auditId/tasks',
    name: 'TaskView',
    component: TaskView,
    props: true
  },
  {
    path: '/reviewer/task/:auditId',
    name: 'ReviewTaskView',
    component: ReviewTaskView,
    props: true
  },
  {
    path: '/auditor/audits',
    name: 'Audits',
    component: Audits
  },
  {
    path: '/auditor/kpi',
    name: 'AuditorKPI',
    component: () => import('../components/Auditor/AuditorDashboard.vue')
  },
  {
    path: '/incident/create',
    name: 'CreateIncident',
    component: CreateIncident
  },
  {
    path: '/incident/incident',
    name: 'Incident',
    component: IncidentManagement
  },
  {
    path: '/incident/dashboard',
    name: 'IncidentDashboard',
    component: IncidentDashboard
  },
  {
    path: '/incident/:id',
    name: 'IncidentDetails',
    component: IncidentDetails,
    props: true
  },
  {
    path: '/incident/audit-findings',
    name: 'AuditFindings',
    component: AuditFindings
  },
  {
    path: '/incident/audit-finding-details/:id',
    name: 'AuditFindingDetails',
    component: AuditFindingDetails,
    props: true
  },
  {
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },
  {
    path: '/incident/incident',
    name: 'IncidentManagement',
    component: () => import('../components/Incident/Incident.vue')
  },
  {
    path: '/incident/performance/dashboard',
    name: 'IncidentPerformanceDashboard',
    component: () => import('../components/Incident/IncidentPerformanceDashboard.vue')


  },{
    path: '/risk/create',
    name: 'CreateRisk',
    component: CreateRisk
  },
  {
    path: '/risk/riskregister',
    name: 'RiskRegister',
    redirect: '/risk/riskregister-list'
  },
  {
    path: '/risk/riskregister-list',
    name: 'RiskRegisterList',
    component: RiskRegisterList
  },
  {
    path: '/risk/create-risk',
    name: 'CreateRiskForm',
    component: CreateRisk
  },
  {
    path: '/risk/riskdashboard',
    name: 'RiskDashboard',
    component: RiskDashboard
  },
  {
    path: '/risk/riskinstances',
    name: 'RiskInstances',
    redirect: '/risk/riskinstances-list'
  },
  {
    path: '/risk/riskinstances-list',
    name: 'RiskInstancesList',
    component: RiskInstances
  },
  {
    path: '/risk/create-instance',
    name: 'CreateRiskInstance',
    component: CreateRiskInstance
  },
  {
    path: '/risk/resolution',
    name: 'RiskResolution',
    component: RiskResolution
  },
  {
    path: '/risk/workflow',
    name: 'RiskWorkflow',
    component: RiskWorkflow
  },
  {
    path: '/risk/scoring',
    name: 'RiskScoring',
    component: RiskScoring
  },
  {
    path: '/risk/scoring-details/:riskId',
    name: 'ScoringDetails',
    component: ScoringDetails,
    props: true
  },
  {
    path: '/risk/tailoring',
    name: 'RiskTailoring',
    component: TailoringRisk
  },
  {
    path: '/risk/riskkpi',
    name: 'RiskKPI',
    component: RiskKPI
  },
  {
    path: '/view-risk/:id',
    name: 'ViewRisk',
    component: ViewRisk
  },
  {
    path: '/view-instance/:id',
    name: 'ViewInstance',
    component: ViewInstance
  },



  {
    path: '/framework-explorer/policies/:frameworkId',
    name: 'FrameworkPolicies',
    component: FrameworkPolicies,
    props: true
  },
  {
    path: '/policy/approval',
    name: 'PolicyApproval',
    component: PolicyApprover
  },
  {
    path: '/framework-approval',
    name: 'FrameworkApprover',
    component: FrameworkApprover
  },
  {
    path: '/framework-explorer',
    name: 'FrameworkExplorer',
    component: FrameworkExplorer
  },
  {
    path: '/policy/performance/dashboard',
    name: 'PolicyPerformanceDashboard',
    component: PolicyDashboard
  },
  {
    path: '/policy/performance/kpis',
    name: 'KPIDashboard',
    component: KPIDashboard
  },
  {
    path: '/framework-status-changes',
    name: 'StatusChangeRequests',
    component: StatusChangeRequests
  },
  
  {
    path: '/reviewer/confirmation/:auditId',
    name: 'ReviewConfirmation',
    component: ReviewConfirmation,
    props: true
  },
  {
    path: '/auditor/dashboard',
    name: 'AuditorDashboard',
    component: AuditorDashboard
  },
  {
    path: '/auditor/reports',
    name: 'AuditReports',
    component: AuditReport
  },
  {
    path: '/create-policy/upload-framework',
    name: 'UploadFramework',
    component: UploadFramework
  },
  {
    path: '/auditor/performance',
    component: PerformanceAnalysis,
    children: [
      {
        path: '',
        redirect: '/auditor/performance/dashboard'
      },
      {
        path: 'userdashboard',
        name: 'PerformanceDashboard',
        component: PerformanceDashboard
      },
      {
        path: 'kpi',
        name: 'KPIAnalysis',
        component: KPIAnalysis
      }
    ]
  },

  {
    path: '/compliance/create',
    name: 'CreateCompliance',
    component: CreateCompliance
  },
  {
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },
  {
    path: '/compliance/list',
    name: 'AllCompliance',
    component: AllCompliance,
    alias: '/control-management'
  },
  {
    path: '/compliance/audit-status',
    name: 'Compliances',
    component: Compliances
  },
  {
    path: '/compliance/view/:type/:id/:name',
    name: 'ComplianceView',
    component: ComplianceView,
    props: true
  },
  {
    path: '/compliance/audit/:type/:id/:name',
    name: 'ComplianceAuditView',
    component: ComplianceAuditView,
    props: true
  },{
    path: '/compliance/user-dashboard',
    name: 'ComplianceDashboard',
    component: ComplianceDashboard
  },
  {
    path: '/compliance/kpi-dashboard',  
    name: 'ComplianceKPI',
    component: ComplianceKPI
  },
  {
    path: '/compliance/tailoring',
    name: 'ComplianceTailoring',
    component: ComplianceTailoring
  },
  {
    path: '/compliance/versioning',
    name: 'ComplianceVersioning',
    component: ComplianceVersioning
  },
  {
    path: '/compliance/popup-demo',
    name: 'PopupDemo',
    component: PopupDemo
  },
  {
    path: '/compliance/edit/:id',
    name: 'EditCompliance',
    component: EditCompliance
  },
  {
    path: '/compliance/copy/:id',
    name: 'CopyCompliance',
    component: CopyCompliance
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if route requires auth and user is not authenticated
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    // Redirect to home if user is already authenticated and trying to access login
    next('/home')
  } else {
    next()
  }
})

export default router 