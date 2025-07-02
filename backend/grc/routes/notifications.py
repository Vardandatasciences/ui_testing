from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
import uuid

# Simple in-memory storage for notifications (in production, use database)
notifications_storage = []

@csrf_exempt
@require_http_methods(["POST"])
def push_notification(request):
    """
    Simple push notification function that can be called from any frontend operation
    """
    try:
        data = json.loads(request.body)
        
        # Extract notification data
        title = data.get('title', 'New Notification')
        message = data.get('message', 'You have a new notification')
        category = data.get('category', 'common')
        priority = data.get('priority', 'medium')
        user_id = data.get('user_id', 'default_user')
        
        # Create notification object
        notification = {
            'id': str(uuid.uuid4()),
            'title': title,
            'message': message,
            'category': category,
            'priority': priority,
            'createdAt': datetime.now().isoformat(),
            'status': {
                'isRead': False,
                'readAt': None
            },
            'user_id': user_id
        }
        
        # Store notification (in production, save to database)
        notifications_storage.append(notification)
        
        # Keep only last 100 notifications to prevent memory issues
        if len(notifications_storage) > 100:
            notifications_storage.pop(0)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification sent successfully',
            'notification': notification
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_notifications(request):
    """
    Get all notifications for a user
    """
    try:
        user_id = request.GET.get('user_id', 'default_user')
        
        # Filter notifications by user_id (in production, query database)
        user_notifications = [
            n for n in notifications_storage 
            if n.get('user_id') == user_id
        ]
        
        return JsonResponse({
            'status': 'success',
            'notifications': user_notifications
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mark_as_read(request):
    """
    Mark a notification as read
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        # Find and update notification (in production, update database)
        for notification in notifications_storage:
            if notification['id'] == notification_id:
                notification['status']['isRead'] = True
                notification['status']['readAt'] = datetime.now().isoformat()
                break
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification marked as read'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """
    Mark all notifications as read for a user
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id', 'default_user')
        
        # Mark all user notifications as read (in production, update database)
        for notification in notifications_storage:
            if notification.get('user_id') == user_id:
                notification['status']['isRead'] = True
                notification['status']['readAt'] = datetime.now().isoformat()
        
        return JsonResponse({
            'status': 'success',
            'message': 'All notifications marked as read'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500) 