"""
RBAC Decorators for GRC System

This module provides decorators for checking RBAC permissions on view functions.
These decorators provide an additional layer of security beyond the permission classes.
"""

from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import logging
from .utils import RBACUtils

logger = logging.getLogger(__name__)

def rbac_required(required_permission=None, endpoint_name=None):
    """
    Decorator to check RBAC permissions for view functions
    
    Args:
        required_permission: Specific permission to check (e.g., 'view_all_policy', 'create_policy')
        endpoint_name: Name of the endpoint for automatic permission lookup
    
    Usage:
        @rbac_required(required_permission='view_all_policy')
        def my_view(request):
            # Your view logic here
            pass
        
        # Or use endpoint name for automatic lookup
        @rbac_required(endpoint_name='get_policy_kpis')
        def get_policy_kpis(request):
            # Your view logic here
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Use endpoint name if provided, otherwise use function name
                check_endpoint_name = endpoint_name or view_func.__name__
                
                # Check permission
                permission_result = RBACUtils.check_endpoint_permission(
                    request, 
                    check_endpoint_name, 
                    required_permission
                )
                
                if not permission_result['allowed']:
                    logger.warning(f"[RBAC DECORATOR] Access denied to {check_endpoint_name}: {permission_result['message']}")
                    
                    # Return JSON response for API endpoints
                    return JsonResponse({
                        'error': 'Permission denied',
                        'message': permission_result['message'],
                        'required_permission': required_permission,
                        'endpoint': check_endpoint_name
                    }, status=403)
                
                # Log successful access
                logger.info(f"[RBAC DECORATOR] Access granted to {check_endpoint_name} for user {permission_result['user_id']}")
                
                # Call the original view function
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"[RBAC DECORATOR] Error in permission check: {str(e)}")
                return JsonResponse({
                    'error': 'Permission check failed',
                    'message': str(e)
                }, status=500)
        
        return wrapper
    return decorator

def policy_view_required(view_func):
    """Decorator for functions that require policy view permission"""
    return rbac_required(required_permission='view_all_policy')(view_func)

def policy_create_required(view_func):
    """Decorator for functions that require policy create permission"""
    return rbac_required(required_permission='create_policy')(view_func)

def policy_edit_required(view_func):
    """Decorator for functions that require policy edit permission"""
    return rbac_required(required_permission='edit_policy')(view_func)

def policy_approve_required(view_func):
    """Decorator for functions that require policy approve permission"""
    return rbac_required(required_permission='approve_policy')(view_func)

def policy_delete_required(view_func):
    """Decorator for functions that require policy delete permission (uses edit permission)"""
    return rbac_required(required_permission='edit_policy')(view_func)

def policy_assign_required(view_func):
    """Decorator for functions that require policy assign permission (uses edit permission)"""
    return rbac_required(required_permission='edit_policy')(view_func)

def check_user_permissions(request):
    """
    Helper function to check user permissions and return detailed info
    
    Returns:
        dict: User permission details or None if no access
    """
    try:
        user_id = RBACUtils.get_user_id_from_request(request)
        if not user_id:
            return None
        
        return RBACUtils.get_user_permissions_summary(user_id)
        
    except Exception as e:
        logger.error(f"[RBAC] Error checking user permissions: {e}")
        return None

def log_permission_access(endpoint_name, user_id, granted=True, reason=""):
    """
    Log permission access attempts for auditing
    
    Args:
        endpoint_name: Name of the endpoint accessed
        user_id: ID of the user attempting access
        granted: Whether access was granted
        reason: Reason for denial (if applicable)
    """
    try:
        access_type = "GRANTED" if granted else "DENIED"
        logger.info(f"[RBAC ACCESS LOG] {access_type} - User {user_id} -> {endpoint_name}")
        
        if not granted and reason:
            logger.info(f"[RBAC ACCESS LOG] DENIAL REASON: {reason}")
        
        # Here you could also save to database for audit trail
        # AuditLog.objects.create(user_id=user_id, endpoint=endpoint_name, granted=granted, reason=reason)
        
    except Exception as e:
        logger.error(f"[RBAC ACCESS LOG] Error logging access: {e}")

def require_any_permission(*required_permissions):
    """
    Decorator that requires user to have ANY of the specified permissions
    
    Args:
        *required_permissions: Variable number of permission names
    
    Usage:
        @require_any_permission('view_all_policy', 'approve_policy')
        def my_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                user_id = RBACUtils.get_user_id_from_request(request)
                if not user_id:
                    return JsonResponse({
                        'error': 'Authentication required',
                        'message': 'No user ID found in session'
                    }, status=401)
                
                from ..models import RBAC
                rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
                if not rbac_record:
                    return JsonResponse({
                        'error': 'Authorization failed',
                        'message': f'No RBAC record found for user {user_id}'
                    }, status=403)
                
                # Check if user has any of the required permissions
                has_permission = False
                granted_permissions = []
                
                for permission in required_permissions:
                    if getattr(rbac_record, permission, False):
                        has_permission = True
                        granted_permissions.append(permission)
                
                if not has_permission:
                    log_permission_access(
                        view_func.__name__, 
                        user_id, 
                        granted=False, 
                        reason=f"User lacks any of required permissions: {required_permissions}"
                    )
                    
                    return JsonResponse({
                        'error': 'Permission denied',
                        'message': f'User requires any of: {", ".join(required_permissions)}',
                        'required_permissions': list(required_permissions)
                    }, status=403)
                
                # Log successful access
                log_permission_access(
                    view_func.__name__, 
                    user_id, 
                    granted=True, 
                    reason=f"Granted via permissions: {granted_permissions}"
                )
                
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"[RBAC ANY PERMISSION] Error: {str(e)}")
                return JsonResponse({
                    'error': 'Permission check failed',
                    'message': str(e)
                }, status=500)
        
        return wrapper
    return decorator

def require_all_permissions(*required_permissions):
    """
    Decorator that requires user to have ALL of the specified permissions
    
    Args:
        *required_permissions: Variable number of permission names
    
    Usage:
        @require_all_permissions('view_all_policy', 'approve_policy')
        def my_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                user_id = RBACUtils.get_user_id_from_request(request)
                if not user_id:
                    return JsonResponse({
                        'error': 'Authentication required',
                        'message': 'No user ID found in session'
                    }, status=401)
                
                from ..models import RBAC
                rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
                if not rbac_record:
                    return JsonResponse({
                        'error': 'Authorization failed',
                        'message': f'No RBAC record found for user {user_id}'
                    }, status=403)
                
                # Check if user has all required permissions
                missing_permissions = []
                
                for permission in required_permissions:
                    if not getattr(rbac_record, permission, False):
                        missing_permissions.append(permission)
                
                if missing_permissions:
                    log_permission_access(
                        view_func.__name__, 
                        user_id, 
                        granted=False, 
                        reason=f"User lacks required permissions: {missing_permissions}"
                    )
                    
                    return JsonResponse({
                        'error': 'Permission denied',
                        'message': f'User lacks required permissions: {", ".join(missing_permissions)}',
                        'missing_permissions': missing_permissions
                    }, status=403)
                
                # Log successful access
                log_permission_access(
                    view_func.__name__, 
                    user_id, 
                    granted=True, 
                    reason=f"User has all required permissions: {required_permissions}"
                )
                
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"[RBAC ALL PERMISSIONS] Error: {str(e)}")
                return JsonResponse({
                    'error': 'Permission check failed',
                    'message': str(e)
                }, status=500)
        
        return wrapper
    return decorator