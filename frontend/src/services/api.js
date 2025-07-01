import axios from 'axios';
 
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 15000 // Add a 15-second timeout for all requests
});
 
// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
   
    // Add more detailed logging for network errors
    if (error.code === 'ERR_NETWORK') {
      console.error('Network error details:', {
        message: error.message,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          timeout: error.config?.timeout
        }
      });
    }
   
    return Promise.reject(error);
  }
);
// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
 
  // Log outgoing requests
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
    data: config.data,
    params: config.params
  });
 
  return config;
});
 
// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
 
  // Log outgoing requests
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
    data: config.data,
    params: config.params
  });
 
  return config;
});
 
 
export const incidentService = {
  // Incident main endpoints
  getIncidents: (params) => api.get('api/incidents/', { params }),
  createIncident: (data) => api.post('api/incidents/create/', data),
  updateIncidentStatus: (incidentId, data) => api.put(`api/incidents/${incidentId}/status/`, data),
 
  // Incident analytics endpoints
  getIncidentMetrics: (params) => api.get('api/incidents/metrics/', { params }),
  getIncidentMTTD: (params) => api.get('api/incidents/metrics/mttd/', { params }),
  getIncidentMTTR: (params) => api.get('api/incidents/metrics/mttr/', { params }),
  getIncidentMTTC: (params) => api.get('api/incidents/metrics/mttc/', { params }),
  getIncidentMTTRV: (params) => api.get('api/incidents/metrics/mttrv/', { params }),
  getIncidentVolume: (params) => api.get('api/incidents/metrics/volume/', { params }),
  getIncidentsBySeverity: (params) => api.get('api/incidents/metrics/by-severity/', { params }),
  getIncidentRootCauses: (params) => api.get('api/incidents/metrics/root-causes/', { params }),
  getIncidentTypes: (params) => api.get('api/incidents/metrics/types/', { params }),
  getIncidentOrigins: (params) => api.get('api/incidents/metrics/origins/', { params }),
  getIncidentCost: (params) => api.get('api/incidents/metrics/cost/', { params }),
  getIncidentClosureRate: (params) => api.get('api/incidents/metrics/closure-rate/', { params }),
  getIncidentReopenedCount: (params) => api.get('api/incidents/metrics/reopened-count/', { params }),
  getIncidentCount: (params) => api.get('api/incidents/metrics/count/', { params }),
 
  // Incident analytics for dashboard
  getIncidentDashboard: (params) => api.get('api/incidents/dashboard/', { params }),
  getIncidentAnalytics: (data) => api.post('api/incidents/dashboard/analytics/', data),
 
  // Other incident-related endpoints
  getIncidentCountsByStatus: () => api.get('api/incidents/counts-by-status/'),
  getRecentIncidents: (limit = 3) => api.get('api/incidents/recent/', { params: { limit } })
};
 
export const auditService = {
  // Audit findings related endpoints
  getAuditFindings: (params) => api.get('api/audit-findings/', { params }),
  getAuditFindingsDetail: (complianceId) => api.get(`api/audit-findings/${complianceId}/details/`),
 
  // Get data from lastchecklistitemverified table
  getChecklistVerified: (params = {}) => {
    const url = new URL(`${api.defaults.baseURL}/api/lastchecklistitemverified/`);
   
    // Add complied parameters if present
    if (params.complied && Array.isArray(params.complied)) {
      params.complied.forEach(value => {
        url.searchParams.append('complied[]', value);
      });
    } else {
      // Default to showing only non-compliant (0) and partially compliant (1)
      url.searchParams.append('complied[]', '0');
      url.searchParams.append('complied[]', '1');
    }
   
    return api.get(url.toString());
  },
 
  // Get specific audit finding details
  getAuditDetail: (auditId) => api.get(`api/audits/${auditId}/`),
 
  // Get audit findings by compliance id
  getAuditFindingsByCompliance: (complianceId) => api.get(`api/audit-findings/compliance/${complianceId}/`),
  getUsers: () => api.get('api/users/'),
 
  getOntimeMitigationPercentage: () => api.get('api/compliance/kpi-dashboard/analytics/ontime-mitigation/'),
 
  // Get compliance audit information
  getComplianceAuditInfo: (complianceId) => api.get(`api/compliance/compliance/${complianceId}/audit-info/`),
};
 
export const complianceService = {
  // Framework endpoints
  getFrameworks: () => api.get('/api/compliance/frameworks/'),
  getComplianceFrameworks: () => api.get('/api/compliance/frameworks/'),
 
  // Policy endpoints
  getPolicies: (frameworkId) => api.get(`/api/compliance/frameworks/${frameworkId}/policies/list/`),
  getCompliancePolicies: (frameworkId) => api.get(`/api/compliance/frameworks/${frameworkId}/policies/list/`),
 
  // SubPolicy endpoints
  getSubPolicies: (policyId) => api.get(`/api/compliance/policies/${policyId}/subpolicies/`),
  getComplianceSubPolicies: (policyId) => api.get(`/api/compliance/policies/${policyId}/subpolicies/`),
 
  // View all compliances by type (framework, policy, subpolicy)
  getCompliancesByType: (type, id) => api.get(`/api/compliance/view/${type}/${id}/`),
 
  // CategoryBusinessUnit endpoints
  getCategoryBusinessUnits: (source) => api.get('/api/category-business-units/', { params: { source } }),
  getCategoryBusinessPolicies: (source) => api.get('/api/category-business-units/', { params: { source } }),
  addCategoryBusinessUnit: (data) => api.post('/api/category-business-units/add/', data),
 
  // Compliance endpoints
  createCompliance: (data) => {
    // Add default values for required fields
    const defaultData = {
      ApprovalDueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days from now
      Status: 'Under Review',
      ActiveInactive: 'Active',
      ComplianceVersion: '1.0',
      ...data
    };
   
    // Ensure all required fields are present and properly formatted
    const formattedData = {
      SubPolicy: defaultData.SubPolicy,
      ComplianceTitle: defaultData.ComplianceTitle || '',
      ComplianceItemDescription: defaultData.ComplianceItemDescription || '',
      ComplianceType: defaultData.ComplianceType || '',
      Scope: defaultData.Scope || '',
      Objective: defaultData.Objective || '',
      BusinessUnitsCovered: defaultData.BusinessUnitsCovered || '',
      IsRisk: Boolean(defaultData.IsRisk),
      PossibleDamage: defaultData.PossibleDamage || '',
      mitigation: defaultData.mitigation || '',
      PotentialRiskScenarios: defaultData.PotentialRiskScenarios || '',
      RiskType: defaultData.RiskType || '',
      RiskCategory: defaultData.RiskCategory || '',
      RiskBusinessImpact: defaultData.RiskBusinessImpact || '',
      Criticality: defaultData.Criticality || 'Medium',
      MandatoryOptional: defaultData.MandatoryOptional || 'Mandatory',
      ManualAutomatic: defaultData.ManualAutomatic || 'Manual',
      Impact: defaultData.Impact || 5.0,
      Probability: defaultData.Probability || 5.0,
      Status: defaultData.Status,
      ComplianceVersion: defaultData.ComplianceVersion,
      reviewer: defaultData.reviewer_id || defaultData.reviewer, // Support both field names
      CreatedByName: defaultData.CreatedByName || (defaultData.reviewer_id || defaultData.reviewer).toString(),
      Applicability: defaultData.Applicability || '',
      MaturityLevel: defaultData.MaturityLevel || 'Initial',
      ActiveInactive: defaultData.ActiveInactive,
      PermanentTemporary: defaultData.PermanentTemporary || 'Permanent',
      ApprovalDueDate: defaultData.ApprovalDueDate
    };
 
    // Debug log
    console.log('Sending compliance data:', formattedData);
   
    return api.post(`/api/compliance-create/`, formattedData).then(response => {
      console.log('Compliance create response:', response.data);
      return {
        data: {
          success: response.data.success,
          ComplianceId: response.data.compliance_id,
          Identifier: response.data.Identifier,
          version: response.data.version
        }
      };
    }).catch(error => {
      console.error('Compliance create error:', error.response?.data);
      throw error;
    });
  },
 
  // Add updateCompliance function
  updateCompliance: (complianceId, data) => {
    // Format the data similar to createCompliance
    const formattedData = {
      ComplianceTitle: data.ComplianceTitle || '',
      ComplianceItemDescription: data.ComplianceItemDescription || '',
      ComplianceType: data.ComplianceType || '',
      Scope: data.Scope || '',
      Objective: data.Objective || '',
      BusinessUnitsCovered: data.BusinessUnitsCovered || '',
      IsRisk: Boolean(data.IsRisk),
      PossibleDamage: data.PossibleDamage || '',
      mitigation: data.mitigationSteps ? data.mitigationSteps.reduce((obj, step, index) => {
        if (step.description.trim()) {
          obj[`step${index + 1}`] = step.description.trim();
        }
        return obj;
      }, {}) : {},
      PotentialRiskScenarios: data.PotentialRiskScenarios || '',
      RiskType: data.RiskType || '',
      RiskCategory: data.RiskCategory || '',
      RiskBusinessImpact: data.RiskBusinessImpact || '',
      Criticality: data.Criticality || 'Medium',
      MandatoryOptional: data.MandatoryOptional || 'Mandatory',
      ManualAutomatic: data.ManualAutomatic || 'Manual',
      Impact: data.Impact || '5.0',
      Probability: data.Probability || '5.0',
      Status: 'Under Review',
      ComplianceVersion: data.ComplianceVersion,
      reviewer: data.reviewer_id || data.reviewer,
      Applicability: data.Applicability || '',
      MaturityLevel: data.MaturityLevel || 'Initial',
      ActiveInactive: 'Active',
      PermanentTemporary: data.PermanentTemporary || 'Permanent',
      // Ensure versionType is properly capitalized (must be 'Major' or 'Minor')
      versionType: data.versionType === 'major' ? 'Major' : 'Minor',
      PreviousComplianceVersionId: data.PreviousComplianceVersionId
    };
 
    // Debug log
    console.log('Updating compliance data:', formattedData);
   
    return api.put(`/api/compliance_edit/${complianceId}/edit/`, formattedData)
      .then(response => {
        console.log('Compliance update response:', response.data);
        return response;
      })
      .catch(error => {
        console.error('Compliance update error:', error.response?.data);
        throw error;
      });
  },
 
  editCompliance: (complianceId, data) => api.put(`/api/compliance_edit/${complianceId}/edit/`, data),
  cloneCompliance: (complianceId, data) => {
    console.log('Cloning compliance with ID:', complianceId, 'Data:', data);
    
    // Ensure SubPolicy is set correctly (it might be called target_subpolicy_id in the UI)
    const cloneData = { ...data };
    if (cloneData.target_subpolicy_id && !cloneData.SubPolicy) {
      cloneData.SubPolicy = cloneData.target_subpolicy_id;
    }
    
    return api.post(`/api/clone-compliance/${complianceId}/clone/`, cloneData)
      .then(response => {
        console.log('Compliance clone response:', response.data);
        return response;
      })
      .catch(error => {
        console.error('Compliance clone error:', error.response?.data);
        throw error;
      });
  },
  getComplianceDashboard: (filters) => api.get('/api/compliance/user-dashboard/', { params: filters }),
  getComplianceAnalytics: (data) => api.post('/api/compliance/kpi-dashboard/analytics/', data),
  getCompliancesBySubPolicy: (subPolicyId) => api.get(`/api/subpolicies/${subPolicyId}/compliances/`),
  getComplianceById: (complianceId) => api.get(`/api/compliance/${complianceId}/`),
  toggleComplianceVersion: (complianceId) => api.post(`/api/compliance/${complianceId}/toggle-version/`),
  deactivateCompliance: (complianceId, data) => api.post(`/api/compliance/${complianceId}/deactivate/`, data),
  approveComplianceDeactivation: (approvalId, data) => api.post(`/api/compliance/deactivation/${approvalId}/approve/`, data),
  rejectComplianceDeactivation: (approvalId, data) => api.post(`/api/compliance/deactivation/${approvalId}/reject/`, data),
 
  // KPI endpoints
  getMaturityLevelKPI: () => api.get('api/compliance/kpi-dashboard/analytics/maturity-level/'),
  getNonComplianceCount: () => api.get('api/compliance/kpi-dashboard/analytics/non-compliance-count/'),
  getMitigatedRisksCount: () => api.get('api/compliance/kpi-dashboard/analytics/mitigated-risks-count/'),
  getAutomatedControlsCount: () => api.get('api/compliance/kpi-dashboard/analytics/automated-controls-count/'),
  getNonComplianceRepetitions: () => api.get('api/compliance/kpi-dashboard/analytics/non-compliance-repetitions/'),
  getComplianceKPI: () => api.get('api/compliance/kpi-dashboard/'),
  getComplianceStatusOverview: () => api.get('api/compliance/kpi-dashboard/analytics/status-overview/'),
  getReputationalImpact: () => api.get('api/compliance/kpi-dashboard/analytics/reputational-impact/'),
  getRemediationCost: () => api.get('api/compliance/kpi-dashboard/analytics/remediation-cost/'),
  getNonCompliantIncidents: (period) => api.get('api/compliance/kpi-dashboard/analytics/non-compliant-incidents/', { params: { period } }),
 
  // Compliance approval endpoints with more robust error handling
  getCompliancePolicyApprovals: (params) => api.get('api/compliance/policy-approvals-compliance/reviewer/', { params }),
  getComplianceRejectedApprovals: (reviewerId) => api.get(`api/compliance/policy-approvals-compliance/rejected/${reviewerId}/`),
  submitComplianceReview: (approvalId, data) => {
    console.log(`Submitting compliance review for approval ID ${approvalId}:`, data);
    // Use a more explicit timeout for this critical endpoint
    return api.put(`/api/compliance/compliance-approvals/${approvalId}/review/`, data, { timeout: 20000 });
  },
  resubmitComplianceApproval: (approvalId, data) => api.put(`/api/compliance/compliance-approvals/resubmit/${approvalId}/`, data),
 
  // User endpoints
  getUsers: () => api.get('/api/compliance-users/'),
 
  getOntimeMitigationPercentage: () => api.get('api/compliance/kpi-dashboard/analytics/ontime-mitigation/'),
};
 
export default api;
 