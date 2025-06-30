from django.urls import path, include
from django.http import HttpResponse
from . import views
from .views import get_incident_counts as get_counts
from rest_framework.routers import DefaultRouter
from .views import create_workflow, create_incident_from_audit_finding
from .views import FileUploadView

urlpatterns = [
     path('', lambda request: HttpResponse("API is working ✅")),
    
    # Dashboard endpoints (moved to top for priority)
    path('incidents/dashboard/', views.incident_dashboard, name='incident-dashboard'),
    path('incidents/dashboard/analytics/', views.incident_analytics, name='incident-analytics'),
    path('incidents/recent/', views.get_recent_incidents, name='recent-incidents'),
    
    # Other incident endpoints
    path('incidents/', views.list_incidents, name='list-incidents'),
    path('api/incidents/', views.list_incidents, name='api-list-incidents'),
    path('api/incidents/create/', views.create_incident, name='api-create-incident'),
    path('api/incidents/create', views.create_incident, name='api-create-incident-no-slash'),
    path('incident/create/', views.create_incident, name='create-incident-singular'),
    path('incident/schedule-manual/', views.schedule_manual_incident, name='schedule_manual_incident'),
    path('incident/reject/', views.reject_incident, name='reject_incident'),
    path('incidents/create/', views.create_incident, name='create-incident'),
    path('incidents/export/', views.export_incidents, name='export-incidents'),  # Use our new view
    
    # Audit findings endpoints
    path('audit-findings/', views.get_audit_findings, name='get-audit-findings'),
    path('lastchecklistitemverified/', views.audit_findings_list, name='audit-findings-list'),
    path('audit-findings/compliance/<int:compliance_id>/', views.audit_finding_detail, name='audit-finding-detail'),
    path('audit-findings/incident/<int:incident_id>/', views.audit_finding_incident_detail, name='audit-finding-incident-detail'),
    path('audit-findings/export/', views.export_audit_findings, name='export-audit-findings'),
    
    path('users/', views.list_users, name='list-users'),
    path('api/users/', views.list_users, name='api-get-users'),
    path('workflow/create/', views.create_workflow, name='workflow-create'),
    path('workflow/assigned/', views.list_assigned_findings, name='list-assigned-findings'),
    path('dashboard/incidents/', views.combined_incidents_and_audit_findings, name='dashboard-incidents'),
    path('incident/from-audit-finding/', views.create_incident_from_audit_finding, name='incident_from_audit_finding'),
    path('incident/schedule-manual/', views.schedule_manual_incident, name='schedule_manual_incident'),
    path('incident/reject/', views.reject_incident, name='reject_incident'),
    path('api/incident/mttd/', views.incident_mttd, name='incident-mttd'),
    path('api/incident/mttr/', views.incident_mttr, name='incident_mttr'),
    path('api/incident/mttc/', views.incident_mttc, name='incident-mttc'),
    path('api/incident/mttrv/', views.incident_mttrv, name='incident-mttrv'),
    path('api/incident/first-response-time/', views.first_response_time, name='first-response-time'),
    path('api/incident/incident-volume/', views.incident_volume, name='incident-volume'),
    path('api/incident/escalation-rate/', views.escalation_rate, name='escalation-rate'),
    path('api/incident/repeat-rate/', views.repeat_rate, name='repeat-rate'),
    path('api/incident/metrics/', views.incident_metrics, name='incident-metrics'),
    path('api/incidents/counts/', views.get_incident_counts, name='incident-counts'),
    path('api/incident/count/', views.incident_count, name='incident-count'),
    path('api/incident/by-severity/', views.incidents_by_severity, name='incidents-by-severity'),
    path('api/incident/root-causes/', views.incident_root_causes, name='incident-root-causes'),
    path('api/incident/origins/', views.incident_origins, name='incident-origins'),
    path('api/incident/types/', views.incident_types, name='incident-types'),
    path('api/incident/incident-cost/', views.incident_cost, name='incident-cost'),
    path('api/incident/cost/', views.incident_cost, name='incident-cost-alt'),
    path('api/incident/reopened-count/', views.incident_reopened_count, name='incident-reopened-count'),
    path('api/incident/false-positive-rate/', views.false_positive_rate, name='false-positive-rate'),
    path('api/incident/detection-accuracy/', views.detection_accuracy, name='detection-accuracy'),
    path('api/incident/incident-closure-rate/', views.incident_closure_rate, name='incident-closure-rate'),
#
    path('incidents/<int:incident_id>/status/', views.update_incident_status, name='update-incident-status'),
    path('incidents/<int:incident_id>/assign/', views.assign_incident, name='assign-incident'),
    path('api/compliances/', views.get_compliances, name='get-compliances'),
    path('api/custom-users/', views.list_users, name='custom-users'),
    
    # Incident User Tasks endpoints
    path('api/user-incidents/<int:user_id>/', views.user_incidents, name='user-incidents'),
    path('api/incident-reviewer-tasks/<int:user_id>/', views.incident_reviewer_tasks, name='incident-reviewer-tasks'),
    path('api/incident-mitigations/<int:incident_id>/', views.incident_mitigations, name='incident-mitigations'),
    path('api/assign-incident-reviewer/', views.assign_incident_reviewer, name='assign-incident-reviewer'),
    path('api/incident-review-data/<int:incident_id>/', views.incident_review_data, name='incident-review-data'),
    path('api/complete-incident-review/', views.complete_incident_review, name='complete-incident-review'),
    path('api/submit-incident-assessment/', views.submit_incident_assessment, name='submit-incident-assessment'),
    path('api/incident-approval-data/<int:incident_id>/', views.incident_approval_data, name='incident-approval-data'),
    
    # Audit Finding User Tasks endpoints
    path('api/user-audit-findings/<int:user_id>/', views.user_audit_findings, name='user-audit-findings'),
    path('api/audit-finding-reviewer-tasks/<int:user_id>/', views.audit_finding_reviewer_tasks, name='audit-finding-reviewer-tasks'),
    path('api/audit-finding-mitigations/<int:incident_id>/', views.audit_finding_mitigations, name='audit-finding-mitigations'),
    path('api/assign-audit-finding-reviewer/', views.assign_audit_finding_reviewer, name='assign-audit-finding-reviewer'),
    path('api/audit-finding-review-data/<int:incident_id>/', views.audit_finding_review_data, name='audit-finding-review-data'),
    path('api/complete-audit-finding-review/', views.complete_audit_finding_review, name='complete-audit-finding-review'),
    path('api/submit-audit-finding-assessment/', views.submit_audit_finding_assessment, name='submit-audit-finding-assessment'),
    
    # Test endpoint for notifications
    path('api/test-notification/', views.test_notification, name='test-notification'),
    path('api/upload-file/', FileUploadView.as_view(), name='upload-file'),
    
    # Category and Business Unit endpoints
    path('api/categories/', views.get_categories, name='get-categories'),
    path('api/business-units/', views.get_business_units, name='get-business-units'),
    path('api/categories/add/', views.add_category, name='add-category'),
    path('api/business-units/add/', views.add_business_unit, name='add-business-unit'),
    path('api/seed-sample-data/', views.seed_sample_data, name='seed-sample-data'),
    path('api/debug-category-data/', views.debug_category_data, name='debug-category-data'),
]






 
 