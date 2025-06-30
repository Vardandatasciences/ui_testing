from rest_framework.decorators import api_view
from rest_framework.response import Response
from .kpi_functions import (
    get_audit_completion_stats,
    get_audit_cycle_time,
    get_finding_rate,
    get_time_to_close,
    get_audit_pass_rate,
    get_non_compliance_trend,
    get_severity_distribution,
    get_closure_rate,
    get_evidence_collection_progress,
    get_compliance_readiness,
    get_report_timeliness
)

@api_view(['GET'])
def audit_completion(request):
    """Get audit completion statistics"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_audit_completion_stats(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def audit_cycle_time(request):
    """Get average audit cycle time"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_audit_cycle_time(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def finding_rate(request):
    """Get average findings per audit"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_finding_rate(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def time_to_close(request):
    """Get average time to close findings"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_time_to_close(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def audit_pass_rate(request):
    """Get audit pass rate"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_audit_pass_rate(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def non_compliance_trend(request):
    """Get non-compliance trend"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_non_compliance_trend(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def severity_distribution(request):
    """Get severity distribution of findings"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_severity_distribution(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def closure_rate(request):
    """Get finding closure rate"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_closure_rate(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def evidence_collection(request):
    """Get evidence collection progress"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_evidence_collection_progress(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def compliance_readiness(request):
    """Get compliance readiness status"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_compliance_readiness(time_filter, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def report_timeliness(request):
    """Get audit report timeliness metrics"""
    time_filter = request.GET.get('time_filter', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = get_report_timeliness(time_filter, start_date, end_date)
    return Response(data) 