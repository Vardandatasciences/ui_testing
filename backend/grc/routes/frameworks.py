from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from ..models import Framework, FrameworkApproval, Policy, SubPolicy, PolicyApproval, FrameworkVersion,Users
import json
from datetime import datetime
from django.db import connection
from ..notification_service import NotificationService  # Add this import
# Import logging modules
import logging
import traceback
from ..utils import send_log, get_client_ip

# Configure logging
logger = logging.getLogger(__name__)

# RBAC Permission imports - Add comprehensive RBAC permissions
from ..rbac.permissions import (
    PolicyFrameworkPermission, PolicyApprovalWorkflowPermission, PolicyViewPermission,
    PolicyApprovePermission, PolicyEditPermission
)


def get_next_reviewer_version(framework):
    """
    Helper function to determine the next reviewer version for a framework
    """
    # Check if there's already a reviewer version for this framework
    latest_reviewer_version = FrameworkApproval.objects.filter(
        FrameworkId=framework,
        Version__startswith='r'
    ).order_by('-ApprovalId').first()
    
    if latest_reviewer_version:
        # Increment the existing reviewer version
        try:
            version_num = int(latest_reviewer_version.Version[1:])
            return f'r{version_num + 1}'
        except ValueError:
            return 'r1'
    else:
        # First reviewer version
        return 'r1'


def get_next_policy_reviewer_version(policy):
    """
    Helper function to determine the next reviewer version for a policy
    """
    # Check if there's already a reviewer version for this policy
    latest_reviewer_version = PolicyApproval.objects.filter(
        PolicyId=policy,
        Version__startswith='r'
    ).order_by('-ApprovalId').first()
    
    if latest_reviewer_version:
        # Increment the existing reviewer version
        try:
            version_num = int(latest_reviewer_version.Version[1:])
            return f'r{version_num + 1}'
        except ValueError:
            return 'r1'
    else:
        # First reviewer version
        return 'r1'


@api_view(['POST'])
@permission_classes([AllowAny])  # RBAC: Require PolicyApprovalWorkflowPermission for creating framework approvals
def create_framework_approval(request, framework_id):
    """
    Create a framework approval entry when a new framework is created
    """
    # Log framework approval creation attempt
    logger.info(f"Framework approval creation attempt for framework ID: {framework_id}")
    send_log(
        module="Framework",
        actionType="CREATE_APPROVAL",
        description=f"Framework approval creation attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    # Import security modules
    from django.utils.html import escape as escape_html
    import shlex
    
    # =================================================================
    # SECURITY IMPLEMENTATIONS - Context-Appropriate Server-Side Encoding
    # =================================================================
    # 1. HTML Context → escape_html() - Prevents XSS attacks
    # 2. SQL Context → Django ORM (parameterized queries) - Prevents SQL injection
    # 3. Shell Context → shlex.quote() - Prevents command injection
    # 4. All user inputs are sanitized before storage and rendering
    # =================================================================
    
    # Security Helper Function: Secure URL handling for potential shell command usage
    def secure_url_for_shell(url):
        """
        Example: Shell Command Injection Protection
        If URL needs to be used in shell commands (like wget, curl), use shlex.quote()
        Example: subprocess.run(['wget', shlex.quote(url)])
        """
        if url:
            return shlex.quote(str(url))
        return ""
    
    try:
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        logger.info(f"Found framework: {framework.FrameworkName} (ID: {framework_id})")
        
        # Security: Escape framework name for safe logging (prevents log injection)
        safe_framework_name = escape_html(framework.FrameworkName)
        print(f"DEBUG: Creating framework approval for: {safe_framework_name} (ID: {framework_id})")
        
        # Extract data for the approval
        user_id = request.data.get('UserId', 1)  # Default to 1 if not provided
        reviewer_id = framework.Reviewer if framework.Reviewer else request.data.get('ReviewerId', 2)  # Default to 2
        
        # Security: XSS Protection - Escape policy and subpolicy text fields before adding to approval data
        policies_data = []
        created_policies = Policy.objects.filter(FrameworkId=framework)
        
        for policy in created_policies:
            policy_dict = {
                "PolicyId": policy.PolicyId,
                "PolicyName": escape_html(policy.PolicyName),
                "PolicyDescription": escape_html(policy.PolicyDescription),
                "Status": policy.Status,
                "StartDate": policy.StartDate.isoformat() if policy.StartDate else None,
                "EndDate": policy.EndDate.isoformat() if policy.EndDate else None,
                "Department": escape_html(policy.Department),
                "CreatedByName": escape_html(policy.CreatedByName),
                "CreatedByDate": policy.CreatedByDate.isoformat() if policy.CreatedByDate else None,
                "Applicability": escape_html(policy.Applicability),
                "DocURL": escape_html(policy.DocURL),
                "Scope": escape_html(policy.Scope),
                "Objective": escape_html(policy.Objective),
                "Identifier": escape_html(policy.Identifier),
                "PermanentTemporary": policy.PermanentTemporary,
                "ActiveInactive": policy.ActiveInactive,
                "Reviewer": escape_html(policy.Reviewer),
                "CoverageRate": policy.CoverageRate,
                "CurrentVersion": policy.CurrentVersion,
                "subpolicies": []
            }
            
            # Security: XSS Protection - Escape subpolicy text fields
            subpolicies = SubPolicy.objects.filter(PolicyId=policy)
            for subpolicy in subpolicies:
                subpolicy_dict = {
                    "SubPolicyId": subpolicy.SubPolicyId,
                    "SubPolicyName": escape_html(subpolicy.SubPolicyName),
                    "CreatedByName": escape_html(subpolicy.CreatedByName),
                    "CreatedByDate": subpolicy.CreatedByDate.isoformat() if subpolicy.CreatedByDate else None,
                    "Identifier": escape_html(subpolicy.Identifier),
                    "Description": escape_html(subpolicy.Description),
                    "Status": subpolicy.Status,
                    "PermanentTemporary": subpolicy.PermanentTemporary,
                    "Control": escape_html(subpolicy.Control)
                }
                policy_dict["subpolicies"].append(subpolicy_dict)
            
            policies_data.append(policy_dict)
        
        # Security: XSS Protection - Escape all framework text fields before storing in extracted_data
        extracted_data = {
            "FrameworkName": escape_html(framework.FrameworkName),
            "FrameworkDescription": escape_html(framework.FrameworkDescription),
            "Category": escape_html(framework.Category),
            "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
            "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
            "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
            "CreatedByName": escape_html(framework.CreatedByName),
            "CreatedByDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
            "Identifier": escape_html(framework.Identifier),
            "Status": framework.Status,
            "ActiveInactive": framework.ActiveInactive,
            "InternalExternal": framework.InternalExternal,
            "type": "framework",
            "docURL": escape_html(framework.DocURL),
            "reviewer": escape_html(framework.Reviewer),
            "source": "manual_approval",
            "policies": policies_data,
            "totalPolicies": len(policies_data),
            "totalSubpolicies": sum(len(p["subpolicies"]) for p in policies_data)
        }
        
        # Create the framework approval
        framework_approval = FrameworkApproval.objects.create(
            FrameworkId=framework,
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            Version="u1",  # Default initial version
            ApprovedNot=None  # Not yet approved
        )
        
        logger.info(f"Framework approval created successfully with ID: {framework_approval.ApprovalId}")
        send_log(
            module="Framework",
            actionType="CREATE_APPROVAL_SUCCESS",
            description=f"Framework approval created successfully for framework '{framework.FrameworkName}'",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            entityId=framework_approval.ApprovalId,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_id": framework_id,
                "framework_name": framework.FrameworkName,
                "approval_id": framework_approval.ApprovalId,
                "version": framework_approval.Version
            }
        )
        
        return Response({
            "message": "Framework approval created successfully",
            "ApprovalId": framework_approval.ApprovalId,
            "Version": framework_approval.Version
        }, status=status.HTTP_201_CREATED)
        
    except Framework.DoesNotExist:
        logger.error(f"Framework not found with ID: {framework_id}")
        send_log(
            module="Framework",
            actionType="CREATE_APPROVAL_FAILED",
            description=f"Framework approval creation failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error creating framework approval for framework {framework_id}: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="CREATE_APPROVAL_FAILED",
            description=f"Framework approval creation failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # RBAC: Require PolicyViewPermission for viewing framework approvals
def get_framework_approvals(request, framework_id=None):
    """
    Get all framework approvals or approvals for a specific framework
    """
    # Log framework approvals retrieval attempt
    logger.info(f"Framework approvals retrieval attempt for framework ID: {framework_id}")
    send_log(
        module="Framework",
        actionType="VIEW_APPROVALS",
        description=f"Framework approvals retrieval attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    # Import security modules for safe logging
    from django.utils.html import escape as escape_html
    import shlex
    
    try:
        if framework_id:
            # Security: Log framework ID safely
            logger.info(f"Getting approvals for framework ID: {framework_id}")
            print(f"DEBUG: Getting approvals for framework ID: {framework_id}")
            approvals = FrameworkApproval.objects.filter(FrameworkId=framework_id)
        else:
            logger.info("Getting all framework approvals")
            print("DEBUG: Getting all framework approvals")
            approvals = FrameworkApproval.objects.all()
            
        approvals_data = []
        for approval in approvals:
            approval_data = {
                "ApprovalId": approval.ApprovalId,
                "FrameworkId": approval.FrameworkId.FrameworkId if approval.FrameworkId else None,
                "ExtractedData": approval.ExtractedData,
                "UserId": approval.UserId,
                "ReviewerId": approval.ReviewerId,
                "Version": approval.Version,
                "ApprovedNot": approval.ApprovedNot,
                "ApprovedDate": approval.ApprovedDate.isoformat() if approval.ApprovedDate else None
            }
            
            # If this is an approved framework, also include its policies
            if approval.ApprovedNot is True:
                policies = Policy.objects.filter(FrameworkId=approval.FrameworkId)
                policies_data = []
                
                for policy in policies:
                    # Security: XSS Protection - Escape policy name in response data
                    policy_data = {
                        "PolicyId": policy.PolicyId,
                        "PolicyName": escape_html(policy.PolicyName),
                        "Status": policy.Status
                    }
                    policies_data.append(policy_data)
                
                approval_data["policies"] = policies_data
            
            approvals_data.append(approval_data)
        
        logger.info(f"Successfully retrieved {len(approvals_data)} framework approvals")
        send_log(
            module="Framework",
            actionType="VIEW_APPROVALS_SUCCESS",
            description=f"Successfully retrieved {len(approvals_data)} framework approvals",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_id": framework_id,
                "approvals_count": len(approvals_data)
            }
        )
            
        return Response(approvals_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving framework approvals: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="VIEW_APPROVALS_FAILED",
            description=f"Framework approvals retrieval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])# RBAC: Require PolicyApprovalWorkflowPermission for updating framework approvals
def update_framework_approval(request, approval_id):
    """
    Update a framework approval status
    """
    try:
        approval = FrameworkApproval.objects.get(ApprovalId=approval_id)
        
        # Update approval status
        approved = request.data.get('ApprovedNot')
        if approved is not None:
            approval.ApprovedNot = approved
            
            # If approved, set approval date
            if approved:
                approval.ApprovedDate = timezone.now().date()
                
                # Also update the framework status
                if approval.FrameworkId:
                    framework = approval.FrameworkId
                    framework.Status = 'Approved'
                    
                    # Check if the framework is inactive, and update Status accordingly
                    if framework.ActiveInactive == 'Inactive':
                        framework.Status = 'Inactive'
                        
                        # Also update the ExtractedData
                        if extracted_data:
                            # If extracted_data was provided in the request
                            if 'ActiveInactive' in extracted_data and extracted_data['ActiveInactive'] == 'Inactive':
                                extracted_data['Status'] = 'Inactive'
                        elif 'ActiveInactive' in approval.ExtractedData and approval.ExtractedData['ActiveInactive'] == 'Inactive':
                            # If using existing ExtractedData
                            approval.ExtractedData['Status'] = 'Inactive'
                    
                    framework.save()
            elif approved is False:
                # If rejected, update framework status
                if approval.FrameworkId:
                    framework = approval.FrameworkId
                    framework.Status = 'Rejected'
                    framework.save()
        
        # Update extracted data if provided
        extracted_data = request.data.get('ExtractedData')
        if extracted_data:
            approval.ExtractedData = extracted_data
            
        approval.save()
        
        return Response({
            "message": "Framework approval updated successfully",
            "ApprovalId": approval.ApprovalId,
            "ApprovedNot": approval.ApprovedNot,
            "ApprovedDate": approval.ApprovedDate.isoformat() if approval.ApprovedDate else None
        }, status=status.HTTP_200_OK)
        
    except FrameworkApproval.DoesNotExist:
        return Response({"error": "Framework approval not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny]) # RBAC: Require PolicyApprovalWorkflowPermission for submitting framework reviews
def submit_framework_review(request, framework_id):
    """
    Submit a review for a framework
    """
    logger.info(f"Framework review submission attempt for framework ID: {framework_id}")
    send_log(
        module="Framework",
        actionType="SUBMIT_REVIEW",
        description=f"Framework review submission attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    try:
        print(f"submit_framework_review called for framework_id: {framework_id}")
        print(f"Request data: {request.data}")
        logger.debug(f"Request data received: {request.data}")
        
        framework = Framework.objects.get(FrameworkId=framework_id)
        logger.info(f"Found framework: {framework.FrameworkName}, current status: {framework.Status}")
        print(f"Found framework: {framework.FrameworkName}, current status: {framework.Status}")
        
        # Get current version info
        current_version = request.data.get('currentVersion', 'u1')
        user_id = request.data.get('UserId', 1)
        reviewer_id = request.data.get('ReviewerId', 2)
        approved = request.data.get('ApprovedNot')
        extracted_data = request.data.get('ExtractedData')
        remarks = request.data.get('remarks', '')
        
        print(f"Processing: version={current_version}, approved={approved}, type={type(approved)}")
        
        # Validate required data
        if extracted_data is None:
            return Response({"error": "ExtractedData is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert boolean/null to proper values
        if approved == 'true' or approved is True:
            approved = True
        elif approved == 'false' or approved is False:
            approved = False
        else:
            approved = None
            
        print(f"Normalized approved value: {approved}, type={type(approved)}")
        
        # Create or update the framework approval
        with transaction.atomic():
            # Determine the next version
            # Check if there's already a reviewer version for this framework
            latest_reviewer_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='r'
            ).order_by('-ApprovalId').first()
            
            if latest_reviewer_version:
                # Increment the existing reviewer version
                try:
                    version_num = int(latest_reviewer_version.Version[1:])
                    new_version = f'r{version_num + 1}'
                except ValueError:
                    new_version = 'r1'
            else:
                # First reviewer version
                new_version = 'r1'
            
            # Create a new approval record with the reviewer version
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=user_id,
                ReviewerId=reviewer_id,
                Version=new_version,
                ApprovedNot=approved
            )
            
            # Set approval date if approved
            if approved:
                new_approval.ApprovedDate = timezone.now().date()
                new_approval.save()
                
                logger.info(f"Framework {framework_id} approved by reviewer")
                # Update framework status
                framework.Status = 'Approved'
                # Set framework to Active or Scheduled based on StartDate
                from datetime import date
                today = date.today()
                print(f"DEBUG: Today's date: {today}")
                print(f"DEBUG: Framework StartDate: {framework.StartDate} (type: {type(framework.StartDate)})")
                
                if framework.StartDate and framework.StartDate > today:
                    framework.ActiveInactive = 'Scheduled'
                    print(f"DEBUG: Framework {framework_id} set to 'Scheduled' because StartDate {framework.StartDate} > today {today}")
                else:
                    framework.ActiveInactive = 'Active'
                    print(f"DEBUG: Framework {framework_id} set to 'Active' because StartDate {framework.StartDate} <= today {today} or StartDate is None")
                
                # Ensure CurrentVersion is preserved during approval
                # We do this by not touching the CurrentVersion field
                # or by setting it explicitly from the framework version record
                current_framework_version = FrameworkVersion.objects.filter(
                    FrameworkId=framework
                ).first()
                if current_framework_version:
                    print(f"Setting CurrentVersion to {current_framework_version.Version} for framework {framework_id}")
                    framework.CurrentVersion = current_framework_version.Version
                    
                    # Update all policies to have the same CurrentVersion
                    policies = Policy.objects.filter(FrameworkId=framework)
                    for policy in policies:
                        policy.CurrentVersion = str(float(current_framework_version.Version))
                        print(f"Setting CurrentVersion to {policy.CurrentVersion} for policy {policy.PolicyId}")
                        policy.save()
                
                # Update extracted data to reflect the active/scheduled status
                if extracted_data:
                    extracted_data['ActiveInactive'] = framework.ActiveInactive
                    extracted_data['Status'] = 'Approved'
                
                # Send notification to submitter about framework approval
                try:
                    notification_service = NotificationService()
                    submitter = Users.objects.get(UserId=user_id)
                    reviewer = Users.objects.get(UserId=reviewer_id)
                    approval_date = timezone.now().date().isoformat()
                    notification_data = {
                        'notification_type': 'frameworkFinalApproved',
                        'email': submitter.Email,
                        'email_type': 'gmail',
                        'template_data': [
                            submitter.UserName,
                            framework.FrameworkName,
                            reviewer.UserName,
                            approval_date
                        ]
                    }
                    notification_service.send_multi_channel_notification(notification_data)
                except Exception as notify_ex:
                    print(f"DEBUG: Error sending framework approval notification: {notify_ex}")
                
                # IMPORTANT: Deactivate previous versions of this framework
                print("\n--- STARTING PREVIOUS VERSION DEACTIVATION ---")
                
                previous_frameworks_deactivated = []
                
                # Method 1: Use the FrameworkVersion.PreviousVersionId relationship
                print("DEBUG: Method 1 - Using PreviousVersionId relationship")
                try:
                    # Get the version record for the current framework
                    current_framework_version = FrameworkVersion.objects.filter(
                        FrameworkId=framework
                    ).first()
                    
                    if current_framework_version:
                        print(f"DEBUG: Current framework {framework_id} has version record: ID={current_framework_version.VersionId}, Version={current_framework_version.Version}, PreviousVersionId={current_framework_version.PreviousVersionId}")
                        
                        # First, try using PreviousVersionId
                        if current_framework_version.PreviousVersionId:
                            try:
                                # Get the previous version record
                                previous_version = FrameworkVersion.objects.get(
                                    VersionId=current_framework_version.PreviousVersionId
                                )
                                
                                if previous_version and previous_version.FrameworkId:
                                    previous_framework_id = previous_version.FrameworkId.FrameworkId
                                    print(f"DEBUG: Previous version points to framework ID: {previous_framework_id}")
                                    
                                    previous_framework = previous_version.FrameworkId
                                    
                                    print(f"DEBUG: Previous framework {previous_framework_id} status before update: {previous_framework.ActiveInactive}")
                                    previous_framework.ActiveInactive = 'Inactive'
                                    # Make sure Status remains 'Approved' if it was already approved
                                    if previous_framework.Status == 'Approved':
                                        # Don't change the Status, leave it as 'Approved'
                                        print(f"DEBUG: Keeping Status 'Approved' for framework {previous_framework_id}")
                                    previous_framework.save()
                                    
                                    # Verify the update
                                    previous_framework.refresh_from_db()
                                    print(f"DEBUG: Previous framework {previous_framework_id} status after update: {previous_framework.ActiveInactive}, Status: {previous_framework.Status}")
                                    
                                    # Set all policies of the previous framework to inactive
                                    previous_policies = Policy.objects.filter(FrameworkId=previous_framework)
                                    for prev_policy in previous_policies:
                                        prev_policy.ActiveInactive = 'Inactive'
                                        # Don't change Status if it's already Approved
                                        if prev_policy.Status == 'Approved':
                                            print(f"DEBUG: Keeping Status 'Approved' for policy {prev_policy.PolicyId}")
                                        # Don't change CurrentVersion value
                                        print(f"DEBUG: Preserving CurrentVersion {prev_policy.CurrentVersion} for policy {prev_policy.PolicyId}")
                                        prev_policy.save()
                                    
                                    print(f"DEBUG: Using PreviousVersionId: Deactivated framework {previous_framework_id} and its {previous_policies.count()} policies")
                                    previous_frameworks_deactivated.append(int(previous_framework_id))
                            except FrameworkVersion.DoesNotExist:
                                print(f"DEBUG: Previous version record with ID {current_framework_version.PreviousVersionId} not found")
                    else:
                        print(f"DEBUG: No FrameworkVersion record found for framework {framework_id}")
                except Exception as e:
                    print(f"DEBUG: Error in Method 1: {str(e)}")
                
                # Method 2: Fallback method - direct check and update for frameworks with same identifier
                print("\nDEBUG: Method 2 - Fallback direct check for frameworks with same identifier")
                try:
                    # Get the identifier of the current framework
                    current_identifier = framework.Identifier
                    print(f"DEBUG: Current framework identifier: {current_identifier}")
                    
                    # Find all frameworks with this identifier except the current one
                    other_frameworks = Framework.objects.filter(
                        Identifier=current_identifier
                    ).exclude(FrameworkId=framework_id)
                    
                    print(f"DEBUG: Found {other_frameworks.count()} other frameworks with the same identifier")
                    
                    for other_framework in other_frameworks:
                        # Skip if already deactivated
                        if int(other_framework.FrameworkId) in previous_frameworks_deactivated:
                            print(f"DEBUG: Framework {other_framework.FrameworkId} already processed, skipping")
                            continue
                        
                        print(f"DEBUG: Framework {other_framework.FrameworkId} status before update: {other_framework.ActiveInactive}")
                        
                        # Set to inactive
                        other_framework.ActiveInactive = 'Inactive'
                        # Make sure Status remains 'Approved' if it was already approved
                        if other_framework.Status == 'Approved':
                            # Don't change the Status, leave it as 'Approved'
                            print(f"DEBUG: Keeping Status 'Approved' for framework {other_framework.FrameworkId}")
                        other_framework.save()
                        
                        # Verify the update
                        other_framework.refresh_from_db()
                        print(f"DEBUG: Framework {other_framework.FrameworkId} status after update: {other_framework.ActiveInactive}, Status: {other_framework.Status}")
                        
                        # Set all policies to inactive
                        other_policies = Policy.objects.filter(FrameworkId=other_framework)
                        for other_policy in other_policies:
                            other_policy.ActiveInactive = 'Inactive'
                            # Don't change Status if it's already Approved
                            if other_policy.Status == 'Approved':
                                print(f"DEBUG: Keeping Status 'Approved' for policy {other_policy.PolicyId}")
                            # Don't change CurrentVersion value
                            print(f"DEBUG: Preserving CurrentVersion {other_policy.CurrentVersion} for policy {other_policy.PolicyId}")
                            other_policy.save()
                        
                        print(f"DEBUG: By direct check: Deactivated framework {other_framework.FrameworkId} and its {other_policies.count()} policies")
                        previous_frameworks_deactivated.append(int(other_framework.FrameworkId))
                except Exception as e:
                    print(f"DEBUG: Error in Method 2: {str(e)}")
                
                # Log summary of what was deactivated
                print(f"\nDEBUG: Deactivated frameworks: {previous_frameworks_deactivated}")
                
                # Approve all policies and subpolicies associated with this framework
                policies = Policy.objects.filter(FrameworkId=framework)
                print(f"Approving {policies.count()} policies for framework {framework_id}")
                
                # Update all policies in the database
                for policy in policies:
                    policy.Status = 'Approved'
                    # Set policy to Active or Scheduled based on StartDate
                    from datetime import date
                    today = date.today()
                    print(f"DEBUG: Policy {policy.PolicyId} - Today: {today}, StartDate: {policy.StartDate} (type: {type(policy.StartDate)})")
                    
                    if policy.StartDate and policy.StartDate > today:
                        policy.ActiveInactive = 'Scheduled'
                        print(f"Set policy {policy.PolicyId} to Approved status and Scheduled status (StartDate: {policy.StartDate} > today: {today})")
                    else:
                        policy.ActiveInactive = 'Active'
                        print(f"Set policy {policy.PolicyId} to Approved status and Active status (StartDate: {policy.StartDate} <= today: {today} or None)")
                    
                    # 🔁 Patch to pull updated values from ExtractedData
                    for pol_data in extracted_data.get('policies', []):
                        if str(pol_data.get('PolicyId')) == str(policy.PolicyId):
                            policy.PolicyType = pol_data.get('PolicyType', '')
                            policy.PolicyCategory = pol_data.get('PolicyCategory', '')
                            policy.PolicySubCategory = pol_data.get('PolicySubCategory', '')
                            break

                    policy.save()
                    
                    # Update all subpolicies for this policy
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    for subpolicy in subpolicies:
                        subpolicy.Status = 'Approved'
                        subpolicy.save()
                        print(f"Set subpolicy {subpolicy.SubPolicyId} to Approved status")
                
                # Also update the status in the extracted data
                if 'policies' in extracted_data:
                    for policy_data in extracted_data['policies']:
                        policy_data['Status'] = 'Approved'
                        # Find the corresponding policy to get its updated ActiveInactive status
                        for policy in policies:
                            if str(policy.PolicyId) == str(policy_data.get('PolicyId')):
                                policy_data['ActiveInactive'] = policy.ActiveInactive
                                break
                        if 'subpolicies' in policy_data:
                            for subpolicy_data in policy_data['subpolicies']:
                                subpolicy_data['Status'] = 'Approved'
                    
                    # Update the extracted data in the approval record
                    new_approval.ExtractedData = extracted_data
                    new_approval.save()
                
                framework.save()
            elif approved is False:
                logger.info(f"Framework {framework_id} rejected by reviewer")
                # Update framework status if rejected
                framework.Status = 'Rejected'
                framework.save()
                
                # Also reject all policies in this framework
                # Get all policies for this framework
                policies = Policy.objects.filter(FrameworkId=framework)
                logger.info(f"Rejecting {policies.count()} policies associated with framework {framework_id}")
                
                for policy in policies:
                    # Update policy status to rejected
                    policy.Status = 'Rejected'
                    policy.save()
                    
                    # Create rejection entry in policy approval
                    policy_extracted_data = {
                        "PolicyName": policy.PolicyName,
                        "PolicyDescription": policy.PolicyDescription,
                        "Status": "Rejected",
                        "Scope": policy.Scope,
                        "Objective": policy.Objective,
                        "type": "policy",
                        "framework_rejection": True,
                        "rejection_reason": remarks or f'Framework was rejected',
                        "remarks": remarks
                    }
                    
                    # Get all subpolicies for this policy
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    
                    # Create subpolicies data
                    subpolicies_data = []
                    for subpolicy in subpolicies:
                        # Update subpolicy status to rejected
                        subpolicy.Status = 'Rejected'
                        subpolicy.save()
                        
                        subpolicy_data = {
                            "SubPolicyId": subpolicy.SubPolicyId,
                            "SubPolicyName": subpolicy.SubPolicyName,
                            "Identifier": subpolicy.Identifier,
                            "Description": subpolicy.Description,
                            "Status": "Rejected",
                            "approval": {
                                "approved": False,
                                "remarks": remarks or f'Subpolicy "{subpolicy.SubPolicyName}" was rejected'
                            }
                        }
                        subpolicies_data.append(subpolicy_data)
                    
                    # Add subpolicies to policy data
                    policy_extracted_data["subpolicies"] = subpolicies_data
                    
                    # Create policy approval record
                    PolicyApproval.objects.create(
                        PolicyId=policy,
                        ExtractedData=policy_extracted_data,
                        UserId=user_id,
                        ReviewerId=reviewer_id,
                        Version=get_next_policy_reviewer_version(policy),
                        ApprovedNot=False  # Rejected
                    )
                # Send notification to submitter about framework rejection
                try:
                    notification_service = NotificationService()
                    submitter = Users.objects.get(UserId=user_id)
                    reviewer = Users.objects.get(UserId=reviewer_id)
                    notification_data = {
                        'notification_type': 'frameworkRejected',
                        'email': submitter.Email,
                        'email_type': 'gmail',
                        'template_data': [
                            submitter.UserName,
                            framework.FrameworkName,
                            reviewer.UserName,
                            remarks or 'Framework was rejected'
                        ]
                    }
                    notification_service.send_multi_channel_notification(notification_data)
                except Exception as notify_ex:
                    print(f"DEBUG: Error sending framework rejection notification: {notify_ex}")
            
            logger.info(f"Framework review submitted successfully for framework {framework_id}, approval status: {approved}")
            send_log(
                module="Framework",
                actionType="SUBMIT_REVIEW_SUCCESS",
                description=f"Framework review submitted successfully for framework '{framework.FrameworkName}', approval status: {approved}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="FrameworkApproval",
                entityId=new_approval.ApprovalId,
                ipAddress=get_client_ip(request),
                additionalInfo={
                    "framework_id": framework_id,
                    "framework_name": framework.FrameworkName,
                    "approved": approved,
                    "approval_id": new_approval.ApprovalId,
                    "version": new_approval.Version
                }
            )
            
            return Response({
                "message": "Framework review submitted successfully",
                "ApprovalId": new_approval.ApprovalId,
                "Version": new_approval.Version,
                "ApprovedNot": new_approval.ApprovedNot,
                "ApprovedDate": new_approval.ApprovedDate.isoformat() if new_approval.ApprovedDate else None
            }, status=status.HTTP_200_OK)
            
    except Framework.DoesNotExist:
        logger.error(f"Framework not found with ID: {framework_id}")
        send_log(
            module="Framework",
            actionType="SUBMIT_REVIEW_FAILED",
            description=f"Framework review submission failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error submitting framework review for framework {framework_id}: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="SUBMIT_REVIEW_FAILED",
            description=f"Framework review submission failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # RBAC: Require PolicyViewPermission for getting latest framework approval
def get_latest_framework_approval(request, framework_id):
    """
    Get the latest approval for a framework
    """
    try:
        # Get the latest approval by created date
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework_id
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            return Response({"message": "No approvals found for this framework"}, status=status.HTTP_404_NOT_FOUND)
        
        approval_data = {
            "ApprovalId": latest_approval.ApprovalId,
            "FrameworkId": latest_approval.FrameworkId.FrameworkId if latest_approval.FrameworkId else None,
            "ExtractedData": latest_approval.ExtractedData,
            "UserId": latest_approval.UserId,
            "ReviewerId": latest_approval.ReviewerId,
            "Version": latest_approval.Version,
            "ApprovedNot": latest_approval.ApprovedNot,
            "ApprovedDate": latest_approval.ApprovedDate.isoformat() if latest_approval.ApprovedDate else None
        }
        
        return Response(approval_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny]) # RBAC: Require PolicyApprovalWorkflowPermission for approving/rejecting subpolicies in framework
def approve_reject_subpolicy_in_framework(request, framework_id, policy_id, subpolicy_id):
    """
    Approve or reject a specific subpolicy within a framework approval process
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Get the latest framework approval
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            return Response({"error": "No framework approval found"}, status=status.HTTP_404_NOT_FOUND)
        
        approved = request.data.get('approved', None)  # True for approve, False for reject
        rejection_reason = request.data.get('rejection_reason', '')
        submit_review = request.data.get('submit_review', False)  # New flag to submit review immediately
        
        if approved is None:
            return Response({"error": "Approval status not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a copy of the extracted data for the new version
        extracted_data = latest_approval.ExtractedData.copy()
        
        # Find and update the subpolicy status in JSON
        policies = extracted_data.get('policies', [])
        policy_found = False
        subpolicy_found = False
        
        with transaction.atomic():
            for policy in policies:
                if str(policy.get('PolicyId')) == str(policy_id):
                    policy_found = True
                    subpolicies = policy.get('subpolicies', [])
                    
                    for subpolicy in subpolicies:
                        if str(subpolicy.get('SubPolicyId')) == str(subpolicy_id):
                            subpolicy_found = True
                            
                            # Update the actual SubPolicy record in database
                            try:
                                db_subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id)
                                db_policy = Policy.objects.get(PolicyId=policy_id)
                                db_framework = framework
                                submitter = Users.objects.get(UserId=latest_approval.UserId)
                                reviewer = Users.objects.get(UserId=latest_approval.ReviewerId)
                                notification_service = NotificationService()
                                
                                if approved:
                                    db_subpolicy.Status = 'Approved'
                                    subpolicy['Status'] = 'Approved'
                                    
                                    # Check if all subpolicies for this policy are approved
                                    all_subpolicies = SubPolicy.objects.filter(PolicyId=policy_id)
                                    all_approved = all(sp.Status == 'Approved' for sp in all_subpolicies)
                                    
                                    # If all subpolicies are approved, we can mark the policy as ready for approval
                                    if all_approved:
                                        db_policy.Status = 'Ready for Approval'
                                        db_policy.save()
                                        policy['Status'] = 'Ready for Approval'
                                    
                                    # Send notification to submitter about approval
                                    if submitter and reviewer:
                                        notification_data = {
                                            'notification_type': 'policyApproved',
                                            'email': submitter.Email,
                                            'email_type': 'gmail',
                                            'template_data': [
                                                submitter.UserName,
                                                db_policy.PolicyName,
                                                reviewer.UserName,
                                                db_framework.FrameworkName
                                            ]
                                        }
                                        notification_service.send_multi_channel_notification(notification_data)
                                else:
                                    db_subpolicy.Status = 'Rejected'
                                    subpolicy['Status'] = 'Rejected'
                                    
                                    # Also update the policy status in database
                                    db_policy.Status = 'Rejected'
                                    db_policy.save()
                                    policy['Status'] = 'Rejected'
                                    
                                    # Add rejection details to framework ExtractedData
                                    extracted_data['framework_approval'] = {
                                        'approved': False,
                                        'remarks': rejection_reason or f'Subpolicy "{subpolicy.get("SubPolicyName", "")}" was rejected',
                                        'rejected_by': 'Reviewer',
                                        'rejection_level': 'subpolicy',
                                        'rejected_item': f'Subpolicy: {subpolicy.get("SubPolicyName", "")}'
                                    }
                                    
                                    # Send notification to submitter about rejection
                                    if submitter and reviewer:
                                        notification_data = {
                                            'notification_type': 'policyRejected',
                                            'email': submitter.Email,
                                            'email_type': 'gmail',
                                            'template_data': [
                                                submitter.UserName,
                                                db_policy.PolicyName,
                                                reviewer.UserName,
                                                rejection_reason or f'Policy "{policy.get("PolicyName", "")}" was rejected'
                                            ]
                                        }
                                        notification_service.send_multi_channel_notification(notification_data)
                                    
                                    # If submit_review flag is true, submit the final review directly
                                    if submit_review:
                                        # Create a single reviewer version with rejection
                                        framework_approval = FrameworkApproval.objects.create(
                                            FrameworkId=framework,
                                            ExtractedData=extracted_data,
                                            UserId=latest_approval.UserId,
                                            ReviewerId=latest_approval.ReviewerId,
                                            ApprovedNot=False,  # Rejected
                                            Version=get_next_reviewer_version(framework)  # Use the helper function
                                        )
                                        
                                        # Update framework status to rejected
                                        framework.Status = 'Rejected'
                                        framework.save()
                                        
                                        return Response({
                                            "message": "Subpolicy rejected and review submitted successfully",
                                            "subpolicy_status": "Rejected",
                                            "framework_status": "Rejected",
                                            "ApprovalId": framework_approval.ApprovalId,
                                            "Version": framework_approval.Version
                                        }, status=status.HTTP_200_OK)
                                    else:
                                        # Create new reviewer version without final submission
                                        return create_reviewer_version(framework, extracted_data, latest_approval, False, rejection_reason)
                                
                                db_subpolicy.save()
                                
                            except SubPolicy.DoesNotExist:
                                return Response({"error": "SubPolicy not found in database"}, status=status.HTTP_404_NOT_FOUND)
                            
                            break
                    
                    if not approved:
                        break  # No need to continue if rejecting
            
            if not policy_found:
                return Response({"error": "Policy not found in framework"}, status=status.HTTP_404_NOT_FOUND)
            
            if not subpolicy_found:
                return Response({"error": "Subpolicy not found in policy"}, status=status.HTTP_404_NOT_FOUND)
            
            # If approved, just update the current approval
            latest_approval.ExtractedData = extracted_data
            latest_approval.save()
            
            return Response({
                "message": f"Subpolicy {'approved' if approved else 'rejected'} successfully",
                "subpolicy_status": "Approved" if approved else "Rejected"
            }, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])  # RBAC: Require PolicyApprovalWorkflowPermission for approving/rejecting policies in framework
def approve_reject_policy_in_framework(request, framework_id, policy_id):
    """
    Approve or reject a specific policy within a framework approval process
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Get the latest framework approval
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            return Response({"error": "No framework approval found"}, status=status.HTTP_404_NOT_FOUND)
        
        approved = request.data.get('approved', None)  # True for approve, False for reject
        rejection_reason = request.data.get('rejection_reason', '')
        submit_review = request.data.get('submit_review', False)  # New flag to submit review immediately
        
        if approved is None:
            return Response({"error": "Approval status not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a copy of the extracted data for the new version
        extracted_data = latest_approval.ExtractedData.copy()
        
        # Find and update the policy status in JSON
        policies = extracted_data.get('policies', [])
        policy_found = False
        
        with transaction.atomic():
            for policy in policies:
                if str(policy.get('PolicyId')) == str(policy_id):
                    policy_found = True
                    
                    # Prepare notification service and user info
                    notification_service = NotificationService()
                    try:
                        db_policy = Policy.objects.get(PolicyId=policy_id)
                        submitter = Users.objects.get(UserId=latest_approval.UserId)
                        reviewer = Users.objects.get(UserId=latest_approval.ReviewerId)
                    except Exception as user_ex:
                        print(f"Notification user lookup error: {user_ex}")
                        submitter = None
                        reviewer = None
                    now_str = timezone.now().strftime('%Y-%m-%d %H:%M')
                    
                    if approved:
                        # Check if all subpolicies are approved first
                        subpolicies = policy.get('subpolicies', [])
                        if subpolicies:
                            all_subpolicies_approved = all(sp.get('Status') == 'Approved' for sp in subpolicies)
                            if not all_subpolicies_approved:
                                return Response({
                                    "error": "All subpolicies must be approved before approving the policy"
                                }, status=status.HTTP_400_BAD_REQUEST)
                        
                        # Update the actual Policy record in database
                        try:
                            db_policy.Status = 'Approved'
                            db_policy.save()
                            policy['Status'] = 'Approved'
                            
                            # Check if all policies are approved to update framework status
                            all_policies_approved = all(p.get('Status') == 'Approved' for p in policies)
                            if all_policies_approved:
                                extracted_data['Status'] = 'Ready for Final Approval'
                            
                            # Send notification to submitter about approval
                            if submitter and reviewer:
                                notification_data = {
                                    'notification_type': 'policyApproved',
                                    'email': submitter.Email,
                                    'email_type': 'gmail',
                                    'template_data': [
                                        submitter.UserName,
                                        db_policy.PolicyName,
                                        reviewer.UserName,
                                        now_str
                                    ]
                                }
                                notification_service.send_multi_channel_notification(notification_data)
                        except Policy.DoesNotExist:
                            return Response({"error": "Policy not found in database"}, status=status.HTTP_404_NOT_FOUND)
                        
                    else:
                        # Update the actual Policy record in database
                        try:
                            db_policy.Status = 'Rejected'
                            db_policy.save()
                            policy['Status'] = 'Rejected'
                            
                            # Reject all subpolicies in this policy
                            subpolicies_in_db = SubPolicy.objects.filter(PolicyId=policy_id)
                            for sp_db in subpolicies_in_db:
                                sp_db.Status = 'Rejected'
                                sp_db.save()
                            
                            subpolicies = policy.get('subpolicies', [])
                            for subpolicy in subpolicies:
                                subpolicy['Status'] = 'Rejected'
                            
                            # Reject entire framework
                            framework.Status = 'Rejected'
                            framework.save()
                            extracted_data['Status'] = 'Rejected'
                            
                            # Add rejection details
                            extracted_data['framework_approval'] = {
                                'approved': False,
                                'remarks': rejection_reason or f'Policy "{policy.get("PolicyName", "")}" was rejected',
                                'rejected_by': 'Reviewer',
                                'rejection_level': 'policy',
                                'rejected_item': f'Policy: {policy.get("PolicyName", "")}'
                            }
                            
                            # Send notification to submitter about rejection
                            if submitter and reviewer:
                                notification_data = {
                                    'notification_type': 'policyRejected',
                                    'email': submitter.Email,
                                    'email_type': 'gmail',
                                    'template_data': [
                                        submitter.UserName,
                                        db_policy.PolicyName,
                                        reviewer.UserName,
                                        rejection_reason or f'Policy "{policy.get("PolicyName", "")}" was rejected'
                                    ]
                                }
                                notification_service.send_multi_channel_notification(notification_data)
                            
                            # If submit_review flag is true, submit the final review directly
                            if submit_review:
                                # Create a single reviewer version with rejection
                                framework_approval = FrameworkApproval.objects.create(
                                    FrameworkId=framework,
                                    ExtractedData=extracted_data,
                                    UserId=latest_approval.UserId,
                                    ReviewerId=latest_approval.ReviewerId,
                                    ApprovedNot=False,  # Rejected
                                    Version=get_next_reviewer_version(framework)  # Use the helper function
                                )
                                
                                # Update framework status to rejected
                                framework.Status = 'Rejected'
                                framework.save()
                                
                                return Response({
                                    "message": "Policy rejected and review submitted successfully",
                                    "policy_status": "Rejected",
                                    "framework_status": "Rejected",
                                    "ApprovalId": framework_approval.ApprovalId,
                                    "Version": framework_approval.Version
                                }, status=status.HTTP_200_OK)
                            else:
                                # Create new reviewer version without final submission
                                return create_reviewer_version(framework, extracted_data, latest_approval, False, rejection_reason)
                        
                        except Policy.DoesNotExist:
                            return Response({"error": "Policy not found in database"}, status=status.HTTP_404_NOT_FOUND)
                    
                    break
            
            if not policy_found:
                return Response({"error": "Policy not found in framework"}, status=status.HTTP_404_NOT_FOUND)
            
            # If approved, just update the current approval
            latest_approval.ExtractedData = extracted_data
            latest_approval.save()
            
            return Response({
                "message": f"Policy {'approved' if approved else 'rejected'} successfully",
                "policy_status": "Approved" if approved else "Rejected"
            }, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])  # RBAC: Require PolicyApprovalWorkflowPermission for final framework approval
def approve_entire_framework_final(request, framework_id):
    """
    Final approval of entire framework after all policies are approved
    """
    try:
        print(f"\n\n==== DEBUG: Starting approve_entire_framework_final for framework ID: {framework_id} ====")
        framework = Framework.objects.get(FrameworkId=framework_id)
        print(f"DEBUG: Found framework: {framework.FrameworkName} (ID: {framework.FrameworkId}), Status: {framework.Status}, ActiveInactive: {framework.ActiveInactive}")
        
        # Get the latest framework approval
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            return Response({"error": "No framework approval found"}, status=status.HTTP_404_NOT_FOUND)
        
        extracted_data = latest_approval.ExtractedData.copy()
        policies = extracted_data.get('policies', [])
        
        # Verify all policies are approved
        if not all(p.get('Status') == 'Approved' for p in policies):
            return Response({
                "error": "All policies must be approved before final framework approval"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Update framework status in database
            framework.Status = 'Approved'
            # Set framework to Active or Scheduled based on StartDate
            from datetime import date
            today = date.today()
            print(f"DEBUG: Today's date: {today}")
            print(f"DEBUG: Framework StartDate: {framework.StartDate} (type: {type(framework.StartDate)})")
            
            if framework.StartDate and framework.StartDate > today:
                framework.ActiveInactive = 'Scheduled'
                print(f"DEBUG: Framework {framework_id} set to 'Scheduled' because StartDate {framework.StartDate} > today {today}")
            else:
                framework.ActiveInactive = 'Active'
                print(f"DEBUG: Framework {framework_id} set to 'Active' because StartDate {framework.StartDate} <= today {today} or StartDate is None")
            
            # Ensure CurrentVersion is set correctly from the FrameworkVersion record
            current_framework_version = FrameworkVersion.objects.filter(
                FrameworkId=framework
            ).first()
            if current_framework_version:
                print(f"DEBUG: Setting CurrentVersion to {current_framework_version.Version} for framework {framework_id}")
                framework.CurrentVersion = current_framework_version.Version
                
                # Update all policies to have the same CurrentVersion
                policies_db = Policy.objects.filter(FrameworkId=framework)
                for policy in policies_db:
                    policy.CurrentVersion = str(float(current_framework_version.Version))
                    # Set policy status to Approved and ActiveInactive based on StartDate
                    policy.Status = 'Approved'
                    from datetime import date
                    today = date.today()
                    print(f"DEBUG: Policy {policy.PolicyId} - Today: {today}, StartDate: {policy.StartDate} (type: {type(policy.StartDate)})")
                    
                    if policy.StartDate and policy.StartDate > today:
                        policy.ActiveInactive = 'Scheduled'
                        print(f"DEBUG: Setting policy {policy.PolicyId} to Status='Approved', ActiveInactive='Scheduled' (StartDate: {policy.StartDate} > today: {today})")
                    else:
                        policy.ActiveInactive = 'Active'
                        print(f"DEBUG: Setting policy {policy.PolicyId} to Status='Approved', ActiveInactive='Active' (StartDate: {policy.StartDate} <= today: {today} or None)")
                    policy.save()
            
            framework.save()
            print(f"DEBUG: Updated framework {framework_id} status to 'Approved'")
            
            # Update all policies in the JSON data as well
            for policy_data in policies:
                policy_data['Status'] = 'Approved'
                # Find the corresponding policy to get its updated ActiveInactive status
                for policy in policies_db:
                    if str(policy.PolicyId) == str(policy_data.get('PolicyId')):
                        policy_data['ActiveInactive'] = policy.ActiveInactive
                        break
            
            # Also update all related SubPolicies to be Approved
            for policy in policies_db:
                subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                for subpolicy in subpolicies:
                    subpolicy.Status = 'Approved'
                    subpolicy.save()
                    print(f"DEBUG: Set subpolicy {subpolicy.SubPolicyId} to Status='Approved'")
            
            # Now deactivate any previous frameworks with the same identifier
            previous_frameworks_deactivated = []
            
            # Method 1: Check if there's a previous version record for this framework
            try:
                latest_version = FrameworkVersion.objects.filter(
                    FrameworkId=framework
                ).order_by('-Version').first()
                
                if latest_version and latest_version.PreviousVersionId:
                    previous_framework_id = latest_version.PreviousVersionId
                    print(f"DEBUG: Found previous framework version: {previous_framework_id}")
                    
                    try:
                        previous_version = FrameworkVersion.objects.get(FrameworkId=previous_framework_id)
                        previous_framework = previous_version.FrameworkId
                        
                        print(f"DEBUG: Previous framework {previous_framework_id} status before update: {previous_framework.ActiveInactive}")
                        previous_framework.ActiveInactive = 'Inactive'
                        # Make sure Status remains 'Approved' if it was already approved
                        if previous_framework.Status == 'Approved':
                            # Don't change the Status, leave it as 'Approved'
                            print(f"DEBUG: Keeping Status 'Approved' for framework {previous_framework_id}")
                        previous_framework.save()
                        
                        # Verify the update
                        previous_framework.refresh_from_db()
                        print(f"DEBUG: Previous framework {previous_framework_id} status after update: {previous_framework.ActiveInactive}, Status: {previous_framework.Status}")
                        
                        # Set all policies of the previous framework to inactive
                        previous_policies = Policy.objects.filter(FrameworkId=previous_framework)
                        for previous_policy in previous_policies:
                            previous_policy.ActiveInactive = 'Inactive'
                            # Don't change Status if it's already Approved
                            if previous_policy.Status == 'Approved':
                                print(f"DEBUG: Keeping Status 'Approved' for policy {previous_policy.PolicyId}")
                            # Don't change CurrentVersion value
                            print(f"DEBUG: Preserving CurrentVersion {previous_policy.CurrentVersion} for policy {previous_policy.PolicyId}")
                            previous_policy.save()
                        
                        previous_frameworks_deactivated.append(int(previous_framework_id))
                        print(f"DEBUG: Deactivated previous framework {previous_framework_id} and its {previous_policies.count()} policies")
                    except Exception as e:
                        print(f"DEBUG: Error in Method 1: {str(e)}")
            except Exception as e:
                print(f"DEBUG: Error in Method 1 (outer): {str(e)}")
            
            # Method 2: Use the identifier field to find other frameworks
            try:
                # Get the identifier of the current framework
                current_identifier = framework.Identifier
                print(f"DEBUG: Current framework identifier: {current_identifier}")
                
                # Find all frameworks with this identifier except the current one
                other_frameworks = Framework.objects.filter(
                    Identifier=current_identifier
                ).exclude(FrameworkId=framework_id)
                
                print(f"DEBUG: Found {other_frameworks.count()} other frameworks with the same identifier")
                
                for other_framework in other_frameworks:
                    # Skip if already deactivated
                    if int(other_framework.FrameworkId) in previous_frameworks_deactivated:
                        print(f"DEBUG: Framework {other_framework.FrameworkId} already processed, skipping")
                        continue
                    
                    print(f"DEBUG: Framework {other_framework.FrameworkId} status before update: {other_framework.ActiveInactive}")
                    
                    # Set to inactive
                    other_framework.ActiveInactive = 'Inactive'
                    # Make sure Status remains 'Approved' if it was already approved
                    if other_framework.Status == 'Approved':
                        # Don't change the Status, leave it as 'Approved'
                        print(f"DEBUG: Keeping Status 'Approved' for framework {other_framework.FrameworkId}")
                    other_framework.save()
                    
                    # Verify the update
                    other_framework.refresh_from_db()
                    print(f"DEBUG: Framework {other_framework.FrameworkId} status after update: {other_framework.ActiveInactive}, Status: {other_framework.Status}")
                    
                    # Set all policies to inactive
                    other_policies = Policy.objects.filter(FrameworkId=other_framework)
                    for other_policy in other_policies:
                        other_policy.ActiveInactive = 'Inactive'
                        # Don't change Status if it's already Approved
                        if other_policy.Status == 'Approved':
                            print(f"DEBUG: Keeping Status 'Approved' for policy {other_policy.PolicyId}")
                        # Don't change CurrentVersion value
                        print(f"DEBUG: Preserving CurrentVersion {other_policy.CurrentVersion} for policy {other_policy.PolicyId}")
                        other_policy.save()
                    
                    print(f"DEBUG: By direct check: Deactivated framework {other_framework.FrameworkId} and its {other_policies.count()} policies")
                    previous_frameworks_deactivated.append(int(other_framework.FrameworkId))
            except Exception as e:
                print(f"DEBUG: Error in Method 2: {str(e)}")
            
            # Log summary of what was deactivated
            print(f"\nDEBUG: Deactivated frameworks: {previous_frameworks_deactivated}")
            
            # Approve all policies and subpolicies associated with this framework
            policies = Policy.objects.filter(FrameworkId=framework)
            print(f"Approving {policies.count()} policies for framework {framework_id}")
            
            # Update all policies in the database
            for policy in policies:
                policy.Status = 'Approved'
                # Set policy to Active or Scheduled based on StartDate
                today = timezone.now().date()
                if policy.StartDate and policy.StartDate > today:
                    policy.ActiveInactive = 'Scheduled'
                    print(f"Set policy {policy.PolicyId} to Approved status and Scheduled status (StartDate: {policy.StartDate})")
                else:
                    policy.ActiveInactive = 'Active'
                    print(f"Set policy {policy.PolicyId} to Approved status and Active status (StartDate: {policy.StartDate})")
                policy.save()
                
                # Update all subpolicies for this policy
                subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                for subpolicy in subpolicies:
                    subpolicy.Status = 'Approved'
                    subpolicy.save()
                    print(f"Set subpolicy {subpolicy.SubPolicyId} to Approved status")
            
            # Also update the status in the extracted data
            if 'policies' in extracted_data:
                for policy_data in extracted_data['policies']:
                    policy_data['Status'] = 'Approved'
                    # Find the corresponding policy to get its updated ActiveInactive status
                    for policy in policies:
                        if str(policy.PolicyId) == str(policy_data.get('PolicyId')):
                            policy_data['ActiveInactive'] = policy.ActiveInactive
                            break
                    if 'subpolicies' in policy_data:
                        for subpolicy_data in policy_data['subpolicies']:
                            subpolicy_data['Status'] = 'Approved'
                
                # Update the extracted data in the approval record
                latest_approval.ExtractedData = extracted_data
                latest_approval.save()
            
            # Send notification to submitter about final framework approval
            try:
                notification_service = NotificationService()
                submitter = Users.objects.get(UserId=latest_approval.UserId)
                reviewer = Users.objects.get(UserId=latest_approval.ReviewerId)
                approval_date = timezone.now().date().isoformat()
                notification_data = {
                    'notification_type': 'frameworkFinalApproved',
                    'email': submitter.Email,
                    'email_type': 'gmail',
                    'template_data': [
                        submitter.UserName,
                        framework.FrameworkName,
                        reviewer.UserName,
                        approval_date
                    ]
                }
                notification_service.send_multi_channel_notification(notification_data)
            except Exception as notify_ex:
                print(f"DEBUG: Error sending framework final approval notification: {notify_ex}")
            
            extracted_data['framework_approval'] = {
                'approved': True,
                'remarks': 'Framework approved successfully',
                'approved_by': 'Reviewer',
                'approval_date': timezone.now().date().isoformat()
            }
            
            print("\n==== DEBUG: Completed framework approval process ====\n")
            
            # Create new reviewer version for final approval
            return create_reviewer_version(framework, extracted_data, latest_approval, True, 'Framework approved successfully')
        
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"DEBUG: Unhandled exception in approve_entire_framework_final: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_reviewer_version(framework, extracted_data, latest_approval, approved, remarks):
    """
    Helper function to create a new reviewer version of framework approval
    """
    try:
        with transaction.atomic():
            # Determine the next reviewer version using the helper function
            new_version = get_next_reviewer_version(framework)
            
            # Create a new approval record with the reviewer version
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=latest_approval.UserId,
                ReviewerId=latest_approval.ReviewerId,
                Version=new_version,
                ApprovedNot=approved
            )
            
            # Set approval/rejection date
            if approved:
                # Set the approval date to current date
                new_approval.ApprovedDate = timezone.now().date()
                
                # Update framework status
                if framework.ActiveInactive == 'Inactive':
                    framework.Status = 'Inactive'
                else:
                    framework.Status = 'Approved'
                
                # Ensure all policies and subpolicies are approved in the extracted data
                if 'policies' in extracted_data:
                    for policy_data in extracted_data['policies']:
                        policy_data['Status'] = 'Approved'
                        if 'subpolicies' in policy_data:
                            for subpolicy_data in policy_data['subpolicies']:
                                subpolicy_data['Status'] = 'Approved'
                
                # Update the extracted data in the approval record
                new_approval.ExtractedData = extracted_data
                
                framework.save()
            else:
                # Update framework status to rejected
                framework.Status = 'Rejected'
                framework.save()
            
            # Save the approval record with the date
            new_approval.save()
            
            return Response({
                "message": f"Framework {'approved' if approved else 'rejected'} successfully",
                "ApprovalId": new_approval.ApprovalId,
                "Version": new_approval.Version,
                "ApprovedNot": new_approval.ApprovedNot,
                "framework_status": "Approved" if approved else "Rejected",
                "ApprovedDate": new_approval.ApprovedDate.isoformat() if new_approval.ApprovedDate else None
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({"error": f"Error creating reviewer version: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # RBAC: Require PolicyViewPermission for viewing rejected frameworks
def get_rejected_frameworks_for_user(request, framework_id=None, user_id=None):
    """
    Get all rejected frameworks for a specific user that can be edited and resubmitted
    Note: framework_id parameter is ignored - it's only in URL for consistency
    """
    try:
        if not user_id:
            user_id = request.GET.get('user_id', 1)  # Default user
            
        # Get all frameworks with rejected status
        rejected_frameworks = Framework.objects.filter(Status='Rejected')
        
        # Find the latest approval for each rejected framework
        rejected_framework_data = []
        
        for framework in rejected_frameworks:
            # Get the latest approval for this framework
            latest_approval = FrameworkApproval.objects.filter(
                FrameworkId=framework.FrameworkId,
                ApprovedNot=False  # Must be rejected
            ).order_by('-ApprovalId').first()
            
            if latest_approval:
                framework_data = {
                    "ApprovalId": latest_approval.ApprovalId,
                    "FrameworkId": framework.FrameworkId,
                    "ExtractedData": latest_approval.ExtractedData,
                    "Version": latest_approval.Version,
                    "ApprovedNot": latest_approval.ApprovedNot,
                    "rejection_reason": latest_approval.ExtractedData.get('framework_approval', {}).get('remarks', 'No reason provided'),
                    "created_at": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None
                }
                rejected_framework_data.append(framework_data)
        
        return Response(rejected_framework_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # RBAC: Require PolicyEditPermission for requesting framework status changes
def request_framework_status_change(request, framework_id):
    """
    Request approval for changing a framework's status from Active to Inactive
    Creates a framework approval entry that needs to be approved by a reviewer
    """
    logger.info(f"Framework status change request for framework ID: {framework_id}")
    send_log(
        module="Framework",
        actionType="REQUEST_STATUS_CHANGE",
        description=f"Framework status change request for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    try:
        print(f"DEBUG: request_framework_status_change called for framework_id: {framework_id}")
        print(f"DEBUG: Request data: {request.data}")
        logger.debug(f"Request data received: {request.data}")
        
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        logger.info(f"Found framework: {framework.FrameworkName}, Status: {framework.Status}, ActiveInactive: {framework.ActiveInactive}")
        print(f"DEBUG: Found framework: {framework.FrameworkName}, Status: {framework.Status}, ActiveInactive: {framework.ActiveInactive}")
        
        # Check if framework is active
        if framework.ActiveInactive != 'Active':
            return Response({"error": "Only Active frameworks can be submitted for status change approval"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Extract data for the approval
        user_id = request.data.get('UserId', 1)  # Default to 1 if not provided
        reviewer_id = request.data.get('ReviewerId', 2)  # Default to 2
        print(f"DEBUG: UserId: {user_id}, ReviewerId: {reviewer_id}")
        
        reviewer_email = None
        if reviewer_id:
            try:
                reviewer_user = Users.objects.get(UserId=reviewer_id)
                reviewer_email = reviewer_user.Email
                print(f"DEBUG: Found reviewer: {reviewer_user.UserName} ({reviewer_email})")
            except Users.DoesNotExist:
                print(f"DEBUG: Reviewer with ID {reviewer_id} not found")
        
        reason = request.data.get('reason', 'No reason provided')
        print(f"DEBUG: Reason: {reason}")
        
        # Collect policies and subpolicies data for approval JSON
        policies_data = []
        created_policies = Policy.objects.filter(FrameworkId=framework)
        
        for policy in created_policies:
            policy_dict = {
                "PolicyId": policy.PolicyId,
                "PolicyName": policy.PolicyName,
                "PolicyDescription": policy.PolicyDescription,
                "Status": policy.Status,
                "StartDate": policy.StartDate.isoformat() if policy.StartDate else None,
                "EndDate": policy.EndDate.isoformat() if policy.EndDate else None,
                "Department": policy.Department,
                "CreatedByName": policy.CreatedByName,
                "CreatedByDate": policy.CreatedByDate.isoformat() if policy.CreatedByDate else None,
                "Applicability": policy.Applicability,
                "DocURL": policy.DocURL,
                "Scope": policy.Scope,
                "Objective": policy.Objective,
                "Identifier": policy.Identifier,
                "PermanentTemporary": policy.PermanentTemporary,
                "ActiveInactive": policy.ActiveInactive,
                "Reviewer": policy.Reviewer,
                "CoverageRate": policy.CoverageRate,
                "CurrentVersion": policy.CurrentVersion,
                "subpolicies": []
            }
            
            # Get subpolicies for this policy
            subpolicies = SubPolicy.objects.filter(PolicyId=policy)
            for subpolicy in subpolicies:
                subpolicy_dict = {
                    "SubPolicyId": subpolicy.SubPolicyId,
                    "SubPolicyName": subpolicy.SubPolicyName,
                    "CreatedByName": subpolicy.CreatedByName,
                    "CreatedByDate": subpolicy.CreatedByDate.isoformat() if subpolicy.CreatedByDate else None,
                    "Identifier": subpolicy.Identifier,
                    "Description": subpolicy.Description,
                    "Status": subpolicy.Status,
                    "PermanentTemporary": subpolicy.PermanentTemporary,
                    "Control": subpolicy.Control
                }
                policy_dict["subpolicies"].append(subpolicy_dict)
            
            policies_data.append(policy_dict)
        
        extracted_data = {
            "FrameworkName": framework.FrameworkName,
            "FrameworkDescription": framework.FrameworkDescription,
            "Category": framework.Category,
            "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
            "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
            "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
            "CreatedByName": framework.CreatedByName,
            "CreatedByDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
            "Identifier": framework.Identifier,
            "Status": framework.Status,
            "ActiveInactive": framework.ActiveInactive,
            "InternalExternal": framework.InternalExternal,
            "type": "framework",
            "docURL": framework.DocURL,
            "reviewer": framework.Reviewer,
            "source": "status_change_request",
            "request_type": "status_change",
            "requested_status": "Inactive",
            "current_status": "Active",
            "reason_for_change": reason,
            "requested_date": timezone.now().date().isoformat(),
            "policies": policies_data,
            "totalPolicies": len(policies_data),
            "totalSubpolicies": sum(len(p["subpolicies"]) for p in policies_data),
            "cascade_to_policies": request.data.get('cascadeToApproved', True)
        }
        
        with transaction.atomic():
            # Update framework status to Under Review
            framework.Status = 'Under Review'
            framework.save()
            
            # Determine the next user version
            latest_user_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='u'
            ).order_by('-ApprovalId').first()
            
            if latest_user_version:
                try:
                    version_num = int(latest_user_version.Version[1:])
                    new_version = f'u{version_num + 1}'
                except ValueError:
                    new_version = 'u1'
            else:
                new_version = 'u1'  # First approval
            
            # Create the framework approval
            framework_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=user_id,
                ReviewerId=reviewer_id,
                Version=new_version,
                ApprovedNot=None  # Not yet approved
            )
            print(f"DEBUG: Created FrameworkApproval with ID: {framework_approval.ApprovalId}, Version: {new_version}, ReviewerId: {reviewer_id}")
            
            # Send notification to reviewer if email is available
            if 'reviewer_email' not in locals():
                reviewer_email = None
                if reviewer_id:
                    try:
                        reviewer_user = Users.objects.get(UserId=reviewer_id)
                        reviewer_email = reviewer_user.Email
                        print(f"DEBUG: Sending notification to reviewer: {reviewer_user.UserName} ({reviewer_email})")
                    except Users.DoesNotExist:
                        print(f"DEBUG: Could not find reviewer with ID {reviewer_id} for notification")
            
            if reviewer_email:
                print(f"DEBUG: Attempting to send notification to {reviewer_email}")
                notification_service = NotificationService()
                notification_data = {
                    'notification_type': 'frameworkInactiveRequested',
                    'email': reviewer_email,
                    'email_type': 'gmail',
                    'template_data': [
                        framework.FrameworkName,
                        reviewer_user.UserName if 'reviewer_user' in locals() else 'Unknown',
                        framework.CreatedByName,
                        reason
                    ]
                }
                notification_result = notification_service.send_multi_channel_notification(notification_data)
                print(f"DEBUG: Framework inactivation notification result: {notification_result}")
            else:
                print("DEBUG: No reviewer email found, skipping notification")
        
        logger.info(f"Framework status change request submitted successfully for framework {framework_id}")
        send_log(
            module="Framework",
            actionType="REQUEST_STATUS_CHANGE_SUCCESS",
            description=f"Framework status change request submitted successfully for framework '{framework.FrameworkName}'",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            entityId=framework_approval.ApprovalId,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_id": framework_id,
                "framework_name": framework.FrameworkName,
                "approval_id": framework_approval.ApprovalId,
                "reviewer_id": reviewer_id,
                "reason": reason
            }
        )
        
        return Response({
            "message": "Framework status change request submitted successfully. Awaiting approval.",
            "ApprovalId": framework_approval.ApprovalId,
            "Version": framework_approval.Version,
            "Status": "Under Review",
            "ReviewerId": reviewer_id,
            "ReviewerEmail": reviewer_email if reviewer_email else None
        }, status=status.HTTP_201_CREATED)
        
    except Framework.DoesNotExist:
        logger.error(f"Framework not found with ID: {framework_id}")
        send_log(
            module="Framework",
            actionType="REQUEST_STATUS_CHANGE_FAILED",
            description=f"Framework status change request failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error requesting framework status change for framework {framework_id}: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="REQUEST_STATUS_CHANGE_FAILED",
            description=f"Framework status change request failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # RBAC: Require PolicyApprovePermission for approving framework status changes
def approve_framework_status_change(request, approval_id):
    """
    Approve or reject a framework status change request
    """
    logger.info(f"Framework status change approval attempt for approval ID: {approval_id}")
    send_log(
        module="Framework",
        actionType="APPROVE_STATUS_CHANGE",
        description=f"Framework status change approval attempt for approval ID: {approval_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    try:
        approval = FrameworkApproval.objects.get(ApprovalId=approval_id)
        framework = approval.FrameworkId
        logger.info(f"Found framework: {framework.FrameworkName} for status change approval")
        
        # Check if this is a status change request
        if approval.ExtractedData.get('request_type') != 'status_change':
            logger.warning(f"Approval {approval_id} is not a status change request")
            return Response({"error": "This is not a status change request"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get approval decision
        approved = request.data.get('approved', False)
        remarks = request.data.get('remarks', '')
        logger.info(f"Processing status change approval: approved={approved}, remarks={remarks}")
        
        with transaction.atomic():
            # Create a copy of the extracted data
            extracted_data = approval.ExtractedData.copy()
            
            if approved:
                logger.info(f"Approving status change for framework {framework.FrameworkId} to Inactive")
                # Change framework status to Inactive
                framework.ActiveInactive = 'Inactive'
                framework.Status = 'Approved'  # Also set Status field to Inactive
                framework.save()
                
                # Update extracted data
                extracted_data['ActiveInactive'] = 'Inactive'
                extracted_data['Status'] = 'Approved'
                extracted_data['status_change_approval'] = {
                    'approved': True,
                    'remarks': remarks or 'Status change approved',
                    'approved_by': 'Reviewer',
                    'approval_date': timezone.now().date().isoformat()
                }
                
                # Check if we should cascade to policies
                cascade_to_policies = extracted_data.get('cascade_to_policies', True)
                if cascade_to_policies:
                    # Get all policies for this framework (not just approved ones)
                    policies = Policy.objects.filter(
                        FrameworkId=framework
                    )
                    
                    # Update their status to Inactive
                    for policy in policies:
                        policy.ActiveInactive = 'Inactive'
                        policy.Status = 'Approved'  # Also set Status field to Inactive
                        policy.save()
                        
                        # Also update all subpolicies for this policy to Inactive
                        subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                        for subpolicy in subpolicies:
                            subpolicy.Status = 'Inactive'
                            subpolicy.save()
                        
                        # Update in extracted data
                        for policy_data in extracted_data.get('policies', []):
                            if policy_data.get('PolicyId') == policy.PolicyId:
                                policy_data['ActiveInactive'] = 'Inactive'
                                policy_data['Status'] = 'Approved'  # Also update Status in JSON
                                
                                # Update subpolicies in extracted data
                                for subpolicy_data in policy_data.get('subpolicies', []):
                                    subpolicy_data['Status'] = 'Approved'
            else:
                logger.info(f"Rejecting status change for framework {framework.FrameworkId}")
                # Reject status change request, revert framework status
                framework.Status = 'Approved'  # Reset from "Under Review"
                framework.save()
                
                # Update extracted data
                extracted_data['status_change_approval'] = {
                    'approved': False,
                    'remarks': remarks or 'Status change rejected',
                    'rejected_by': 'Reviewer',
                    'rejection_date': timezone.now().date().isoformat()
                }
            
            # Determine the next reviewer version
            latest_reviewer_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='r'
            ).order_by('-ApprovalId').first()
            
            if latest_reviewer_version:
                try:
                    version_num = int(latest_reviewer_version.Version[1:])
                    new_version = f'r{version_num + 1}'
                except ValueError:
                    new_version = 'r1'
            else:
                new_version = 'r1'
                
            # Create a new approval record with the reviewer version
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=approval.UserId,
                ReviewerId=approval.ReviewerId,
                Version=new_version,
                ApprovedNot=approved
            )
            
            # Set approval date if approved
            if approved:
                new_approval.ApprovedDate = timezone.now().date()
                new_approval.save()
            
            # Send notification to submitter about approval or rejection
            submitter_email = None
            submitter_name = framework.CreatedByName
            if submitter_name:
                submitter_user = Users.objects.filter(UserName=submitter_name).first()
                if submitter_user:
                    submitter_email = submitter_user.Email
            reviewer_name = None
            if approval.ReviewerId:
                reviewer_user = Users.objects.filter(UserId=approval.ReviewerId).first()
                if reviewer_user:
                    reviewer_name = reviewer_user.UserName
            if submitter_email and reviewer_name:
                notification_service = NotificationService()
                if approved:
                    notification_data = {
                        'notification_type': 'frameworkInactivationApproved',
                        'email': submitter_email,
                        'email_type': 'gmail',
                        'template_data': [
                            submitter_name,
                            framework.FrameworkName,
                            reviewer_name,
                            remarks or 'Status change approved'
                        ]
                    }
                else:
                    notification_data = {
                        'notification_type': 'frameworkInactivationRejected',
                        'email': submitter_email,
                        'email_type': 'gmail',
                        'template_data': [
                            framework.FrameworkName,
                            submitter_name,
                            reviewer_name,
                            remarks or 'Status change rejected'
                        ]
                    }
                notification_result = notification_service.send_multi_channel_notification(notification_data)
                print(f"Framework inactivation approval notification result: {notification_result}")
            
        logger.info(f"Framework status change {'approved' if approved else 'rejected'} successfully for approval {approval_id}")
        send_log(
            module="Framework",
            actionType="APPROVE_STATUS_CHANGE_SUCCESS",
            description=f"Framework status change {'approved' if approved else 'rejected'} successfully for framework '{framework.FrameworkName}'",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            entityId=new_approval.ApprovalId,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_id": framework.FrameworkId,
                "framework_name": framework.FrameworkName,
                "approved": approved,
                "approval_id": new_approval.ApprovalId,
                "remarks": remarks
            }
        )
        
        return Response({
            "message": f"Framework status change request {'approved' if approved else 'rejected'}",
            "ApprovalId": new_approval.ApprovalId,
            "Version": new_approval.Version,
            "ApprovedNot": approved,
            "framework_status": framework.Status,
            "framework_active_inactive": framework.ActiveInactive
        }, status=status.HTTP_200_OK)
        
    except FrameworkApproval.DoesNotExist:
        logger.error(f"Framework approval not found with ID: {approval_id}")
        send_log(
            module="Framework",
            actionType="APPROVE_STATUS_CHANGE_FAILED",
            description=f"Framework status change approval failed - approval not found (ID: {approval_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework approval not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error approving framework status change for approval {approval_id}: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="APPROVE_STATUS_CHANGE_FAILED",
            description=f"Framework status change approval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # RBAC: Require PolicyViewPermission for viewing status change requests
def get_status_change_requests(request):
    """
    Get all framework status change requests
    Include both pending and processed (approved/rejected) requests
    Group related approvals by framework name to ensure consistent status display
    """
    logger.info("Retrieving all framework status change requests")
    send_log(
        module="Framework",
        actionType="VIEW_STATUS_CHANGE_REQUESTS",
        description="Retrieving all framework status change requests",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkApproval",
        ipAddress=get_client_ip(request)
    )
    
    try:
        # Find all framework approvals with request_type=status_change
        status_change_requests = []
        framework_status_map = {}  # To track the latest status for each framework
        logger.debug("Starting framework status change requests retrieval")
        
        # Get all approvals, not just those with ApprovedNot=None
        approvals = FrameworkApproval.objects.filter().order_by('-ApprovalId')
        
        # First pass: Get the latest status for each framework
        for approval in approvals:
            # Check if the extracted data contains request_type=status_change
            if approval.ExtractedData.get('request_type') == 'status_change':
                framework = approval.FrameworkId
                framework_name = framework.FrameworkName
                
                # Only track the status if we haven't seen this framework before
                # or if this is a newer approval (with a higher ApprovalId)
                if framework_name not in framework_status_map:
                    framework_status_map[framework_name] = {
                        'status': approval.ApprovedNot,
                        'approvalId': approval.ApprovalId
                    }
        
        # Second pass: Create the request data with consistent status
        for approval in approvals:
            # Check if the extracted data contains request_type=status_change
            if approval.ExtractedData.get('request_type') == 'status_change':
                framework = approval.FrameworkId
                framework_name = framework.FrameworkName
                
                # Get the policies and subpolicies that would be affected if approved
                affected_policies = []
                total_subpolicies = 0
                if approval.ExtractedData.get('cascade_to_policies', True):
                    policies = Policy.objects.filter(
                        FrameworkId=framework
                    )
                    
                    for policy in policies:
                        # Count subpolicies for this policy
                        subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                        subpolicy_count = subpolicies.count()
                        total_subpolicies += subpolicy_count
                        
                        affected_policies.append({
                            'PolicyId': policy.PolicyId,
                            'PolicyName': policy.PolicyName,
                            'Department': policy.Department,
                            'Status': policy.Status,
                            'ActiveInactive': policy.ActiveInactive,
                            'Identifier': policy.Identifier,
                            'Description': policy.PolicyDescription[:100] + '...' if policy.PolicyDescription and len(policy.PolicyDescription) > 100 else policy.PolicyDescription,
                            'SubpolicyCount': subpolicy_count
                        })
                
                # Use the latest status for this framework from our map
                latest_status = framework_status_map.get(framework_name, {'status': None})['status']
                
                # Determine status based on the latest status for this framework
                approval_status = "Pending Approval"
                if latest_status is True:
                    approval_status = "Approved"
                elif latest_status is False:
                    approval_status = "Rejected"
                
                # Include any approval remarks
                approval_remarks = ""
                if approval.ExtractedData.get('status_change_approval'):
                    approval_remarks = approval.ExtractedData.get('status_change_approval').get('remarks', '')
                
                request_data = {
                    'ApprovalId': approval.ApprovalId,
                    'FrameworkId': framework.FrameworkId,
                    'FrameworkName': framework.FrameworkName,
                    'Category': framework.Category,
                    'RequestType': 'Change Status to Inactive',
                    'RequestDate': approval.ExtractedData.get('requested_date'),
                    'Reason': approval.ExtractedData.get('reason_for_change', 'No reason provided'),
                    'UserId': approval.UserId,
                    'ReviewerId': approval.ReviewerId,
                    'Version': approval.Version,
                    'Status': approval_status,
                    'ApprovedNot': latest_status,  # Use the latest status for consistency
                    'ApprovedDate': approval.ApprovedDate.isoformat() if approval.ApprovedDate else None,
                    'CascadeToApproved': approval.ExtractedData.get('cascade_to_policies', True),
                    'PolicyCount': len(affected_policies),
                    'SubpolicyCount': total_subpolicies,
                    'AffectedPolicies': affected_policies,
                    'Remarks': approval_remarks,
                    'IsLatestApproval': approval.ApprovalId == framework_status_map.get(framework_name, {'approvalId': None})['approvalId']
                }
                
                status_change_requests.append(request_data)
        
        logger.info(f"Successfully retrieved {len(status_change_requests)} framework status change requests")
        send_log(
            module="Framework",
            actionType="VIEW_STATUS_CHANGE_REQUESTS_SUCCESS",
            description=f"Successfully retrieved {len(status_change_requests)} framework status change requests",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            ipAddress=get_client_ip(request),
            additionalInfo={
                "requests_count": len(status_change_requests)
            }
        )
        
        return Response(status_change_requests, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving framework status change requests: {str(e)}")
        logger.error(traceback.format_exc())
        send_log(
            module="Framework",
            actionType="VIEW_STATUS_CHANGE_REQUESTS_FAILED",
            description=f"Framework status change requests retrieval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkApproval",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def update_existing_activeinactive_by_date(request):
    """
    Update existing approved frameworks and policies ActiveInactive status based on StartDate
    This is a utility function to fix existing data
    """
    try:
        from datetime import date
        today = date.today()
        print(f"DEBUG: Today's date for update: {today}")
        
        updated_frameworks = 0
        updated_policies = 0
        
        # Update approved frameworks
        approved_frameworks = Framework.objects.filter(Status='Approved')
        print(f"DEBUG: Found {approved_frameworks.count()} approved frameworks to check")
        
        for framework in approved_frameworks:
            old_status = framework.ActiveInactive
            print(f"DEBUG: Framework {framework.FrameworkId} - StartDate: {framework.StartDate}, Current ActiveInactive: {old_status}")
            
            if framework.StartDate and framework.StartDate > today:
                framework.ActiveInactive = 'Scheduled'
                framework.save()
                updated_frameworks += 1
                print(f"DEBUG: Updated Framework {framework.FrameworkId} from '{old_status}' to 'Scheduled' (StartDate: {framework.StartDate} > today: {today})")
            elif framework.StartDate and framework.StartDate <= today and old_status not in ['Active', 'Inactive']:
                framework.ActiveInactive = 'Active'
                framework.save()
                updated_frameworks += 1
                print(f"DEBUG: Updated Framework {framework.FrameworkId} from '{old_status}' to 'Active' (StartDate: {framework.StartDate} <= today: {today})")
        
        # Update approved policies
        approved_policies = Policy.objects.filter(Status='Approved')
        print(f"DEBUG: Found {approved_policies.count()} approved policies to check")
        
        for policy in approved_policies:
            old_status = policy.ActiveInactive
            print(f"DEBUG: Policy {policy.PolicyId} - StartDate: {policy.StartDate}, Current ActiveInactive: {old_status}")
            
            if policy.StartDate and policy.StartDate > today:
                policy.ActiveInactive = 'Scheduled'
                policy.save()
                updated_policies += 1
                print(f"DEBUG: Updated Policy {policy.PolicyId} from '{old_status}' to 'Scheduled' (StartDate: {policy.StartDate} > today: {today})")
            elif policy.StartDate and policy.StartDate <= today and old_status not in ['Active', 'Inactive']:
                policy.ActiveInactive = 'Active'
                policy.save()
                updated_policies += 1
                print(f"DEBUG: Updated Policy {policy.PolicyId} from '{old_status}' to 'Active' (StartDate: {policy.StartDate} <= today: {today})")
        
        return Response({
            "message": "Successfully updated ActiveInactive status based on StartDate",
            "updated_frameworks": updated_frameworks,
            "updated_policies": updated_policies,
            "today_date": today.isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR in update_existing_activeinactive_by_date: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users_for_reviewer_selection(request):
    """
    Get all users that can be selected as reviewers for framework status change requests
    """
    try:
        print("DEBUG: Fetching users for reviewer selection...")
        users = Users.objects.all().values('UserId', 'UserName', 'Email')
        users_list = list(users)
        print(f"DEBUG: Found {len(users_list)} users: {users_list}")
        
        # If no users found, create test users automatically
        if len(users_list) == 0:
            print("DEBUG: No users found, creating test users...")
            from datetime import datetime
            
            test_users = [
                {
                    'UserName': 'John Reviewer',
                    'Email': 'john.reviewer@company.com',
                    'Password': 'password123'
                },
                {
                    'UserName': 'Jane Approver', 
                    'Email': 'jane.approver@company.com',
                    'Password': 'password123'
                },
                {
                    'UserName': 'Bob Manager',
                    'Email': 'bob.manager@company.com', 
                    'Password': 'password123'
                }
            ]
            
            for user_data in test_users:
                user = Users.objects.create(
                    UserName=user_data['UserName'],
                    Email=user_data['Email'],
                    Password=user_data['Password'],
                    CreatedAt=datetime.now(),
                    UpdatedAt=datetime.now()
                )
                users_list.append({
                    'UserId': user.UserId,
                    'UserName': user.UserName,
                    'Email': user.Email
                })
            
            print(f"DEBUG: Created {len(test_users)} test users. Total users now: {len(users_list)}")
        
        return Response(users_list, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR: Failed to fetch users: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_status_change_requests_by_reviewer(request, reviewer_id=None):
    """
    Get framework status change requests filtered by reviewer
    """
    try:
        # If reviewer_id is provided, filter by that reviewer
        if reviewer_id:
            approvals = FrameworkApproval.objects.filter(
                ReviewerId=reviewer_id
            ).order_by('-ApprovalId')
        else:
            # Get all approvals if no reviewer specified
            approvals = FrameworkApproval.objects.all().order_by('-ApprovalId')
        
        status_change_requests = []
        framework_status_map = {}
        
        # First pass: Get the latest status for each framework
        for approval in approvals:
            if approval.ExtractedData.get('request_type') == 'status_change':
                framework = approval.FrameworkId
                framework_name = framework.FrameworkName
                
                if framework_name not in framework_status_map:
                    framework_status_map[framework_name] = {
                        'status': approval.ApprovedNot,
                        'approvalId': approval.ApprovalId
                    }
        
        # Second pass: Create the request data with consistent status
        for approval in approvals:
            if approval.ExtractedData.get('request_type') == 'status_change':
                framework = approval.FrameworkId
                framework_name = framework.FrameworkName
                
                # Get the policies that would be affected if approved
                affected_policies = []
                total_subpolicies = 0
                if approval.ExtractedData.get('cascade_to_policies', True):
                    policies = Policy.objects.filter(FrameworkId=framework)
                    
                    for policy in policies:
                        subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                        subpolicy_count = subpolicies.count()
                        total_subpolicies += subpolicy_count
                        
                        affected_policies.append({
                            'PolicyId': policy.PolicyId,
                            'PolicyName': policy.PolicyName,
                            'Department': policy.Department,
                            'Status': policy.Status,
                            'ActiveInactive': policy.ActiveInactive,
                            'SubpolicyCount': subpolicy_count
                        })
                
                latest_status = framework_status_map.get(framework_name, {'status': None})['status']
                
                approval_status = "Pending Approval"
                if latest_status is True:
                    approval_status = "Approved"
                elif latest_status is False:
                    approval_status = "Rejected"
                
                approval_remarks = ""
                if approval.ExtractedData.get('status_change_approval'):
                    approval_remarks = approval.ExtractedData.get('status_change_approval').get('remarks', '')
                
                # Get reviewer information
                reviewer_info = None
                if approval.ReviewerId:
                    try:
                        reviewer_user = Users.objects.get(UserId=approval.ReviewerId)
                        reviewer_info = {
                            'UserId': reviewer_user.UserId,
                            'UserName': reviewer_user.UserName,
                            'Email': reviewer_user.Email
                        }
                    except Users.DoesNotExist:
                        pass
                
                request_data = {
                    'ApprovalId': approval.ApprovalId,
                    'FrameworkId': framework.FrameworkId,
                    'FrameworkName': framework.FrameworkName,
                    'Category': framework.Category,
                    'RequestType': 'Change Status to Inactive',
                    'RequestDate': approval.ExtractedData.get('requested_date'),
                    'Reason': approval.ExtractedData.get('reason_for_change', 'No reason provided'),
                    'UserId': approval.UserId,
                    'ReviewerId': approval.ReviewerId,
                    'ReviewerInfo': reviewer_info,
                    'Version': approval.Version,
                    'Status': approval_status,
                    'ApprovedNot': latest_status,
                    'ApprovedDate': approval.ApprovedDate.isoformat() if approval.ApprovedDate else None,
                    'CascadeToApproved': approval.ExtractedData.get('cascade_to_policies', True),
                    'PolicyCount': len(affected_policies),
                    'SubpolicyCount': total_subpolicies,
                    'AffectedPolicies': affected_policies,
                    'Remarks': approval_remarks,
                    'IsLatestApproval': approval.ApprovalId == framework_status_map.get(framework_name, {'approvalId': None})['approvalId']
                }
                
                status_change_requests.append(request_data)
        
        return Response(status_change_requests, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_test_users(request):
    """
    Create test users for testing reviewer selection functionality
    This is a temporary endpoint for testing purposes
    """
    try:
        from datetime import datetime
        
        # Check if users already exist
        existing_users = Users.objects.count()
        if existing_users > 0:
            return Response({"message": f"Users already exist in database ({existing_users} users found)"}, status=status.HTTP_200_OK)
        
        # Create test users
        test_users = [
            {
                'UserName': 'John Reviewer',
                'Email': 'john.reviewer@company.com',
                'Password': 'password123'
            },
            {
                'UserName': 'Jane Approver', 
                'Email': 'jane.approver@company.com',
                'Password': 'password123'
            },
            {
                'UserName': 'Bob Manager',
                'Email': 'bob.manager@company.com', 
                'Password': 'password123'
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user = Users.objects.create(
                UserName=user_data['UserName'],
                Email=user_data['Email'],
                Password=user_data['Password'],
                CreatedAt=datetime.now(),
                UpdatedAt=datetime.now()
            )
            created_users.append({
                'UserId': user.UserId,
                'UserName': user.UserName,
                'Email': user.Email
            })
        
        return Response({
            "message": f"Created {len(created_users)} test users successfully",
            "users": created_users
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"ERROR: Failed to create test users: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)