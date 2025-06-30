"""
RBAC Views for GRC System

Views for testing and debugging RBAC permissions
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging
from .utils import RBACUtils
from .decorators import rbac_required, require_any_permission, require_all_permissions

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def get_user_permissions(request):
    """Get detailed permissions for the current user"""
    try:
        user_id = RBACUtils.get_user_id_from_request(request)
        if not user_id:
            return JsonResponse({
                'error': 'No user ID found',
                'user_id': None,
                'permissions': None
            }, status=401)
        
        permissions_summary = RBACUtils.get_user_permissions_summary(user_id)
        if not permissions_summary:
            return JsonResponse({
                'error': 'No RBAC record found',
                'user_id': user_id,
                'permissions': None
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'user_id': user_id,
            'permissions': permissions_summary
        })
        
    except Exception as e:
        logger.error(f"[RBAC] Error getting user permissions: {e}")
        return JsonResponse({
            'error': 'Failed to get permissions',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_user_role(request):
    """Get user role information"""
    try:
        user_id = RBACUtils.get_user_id_from_request(request)
        if not user_id:
            return JsonResponse({
                'error': 'No user ID found',
                'user_id': None,
                'role': None
            })
        
        from ..models import RBAC
        rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
        if not rbac_record:
            return JsonResponse({
                'error': 'No RBAC record found',
                'user_id': user_id,
                'role': None
            })
        
        return JsonResponse({
            'success': True,
            'user_id': user_id,
            'role': rbac_record.role,
            'username': rbac_record.username,
            'is_active': rbac_record.is_active
        })
        
    except Exception as e:
        logger.error(f"[RBAC] Error getting user role: {e}")
        return JsonResponse({
            'error': 'Failed to get role',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def debug_user_permissions(request):
    """Debug endpoint to show detailed permission information"""
    try:
        user_id = RBACUtils.get_user_id_from_request(request)
        if not user_id:
            return JsonResponse({
                'debug_info': {
                    'session_available': hasattr(request, 'session'),
                    'session_keys': list(request.session.keys()) if hasattr(request, 'session') else [],
                    'user_id_in_session': request.session.get('user_id') if hasattr(request, 'session') else None,
                    'error': 'No user ID found in session'
                }
            })
        
        from ..models import RBAC
        rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
        
        debug_info = {
            'user_id': user_id,
            'rbac_record_exists': rbac_record is not None,
            'session_data': dict(request.session) if hasattr(request, 'session') else {},
        }
        
        if rbac_record:
            debug_info.update({
                'role': rbac_record.role,
                'username': rbac_record.username,
                'is_active': rbac_record.is_active,
                'policy_permissions': {
                    'view': rbac_record.view_all_policy,
                    'create': rbac_record.create_policy,
                    'edit': rbac_record.edit_policy,
                    'approve': rbac_record.approve_policy,
                    'create_framework': rbac_record.create_framework,
                    'approve_framework': rbac_record.approve_framework,
                    'analytics': rbac_record.policy_performance_analytics,
                },
                'incident_permissions': {
                    'view': rbac_record.view_all_incident,
                    'create': rbac_record.create_incident,
                    'edit': rbac_record.edit_incident,
                    'assign': rbac_record.assign_incident,
                    'evaluate': rbac_record.evaluate_assigned_incident,
                    'escalate': rbac_record.escalate_to_risk,
                    'analytics': rbac_record.incident_performance_analytics,
                },
                'audit_permissions': {
                    'assign': rbac_record.assign_audit,
                    'conduct': rbac_record.conduct_audit,
                    'review': rbac_record.review_audit,
                    'view_reports': rbac_record.view_audit_reports,
                    'analytics': rbac_record.audit_performance_analytics,
                },
                'risk_permissions': {
                    'view': rbac_record.view_all_risk,
                    'create': rbac_record.create_risk,
                    'edit': rbac_record.edit_risk,
                    'approve': rbac_record.approve_risk,
                    'assign': rbac_record.assign_risk,
                    'evaluate': rbac_record.evaluate_assigned_risk,
                    'analytics': rbac_record.risk_performance_analytics,
                },
                'compliance_permissions': {
                    'view': rbac_record.view_all_compliance,
                    'create': rbac_record.create_compliance,
                    'edit': rbac_record.edit_compliance,
                    'approve': rbac_record.approve_compliance,
                    'analytics': rbac_record.compliance_performance_analytics,
                }
            })
        
        return JsonResponse({
            'debug_info': debug_info
        })
        
    except Exception as e:
        logger.error(f"[RBAC DEBUG] Error: {e}")
        return JsonResponse({
            'debug_info': {
                'error': str(e),
                'user_id': user_id if 'user_id' in locals() else None
            }
        })

@require_http_methods(["GET"])
def debug_rbac_data(request):
    """Debug endpoint to show all RBAC data"""
    try:
        user_id = RBACUtils.get_user_id_from_request(request)
        
        # Get all RBAC records for debugging (limit for security)
        from ..models import RBAC
        all_rbac = RBAC.objects.filter(is_active='Y')[:10]  # Limit to 10 records
        
        rbac_data = []
        for record in all_rbac:
            rbac_data.append({
                'id': record.rbac_id,
                'user_id': record.user_id,
                'username': record.username,
                'role': record.role,
                'is_active': record.is_active,
                'permissions_summary': {
                    'policy': f"v:{record.view_all_policy}, c:{record.create_policy}, e:{record.edit_policy}, a:{record.approve_policy}",
                    'incident': f"v:{record.view_all_incident}, c:{record.create_incident}, e:{record.edit_incident}, assign:{record.assign_incident}",
                    'audit': f"assign:{record.assign_audit}, conduct:{record.conduct_audit}, review:{record.review_audit}, reports:{record.view_audit_reports}",
                    'risk': f"v:{record.view_all_risk}, c:{record.create_risk}, e:{record.edit_risk}, a:{record.approve_risk}",
                    'compliance': f"v:{record.view_all_compliance}, c:{record.create_compliance}, e:{record.edit_compliance}, a:{record.approve_compliance}"
                }
            })
        
        return JsonResponse({
            'current_user_id': user_id,
            'total_active_rbac_records': RBAC.objects.filter(is_active='Y').count(),
            'sample_rbac_data': rbac_data,
            'debug_note': 'Showing first 10 active RBAC records for debugging'
        })
        
    except Exception as e:
        logger.error(f"[RBAC DEBUG] Error getting RBAC data: {e}")
        return JsonResponse({
            'error': 'Failed to get RBAC data',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def debug_auth_status(request):
    """Debug authentication and session status"""
    try:
        debug_data = {
            'session_info': {
                'has_session': hasattr(request, 'session'),
                'session_key': getattr(request.session, 'session_key', None) if hasattr(request, 'session') else None,
                'session_data': dict(request.session) if hasattr(request, 'session') else {},
                'session_empty': request.session.is_empty() if hasattr(request, 'session') else True,
            },
            'user_info': {
                'has_user': hasattr(request, 'user'),
                'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            },
            'rbac_status': {
                'user_id_from_session': RBACUtils.get_user_id_from_request(request),
            }
        }
        
        # Get RBAC record if user ID found
        user_id = RBACUtils.get_user_id_from_request(request)
        if user_id:
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            debug_data['rbac_status']['has_rbac_record'] = rbac_record is not None
            if rbac_record:
                debug_data['rbac_status']['role'] = rbac_record.role
                debug_data['rbac_status']['username'] = rbac_record.username
        
        return JsonResponse(debug_data)
        
    except Exception as e:
        logger.error(f"[RBAC DEBUG AUTH] Error: {e}")
        return JsonResponse({
            'error': 'Failed to debug auth status',
            'details': str(e)
        }, status=500)

# Test endpoints with RBAC decorators - updated to use new field names
@require_http_methods(["GET"])
@rbac_required(required_permission='view_all_policy')
def test_policy_view_permission(request):
    """Test endpoint that requires policy view permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have policy view permission',
        'user_id': user_id,
        'permission_tested': 'view_all_policy'
    })

@require_http_methods(["GET"])
@rbac_required(required_permission='create_policy')
def test_policy_create_permission(request):
    """Test endpoint that requires policy create permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have policy create permission',
        'user_id': user_id,
        'permission_tested': 'create_policy'
    })

@require_http_methods(["GET"])
@rbac_required(required_permission='approve_policy')
def test_policy_approve_permission(request):
    """Test endpoint that requires policy approve permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have policy approve permission',
        'user_id': user_id,
        'permission_tested': 'approve_policy'
    })

@require_http_methods(["GET"])
@require_any_permission('view_all_policy', 'create_policy')
def test_any_permission(request):
    """Test endpoint that requires ANY of view_all_policy OR create_policy"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have either view_all_policy OR create_policy permission',
        'user_id': user_id,
        'permission_tested': 'view_all_policy OR create_policy'
    })

@require_http_methods(["GET"])
@require_all_permissions('view_all_policy', 'create_policy')
def test_all_permissions(request):
    """Test endpoint that requires ALL of view_all_policy AND create_policy"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have both view_all_policy AND create_policy permissions',
        'user_id': user_id,
        'permission_tested': 'view_all_policy AND create_policy'
    })

# Additional test endpoints for incident module
@require_http_methods(["GET"])
@rbac_required(required_permission='view_all_incident')
def test_incident_view_permission(request):
    """Test endpoint that requires incident view permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have incident view permission',
        'user_id': user_id,
        'permission_tested': 'view_all_incident'
    })

@require_http_methods(["GET"])
@rbac_required(required_permission='create_incident')
def test_incident_create_permission(request):
    """Test endpoint that requires incident create permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have incident create permission',
        'user_id': user_id,
        'permission_tested': 'create_incident'
    })

@require_http_methods(["GET"])
@rbac_required(required_permission='assign_incident')
def test_incident_assign_permission(request):
    """Test endpoint that requires incident assign permission"""
    user_id = RBACUtils.get_user_id_from_request(request)
    return JsonResponse({
        'message': 'Success! You have incident assign permission',
        'user_id': user_id,
        'permission_tested': 'assign_incident'
    })

@require_http_methods(["POST"])
def test_endpoint_permission(request):
    """Test specific endpoint permission by name"""
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        endpoint_name = data.get('endpoint_name', 'get_policy_kpis')
        
        permission_result = RBACUtils.check_endpoint_permission(request, endpoint_name)
        
        return JsonResponse({
            'endpoint_tested': endpoint_name,
            'permission_result': permission_result
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to test endpoint permission',
            'details': str(e)
        }, status=500) 