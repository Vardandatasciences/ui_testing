from django.urls import path, include
from django.http import HttpResponse
from . import incident_views
from .incident_views import get_incident_counts as get_counts
from rest_framework.routers import DefaultRouter
from .incident_views import create_workflow, create_incident_from_audit_finding
from .incident_views import FileUploadView
from . import compliance_views
from . import views



from . import audit_views
from . import report_views
from . import audit_report_views
from . import kpi_functions 
from . import audit_report_handlers
from . import UserDashboard
from .audit_views import (
    get_assign_data, load_review_data, load_latest_review_version,
    load_continuing_data, load_audit_continuing_data, save_audit_json_version,
    get_audit_compliances
)
from . import notification_service
from .assign_audit import get_frameworks, get_policies, get_subpolicies, get_users_audit, create_audit, add_compliance_to_audit, get_compliance_count
from .auditing import get_audit_task_details, save_audit_version, send_audit_for_review
from . import reviewing


from grc.rbac import views as rbac_views





from django.urls import path

from .routes.policy import (
    framework_list, framework_detail, policy_detail, policy_list,
    add_policy_to_framework, add_subpolicy_to_policy, 
    subpolicy_detail, 
    # create_framework_version,
    export_policies_to_excel,
    update_policy_approval,
    submit_policy_review,
    resubmit_policy_approval,
    list_users,
    get_framework_explorer_data,
    get_framework_policies,
    toggle_policy_status,
    get_framework_details,
    get_policy_details,
    all_policies_get_frameworks,
    all_policies_get_framework_versions,
    all_policies_get_framework_version_policies,
    all_policies_get_policies,
    all_policies_get_policy_versions,
    all_policies_get_subpolicies,
    all_policies_get_policy_version_subpolicies,
    all_policies_get_subpolicy_details,
    get_policy_dashboard_summary,
    get_policy_status_distribution,
    get_reviewer_workload,
    get_recent_policy_activity,
    get_avg_policy_approval_time,
    get_policy_analytics,
    get_policy_kpis,
    acknowledge_policy,
    get_policies_by_framework,
    get_subpolicies_by_policy,  
    get_latest_policy_approval,
    get_latest_policy_approval_by_role,
    get_latest_reviewer_version,
    submit_subpolicy_review,
    resubmit_subpolicy,
    get_policy_version,
    get_subpolicy_version,
    submit_policy_approval_review,
    get_policy_version_history,
    list_policy_approvals_for_reviewer,
    list_rejected_policy_approvals_for_user,
    create_tailored_framework,
    create_tailored_policy,
    get_policy_categories,
    save_policy_category,
    get_entities,
    get_policy_compliance_stats,
    request_policy_status_change,
    approve_policy_status_change,
    get_policy_status_change_requests,
    get_policy_status_change_requests_by_reviewer,
    test_policy_status_debug,
    get_policy_extraction_progress,
    get_policy_counts_by_status,
    get_policies_paginated_by_status,
)


from .routes.upload_framework import (
    upload_framework_file, 
    get_processing_status, 
    get_sections, 
    update_section, 
    create_checked_structure,
    get_extracted_policies,
    direct_process_checked_sections,
    save_updated_policies,
    save_policies,
    save_single_policy,
    get_saved_excel_files,
    save_policy_details,
    save_complete_policy_package,
    save_framework_to_database,
    load_default_data
)
from .routes.frameworks import (
    create_framework_approval,
    get_framework_approvals,
    update_framework_approval,
    submit_framework_review,
    get_latest_framework_approval,
    get_rejected_frameworks_for_user,
    approve_reject_subpolicy_in_framework,
    approve_reject_policy_in_framework,
    approve_entire_framework_final,
    request_framework_status_change,
    approve_framework_status_change,
    get_status_change_requests,
    update_existing_activeinactive_by_date,
    get_users_for_reviewer_selection,
    get_status_change_requests_by_reviewer,
    create_test_users
)
from .routes.framework_version import (
    create_framework_version as new_create_framework_version,
    get_framework_versions,
    get_all_framework_versions,
    activate_deactivate_framework_version,
    get_rejected_framework_versions,
    resubmit_rejected_framework,
    resubmit_framework_approval
)
from .routes.policy_version import (
    create_policy_version as policy_version_create,
    get_policy_versions as policy_version_get_versions,
    get_all_policy_versions as policy_version_get_all,
    get_rejected_policy_versions,
    # resubmit_policy_approval as policy_version_resubmit,
    activate_deactivate_policy,
    approve_policy_version
)
from django.urls import path, include
from . import risk_views
from rest_framework.routers import DefaultRouter
from .risk_views import RiskViewSet, IncidentViewSet, ComplianceViewSet, RiskInstanceViewSet
from .routes import previous_version
from .routes import compliance

# Authentication URLs - Clean implementation
auth_urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
]

# Add explicit URL paths for the ViewSets (api/ prefix is added by main urls.py)
risk_api_urlpatterns = [
    # Risk ViewSet URLs
    path('risks/', risk_views.RiskViewSet.as_view({'get': 'list', 'post': 'create'}), name='risk-list'),
    path('risks/<int:pk>/', risk_views.RiskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='risk-detail'),
    
    # RiskInstance ViewSet URLs
    path('risk-instances/', risk_views.RiskInstanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='risk-instance-list'),
    path('risk-instances/<int:pk>/', risk_views.RiskInstanceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='risk-instance-detail'),
    
    # Incident ViewSet URLs
    path('incidents/', risk_views.IncidentViewSet.as_view({'get': 'list', 'post': 'create'}), name='incident-list'),
    path('incidents/<int:pk>/', risk_views.IncidentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='incident-detail'),
    
    # Compliance ViewSet URLs
    path('compliances/', risk_views.ComplianceViewSet.as_view({'get': 'list', 'post': 'create'}), name='compliance-list'),
    path('compliances/<int:ComplianceId>/', risk_views.ComplianceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='compliance-detail'),
]

# User management URLs
user_urlpatterns = [
    path('users/', risk_views.get_users, name='get-users'),
    path('custom-users/', risk_views.get_custom_users, name='custom-users'),
    path('custom-users/<int:user_id>/', risk_views.get_custom_user, name='custom-user'),
    path('user-risks/<int:user_id>/', risk_views.get_user_risks, name='user-risks'),
    path('user-notifications/<int:user_id>/', risk_views.get_user_notifications, name='user-notifications'),
    path('generate-test-notification/<int:user_id>/', risk_views.generate_test_notification, name='generate-test-notification'),
]

# Risk management URLs
risk_urlpatterns = [
    path('risk/metrics', risk_views.risk_metrics, name='risk_metrics'),
    path('risk-workflow/', risk_views.risk_workflow, name='risk-workflow'),
    path('risk-assign/', risk_views.assign_risk_instance, name='risk-assign'),
    path('risk-update-status/', risk_views.update_risk_status, name='risk-update-status'),
    path('risk-mitigations/<int:risk_id>/', risk_views.get_risk_mitigations, name='risk-mitigations'),
    path('risk-update-mitigation/<int:risk_id>/', risk_views.update_risk_mitigation, name='risk-update-mitigation'),
    path('risk-form-details/<int:risk_id>/', risk_views.get_risk_form_details, name='risk-form-details'),
    # Add incident management URLs
    path('last-incident/', risk_views.last_incident, name='last-incident'),
    path('compliance-by-incident/<int:incident_id>/', risk_views.get_compliance_by_incident, name='compliance-by-incident'),
    path('risks-by-incident/<int:incident_id>/', risk_views.get_risks_by_incident, name='risks-by-incident'),
    path('risks-for-dropdown/', risk_views.get_all_risks_for_dropdown, name='risks-for-dropdown'),
    path('compliances-for-dropdown/', risk_views.get_all_compliances_for_dropdown, name='compliances-for-dropdown'),
    path('users-for-dropdown/', risk_views.get_users_for_dropdown, name='users-for-dropdown'),
    path('analyze-incident/', risk_views.analyze_incident, name='analyze-incident'),
]

# Risk reviewer URLs
risk_reviewer_urlpatterns = [
    path('assign-reviewer/', risk_views.assign_reviewer, name='assign-reviewer'),
    path('reviewer-tasks/<int:user_id>/', risk_views.get_reviewer_tasks, name='reviewer-tasks'),
    path('complete-review/', risk_views.complete_review, name='complete-review'),
    path('reviewer-comments/<int:risk_id>/', risk_views.get_reviewer_comments, name='reviewer-comments'),
    path('latest-review/<int:risk_id>/', risk_views.get_latest_review, name='latest-review'),
    path('get-assigned-reviewer/<int:risk_id>/', risk_views.get_assigned_reviewer, name='get-assigned-reviewer'),
]

# Previous version management URLs
previous_version_urlpatterns = [
    path('risk/<int:risk_id>/versions/', previous_version.get_all_versions, name='get-all-versions'),
    path('risk/<int:risk_id>/version/<str:version>/', previous_version.get_previous_version, name='get-previous-version'),
    path('risk/<int:risk_id>/compare/<str:version1>/<str:version2>/', previous_version.get_version_comparison, name='get-version-comparison'),
]

# Mitigation management URLs
mitigation_urlpatterns = [
    path('update-mitigation-status/', risk_views.update_mitigation_status, name='update-mitigation-status'),
]

# Logging URLs
log_urlpatterns = [
    path('logs/', risk_views.GRCLogList.as_view(), name='log-list'),
    path('logs/<int:pk>/', risk_views.GRCLogDetail.as_view(), name='log-detail'),
]

# Risk KPI URLs
risk_kpi_urlpatterns = [
    path('risk/kpi-data/', risk_views.risk_kpi_data, name='risk_kpi_data'),
    path('risk/active-risks-kpi/', risk_views.active_risks_kpi, name='active_risks_kpi'),
    path('risk/exposure-trend/', risk_views.risk_exposure_trend, name='risk_exposure_trend'),
    path('risk/reduction-trend/', risk_views.risk_reduction_trend, name='risk_reduction_trend'),
    path('risk/high-criticality/', risk_views.high_criticality_risks, name='high_criticality_risks'),
    path('risk/mitigation-completion-rate/', risk_views.mitigation_completion_rate, name='mitigation_completion_rate'),
    path('risk/avg-remediation-time/', risk_views.avg_remediation_time, name='avg_remediation_time'),
    path('risk/recurrence-rate/', risk_views.recurrence_rate, name='recurrence_rate'),
    path('risk/avg-incident-response-time/', risk_views.avg_incident_response_time, name='avg_incident_response_time'),
    path('risk/mitigation-cost/', risk_views.mitigation_cost, name='mitigation_cost'),
    path('risk/identification-rate/', risk_views.risk_identification_rate, name='risk_identification_rate'),
    path('risk/due-mitigation/', risk_views.due_mitigation, name='due_mitigation'),
    path('risk/classification-accuracy/', risk_views.classification_accuracy, name='classification_accuracy'),
    path('risk/improvement-initiatives/', risk_views.improvement_initiatives, name='improvement_initiatives'),
    path('risk/impact/', risk_views.risk_impact, name='risk_impact'),
    path('risk/severity/', risk_views.risk_severity, name='risk_severity'),
    path('risk/exposure-score/', risk_views.risk_exposure_score, name='risk_exposure_score'),
    path('risk/resilience/', risk_views.risk_resilience, name='risk_resilience'),
    path('risk/assessment-frequency/', risk_views.risk_assessment_frequency, name='risk_assessment_frequency'),
    path('risk/assessment-consensus/', risk_views.risk_assessment_consensus, name='risk_assessment_consensus'),
    path('risk/approval-rate-cycle/', risk_views.risk_approval_rate_cycle, name='risk_approval_rate_cycle'),
    path('risk/register-update-frequency/', risk_views.risk_register_update_frequency, name='risk_register_update_frequency'),
    path('risk/recurrence-probability/', risk_views.risk_recurrence_probability, name='risk_recurrence_probability'),
    path('risk/tolerance-thresholds/', risk_views.risk_tolerance_thresholds, name='risk_tolerance_thresholds'),
    path('risk/appetite/', risk_views.risk_appetite, name='risk_appetite'),
]

# Compliance URLs
compliance_urlpatterns = [
    path('compliance/frameworks/', compliance.get_frameworks, name='get-frameworks'),
    path('compliance/frameworks/<int:framework_id>/policies/', compliance.get_policies, name='get-policies'),
    path('compliance/policies/<int:policy_id>/subpolicies/', compliance.get_subpolicies, name='get-subpolicies'),
    path('compliance/view/<str:type>/<int:id>/', compliance.get_compliances_by_type, name='get-compliances-by-type'),
]

# Combine all URL patterns
urlpatterns = [
    *auth_urlpatterns,
    *risk_api_urlpatterns,
    *user_urlpatterns,
    *risk_urlpatterns,
    *risk_reviewer_urlpatterns,
    *previous_version_urlpatterns,
    *mitigation_urlpatterns,
    *log_urlpatterns,
    *risk_kpi_urlpatterns,
    *compliance_urlpatterns,



      # RBAC endpoints - All under /api/ prefix for consistency
    # Note: These are moved to the bottom with /api/ prefix
    
    # Authentication endpoints - Available both with and without /api/ prefix
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('api/login/', views.login_user, name='api-login'),
    path('api/logout/', views.logout_user, name='api-logout'),
    path('api/register/', views.register_user, name='api-register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    path('api/test-connection/', views.test_connection, name='api-test-connection'),
    
    # RBAC endpoints - Moved to beginning to ensure they load
    path('api/user-permissions/', rbac_views.get_user_permissions, name='api-user-permissions'),
    path('api/user-role/', rbac_views.get_user_role, name='api-user-role'),
    path('api/debug-permissions/', rbac_views.debug_user_permissions, name='api-debug-permissions'),
    path('api/debug-rbac-data/', rbac_views.debug_rbac_data, name='api-debug-rbac-data'),
    path('api/debug-auth-status/', rbac_views.debug_auth_status, name='api-debug-auth-status'),
    path('api/debug-user-permissions/', incident_views.debug_user_permissions_endpoint, name='api-debug-user-permissions'),
    path('api/test-user-permissions/', incident_views.test_user_permissions_comprehensive, name='api-test-user-permissions'),
    
    # RBAC test endpoints
    path('api/test-policy-view/', rbac_views.test_policy_view_permission, name='api-test-policy-view'),
    path('api/test-policy-create/', rbac_views.test_policy_create_permission, name='api-test-policy-create'),
    path('api/test-policy-approve/', rbac_views.test_policy_approve_permission, name='api-test-policy-approve'),
    path('api/test-any-permission/', rbac_views.test_any_permission, name='api-test-any-permission'),
    path('api/test-all-permissions/', rbac_views.test_all_permissions, name='api-test-all-permissions'),
    path('api/test-endpoint-permission/', rbac_views.test_endpoint_permission, name='api-test-endpoint-permission'),
    
    # Dashboard endpoints (moved to top for priority)
    path('incidents/dashboard/', incident_views.incident_dashboard, name='incident-dashboard'),
    path('incidents/dashboard/analytics/', incident_views.incident_analytics, name='incident-analytics'),
    
    # API endpoints for dashboard KPIs and export (referenced in tests)
    path('api/dashboard-kpis/', incident_views.incident_dashboard, name='api-dashboard-kpis'),
    path('api/incident-export/', incident_views.export_incidents, name='api-incident-export'),
    path('api/incident-incidents/', incident_views.list_incidents, name='api-incident-incidents'),
    path('api/incidents-users/', incident_views.list_users, name='api-incidents-users'),
    path('api/incidents/create/', incident_views.create_incident, name='api-incidents-create'),
    path('api/incidents/export/', incident_views.export_incidents, name='api-incidents-export'),
    path('api/incidents/<int:incident_id>/', incident_views.incident_by_id, name='api-incident-by-id'),
    path('api/incidents/<int:incident_id>/update/', incident_views.update_incident_by_id, name='api-update-incident-by-id'),
    path('incidents/recent/', incident_views.get_recent_incidents, name='recent-incidents'),
    
    # Other incident endpoints
    # path('incidents/', incident_views.list_incidents, name='list-incidents'),
    path('incident-incidents/', incident_views.list_incidents, name='api-list-incidents'),
    path('incidents/create/', incident_views.create_incident, name='api-create-incident'),
    path('incidents/create', incident_views.create_incident, name='api-create-incident-no-slash'),
    path('incident/create/', incident_views.create_incident, name='create-incident-singular'),
    path('incident/schedule-manual/', incident_views.schedule_manual_incident, name='schedule_manual_incident'),
    path('incident/reject/', incident_views.reject_incident, name='reject_incident'),
    path('incidents/create/', incident_views.create_incident, name='create-incident'),
    path('incidents/export/', incident_views.export_incidents, name='export-incidents'),  # Use our new view
    
    # Audit findings endpoints
    path('audit-findings/', incident_views.get_audit_findings, name='get-audit-findings'),
    path('lastchecklistitemverified/', incident_views.audit_findings_list, name='audit-findings-list'),
    path('audit-findings/compliance/<int:compliance_id>/', incident_views.audit_finding_detail, name='audit-finding-detail'),
    path('audit-findings/incident/<int:incident_id>/', incident_views.audit_finding_incident_detail, name='audit-finding-incident-detail'),
    path('audit-findings/export/', incident_views.export_audit_findings, name='export-audit-findings'),
    
    path('incident-users/', incident_views.list_users, name='list-users'),
    path('incidents-users/', incident_views.list_users, name='incidents-users'),  # Added for frontend compatibility
    # path('api/users/', incident_views.list_users, name='api-get-users'),
    path('workflow/create/', incident_views.create_workflow, name='workflow-create'),
    path('workflow/assigned/', incident_views.list_assigned_findings, name='list-assigned-findings'),
    path('dashboard/incidents/', incident_views.combined_incidents_and_audit_findings, name='dashboard-incidents'),
    path('incident/from-audit-finding/', incident_views.create_incident_from_audit_finding, name='incident_from_audit_finding'),
    path('incident/schedule-manual/', incident_views.schedule_manual_incident, name='schedule_manual_incident'),
    path('incident/reject/', incident_views.reject_incident, name='reject_incident'),
    path('incident/mttd/', incident_views.incident_mttd, name='incident-mttd'),
    path('incident/mttr/', incident_views.incident_mttr, name='incident_mttr'),
    path('incident/mttc/', incident_views.incident_mttc, name='incident-mttc'),
    path('incident/mttrv/', incident_views.incident_mttrv, name='incident-mttrv'),
    path('incident/first-response-time/', incident_views.first_response_time, name='first-response-time'),
    path('incident/incident-volume/', incident_views.incident_volume, name='incident-volume'),
    path('incident/escalation-rate/', incident_views.escalation_rate, name='escalation-rate'),
    path('incident/repeat-rate/', incident_views.repeat_rate, name='repeat-rate'),
    path('incident/metrics/', incident_views.incident_metrics, name='incident-metrics'),
    path('incidents/counts/', incident_views.get_incident_counts, name='incident-counts'),
    path('incident/count/', incident_views.incident_count, name='incident-count'),
    path('incident/by-severity/', incident_views.incidents_by_severity, name='incidents-by-severity'),
    path('incident/root-causes/', incident_views.incident_root_causes, name='incident-root-causes'),
    path('incident/origins/', incident_views.incident_origins, name='incident-origins'),
    path('incident/types/', incident_views.incident_types, name='incident-types'),
    path('incident/incident-cost/', incident_views.incident_cost, name='incident-cost'),
    path('incident/cost/', incident_views.incident_cost, name='incident-cost-alt'),
    path('incident/reopened-count/', incident_views.incident_reopened_count, name='incident-reopened-count'),
    path('incident/false-positive-rate/', incident_views.false_positive_rate, name='false-positive-rate'),
    path('incident/detection-accuracy/', incident_views.detection_accuracy, name='detection-accuracy'),
    path('incident/incident-closure-rate/', incident_views.incident_closure_rate, name='incident-closure-rate'),
#
    path('incidents/<int:incident_id>/status/', incident_views.update_incident_status, name='update-incident-status'),
    path('incidents/<int:incident_id>/assign/', incident_views.assign_incident, name='assign-incident'),
    # API versions of the above endpoints for frontend compatibility
    path('api/incidents/<int:incident_id>/status/', incident_views.update_incident_status, name='api-update-incident-status'),
    path('api/incidents/<int:incident_id>/assign/', incident_views.assign_incident, name='api-assign-incident'),
    path('incident-compliances/', incident_views.get_compliances, name='get-compliances'),
    path('api/custom-users/', incident_views.list_users, name='custom-users'),
    
    # Incident User Tasks endpoints
    path('user-incidents/<int:user_id>/', incident_views.user_incidents, name='user-incidents'),
    path('incident-reviewer-tasks/<int:user_id>/', incident_views.incident_reviewer_tasks, name='incident-reviewer-tasks'),
    path('incident-mitigations/<int:incident_id>/', incident_views.incident_mitigations, name='incident-mitigations'),
    path('assign-incident-reviewer/', incident_views.assign_incident_reviewer, name='assign-incident-reviewer'),
    path('incident-review-data/<int:incident_id>/', incident_views.incident_review_data, name='incident-review-data'),
    path('complete-incident-review/', incident_views.complete_incident_review, name='complete-incident-review'),
    path('submit-incident-assessment/', incident_views.submit_incident_assessment, name='submit-incident-assessment'),
    path('incident-approval-data/<int:incident_id>/', incident_views.incident_approval_data, name='incident-approval-data'),
    
    # Audit Finding User Tasks endpoints
    path('user-audit-findings/<int:user_id>/', incident_views.user_audit_findings, name='user-audit-findings'),
    path('audit-finding-reviewer-tasks/<int:user_id>/', incident_views.audit_finding_reviewer_tasks, name='audit-finding-reviewer-tasks'),
    path('audit-finding-mitigations/<int:incident_id>/', incident_views.audit_finding_mitigations, name='audit-finding-mitigations'),
    path('assign-audit-finding-reviewer/', incident_views.assign_audit_finding_reviewer, name='assign-audit-finding-reviewer'),
    path('audit-finding-review-data/<int:incident_id>/', incident_views.audit_finding_review_data, name='audit-finding-review-data'),
    path('complete-audit-finding-review/', incident_views.complete_audit_finding_review, name='complete-audit-finding-review'),
    path('submit-audit-finding-assessment/', incident_views.submit_audit_finding_assessment, name='submit-audit-finding-assessment'),
    
    # Test endpoint for notifications
    path('api/test-notification/', incident_views.test_notification, name='test-notification'),
    path('api/test-logging/', incident_views.test_logging, name='test-logging'),
    path('upload-incident-file/', FileUploadView.as_view(), name='upload-file'),
    path('upload-file/', FileUploadView.as_view(), name='api-upload-file'),
    
    # Category and Business Unit endpoints
    path('categories/', incident_views.get_categories, name='get-categories'),
    path('business-units/', incident_views.get_business_units, name='get-business-units'),
    path('categories/add/', incident_views.add_category, name='add-category'),
    path('business-units/add/', incident_views.add_business_unit, name='add-business-unit'),
    path('seed-sample-data/', incident_views.seed_sample_data, name='seed-sample-data'),
    path('debug-category-data/', incident_views.debug_category_data, name='debug-category-data'),


    path('frameworks/', framework_list, name='framework-list'),
    path('frameworks/<int:pk>/', framework_detail, name='framework-detail'),
    path('frameworks/<int:framework_id>/create-version/', new_create_framework_version, name='create-framework-version'),
    # path('frameworks/<int:pk>/create-version/', create_framework_version, name='legacy-create-framework-version'),
    path('frameworks/<int:framework_id>/export/', export_policies_to_excel, name='export-framework-policies'),
    path('frameworks/<int:framework_id>/versions/', get_framework_versions, name='get-framework-versions'),
    path('framework-versions/', get_all_framework_versions, name='get-all-framework-versions'),
    path('frameworks/<int:framework_id>/toggle-active/', activate_deactivate_framework_version, name='activate-deactivate-framework-version'),
    path('framework-versions/rejected/', get_rejected_framework_versions, name='get-rejected-framework-versions'),
    path('framework-versions/rejected/<int:user_id>/', get_rejected_framework_versions, name='get-rejected-framework-versions-by-user'),
    path('frameworks/<int:framework_id>/resubmit-version/', resubmit_rejected_framework, name='resubmit-rejected-framework'),
    path('frameworks/<int:framework_id>/resubmit-approval/', resubmit_framework_approval, name='resubmit-framework-approval'),
    path('policies/', policy_list, name='policy-list'),
    path('policies/<int:pk>/', policy_detail, name='policy-detail'),
    path('policies/<int:policy_id>/create-version/', policy_version_create, name='create-policy-version'),
    path('policies/<int:policy_id>/versions/', policy_version_get_versions, name='get-policy-versions'),
    path('policy-versions/', policy_version_get_all, name='get-all-policy-versions'),
    path('policies/<int:policy_id>/toggle-active/', activate_deactivate_policy, name='activate-deactivate-policy'),
    path('policies/<int:policy_id>/approve-version/', approve_policy_version, name='approve-policy-version'),
    path('policy-versions/rejected/', get_rejected_policy_versions, name='get-rejected-policy-versions'),
    path('policy-versions/rejected/<int:user_id>/', get_rejected_policy_versions, name='get-rejected-policy-versions-by-user'),
    path('policies/<int:policy_id>/resubmit-approval/', resubmit_policy_approval, name='resubmit-policy-approval'),
    path('policies/<int:policy_id>/resubmit-approval/', resubmit_policy_approval, name='api-resubmit-policy-approval'),
    path('policy-approvals/<int:approval_id>/reject/', submit_policy_review, name='reject-policy-approval'),
    path('subpolicies/<int:pk>/', subpolicy_detail, name='subpolicy-detail'),
    path('frameworks/<int:framework_id>/policies/', add_policy_to_framework, name='add-policy-to-framework'),
    path('frameworks/<int:framework_id>/policies/list/', compliance_views.get_policies, name='get-policies'),
    path('policies/<int:policy_id>/subpolicies/add/', add_subpolicy_to_policy, name='add-subpolicy-to-policy'),
    path('subpolicies/<int:pk>/review/', submit_subpolicy_review, name='submit-subpolicy-review'),
    path('subpolicies/<int:pk>/resubmit/', resubmit_subpolicy, name='resubmit-subpolicy'),
    path('policy-approvals/reviewer/', list_policy_approvals_for_reviewer, name='policy-approvals-for-reviewer'),
    path('policy-counts/', get_policy_counts_by_status, name='get-policy-counts-by-status'),
    path('policies-paginated/', get_policies_paginated_by_status, name='get-policies-paginated-by-status'),
    path('policy-approvals/<int:approval_id>/', update_policy_approval, name='update_policy_approval'),
    path('policy-approvals/<int:approval_id>/review/', submit_policy_review, name='submit_policy_review'),
    path('policy-approvals/rejected/<int:user_id>/', list_rejected_policy_approvals_for_user, name='list-rejected-policy-approvals-for-user'),
    path('policy-approvals/resubmit/<int:approval_id>/', resubmit_policy_approval, name='resubmit-policy-approval-from-routes'),
    path('policy-users/', list_users, name='list-users'),
    path('framework-explorer/', get_framework_explorer_data, name='framework-explorer'),
    path('frameworks/<int:framework_id>/policies-list/', get_framework_policies, name='framework-policies'),
    path('frameworks/<int:framework_id>/toggle-status/', request_framework_status_change, name='toggle-framework-status'),
    path('policies/<int:policy_id>/toggle-status/', toggle_policy_status, name='toggle-policy-status'),
    path('frameworks/<int:framework_id>/details/', get_framework_details, name='framework-details'),
    path('policies/<int:policy_id>/details/', get_policy_details, name='policy-details'),
    path('all-policies/frameworks/', all_policies_get_frameworks, name='all-policies-frameworks'),
    path('all-policies/frameworks/<int:framework_id>/versions/', all_policies_get_framework_versions, name='all-policies-framework-versions'),
    path('all-policies/framework-versions/<int:version_id>/policies/', all_policies_get_framework_version_policies, name='all-policies-framework-version-policies'),
    path('all-policies/policies/', all_policies_get_policies, name='all-policies-policies'),
    path('all-policies/policies/<int:policy_id>/versions/', all_policies_get_policy_versions, name='all-policies-policy-versions'),
    path('all-policies/subpolicies/', all_policies_get_subpolicies, name='all-policies-subpolicies'),
    path('all-policies/policy-versions/<int:version_id>/subpolicies/', all_policies_get_policy_version_subpolicies, name='all-policies-policy-version-subpolicies'),
    path('all-policies/subpolicies/<int:subpolicy_id>/', all_policies_get_subpolicy_details, name='all-policies-subpolicy-details'),
    
    
    
    path('policy-dashboard/', get_policy_dashboard_summary),
    path('policy-status-distribution/', get_policy_status_distribution),
    path('reviewer-workload/', get_reviewer_workload),
    path('recent-policy-activity/', get_recent_policy_activity),
    path('avg-policy-approval-time/', get_avg_policy_approval_time),
    path('policy-analytics/', get_policy_analytics),
    
    
    path('api/policy-analytics/', get_policy_analytics, name='policy-analytics'),

    path('policy-kpis/', get_policy_kpis),    
    path('acknowledge-policy/<int:policy_id>/', acknowledge_policy, name='acknowledge-policy'),      
    path('frameworks/<int:framework_id>/get-policies/', get_policies_by_framework, name='get-policies-by-framework'),
    path('policies/<int:policy_id>/get-subpolicies/', get_subpolicies_by_policy, name='get-subpolicies-by-policy'),
    path('policies/<int:policy_id>/version/', get_policy_version, name='get-policy-version'),
    path('subpolicies/<int:subpolicy_id>/version/', get_subpolicy_version, name='get-subpolicy-version'),
    path('policy-approvals/latest/<int:policy_id>/', get_latest_policy_approval, name='get-latest-policy-approval'),
    path('policy-approvals/latest-by-role/<int:policy_id>/<str:role>/', get_latest_policy_approval_by_role, name='get-latest-policy-approval-by-role'),
    path('policies/<int:policy_id>/reviewer-version/', get_latest_reviewer_version, name='get-policy-reviewer-version'),
    path('policies/<int:policy_id>/submit-review/', submit_policy_approval_review, name='submit-policy-approval-review'),
    path('policies/<int:policy_id>/version-history/', get_policy_version_history, name='get-policy-version-history'),
    path('frameworks/<int:framework_id>/create-approval/', create_framework_approval, name='create-framework-approval'),
    path('frameworks/<int:framework_id>/approvals/', get_framework_approvals, name='get-framework-approvals'),
    path('frameworks/approvals/', get_framework_approvals, name='get-all-framework-approvals'),
    path('framework-approvals/<int:approval_id>/', update_framework_approval, name='update-framework-approval'),
    path('frameworks/<int:framework_id>/submit-review/', submit_framework_review, name='submit-framework-review'),
    path('framework-approvals/latest/<int:framework_id>/', get_latest_framework_approval, name='get-latest-framework-approval'),
    path('frameworks/<int:framework_id>/resubmit-approval/', resubmit_framework_approval, name='resubmit-framework-approval'),
    path('frameworks/<int:framework_id>/rejected/', get_rejected_frameworks_for_user, name='get-rejected-frameworks-for-user'),
    path('frameworks/rejected/', get_rejected_frameworks_for_user, name='get-all-rejected-frameworks'),
    path('tailoring/create-framework/', create_tailored_framework, name='create-tailored-framework'),
    path('tailoring/create-policy/', create_tailored_policy, name='create-tailored-policy'),
    path('frameworks/<int:framework_id>/policies/<int:policy_id>/subpolicies/<int:subpolicy_id>/approve-reject/', approve_reject_subpolicy_in_framework, name='approve-reject-subpolicy-in-framework'),
    path('frameworks/<int:framework_id>/policies/<int:policy_id>/approve-reject/', approve_reject_policy_in_framework, name='approve-reject-policy-in-framework'),
    path('frameworks/<int:framework_id>/approve-final/', approve_entire_framework_final, name='approve-entire-framework-final'),
    path('frameworks/<int:framework_id>/request-status-change/', request_framework_status_change, name='request-framework-status-change'),
    path('framework-approvals/<int:approval_id>/approve-status-change/', approve_framework_status_change, name='approve-framework-status-change'),
    path('framework-status-change-requests/', get_status_change_requests, name='get-status-change-requests'),
    
    
    path('policy-categories/', get_policy_categories, name='policy-categories'),
    path('policy-categories/save/', save_policy_category, name='save_policy_category'),

    path('policies/<int:policy_id>/request-status-change/', request_policy_status_change, name='request-policy-status-change'),
    path('policy-approvals/<int:approval_id>/approve-status-change/', approve_policy_status_change, name='approve-policy-status-change'),
    path('policy-status-change-requests/', get_policy_status_change_requests, name='get-policy-status-change-requests'),
    path('policy-status-change-requests-by-reviewer/', get_policy_status_change_requests_by_reviewer, name='get-policy-status-change-requests-by-reviewer'),
    path('policy-status-change-requests-by-reviewer/<int:reviewer_id>/', get_policy_status_change_requests_by_reviewer, name='get-policy-status-change-requests-by-reviewer-filtered'),
    path('policies/<int:policy_id>/test-debug/', test_policy_status_debug, name='test-policy-status-debug'),
    path('policy-categories/', get_policy_categories, name='policy-categories'),
    path('policy-categories/save/', save_policy_category, name='save_policy_category'),
    path('entities/', get_entities, name='get-entities'),
    path('update-activeinactive-by-date/', update_existing_activeinactive_by_date, name='update-activeinactive-by-date'),
    path('users-for-reviewer-selection/', get_users_for_reviewer_selection, name='get-users-for-reviewer-selection'),
    path('status-change-requests-by-reviewer/', get_status_change_requests_by_reviewer, name='get-status-change-requests-by-reviewer'),
    path('status-change-requests-by-reviewer/<int:reviewer_id>/', get_status_change_requests_by_reviewer, name='get-status-change-requests-by-reviewer-filtered'),
    path('test-users/', create_test_users, name='create-test-users'),
    path('policies/<int:policy_id>/compliance-stats/', get_policy_compliance_stats, name='get-policy-compliance-stats'),











    # Auth endpoints - Moved to top of file
   
    # Framework and Policy endpoints
    path('api/compliance/frameworks/', compliance_views.get_frameworks, name='get-frameworks'),
    path('compliance/policies/<int:policy_id>/subpolicies/', compliance_views.get_subpolicies, name='get-subpolicies'),
   
    # Compliance endpoints
    path('compliance-create/', compliance_views.create_compliance, name='create-compliance'),
    # path('api/compliance/create/', compliance_views.create_compliance, name='api-create-compliance'),
    path('api/compliance-create/', compliance_views.create_compliance, name='api-compliance-create'),
    path('compliance_edit/<int:compliance_id>/edit/', compliance_views.edit_compliance, name='edit-compliance'),
    path('api/compliance_edit/<int:compliance_id>/edit/', compliance_views.edit_compliance, name='api-edit-compliance'),
    path('clone-compliance/<int:compliance_id>/clone/', compliance_views.clone_compliance, name='clone-compliance'),
    path('compliance/<int:compliance_id>/framework-info/', compliance_views.get_compliance_framework_info, name='get-compliance-framework-info'),
    path('compliance/<int:compliance_id>/', compliance_views.get_compliance_details, name='get-compliance-details'),
    path('compliance/user-dashboard/', compliance_views.get_compliance_dashboard, name='compliance-dashboard'),
    path('compliance/kpi-dashboard/analytics/', compliance_views.get_compliance_analytics, name='compliance-analytics'),
    path('subpolicies/<int:subpolicy_id>/compliances/', compliance_views.get_compliances_by_subpolicy, name='get-compliances-by-subpolicy'),
   
    # All Policies endpoints
    path('compliance/all-policies/frameworks/', compliance_views.all_policies_get_frameworks, name='all-policies-get-frameworks'),
    path('compliance/all-policies/policies/', compliance_views.all_policies_get_policies, name='all-policies-get-policies'),
    path('compliance/all-policies/subpolicies/', compliance_views.all_policies_get_subpolicies, name='all-policies-get-subpolicies'),
    path('compliance/all-policies/subpolicy/<int:subpolicy_id>/compliance-compliances/', compliance_views.all_policies_get_subpolicy_compliances, name='all-policies-get-subpolicy-compliances'),
    path('compliance/all-policies/compliance/<int:compliance_id>/versions/', compliance_views.all_policies_get_compliance_versions, name='all-policies-get-compliance-versions'),
   
    # Compliance approval endpoints
    path('compliance/compliance-approvals/<int:approval_id>/review/', compliance_views.submit_compliance_review, name='submit_compliance_review'),
    path('compliance/compliance-approvals/resubmit/<int:approval_id>/', compliance_views.resubmit_compliance_approval, name='resubmit_compliance_approval'),
    path('compliance/versioning/', compliance_views.get_compliance_versioning, name='get-compliance-versioning'),
    path('compliance/policy-approvals-compliance/reviewer/', compliance_views.get_policy_approvals_by_reviewer, name='get-policy-approvals-by-reviewer'),
    path('compliance/policy-approvals-compliance/rejected/<int:reviewer_id>/', compliance_views.get_rejected_approvals, name='get-rejected-approvals'),
   
    # User endpoints
    path('compliance-users/', compliance_views.get_all_users, name='get-compliance-users'),
 
    # Compliance export endpoints
    path('api/compliance/export/all-compliances/<str:export_format>/<str:item_type>/<int:item_id>/',
         compliance_views.export_compliances,
         name='export-all-compliances'),
   
    path('api/compliance/export/all-compliances/<str:export_format>/',
         compliance_views.export_compliances,
         name='export-all-compliances-legacy'),
   
    path('compliances/framework/<int:framework_id>/', compliance_views.get_framework_compliances, name='get-framework-compliances'),
    path('compliances/policy/<int:policy_id>/', compliance_views.get_policy_compliances, name='get-policy-compliances'),
    path('compliances/subpolicy/<int:subpolicy_id>/', compliance_views.get_subpolicy_compliances, name='get-subpolicy-compliances'),
 
    # API endpoints
    path('compliance/frameworks/', compliance_views.get_frameworks, name='api-get-frameworks'),
    path('compliance/frameworks/<int:framework_id>/policies/list/', compliance_views.get_policies, name='api-get-policies'),
    path('compliance/policies/<int:policy_id>/subpolicies/', compliance_views.get_subpolicies, name='api-get-subpolicies'),
    path('api/subpolicies/<int:subpolicy_id>/compliances/', compliance_views.get_compliances_by_subpolicy, name='api-get-compliances-by-subpolicy'),
    path('compliance/policies/<int:policy_id>/subpolicies/add/', add_subpolicy_to_policy, name='api-add-subpolicy-to-policy'),
    path('compliance/all-policies/frameworks/', compliance_views.all_policies_get_frameworks, name='all-policies-frameworks'),
    path('compliance/all-policies/frameworks/<int:framework_id>/versions/', compliance_views.all_policies_get_framework_versions, name='all-policies-framework-versions'),
    path('compliance/all-policies/framework-versions/<int:version_id>/policies/', compliance_views.all_policies_get_framework_version_policies, name='all-policies-framework-version-policies'),
    path('compliance/all-policies/policies/', compliance_views.all_policies_get_policies, name='all-policies-policies'),
    path('api/compliance/all-policies/policies/<int:policy_id>/versions/', compliance_views.all_policies_get_policy_versions, name='all-policies-policy-versions'),
    path('api/compliance/all-policies/subpolicies/', compliance_views.all_policies_get_subpolicies, name='all-policies-subpolicies'),
    path('api/compliance/all-policies/policy-versions/<int:version_id>/subpolicies/', compliance_views.all_policies_get_policy_version_subpolicies, name='all-policies-policy-version-subpolicies'),
    path('api/compliance/all-policies/subpolicies/<int:subpolicy_id>/', compliance_views.all_policies_get_subpolicy_details, name='all-policies-subpolicy-details'),
    path('compliance/all-policies/subpolicies/<int:subpolicy_id>/compliances/', compliance_views.all_policies_get_subpolicy_compliances, name='all-policies-subpolicy-compliances'),
    path('api/compliance/all-policies/compliances/<int:compliance_id>/versions/', compliance_views.all_policies_get_compliance_versions, name='all-policies-compliance-versions'),
       
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
    path('compliance/compliance/<int:compliance_id>/audit-info/',
         compliance_views.get_compliance_audit_info,
         name='get-compliance-audit-info'),
 
    path('test-notification/', compliance_views.test_notification, name='test-notification'),
   
    # Category endpoints
    path('categories/<str:source>/', compliance_views.get_category_values, name='get-category-values'),
    path('categories/add/', compliance_views.add_category_value, name='add-category-value'),
    path('categories/initialize/', compliance_views.initialize_default_categories, name='initialize-categories'),

    path('category-business-units/', compliance_views.get_category_business_units, name='get_category_business_units'),
    path('category-business-units/add/', compliance_views.add_category_business_unit, name='add_category_business_unit'),













    # Data endpoints for assignment
    path('assign-data/', get_assign_data, name='get_assign_data'),
    path('create-audit/', create_audit, name='create_audit'),  # Creates separate audits for each team member
    
    # Policy allocation endpoint
    # path('allocate-policy/', audit_views.allocate_policy, name='allocate_policy'),

    # Audit endpoints
    path('api/audits/', audit_views.get_all_audits, name='get_all_audits'),
    path('my-audits/', audit_views.get_my_audits, name='get_my_audits'),
    path('my-reviews/', audit_views.get_my_reviews, name='get_my_reviews'),
    path('api/audits/<int:audit_id>/', audit_views.get_audit_details, name='get_audit_details'),
    path('audits/<int:audit_id>/status/', audit_views.update_audit_status, name='update_audit_status'),
    path('audits/<int:audit_id>/update-audit-review-status/', reviewing.update_audit_review_status, name='update_audit_review_status'),
    path('api/audits/<int:audit_id>/get-status/', audit_views.get_audit_status, name='get_audit_status'),
    path('api/audits/<int:audit_id>/compliances/', get_audit_compliances, name='get_audit_compliances'),
    path('api/audits/<int:audit_id>/submit/', audit_views.submit_audit_findings, name='submit_audit_findings'),
    
    # Audit Version endpoints
    path('api/audits/<int:audit_id>/versions/', audit_views.get_audit_versions, name='get_audit_versions'),
    path('api/audits/<int:audit_id>/versions/<str:version>/', audit_views.get_audit_version_details, name='get_audit_version_details'),
    path('api/audits/<int:audit_id>/check-version/', audit_views.check_audit_version, name='check_audit_version'),
    
    # New endpoint for saving audit JSON to version table
    path('api/audits/<int:audit_id>/save-audit-version/', save_audit_json_version, name='save_audit_json_version'),
    
    # New endpoint for saving audit form data as versions
    path('audits/<int:audit_id>/save-version/', save_audit_version, name='save_audit_version'),
    
    # New endpoint for sending audit for review
    path('audits/<int:audit_id>/send-for-review/', send_audit_for_review, name='send_audit_for_review'),
    
    # Audit Finding endpoints
    path('api/audit-findings/<int:compliance_id>/', audit_views.update_audit_finding, name='update_audit_finding'),
    path('api/audit-findings/<int:compliance_id>/evidence/', audit_views.upload_evidence, name='upload_evidence'),
    # Also register the endpoint with the exact URL the frontend is calling
    path('api/upload-evidence/<int:compliance_id>/', audit_views.upload_evidence, name='upload_evidence_direct'),
    
    # Compliance endpoints
    path('api/compliance/', audit_views.get_all_compliance, name='get_all_compliance'),
    path('api/subpolicies/<int:subpolicy_id>/compliance/', audit_views.get_compliance_by_subpolicy, name='get_compliance_by_subpolicy'),
    
    # New endpoint for adding compliance items in audit context
    path('api/audits/<int:audit_id>/add-compliance/', add_compliance_to_audit, name='add_compliance_to_audit'),
    
    # Migration helper endpoints
    path('api/add-majorminor-column/', audit_views.add_majorminor_column, name='add_majorminor_column'),
    
    # Fixed subpolicy version field
    path('api/fix-subpolicy-version/', audit_views.fix_subpolicy_version_field, name='fix_subpolicy_version_field'),
    path('api/fix-audit-table/', audit_views.fix_audit_table, name='fix_audit_table'),

    # Endpoint for saving review progress
    path('audits/<int:audit_id>/save-review-progress/', audit_views.save_review_progress, name='save_review_progress'),

    # New endpoint for loading review data
    path('api/audits/<int:audit_id>/load-review/', load_review_data, name='load_review_data'),
    
    # Endpoint for loading latest review version data regardless of prefix (A or R)
    path('api/audits/<int:audit_id>/load-latest-review-version/', load_latest_review_version, name='load_latest_review_version'),
    
    # Endpoint for loading continuing data for auditors after reviewer feedback
    path('api/audits/<int:audit_id>/load-continuing-data/', load_continuing_data, name='load_continuing_data'),
    
    # Alias for load-continuing-data for consistency with frontend API call
    path('api/audits/<int:audit_id>/load-audit-continuing-data/', load_audit_continuing_data, name='load_audit_continuing_data'),

    # Add this to urlpatterns
    path('api/audits/<int:audit_id>/debug-status-transition/', audit_views.debug_audit_status_transition, name='debug_audit_status_transition'),

    # New debug endpoint
    path('api/debug/audit-version-schema/', audit_views.debug_audit_version_schema, name='debug_audit_version_schema'),

    # New debug endpoint for checking audit versions
    path('debug/audit-versions/<int:audit_id>/', audit_views.debug_audit_versions, name='debug_audit_versions'),

    # New endpoint for generating and downloading audit report - using the simplified version
    path('generate-audit-report/<int:audit_id>/', report_views.generate_audit_report, name='generate-audit-report'),

    # Audit Reports endpoints
    path('audit-reports/', audit_report_views.get_audit_reports, name='get_audit_reports'),
    path('audit-reports/<int:audit_id>/versions/', audit_report_views.get_audit_report_versions, name='get_audit_report_versions'),
    path('audit-reports/<int:audit_id>/versions/<str:version>/delete/', audit_report_views.delete_audit_report_version, name='delete_audit_report_version'),
    path('audit-reports/<int:audit_id>/versions/<str:version>/s3-link/', audit_report_views.get_audit_report_s3_link, name='get_audit_report_s3_link'),
    path('audit-reports/check/', audit_report_handlers.check_audit_reports, name='check_reports'),
    path('audit-reports/details/', audit_report_handlers.get_report_details, name='get_report_details'),
    path('compliance-count/', get_compliance_count, name='get_compliance_count'),
    
    # KPI endpoints
    path('kpi/non-compliance/', kpi_functions.get_non_compliance_count, name='non_compliance_count'),
    path('kpi/audit-completion/', kpi_functions.get_audit_completion_metrics, name='audit_completion_metrics'),
    path('kpi/audit-cycle-time/', kpi_functions.get_audit_cycle_time, name='audit_cycle_time'),
    path('kpi/finding-rate/', kpi_functions.get_finding_rate, name='finding_rate'),
    path('kpi/time-to-close/', kpi_functions.get_time_to_close_findings, name='time_to_close_findings'),
    #path('kpi/audit-pass-rate/', kpi_functions.get_audit_pass_rate, name='audit_pass_rate'),
    path('kpi/non-compliance-issues/', kpi_functions.get_non_compliance_issues, name='non_compliance_issues'),
    path('kpi/severity-distribution/', kpi_functions.get_severity_distribution, name='severity_distribution'),
    path('kpi/closure-rate/', kpi_functions.get_findings_closure_rate, name='findings_closure_rate'),
    path('kpi/evidence-completion/', kpi_functions.get_evidence_completion, name='evidence_completion'),
    path('kpi/report-timeliness/', kpi_functions.get_report_timeliness, name='report_timeliness'),
    path('kpi/compliance-readiness/', kpi_functions.get_compliance_readiness, name='compliance_readiness'),
    
    # Dashboard endpoints
    path('dashboard/audit-completion-rate/', UserDashboard.get_audit_completion_rate, name='get_audit_completion_rate'),
    path('dashboard/total-audits/', UserDashboard.get_total_audits, name='get_total_audits'),
    path('dashboard/open-audits/', UserDashboard.get_open_audits, name='get_open_audits'),
    path('dashboard/completed-audits/', UserDashboard.get_completed_audits, name='get_completed_audits'),
    
    # Chart data endpoints
    path('dashboard/audit-completion-trend/', UserDashboard.audit_completion_trend, name='audit_completion_trend'),
    path('dashboard/audit-compliance-trend/', UserDashboard.audit_compliance_trend, name='audit_compliance_trend'),
    path('dashboard/audit-finding-trend/', UserDashboard.audit_finding_trend, name='audit_finding_trend'),
    path('dashboard/framework-performance/', UserDashboard.framework_performance, name='framework_performance'),
    path('dashboard/category-performance/', UserDashboard.category_performance, name='category_performance'),
    path('dashboard/status-distribution/', UserDashboard.status_distribution, name='status_distribution'),
    path('dashboard/recent-audit-activities/', UserDashboard.recent_audit_activities, name='recent_audit_activities'),

    # New URL patterns for assign_audit.py
    path('frameworks/', get_frameworks, name='get_frameworks'),  # Commented out to avoid conflict with the framework_list endpoint
    path('policies/', get_policies, name='get_policies'),
    path('subpolicies/', get_subpolicies, name='get_subpolicies'),
    path('audit-users/', get_users_audit, name='get_users_audit'),
    path('compliance-count/', get_compliance_count, name='get_compliance_count'),
    path('compliance-count/<int:policy_id>/', get_compliance_count, name='get_compliance_count_by_policy'),

    # Task View endpoint with compliances
    path('audits/<int:audit_id>/task-details/', get_audit_task_details, name='get_audit_task_details'),

    # Audit compliances endpoints - support both URL patterns
    path('audit-compliances/<int:audit_id>/', get_audit_compliances, name='get_audit_compliances'),
    path('audits/<int:audit_id>/compliances/', get_audit_compliances, name='get_audit_compliances_alt'),

    # New URL pattern for approve_audit_and_create_incidents
    path('approve-audit-and-create-incidents/<int:audit_id>/', report_views.approve_audit_and_create_incidents, name='approve_audit_and_create_incidents'),

    path('business-impacts/', risk_views.get_business_impacts, name='get_business_impacts'),
    path('business-impacts/add/', risk_views.add_business_impact, name='add_business_impact'),
    path('risk-categories/', risk_views.get_risk_categories, name='get_risk_categories'),
    path('risk-categories/add/', risk_views.add_risk_category, name='add_risk_category'),

    # RBAC endpoints - Properly configured under /api/ prefix
    path('api/user-permissions/', rbac_views.get_user_permissions, name='api-user-permissions'),
    path('api/user-role/', rbac_views.get_user_role, name='api-user-role'),
    path('api/debug-permissions/', rbac_views.debug_user_permissions, name='api-debug-permissions'),
    path('api/debug-rbac-data/', rbac_views.debug_rbac_data, name='api-debug-rbac-data'),
    path('api/debug-auth-status/', rbac_views.debug_auth_status, name='api-debug-auth-status'),
    
    # Add test endpoint for user details
    path('api/test-user-details/<int:user_id>/', views.get_user_details_by_id, name='test-user-details'),
    path('api/save-user-session/', views.save_user_session, name='save-user-session'),









# Upload Framework endpoints
    path('upload-framework/', upload_framework_file, name='upload-framework'),
    path('load-default-data/', load_default_data, name='load-default-data'),
    path('processing-status/<str:task_id>/', get_processing_status, name='processing-status'),
    path('get-sections/<str:task_id>/', get_sections, name='get-sections'),
    path('update-section/', update_section, name='update-section'),
    path('create-checked-structure/', create_checked_structure, name='create-checked-structure'),
    path('extracted-policies/<str:task_id>/', get_extracted_policies, name='get-extracted-policies'),
    path('direct-process-checked-sections/', direct_process_checked_sections, name='direct-process-checked-sections'),
    path('save-updated-policies/', save_updated_policies, name='save-updated-policies'),
    path('save-policies/', save_policies, name='save-policies'),
    path('save-single-policy/', save_single_policy, name='save-single-policy'),
    path('saved-excel-files/<str:task_id>/', get_saved_excel_files, name='get-saved-excel-files'),
    path('policy-extraction-progress/<str:task_id>/', get_policy_extraction_progress, name='get-policy-extraction-progress'),
    
    # New policy details endpoints
    path('save-policy-details/', save_policy_details, name='save-policy-details'),
    path('save-complete-policy-package/', save_complete_policy_package, name='save-complete-policy-package'),
    
    
    
    
    path('save-framework-to-database/', save_framework_to_database, name='save-framework-to-database'),
    
    
    # temporary use muni changed , need to clarify with praharshitha 
    path('compliances/<str:type>/<int:id>/', compliance_views.get_compliances_by_type, name='get_compliances_by_type'),
    path('api/subpolicies/<int:subpolicy_id>/compliances/', compliance_views.get_compliances_by_subpolicy, name='api-get-compliances-by-subpolicy'),
    path('api/compliance/<int:compliance_id>/toggle-version/', compliance_views.toggle_compliance_version, name='api-toggle-compliance-version'),
    path('api/compliance/<int:compliance_id>/toggle/', compliance_views.toggle_compliance_version, name='api-toggle-compliance-alternative'),
    path('compliance/all-policies/frameworks/', compliance_views.all_policies_get_frameworks, name='all-policies-frameworks'),
] + compliance_urlpatterns