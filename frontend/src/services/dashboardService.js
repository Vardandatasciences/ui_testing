import axios from 'axios';

const API_BASE = 'http://localhost:8000/api'; // Replace with your backend URL

export default {
    async getDashboardSummary() {
        try {
            const summaryRes = await axios.get(`${API_BASE}/policy-dashboard/`);
            return {
                data: {
                    ...summaryRes.data,
                    policies: Array.isArray(summaryRes.data.policies) ? summaryRes.data.policies : []
                }
            };
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            return {
                data: {
                    total_policies: 0,
                    active_policies: 0,
                    inactive_policies: 0,
                    total_subpolicies: 0,
                    approval_rate: 0,
                    policies: []
                }
            };
        }
    },
    getPolicyAnalytics(xAxis, yAxis) {
        return axios.get(`${API_BASE}/policy-analytics/`, {
            params: {
                x_axis: xAxis,
                y_axis: yAxis
            }
        });
    },
    getPolicyStatusDistribution() {
      return axios.get(`${API_BASE}/policy-status-distribution/`);
    },
    getReviewerWorkload() {
      return axios.get(`${API_BASE}/reviewer-workload/`);
    },
    getRecentPolicyActivity() {
      return axios.get(`${API_BASE}/recent-policy-activity/`);
    },
    getAvgApprovalTime() {
      return axios.get(`${API_BASE}/avg-policy-approval-time/`);
    },
    getAllPolicies() {
        return axios.get(`${API_BASE}/policies/`);
    }
  };
  