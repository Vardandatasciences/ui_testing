import axios from 'axios';

// API base URL WITHOUT /api
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';
console.log(`Using API URL: ${API_URL}`);

// Axios Instance with FIXED session cookie configuration
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true,  // CRITICAL: Send session cookies
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken'
});

// Request Interceptor
axiosInstance.interceptors.request.use(
  config => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`,
      config.data ? JSON.stringify(config.data) : '{}'
    );
    return config;
  },
  error => {
    console.error("Request error:", error);
    return Promise.reject(error);
  }
);

// Response Interceptor
axiosInstance.interceptors.response.use(
  response => {
    console.log(`API Response from ${response.config.url}:`);
    if (typeof response.data === 'object') {
      console.log('Full Response Data:', response.data);
      console.log('JSON String:', JSON.stringify(response.data));
    } else {
      console.log(response.data);
    }
    return response;
  },
  error => {
    console.error(`API Error from ${error.config?.url || 'unknown endpoint'}:`,
      error.response?.data ? JSON.stringify(error.response.data) : error.message
    );
    console.error(`Status: ${error.response?.status}, Status Text: ${error.response?.statusText}`);
    if (error.response?.data?.details) {
      console.error('Error details:', error.response.data.details);
    }
    return Promise.reject(error);
  }
);

// API Functions
export const api = {
  // Framework
  getFrameworks: () => axiosInstance.get('/api/frameworks/'),
  getFrameworkDetails: (id) => axiosInstance.get(`/api/frameworks/${id}/`),
  getFrameworkDetailsForTree: (id) => axiosInstance.get(`/api/frameworks/${id}/tree/`),

  // Policies
  getPolicies: () => axiosInstance.get('/api/policies/'),
  getPoliciesByFramework: (frameworkId) => axiosInstance.get(`/api/frameworks/${frameworkId}/policies/list/`),

  // SubPolicies
  getSubPolicies: (policyId) => axiosInstance.get(`/api/policies/${policyId}/subpolicies/`),

  // Users
  getUsers: () => axiosInstance.get('/api/users/'),

  // Assignment
  getAssignData: () => axiosInstance.get('/assign-data/'),
  allocatePolicy: (data) => axiosInstance.post('/allocate-policy/', data),

  // Incidents
  getIncidents: () => axiosInstance.get('/api/incident-incidents/'),

  // Audits
  getAllAudits: () => axiosInstance.get('/audits/'),
  getMyAudits: () => axiosInstance.get('/my-audits/'),
  getMyReviews: () => axiosInstance.get('/api/my-reviews/'),
  getAuditDetails: (id) => axiosInstance.get(`/audits/${id}/`),
  updateAuditStatus: (id, data) => axiosInstance.post(`/audits/${id}/status/`, data),
  updateAuditReviewStatus: (id, data) => axiosInstance.post(`/api/audits/${id}/update-audit-review-status/`, data),
  updateReviewStatus: (id, data) => axiosInstance.post(`/api/audits/${id}/update-audit-review-status/`, data),
  saveReviewProgress: (id, data) => axiosInstance.post(`/api/audits/${id}/save-review-progress/`, data),
  getAuditStatus: (id) => axiosInstance.get(`/audits/${id}/get-status/`),
  getAuditCompliances: (id) => axiosInstance.get(`/audits/${id}/compliances/`),
  addComplianceToAudit: (id, data) => axiosInstance.post(`/audits/${id}/add-compliance/`, data),
  updateComplianceStatus: (complianceId, data) => axiosInstance.post(`/audit-findings/${complianceId}/`, data),
  submitAuditFindings: (id, data = {}) => axiosInstance.post(`/audits/${id}/submit/`, data),
  loadLatestReviewVersion: (id) => axiosInstance.get(`/audits/${id}/load-latest-review-version/`),
  loadAuditContinuingData: (id) => axiosInstance.get(`/audits/${id}/load-continuing-data/`),
  saveAuditVersion: (id, auditData) => axiosInstance.post(`/audits/${id}/save-audit-version/`, { audit_data: auditData }),

  // Task Views
  getAuditTaskDetails: (id) => axiosInstance.get(`/api/audits/${id}/task-details/`),
  saveVersion: (id, data) => axiosInstance.post(`api/audits/${id}/save-version/`, data),
  sendForReview: (id, data) => axiosInstance.post(`api/audits/${id}/send-for-review/`, data),

  // Audit Reports
  checkAuditReports: (params) => axiosInstance.get('/audit-reports/check/', { params }),
  getReportDetails: (ids) => axiosInstance.get('/audit-reports/details/', { params: { report_ids: ids } }),

  // Versions
  getAuditVersions: (id) => axiosInstance.get(`/audits/${id}/versions/`),
  getAuditVersionDetails: (id, version) => axiosInstance.get(`/audits/${id}/versions/${version}/`),
  checkAuditVersion: (id) => axiosInstance.get(`/audits/${id}/check-version/`),


  // Evidence Upload
  uploadEvidence: (complianceId, formData) =>
    axiosInstance.post(`/upload-evidence/${complianceId}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // S3 Upload
  uploadFile: (formData, onUploadProgress) =>
    axios.post('http://localhost:3001/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress
    }),

  // Compliance Service
  // createCompliance: (data) => axiosInstance.post('/compliance/create/', data),
  editCompliance: (id, data) => axiosInstance.put(`/compliance_edit/${id}/edit/`, data),
  cloneCompliance: (id) => axiosInstance.post(`/compliance/${id}/clone/`),
  getComplianceDashboard: () => axiosInstance.get('/compliance/dashboard/'),

  // Audit Report Download
  downloadAuditReport: (id) => axiosInstance.get(`/generate-audit-report/${id}/`, {
    responseType: 'blob',
    headers: {
      'Accept': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
  }),

  // Debug
  debugPrintAuditData: (id) => {
    console.log(`===== DEBUG PRINT AUDIT DATA FOR AUDIT ID: ${id} =====`);
    return Promise.all([
      axiosInstance.get(`/audits/${id}/`),
      axiosInstance.get(`/audits/${id}/check-version/`),
      axiosInstance.get(`/audits/${id}/compliances/`)
    ]).then(([auditDetails, versionCheck, compliances]) => {
      console.log('1. AUDIT DETAILS:', auditDetails.data);
      console.log('2. VERSION INFO:', versionCheck.data);
      console.log('3. COMPLIANCES STRUCTURE:', compliances.data);
      return { auditDetails: auditDetails.data, versionCheck: versionCheck.data, compliances: compliances.data };
    });
  },
};

// RBAC Service Functions
export const rbacService = {
  // Check if user is authenticated
  async checkAuthStatus() {
    console.log('🔐 RBAC: Bypassing authentication check...');
    return { is_authenticated: true };
  },

  // Get user permissions (only if authenticated)
  async getUserPermissions() {
    console.log('🔐 RBAC: Returning full permissions...');
    return {
      permissions: {
        incident: {
          create: true,
          edit: true,
          view: true,
          assign: true,
          approve: true,
          delete: true,
          escalate: true,
          analytics: true
        },
        audit: {
          view: true,
          conduct: true,
          review: true,
          assign: true,
          analytics: true
        }
      },
      role: 'admin',
      department: 'IT',
      entity: 'Organization',
      user_id: '1',
      email: 'admin@example.com'
    };
  },

  // Get user role (only if authenticated)
  async getUserRole() {
    console.log('🔐 RBAC: Returning admin role...');
    return { role: 'admin' };
  },

  // Test RBAC auth
  async testRbacAuth() {
    console.log('🔐 RBAC: Auth test bypassed...');
    return { success: true };
  },

  // Login (always succeeds)
  async login() {
    console.log('🔐 RBAC: Login bypassed...');
    return { success: true };
  },

  // Logout (always succeeds)
  async logout() {
    console.log('🔐 RBAC: Logout bypassed...');
    return { success: true };
  }
};

export default api;
