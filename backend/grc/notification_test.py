import os
import sys
import django
import argparse
import logging
from datetime import datetime

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notification_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("notification_test")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Now import Django models
from grc.models import Notification, User
from grc.notification_service import NotificationService

def test_notification(email=None, notification_type='all', force_create=False):
    """
    Test the notification system by sending test emails
    
    Args:
        email: Email address to send test notifications to
        notification_type: Type of notification to test ('all', 'creation', 'edit', 'approval', 'rejection', 'toggle')
        force_create: Create the user if not found
    """
    try:
        notification_service = NotificationService()
        
        # If no email provided, find a user from the database
        if not email:
            user = User.objects.filter(email__isnull=False).exclude(email='').first()
            if user:
                email = user.email
                logger.info(f"Using email from existing user: {email}")
            else:
                email = "test@example.com"
                logger.warning(f"No users with valid email found. Using default: {email}")
        
        # Validate email exists in users table
        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"User with email {email} not found in database")
            
            if force_create:
                # Create a user for testing
                username = email.split('@')[0]
                user = User(
                    UserName=username,
                    email=email,
                    Password='testpassword'  # In production, this would be hashed
                )
                user.save()
                logger.info(f"Created test user: {username} with email {email} (ID: {user.UserId})")
            else:
                logger.error("Use --force-create to create a test user")
                return False
        
        results = {}
        
        # Test compliance creation notification
        if notification_type in ['all', 'creation']:
            creation_data = {
                'notification_type': 'compliance_creation',
                'email': email,
                'email_type': 'gmail',
                'template_data': [
                    user.UserName,
                    '12345',
                    'This is a test compliance description',
                    '1.0',
                    'Test Creator',
                    datetime.now().strftime('%Y-%m-%d')
                ]
            }
            results['creation'] = notification_service.send_multi_channel_notification(creation_data)
            logger.info(f"Creation notification result: {results['creation']}")
            
        # Test compliance edit notification
        if notification_type in ['all', 'edit']:
            edit_data = {
                'notification_type': 'compliance_edit',
                'email': email,
                'email_type': 'gmail',
                'template_data': [
                    user.UserName,
                    '12345',
                    'Updated compliance description',
                    '1.1',
                    '1.0',
                    'Test Editor',
                    datetime.now().strftime('%Y-%m-%d')
                ]
            }
            results['edit'] = notification_service.send_multi_channel_notification(edit_data)
            logger.info(f"Edit notification result: {results['edit']}")
            
        # Test compliance approval notification
        if notification_type in ['all', 'approval']:
            approval_data = {
                'notification_type': 'compliance_review',
                'email': email,
                'email_type': 'gmail',
                'template_data': [
                    user.UserName,
                    '12345',
                    'Approved compliance description',
                    '1.0',
                    'approved',
                    'This compliance looks good!'
                ]
            }
            results['approval'] = notification_service.send_multi_channel_notification(approval_data)
            logger.info(f"Approval notification result: {results['approval']}")
            
        # Test compliance rejection notification
        if notification_type in ['all', 'rejection']:
            rejection_data = {
                'notification_type': 'compliance_review',
                'email': email,
                'email_type': 'gmail',
                'template_data': [
                    user.UserName,
                    '12345',
                    'Rejected compliance description',
                    '1.0',
                    'rejected',
                    'This compliance needs more work.'
                ]
            }
            results['rejection'] = notification_service.send_multi_channel_notification(rejection_data)
            logger.info(f"Rejection notification result: {results['rejection']}")
            
        # Test version toggle notification
        if notification_type in ['all', 'toggle']:
            toggle_data = {
                'notification_type': 'policyStatusChange',
                'email': email,
                'email_type': 'gmail',
                'template_data': [
                    user.UserName,
                    'Compliance COMP-12345 v1.0',
                    'Activated',
                    'Administrator',
                    datetime.now().strftime('%Y-%m-%d')
                ]
            }
            results['toggle'] = notification_service.send_multi_channel_notification(toggle_data)
            logger.info(f"Toggle notification result: {results['toggle']}")
        
        # Check if notifications were logged in the database
        recent_notifications = Notification.objects.filter(recipient=email).order_by('-created_at')[:10]
        if recent_notifications:
            logger.info(f"Found {recent_notifications.count()} recent notification records:")
            for n in recent_notifications:
                logger.info(f"  - ID: {n.id}, Type: {n.type}, Channel: {n.channel}, Success: {n.success}, Created: {n.created_at}")
        else:
            logger.warning("No notification records found in database")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing notifications: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test GRC notification system')
    parser.add_argument('--email', help='Email address to send test notifications to')
    parser.add_argument('--type', default='all', 
                      choices=['all', 'creation', 'edit', 'approval', 'rejection', 'toggle'],
                      help='Type of notification to test')
    parser.add_argument('--force-create', action='store_true', 
                      help='Create user if email not found in database')
    
    args = parser.parse_args()
    
    success = test_notification(args.email, args.type, args.force_create)
    if success:
        print("Notification test completed successfully. Check logs for details.")
        sys.exit(0)
    else:
        print("Notification test failed. Check logs for details.")
        sys.exit(1) 