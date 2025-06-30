from django.urls import path
from . import views

urlpatterns = [
    # KPI endpoints
    path('kpi/audit-completion/', views.audit_completion, name='audit-completion'),
    path('kpi/audit-cycle-time/', views.audit_cycle_time, name='audit-cycle-time'),
    path('kpi/finding-rate/', views.finding_rate, name='finding-rate'),
    path('kpi/time-to-close/', views.time_to_close, name='time-to-close'),
    path('kpi/audit-pass-rate/', views.audit_pass_rate, name='audit-pass-rate'),
    path('kpi/non-compliance-trend/', views.non_compliance_trend, name='non-compliance-trend'),
    path('kpi/severity-distribution/', views.severity_distribution, name='severity-distribution'),
    path('kpi/closure-rate/', views.closure_rate, name='closure-rate'),
    path('kpi/evidence-collection/', views.evidence_collection, name='evidence-collection'),
    path('kpi/compliance-readiness/', views.compliance_readiness, name='compliance-readiness'),
    path('kpi/report-timeliness/', views.report_timeliness, name='report-timeliness'),
] 