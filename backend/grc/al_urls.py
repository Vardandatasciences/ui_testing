from django.urls import path
from . import compliance_views
 
from .compliance_views import *
 
urlpatterns = [
    # Auth endpoints
    path('login/', compliance_views.login, name='login'),
    path('register/', compliance_views.register, name='register'),
    path('test-connection/', compliance_views.test_connection, name='test-connection'),
   
    # Framework and Policy endpoints
    path('frameworks/', compliance_views.get_frameworks, name='get-frameworks'),
    path('frameworks/<int:framework_id>/policies/list/', compliance_views.get_policies, name='get-policies'),
    path('policies/<int:policy_id>/subpolicies/', compliance_views.get_subpolicies, name='get-subpolicies'),
   
    # Compliance endpoints
    path('compliance/create/', compliance_views.create_compliance, name='create-compliance'),
    path('compliance/<int:compliance_id>/edit/', compliance_views.edit_compliance, name='edit-compliance'),
    path('compliance/<int:compliance_id>/clone/', compliance_views.clone_compliance, name='clone-compliance'),
    path('compliance/<int:compliance_id>/framework-info/', compliance_views.get_compliance_framework_info, name='get-compliance-framework-info'),
    path('compliance/<int:compliance_id>/', compliance_views.get_compliance_details, name='get-compliance-details'),
    path('compliance/user-dashboard/', compliance_views.get_compliance_dashboard, name='compliance-dashboard'),
    path('compliance/kpi-dashboard/analytics/', compliance_views.get_compliance_analytics, name='compliance-analytics'),
    path('subpolicies/<int:subpolicy_id>/compliances/', compliance_views.get_compliances_by_subpolicy, name='get-compliances-by-subpolicy'),
   
    # All Policies endpoints
    path('all-policies/frameworks/', compliance_views.all_policies_get_frameworks, name='all-policies-get-frameworks'),
    path('all-policies/policies/', compliance_views.all_policies_get_policies, name='all-policies-get-policies'),
    path('all-policies/subpolicies/', compliance_views.all_policies_get_subpolicies, name='all-policies-get-subpolicies'),
    path('all-policies/subpolicy/<int:subpolicy_id>/compliances/', compliance_views.all_policies_get_subpolicy_compliances, name='all-policies-get-subpolicy-compliances'),
    path('all-policies/compliance/<int:compliance_id>/versions/', compliance_views.all_policies_get_compliance_versions, name='all-policies-get-compliance-versions'),
   
    # Compliance approval endpoints
    path('compliance-approvals/<int:approval_id>/review/', compliance_views.submit_compliance_review, name='submit_compliance_review'),
    path('compliance-approvals/resubmit/<int:approval_id>/', compliance_views.resubmit_compliance_approval, name='resubmit_compliance_approval'),
    path('compliance/versioning/', compliance_views.get_compliance_versioning, name='get-compliance-versioning'),
    path('policy-compliance-approvals/reviewer/', compliance_views.get_policy_approvals_by_reviewer, name='get-policy-approvals-by-reviewer'),
    path('policy-approvals/rejected/<int:reviewer_id>/', compliance_views.get_rejected_approvals, name='get-rejected-approvals'),
   
    # User endpoints
    path('users/', compliance_views.get_all_users, name='get-all-users'),
 
    # Compliance export endpoints
    path('api/export/all-compliances/<str:export_format>/<str:item_type>/<int:item_id>/',
         compliance_views.export_compliances,
         name='export-all-compliances'),
   
    path('api/export/all-compliances/<str:export_format>/',
         compliance_views.export_compliances,
         name='export-all-compliances-legacy'),
   
    path('compliances/framework/<int:framework_id>/', compliance_views.get_framework_compliances, name='get-framework-compliances'),
    path('compliances/policy/<int:policy_id>/', compliance_views.get_policy_compliances, name='get-policy-compliances'),
    path('compliances/subpolicy/<int:subpolicy_id>/', compliance_views.get_subpolicy_compliances, name='get-subpolicy-compliances'),
 
    # API endpoints
    path('all-policies/frameworks/', compliance_views.all_policies_get_frameworks, name='all-policies-frameworks'),
    path('all-policies/frameworks/<int:framework_id>/versions/', compliance_views.all_policies_get_framework_versions, name='all-policies-framework-versions'),
    path('all-policies/framework-versions/<int:version_id>/policies/', compliance_views.all_policies_get_framework_version_policies, name='all-policies-framework-version-policies'),
    path('api/all-policies/policies/', compliance_views.all_policies_get_policies, name='all-policies-policies'),
    path('api/all-policies/policies/<int:policy_id>/versions/', compliance_views.all_policies_get_policy_versions, name='all-policies-policy-versions'),
    path('api/all-policies/subpolicies/', compliance_views.all_policies_get_subpolicies, name='all-policies-subpolicies'),
    path('api/all-policies/policy-versions/<int:version_id>/subpolicies/', compliance_views.all_policies_get_policy_version_subpolicies, name='all-policies-policy-version-subpolicies'),
    path('api/all-policies/subpolicies/<int:subpolicy_id>/', compliance_views.all_policies_get_subpolicy_details, name='all-policies-subpolicy-details'),
    path('api/all-policies/subpolicies/<int:subpolicy_id>/compliances/', compliance_views.all_policies_get_subpolicy_compliances, name='all-policies-subpolicy-compliances'),
    path('api/all-policies/compliances/<int:compliance_id>/versions/', compliance_views.all_policies_get_compliance_versions, name='all-policies-compliance-versions'),
       
    # Version control endpoints
    path('compliance/<int:compliance_id>/toggle-version/', compliance_views.toggle_compliance_version, name='toggle-compliance-version'),
    path('compliance/<int:compliance_id>/deactivate/', compliance_views.deactivate_compliance, name='deactivate-compliance'),
    path('compliance/deactivation/<int:approval_id>/approve/', compliance_views.approve_compliance_deactivation, name='approve-compliance-deactivation'),
    path('compliance/deactivation/<int:approval_id>/reject/', compliance_views.reject_compliance_deactivation, name='reject-compliance-deactivation'),
 
    # Performance Analysis endpoints
    path('compliance/kpi-dashboard/', compliance_views.get_compliance_kpi, name='get-compliance-kpi-dashboard'),
    path('compliance/user-dashboard/', compliance_views.get_compliance_dashboard, name='get-compliance-user-dashboard'),
    path('compliance/kpi-dashboard/analytics/', compliance_views.get_compliance_analytics, name='get-compliance-kpi-analytics'),
    path('compliance/kpi-dashboard/analytics/maturity-level/', compliance_views.get_maturity_level_kpi, name='get-maturity-level-kpi'),
    path('compliance/kpi-dashboard/analytics/non-compliance-count/', compliance_views.get_non_compliance_count, name='get-non-compliance-count'),
    path('compliance/kpi-dashboard/analytics/mitigated-risks-count/', compliance_views.get_mitigated_risks_count, name='get-mitigated-risks-count'),
    path('compliance/kpi-dashboard/analytics/automated-controls-count/', compliance_views.get_automated_controls_count, name='get-automated-controls-count'),
    path('compliance/kpi-dashboard/analytics/non-compliance-repetitions/', compliance_views.get_non_compliance_repetitions, name='get-non-compliance-repetitions'),
    path('compliance/kpi-dashboard/analytics/ontime-mitigation/', compliance_views.get_ontime_mitigation_percentage, name='get-ontime-mitigation-percentage'),
    path('compliance/kpi-dashboard/analytics/reputational-impact/', compliance_views.get_reputational_impact_assessment, name='get-reputational-impact'),
    path('compliance/kpi-dashboard/analytics/status-overview/', compliance_views.get_compliance_status_overview, name='get-compliance-status-overview'),
    path('compliance/kpi-dashboard/analytics/remediation-cost/', compliance_views.get_remediation_cost_kpi, name='get-remediation-cost-kpi'),
    path('compliance/kpi-dashboard/analytics/non-compliant-incidents/', compliance_views.get_non_compliant_incidents_by_time, name='get-non-compliant-incidents'),
 
    # Audit information for compliance
    path('api/compliance/<int:compliance_id>/audit-info/',
         compliance_views.get_compliance_audit_info,
         name='get-compliance-audit-info'),
 
    path('test-notification/', compliance_views.test_notification, name='test-notification'),
   
    # Category endpoints
    path('categories/<str:source>/', compliance_views.get_category_values, name='get-category-values'),
    path('categories/add/', compliance_views.add_category_value, name='add-category-value'),
    path('categories/initialize/', compliance_views.initialize_default_categories, name='initialize-categories'),


]