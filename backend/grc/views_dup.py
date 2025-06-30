from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework import viewsets
from .models import Risk
from .serializers import RiskSerializer
from .serializers import UserSerializer, RiskWorkflowSerializer
from rest_framework import viewsets
from .models import Risk, RiskAssignment
from .serializers import RiskSerializer, RiskInstanceSerializer
from .models import Incident
from .serializers import IncidentSerializer
from .models import Compliance
from .serializers import ComplianceSerializer
from .models import RiskInstance
from .serializers import RiskInstanceSerializer
from .slm_service import analyze_security_incident
from django.http import JsonResponse
from django.db.models import Count, Q
from .slm_service import analyze_security_incident
from django.contrib.auth.models import User
import datetime
import json
import traceback
from rest_framework import generics
from .models import GRCLog
from .serializers import GRCLogSerializer
import os
import base64
import tempfile
from .s3_fucntions import S3Client
from .export_service import export_data
from .notification_service import NotificationService
from datetime import datetime

# Create your views here.



import requests

LOGGING_SERVICE_URL = "http://localhost:4000/api/logs"

def send_log(module, actionType, description=None, userId=None, userName=None,
             userRole=None, entityType=None, logLevel='INFO', ipAddress=None,
             additionalInfo=None, entityId=None):
    
    # Create log entry in database
    try:
        # Prepare data for GRCLog model
        log_data = {
            'Module': module,
            'ActionType': actionType,
            'Description': description,
            'UserId': userId,
            'UserName': userName,
            'EntityType': entityType,
            'EntityId': entityId,
            'LogLevel': logLevel,
            'IPAddress': ipAddress,
            'AdditionalInfo': additionalInfo
        }
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        # Create and save the log entry
        log_entry = GRCLog(**log_data)
        log_entry.save()
        
        # Optionally still send to logging service if needed
        try:
            if LOGGING_SERVICE_URL:
                # Format for external service (matches expected format in loggingservice.js)
                api_log_data = {
                    "module": module,
                    "actionType": actionType,  # This is exactly what the service expects
                    "description": description,
                    "userId": userId,
                    "userName": userName,
                    "userRole": userRole,
                    "entityType": entityType,
                    "logLevel": logLevel,
                    "ipAddress": ipAddress,
                    "additionalInfo": additionalInfo
                }
                # Clean out None values
                api_log_data = {k: v for k, v in api_log_data.items() if v is not None}
                
                response = requests.post(LOGGING_SERVICE_URL, json=api_log_data)
                if response.status_code != 200:
                    print(f"Failed to send log to service: {response.text}")
        except Exception as e:
            print(f"Error sending log to service: {str(e)}")
            
        return log_entry.LogId  # Return the ID of the created log
    except Exception as e:
        print(f"Error saving log to database: {str(e)}")
        # Try to capture the error itself
        try:
            error_log = GRCLog(
                Module=module,
                ActionType='LOG_ERROR',
                Description=f"Error logging {actionType} on {module}: {str(e)}",
                LogLevel='ERROR'
            )
            error_log.save()
        except:
            pass  # If we can't even log the error, just continue
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    send_log(
        module="Auth",
        actionType="LOGIN",
        description="User login attempt",
        userId=None,
        userName=request.data.get('email'),
        entityType="User"
    )
    
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Hardcoded credentials
    if email == "admin@example.com" and password == "password123":
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': email,
                'name': 'Admin User'
            }
        })
    else:
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    send_log(
        module="Auth",
        actionType="REGISTER",
        description="User registration attempt",
        userId=None,
        userName=request.data.get('username', ''),
        entityType="User"
    )
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def test_connection(request):
    send_log(
        module="System",
        actionType="TEST",
        description="API connection test",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None
    )
    
    return Response({"message": "Connection successful!"})

@api_view(['GET'])
def last_incident(request):
    send_log(
        module="Incident",
        actionType="VIEW",
        description="Viewing last incident",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Incident"
    )
    
    last = Incident.objects.order_by('-IncidentId').first()
    if last:
        serializer = IncidentSerializer(last)
        return Response(serializer.data)
    else:
        return Response({}, status=404)

@api_view(['GET'])
def get_compliance_by_incident(request, incident_id):
    send_log(
        module="Compliance",
        actionType="VIEW",
        description=f"Viewing compliance for incident {incident_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Compliance",
        additionalInfo={"incident_id": incident_id}
    )
    
    try:
        # Find the incident
        incident = Incident.objects.get(IncidentId=incident_id)
        
        # Find related compliance(s) where ComplianceId matches the incident's ComplianceId
        if incident.ComplianceId:
            compliance = Compliance.objects.filter(ComplianceId=incident.ComplianceId).first()
            if compliance:
                serializer = ComplianceSerializer(compliance)
                return Response(serializer.data)
        
        return Response({"message": "No related compliance found"}, status=404)
    except Incident.DoesNotExist:
        return Response({"message": "Incident not found"}, status=404)

@api_view(['GET'])
def get_risks_by_incident(request, incident_id):
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing risks for incident {incident_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Risk",
        additionalInfo={"incident_id": incident_id}
    )
    
    try:
        # Find the incident
        incident = Incident.objects.get(IncidentId=incident_id)
        
        # Get compliance ID from the incident
        compliance_id = incident.ComplianceId
        
        if compliance_id:
            # Find all risks with the same compliance ID
            risks = Risk.objects.filter(ComplianceId=compliance_id)
            
            if risks.exists():
                serializer = RiskSerializer(risks, many=True)
                return Response(serializer.data)
        
        return Response({"message": "No related risks found"}, status=404)
    except Incident.DoesNotExist:
        return Response({"message": "Incident not found"}, status=404)

class RiskViewSet(viewsets.ModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    
    def list(self, request):
        send_log(
            module="Risk",
            actionType="LIST",
            description="Viewing all risks",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk"
        )
        return super().list(request)
    
    def retrieve(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Viewing risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().retrieve(request, pk)
    
    def create(self, request):
        send_log(
            module="Risk",
            actionType="CREATE",
            description="Creating new risk",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk"
        )
        return super().create(request)
    
    def update(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="UPDATE",
            description=f"Updating risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().update(request, pk)
    
    def destroy(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="DELETE",
            description=f"Deleting risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().destroy(request, pk)

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    
    def list(self, request):
        send_log(
            module="Incident",
            actionType="LIST",
            description="Viewing all incidents",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident"
        )
        return super().list(request)
    
    def retrieve(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="VIEW",
            description=f"Viewing incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().retrieve(request, pk)
    
    def create(self, request):
        send_log(
            module="Incident",
            actionType="CREATE",
            description="Creating new incident",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident"
        )
        return super().create(request)
    
    def update(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="UPDATE",
            description=f"Updating incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().update(request, pk)
    
    def destroy(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="DELETE",
            description=f"Deleting incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().destroy(request, pk)

class ComplianceViewSet(viewsets.ModelViewSet):
    queryset = Compliance.objects.all()
    serializer_class = ComplianceSerializer
    lookup_field = 'ComplianceId'
    
    def list(self, request):
        send_log(
            module="Compliance",
            actionType="LIST",
            description="Viewing all compliances",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance"
        )
        return super().list(request)
    
    def retrieve(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="VIEW",
            description=f"Viewing compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().retrieve(request, ComplianceId=ComplianceId)
    
    def create(self, request):
        send_log(
            module="Compliance",
            actionType="CREATE",
            description="Creating new compliance",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance"
        )
        return super().create(request)
    
    def update(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="UPDATE",
            description=f"Updating compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().update(request, ComplianceId=ComplianceId)
    
    def destroy(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="DELETE",
            description=f"Deleting compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().destroy(request, ComplianceId=ComplianceId)

class DateFieldFixMixin:
    """
    A mixin to fix date field serialization issues.
    This ensures that date objects are properly converted to strings without timezone issues.
    """
    def get_serializer(self, *args, **kwargs):
        """Get the serializer but patch datetime fields to handle dates properly"""
        serializer = super().get_serializer(*args, **kwargs)
        return serializer

class RiskInstanceViewSet(DateFieldFixMixin, viewsets.ModelViewSet):
    queryset = RiskInstance.objects.all()
    serializer_class = RiskInstanceSerializer
    
    def create(self, request, *args, **kwargs):
        # Log the create operation
        send_log(
            module="Risk",
            actionType="CREATE",
            description="Creating new risk instance",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance"
        )
        
        print("Original request data:", request.data)
        
        # Create a mutable dictionary for our data
        mutable_data = {}
        
        # Copy all fields except RiskMitigation, RiskOwner, and RiskStatus
        for key, value in request.data.items():
            if key not in ['RiskMitigation', 'RiskOwner', 'RiskStatus']:
                mutable_data[key] = value
        
        # Handle RiskOwner (always set to "System Owner")
        mutable_data['RiskOwner'] = "System Owner"
        
        # Handle RiskStatus (always set to "Open")
        mutable_data['RiskStatus'] = "Open"
        
        # Handle RiskMitigation - convert to proper JSON format
        if 'RiskMitigation' in request.data and request.data['RiskMitigation']:
            mitigation = request.data['RiskMitigation']
            
            # If it's already a dict, use it directly
            if isinstance(mitigation, dict):
                mutable_data['RiskMitigation'] = mitigation
            
            # If it's a string, convert to numbered JSON format
            elif isinstance(mitigation, str):
                sentences = [s.strip() for s in mitigation.split('.') if s.strip()]
                mitigation_dict = {}
                for i, sentence in enumerate(sentences, 1):
                    mitigation_dict[str(i)] = sentence
                mutable_data['RiskMitigation'] = mitigation_dict
            
            # If it's a list, use numbered format
            elif isinstance(mitigation, list):
                mitigation_dict = {}
                for i, item in enumerate(mitigation, 1):
                    mitigation_dict[str(i)] = item
                mutable_data['RiskMitigation'] = mitigation_dict
            
            # Handle case where it's already a JSON string
            elif isinstance(mitigation, str) and (mitigation.startswith('{') or mitigation.startswith('[')):
                try:
                    import json
                    mitigation_data = json.loads(mitigation)
                    mutable_data['RiskMitigation'] = mitigation_data
                except json.JSONDecodeError:
                    # If not valid JSON, create a simple entry
                    mutable_data['RiskMitigation'] = {"1": mitigation}
        else:
            # Default empty object
            mutable_data['RiskMitigation'] = {}
        
        # Handle MitigationDueDate to ensure it's a proper date object
        if 'MitigationDueDate' in mutable_data and mutable_data['MitigationDueDate']:
            try:
                from datetime import datetime, date
                due_date = mutable_data['MitigationDueDate']
                
                # If it's already a date object, keep it
                if isinstance(due_date, date):
                    pass
                # If it's a datetime object, convert to date
                elif isinstance(due_date, datetime):
                    mutable_data['MitigationDueDate'] = due_date.date()
                # If it's a string, parse it
                elif isinstance(due_date, str):
                    # Try different formats
                    try:
                        # ISO format
                        parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        mutable_data['MitigationDueDate'] = parsed_date.date()
                    except ValueError:
                        try:
                            # Common date format
                            parsed_date = datetime.strptime(due_date, '%Y-%m-%d')
                            mutable_data['MitigationDueDate'] = parsed_date.date()
                        except ValueError:
                            # If all parsing fails, remove the field
                            print(f"Invalid date format: {due_date}, removing field")
                            mutable_data.pop('MitigationDueDate')
            except Exception as e:
                print(f"Error processing MitigationDueDate: {e}")
                mutable_data.pop('MitigationDueDate', None)
        
        print("Processed data:", mutable_data)
        
        # Replace the request data with our processed data
        request._full_data = mutable_data
        
        # Create the risk instance
        response = super().create(request, *args, **kwargs)
        
        # If creation was successful, send notification to risk managers
        if response.status_code == 201:  # 201 Created
            try:
                # Get the created risk instance
                risk_instance = RiskInstance.objects.get(RiskInstanceId=response.data['RiskInstanceId'])
                
                # Send notification to risk managers (assuming there's a designated email)
                notification_service = NotificationService()
                
                # Find risk managers to notify
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE designation = 'Manager' LIMIT 1")
                    risk_manager = cursor.fetchone()
                
                if risk_manager:
                    notification_data = {
                        'notification_type': 'riskIdentified',
                        'email': risk_manager[2],  # risk manager email
                        'email_type': 'gmail',
                        'template_data': [
                            risk_manager[1],  # risk manager name
                            risk_instance.RiskDescription or f"Risk #{risk_instance.RiskInstanceId}",  # risk title
                            risk_instance.Category or "Uncategorized",  # category
                            request.user.username if request.user.is_authenticated else "System User"  # creator name
                        ]
                    }
                    
                    notification_result = notification_service.send_multi_channel_notification(notification_data)
                    print(f"New risk notification result: {notification_result}")
            except Exception as e:
                print(f"Error sending new risk notification: {e}")
        
        return response

    def update(self, request, *args, **kwargs):
        # Log the update operation
        instance = self.get_object()
        send_log(
            module="Risk",
            actionType="UPDATE",
            description=f"Updating risk instance {instance.RiskInstanceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"risk_id": instance.RiskInstanceId}
        )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # Log the delete operation
        instance = self.get_object()
        send_log(
            module="Risk",
            actionType="DELETE",
            description=f"Deleting risk instance {instance.RiskInstanceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"risk_id": instance.RiskInstanceId}
        )
        
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
def analyze_incident(request):
    send_log(
        module="Incident",
        actionType="ANALYZE",
        description="Analyzing incident with SLM model",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Incident",
        additionalInfo={"title": request.data.get('title', '')}
    )
    
    incident_description = request.data.get('description', '')
    incident_title = request.data.get('title', '')
    
    # Combine title and description for better context

    print(incident_title)
    print(incident_description)
    full_incident = f"Title: {incident_title}\n\nDescription: {incident_description}"
    
    # Call the SLM function
    analysis_result = analyze_security_incident(incident_title)

    print(analysis_result)
    
    return Response(analysis_result)

def risk_metrics(request):
    # Log the metrics view
    send_log(
        module="Risk",
        actionType="VIEW",
        description="Viewing risk metrics dashboard",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMetrics"
    )
    
    # Get the category filter parameter
    category = request.GET.get('category', '')
    
    # Base queryset
    queryset = RiskInstance.objects.all()
    
    # Apply category filter if provided
    if category:
        queryset = queryset.filter(Category__icontains=category)
    
    # Get total count after filtering by category
    total_count = queryset.count()
    
    print(f"Category filter: '{category}', Total risk instances: {total_count}")
    
    # Default counts
    open_count = 0
    in_progress_count = 0
    closed_count = 0
    
    # Let's count by looking at the filtered data
    for instance in queryset:
        status = instance.RiskStatus.lower() if instance.RiskStatus else ""
        if status == "" or status is None:
            # If status is empty, count as open by default
            open_count += 1
        elif "open" in status:
            open_count += 1
        elif "progress" in status or "in prog" in status:
            in_progress_count += 1
        elif "closed" in status or "complete" in status:
            closed_count += 1
        else:
            # Any other status, count as open
            open_count += 1
    
    # Debug info
    print(f"Filtered - Total: {total_count}, Open: {open_count}, In Progress: {in_progress_count}, Closed: {closed_count}")
    
    return JsonResponse({
        'total': total_count,
        'open': open_count,
        'inProgress': in_progress_count,
        'closed': closed_count
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    send_log(
        module="User",
        actionType="VIEW",
        description="Viewing all users",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="User"
    )
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def risk_workflow(request):
    """Get all risk instances for the workflow view"""
    try:
        # Fetch all risk instances
        risk_instances = RiskInstance.objects.all()
        
        # Log the view action
        send_log(
            module="Risk",
            actionType="VIEW",
            description="User viewed risk workflow",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance"
        )
        
        # If there are no instances, print a debug message
        if not risk_instances.exists():
            print("No risk instances found in the database")
            
        data = []
        
        for risk in risk_instances:
            # Handle date objects properly
            mitigation_due_date = None
            if risk.MitigationDueDate:
                if hasattr(risk.MitigationDueDate, 'isoformat'):
                    mitigation_due_date = risk.MitigationDueDate.isoformat()
                else:
                    mitigation_due_date = risk.MitigationDueDate
                    
            # Create response data
            risk_data = {
                'RiskInstanceId': risk.RiskInstanceId,
                'RiskId': risk.RiskId,
                'RiskDescription': risk.RiskDescription,
                'Criticality': risk.Criticality,
                'Category': risk.Category,
                'RiskStatus': risk.RiskStatus,
                'RiskPriority': risk.RiskPriority,
                'RiskImpact': risk.RiskImpact,
                'MitigationDueDate': mitigation_due_date,
                'MitigationStatus': risk.MitigationStatus,
                'ReviewerCount': risk.ReviewerCount or 0,
                'assignedTo': None
            }
            
            # Try to find an assignment if possible
            try:
                if risk.RiskId:
                    risk_obj = Risk.objects.filter(RiskId=risk.RiskId).first()
                    if risk_obj:
                        assignment = RiskAssignment.objects.filter(risk=risk_obj).first()
                        if assignment:
                            risk_data['assignedTo'] = assignment.assigned_to.username
            except Exception as e:
                print(f"Error checking assignment: {e}")
                
            data.append(risk_data)
        
        # Print debug info
        print(f"Returning {len(data)} risk instances")
        return Response(data)
        
    except Exception as e:
        # Log the error
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Error viewing risk workflow: {str(e)}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            logLevel="ERROR"
        )
        print(f"Error in risk_workflow view: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def assign_risk_instance(request):
    """Assign a risk instance to a user from custom user table"""
    risk_id = request.data.get('risk_id')
    user_id = request.data.get('user_id')
    mitigations = request.data.get('mitigations')
    due_date = request.data.get('due_date')
    risk_form_details = request.data.get('risk_form_details')
    
    # Log the assignment request
    send_log(
        module="Risk",
        actionType="ASSIGN",
        description=f"Assigning risk {risk_id} to user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
    )
    
    if not risk_id or not user_id:
        return Response({'error': 'Risk ID and User ID are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # For custom users we don't use Django ORM
        # Just validate the user exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [user_id])
            user = cursor.fetchone()
        
        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        # Update risk instance with assigned user
        risk_instance.RiskOwner = user[1]  # user_name
        risk_instance.UserId = user_id
        risk_instance.RiskStatus = 'Assigned'  # Update to assigned status when admin assigns
        
        # Set form details if provided
        if risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Set mitigation due date if provided
        if due_date:
            from datetime import datetime, date
            try:
                # Convert to proper date object based on input type
                if isinstance(due_date, date):
                    risk_instance.MitigationDueDate = due_date
                elif isinstance(due_date, datetime):
                    risk_instance.MitigationDueDate = due_date.date()
                elif isinstance(due_date, str):
                    # Try different formats
                    try:
                        # ISO format
                        parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        risk_instance.MitigationDueDate = parsed_date.date()
                    except ValueError:
                        try:
                            # Common date format
                            parsed_date = datetime.strptime(due_date, '%Y-%m-%d')
                            risk_instance.MitigationDueDate = parsed_date.date()
                        except ValueError:
                            print(f"Invalid date format: {due_date}")
            except Exception as e:
                print(f"Error processing due date: {e}")
        
        # Save mitigations if provided
        if mitigations:
            print(f"Saving mitigations to RiskMitigation field: {mitigations}")
            # Store in RiskMitigation first
            risk_instance.RiskMitigation = mitigations
            # Also copy to ModifiedMitigations
            risk_instance.ModifiedMitigations = mitigations
        
        # Set default MitigationStatus
        risk_instance.MitigationStatus = 'Yet to Start'
        
        risk_instance.save()
        print(f"Risk instance updated successfully with mitigations: {risk_instance.RiskMitigation}")
        
        # Send notification to the assigned user
        try:
            notification_service = NotificationService()
            # Format due date for notification
            formatted_due_date = risk_instance.MitigationDueDate.strftime('%Y-%m-%d') if risk_instance.MitigationDueDate else "Not specified"
            
            # Send risk mitigation assignment notification
            notification_data = {
                'notification_type': 'riskMitigationAssigned',
                'email': user[2],  # user email
                'email_type': 'gmail',  # Use gmail as default
                'template_data': [
                    user[1],  # mitigator name
                    risk_instance.RiskDescription or f"Risk #{risk_id}",  # risk title
                    formatted_due_date  # due date
                ]
            }
            
            notification_result = notification_service.send_multi_channel_notification(notification_data)
            print(f"Notification result: {notification_result}")
        except Exception as e:
            print(f"Error sending notification: {e}")
        
        # Log success or failure
        if risk_instance:
            send_log(
                module="Risk",
                actionType="ASSIGN",
                description=f"Successfully assigned risk {risk_id} to user {user_id}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskInstance",
                additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
            )
            return Response({'success': True})
        else:
            send_log(
                module="Risk",
                actionType="ASSIGN",
                description=f"Failed to assign risk {risk_id}: {str(e)}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskInstance",
                logLevel="ERROR",
                additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
            )
            return Response({'error': str(e)}, status=500)
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error assigning risk: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_custom_users(request):
    """Get users from the custom user table"""
    send_log(
        module="User",
        actionType="VIEW",
        description="Viewing custom users",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="CustomUser"
    )
    
    try:
        # Using raw SQL query to fetch from your custom table
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM grc.users")
            columns = [col[0] for col in cursor.description]
            users = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return Response(users)
    except Exception as e:
        print(f"Error fetching custom users: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_user_risks(request, user_id):
    """Get all risks assigned to a specific user, including completed ones"""
    try:
        # Log the view action
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Viewing risks assigned to user {user_id}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"viewed_user_id": user_id}
        )
        
        # Query risks that have the specific user assigned
        risk_instances = RiskInstance.objects.filter(UserId=user_id)
        
        if not risk_instances.exists():
            print(f"No risk instances found for user {user_id}")
        
        data = []
        for risk in risk_instances:
            # Handle date objects properly
            mitigation_due_date = None
            if risk.MitigationDueDate:
                if hasattr(risk.MitigationDueDate, 'isoformat'):
                    mitigation_due_date = risk.MitigationDueDate.isoformat()
                else:
                    mitigation_due_date = risk.MitigationDueDate
            
            risk_data = {
                'RiskInstanceId': risk.RiskInstanceId,
                'RiskId': risk.RiskId,
                'RiskDescription': risk.RiskDescription,
                'Criticality': risk.Criticality,
                'Category': risk.Category,
                'RiskStatus': risk.RiskStatus,
                'RiskPriority': risk.RiskPriority,
                'RiskImpact': risk.RiskImpact,
                'UserId': risk.UserId,
                'RiskOwner': risk.RiskOwner,
                'MitigationDueDate': mitigation_due_date,
                'MitigationStatus': risk.MitigationStatus,
                'ReviewerCount': risk.ReviewerCount or 0
            }
            data.append(risk_data)
        
        # Sort by status - active tasks first, then completed tasks
        sorted_data = sorted(data, key=lambda x: (
            0 if x['RiskStatus'] == 'Work In Progress' else
            1 if x['RiskStatus'] == 'Under Review' else
            2 if x['RiskStatus'] == 'Revision Required' else
            3 if x['RiskStatus'] == 'Approved' else 4
        ))
        
        print(f"Returning {len(sorted_data)} risk instances for user {user_id}")
        return Response(sorted_data)
    
    except Exception as e:
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Error viewing user risks: {str(e)}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            logLevel="ERROR",
            additionalInfo={"viewed_user_id": user_id}
        )
        print(f"Error fetching user risks: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def update_risk_status(request):
    """Update the status of a risk instance"""
    risk_id = request.data.get('risk_id')
    status = request.data.get('status')
    
    # Log the status update request
    send_log(
        module="Risk",
        actionType="UPDATE",
        description=f"Updating risk {risk_id} status to {status}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id, "new_status": status}
    )
    
    if not risk_id or not status:
        return Response({'error': 'Risk ID and status are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update the status
        risk_instance.RiskStatus = status
        risk_instance.save()
        
        return Response({
            'success': True,
            'message': f'Risk status updated to {status}'
        })
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating risk status: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_risk_mitigations(request, risk_id):
    """Get mitigation steps for a specific risk"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing mitigations for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Check if there are mitigations in the RiskMitigation field
        if not risk_instance.RiskMitigation:
            # If no specific mitigation steps, create a generic one
            mitigations = [{
                "title": "Step 1",
                "description": "No detailed mitigation workflow available.",
                "status": "Not Started"
            }]
        else:
            # Try to parse the RiskMitigation field as JSON
            try:
                # Handle string format (most common case)
                if isinstance(risk_instance.RiskMitigation, str):
                    # Parse the JSON string
                    parsed_data = json.loads(risk_instance.RiskMitigation)
                    
                    # Handle numbered object format: {"1": "Step 1", "2": "Step 2", ...}
                    if isinstance(parsed_data, dict) and all(k.isdigit() or (isinstance(k, int)) for k in parsed_data.keys()):
                        mitigations = []
                        # Sort keys numerically
                        ordered_keys = sorted(parsed_data.keys(), key=lambda k: int(k) if isinstance(k, str) else k)
                        
                        for key in ordered_keys:
                            mitigations.append({
                                "title": f"Step {key}",
                                "description": parsed_data[key],
                                "status": "Not Started"
                            })
                    # Handle array format
                    elif isinstance(parsed_data, list):
                        mitigations = parsed_data
                    # Handle other object formats
                    else:
                        mitigations = [parsed_data]
                        
                # Handle direct object format (already parsed)
                elif isinstance(risk_instance.RiskMitigation, dict):
                    parsed_data = risk_instance.RiskMitigation
                    # Handle numbered object
                    if all(k.isdigit() or (isinstance(k, int)) for k in parsed_data.keys()):
                        mitigations = []
                        ordered_keys = sorted(parsed_data.keys(), key=lambda k: int(k) if isinstance(k, str) else k)
                        
                        for key in ordered_keys:
                            mitigations.append({
                                "title": f"Step {key}",
                                "description": parsed_data[key],
                                "status": "Not Started"
                            })
                    else:
                        mitigations = [parsed_data]
                        
                # Handle direct array format
                elif isinstance(risk_instance.RiskMitigation, list):
                    mitigations = risk_instance.RiskMitigation
                    
                # Handle unexpected format
                else:
                    mitigations = [{
                        "title": "Step 1",
                        "description": str(risk_instance.RiskMitigation),
                        "status": "Not Started"
                    }]
                    
            except json.JSONDecodeError:
                # If it's not valid JSON, create a single step with the text
                mitigations = [{
                    "title": "Step 1",
                    "description": risk_instance.RiskMitigation,
                    "status": "Not Started"
                }]
            except Exception as e:
                print(f"Error parsing mitigations: {e}")
                mitigations = [{
                    "title": "Step 1",
                    "description": f"Error parsing mitigation data: {str(e)}",
                    "status": "Error"
                }]
        
        # Add default fields if they're missing
        for i, step in enumerate(mitigations):
            if "title" not in step:
                step["title"] = f"Step {i+1}"
            if "description" not in step:
                step["description"] = "No description provided"
            if "status" not in step:
                step["status"] = "Not Started"
            # Set locked state based on previous steps
            step["locked"] = i > 0  # All steps except first are initially locked
        
        return Response(mitigations)
    
    except RiskInstance.DoesNotExist:
        return Response([{
            "title": "Error",
            "description": "Risk instance not found",
            "status": "Error"
        }], status=404)
    except Exception as e:
        print(f"Error fetching risk mitigations: {e}")
        return Response([{
            "title": "Error",
            "description": f"Server error: {str(e)}",
            "status": "Error"
        }], status=500)

@api_view(['POST'])
def update_mitigation_approval(request):
    """Update the approval status of a mitigation step"""
    approval_id = request.data.get('approval_id')
    mitigation_id = request.data.get('mitigation_id')
    approved = request.data.get('approved')
    remarks = request.data.get('remarks', '')
    
    send_log(
        module="Risk",
        actionType="APPROVE_MITIGATION",
        description=f"Updating mitigation approval for risk {approval_id}, mitigation {mitigation_id}, approved: {approved}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"approval_id": approval_id, "mitigation_id": mitigation_id, "approved": approved}
    )
    
    if not approval_id or not mitigation_id:
        return Response({'error': 'Approval ID and mitigation ID are required'}, status=400)
    
    try:
        # Get the latest approval record by RiskInstanceId
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest version for this risk
            cursor.execute("""
                SELECT ra.ExtractedInfo, ra.UserId, ra.ApproverId, ra.version 
                FROM grc.risk_approval ra
                WHERE ra.RiskInstanceId = %s
                ORDER BY 
                    CASE 
                        WHEN ra.version LIKE 'U%_update%' THEN 1
                        WHEN ra.version LIKE 'U%' THEN 2
                        WHEN ra.version LIKE 'R%_update%' THEN 3
                        WHEN ra.version LIKE 'R%' THEN 4
                        ELSE 5
                    END,
                    ra.version DESC
                LIMIT 1
            """, [approval_id])
            row = cursor.fetchone()
            
            if not row:
                return Response({'error': 'Approval record not found'}, status=404)
            
            import json
            extracted_info, user_id, approver_id, current_version = row[0], row[1], row[2], row[3]
            extracted_info_dict = json.loads(extracted_info)
            
            # Create a working copy to modify
            if 'mitigations' in extracted_info_dict and mitigation_id in extracted_info_dict['mitigations']:
                extracted_info_dict['mitigations'][mitigation_id]['approved'] = approved
                extracted_info_dict['mitigations'][mitigation_id]['remarks'] = remarks
                
                # Create an interim update version
                # If version already has _update suffix, don't add it again
                update_version = current_version + "_update" if "_update" not in current_version else current_version
                
                # Insert a new record with the interim version
                cursor.execute("""
                    INSERT INTO grc.risk_approval 
                    (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    approval_id,
                    update_version,
                    json.dumps(extracted_info_dict),
                    user_id,
                    approver_id
                ])
                
                return Response({
                    'success': True,
                    'message': f'Mitigation {mitigation_id} approval status updated'
                })
            else:
                return Response({'error': 'Mitigation ID not found in approval record'}, status=404)
    except Exception as e:
        print(f"Error updating mitigation approval: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def assign_reviewer(request):
    """Assign a reviewer to a risk instance and create approval record"""
    risk_id = request.data.get('risk_id')
    reviewer_id = request.data.get('reviewer_id')
    user_id = request.data.get('user_id')  # Current user/assigner ID
    mitigations = request.data.get('mitigations')  # Get mitigation data with status
    risk_form_details = request.data.get('risk_form_details', None)  # Get form details
    
    # Ensure user_id is a string for the logging service
    user_id_str = str(user_id) if user_id is not None else None
    
    # Log the reviewer assignment
    send_log(
        module="Risk",
        actionType="ASSIGN_REVIEWER",
        description=f"Assigning reviewer {reviewer_id} to risk {risk_id}",
        userId=user_id_str,  # Convert to string to avoid the error
        entityType="RiskApproval",
        additionalInfo={"risk_id": risk_id, "reviewer_id": reviewer_id}
    )
    
    if not risk_id or not reviewer_id or not user_id:
        return Response({'error': 'Risk ID, reviewer ID, and user ID are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update form details if provided
        if risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Validate reviewer exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [reviewer_id])
            reviewer = cursor.fetchone()
            
            cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [user_id])
            user = cursor.fetchone()
        
        if not reviewer:
            return Response({'error': 'Reviewer not found'}, status=404)
        
        # Update the risk instance status
        risk_instance.RiskStatus = 'Assigned'  # Keep as assigned
        risk_instance.MitigationStatus = 'Revision Required by Reviewer'  # User submitted, needs reviewer
        
        # Initialize ReviewerCount if it's None
        if risk_instance.ReviewerCount is None:
            risk_instance.ReviewerCount = 0
            
        # Increment reviewer count when assigning a reviewer
        risk_instance.ReviewerCount += 1
        
        risk_instance.save()
        
        # Determine the next version number (U1, U2, etc.)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT version FROM grc.risk_approval 
                WHERE RiskInstanceId = %s AND version LIKE 'U%%'
                ORDER BY CAST(SUBSTRING(version, 2) AS UNSIGNED) DESC
                LIMIT 1
            """, [risk_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                version = "U1"  # First user submission
            else:
                current_version = row[0]
                # Extract number part and increment
                if current_version.startswith('U'):
                    try:
                        number = int(current_version[1:])
                        version = f"U{number + 1}"
                    except ValueError:
                        version = "U1"
                else:
                    version = "U1"  # Fallback to U1
        
        # Create a simplified JSON structure for ExtractedInfo
        import json
        from datetime import datetime  # Import datetime here to avoid the error
        
        # Use the mitigation data provided, or get from the risk instance
        mitigation_steps = {}
        if mitigations:
            # Use the provided mitigations data but don't set 'approved' field for initial submission
            is_first_submission = version == "U1"
            
            for key, value in mitigations.items():
                # Handle case where value is a string
                if isinstance(value, str):
                    mitigation_steps[key] = {
                        "description": value,
                        "status": "Completed",
                        "comments": "",
                        "user_submitted_date": datetime.now().isoformat()
                    }
                else:
                    mitigation_steps[key] = {
                        "description": value.get("description", ""),
                        "status": value.get("status", "Completed"),
                        "comments": value.get("comments", ""),
                        "fileData": value.get("fileData", None),
                        "fileName": value.get("fileName", None),
                        "user_submitted_date": datetime.now().isoformat()  # Fixed: using datetime.now()
                    }
                    
                    # Only set approved field if this is not the first submission or the value is coming from a previous approval
                    if not is_first_submission and "approved" in value:
                        if isinstance(value["approved"], bool):
                            mitigation_steps[key]["approved"] = value["approved"]
                            mitigation_steps[key]["remarks"] = value.get("remarks", "")
        
        # Create the simplified JSON structure
        extracted_info = {
            "risk_id": risk_id,
            "mitigations": mitigation_steps,
            "version": version,
            "submission_date": datetime.now().isoformat(),
            "user_submitted_date": datetime.now().isoformat(),  # Fixed: using datetime.now()
            "risk_form_details": risk_form_details  # Add form details to ExtractedInfo
        }
        
        # If risk_form_details has user_submitted_date, make sure it's in the top level as well
        if risk_form_details and 'user_submitted_date' in risk_form_details:
            extracted_info["user_submitted_date"] = risk_form_details["user_submitted_date"]
        
        # Insert into risk_approval table with ApprovedRejected as NULL for new submissions
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO grc.risk_approval 
                (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId, ApprovedRejected)
                VALUES (%s, %s, %s, %s, %s, NULL)
                """,
                [
                    risk_id,
                    version,  # Use the version we calculated
                    json.dumps(extracted_info),
                    user_id,
                    reviewer_id
                ]
            )
        
        # Send notification to reviewer about new mitigation to review
        try:
            notification_service = NotificationService()
            
            # Calculate review due date (5 days from now)
            from datetime import timedelta  # Import timedelta here
            review_due_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
            
            notification_data = {
                'notification_type': 'riskMitigationCompleted',
                'email': reviewer[2],  # reviewer email
                'email_type': 'gmail',
                'template_data': [
                    reviewer[1],  # reviewer name
                    risk_instance.RiskDescription or f"Risk #{risk_id}",  # risk title
                    user[1],  # mitigator name
                    review_due_date  # review due date
                ]
            }
            
            notification_result = notification_service.send_multi_channel_notification(notification_data)
            print(f"Notification result: {notification_result}")
        except Exception as e:
            print(f"Error sending notification: {e}")
        
        return Response({
            'success': True,
            'message': f'Reviewer {reviewer[1]} assigned to risk and approval record created with version {version}'
        })
    except Exception as e:
        print(f"Error assigning reviewer: {e}")
        # Add traceback for more detailed error information
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_reviewer_tasks(request, user_id):
    """Get all risks where the user is assigned as a reviewer, including completed ones"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing reviewer tasks for user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"reviewer_id": user_id}
    )
    
    try:
        # Using raw SQL query to fetch from approval table
        from django.db import connection
        with connection.cursor() as cursor:
            # Modified query to reduce sorting memory usage
            # Get risk IDs first to reduce dataset size
            cursor.execute("""
                SELECT DISTINCT ra.RiskInstanceId
                FROM grc.risk_approval ra
                WHERE ra.ApproverId = %s
            """, [user_id])
            
            risk_ids = [row[0] for row in cursor.fetchall()]
            
            if not risk_ids:
                return Response([])
                
            # Fetch data for each risk ID individually to avoid large sorts
            reviewer_tasks = []
            
            for risk_id in risk_ids:
                cursor.execute("""
                    SELECT ra.RiskInstanceId, ra.ExtractedInfo, ra.UserId, ra.ApproverId, ra.version,
                           ri.RiskDescription, ri.Criticality, ri.Category, ri.RiskStatus, ri.RiskPriority 
                    FROM grc.risk_approval ra
                    JOIN grc.risk_instance ri ON ra.RiskInstanceId = ri.RiskInstanceId
                    WHERE ra.RiskInstanceId = %s AND ra.ApproverId = %s
                    ORDER BY ra.version DESC
                    LIMIT 1
                """, [risk_id, user_id])
                
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                if rows:
                    task = dict(zip(columns, rows[0]))
                    reviewer_tasks.append(task)
            
            # Sort the tasks in Python instead of in SQL
            reviewer_tasks.sort(key=lambda x: (
                0 if x['RiskStatus'] == 'Under Review' else
                1 if x['RiskStatus'] == 'Revision Required' else
                2 if x['RiskStatus'] == 'Work In Progress' else
                3 if x['RiskStatus'] == 'Approved' else 4,
                x['RiskInstanceId']
            ))
            
            # For each task, get the previous version data (if needed)
            # This is where we'll limit processing to reduce memory usage
            for task in reviewer_tasks:
                risk_id = task['RiskInstanceId']
                current_version = task['version']
                
                # Skip previous version lookup for approved or older tasks
                if task['RiskStatus'] in ['Approved', 'Completed']:
                    task['PreviousVersion'] = None
                    continue
                
                # Extract numeric part of version for comparison
                current_num = int(current_version[1:]) if current_version[1:].isdigit() else 0
                previous_num = current_num - 1
                
                # Determine the previous version format
                if current_version.startswith('U'):
                    previous_version = f"U{previous_num}" if previous_num > 0 else None
                elif current_version.startswith('R'):
                    previous_version = f"R{previous_num}" if previous_num > 0 else "U1"
                else:
                    previous_version = None
                
                # If we have a previous version to look for
                if previous_version:
                    cursor.execute("""
                        SELECT ExtractedInfo
                        FROM grc.risk_approval
                        WHERE RiskInstanceId = %s AND version = %s
                        LIMIT 1
                    """, [risk_id, previous_version])
                    prev_row = cursor.fetchone()
                    
                    if prev_row:
                        import json
                        try:
                            previous_data = json.loads(prev_row[0])
                            # Add previous version data to the task
                            task['PreviousVersion'] = previous_data
                        except json.JSONDecodeError:
                            task['PreviousVersion'] = None
                    else:
                        task['PreviousVersion'] = None
                else:
                    task['PreviousVersion'] = None
        
        return Response(reviewer_tasks)
    except Exception as e:
        print(f"Error fetching reviewer tasks: {e}")
        traceback.print_exc()  # Add traceback for better debugging
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def complete_review(request):
    """Complete the review process for a risk"""
    import json
    import datetime
    import traceback
    
    try:
        # Print request data for debugging
        print("Complete review request data:", request.data)
        
        approval_id = request.data.get('approval_id')  # This is RiskInstanceId
        risk_id = request.data.get('risk_id')
        approved = request.data.get('approved')
        mitigations = request.data.get('mitigations', {})  # Get all mitigations
        risk_form_details = request.data.get('risk_form_details', None)  # Get form details
        
        # Make sure we have the necessary data
        if not risk_id:
            print("Missing risk_id in request data")
            return Response({'error': 'Risk ID is required'}, status=400)
            
        # Set approval_id to risk_id if it's missing
        if not approval_id:
            approval_id = risk_id
        
        # Get the risk instance to update statuses
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update risk form details if approved
        if approved and risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Update risk status based on approval
        if approved:
            risk_instance.RiskStatus = 'Approved'
            risk_instance.MitigationStatus = 'Completed'
            # No need to increment reviewer count as this is the final approval
        else:
            risk_instance.RiskStatus = 'Assigned'  # Keep as assigned
            risk_instance.MitigationStatus = 'Revision Required by User'  # Reviewer submitted, needs user revision
            
            # Increment reviewer count only if not yet approved
            if risk_instance.ReviewerCount is None:
                risk_instance.ReviewerCount = 1
            else:
                risk_instance.ReviewerCount += 1
        
        risk_instance.save()
        
        # Get current approval record to get relevant data
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest version
            cursor.execute("""
                SELECT ExtractedInfo, UserId, ApproverId, version
                FROM grc.risk_approval
                WHERE RiskInstanceId = %s
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'Approval record not found'}, status=404)
                
            extracted_info, user_id, approver_id, current_version = row[0], row[1], row[2], row[3]
            
            # Get user and reviewer information for notification
            cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [user_id])
            user = cursor.fetchone()
            
            cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [approver_id])
            reviewer = cursor.fetchone()
            
            # Determine the next R version
            cursor.execute("""
                SELECT version FROM grc.risk_approval 
                WHERE RiskInstanceId = %s AND version LIKE 'R%%'
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            
            if not row or not row[0]:
                # First reviewer version
                new_version = "R1"
            else:
                # Get the next reviewer version
                current_r_version = row[0]
                try:
                    # Extract the number part
                    number = int(current_r_version[1:])
                    new_version = f"R{number + 1}"
                except ValueError:
                    new_version = "R1"
            
            # Create the new data structure directly matching your desired format
            extracted_info_dict = json.loads(extracted_info)
            
            # Build the new JSON structure with the exact format you want
            new_json = {
                "risk_id": int(risk_id) if isinstance(risk_id, str) and risk_id.isdigit() else risk_id,
                "version": new_version,
                "mitigations": {},
                "review_date": datetime.datetime.now().isoformat(),
                "reviewer_submitted_date": datetime.datetime.now().isoformat(),  # Add reviewer submission date
                "overall_approved": approved,
                "risk_form_details": risk_form_details or extracted_info_dict.get("risk_form_details", {})  # Include form details
            }
            
            # Add reviewer_submitted_date to risk_form_details if it exists
            if new_json["risk_form_details"]:
                new_json["risk_form_details"]["reviewer_submitted_date"] = datetime.datetime.now().isoformat()
            
            # Preserve the user_submitted_date for risk_form_details if it exists in the extracted_info
            if extracted_info_dict.get("risk_form_details", {}).get("user_submitted_date"):
                if not new_json["risk_form_details"]:
                    new_json["risk_form_details"] = {}
                new_json["risk_form_details"]["user_submitted_date"] = extracted_info_dict["risk_form_details"]["user_submitted_date"]
            elif extracted_info_dict.get("user_submitted_date"):
                if not new_json["risk_form_details"]:
                    new_json["risk_form_details"] = {}
                new_json["risk_form_details"]["user_submitted_date"] = extracted_info_dict["user_submitted_date"]
            
            # Copy the mitigations from the request
            for mitigation_id, mitigation_data in mitigations.items():
                # Include file data and comments in the stored JSON
                new_json["mitigations"][mitigation_id] = {
                    "description": mitigation_data["description"],
                    "approved": mitigation_data["approved"],
                    "remarks": mitigation_data["remarks"] if not mitigation_data["approved"] else "",
                    "comments": mitigation_data.get("comments", ""),
                    "fileData": mitigation_data.get("fileData", None),
                    "fileName": mitigation_data.get("fileName", None),
                    "reviewer_submitted_date": datetime.datetime.now().isoformat(),  # Add reviewer submission date
                    "user_submitted_date": mitigation_data.get("user_submitted_date", None)  # Preserve user submission date
                }
            
            # Insert new record with the R version and set ApprovedRejected column
            cursor.execute("""
                INSERT INTO grc.risk_approval 
                (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId, ApprovedRejected)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                risk_id,
                new_version,
                json.dumps(new_json),
                user_id,
                approver_id,
                "Approved" if approved else "Rejected"
            ])
            
            # Update the risk status based on approval
            risk_status = 'Approved' if approved else 'Revision Required'
            cursor.execute("""
                UPDATE grc.risk_instance
                SET RiskStatus = %s
                WHERE RiskInstanceId = %s
            """, [risk_status, risk_id])

            # Send notification to user about the review outcome
            try:
                notification_service = NotificationService()
                
                # Get first rejected mitigation remark for notification (if any)
                reviewer_comment = ""
                for mitigation_id, mitigation_data in mitigations.items():
                    if not mitigation_data.get("approved", True) and mitigation_data.get("remarks"):
                        reviewer_comment = mitigation_data.get("remarks")
                        break
                
                # Prepare notification data
                notification_data = {
                    'notification_type': 'complianceReviewed',  # Using compliance template for risk reviews
                    'email': user[2],  # user email
                    'email_type': 'gmail',
                    'template_data': [
                        user[1],  # officer name (user)
                        risk_instance.RiskDescription or f"Risk #{risk_id}",  # item title
                        "Approved" if approved else "Rejected",  # status
                        reviewer[1],  # reviewer name
                        reviewer_comment  # reviewer comments (if rejected)
                    ]
                }
                
                notification_result = notification_service.send_multi_channel_notification(notification_data)
                print(f"Notification result: {notification_result}")
            except Exception as e:
                print(f"Error sending notification: {e}")

        send_log(
            module="Risk",
            actionType="COMPLETE_REVIEW",
            description=f"Completing review for risk {risk_id} with status: {'Approved' if approved else 'Rejected'}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskApproval",
            additionalInfo={"risk_id": risk_id, "approved": approved}
        )
            
        return Response({
            'success': True,
            'message': f'Review completed and risk status updated to {risk_status} with version {new_version}'
        })
    except Exception as e:
        print(f"Error completing review: {e}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_user_notifications(request, user_id):
    """Get notifications for the user about their reviewed tasks"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing notifications for user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Notification",
        additionalInfo={"user_id": user_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version for each risk submitted by this user
            cursor.execute("""
                WITH latest_r_versions AS (
                    SELECT ra.RiskInstanceId, MAX(ra.version) as latest_version
                    FROM grc.risk_approval ra
                    WHERE ra.UserId = %s 
                    AND ra.version LIKE 'R%'
                    AND ra.version NOT LIKE '%update%'
                    GROUP BY ra.RiskInstanceId
                )
                SELECT ra.RiskInstanceId, ra.ExtractedInfo, ra.version,
                       ri.RiskDescription, ri.RiskStatus
                FROM grc.risk_approval ra
                JOIN latest_r_versions lrv ON ra.RiskInstanceId = lrv.RiskInstanceId AND ra.version = lrv.latest_version
                JOIN grc.risk_instance ri ON ra.RiskInstanceId = ri.RiskInstanceId
                WHERE ra.UserId = %s
            """, [user_id, user_id])
            columns = [col[0] for col in cursor.description]
            notifications = []
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                
                # Extract approval info
                extracted_info = json.loads(data['ExtractedInfo'])
                overall_approved = extracted_info.get('overall_approved', None)
                
                # Add approval status info
                data['approved'] = overall_approved
                notifications.append(data)
            
        return Response(notifications)
    except Exception as e:
        print(f"Error fetching user notifications: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def update_mitigation_status(request):
    """Update the mitigation status of a risk instance"""
    risk_id = request.data.get('risk_id')
    status = request.data.get('status')
    
    send_log(
        module="Risk",
        actionType="UPDATE",
        description=f"Updating mitigation status for risk {risk_id} to {status}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"risk_id": risk_id, "status": status}
    )
    
    # Debug information
    print(f"Received update_mitigation_status request: risk_id={risk_id}, status={status}")
    print(f"Request data: {request.data}")
    
    if not risk_id:
        return Response({'error': 'Risk ID is required'}, status=400)
    
    if not status:
        return Response({'error': 'Status is required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        old_status = risk_instance.MitigationStatus
        
        # Update the mitigation status
        risk_instance.MitigationStatus = status
        
        # If status is completed, also update risk status to approved
        if status == 'Completed':
            risk_instance.RiskStatus = 'Approved'
        
        risk_instance.save()
        print(f"Successfully updated risk {risk_id} mitigation status to {status}")
        
        # Send notification to risk managers about status change
        try:
            # Only send notification if the status has meaningfully changed
            if old_status != status:
                notification_service = NotificationService()
                
                # Find risk managers to notify
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE designation = 'Manager' LIMIT 1")
                    risk_manager = cursor.fetchone()
                    
                    # Also get the owner of the risk for notification
                    if risk_instance.UserId:
                        cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", 
                                      [risk_instance.UserId])
                        risk_owner = cursor.fetchone()
                    else:
                        risk_owner = None
                
                # Notify risk manager
                if risk_manager:
                    # Use riskScoreUpdated template (repurposed for status updates)
                    notification_data = {
                        'notification_type': 'riskScoreUpdated',
                        'email': risk_manager[2],  # risk manager email
                        'email_type': 'gmail',
                        'template_data': [
                            risk_manager[1],  # risk manager name
                            risk_instance.RiskDescription or f"Risk #{risk_id}",  # risk title
                            old_status or "Not Started",  # old status
                            status,  # new status
                            request.user.username if request.user.is_authenticated else "System User"  # actor name
                        ]
                    }
                    
                    notification_result = notification_service.send_multi_channel_notification(notification_data)
                    print(f"Status change notification to manager result: {notification_result}")
                
                # Also notify the risk owner if available and different from the updater
                if risk_owner and risk_owner[0] != request.user.id:
                    notification_data = {
                        'notification_type': 'riskScoreUpdated',
                        'email': risk_owner[2],  # risk owner email
                        'email_type': 'gmail',
                        'template_data': [
                            risk_owner[1],  # risk owner name
                            risk_instance.RiskDescription or f"Risk #{risk_id}",  # risk title
                            old_status or "Not Started",  # old status
                            status,  # new status
                            request.user.username if request.user.is_authenticated else "System User"  # actor name
                        ]
                    }
                    
                    notification_result = notification_service.send_multi_channel_notification(notification_data)
                    print(f"Status change notification to owner result: {notification_result}")
        except Exception as e:
            print(f"Error sending status change notification: {e}")
        
        return Response({
            'success': True,
            'message': f'Mitigation status updated to {status}'
        })
    except RiskInstance.DoesNotExist:
        print(f"Error: Risk instance with ID {risk_id} not found")
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating mitigation status: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_reviewer_comments(request, risk_id):
    """Get reviewer comments for rejected mitigations"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing reviewer comments for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version for this risk
            cursor.execute("""
                SELECT ra.ExtractedInfo
                FROM grc.risk_approval ra
                WHERE ra.RiskInstanceId = %s 
                AND ra.version LIKE 'R%%'
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({}, status=404)
            
            import json
            extracted_info = json.loads(row[0])
            
            comments = {}
            if 'mitigations' in extracted_info:
                for mitigation_id, mitigation_data in extracted_info['mitigations'].items():
                    # Only include rejected mitigations with remarks
                    if mitigation_data.get('approved') is False and mitigation_data.get('remarks'):
                        comments[mitigation_id] = mitigation_data['remarks']
            
            return Response(comments)
    except Exception as e:
        print(f"Error fetching reviewer comments: {e}")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_latest_review(request, risk_id):
    """Get the latest review data for a risk (latest R version)"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing latest review for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version of review data
            cursor.execute("""
                SELECT ExtractedInfo
                FROM grc.risk_approval
                WHERE RiskInstanceId = %s AND version LIKE 'R%%'
                ORDER BY 
                    CAST(SUBSTRING(version, 2) AS UNSIGNED) DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                # If no review found, return empty object
                return Response({})
            
            import json
            extracted_info = json.loads(row[0])
            print(extracted_info)
            return Response(extracted_info)
    except Exception as e:
        print(f"Error fetching latest review: {e}")
        traceback.print_exc()
        # Return empty object instead of error in case of exception
        return Response({})

@api_view(['GET'])
def get_assigned_reviewer(request, risk_id):
    """Get the assigned reviewer for a risk from the risk_approval table"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing assigned reviewer for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the ApproverId from any version (they should all have the same reviewer)
            cursor.execute("""
                SELECT ApproverId, user_name 
                FROM grc.risk_approval ra
                JOIN grc.users u ON ra.ApproverId = u.user_id
                WHERE ra.RiskInstanceId = %s
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({}, status=200)  # Return empty object with 200 status instead of 404
            
            return Response({
                'reviewer_id': row[0],
                'reviewer_name': row[1]
            })
    except Exception as e:
        print(f"Error fetching assigned reviewer: {e}")
        # Return empty object with 200 status instead of error
        return Response({}, status=200)

@api_view(['PUT'])
def update_risk_mitigation(request, risk_id):
    """Update the mitigation steps for a risk instance"""
    mitigation_data = request.data.get('mitigation_data')
    
    # Log the mitigation update
    send_log(
        module="Risk",
        actionType="UPDATE_MITIGATION",
        description=f"Updating mitigation data for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id}
    )
    
    if not mitigation_data:
        return Response({'error': 'Mitigation data is required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Only update the ModifiedMitigations field, keep RiskMitigation unchanged
        risk_instance.ModifiedMitigations = mitigation_data
        risk_instance.save()
        
        return Response({
            'success': True,
            'message': 'Modified mitigation data updated successfully'
        })
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating modified mitigation: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_risk_form_details(request, risk_id):
    """Get form details for a risk instance"""
    try:
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        form_details = risk_instance.RiskFormDetails
        
        # If no form details exist, return default empty structure
        if not form_details:
            form_details = {
                "cost": "",
                "impact": "",
                "financialImpact": "",
                "reputationalImpact": ""
            }
        
        return Response(form_details)
    except RiskInstance.DoesNotExist:
        return Response({"error": "Risk instance not found"}, status=404)
    except Exception as e:
        print(f"Error fetching risk form details: {e}")
        return Response({"error": str(e)}, status=500)

class GRCLogList(generics.ListCreateAPIView):
    queryset = GRCLog.objects.all().order_by('-Timestamp')
    serializer_class = GRCLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = GRCLog.objects.all().order_by('-Timestamp')
        
        # Filter by module if provided
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(Module__icontains=module)
            
        # Filter by action type if provided
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(ActionType__icontains=action_type)
            
        # Filter by entity type if provided
        entity_type = self.request.query_params.get('entity_type')
        if entity_type:
            queryset = queryset.filter(EntityType__icontains=entity_type)
            
        # Filter by log level if provided
        log_level = self.request.query_params.get('log_level')
        if log_level:
            queryset = queryset.filter(LogLevel__iexact=log_level)
            
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(UserId=user_id)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(Timestamp__range=[start_date, end_date])
            
        return queryset

class GRCLogDetail(generics.RetrieveAPIView):
    queryset = GRCLog.objects.all()
    serializer_class = GRCLogSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
def get_previous_versions(request, risk_id):
    """Get previous versions of a risk for comparison"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the second-most recent version (one before the current)
            cursor.execute("""
                SELECT ExtractedInfo
                FROM grc.risk_approval
                WHERE RiskInstanceId = %s
                ORDER BY 
                    CASE 
                        WHEN version LIKE 'U%_update%' THEN 1
                        WHEN version LIKE 'U%' THEN 2
                        WHEN version LIKE 'R%_update%' THEN 3
                        WHEN version LIKE 'R%' THEN 4
                        ELSE 5
                    END,
                    version DESC
                LIMIT 1 OFFSET 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({"message": "No previous versions found"}, status=200)
            
            import json
            extracted_info = json.loads(row[0])
            return Response(extracted_info)
    except Exception as e:
        print(f"Error fetching previous versions: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def save_uploaded_file(request):
    """Save uploaded file locally first, then upload to S3, and finally delete the local file"""
    try:
        # Extract data from request
        file_data = request.data.get('fileData')
        file_name = request.data.get('fileName')
        risk_id = request.data.get('riskId')
        category = request.data.get('category', 'general')
        mitigation_number = request.data.get('mitigationNumber', '1')
        
        # Validate required fields
        if not file_data or not file_name or not risk_id:
            return Response({'error': 'Missing required fields'}, status=400)
        
        # Create directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 's3_files')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create filename with the specified format
        file_extension = os.path.splitext(file_name)[1]
        new_file_name = f"{os.path.splitext(file_name)[0]}_{risk_id}_{category}_{mitigation_number}{file_extension}"
        file_path = os.path.join(upload_dir, new_file_name)
        
        # Extract and save the base64 data locally
        file_data = file_data.split(',')[1] if ',' in file_data else file_data
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(file_data))
        
        try:
            # Now upload to S3
            s3_client = S3Client(base_url="http://localhost:3000")
            
            # Upload to S3 with metadata
            upload_result = s3_client.upload_file(
                file_path=file_path,
                user_id=str(request.user.id if request.user.is_authenticated else "anonymous"),
                file_name=new_file_name,
                risk_id=str(risk_id),
                category=category,
                mitigation_number=str(mitigation_number)
            )
            
            if not upload_result.get('success'):
                return Response({'error': 'S3 upload failed', 'details': upload_result}, status=500)
            
            # Log the file upload
            send_log(
                module="Risk",
                actionType="FILE_UPLOAD",
                description=f"File uploaded to S3 for risk {risk_id}, mitigation {mitigation_number}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskMitigation",
                additionalInfo={"risk_id": risk_id, "file_name": new_file_name, "s3_file_id": upload_result.get('fileId')}
            )
            
            # Send notification to relevant parties about the file upload
            try:
                # Get risk instance to notify the owner
                risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
                
                # Find relevant people to notify
                from django.db import connection
                with connection.cursor() as cursor:
                    # Get the assigned reviewer
                    cursor.execute("""
                        SELECT ApproverId, u.user_name, u.email
                        FROM grc.risk_approval ra
                        JOIN grc.users u ON ra.ApproverId = u.user_id
                        WHERE ra.RiskInstanceId = %s
                        LIMIT 1
                    """, [risk_id])
                    reviewer = cursor.fetchone()
                    
                    # If there's a reviewer, notify them about the new file
                    if reviewer:
                        notification_service = NotificationService()
                        
                        notification_data = {
                            'notification_type': 'policyNewVersion',  # Repurposing this template for file upload notification
                            'email': reviewer[2],  # reviewer email
                            'email_type': 'gmail',
                            'template_data': [
                                reviewer[1],  # reviewer name
                                f"Supporting document for risk {risk_id}",  # title
                                "1.0",  # version
                                f"http://localhost:3000/file/{upload_result.get('fileId', 'unknown')}"  # link to file
                            ]
                        }
                        
                        notification_result = notification_service.send_multi_channel_notification(notification_data)
                        print(f"File upload notification result: {notification_result}")
            except Exception as e:
                print(f"Error sending file upload notification: {e}")
            
            return Response({
                'success': True,
                'message': 'File uploaded successfully to S3',
                'savedFileName': new_file_name,
                's3FileInfo': upload_result
            })
        finally:
            # Delete the local file after S3 upload (or if upload fails)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Local file {file_path} deleted successfully")
                except Exception as e:
                    print(f"Error deleting local file: {e}")
    except Exception as e:
        print(f"Error saving uploaded file: {e}")
        return Response({'error': str(e)}, status=500)

# Alternative implementation using the simple_upload method
@api_view(['POST'])
def save_uploaded_file_simple(request):
    """Save an uploaded file to S3 using the simple_upload method"""
    try:
        # Extract data from request
        file_data = request.data.get('fileData')
        file_name = request.data.get('fileName')
        risk_id = request.data.get('riskId')
        category = request.data.get('category', 'general')
        mitigation_number = request.data.get('mitigationNumber', '1')
        
        # Validate required fields
        if not file_data or not file_name or not risk_id:
            return Response({'error': 'Missing required fields'}, status=400)
        
        # Create custom filename with the specified format
        file_extension = os.path.splitext(file_name)[1]
        new_file_name = f"{os.path.splitext(file_name)[0]}_{risk_id}_{category}_{mitigation_number}{file_extension}"
        
        # Extract and save the base64 data to a temporary file
        file_data = file_data.split(',')[1] if ',' in file_data else file_data
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name
        
        try:
            # Write decoded base64 data to the temporary file
            with open(temp_file_path, 'wb') as f:
                f.write(base64.b64decode(file_data))
            
            # Rename the temp file to match our desired filename
            final_temp_path = os.path.join(os.path.dirname(temp_file_path), new_file_name)
            os.rename(temp_file_path, final_temp_path)
            
            # Initialize S3 client
            s3_client = S3Client(base_url="http://localhost:3000")
            
            # Upload using the simple method
            upload_result = s3_client.simple_upload(
                file_name=final_temp_path,
                user_id=str(request.user.id if request.user.is_authenticated else "anonymous")
            )
            
            if not upload_result.get('success'):
                return Response({'error': 'S3 upload failed', 'details': upload_result}, status=500)
            
            # Log the file upload
            send_log(
                module="Risk",
                actionType="FILE_UPLOAD",
                description=f"File uploaded to S3 for risk {risk_id}, mitigation {mitigation_number}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskMitigation",
                additionalInfo={"risk_id": risk_id, "file_name": new_file_name, "s3_file_id": upload_result.get('fileId')}
            )
            
            return Response({
                'success': True,
                'message': 'File uploaded successfully to S3',
                'savedFileName': new_file_name,
                's3FileInfo': upload_result
            })
            
        finally:
            # Clean up the temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(final_temp_path):
                os.unlink(final_temp_path)
                
    except Exception as e:
        print(f"Error saving uploaded file to S3: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def export_risks(request):
    """Export risk data to the specified format"""
    try:
        # Get request parameters
        file_format = request.data.get('format', 'xlsx')
        user_id = request.data.get('user_id', 'anonymous')
        risk_ids = request.data.get('risk_ids', [])
        
        # Log the export request
        send_log(
            module="Risk",
            actionType="EXPORT",
            description=f"Exporting risks to {file_format} format",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"format": file_format, "risk_ids": risk_ids}
        )
        
        # If risk_ids is provided, filter risks by those IDs
        if risk_ids:
            risk_instances = RiskInstance.objects.filter(RiskInstanceId__in=risk_ids)
        else:
            # Otherwise, get all risk instances
            risk_instances = RiskInstance.objects.all()
        
        # Convert to list of dictionaries for export
        risk_data = []
        for risk in risk_instances:
            risk_data.append({
                'RiskInstanceId': risk.RiskInstanceId,
                'RiskDescription': risk.RiskDescription,
                'Category': risk.Category,
                'Criticality': risk.Criticality,
                'RiskStatus': risk.RiskStatus,
                'RiskPriority': risk.RiskPriority,
                'RiskOwner': risk.RiskOwner,
                'MitigationStatus': risk.MitigationStatus,
                'MitigationDueDate': risk.MitigationDueDate.isoformat() if risk.MitigationDueDate else None
            })
        
        # Call the export function from export_service.py
        export_result = export_data(
            data=risk_data,
            file_format=file_format,
            user_id=str(user_id),
            options={
                'title': 'Risk Export',
                'timestamp': datetime.datetime.now().isoformat()
            }
        )
        
        # Send notification about the export
        try:
            # Get the user who requested the export
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [user_id])
                export_user = cursor.fetchone()
            
            if export_user and export_result.get('success'):
                notification_service = NotificationService()
                
                # Use the accountUpdate template (repurposed for export notification)
                notification_data = {
                    'notification_type': 'accountUpdate',
                    'email': export_user[2],  # user email
                    'email_type': 'gmail',
                    'template_data': [
                        export_user[1],  # user name
                        f"""
                        <p><strong>Export Details:</strong></p>
                        <p>File: {export_result.get('file_name', 'Unknown')}</p>
                        <p>Format: {file_format.upper()}</p>
                        <p>Records: {len(risk_data)}</p>
                        <p>The export file is ready for download.</p>
                        """
                    ]
                }
                
                notification_result = notification_service.send_multi_channel_notification(notification_data)
                print(f"Export notification result: {notification_result}")
        except Exception as e:
            print(f"Error sending export notification: {e}")
        
        return Response(export_result)
    
    except Exception as e:
        print(f"Error exporting risks: {e}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def send_due_date_reminders(request):
    """Send reminders for risk mitigations approaching their due dates"""
    try:
        # Get risks with due dates in the next 2 days
        from datetime import datetime, timedelta
        today = datetime.now().date()
        reminder_date = today + timedelta(days=2)
        
        # Find risks approaching due dates
        risks_due_soon = RiskInstance.objects.filter(
            MitigationDueDate__gte=today,
            MitigationDueDate__lte=reminder_date,
            RiskStatus__in=['Assigned', 'Work In Progress', 'Under Review', 'Revision Required'],
            MitigationStatus__in=['Yet to Start', 'In Progress', 'Revision Required by User', 'Revision Required by Reviewer']
        )
        
        if not risks_due_soon:
            return Response({"message": "No risks with approaching due dates found"})
        
        notification_service = NotificationService()
        notifications_sent = 0
        
        for risk in risks_due_soon:
            # Skip if no user ID is assigned
            if not risk.UserId:
                continue
                
            # Get user email
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id, user_name, email FROM grc.users WHERE user_id = %s", [risk.UserId])
                user = cursor.fetchone()
                
            if not user or not user[2]:
                continue
                
            # Format due date
            due_date = risk.MitigationDueDate.strftime('%Y-%m-%d') if risk.MitigationDueDate else "Unknown"
            
            # Send the reminder using the complianceDueReminder template
            notification_data = {
                'notification_type': 'complianceDueReminder',
                'email': user[2],  # user email
                'email_type': 'gmail',
                'template_data': [
                    user[1],  # user name
                    risk.RiskDescription or f"Risk #{risk.RiskInstanceId}",  # risk title
                    due_date  # due date
                ]
            }
            
            notification_result = notification_service.send_multi_channel_notification(notification_data)
            if notification_result.get('success'):
                notifications_sent += 1
            
            # Log the reminder
            send_log(
                module="Risk",
                actionType="REMINDER",
                description=f"Due date reminder sent for risk {risk.RiskInstanceId}",
                userId=None,
                userName="System",
                entityType="RiskInstance",
                additionalInfo={"risk_id": risk.RiskInstanceId, "due_date": due_date}
            )
        
        return Response({
            "success": True, 
            "message": f"Sent {notifications_sent} due date reminders",
            "reminders_sent": notifications_sent
        })
    except Exception as e:
        print(f"Error sending due date reminders: {e}")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)
