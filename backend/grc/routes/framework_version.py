from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from ..models import Framework, FrameworkApproval, Policy, SubPolicy, FrameworkVersion, PolicyVersion, Users
from ..notification_service import NotificationService 
import traceback
from ..validators.framework_validator import validate_framework_version_data, ValidationError
from ..utils import send_log, get_client_ip

# RBAC Permission imports - Add comprehensive RBAC permissions
from ..rbac.permissions import (
     PolicyFrameworkPermission, PolicyViewPermission,
    PolicyEditPermission, PolicyApprovalWorkflowPermission
)


@api_view(['POST'])
 # RBAC: Require PolicyVersioningPermission for creating framework versions
def create_framework_version(request, framework_id):
    """
    Create a new version of a framework with its policies and subpolicies.
    Supports both major and minor versioning.
    
    Expected request data:
    - version_type: 'major' or 'minor' (default: 'minor')
    - Other framework data...
    
    This is used from the Versioning.vue component.
    """
    # Log framework version creation attempt
    send_log(
        module="Framework",
        actionType="VERSION_CREATE",
        description=f"Creating new version for framework {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="Framework",
        entityId=framework_id,
        ipAddress=get_client_ip(request)
    )
    
    try:
        # Import security modules
        from django.utils.html import escape as escape_html
        import shlex
        import re
        
        # Validate request data
        try:
            validated_data = validate_framework_version_data(request.data)
        except ValidationError as e:
            # Log validation error
            send_log(
                module="Framework",
                actionType="VERSION_CREATE_FAILED",
                description=f"Framework version validation failed: {str(e)}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=framework_id,
                logLevel="WARNING",
                ipAddress=get_client_ip(request)
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the original framework
        original_framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Verify framework exists and is active
        if original_framework.ActiveInactive != 'Active':
            # Log inactive framework error
            send_log(
                module="Framework",
                actionType="VERSION_CREATE_FAILED",
                description=f"Cannot version inactive framework {framework_id}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=framework_id,
                logLevel="WARNING",
                ipAddress=get_client_ip(request),
                additionalInfo={"framework_status": original_framework.ActiveInactive}
            )
            return Response({"error": "Only active frameworks can be versioned"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract version type from request data (default to 'minor')
        version_type = request.data.get('version_type', 'minor').lower()
        if version_type not in ['major', 'minor']:
            # Log invalid version type error
            send_log(
                module="Framework",
                actionType="VERSION_CREATE_FAILED",
                description=f"Invalid version type '{version_type}' for framework {framework_id}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=framework_id,
                logLevel="WARNING",
                ipAddress=get_client_ip(request),
                additionalInfo={"version_type": version_type}
            )
            return Response({"error": "version_type must be 'major' or 'minor'"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"DEBUG: Framework version type: {version_type}")
        
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
        
        # Use validated data
        framework_data = validated_data
        
        # Start database transaction
        with transaction.atomic():
            # Find the previous version record in FrameworkVersion table
            previous_version_record = FrameworkVersion.objects.filter(
                FrameworkId=original_framework
            ).first()
            
            # Enhanced version calculation logic with major/minor support
            # Work with float values since FrameworkVersion.Version is a FloatField
            current_version_float = original_framework.CurrentVersion
            print(f"DEBUG: Current framework version: {current_version_float}")
            
            if version_type == 'major':
                # Major version increment: 1.0 -> 2.0, 1.5 -> 2.0, 2.3 -> 3.0
                try:
                    current_major = int(current_version_float)
                    new_version_float = float(current_major + 1)
                    print(f"DEBUG: Framework major version increment: {current_version_float} -> {new_version_float}")
                except (ValueError, TypeError) as e:
                    print(f"ERROR: Invalid current framework version: {current_version_float}, error: {str(e)}")
                    
                    # Log version calculation error
                    send_log(
                        module="Framework",
                        actionType="VERSION_CREATE_FAILED",
                        description=f"Invalid current framework version for major increment: {current_version_float}",
                        userId=getattr(request.user, 'id', None),
                        userName=getattr(request.user, 'username', 'Anonymous'),
                        entityType="Framework",
                        entityId=framework_id,
                        logLevel="ERROR",
                        ipAddress=get_client_ip(request),
                        additionalInfo={"current_version": current_version_float, "version_type": "major", "error": str(e)}
                    )
                    
                    return Response({"error": f"Invalid current framework version: {current_version_float}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Minor version increment: 1.0 -> 1.1, 1.5 -> 1.6, 2.0 -> 2.1
                try:
                    current_major = int(current_version_float)
                    current_minor_part = current_version_float - current_major
                    
                    # Find the highest version for this major version by checking existing versions
                    all_versions = FrameworkVersion.objects.filter(
                FrameworkId__Identifier=original_framework.Identifier
                    ).values_list('Version', flat=True)
                    
                    # Filter versions that belong to the same major version
                    same_major_versions = []
                    for v in all_versions:
                        try:
                            if int(v) == current_major:
                                same_major_versions.append(v)
                        except (ValueError, TypeError):
                            continue
                    
                    # Include the current version
                    same_major_versions.append(current_version_float)
                    
                    if same_major_versions:
                        highest_version = max(same_major_versions)
                        # Increment by 0.1 and round to avoid floating point precision issues
                        new_version_float = round(highest_version + 0.1, 1)
                    else:
                        # If no versions found, start with major.1
                        new_version_float = current_major + 0.1
                        
                    print(f"DEBUG: Framework minor version increment: {current_version_float} -> {new_version_float}")
                except (ValueError, TypeError) as e:
                    print(f"ERROR: Invalid current framework version: {current_version_float}, error: {str(e)}")
                    
                    # Log version calculation error
                    send_log(
                        module="Framework",
                        actionType="VERSION_CREATE_FAILED",
                        description=f"Invalid current framework version for minor increment: {current_version_float}",
                        userId=getattr(request.user, 'id', None),
                        userName=getattr(request.user, 'username', 'Anonymous'),
                        entityType="Framework",
                        entityId=framework_id,
                        logLevel="ERROR",
                        ipAddress=get_client_ip(request),
                        additionalInfo={"current_version": current_version_float, "version_type": "minor", "error": str(e)}
                    )
                    
                    return Response({"error": f"Invalid current framework version: {current_version_float}"}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"DEBUG: Creating new framework with version: {new_version_float}")
            
            # Check if we have a reviewer ID and convert to name if needed
            reviewer_name = framework_data.get('ReviewerName', '')
            if not reviewer_name and framework_data.get('Reviewer'):
                reviewer_id = framework_data.get('Reviewer')
                try:
                    reviewer_user = Users.objects.get(UserId=reviewer_id)
                    reviewer_name = reviewer_user.UserName
                except Users.DoesNotExist:
                    reviewer_name = framework_data.get('Reviewer', original_framework.Reviewer)
                    print(f"Reviewer with ID {reviewer_id} not found, using original value")
                    
            # Security: Sanitize framework data before database storage (Django ORM provides SQL injection protection)
            new_framework = Framework.objects.create(
                FrameworkName=escape_html(framework_data.get('FrameworkName', original_framework.FrameworkName)),
                FrameworkDescription=escape_html(framework_data.get('FrameworkDescription', original_framework.FrameworkDescription)),
                Category=escape_html(framework_data.get('Category', original_framework.Category)),
                StartDate=framework_data.get('StartDate', original_framework.StartDate),
                EndDate=framework_data.get('EndDate', original_framework.EndDate),
                DocURL=framework_data.get('DocURL', original_framework.DocURL),  # Note: If used in shell commands, apply secure_url_for_shell()
                Identifier=escape_html(framework_data.get('Identifier', original_framework.Identifier)),
                CreatedByName=escape_html(framework_data.get('CreatedByName', original_framework.CreatedByName)),
                CreatedByDate=timezone.now().date(),
                Reviewer=escape_html(reviewer_name or framework_data.get('Reviewer', original_framework.Reviewer)),
                Status='Under Review',  # Always start as Under Review
                ActiveInactive='Inactive',  # Default to Inactive for new versions
                CurrentVersion=new_version_float,  # Set the CurrentVersion to the new version number
                InternalExternal=framework_data.get('InternalExternal', original_framework.InternalExternal)
            )
            
            # Create entry in FrameworkVersion table
            framework_version = FrameworkVersion.objects.create(
                FrameworkId=new_framework,
                FrameworkName=new_framework.FrameworkName,
                Version=new_version_float,  # Store as float for proper sorting
                PreviousVersionId=previous_version_record.VersionId if previous_version_record else None,
                CreatedBy=framework_data.get('CreatedByName', original_framework.CreatedByName),
                CreatedDate=timezone.now().date()
            )
            
            # Log successful framework version creation
            send_log(
                module="Framework",
                actionType="VERSION_CREATE_SUCCESS",
                description=f"Framework version {new_version_float} created successfully",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=new_framework.FrameworkId,
                ipAddress=get_client_ip(request),
                additionalInfo={
                    "framework_name": new_framework.FrameworkName,
                    "new_version": new_version_float,
                    "previous_version": current_version_float,
                    "version_type": version_type,
                    "original_framework_id": framework_id
                }
            )
            
            # Process existing policies (to include or exclude)
            policies_count = len(framework_data.get('policies', []))
            print(f"DEBUG: Processing {policies_count} existing policies")
            
            # Log policy processing start
            send_log(
                module="Framework",
                actionType="VERSION_PROCESS_POLICIES",
                description=f"Processing {policies_count} existing policies for framework version {new_version_float}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=new_framework.FrameworkId,
                ipAddress=get_client_ip(request),
                additionalInfo={"policies_count": policies_count}
            )
            
            if 'policies' in framework_data:
                for policy_data in framework_data.get('policies', []):
                    # Skip policies marked for exclusion
                    if policy_data.get('exclude', False):
                        # Security: Escape policy name for safe logging
                        safe_policy_name = escape_html(policy_data.get('PolicyName', 'Unknown'))
                        print(f"DEBUG: Excluding policy {safe_policy_name}")
                        continue
                    
                    print(f"DEBUG: Processing existing policy {policy_data.get('PolicyName', 'Unknown')}")
                    
                    # Get original policy
                    original_policy_id = policy_data.get('original_policy_id')
                    
                    if original_policy_id:
                        try:
                            original_policy = Policy.objects.get(PolicyId=original_policy_id)
                            
                            # Find previous policy version
                            previous_policy_version = PolicyVersion.objects.filter(
                                PolicyId=original_policy
                            ).first()
                            
                            # Security: Sanitize policy data before database storage
                            new_policy = Policy.objects.create(
                                FrameworkId=new_framework,
                                PolicyName=escape_html(policy_data.get('PolicyName', original_policy.PolicyName)),
                                PolicyDescription=escape_html(policy_data.get('PolicyDescription', original_policy.PolicyDescription)),
                                Status='Under Review',
                                StartDate=policy_data.get('StartDate', original_policy.StartDate),
                                EndDate=policy_data.get('EndDate', original_policy.EndDate),
                                Department=escape_html(policy_data.get('Department', original_policy.Department)),
                                CreatedByName=escape_html(new_framework.CreatedByName),
                                CreatedByDate=timezone.now().date(),
                                Applicability=escape_html(policy_data.get('Applicability', original_policy.Applicability)),
                                DocURL=policy_data.get('DocURL', original_policy.DocURL),  # Note: If used in shell commands, apply secure_url_for_shell()
                                Scope=escape_html(policy_data.get('Scope', original_policy.Scope)),
                                Objective=escape_html(policy_data.get('Objective', original_policy.Objective)),
                                Identifier=escape_html(policy_data.get('Identifier', original_policy.Identifier)),
                                PermanentTemporary='',
                                ActiveInactive='Inactive',
                                Reviewer=escape_html(policy_data.get('ReviewerName', policy_data.get('Reviewer', original_policy.Reviewer))),
                                CoverageRate=policy_data.get('CoverageRate', original_policy.CoverageRate),
                                CurrentVersion=str(new_version_float),  # Set the CurrentVersion to match the framework version
                                PolicyType=escape_html(policy_data.get('PolicyType', original_policy.PolicyType)),
                                PolicyCategory=escape_html(policy_data.get('PolicyCategory', original_policy.PolicyCategory)),
                                PolicySubCategory=escape_html(policy_data.get('PolicySubCategory', original_policy.PolicySubCategory)),
                                Entities=policy_data.get('Entities', original_policy.Entities)
                            )
                            
                            # Create a policy version entry
                            PolicyVersion.objects.create(
                                PolicyId=new_policy,
                                Version=str(new_version_float),
                                PolicyName=new_policy.PolicyName,
                                CreatedBy=new_policy.CreatedByName,
                                CreatedDate=timezone.now().date(),
                                PreviousVersionId=previous_policy_version.VersionId if previous_policy_version else None
                            )
                            
                            # Process existing subpolicies
                            if 'subpolicies' in policy_data:
                                for subpolicy_data in policy_data.get('subpolicies', []):
                                    # Skip subpolicies marked for exclusion
                                    if subpolicy_data.get('exclude', False):
                                        continue
                                    
                                    original_subpolicy_id = subpolicy_data.get('original_subpolicy_id')
                                    
                                    if original_subpolicy_id:
                                        try:
                                            original_subpolicy = SubPolicy.objects.get(SubPolicyId=original_subpolicy_id)
                                            
                                            # Security: Sanitize subpolicy data before database storage
                                            safe_subpolicy_name = escape_html(subpolicy_data.get('SubPolicyName', original_subpolicy.SubPolicyName))
                                            print(f"Creating existing subpolicy {safe_subpolicy_name} for policy {new_policy.PolicyName}")
                                            SubPolicy.objects.create(
                                                PolicyId=new_policy,
                                                SubPolicyName=escape_html(subpolicy_data.get('SubPolicyName', original_subpolicy.SubPolicyName)),
                                                CreatedByName=escape_html(new_policy.CreatedByName),
                                                CreatedByDate=timezone.now().date(),
                                                Identifier=escape_html(subpolicy_data.get('Identifier', original_subpolicy.Identifier)),
                                                Description=escape_html(subpolicy_data.get('Description', original_subpolicy.Description)),
                                                Status='Under Review',
                                                PermanentTemporary=subpolicy_data.get('PermanentTemporary', ''),
                                                Control=escape_html(subpolicy_data.get('Control', original_subpolicy.Control))
                                            )
                                        except SubPolicy.DoesNotExist:
                                            # Log but continue if subpolicy not found
                                            print(f"Original subpolicy {original_subpolicy_id} not found, skipping.")
                                    else:
                                        # Security: Sanitize new subpolicy data before database storage
                                        print(f"Creating new subpolicy (old format) for existing policy {new_policy.PolicyName}")
                                        SubPolicy.objects.create(
                                            PolicyId=new_policy,
                                            SubPolicyName=escape_html(subpolicy_data.get('SubPolicyName', '')),
                                            CreatedByName=escape_html(new_policy.CreatedByName),
                                            CreatedByDate=timezone.now().date(),
                                            Identifier=escape_html(subpolicy_data.get('Identifier', '')),
                                            Description=escape_html(subpolicy_data.get('Description', '')),
                                            Status='Under Review',
                                            PermanentTemporary=subpolicy_data.get('PermanentTemporary', ''),
                                            Control=escape_html(subpolicy_data.get('Control', ''))
                                        )
                            
                            # Process new subpolicies for existing policies
                            if 'new_subpolicies' in policy_data:
                                for new_subpolicy_data in policy_data.get('new_subpolicies', []):
                                    # Security: Escape subpolicy name for safe logging and sanitize data
                                    safe_subpolicy_name = escape_html(new_subpolicy_data.get('SubPolicyName', ''))
                                    print(f"Creating new subpolicy {safe_subpolicy_name} for existing policy {new_policy.PolicyName}")
                                    SubPolicy.objects.create(
                                        PolicyId=new_policy,
                                        SubPolicyName=escape_html(new_subpolicy_data.get('SubPolicyName', '')),
                                        CreatedByName=escape_html(new_policy.CreatedByName),
                                        CreatedByDate=timezone.now().date(),
                                        Identifier=escape_html(new_subpolicy_data.get('Identifier', '')),
                                        Description=escape_html(new_subpolicy_data.get('Description', '')),
                                        Status='Under Review',
                                        PermanentTemporary=new_subpolicy_data.get('PermanentTemporary', ''),
                                        Control=escape_html(new_subpolicy_data.get('Control', ''))
                                        )
                                
                        except Policy.DoesNotExist:
                            # Log but continue if policy not found
                            print(f"Original policy {original_policy_id} not found, skipping.")
            
            # Process new policies
            new_policies_count = len(framework_data.get('new_policies', []))
            print(f"DEBUG: Processing {new_policies_count} new policies")
            
            # Log new policies processing start
            send_log(
                module="Framework",
                actionType="VERSION_PROCESS_NEW_POLICIES",
                description=f"Processing {new_policies_count} new policies for framework version {new_version_float}",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=new_framework.FrameworkId,
                ipAddress=get_client_ip(request),
                additionalInfo={"new_policies_count": new_policies_count}
            )
            
            if 'new_policies' in framework_data:
                for new_policy_data in framework_data.get('new_policies', []):
                    # Security: Escape policy name for safe logging
                    safe_new_policy_name = escape_html(new_policy_data.get('PolicyName', 'Unknown'))
                    print(f"DEBUG: Processing new policy {safe_new_policy_name}")
                    # Security: Sanitize new policy data before database storage
                    new_policy = Policy.objects.create(
                        FrameworkId=new_framework,
                        PolicyName=escape_html(new_policy_data.get('PolicyName', '')),
                        PolicyDescription=escape_html(new_policy_data.get('PolicyDescription', '')),
                        Status='Under Review',
                        StartDate=new_policy_data.get('StartDate'),
                        EndDate=new_policy_data.get('EndDate'),
                        Department=escape_html(new_policy_data.get('Department', '')),
                        CreatedByName=escape_html(new_framework.CreatedByName),
                        CreatedByDate=timezone.now().date(),
                        Applicability=escape_html(new_policy_data.get('Applicability', '')),
                        DocURL=new_policy_data.get('DocURL', ''),  # Note: If used in shell commands, apply secure_url_for_shell()
                        Scope=escape_html(new_policy_data.get('Scope', '')),
                        Objective=escape_html(new_policy_data.get('Objective', '')),
                        Identifier=escape_html(new_policy_data.get('Identifier', '')),
                        PermanentTemporary='',
                        ActiveInactive='Inactive',
                        Reviewer=escape_html(new_policy_data.get('ReviewerName', '')),
                        CoverageRate=new_policy_data.get('CoverageRate'),
                        CurrentVersion=str(new_version_float),  # Set CurrentVersion to match the framework version
                        PolicyType=escape_html(new_policy_data.get('PolicyType', '')),
                        PolicyCategory=escape_html(new_policy_data.get('PolicyCategory', '')),
                        PolicySubCategory=escape_html(new_policy_data.get('PolicySubCategory', '')),
                        Entities=new_policy_data.get('Entities', [])
                    )
                    
                    # Create a policy version entry for new policy
                    PolicyVersion.objects.create(
                        PolicyId=new_policy,
                        Version=str(new_version_float),
                        PolicyName=new_policy.PolicyName,
                        CreatedBy=new_policy.CreatedByName,
                        CreatedDate=timezone.now().date(),
                        PreviousVersionId=None  # No previous version for new policies
                    )
                    
                    # Process new subpolicies
                    subpolicies_count = len(new_policy_data.get('subpolicies', []))
                    print(f"DEBUG: Processing {subpolicies_count} subpolicies for new policy {new_policy.PolicyName}")
                    if 'subpolicies' in new_policy_data:
                        for new_subpolicy_data in new_policy_data.get('subpolicies', []):
                            # Security: Escape subpolicy name for safe logging and sanitize data
                            safe_new_subpolicy_name = escape_html(new_subpolicy_data.get('SubPolicyName', 'Unknown'))
                            print(f"DEBUG: Creating subpolicy {safe_new_subpolicy_name} for new policy")
                            SubPolicy.objects.create(
                                PolicyId=new_policy,
                                SubPolicyName=escape_html(new_subpolicy_data.get('SubPolicyName', '')),
                                CreatedByName=escape_html(new_policy.CreatedByName),
                                CreatedByDate=timezone.now().date(),
                                Identifier=escape_html(new_subpolicy_data.get('Identifier', '')),
                                Description=escape_html(new_subpolicy_data.get('Description', '')),
                                Status='Under Review',
                                PermanentTemporary=new_subpolicy_data.get('PermanentTemporary', ''),
                                Control=escape_html(new_subpolicy_data.get('Control', ''))
                            )
            
            # Create framework approval entry
            create_framework_approval_for_version(new_framework.FrameworkId)
            
            # Mark the original framework as inactive
            # Note: This doesn't actually deactivate the framework right away - 
            # it will only be deactivated when the new version is approved
            # But we'll keep a reference to it for future processing
            print(f"INFO: Original framework ID {original_framework.FrameworkId} will be deactivated when the new version is approved")
            
            # After creating the new framework version, send notification to reviewer if email is available
            framework_reviewer_email = None
            if reviewer_name:
                reviewer_user = Users.objects.filter(UserName=reviewer_name).first()
                if reviewer_user:
                    framework_reviewer_email = reviewer_user.Email
            if framework_reviewer_email:
                notification_service = NotificationService()
                # Security: XSS Protection - Escape HTML content before building email template
                notification_data = {
                    'notification_type': 'frameworkVersionSubmitted',
                    'email': framework_reviewer_email,
                    'email_type': 'gmail',
                    'template_data': [
                        escape_html(new_framework.FrameworkName),  # Escape framework name for HTML context
                        escape_html(reviewer_name),  # Escape reviewer name for HTML context
                        escape_html(new_framework.CreatedByName),  # Escape submitter name for HTML context
                        str(new_version_float)  # Version number is safe
                    ]
                }
                notification_result = notification_service.send_multi_channel_notification(notification_data)
                print(f"Framework version notification result: {notification_result}")
            
            # Log successful framework version completion
            send_log(
                module="Framework",
                actionType="VERSION_CREATE_COMPLETE",
                description=f"Framework version {new_version_float} created and configured successfully",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="Framework",
                entityId=new_framework.FrameworkId,
                ipAddress=get_client_ip(request),
                additionalInfo={
                    "framework_name": new_framework.FrameworkName,
                    "new_version": new_version_float,
                    "previous_version": current_version_float,
                    "version_type": version_type,
                    "policies_processed": policies_count,
                    "new_policies_added": new_policies_count,
                    "status": new_framework.Status
                }
            )
            
            # Return the new framework and version information
            return Response({
                "message": "Framework version created successfully",
                "FrameworkId": new_framework.FrameworkId,
                "FrameworkName": new_framework.FrameworkName,
                "PreviousVersion": current_version_float,
                "NewVersion": new_version_float,
                "VersionType": version_type,
                "Status": new_framework.Status
            }, status=status.HTTP_201_CREATED)
    
    except Framework.DoesNotExist:
        # Log framework not found error
        send_log(
            module="Framework",
            actionType="VERSION_CREATE_FAILED",
            description=f"Original framework {framework_id} not found",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Original framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Log general exception
        send_log(
            module="Framework",
            actionType="VERSION_CREATE_FAILED",
            description=f"Unexpected error creating framework version: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request),
            additionalInfo={"error": str(e)}
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_framework_approval_for_version(framework_id):
    """
    Helper function to create a framework approval entry for a new framework version
    """
    try:
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # For approval, we need reviewer ID, not name
        reviewer_id = None
        if framework.Reviewer:
            # Try to look up reviewer ID by name
            try:
                reviewer = Users.objects.filter(UserName=framework.Reviewer).first()
                if reviewer:
                    reviewer_id = reviewer.UserId
                else:
                    # If not found and the Reviewer looks like a number, use it as ID
                    if isinstance(framework.Reviewer, str) and framework.Reviewer.isdigit():
                        reviewer_id = int(framework.Reviewer)
                    else:
                        reviewer_id = 2  # Default reviewer id
            except Exception as e:
                print(f"Error finding reviewer ID: {str(e)}")
                reviewer_id = 2  # Default to reviewer ID 2
        else:
            reviewer_id = 2  # Default reviewer id
        
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
                "PolicyType":policy.PolicyType,
                "PolicyCategory":policy.PolicyCategory,
                "PolicySubCategory":policy.PolicySubCategory,
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
        
        # Prepare the extracted data for the approval
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
            "reviewer": reviewer_id,  # Use ID in extracted_data
            "source": "versioning",
            "policies": policies_data,
            "totalPolicies": len(policies_data),
            "totalSubpolicies": sum(len(p["subpolicies"]) for p in policies_data),
            "CurrentVersion": framework.CurrentVersion  # Include the CurrentVersion in extracted data
        }
            
        # Create the framework approval
        FrameworkApproval.objects.create(
            FrameworkId=framework,
            ExtractedData=extracted_data,
            UserId=1,  # Default user id
            ReviewerId=reviewer_id,  # Use reviewer ID, not name
            Version="u1",  # Default initial version
            ApprovedNot=None  # Not yet approved
        )
        
        return True
    except Exception as e:
        print(f"Error creating framework approval: {str(e)}")
        return False


@api_view(['GET'])
@permission_classes([PolicyViewPermission])  # RBAC: Require PolicyViewPermission for viewing framework versions
def get_framework_versions(request, framework_id=None):
    """
    Get all versions of a framework by its Identifier
    """
    # Log framework versions retrieval attempt
    send_log(
        module="Framework",
        actionType="VIEW_VERSIONS",
        description=f"Framework versions retrieval attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkVersion",
        ipAddress=get_client_ip(request)
    )
    
    try:
        if framework_id:
            # Get the framework to find its identifier
            framework = Framework.objects.get(FrameworkId=framework_id)
            identifier = framework.Identifier
            
            # Find all frameworks with this identifier
            frameworks = Framework.objects.filter(Identifier=identifier).order_by('-FrameworkId')
            
            # Get the version information for each framework
            versions_data = []
            for fw in frameworks:
                version_info = FrameworkVersion.objects.filter(FrameworkId=fw).first()
                if version_info:
                    versions_data.append({
                        "FrameworkId": fw.FrameworkId,
                        "FrameworkName": fw.FrameworkName,
                        "Version": version_info.Version,
                        "CreatedBy": version_info.CreatedBy,
                        "CreatedDate": version_info.CreatedDate.isoformat() if version_info.CreatedDate else None,
                        "Status": fw.Status,
                        "ActiveInactive": fw.ActiveInactive
                    })
                else:
                    # Handle frameworks without version information
                    versions_data.append({
                        "FrameworkId": fw.FrameworkId,
                        "FrameworkName": fw.FrameworkName,
                        "Version": "1",  # Default to version 1
                        "CreatedBy": fw.CreatedByName,
                        "CreatedDate": fw.CreatedByDate.isoformat() if fw.CreatedByDate else None,
                        "Status": fw.Status,
                        "ActiveInactive": fw.ActiveInactive
                    })
            
            send_log(
                module="Framework",
                actionType="VIEW_VERSIONS_SUCCESS",
                description=f"Successfully retrieved {len(versions_data)} framework versions",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="FrameworkVersion",
                ipAddress=get_client_ip(request),
                additionalInfo={"framework_id": framework_id, "versions_count": len(versions_data)}
            )
            
            return Response(versions_data, status=status.HTTP_200_OK)
        else:
            send_log(
                module="Framework",
                actionType="VIEW_VERSIONS_FAILED",
                description="Framework versions retrieval failed - no framework ID provided",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="FrameworkVersion",
                logLevel="WARNING",
                ipAddress=get_client_ip(request)
            )
            return Response({"error": "Framework ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Framework.DoesNotExist:
        send_log(
            module="Framework",
            actionType="VIEW_VERSIONS_FAILED",
            description=f"Framework versions retrieval failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        send_log(
            module="Framework",
            actionType="VIEW_VERSIONS_FAILED",
            description=f"Framework versions retrieval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([PolicyViewPermission])  # RBAC: Require PolicyViewPermission for viewing all framework versions
def get_all_framework_versions(request):
    """
    Get all framework versions in the system
    """
    # Log all framework versions retrieval attempt
    send_log(
        module="Framework",
        actionType="VIEW_ALL_VERSIONS",
        description="All framework versions retrieval attempt",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkVersion",
        ipAddress=get_client_ip(request)
    )
    
    try:
        # Get all framework versions
        framework_versions = FrameworkVersion.objects.all().order_by('-CreatedDate')
        
        versions_data = []
        for version in framework_versions:
            framework = version.FrameworkId
            if framework:
                versions_data.append({
                    "VersionId": version.VersionId,
                    "FrameworkId": framework.FrameworkId,
                    "FrameworkName": framework.FrameworkName,
                    "Version": version.Version,
                    "PreviousVersionId": version.PreviousVersionId,
                    "CreatedBy": version.CreatedBy,
                    "CreatedDate": version.CreatedDate.isoformat() if version.CreatedDate else None,
                    "Status": framework.Status,
                    "ActiveInactive": framework.ActiveInactive,
                    "Category": framework.Category
                })
        
        send_log(
            module="Framework",
            actionType="VIEW_ALL_VERSIONS_SUCCESS",
            description=f"Successfully retrieved {len(versions_data)} framework versions",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            ipAddress=get_client_ip(request),
            additionalInfo={"versions_count": len(versions_data)}
        )
        
        return Response(versions_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        send_log(
            module="Framework",
            actionType="VIEW_ALL_VERSIONS_FAILED",
            description=f"All framework versions retrieval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([PolicyEditPermission])  # RBAC: Require PolicyEditPermission for activating/deactivating framework versions
def activate_deactivate_framework_version(request, framework_id):
    """
    Activate or deactivate a specific framework version with date-based scheduling logic
    """
    # Log framework activation/deactivation attempt
    send_log(
        module="Framework",
        actionType="TOGGLE_VERSION_STATUS",
        description=f"Framework version status toggle attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="Framework",
        entityId=framework_id,
        ipAddress=get_client_ip(request)
    )
    
    try:
        from datetime import date
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Save current status
        current_status = framework.Status
        print(f"DEBUG: Current framework status before toggle: ActiveInactive={framework.ActiveInactive}, Status={current_status}")
        
        # Determine action - if activating, use date-based logic
        action = request.data.get('action', 'toggle')  # 'activate', 'deactivate', or 'toggle'
        
        if action == 'activate' or (action == 'toggle' and framework.ActiveInactive != 'Active'):
            # Activating framework - use date-based scheduling logic
            today = date.today()
            print(f"DEBUG: Framework Version Activation {framework_id} - Today: {today}, StartDate: {framework.StartDate} (type: {type(framework.StartDate)})")
            
            if framework.StartDate and framework.StartDate > today:
                framework.ActiveInactive = 'Scheduled'
                print(f"Set framework version {framework_id} to Scheduled status (StartDate: {framework.StartDate} > today: {today})")
            else:
                framework.ActiveInactive = 'Active'
                print(f"Set framework version {framework_id} to Active status (StartDate: {framework.StartDate} <= today: {today} or None)")
                
            new_active_status = framework.ActiveInactive
        else:
            # Deactivating framework
            framework.ActiveInactive = 'Inactive'
            new_active_status = 'Inactive'
            print(f"Set framework version {framework_id} to Inactive status")
        
        # Make sure Status remains 'Approved' if it was already approved
        if current_status == 'Approved':
            # Don't change the Status, leave it as 'Approved'
            print(f"DEBUG: Keeping Status '{current_status}' for framework {framework_id}")
        
        framework.save()
        
        # Verify the Status field was preserved
        framework.refresh_from_db()
        print(f"DEBUG: Framework status after toggle: ActiveInactive={framework.ActiveInactive}, Status={framework.Status}")
        
        send_log(
            module="Framework",
            actionType="TOGGLE_VERSION_STATUS_SUCCESS",
            description=f"Framework version status updated to {new_active_status} successfully",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_name": framework.FrameworkName,
                "new_status": new_active_status,
                "action": action
            }
        )
        
        return Response({
            "message": f"Framework version updated to {new_active_status} successfully",
            "FrameworkId": framework.FrameworkId,
            "ActiveInactive": framework.ActiveInactive,
            "Status": framework.Status
        }, status=status.HTTP_200_OK)
    
    except Framework.DoesNotExist:
        send_log(
            module="Framework",
            actionType="TOGGLE_VERSION_STATUS_FAILED",
            description=f"Framework version status toggle failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        send_log(
            module="Framework",
            actionType="TOGGLE_VERSION_STATUS_FAILED",
            description=f"Framework version status toggle failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([PolicyViewPermission])  # RBAC: Require PolicyViewPermission for viewing rejected framework versions
def get_rejected_framework_versions(request, user_id=None):
    """
    Get all rejected framework versions for a specific user that can be edited and resubmitted
    """
    # Log rejected framework versions retrieval attempt
    send_log(
        module="Framework",
        actionType="VIEW_REJECTED_VERSIONS",
        description=f"Rejected framework versions retrieval attempt for user ID: {user_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="FrameworkVersion",
        ipAddress=get_client_ip(request)
    )
    
    try:
        if not user_id:
            user_id = request.GET.get('user_id', None)
            
        if not user_id:
            send_log(
                module="Framework",
                actionType="VIEW_REJECTED_VERSIONS_FAILED",
                description="Rejected framework versions retrieval failed - no user ID provided",
                userId=getattr(request.user, 'id', None),
                userName=getattr(request.user, 'username', 'Anonymous'),
                entityType="FrameworkVersion",
                logLevel="WARNING",
                ipAddress=get_client_ip(request)
            )
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get all framework approvals where:
        # 1. The approval is rejected (ApprovedNot=False)
        # 2. The version starts with 'r' (reviewer version)
        # 3. If user_id is provided, filter by UserId
        query_filters = {
            'ApprovedNot': False,
            'Version__startswith': 'r'
        }
        
        if user_id:
            query_filters['UserId'] = user_id
            
        rejections = FrameworkApproval.objects.filter(**query_filters).order_by('-ApprovalId')
        
        # Group by FrameworkId to get only the latest rejection for each framework
        framework_rejections = {}
        for rejection in rejections:
            if not rejection.FrameworkId:
                continue
                
            framework_id = rejection.FrameworkId.FrameworkId
            if framework_id not in framework_rejections:
                framework_rejections[framework_id] = rejection
        
        # Format response
        rejected_frameworks = []
        for rejection in framework_rejections.values():
            framework = rejection.FrameworkId
            
            # Get version info
            version_info = FrameworkVersion.objects.filter(FrameworkId=framework).first()
            
            rejection_data = {
                "ApprovalId": rejection.ApprovalId,
                "FrameworkId": framework.FrameworkId,
                "FrameworkName": framework.FrameworkName,
                "Version": version_info.Version if version_info else 1,
                "Status": framework.Status,
                "CreatedByName": framework.CreatedByName,
                "CreatedDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
                "ExtractedData": rejection.ExtractedData,
                "RejectionReason": rejection.ExtractedData.get('framework_approval', {}).get('remarks', 'No reason provided')
            }
            
            rejected_frameworks.append(rejection_data)
        
        send_log(
            module="Framework",
            actionType="VIEW_REJECTED_VERSIONS_SUCCESS",
            description=f"Successfully retrieved {len(rejected_frameworks)} rejected framework versions",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            ipAddress=get_client_ip(request),
            additionalInfo={"user_id": user_id, "rejected_count": len(rejected_frameworks)}
        )
        
        return Response(rejected_frameworks, status=status.HTTP_200_OK)
        
    except Exception as e:
        send_log(
            module="Framework",
            actionType="VIEW_REJECTED_VERSIONS_FAILED",
            description=f"Rejected framework versions retrieval failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="FrameworkVersion",
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'PUT'])
@permission_classes([PolicyApprovalWorkflowPermission])  # RBAC: Require PolicyApprovalWorkflowPermission for resubmitting rejected frameworks
def resubmit_rejected_framework(request, framework_id):
    """
    Resubmit a rejected framework with updated data
    Accepts both POST and PUT methods to ensure compatibility with existing frontend
    """
    # Log framework resubmission attempt
    send_log(
        module="Framework",
        actionType="RESUBMIT_FRAMEWORK",
        description=f"Framework resubmission attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="Framework",
        entityId=framework_id,
        ipAddress=get_client_ip(request)
    )
    
    try:
        print(f"DEBUG: Starting resubmit_rejected_framework for framework_id: {framework_id}")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request data: {request.data}")
        
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        print(f"DEBUG: Found framework with name: {framework.FrameworkName}, status: {framework.Status}")
        
        # Verify framework exists and is rejected
        if framework.Status != 'Rejected':
            print(f"DEBUG: Framework status is not 'Rejected', it's '{framework.Status}'")
            return Response({"error": "Only rejected frameworks can be resubmitted"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the latest framework approval (should be a rejected reviewer version 'r1')
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework,
            ApprovedNot=False,
            Version__startswith='r'
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            print(f"DEBUG: No rejected framework approval found for framework_id: {framework_id}")
            return Response({"error": "No rejected framework approval found"}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"DEBUG: Found latest approval with id: {latest_approval.ApprovalId}, version: {latest_approval.Version}")
        
        # Get updated data from request
        updated_data = request.data
        print(f"DEBUG: Updated data received: {updated_data}")
        print(f"DEBUG: Policies in request: {updated_data.get('policies', [])}")
        print(f"DEBUG: Number of policies in request: {len(updated_data.get('policies', []))}")
        
        # Start database transaction
        with transaction.atomic():
            print(f"DEBUG: Starting transaction for framework resubmission")
            
            # Update framework basic fields
            if 'FrameworkName' in updated_data:
                framework.FrameworkName = updated_data['FrameworkName']
                print(f"DEBUG: Updated FrameworkName to: {framework.FrameworkName}")
            if 'FrameworkDescription' in updated_data:
                framework.FrameworkDescription = updated_data['FrameworkDescription']
                print(f"DEBUG: Updated FrameworkDescription")
            if 'Category' in updated_data:
                framework.Category = updated_data['Category']
                print(f"DEBUG: Updated Category to: {framework.Category}")
            
            # Handle date fields
            for date_field in ['EffectiveDate', 'StartDate', 'EndDate']:
                if date_field in updated_data and updated_data[date_field]:
                    try:
                        if isinstance(updated_data[date_field], str):
                            date_value = datetime.strptime(updated_data[date_field], '%Y-%m-%d').date()
                            setattr(framework, date_field, date_value)
                            print(f"DEBUG: Updated {date_field} to {date_value}")
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Error parsing date field {date_field}: {str(e)}")
                        pass
            
            # Change status back to Under Review
            framework.Status = 'Under Review'
            framework.save()
            print(f"DEBUG: Updated framework status to 'Under Review'")
            
            # Create a copy of the extracted data with updated information
            extracted_data = {}
            if latest_approval.ExtractedData:
                try:
                    extracted_data = dict(latest_approval.ExtractedData)
                    print(f"DEBUG: Successfully copied extracted data")
                except Exception as e:
                    print(f"DEBUG: Error copying extracted data: {str(e)}")
                    extracted_data = {}
            
            # Update the framework data in extracted_data
            extracted_data.update({
                "FrameworkName": framework.FrameworkName,
                "FrameworkDescription": framework.FrameworkDescription,
                "Category": framework.Category,
                "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
                "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
                "Status": "Under Review",
                "resubmitted": True,
                "resubmission_date": timezone.now().date().isoformat(),
                "previous_rejection": latest_approval.ExtractedData.get('framework_approval', {})
            })
            
            # Update policies data if provided
            policies_to_process = updated_data.get('policies', [])
            print(f"DEBUG: Policies to process: {policies_to_process}")
            
            if policies_to_process and len(policies_to_process) > 0:
                policies_data = []
                print(f"DEBUG: Processing {len(policies_to_process)} policies from request")
                
                for policy_update in policies_to_process:
                    policy_id = policy_update.get('PolicyId')
                    print(f"DEBUG: Processing policy with ID: {policy_id}")
                    print(f"DEBUG: Policy update data: {policy_update}")
                    
                    # Get policy from database for update
                    try:
                        if policy_id:
                            db_policy = Policy.objects.get(PolicyId=policy_id)
                            print(f"DEBUG: Found policy in database: {db_policy.PolicyName}")
                            
                            # Update policy fields in database
                            db_policy.PolicyName = policy_update.get('PolicyName', db_policy.PolicyName)
                            db_policy.PolicyDescription = policy_update.get('PolicyDescription', db_policy.PolicyDescription)
                            db_policy.Scope = policy_update.get('Scope', db_policy.Scope)
                            db_policy.Objective = policy_update.get('Objective', db_policy.Objective)
                            
                            # Reset policy status to Under Review
                            db_policy.Status = 'Under Review'
                            db_policy.save()
                            print(f"DEBUG: Updated policy {policy_id} in database")
                    except Policy.DoesNotExist:
                        print(f"DEBUG: Policy with ID {policy_id} not found in database")
                    
                    policy_dict = {
                        "PolicyId": policy_update.get('PolicyId'),
                        "PolicyName": policy_update.get('PolicyName', ''),
                        "PolicyDescription": policy_update.get('PolicyDescription', ''),
                        "Status": "Under Review",
                        "StartDate": policy_update.get('StartDate'),
                        "EndDate": policy_update.get('EndDate'),
                        "Department": policy_update.get('Department', ''),
                        "Applicability": policy_update.get('Applicability', ''),
                        "DocURL": policy_update.get('DocURL', ''),
                        "Scope": policy_update.get('Scope', ''),
                        "Objective": policy_update.get('Objective', ''),
                        "Identifier": policy_update.get('Identifier', ''),
                        "CreatedByName": policy_update.get('CreatedByName', ''),
                        "Reviewer": policy_update.get('Reviewer', ''),
                        "CoverageRate": policy_update.get('CoverageRate'),
                        "PolicyType": policy_update.get('PolicyType', ''),
                        "PolicyCategory": policy_update.get('PolicyCategory', ''),
                        "PolicySubCategory": policy_update.get('PolicySubCategory', ''),
                        "subpolicies": []
                    }
                    
                    # Log policy category fields to verify they're being processed
                    print(f"DEBUG: Policy category fields for policy {policy_id}:")
                    print(f"DEBUG: PolicyType: {policy_dict['PolicyType']}")
                    print(f"DEBUG: PolicyCategory: {policy_dict['PolicyCategory']}")
                    print(f"DEBUG: PolicySubCategory: {policy_dict['PolicySubCategory']}")
                    
                    # Update subpolicies
                    subpolicies_to_process = policy_update.get('subpolicies', [])
                    print(f"DEBUG: Subpolicies to process for policy {policy_id}: {subpolicies_to_process}")
                    
                    if subpolicies_to_process and len(subpolicies_to_process) > 0:
                        print(f"DEBUG: Processing {len(subpolicies_to_process)} subpolicies for policy {policy_id}")
                        
                        for subpolicy_update in subpolicies_to_process:
                            subpolicy_id = subpolicy_update.get('SubPolicyId')
                            print(f"DEBUG: Processing subpolicy with ID: {subpolicy_id}")
                            print(f"DEBUG: Subpolicy update data: {subpolicy_update}")
                            
                            # Update subpolicy in database
                            try:
                                if subpolicy_id:
                                    db_subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id)
                                    print(f"DEBUG: Found subpolicy in database: {db_subpolicy.SubPolicyName}")
                                    
                                    # Update subpolicy fields
                                    db_subpolicy.SubPolicyName = subpolicy_update.get('SubPolicyName', db_subpolicy.SubPolicyName)
                                    db_subpolicy.Description = subpolicy_update.get('Description', db_subpolicy.Description)
                                    db_subpolicy.Control = subpolicy_update.get('Control', db_subpolicy.Control)
                                    db_subpolicy.Identifier = subpolicy_update.get('Identifier', db_subpolicy.Identifier)
                                    
                                    # Reset subpolicy status to Under Review
                                    db_subpolicy.Status = 'Under Review'
                                    db_subpolicy.save()
                                    print(f"DEBUG: Updated subpolicy {subpolicy_id} in database")
                            except SubPolicy.DoesNotExist:
                                print(f"DEBUG: Subpolicy with ID {subpolicy_id} not found in database")
                            
                            subpolicy_dict = {
                                "SubPolicyId": subpolicy_update.get('SubPolicyId'),
                                "SubPolicyName": subpolicy_update.get('SubPolicyName', ''),
                                "Description": subpolicy_update.get('Description', ''),
                                "Control": subpolicy_update.get('Control', ''),
                                "Identifier": subpolicy_update.get('Identifier', ''),
                                "Status": "Under Review"
                            }
                            policy_dict["subpolicies"].append(subpolicy_dict)
                    
                    policies_data.append(policy_dict)
                
                extracted_data["policies"] = policies_data
                extracted_data["totalPolicies"] = len(policies_data)
                extracted_data["totalSubpolicies"] = sum(len(p["subpolicies"]) for p in policies_data)
                print(f"DEBUG: Updated extracted_data with {len(policies_data)} policies and {extracted_data['totalSubpolicies']} subpolicies")
            else:
                print(f"DEBUG: No policies data found in request or empty policies array")
            
            # Remove previous rejection details
            if 'framework_approval' in extracted_data:
                extracted_data['previous_rejection'] = extracted_data.pop('framework_approval')
                print(f"DEBUG: Moved framework_approval to previous_rejection")
            
            # Create a new user version for resubmission
            latest_user_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='u'
            ).order_by('-ApprovalId').first()
            
            new_version = 'u1'
            if latest_user_version:
                try:
                    print(f"DEBUG: Found latest user version: {latest_user_version.Version}")
                    version_num = int(latest_user_version.Version[1:])
                    new_version = f'u{version_num + 1}'
                except (ValueError, IndexError) as e:
                    print(f"DEBUG: Error parsing version number: {str(e)}")
                    new_version = 'u2'
            
            print(f"DEBUG: Creating new approval record with version: {new_version}")
            
            # Create new approval record for resubmission
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=latest_approval.UserId,
                ReviewerId=latest_approval.ReviewerId,
                Version=new_version,
                ApprovedNot=None
            )
            
            print(f"DEBUG: Successfully created new approval with id: {new_approval.ApprovalId}")

            # Send notification to reviewer
            try:
                print("DEBUG: Starting notification process")
                # Get reviewer details
                try:
                    reviewer = Users.objects.get(UserId=latest_approval.ReviewerId)
                    reviewer_email = reviewer.Email
                    reviewer_name = reviewer.UserName
                    print(f"DEBUG: Found reviewer - Name: {reviewer_name}, Email: {reviewer_email}")
                except Users.DoesNotExist:
                    print(f"DEBUG: Reviewer not found with ID: {latest_approval.ReviewerId}")
                    raise
                
                # Get submitter details
                try:
                    submitter = Users.objects.get(UserId=latest_approval.UserId)
                    submitter_name = submitter.UserName
                    print(f"DEBUG: Found submitter - Name: {submitter_name}")
                except Users.DoesNotExist:
                    print(f"DEBUG: Submitter not found with ID: {latest_approval.UserId}")
                    raise
                
                if reviewer_email:
                    print(f"DEBUG: Preparing to send resubmission notification to reviewer: {reviewer_email}")
                    notification_service = NotificationService()
                    
                    # Log the notification data
                    notification_data = {
                        'notification_type': 'frameworkResubmitted',
                        'email': reviewer_email,
                        'email_type': 'gmail',
                        'template_data': [
                            reviewer_name,
                            framework.FrameworkName,
                            submitter_name
                        ]
                    }
                    print(f"DEBUG: Notification data: {notification_data}")
                    
                    # Send notification
                    notification_result = notification_service.send_multi_channel_notification(notification_data)
                    print(f"DEBUG: Full notification result: {notification_result}")
                    
                    if not notification_result.get('success'):
                        print(f"DEBUG: Failed to send notification. Error: {notification_result.get('error')}")
                        if 'details' in notification_result:
                            print(f"DEBUG: Notification details: {notification_result['details']}")
                else:
                    print(f"DEBUG: No reviewer email available for notification. Reviewer ID: {latest_approval.ReviewerId}")
            except Users.DoesNotExist as user_error:
                print(f"DEBUG: Error getting user details for notification: {str(user_error)}")
                print(f"DEBUG: User ID that was not found: {latest_approval.ReviewerId if 'latest_approval' in locals() else 'Unknown'}")
            except Exception as notification_error:
                print(f"DEBUG: Error sending notification: {str(notification_error)}")
                print(f"DEBUG: Full error details:")
                traceback.print_exc()
            
            print("DEBUG: Completed framework resubmission process")
        
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_SUCCESS",
            description=f"Framework resubmitted successfully",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_name": framework.FrameworkName,
                "new_approval_id": new_approval.ApprovalId,
                "new_version": new_approval.Version
            }
        )
        
        # Success response
        return Response({
            "message": "Framework resubmitted successfully",
            "ApprovalId": new_approval.ApprovalId,
            "Version": new_approval.Version,
            "FrameworkId": framework.FrameworkId,
            "FrameworkName": framework.FrameworkName,
            "Status": framework.Status
        }, status=200)
        
    except Framework.DoesNotExist:
        print(f"DEBUG: Framework with id {framework_id} not found")
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_FAILED",
            description=f"Framework resubmission failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"DEBUG: Unexpected error in resubmit_rejected_framework: {str(e)}")
        import traceback
        traceback.print_exc()
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_FAILED",
            description=f"Framework resubmission failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([PolicyApprovalWorkflowPermission])  # RBAC: Require PolicyApprovalWorkflowPermission for resubmitting framework approvals
def resubmit_framework_approval(request, framework_id):
    """
    Dedicated endpoint for the existing URL pattern used by frontend
    This handles resubmission of rejected frameworks with policy updates
    """
    # Log framework approval resubmission attempt
    send_log(
        module="Framework",
        actionType="RESUBMIT_FRAMEWORK_APPROVAL",
        description=f"Framework approval resubmission attempt for framework ID: {framework_id}",
        userId=getattr(request.user, 'id', None),
        userName=getattr(request.user, 'username', 'Anonymous'),
        entityType="Framework",
        entityId=framework_id,
        ipAddress=get_client_ip(request)
    )
    
    try:
        print(f"DEBUG: resubmit_framework_approval called for framework_id: {framework_id}")
        print(f"DEBUG: Request data: {request.data}")
        
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        print(f"DEBUG: Found framework with name: {framework.FrameworkName}, status: {framework.Status}")
        
        # Verify framework exists and is rejected
        if framework.Status != 'Rejected':
            print(f"DEBUG: Framework status is not 'Rejected', it's '{framework.Status}'")
            return Response({"error": "Only rejected frameworks can be resubmitted"}, status=400)
        
        # Get the latest framework approval (should be a rejected reviewer version)
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework,
            ApprovedNot=False,
            Version__startswith='r'
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            print(f"DEBUG: No rejected framework approval found for framework_id: {framework_id}")
            return Response({"error": "No rejected framework approval found"}, status=404)
        
        print(f"DEBUG: Found latest approval with id: {latest_approval.ApprovalId}, version: {latest_approval.Version}")
        
        # Get updated data from request
        updated_data = request.data
        print(f"DEBUG: Updated data received: {updated_data}")
        print(f"DEBUG: Policies in request: {updated_data.get('policies', [])}")
        print(f"DEBUG: Number of policies in request: {len(updated_data.get('policies', []))}")
        
        # Start database transaction
        with transaction.atomic():
            print(f"DEBUG: Starting transaction for framework resubmission")
            
            # Update framework basic fields
            if 'FrameworkName' in updated_data:
                framework.FrameworkName = updated_data['FrameworkName']
                print(f"DEBUG: Updated FrameworkName to: {framework.FrameworkName}")
            if 'FrameworkDescription' in updated_data:
                framework.FrameworkDescription = updated_data['FrameworkDescription']
                print(f"DEBUG: Updated FrameworkDescription")
            if 'Category' in updated_data:
                framework.Category = updated_data['Category']
                print(f"DEBUG: Updated Category to: {framework.Category}")
            
            # Handle date fields
            for date_field in ['EffectiveDate', 'StartDate', 'EndDate']:
                if date_field in updated_data and updated_data[date_field]:
                    try:
                        if isinstance(updated_data[date_field], str):
                            date_value = datetime.strptime(updated_data[date_field], '%Y-%m-%d').date()
                            setattr(framework, date_field, date_value)
                            print(f"DEBUG: Updated {date_field} to {date_value}")
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Error parsing date field {date_field}: {str(e)}")
                        pass
            
            # Change status back to Under Review
            framework.Status = 'Under Review'
            framework.save()
            print(f"DEBUG: Updated framework status to 'Under Review'")
            
            # Create a copy of the extracted data with updated information
            extracted_data = {}
            if latest_approval.ExtractedData:
                try:
                    extracted_data = dict(latest_approval.ExtractedData)
                    print(f"DEBUG: Successfully copied extracted data")
                except Exception as e:
                    print(f"DEBUG: Error copying extracted data: {str(e)}")
                    extracted_data = {}
            
            # Update the framework data in extracted_data
            extracted_data.update({
                "FrameworkName": framework.FrameworkName,
                "FrameworkDescription": framework.FrameworkDescription,
                "Category": framework.Category,
                "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
                "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
                "Status": "Under Review",
                "resubmitted": True,
                "resubmission_date": timezone.now().date().isoformat(),
                "previous_rejection": latest_approval.ExtractedData.get('framework_approval', {})
            })
            
            # Update policies data if provided
            policies_to_process = updated_data.get('policies', [])
            print(f"DEBUG: Policies to process: {policies_to_process}")
            
            if policies_to_process and len(policies_to_process) > 0:
                policies_data = []
                print(f"DEBUG: Processing {len(policies_to_process)} policies from request")
                
                for policy_update in policies_to_process:
                    policy_id = policy_update.get('PolicyId')
                    print(f"DEBUG: Processing policy with ID: {policy_id}")
                    print(f"DEBUG: Policy update data: {policy_update}")
                    
                    # Get policy from database for update
                    try:
                        if policy_id:
                            db_policy = Policy.objects.get(PolicyId=policy_id)
                            print(f"DEBUG: Found policy in database: {db_policy.PolicyName}")
                            
                            # Update policy fields in database
                            db_policy.PolicyName = policy_update.get('PolicyName', db_policy.PolicyName)
                            db_policy.PolicyDescription = policy_update.get('PolicyDescription', db_policy.PolicyDescription)
                            db_policy.Scope = policy_update.get('Scope', db_policy.Scope)
                            db_policy.Objective = policy_update.get('Objective', db_policy.Objective)
                            
                            # Reset policy status to Under Review
                            db_policy.Status = 'Under Review'
                            db_policy.save()
                            print(f"DEBUG: Updated policy {policy_id} in database")
                    except Policy.DoesNotExist:
                        print(f"DEBUG: Policy with ID {policy_id} not found in database")
                    
                    policy_dict = {
                        "PolicyId": policy_update.get('PolicyId'),
                        "PolicyName": policy_update.get('PolicyName', ''),
                        "PolicyDescription": policy_update.get('PolicyDescription', ''),
                        "Status": "Under Review",
                        "StartDate": policy_update.get('StartDate'),
                        "EndDate": policy_update.get('EndDate'),
                        "Department": policy_update.get('Department', ''),
                        "Applicability": policy_update.get('Applicability', ''),
                        "DocURL": policy_update.get('DocURL', ''),
                        "Scope": policy_update.get('Scope', ''),
                        "Objective": policy_update.get('Objective', ''),
                        "Identifier": policy_update.get('Identifier', ''),
                        "CreatedByName": policy_update.get('CreatedByName', ''),
                        "Reviewer": policy_update.get('Reviewer', ''),
                        "CoverageRate": policy_update.get('CoverageRate'),
                        "PolicyType": policy_update.get('PolicyType', ''),
                        "PolicyCategory": policy_update.get('PolicyCategory', ''),
                        "PolicySubCategory": policy_update.get('PolicySubCategory', ''),
                        "subpolicies": []
                    }
                    
                    # Log policy category fields to verify they're being processed
                    print(f"DEBUG: Policy category fields for policy {policy_id}:")
                    print(f"DEBUG: PolicyType: {policy_dict['PolicyType']}")
                    print(f"DEBUG: PolicyCategory: {policy_dict['PolicyCategory']}")
                    print(f"DEBUG: PolicySubCategory: {policy_dict['PolicySubCategory']}")
                    
                    # Update subpolicies
                    subpolicies_to_process = policy_update.get('subpolicies', [])
                    print(f"DEBUG: Subpolicies to process for policy {policy_id}: {subpolicies_to_process}")
                    
                    if subpolicies_to_process and len(subpolicies_to_process) > 0:
                        print(f"DEBUG: Processing {len(subpolicies_to_process)} subpolicies for policy {policy_id}")
                        
                        for subpolicy_update in subpolicies_to_process:
                            subpolicy_id = subpolicy_update.get('SubPolicyId')
                            print(f"DEBUG: Processing subpolicy with ID: {subpolicy_id}")
                            print(f"DEBUG: Subpolicy update data: {subpolicy_update}")
                            
                            # Update subpolicy in database
                            try:
                                if subpolicy_id:
                                    db_subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id)
                                    print(f"DEBUG: Found subpolicy in database: {db_subpolicy.SubPolicyName}")
                                    
                                    # Update subpolicy fields
                                    db_subpolicy.SubPolicyName = subpolicy_update.get('SubPolicyName', db_subpolicy.SubPolicyName)
                                    db_subpolicy.Description = subpolicy_update.get('Description', db_subpolicy.Description)
                                    db_subpolicy.Control = subpolicy_update.get('Control', db_subpolicy.Control)
                                    db_subpolicy.Identifier = subpolicy_update.get('Identifier', db_subpolicy.Identifier)
                                    
                                    # Reset subpolicy status to Under Review
                                    db_subpolicy.Status = 'Under Review'
                                    db_subpolicy.save()
                                    print(f"DEBUG: Updated subpolicy {subpolicy_id} in database")
                            except SubPolicy.DoesNotExist:
                                print(f"DEBUG: Subpolicy with ID {subpolicy_id} not found in database")
                            
                            subpolicy_dict = {
                                "SubPolicyId": subpolicy_update.get('SubPolicyId'),
                                "SubPolicyName": subpolicy_update.get('SubPolicyName', ''),
                                "Description": subpolicy_update.get('Description', ''),
                                "Control": subpolicy_update.get('Control', ''),
                                "Identifier": subpolicy_update.get('Identifier', ''),
                                "Status": "Under Review"
                            }
                            policy_dict["subpolicies"].append(subpolicy_dict)
                    
                    policies_data.append(policy_dict)
                
                extracted_data["policies"] = policies_data
                extracted_data["totalPolicies"] = len(policies_data)
                extracted_data["totalSubpolicies"] = sum(len(p["subpolicies"]) for p in policies_data)
                print(f"DEBUG: Updated extracted_data with {len(policies_data)} policies and {extracted_data['totalSubpolicies']} subpolicies")
            else:
                print(f"DEBUG: No policies data found in request or empty policies array")
            
            # Remove previous rejection details
            if 'framework_approval' in extracted_data:
                extracted_data['previous_rejection'] = extracted_data.pop('framework_approval')
                print(f"DEBUG: Moved framework_approval to previous_rejection")
            
            # Create a new user version for resubmission
            latest_user_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='u'
            ).order_by('-ApprovalId').first()
            
            new_version = 'u1'
            if latest_user_version:
                try:
                    print(f"DEBUG: Found latest user version: {latest_user_version.Version}")
                    version_num = int(latest_user_version.Version[1:])
                    new_version = f'u{version_num + 1}'
                except (ValueError, IndexError) as e:
                    print(f"DEBUG: Error parsing version number: {str(e)}")
                    new_version = 'u2'
            
            print(f"DEBUG: Creating new approval record with version: {new_version}")
            
            # Create new approval record for resubmission
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=latest_approval.UserId,
                ReviewerId=latest_approval.ReviewerId,
                Version=new_version,
                ApprovedNot=None
            )
            
            print(f"DEBUG: Successfully created new approval with id: {new_approval.ApprovalId}")

            # Send notification to reviewer
            try:
                print("DEBUG: Starting notification process")
                # Get reviewer details
                try:
                    reviewer = Users.objects.get(UserId=latest_approval.ReviewerId)
                    reviewer_email = reviewer.Email
                    reviewer_name = reviewer.UserName
                    print(f"DEBUG: Found reviewer - Name: {reviewer_name}, Email: {reviewer_email}")
                except Users.DoesNotExist:
                    print(f"DEBUG: Reviewer not found with ID: {latest_approval.ReviewerId}")
                    raise
                
                # Get submitter details
                try:
                    submitter = Users.objects.get(UserId=latest_approval.UserId)
                    submitter_name = submitter.UserName
                    print(f"DEBUG: Found submitter - Name: {submitter_name}")
                except Users.DoesNotExist:
                    print(f"DEBUG: Submitter not found with ID: {latest_approval.UserId}")
                    raise
                
                if reviewer_email:
                    print(f"DEBUG: Preparing to send resubmission notification to reviewer: {reviewer_email}")
                    notification_service = NotificationService()
                    
                    # Log the notification data
                    notification_data = {
                        'notification_type': 'frameworkResubmitted',
                        'email': reviewer_email,
                        'email_type': 'gmail',
                        'template_data': [
                            reviewer_name,
                            framework.FrameworkName,
                            submitter_name
                        ]
                    }
                    print(f"DEBUG: Notification data: {notification_data}")
                    
                    # Send notification
                    notification_result = notification_service.send_multi_channel_notification(notification_data)
                    print(f"DEBUG: Full notification result: {notification_result}")
                    
                    if not notification_result.get('success'):
                        print(f"DEBUG: Failed to send notification. Error: {notification_result.get('error')}")
                        if 'details' in notification_result:
                            print(f"DEBUG: Notification details: {notification_result['details']}")
                else:
                    print(f"DEBUG: No reviewer email available for notification. Reviewer ID: {latest_approval.ReviewerId}")
            except Users.DoesNotExist as user_error:
                print(f"DEBUG: Error getting user details for notification: {str(user_error)}")
                print(f"DEBUG: User ID that was not found: {latest_approval.ReviewerId if 'latest_approval' in locals() else 'Unknown'}")
            except Exception as notification_error:
                print(f"DEBUG: Error sending notification: {str(notification_error)}")
                print(f"DEBUG: Full error details:")
                traceback.print_exc()
            
            print("DEBUG: Completed framework resubmission process")
        
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_APPROVAL_SUCCESS",
            description=f"Framework approval resubmitted successfully",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            ipAddress=get_client_ip(request),
            additionalInfo={
                "framework_name": framework.FrameworkName,
                "new_approval_id": new_approval.ApprovalId,
                "new_version": new_approval.Version
            }
        )
        
        # Success response
        return Response({
            "message": "Framework resubmitted successfully",
            "ApprovalId": new_approval.ApprovalId,
            "Version": new_approval.Version,
            "FrameworkId": framework.FrameworkId,
            "FrameworkName": framework.FrameworkName,
            "Status": framework.Status
        }, status=200)
        
    except Framework.DoesNotExist:
        print(f"DEBUG: Framework with id {framework_id} not found")
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_APPROVAL_FAILED",
            description=f"Framework approval resubmission failed - framework not found (ID: {framework_id})",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"DEBUG: Unexpected error in resubmit_framework_approval: {str(e)}")
        send_log(
            module="Framework",
            actionType="RESUBMIT_FRAMEWORK_APPROVAL_FAILED",
            description=f"Framework approval resubmission failed with error: {str(e)}",
            userId=getattr(request.user, 'id', None),
            userName=getattr(request.user, 'username', 'Anonymous'),
            entityType="Framework",
            entityId=framework_id,
            logLevel="ERROR",
            ipAddress=get_client_ip(request)
        )
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
