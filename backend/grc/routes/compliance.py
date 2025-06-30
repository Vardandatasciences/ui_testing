from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import datetime
import traceback

from ..serializers import ComplianceSerializer, PolicyApprovalSerializer
from ..models import SubPolicy, PolicyApproval, Compliance

@api_view(['POST'])
@permission_classes([AllowAny])
def add_compliance(request, subpolicy_id):
    """
    Add a new compliance item to a subpolicy
    """
    try:
        with transaction.atomic():
            # Get the subpolicy
            subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
            
            # Copy request data and add subpolicy_id
            data = request.data.copy()
            data['SubPolicyId'] = subpolicy_id
            
            # Set default values if not provided
            data.setdefault('Status', 'Under Review')
            data.setdefault('ActiveInactive', 'Active')
            data.setdefault('CreatedByDate', datetime.date.today())
            data.setdefault('ComplianceVersion', '1.0')
            
            # Create the compliance item
            compliance_serializer = ComplianceSerializer(data=data)
            if not compliance_serializer.is_valid():
                return Response(compliance_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            compliance = compliance_serializer.save()
            
            # Create extracted data for PolicyApproval
            extracted_data = {
                'type': 'compliance',
                'ComplianceItemDescription': compliance.ComplianceItemDescription,
                'Criticality': compliance.Criticality,
                'Impact': compliance.Impact,
                'Probability': compliance.Probability,
                'mitigation': compliance.mitigation,
                'PossibleDamage': compliance.PossibleDamage,
                'IsRisk': compliance.IsRisk,
                'MandatoryOptional': compliance.MandatoryOptional,
                'ManualAutomatic': compliance.ManualAutomatic,
                'CreatedByName': compliance.CreatedByName,
                'CreatedByDate': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
                'Status': compliance.Status,
                'ComplianceId': compliance.ComplianceId,
                'ComplianceVersion': compliance.ComplianceVersion,
                'SubPolicyId': subpolicy_id
            }
            
            # Create the PolicyApproval entry with version u1
            policy_approval = PolicyApproval(
                PolicyId=subpolicy.PolicyId,  # Associate with the parent policy
                ExtractedData=extracted_data,
                UserId=data.get('UserId', 1),  # Default to user 1 if not provided
                ReviewerId=data.get('ReviewerId', 1),  # Default to reviewer 1 if not provided
                Version='u1',
                ApprovedNot=None  # Not yet approved
            )
            policy_approval.save()
            
            return Response({
                'message': 'Compliance added to subpolicy successfully',
                'ComplianceId': compliance.ComplianceId,
                'ComplianceVersion': compliance.ComplianceVersion,
                'ApprovalVersion': 'u1'
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error adding compliance to subpolicy', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_compliance_version(request, compliance_id):
    """
    Get the latest version of a compliance item from the policy approvals table
    """
    try:
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Find the latest approval version from the database
        latest_approval = PolicyApproval.objects.filter(
            ExtractedData__ComplianceId=compliance_id
        ).order_by('-Version').first()
        
        # Extract the latest version from policy approvals
        if latest_approval and latest_approval.Version:
            # If version starts with 'u', return it
            if latest_approval.Version.startswith('u'):
                version = latest_approval.Version
            else:
                # Check if there are any user versions (u1, u2, etc.)
                user_approvals = PolicyApproval.objects.filter(
                    ExtractedData__ComplianceId=compliance_id,
                    Version__startswith='u'
                ).order_by('-Version')
                
                if user_approvals.exists():
                    version = user_approvals.first().Version
                else:
                    version = 'u1'  # Default if no user versions found
        else:
            # If no approvals found, default to u1
            version = 'u1'
        
        return Response({
            'compliance_id': compliance_id,
            'version': version
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_reviewer_version(request, compliance_id):
    """
    Get the latest reviewer version (R1, R2, etc.) for a compliance item
    and return the complete policy approval data for that version
    """
    try:
        latest_r_version = 'R1'  # Default if no reviewer versions found
        approval_data = None
        
        # Find the latest R version for a compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Use Python filtering to find R versions
        r_approvals = []
        all_approvals = PolicyApproval.objects.filter(
            ExtractedData__ComplianceId=compliance_id
        ).order_by('-Version')
        
        for approval in all_approvals:
            if approval.Version and approval.Version.startswith('R'):
                r_approvals.append(approval)
        
        if r_approvals:
            # Get the latest policy approval with R version
            latest_approval = r_approvals[0]
            latest_r_version = latest_approval.Version
            
            # Serialize the policy approval data
            serializer = PolicyApprovalSerializer(latest_approval)
            approval_data = serializer.data
        
        # Return the version and approval data
        return Response({
            'compliance_id': compliance_id,
            'version': latest_r_version,
            'approval_data': approval_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_compliance_approvals(request):
    """
    Get all compliance items with 'Under Review' status from both PolicyApproval and Compliance tables
    """
    try:
        # Get all compliance records directly from Compliance table with Under Review status
        under_review_compliances = Compliance.objects.filter(Status__icontains='review')
        
        # Also find all policy approvals with compliance type and Under Review status
        pending_approvals = PolicyApproval.objects.filter(
            ExtractedData__type='compliance'
        ).order_by('-Version')
        
        # Use a set to track which compliance items we've already included
        processed_compliance_ids = set()
        filtered_approvals = []
        
        # First, process direct compliance items
        for compliance in under_review_compliances:
            if compliance.ComplianceId not in processed_compliance_ids:
                processed_compliance_ids.add(compliance.ComplianceId)
                
                # Find or create a PolicyApproval for this compliance
                approval = PolicyApproval.objects.filter(
                    ExtractedData__ComplianceId=compliance.ComplianceId
                ).first()
                
                if approval:
                    # Use existing approval
                    filtered_approvals.append(approval)
                else:
                    # Create a temporary PolicyApproval object to represent this compliance
                    # This will have a real database ApprovalId that can be used for PUT requests
                    extracted_data = {
                        'type': 'compliance',
                        'ComplianceItemDescription': compliance.ComplianceItemDescription,
                        'ComplianceId': compliance.ComplianceId,
                        'Criticality': compliance.Criticality,
                        'Impact': compliance.Impact,
                        'Probability': compliance.Probability,
                        'mitigation': compliance.mitigation,
                        'PossibleDamage': compliance.PossibleDamage,
                        'Status': compliance.Status,
                        'CreatedByName': compliance.CreatedByName,
                        'CreatedByDate': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
                        'Identifier': compliance.Identifier
                    }
                    
                    # Create a real PolicyApproval record that can be referenced later
                    # Find the parent policy through the subpolicy
                    subpolicy = SubPolicy.objects.get(SubPolicyId=compliance.SubPolicyId.SubPolicyId)
                    
                    new_approval = PolicyApproval.objects.create(
                        PolicyId=subpolicy.PolicyId,
                        ExtractedData=extracted_data,
                        UserId=1,  # Default user
                        ReviewerId=2,  # Default reviewer
                        Version='u1',
                        ApprovedNot=None
                    )
                    filtered_approvals.append(new_approval)
        
        # Then process policy approvals
        for approval in pending_approvals:
            if not approval.ExtractedData:
                continue
                
            # Extract the compliance ID
            compliance_id = None
            if 'ComplianceId' in approval.ExtractedData:
                compliance_id = approval.ExtractedData['ComplianceId']
            elif 'compliance_id' in approval.ExtractedData:
                compliance_id = approval.ExtractedData['compliance_id']
            elif 'Identifier' in approval.ExtractedData:
                compliance_id = approval.ExtractedData['Identifier']
            
            # Check status - case insensitive matching for "under review"
            status_value = approval.ExtractedData.get('Status', '')
            is_under_review = False
            
            if status_value:
                is_under_review = 'review' in status_value.lower()
            
            # If we haven't seen this compliance item before and it's under review, add it to our results
            if compliance_id and compliance_id not in processed_compliance_ids and (is_under_review or approval.ApprovedNot is None):
                processed_compliance_ids.add(compliance_id)
                # Make sure Status is set properly for frontend
                if 'Status' not in approval.ExtractedData or not approval.ExtractedData['Status']:
                    approval.ExtractedData['Status'] = 'Under Review'
                filtered_approvals.append(approval)
        
        # For policy approval objects, serialize them properly
        serialized_approvals = []
        for approval in filtered_approvals:
            # It's a PolicyApproval object
            serializer = PolicyApprovalSerializer(approval)
            serialized_approvals.append(serializer.data)
        
        return Response(serialized_approvals, status=status.HTTP_200_OK)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error retrieving pending compliance approvals', 'details': error_info}, 
                      status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_compliance_review(request, approval_id):
    """
    Submit a review for a compliance item
    """
    try:
        # Get the policy approval
        approval = get_object_or_404(PolicyApproval, pk=approval_id)
        
        # Update the approval data
        if 'ExtractedData' in request.data:
            approval.ExtractedData = request.data['ExtractedData']
        
        if 'ApprovedNot' in request.data:
            approval.ApprovedNot = request.data['ApprovedNot']
        
        # Save the updated approval
        approval.save()
        
        # Also update the corresponding compliance record if it exists
        compliance_id = None
        if 'ComplianceId' in approval.ExtractedData:
            compliance_id = approval.ExtractedData['ComplianceId']
        elif 'compliance_id' in approval.ExtractedData:
            compliance_id = approval.ExtractedData['compliance_id']
        
        if compliance_id:
            try:
                compliance = Compliance.objects.get(ComplianceId=compliance_id)
                # Update compliance status to match approval
                if approval.ApprovedNot is True:
                    compliance.Status = 'Approved'
                elif approval.ApprovedNot is False:
                    compliance.Status = 'Rejected'
                compliance.save()
            except Compliance.DoesNotExist:
                # Compliance record doesn't exist or ID is invalid, just continue
                pass
        
        return Response({
            'message': 'Compliance review submitted successfully',
            'ApprovalId': approval_id
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Error submitting compliance review: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_compliance_approval(request, approval_id):
    """
    Resubmit a rejected compliance for review
    """
    try:
        # Get the policy approval
        approval = get_object_or_404(PolicyApproval, pk=approval_id)
        
        # Update the extracted data
        if 'ExtractedData' in request.data:
            approval.ExtractedData = request.data['ExtractedData']
        
        # Reset approval status
        approval.ApprovedNot = None
        
        # Update status in extracted data
        if approval.ExtractedData and 'Status' in approval.ExtractedData:
            approval.ExtractedData['Status'] = 'Under Review'
        
        # Create a new version if needed (increment the user version)
        current_version = approval.Version
        if current_version and current_version.startswith('u'):
            # Try to extract the number part
            try:
                version_num = int(current_version[1:])
                approval.Version = f'u{version_num + 1}'
            except ValueError:
                # If version doesn't follow expected format, just set to u1
                approval.Version = 'u1'
        else:
            # If not a user version, start with u1
            approval.Version = 'u1'
        
        # Save the updated approval
        approval.save()
        
        # Also update the compliance if it exists
        compliance_id = None
        if 'ComplianceId' in approval.ExtractedData:
            compliance_id = approval.ExtractedData['ComplianceId']
        elif 'compliance_id' in approval.ExtractedData:
            compliance_id = approval.ExtractedData['compliance_id']
        
        if compliance_id:
            try:
                compliance = Compliance.objects.get(ComplianceId=compliance_id)
                # Update compliance data from ExtractedData
                compliance.ComplianceItemDescription = approval.ExtractedData.get('ComplianceItemDescription', compliance.ComplianceItemDescription)
                compliance.Criticality = approval.ExtractedData.get('Criticality', compliance.Criticality)
                compliance.Impact = approval.ExtractedData.get('Impact', compliance.Impact)
                compliance.Probability = approval.ExtractedData.get('Probability', compliance.Probability)
                compliance.mitigation = approval.ExtractedData.get('mitigation', compliance.mitigation)
                compliance.Status = 'Under Review'
                compliance.save()
            except Compliance.DoesNotExist:
                # Compliance doesn't exist, just continue
                pass
        
        return Response({
            'message': 'Compliance resubmitted successfully',
            'ApprovalId': approval_id,
            'new_version': approval.Version
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Error resubmitting compliance: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_compliance_status(request, compliance_id):
    """
    Get the status of a compliance item directly from the Compliance table
    """
    try:
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        return Response({
            'compliance_id': compliance_id,
            'status': compliance.Status
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST) 