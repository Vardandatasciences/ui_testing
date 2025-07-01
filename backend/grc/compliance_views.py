# Django ORM type checking suppression for this entire file
# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member
# type: ignore
import logging
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .models import (
    User, Framework, Policy, SubPolicy, Compliance, PolicyApproval, 
    Notification, FrameworkVersion, PolicyVersion, LastChecklistItemVerified,
    AuditVersion, AuditFinding, RiskInstance, ExportTask, GRCLog
    # CategoryBusinessUnit will be imported locally in functions
)
from .serializers import *
from django.utils import timezone   
import datetime
import uuid
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .export_service import (
    export_to_excel,
    export_to_csv,
    export_to_pdf,
    export_to_json,
    export_to_xml
)
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from django.db import connection
import json, requests
from datetime import timedelta
from celery import shared_task
import re
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from django.core.exceptions import ValidationError
import math

# Django model type hints compatibility
if TYPE_CHECKING:
    from django.db.models import Manager
from django.contrib.auth.hashers import make_password, check_password
from .notification_service import NotificationService
from django.contrib.auth.models import User
from .models import Users


LOGGING_SERVICE_URL = None

# Django ORM type checking suppression for all model operations in this file
# mypy: disable-error-code="attr-defined"

# Centralized validation module for allow-list input validation
class ComplianceInputValidator:
    """Centralized validation for all compliance input fields following allow-list pattern"""
    
    # Character sets for validation
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.\-_]+$')
    TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.\,\!\?\-_\(\)\[\]\:\;\'\"\&\%\$\#\@\+\=\n\r\t]+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]+$')
    VERSION_PATTERN = re.compile(r'^[0-9]+\.[0-9]+$')
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    # Allowed values for choice fields
    ALLOWED_CRITICALITY = ['High', 'Medium', 'Low']
    ALLOWED_MANDATORY_OPTIONAL = ['Mandatory', 'Optional']
    ALLOWED_MANUAL_AUTOMATIC = ['Manual', 'Automatic']
    ALLOWED_MATURITY_LEVELS = ['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing']
    ALLOWED_STATUS = ['Under Review', 'Approved', 'Rejected', 'Active', 'Inactive']
    ALLOWED_ACTIVE_INACTIVE = ['Active', 'Inactive']
    ALLOWED_PERMANENT_TEMPORARY = ['Permanent', 'Temporary']
    ALLOWED_VERSIONING_TYPE = ['Minor', 'Major']
    ALLOWED_RISK_TYPES = ['Current', 'Residual', 'Inherent', 'Emerging', 'Accepted']
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input by removing potentially dangerous characters"""
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        # Remove null bytes and control characters except newline, tab, carriage return
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value).strip()
    
    @staticmethod
    def validate_required_string(value: Any, field_name: str, max_length: Optional[int] = None, 
                                min_length: int = 1, pattern = None) -> str:
        """Validate required string fields with allow-list pattern"""
        if value is None or value == '':
            raise ValidationError(f"{field_name} is required and cannot be empty")
        
        # Convert to string and sanitize
        str_value = ComplianceInputValidator.sanitize_string(value)
        
        if len(str_value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        
        if max_length and len(str_value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters")
        
        # Check against allowed pattern
        if pattern and not pattern.match(str_value):
            raise ValidationError(f"{field_name} contains invalid characters")
        
        return str_value
    
    @staticmethod
    def validate_optional_string(value: Any, field_name: str, max_length: Optional[int] = None, 
                                pattern = None) -> str:
        """Validate optional string fields with allow-list pattern"""
        if value is None or value == '':
            return ''
        
        str_value = ComplianceInputValidator.sanitize_string(value)
        
        if max_length and len(str_value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters")
        
        if pattern and str_value and not pattern.match(str_value):
            raise ValidationError(f"{field_name} contains invalid characters")
        
        return str_value
    
    @staticmethod
    def validate_choice_field(value: Any, field_name: str, allowed_choices: List[str]) -> str:
        """Validate choice fields against allowed values"""
        if value is None or value == '':
            raise ValidationError(f"{field_name} is required")
        
        str_value = str(value).strip()
        if str_value not in allowed_choices:
            raise ValidationError(f"{field_name} must be one of: {', '.join(allowed_choices)}")
        
        return str_value
    
    @staticmethod
    def validate_boolean_field(value: Any, field_name: str) -> bool:
        """Validate boolean fields"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes']:
                return True
            elif value.lower() in ['false', '0', 'no', '']:
                return False
        if isinstance(value, int):
            return bool(value)
        
        raise ValidationError(f"{field_name} must be a valid boolean value")
    
    @staticmethod
    def validate_numeric_field(value: Any, field_name: str, min_val: Optional[float] = None, 
                              max_val: Optional[float] = None) -> float:
        """Validate numeric fields with range checking"""
        if value is None or value == '':
            raise ValidationError(f"{field_name} is required")
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")
        
        if min_val is not None and num_value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and num_value > max_val:
            raise ValidationError(f"{field_name} must not exceed {max_val}")
        
        return num_value
    
    @staticmethod
    def validate_integer_field(value: Any, field_name: str, min_val: Optional[int] = None, 
                              max_val: Optional[int] = None) -> int:
        """Validate integer fields with range checking"""
        if value is None or value == '':
            raise ValidationError(f"{field_name} is required")
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
        
        if min_val is not None and int_value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and int_value > max_val:
            raise ValidationError(f"{field_name} must not exceed {max_val}")
        
        return int_value
    
    @staticmethod
    def validate_date_field(value: Any, field_name: str) -> str:
        """Validate date fields"""
        if value is None or value == '':
            raise ValidationError(f"{field_name} is required")
        
        str_value = str(value).strip()
        
        if not ComplianceInputValidator.DATE_PATTERN.match(str_value):
            raise ValidationError(f"{field_name} must be in YYYY-MM-DD format")
        
        try:
            datetime.datetime.strptime(str_value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid date")
        
        return str_value
    
    @staticmethod
    def calculate_new_version(current_version: str, versioning_type: str) -> str:
        """Calculate new version based on versioning type"""
        print(f"  calculate_new_version called with: current_version='{current_version}', versioning_type='{versioning_type}'")
        try:
            # Parse current version (e.g., "2.3" becomes 2.3)
            current_float = float(current_version) if current_version else 1.0
            print(f"  Parsed current_float: {current_float}")
            
            if versioning_type == 'Minor':
                # For minor: add 0.1 to current version (e.g., 2.3 -> 2.4)
                new_version = round(current_float + 0.1, 1)
                print(f"  Minor version calculation: {current_float} + 0.1 = {new_version}")
            elif versioning_type == 'Major':
                # For major: increment major version and reset minor to 0 (e.g., 2.3 -> 3.0)
                major = int(current_float)
                new_version = float(major + 1)
                print(f"  Major version calculation: int({current_float}) + 1 = {new_version}")
            else:
                # Default behavior (Major)
                major = int(current_float)
                new_version = float(major + 1)
                print(f"  Default (Major) version calculation: int({current_float}) + 1 = {new_version}")
            
            result = str(new_version)
            print(f"  Returning: '{result}'")
            return result
        except (ValueError, TypeError) as e:
            # If parsing fails, default to incrementing major version
            print(f"  Error in version calculation: {e}, returning '2.0'")
            return "2.0"
    
    @staticmethod
    def clean_mitigation_data(mitigation_data: str) -> str:
        """
        Clean and format mitigation data for consistent storage and display.
        Now handles JSON format with step-by-step structure.
        """
        if not mitigation_data:
            return ""
        
        # If it's already a JSON string, try to parse and validate
        if isinstance(mitigation_data, str) and (mitigation_data.strip().startswith('{') or mitigation_data.strip().startswith('[')):
            try:
                import json
                parsed = json.loads(mitigation_data)
                
                # Handle the new step-by-step format
                if isinstance(parsed, dict) and 'steps' in parsed:
                    # Validate the structure
                    if isinstance(parsed['steps'], list):
                        # Clean and validate each step
                        cleaned_steps = []
                        for step in parsed['steps']:
                            if isinstance(step, dict) and 'description' in step:
                                cleaned_step = {
                                    'stepNumber': step.get('stepNumber', len(cleaned_steps) + 1),
                                    'description': str(step['description']).strip()
                                }
                                # Only include steps with valid descriptions
                                if cleaned_step['description']:
                                    cleaned_steps.append(cleaned_step)
                        
                        # Reconstruct the JSON structure
                        cleaned_mitigation = {
                            'steps': cleaned_steps,
                            'totalSteps': len(cleaned_steps),
                            'lastUpdated': parsed.get('lastUpdated', ''),
                            'version': '2.0'  # Version to identify new format
                        }
                        
                        return json.dumps(cleaned_mitigation, separators=(',', ':'))
                
                # Handle legacy array format
                if isinstance(parsed, list):
                    # Convert to new format
                    cleaned_steps = []
                    for i, step in enumerate(parsed):
                        if isinstance(step, str) and step.strip():
                            cleaned_steps.append({
                                'stepNumber': i + 1,
                                'description': step.strip()
                            })
                    
                    if cleaned_steps:
                        cleaned_mitigation = {
                            'steps': cleaned_steps,
                            'totalSteps': len(cleaned_steps),
                            'lastUpdated': '',
                            'version': '2.0'
                        }
                        return json.dumps(cleaned_mitigation, separators=(',', ':'))
                
                # Handle legacy object format
                if isinstance(parsed, dict):
                    if 'description' in parsed:
                        # Convert single description to step format
                        cleaned_mitigation = {
                            'steps': [{
                                'stepNumber': 1,
                                'description': str(parsed['description']).strip()
                            }],
                            'totalSteps': 1,
                            'lastUpdated': '',
                            'version': '2.0'
                        }
                        return json.dumps(cleaned_mitigation, separators=(',', ':'))
                
                # Return as formatted JSON if it's a valid structure
                return json.dumps(parsed, separators=(',', ':'))
                
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as plain text
                pass
        
        # Handle plain text - convert to new JSON format
        if isinstance(mitigation_data, str) and mitigation_data.strip():
            import json
            
            # Try to split by common delimiters to create steps
            text = mitigation_data.strip()
            
            # Split by numbered patterns (1., 2., etc.) or newlines
            import re
            steps_text = re.split(r'(?:^|\n)\s*\d+\.\s*', text)
            if len(steps_text) > 1:
                # Remove empty first element if it exists
                if not steps_text[0].strip():
                    steps_text = steps_text[1:]
            else:
                # Split by newlines or semicolons
                steps_text = [s.strip() for s in re.split(r'[;\n]', text) if s.strip()]
            
            # If no clear steps found, treat as single step
            if not steps_text or (len(steps_text) == 1 and not steps_text[0].strip()):
                steps_text = [text]
            
            # Create step objects
            cleaned_steps = []
            for i, step_text in enumerate(steps_text):
                if step_text.strip():
                    cleaned_steps.append({
                        'stepNumber': i + 1,
                        'description': step_text.strip()
                    })
            
            if cleaned_steps:
                cleaned_mitigation = {
                    'steps': cleaned_steps,
                    'totalSteps': len(cleaned_steps),
                    'lastUpdated': '',
                    'version': '2.0'
                }
                return json.dumps(cleaned_mitigation, separators=(',', ':'))
        
        return ""
    
    @staticmethod
    def validate_mitigation_json(mitigation_data: str) -> bool:
        """
        Validate that mitigation data is properly formatted JSON with valid structure
        """
        if not mitigation_data:
            return True  # Empty is valid
        
        try:
            import json
            parsed = json.loads(mitigation_data)
            
            # Must be a dictionary with 'steps' key
            if not isinstance(parsed, dict) or 'steps' not in parsed:
                return False
            
            # Steps must be a list
            if not isinstance(parsed['steps'], list):
                return False
            
            # Each step must have required structure
            for step in parsed['steps']:
                if not isinstance(step, dict):
                    return False
                if 'description' not in step or not isinstance(step['description'], str):
                    return False
                if not step['description'].strip():
                    return False
            
            return True
            
        except json.JSONDecodeError:
            return False
    
    @classmethod
    def validate_compliance_data(cls, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main validation method for compliance data using allow-list approach"""
        validated_data = {}
        errors = {}
        
        try:
            # Validate SubPolicy (required foreign key)
            validated_data['SubPolicy'] = cls.validate_integer_field(
                request_data.get('SubPolicy'), 'SubPolicy', min_val=1
            )
        except ValidationError as e:
            errors['SubPolicy'] = [str(e)]
        
        try:
            # Validate ComplianceTitle (required, max 145 chars)
            validated_data['ComplianceTitle'] = cls.validate_required_string(
                request_data.get('ComplianceTitle'), 'ComplianceTitle', 
                max_length=145, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['ComplianceTitle'] = [str(e)]
        
        try:
            # Validate ComplianceItemDescription (required text field)
            validated_data['ComplianceItemDescription'] = cls.validate_required_string(
                request_data.get('ComplianceItemDescription'), 'ComplianceItemDescription',
                max_length=5000, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['ComplianceItemDescription'] = [str(e)]
        
        try:
            # Validate ComplianceType (required, max 100 chars)
            validated_data['ComplianceType'] = cls.validate_required_string(
                request_data.get('ComplianceType'), 'ComplianceType',
                max_length=100, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['ComplianceType'] = [str(e)]
        
        try:
            # Validate Scope (required text field)
            validated_data['Scope'] = cls.validate_required_string(
                request_data.get('Scope'), 'Scope',
                max_length=5000, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['Scope'] = [str(e)]
        
        try:
            # Validate Objective (required text field)
            validated_data['Objective'] = cls.validate_required_string(
                request_data.get('Objective'), 'Objective',
                max_length=5000, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['Objective'] = [str(e)]
        
        try:
            # Validate BusinessUnitsCovered (required, max 225 chars)
            validated_data['BusinessUnitsCovered'] = cls.validate_required_string(
                request_data.get('BusinessUnitsCovered'), 'BusinessUnitsCovered',
                max_length=225, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['BusinessUnitsCovered'] = [str(e)]
        
        try:
            # Validate IsRisk (boolean)
            validated_data['IsRisk'] = cls.validate_boolean_field(
                request_data.get('IsRisk', False), 'IsRisk'
            )
        except ValidationError as e:
            errors['IsRisk'] = [str(e)]
        
        # If IsRisk is True, validate risk-related fields
        if validated_data.get('IsRisk', False):
            try:
                validated_data['PossibleDamage'] = cls.validate_required_string(
                    request_data.get('PossibleDamage'), 'PossibleDamage',
                    max_length=5000, pattern=cls.TEXT_PATTERN
                )
            except ValidationError as e:
                errors['PossibleDamage'] = [str(e)]
            
            try:
                validated_data['PotentialRiskScenarios'] = cls.validate_required_string(
                    request_data.get('PotentialRiskScenarios'), 'PotentialRiskScenarios',
                    max_length=5000, pattern=cls.TEXT_PATTERN
                )
            except ValidationError as e:
                errors['PotentialRiskScenarios'] = [str(e)]
            
            try:
                validated_data['RiskType'] = cls.validate_required_string(
                    request_data.get('RiskType'), 'RiskType',
                    max_length=45, pattern=cls.TEXT_PATTERN
                )
            except ValidationError as e:
                errors['RiskType'] = [str(e)]
            
            try:
                validated_data['RiskCategory'] = cls.validate_required_string(
                    request_data.get('RiskCategory'), 'RiskCategory',
                    max_length=45, pattern=cls.TEXT_PATTERN
                )
            except ValidationError as e:
                errors['RiskCategory'] = [str(e)]
            
            try:
                validated_data['RiskBusinessImpact'] = cls.validate_required_string(
                    request_data.get('RiskBusinessImpact'), 'RiskBusinessImpact',
                    max_length=45, pattern=cls.TEXT_PATTERN
                )
            except ValidationError as e:
                errors['RiskBusinessImpact'] = [str(e)]
        else:
            # Optional fields when IsRisk is False
            validated_data['PossibleDamage'] = cls.validate_optional_string(
                request_data.get('PossibleDamage'), 'PossibleDamage',
                max_length=5000, pattern=cls.TEXT_PATTERN
            )
            validated_data['PotentialRiskScenarios'] = cls.validate_optional_string(
                request_data.get('PotentialRiskScenarios'), 'PotentialRiskScenarios',
                max_length=5000, pattern=cls.TEXT_PATTERN
            )
            validated_data['RiskType'] = cls.validate_optional_string(
                request_data.get('RiskType'), 'RiskType',
                max_length=45, pattern=cls.TEXT_PATTERN
            )
            validated_data['RiskCategory'] = cls.validate_optional_string(
                request_data.get('RiskCategory'), 'RiskCategory',
                max_length=45, pattern=cls.TEXT_PATTERN
            )
            validated_data['RiskBusinessImpact'] = cls.validate_optional_string(
                request_data.get('RiskBusinessImpact'), 'RiskBusinessImpact',
                max_length=45, pattern=cls.TEXT_PATTERN
            )
        
        try:
            # Validate and clean mitigation (JSON step-by-step format)
            raw_mitigation = request_data.get('mitigation')
            if raw_mitigation:
                # Clean the mitigation data first
                cleaned_mitigation = cls.clean_mitigation_data(raw_mitigation)
                
                # Validate JSON structure
                if not cls.validate_mitigation_json(cleaned_mitigation):
                    raise ValidationError("Invalid mitigation data format")
                
                # Final validation for length (JSON format can be longer)
                if len(cleaned_mitigation) > 10000:  # Increased limit for JSON
                    raise ValidationError("Mitigation data exceeds maximum length")
                
                validated_data['mitigation'] = cleaned_mitigation
            else:
                validated_data['mitigation'] = ''
        except ValidationError as e:
            errors['mitigation'] = [str(e)]
        
        try:
            # Validate Criticality (required choice field)
            validated_data['Criticality'] = cls.validate_choice_field(
                request_data.get('Criticality'), 'Criticality', cls.ALLOWED_CRITICALITY
            )
        except ValidationError as e:
            errors['Criticality'] = [str(e)]
        
        try:
            # Validate MandatoryOptional (required choice field)
            validated_data['MandatoryOptional'] = cls.validate_choice_field(
                request_data.get('MandatoryOptional'), 'MandatoryOptional', cls.ALLOWED_MANDATORY_OPTIONAL
            )
        except ValidationError as e:
            errors['MandatoryOptional'] = [str(e)]
        
        try:
            # Validate ManualAutomatic (required choice field)
            validated_data['ManualAutomatic'] = cls.validate_choice_field(
                request_data.get('ManualAutomatic'), 'ManualAutomatic', cls.ALLOWED_MANUAL_AUTOMATIC
            )
        except ValidationError as e:
            errors['ManualAutomatic'] = [str(e)]
        
        try:
            # Validate Impact (required numeric field, 1-10)
            validated_data['Impact'] = cls.validate_numeric_field(
                request_data.get('Impact'), 'Impact', min_val=1.0, max_val=10.0
            )
        except ValidationError as e:
            errors['Impact'] = [str(e)]
        
        try:
            # Validate Probability (required numeric field, 1-10)
            validated_data['Probability'] = cls.validate_numeric_field(
                request_data.get('Probability'), 'Probability', min_val=1.0, max_val=10.0
            )
        except ValidationError as e:
            errors['Probability'] = [str(e)]
        
        try:
            # Validate ComplianceVersion (required, max 50 chars, version pattern)
            validated_data['ComplianceVersion'] = cls.validate_required_string(
                request_data.get('ComplianceVersion', '1.0'), 'ComplianceVersion',
                max_length=50, pattern=cls.VERSION_PATTERN
            )
        except ValidationError as e:
            errors['ComplianceVersion'] = [str(e)]
        
        try:
            # Validate Applicability (optional, max 45 chars)
            validated_data['Applicability'] = cls.validate_optional_string(
                request_data.get('Applicability'), 'Applicability',
                max_length=45, pattern=cls.TEXT_PATTERN
            )
        except ValidationError as e:
            errors['Applicability'] = [str(e)]
        
        try:
            # Validate Identifier (optional, max 45 chars, identifier pattern)
            identifier = request_data.get('Identifier', '').strip()
            if identifier:
                validated_data['Identifier'] = cls.validate_optional_string(
                    identifier, 'Identifier', max_length=45, pattern=cls.IDENTIFIER_PATTERN
                )
            else:
                validated_data['Identifier'] = ''
        except ValidationError as e:
            errors['Identifier'] = [str(e)]
        
        try:
            # Validate reviewer (required integer)
            validated_data['reviewer'] = cls.validate_integer_field(
                request_data.get('reviewer'), 'reviewer', min_val=1
            )
        except ValidationError as e:
            errors['reviewer'] = [str(e)]
        
        try:
            # Validate ApprovalDueDate (required date)
            validated_data['ApprovalDueDate'] = cls.validate_date_field(
                request_data.get('ApprovalDueDate'), 'ApprovalDueDate'
            )
        except ValidationError as e:
            errors['ApprovalDueDate'] = [str(e)]
        
        # Set default values for system fields
        validated_data['Status'] = 'Under Review'
        validated_data['ActiveInactive'] = 'Inactive'
        validated_data['PermanentTemporary'] = 'Permanent'
        validated_data['MaturityLevel'] = 'Initial'
        
        if errors:
            raise ValidationError(errors)
        
        return validated_data

 
# Create your views here.
 
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Instead of using JWT tokens which expect Django's User model,
        # create a simple token-like response with user data
        return Response({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'UserId': user.UserId,
                'UserName': user.UserName
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
 
@api_view(['GET'])
def test_connection(request):
    return Response({"message": "Connection successful!"})


 
@api_view(['GET'])
def get_frameworks(request):
    print(f"\n=== GET_FRAMEWORKS DEBUG ===")
    
    try:
        # Get all frameworks (remove ActiveInactive filter for now to see all data)
        frameworks = Framework.objects.all()  # type: ignore
        print(f"Found {frameworks.count()} frameworks in total")
        
        # Debug: Print each framework
        for fw in frameworks:
            print(f"Framework: ID={fw.FrameworkId}, Name={fw.FrameworkName}, Status={fw.ActiveInactive}")
        
        serializer = FrameworkSerializer(frameworks, many=True)
        serialized_data = serializer.data
        
        print(f"Serialized data: {serialized_data}")
        
        # Format the response to match frontend expectations
        formatted_frameworks = []
        for fw_data in serialized_data:
            formatted_fw = {
                'id': fw_data.get('FrameworkId'),
                'name': fw_data.get('FrameworkName'),
                'category': fw_data.get('Category', ''),
                'status': fw_data.get('ActiveInactive', ''),
                'description': fw_data.get('FrameworkDescription', ''),
            }
            formatted_frameworks.append(formatted_fw)
            print(f"Formatted framework: {formatted_fw}")
        
        response_data = {
            'success': True, 
            'frameworks': formatted_frameworks,  # Change 'data' to 'frameworks'
            'count': len(formatted_frameworks)
        }
        
        print(f"Final response: {response_data}")
        print("=== END GET_FRAMEWORKS DEBUG ===\n")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in get_frameworks: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error fetching frameworks: {str(e)}'
        }, status=500)
 
@api_view(['GET'])
def get_policies(request, framework_id):
    print(f"\n=== GET_POLICIES DEBUG ===")
    print(f"Received framework_id: {framework_id} (type: {type(framework_id)})")
    
    try:
        # Get all policies for this framework (remove ActiveInactive filter for now to see all data)
        policies = Policy.objects.filter(FrameworkId=framework_id)  # type: ignore
        print(f"Found {policies.count()} policies for framework {framework_id}")
        
        # Debug: Print each policy
        for p in policies:
            print(f"Policy: ID={p.PolicyId}, Name={p.PolicyName}, Status={p.ActiveInactive}")
        
        # Format the response to match frontend expectations
        formatted_policies = []
        for p in policies:
            formatted_policy = {
                'id': p.PolicyId,
                'name': p.PolicyName,
                'applicability': p.Applicability or '',
                'status': p.ActiveInactive or '',
                'scope': p.Applicability or '',  # Add scope field for compatibility
            }
            formatted_policies.append(formatted_policy)
            print(f"Formatted policy: {formatted_policy}")
        
        response_data = {
            'success': True, 
            'policies': formatted_policies,  # Change 'data' to 'policies'
            'count': len(formatted_policies)
        }
        
        print(f"Final response: {response_data}")
        print("=== END GET_POLICIES DEBUG ===\n")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in get_policies: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error fetching policies: {str(e)}'
        }, status=500)
 
@api_view(['GET'])
def get_subpolicies(request, policy_id):
    print(f"\n=== GET_SUBPOLICIES DEBUG ===")
    print(f"Received policy_id: {policy_id} (type: {type(policy_id)})")
    
    try:
        # Get all subpolicies for this policy (remove Status filter for now to see all data)
        subpolicies = SubPolicy.objects.filter(PolicyId=policy_id)  # type: ignore
        print(f"Found {subpolicies.count()} subpolicies for policy {policy_id}")
        
        # Debug: Print each subpolicy
        for sp in subpolicies:
            print(f"SubPolicy: ID={sp.SubPolicyId}, Name={sp.SubPolicyName}, Status={sp.Status}")
        
        serializer = SubPolicySerializer(subpolicies, many=True)
        serialized_data = serializer.data
        
        print(f"Serialized data: {serialized_data}")
        
        # Format the response to match frontend expectations
        formatted_subpolicies = []
        for sp_data in serialized_data:
            formatted_sp = {
                'id': sp_data.get('SubPolicyId'),
                'name': sp_data.get('SubPolicyName'),
                'status': sp_data.get('Status'),
                'description': sp_data.get('Description', ''),
                'control': sp_data.get('Control', ''),
                'identifier': sp_data.get('Identifier', ''),
            }
            formatted_subpolicies.append(formatted_sp)
            print(f"Formatted subpolicy: {formatted_sp}")
        
        response_data = {
            'success': True, 
            'subpolicies': formatted_subpolicies,  # Change 'data' to 'subpolicies'
            'count': len(formatted_subpolicies)
        }
        
        print(f"Final response: {response_data}")
        print("=== END GET_SUBPOLICIES DEBUG ===\n")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in get_subpolicies: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error fetching subpolicies: {str(e)}'
        }, status=500)
 
def ensure_user_has_email(user_id, default_email=None):
    """
    Utility function to ensure a user has an email address.
    Returns True if the user has an email (existing or newly added), False otherwise.
    """
    try:
        from .models import User
        if not Users.objects.filter(UserName=user_id).exists():  # type: ignore
            print(f"User with ID {user_id} not found - creating")
            username = f"User{user_id}"
            email = default_email or f"user{user_id}@example.com"
            Users.objects.create(  # type: ignore
                UserId=user_id,
                UserName=username,
                Password="",
                email=email
            )
            print(f"Created user {username} with email {email}")
            return True
            
        user = Users.objects.get(UserName=user_id)  # type: ignore
        if not user.email:
            email = default_email or f"user{user_id}@example.com"
            user.email = email
            user.save()
            print(f"Updated user {user.UserName} with email {email}")
            
        return bool(user.email)
    except Exception as e:
        print(f"Error ensuring user has email: {str(e)}")
        return False

@api_view(['POST'])
def create_compliance(request):

    print(f"Received request data: {request.data}")
    try:
        # Validate input data using centralized validator
        validated_data = ComplianceInputValidator.validate_compliance_data(request.data)
    except ValidationError as e:
        return Response({
            'success': False,
            'message': 'Input validation failed',
            'errors': e.message_dict if hasattr(e, 'message_dict') else {'general': [str(e)]}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate identifier if not provided
    if not validated_data['Identifier']:
        subpolicy_id = validated_data['SubPolicy']
        identifier = f"COMP-{subpolicy_id}-{datetime.date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"
        validated_data['Identifier'] = identifier
    
    # Get reviewer ID and approval due date
    reviewer_id = validated_data['reviewer']
    approval_due_date = validated_data['ApprovalDueDate']
    
    # Get creator name
    created_by_name = 'System'
    if request.user.is_authenticated:
        created_by_name = request.user.username

    # Create new compliance
    try:
        # Get the SubPolicy object
        from .models import SubPolicy
        try:
            subpolicy = SubPolicy.objects.get(SubPolicyId=validated_data['SubPolicy'])
        except SubPolicy.DoesNotExist:
            print(f"WARNING: SubPolicy {validated_data['SubPolicy']} not found")
            return Response({
                'success': False,
                'message': 'Failed to create compliance',
                'errors': {'general': ['SubPolicy not found']}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Create the compliance with the SubPolicy object
        new_compliance = Compliance.objects.create(
            SubPolicy=subpolicy,
            ComplianceTitle=validated_data['ComplianceTitle'],
            ComplianceItemDescription=validated_data['ComplianceItemDescription'],
            ComplianceType=validated_data['ComplianceType'],
            Scope=validated_data['Scope'],
            Objective=validated_data['Objective'],
            BusinessUnitsCovered=validated_data['BusinessUnitsCovered'],
            IsRisk=validated_data['IsRisk'],
            PossibleDamage=validated_data['PossibleDamage'],
            mitigation=validated_data['mitigation'],
            PotentialRiskScenarios=validated_data.get('PotentialRiskScenarios', ''),
            RiskType=validated_data.get('RiskType', ''),
            RiskCategory=validated_data.get('RiskCategory', ''),
            RiskBusinessImpact=validated_data.get('RiskBusinessImpact', ''),
            Criticality=validated_data['Criticality'],
            MandatoryOptional=validated_data['MandatoryOptional'],
            ManualAutomatic=validated_data['ManualAutomatic'],
            Impact=validated_data['Impact'],
            Probability=validated_data['Probability'],
            MaturityLevel=validated_data.get('MaturityLevel', 'Initial'),
            ActiveInactive=validated_data.get('ActiveInactive', 'Inactive'),
            PermanentTemporary=validated_data.get('PermanentTemporary', 'Permanent'),
            CreatedByName=validated_data.get('CreatedByName', created_by_name),
            CreatedByDate=datetime.date.today(),
            ComplianceVersion='1.0',
            Status='Under Review',
            Identifier=identifier,
            Applicability=validated_data['Applicability']
        )
        
        # Prepare extracted data for policy approval
        extracted_data = {
            'type': 'compliance',
            'ComplianceItemDescription': validated_data['ComplianceItemDescription'],
            'Criticality': validated_data['Criticality'],
            'Impact': validated_data['Impact'],
            'Probability': validated_data['Probability'],
            'mitigation': validated_data['mitigation'],
            'PossibleDamage': validated_data['PossibleDamage'],
            'IsRisk': validated_data['IsRisk'],
            'MandatoryOptional': validated_data['MandatoryOptional'],
            'ManualAutomatic': validated_data['ManualAutomatic'],
            'CreatedByName': validated_data.get('CreatedByName', created_by_name),
            'CreatedByDate': datetime.date.today().isoformat(),
            'Status': 'Under Review',
            'ComplianceId': new_compliance.ComplianceId,
            'ComplianceVersion': '1.0',
            'SubPolicy': validated_data['SubPolicy']
        }
        
        extracted_data['compliance_approval'] = {
            'approved': None,
            'remarks': '',
            'ApprovalDueDate': approval_due_date
        }
       
        # Create policy approval
        user_id = int(validated_data.get('CreatedByName', 1))  # Use CreatedByName as UserId if available
        
        # Ensure users have emails for notifications
        ensure_user_has_email(user_id, "system@example.com")
        reviewer_has_email = ensure_user_has_email(reviewer_id, f"reviewer{reviewer_id}@example.com")
        if not reviewer_has_email:
            print(f"WARNING: Reviewer {reviewer_id} has no email, notifications may fail")
       
        # Get the policy ID from the subpolicy
        policy = subpolicy.PolicyId  # Get the actual Policy instance through the foreign key
            
        # Create the policy approval
        policy_approval = PolicyApproval.objects.create(
            Identifier=validated_data['Identifier'],
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            ApprovedNot=None,
            Version="u1",
            PolicyId=policy,  # Use the actual Policy instance from the foreign key
            ApprovalDueDate=approval_due_date
        )
        
        # Send notification to reviewer
        try:
            print("=== NOTIFICATION DEBUGGING - COMPLIANCE CLONE ===")
            from .notification_service import NotificationService
            notification_service = NotificationService()
            
            # Make sure reviewer has a valid email
            try:
                reviewer = Users.objects.get(UserId=reviewer_id)
                if not reviewer.Email or '@' not in reviewer.Email:
                    reviewer.Email = f"reviewer{reviewer_id}@example.com"
                    reviewer.save()
                    print(f"Updated reviewer {reviewer_id} with email {reviewer.Email}")
                
                print(f"Found reviewer: {reviewer.UserName} with email: {reviewer.Email}")
            except Users.DoesNotExist:
                print(f"ERROR: Reviewer with ID {reviewer_id} does not exist")
            
            # Send notification
            print(f"Sending clone notification for compliance {new_compliance.ComplianceId} to reviewer {reviewer_id}")
            notification_result = notification_service.send_compliance_clone_notification(
                compliance=new_compliance,
                reviewer_id=reviewer_id
            )
            
            if notification_result.get('success'):
                print(f"Successfully sent compliance clone notification to reviewer {reviewer_id}")
            else:
                print(f"Failed to send notification: {notification_result.get('error', 'Unknown error')}")
                print(f"Error details: {notification_result.get('errors', [])}") 
            
            # Log the notification directly in the database
            from .models import Notification
            try:
                reviewer_email, reviewer_name = notification_service.get_user_email_by_id(reviewer_id)
                if reviewer_email:
                    Notification.objects.create(
                        recipient=reviewer_email,
                        type='compliance_clone',
                        channel='email',
                        success=notification_result.get('success', False)
                    )
                    print(f"Created clone notification record for {reviewer_email}")
            except Exception as db_error:
                print(f"ERROR creating notification record: {str(db_error)}")
                
            print("=== END NOTIFICATION DEBUGGING ===")
        except Exception as e:
            print(f"Error sending compliance clone notification: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Continue even if notification fails
 
        return Response({
            'success': True,
            'message': 'Compliance created successfully and sent for review',
            'compliance_id': new_compliance.ComplianceId,
            'Identifier': identifier,
            'version': new_compliance.ComplianceVersion,
            'reviewer_id': reviewer_id
        }, status=status.HTTP_201_CREATED)
 
    except Exception as e:
        print(f"Error creating compliance: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_compliance_dashboard(request):
    try:
        # Get all filter parameters from request
        status = request.query_params.get('status')
        active_inactive = request.query_params.get('active_inactive')
        criticality = request.query_params.get('criticality')
        mandatory_optional = request.query_params.get('mandatory_optional')
        manual_automatic = request.query_params.get('manual_automatic')
        impact = request.query_params.get('impact')
        probability = request.query_params.get('probability')
        permanent_temporary = request.query_params.get('permanent_temporary')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        framework_id = request.query_params.get('framework_id')
        policy_id = request.query_params.get('policy_id')
        subpolicy_id = request.query_params.get('subpolicy_id')

        # Start with base queryset
        queryset = Compliance.objects.all()

        # Apply filters if they exist
        if status:
            queryset = queryset.filter(Status=status)
        if active_inactive:
            queryset = queryset.filter(ActiveInactive=active_inactive)
        if criticality:
            queryset = queryset.filter(Criticality=criticality)
        if mandatory_optional:
            queryset = queryset.filter(MandatoryOptional=mandatory_optional)
        if manual_automatic:
            queryset = queryset.filter(ManualAutomatic=manual_automatic)
        if impact:
            queryset = queryset.filter(Impact=impact)
        if probability:
            queryset = queryset.filter(Probability=probability)
        if permanent_temporary:
            queryset = queryset.filter(PermanentTemporary=permanent_temporary)
        if start_date:
            queryset = queryset.filter(CreatedByDate__gte=start_date)
        if end_date:
            queryset = queryset.filter(CreatedByDate__lte=end_date)
        if subpolicy_id:
            queryset = queryset.filter(SubPolicy=subpolicy_id)
        elif policy_id:
            queryset = queryset.filter(SubPolicy__PolicyId=policy_id)
        elif framework_id:
            queryset = queryset.filter(SubPolicy__Policy__Framework_id=framework_id)

        print("Executing Query:", queryset.query) 
        # Get counts for different statuses
        status_counts = {
            'approved': queryset.filter(Status='Approved').count(),
            'active': queryset.filter(Status='Active').count(),
            'scheduled': queryset.filter(Status='Schedule').count(),
            'rejected': queryset.filter(Status='Rejected').count(),
            'under_review': queryset.filter(Status='Under Review').count(),
            'active_compliance': queryset.filter(ActiveInactive='Active').count()
        }

        # Get counts for criticality levels
        criticality_counts = {
            'high': queryset.filter(Criticality='High').count(),
            'medium': queryset.filter(Criticality='Medium').count(),
            'low': queryset.filter(Criticality='Low').count()
        }

        # Calculate total findings
        total_findings = queryset.filter(IsRisk=True).count()

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'status_counts': status_counts,
                    'criticality_counts': criticality_counts,
                    'total_count': queryset.count(),
                    'total_findings': total_findings
                }
            }
        })

    except Exception as e:
        print(f"Error in get_compliance_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_compliances_by_subpolicy(request, subpolicy_id):
    try:
        # Verify subpolicy exists first
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
       
        # Get all compliances for this subpolicy
        compliances = Compliance.objects.filter(SubPolicy=subpolicy_id)
       
        # Create a dictionary to store compliance groups
        compliance_groups = {}
       
        # First pass: Create groups based on Identifier
        for compliance in compliances:
            if compliance.Identifier not in compliance_groups:
                compliance_groups[compliance.Identifier] = []
            compliance_groups[compliance.Identifier].append(compliance)
       
        # Second pass: Sort each group by version number
        for identifier in compliance_groups:
            compliance_groups[identifier].sort(
                key=lambda x: float(x.ComplianceVersion) if x.ComplianceVersion and x.ComplianceVersion.strip() else 0.0,
                reverse=True
            )
       
        # Convert to list and sort groups by latest version's creation date
        sorted_groups = sorted(
            compliance_groups.values(),
            key=lambda group: group[0].CreatedByDate if group[0].CreatedByDate else datetime.now(),
            reverse=True
        )
       
        # Create grouped structure for the frontend
        serialized_groups = []
        for group in sorted_groups:
            group_data = []
            for compliance in group:
                serializer = ComplianceListSerializer(compliance)
                compliance_data = serializer.data
                
                # Add previous version ID reference if it exists
                if compliance.PreviousComplianceVersionId:
                    compliance_data['PreviousComplianceVersionId'] = compliance.PreviousComplianceVersionId.ComplianceId
                else:
                    compliance_data['PreviousComplianceVersionId'] = None
                
                group_data.append(compliance_data)
            serialized_groups.append(group_data)
       
        return Response({
            'success': True,
            'data': serialized_groups
        })
    except SubPolicy.DoesNotExist:
        return Response({
            'success': False,
            'message': f'SubPolicy with id {subpolicy_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in get_compliances_by_subpolicy: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while fetching compliances'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_compliance_review(request, approval_id):
    try:
        # Get the approval record
        approval = get_object_or_404(PolicyApproval, ApprovalId=approval_id)
        
        # Get the data from request
        # The frontend sends ApprovedNot directly, or as part of ExtractedData
        if 'ApprovedNot' in request.data:
            approved_not = request.data.get('ApprovedNot')
        elif 'ExtractedData' in request.data and 'compliance_approval' in request.data['ExtractedData']:
            approved_not = request.data['ExtractedData']['compliance_approval'].get('approved')
        else:
            approved_not = request.data.get('approved', False)
        
        # Convert to boolean if it's a string
        if isinstance(approved_not, str):
            approved_not = approved_not.lower() == 'true'
        
        # Add debug logging
        print(f"Received approval request with approved_not value: {approved_not} (type: {type(approved_not)})")
        print(f"Request data: {request.data}")
        
        remarks = request.data.get('remarks', '')
        
        # Get extracted data from approval
        extracted_data = approval.ExtractedData
        
        # Update approval status
        approval.ApprovedNot = approved_not
        approval.save()
        
        # Create new approval record with incremented version
        current_version = approval.Version
        if current_version.startswith('u'):
            # User version, increment number
            version_num = int(current_version[1:])
            new_version = f"u{version_num + 1}"
        else:
            # Start with u1
            new_version = "u1"
            
        # Update extracted data with approval info
        if 'compliance_approval' in extracted_data:
            extracted_data['compliance_approval']['approved'] = approved_not
            extracted_data['compliance_approval']['remarks'] = remarks
            
        # Create new approval record - preserve ApprovalDueDate from original approval
        new_approval = PolicyApproval.objects.create(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=approved_not,
            Version=new_version,
            ApprovalDueDate=approval.ApprovalDueDate
        )
        
        print(f"Created new approval record with ID {new_approval.ApprovalId}, Approved: {new_approval.ApprovedNot}")
        
        if 'SubPolicy' in extracted_data:
            try:
                # Find the compliance being reviewed
                current_compliance = Compliance.objects.filter(
                    SubPolicy=extracted_data.get('SubPolicy'),
                    Identifier=approval.Identifier,
                    Status='Under Review'
                ).first()
                
                if current_compliance:
                    print(f"Processing compliance: {current_compliance.ComplianceId}")
                    
                    if approved_not is True:
                        # If approved, set current to Active and previous to Inactive
                        current_compliance.Status = 'Approved'
                        current_compliance.ActiveInactive = 'Active'
                        
                        # Get and deactivate the previous version if it exists
                        if current_compliance.PreviousComplianceVersionId:
                            try:
                                prev_compliance = current_compliance.PreviousComplianceVersionId
                                if prev_compliance.ActiveInactive == 'Active':
                                    prev_compliance.ActiveInactive = 'Inactive'
                                    prev_compliance.save()
                                    print(f"Deactivated previous version: {prev_compliance.ComplianceId}")
                            except Exception as e:
                                print(f"Error deactivating previous version: {e}")
                    else:
                        # If rejected, mark as rejected
                        current_compliance.Status = 'Rejected'
                        
                    current_compliance.save()
                    print(f"Updated compliance status to: {current_compliance.Status}")

                    # Send notification to compliance creator
                    try:
                        from .notification_service import NotificationService
                        notification_service = NotificationService()
                        
                        # Get creator's email
                        creator_id = approval.UserId
                        creator_email, creator_name = notification_service.get_user_email_by_id(creator_id)
                        
                        if creator_email:
                            # Send notification
                            notification_result = notification_service.send_compliance_review_notification(
                                compliance=current_compliance,
                                reviewer_decision=approved_not,
                                creator_id=creator_id,
                                remarks=remarks
                            )
                            print(f"Review notification sent to {creator_name} ({creator_email}): {notification_result}")
                        else:
                            print(f"No email found for creator ID {creator_id}")
                    except Exception as e:
                        print(f"Error sending compliance review notification: {str(e)}")
                        # Continue even if notification fails
                    
                else:
                    print(f"No compliance found for SubPolicy {extracted_data.get('SubPolicy')} and Identifier {approval.Identifier}")
            except Exception as e:
                print(f"Error processing compliance update: {str(e)}")
                
        return Response({
            'success': True,
            'message': 'Review submitted successfully',
            'approval_id': new_approval.ApprovalId,
            'approved': approved_not,
            'version': new_version
        })
        
    except Exception as e:
        print(f"Error in submit_compliance_review: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_compliance_approval(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
   
        # Validate data
        extracted_data = request.data.get('ExtractedData')
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
   
        print(f"Resubmitting compliance with ID: {approval_id}, Identifier: {approval.Identifier}")
   
        # Get all versions for this identifier with 'u' prefix
        all_versions = PolicyApproval.objects.filter(Identifier=approval.Identifier)
   
        # Find the highest 'u' version number
        highest_u_version = 0
        for pa in all_versions:
            if pa.Version and pa.Version.startswith('u') and len(pa.Version) > 1:
                try:
                    version_num = int(pa.Version[1:])
                    if version_num > highest_u_version:
                        highest_u_version = version_num
                except ValueError:
                    continue
   
        # Set the new version
        new_version = f"u{highest_u_version + 1}"
        print(f"Setting new version: {new_version}")
   
        # Reset approval status in the ExtractedData
        if 'compliance_approval' in extracted_data:
            extracted_data['compliance_approval']['approved'] = None
            extracted_data['compliance_approval']['remarks'] = ''
            # Add flag to indicate this is a resubmission
            extracted_data['compliance_approval']['inResubmission'] = True
        else:
            extracted_data['compliance_approval'] = {
                'approved': None,
                'remarks': '',
                'inResubmission': True
            }
            
        # Update the status in the extracted data to 'Under Review'
        extracted_data['Status'] = 'Under Review'
        extracted_data['ActiveInactive'] = 'Inactive'
   
        # Create a new approval object
        new_approval = PolicyApproval(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=None,  # Reset approval status
            Version=new_version,
            PolicyId=approval.PolicyId,  # Preserve the PolicyId
            ApprovalDueDate=approval.ApprovalDueDate  # Preserve the ApprovalDueDate
        )
       
        # Save the new record
        new_approval.save()
        print(f"Saved new approval with ID: {new_approval.ApprovalId}, Version: {new_approval.Version}")
        
        # Update the corresponding compliance status back to 'Under Review'
        try:
            # Find the compliance being resubmitted
            if 'SubPolicy' in extracted_data:
                compliance = Compliance.objects.filter(
                    SubPolicy=extracted_data.get('SubPolicy'),
                    Identifier=approval.Identifier,
                    Status='Rejected'  # Find the rejected compliance
                ).first()
                
                if compliance:
                    # Update the compliance with the edited data
                    compliance.ComplianceItemDescription = extracted_data.get('ComplianceItemDescription', compliance.ComplianceItemDescription)
                    compliance.IsRisk = extracted_data.get('IsRisk', compliance.IsRisk)
                    compliance.PossibleDamage = extracted_data.get('PossibleDamage', compliance.PossibleDamage)
                    compliance.mitigation = extracted_data.get('mitigation', compliance.mitigation)
                    compliance.Criticality = extracted_data.get('Criticality', compliance.Criticality)
                    compliance.MandatoryOptional = extracted_data.get('MandatoryOptional', compliance.MandatoryOptional)
                    compliance.ManualAutomatic = extracted_data.get('ManualAutomatic', compliance.ManualAutomatic)
                    compliance.Impact = extracted_data.get('Impact', compliance.Impact)
                    compliance.Probability = extracted_data.get('Probability', compliance.Probability)
                    compliance.MaturityLevel = extracted_data.get('MaturityLevel', compliance.MaturityLevel)
                    
                    # Update the status back to 'Under Review'
                    compliance.Status = 'Under Review'
                    compliance.save()
                    print(f"Updated compliance {compliance.ComplianceId} status to 'Under Review' and updated fields")
                else:
                    print(f"No rejected compliance found with SubPolicy={extracted_data.get('SubPolicy')}, Identifier={approval.Identifier}")
        except Exception as e:
            print(f"Error updating compliance status: {str(e)}")
            import traceback
            traceback.print_exc()
            # Continue even if compliance update fails
       
        return Response({
            'success': True,
            'message': 'Compliance review resubmitted successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_version
        })
       
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error in resubmit_compliance_approval:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
def get_compliance_versioning(request):
    """
    Returns compliance versioning data for the frontend.
    """
    try:
        # You can customize this to return whatever versioning data you need
        # For now, we'll just return a success message
        return Response({
            'success': True,
            'message': 'Compliance versioning API endpoint',
            'data': []
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
def get_policy_approvals_by_reviewer(request):
    try:
        # Get reviewer ID from request or use default
        reviewer_id = request.query_params.get('reviewer_id', 2)
        print(f"\n\n==== DEBUGGING DEACTIVATION REQUESTS ====")
        print(f"Fetching approvals for reviewer_id: {reviewer_id}")
        
        # First get all compliances that are Under Review
        under_review_compliances = Compliance.objects.filter(
            Status='Under Review'
        ).select_related('SubPolicy')
        
        print(f"Found {under_review_compliances.count()} compliances under review")
        
        # Get their corresponding policy approvals
        approvals = []
        for compliance in under_review_compliances:
            # Get the latest policy approval for this compliance, regardless of approval status
            # This ensures we get the latest version even after rejection and resubmission
            latest_approval = PolicyApproval.objects.filter(
                Identifier=compliance.Identifier,
                ReviewerId=reviewer_id,
            ).order_by('-Version', '-ApprovalId').first()
            
            # Check if this is a version that needs review (newest user-submitted version)
            # Include if: 1) No approval exists, 2) Latest version is pending review, or 
            # 3) Latest version starts with 'u' (user submission) with no decision yet
            if not latest_approval or latest_approval.ApprovedNot is None or (
                latest_approval.Version and latest_approval.Version.startswith('u') and latest_approval.ApprovedNot is None
            ):
                # If no approval exists or we need to show the latest version for review
                if latest_approval:
                    approval_dict = {
                        'ApprovalId': latest_approval.ApprovalId,
                        'Identifier': latest_approval.Identifier,
                        'ExtractedData': latest_approval.ExtractedData,
                        'UserId': latest_approval.UserId,
                        'ReviewerId': latest_approval.ReviewerId,
                        'ApprovedNot': latest_approval.ApprovedNot,
                        'Version': latest_approval.Version,
                        'ApprovedDate': latest_approval.ApprovedDate.strftime('%Y-%m-%d %H:%M:%S') if latest_approval.ApprovedDate and hasattr(latest_approval.ApprovedDate, 'strftime') else None,
                        'ApprovalDueDate': latest_approval.ApprovalDueDate.strftime('%Y-%m-%d') if latest_approval.ApprovalDueDate and hasattr(latest_approval.ApprovalDueDate, 'strftime') else None
                    }
                    approvals.append(approval_dict)
                else:
                    # If no approval exists, create one
                    extracted_data = {
                        'type': 'compliance',
                        'ComplianceItemDescription': compliance.ComplianceItemDescription,
                        'IsRisk': compliance.IsRisk,
                        'PossibleDamage': compliance.PossibleDamage,
                        'mitigation': compliance.mitigation,
                        'Criticality': compliance.Criticality,
                        'MandatoryOptional': compliance.MandatoryOptional,
                        'ManualAutomatic': compliance.ManualAutomatic,
                        'Impact': compliance.Impact,
                        'Probability': compliance.Probability,
                        'MaturityLevel': compliance.MaturityLevel,
                        'ActiveInactive': compliance.ActiveInactive,
                        'PermanentTemporary': compliance.PermanentTemporary,
                        'Status': compliance.Status,
                        'ComplianceVersion': compliance.ComplianceVersion,
                        'CreatedByName': compliance.CreatedByName,
                        'CreatedByDate': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
                        'SubPolicy': compliance.SubPolicy.SubPolicyId if compliance.SubPolicy else None,
                        'compliance_approval': {
                            'approved': None,
                            'remarks': '',
                            'ApprovalDueDate': None
                        }
                    }
                    
                    # Set a default due date 7 days from today
                    from datetime import datetime, timedelta
                    default_due_date = datetime.now().date() + timedelta(days=7)
                    
                    new_approval = PolicyApproval.objects.create(
                        Identifier=compliance.Identifier,
                        ExtractedData=extracted_data,
                        UserId=1,  # System user
                        ReviewerId=reviewer_id,
                        ApprovedNot=None,
                        Version="u1",
                        ApprovalDueDate=default_due_date
                    )
                    
                    approval_dict = {
                        'ApprovalId': new_approval.ApprovalId,
                        'Identifier': new_approval.Identifier,
                        'ExtractedData': extracted_data,
                        'UserId': new_approval.UserId,
                        'ReviewerId': new_approval.ReviewerId,
                        'ApprovedNot': new_approval.ApprovedNot,
                        'Version': new_approval.Version,
                        'ApprovedDate': None,
                        'ApprovalDueDate': new_approval.ApprovalDueDate.strftime('%Y-%m-%d') if new_approval.ApprovalDueDate else None
                    }
                    approvals.append(approval_dict)
        
        # Get pending deactivation requests
        print("\n=== QUERYING DEACTIVATION REQUESTS ===")
        print("Fetching pending deactivation requests...")
        deactivation_requests = PolicyApproval.objects.filter(
            ReviewerId=reviewer_id,
            ApprovedNot=None
        ).exclude(ExtractedData=None)
        
        print(f"Found {deactivation_requests.count()} total pending requests with non-null ExtractedData")
        
        # Debug: Print all request identifiers
        print("All pending request identifiers:")
        for req in deactivation_requests:
            print(f" - {req.Identifier} | Type: {req.ExtractedData.get('type', 'unknown')} | RequestType: {req.ExtractedData.get('RequestType', 'unknown')}")
        
        # Filter to only include records with type='compliance_deactivation'
        deactivation_approvals = []
        for approval in deactivation_requests:
            extracted_data = approval.ExtractedData
            print(f"\nChecking approval {approval.ApprovalId} with identifier {approval.Identifier}")
            
            # Debug approval's ExtractedData
            print(f"ExtractedData type: {extracted_data.get('type', 'None')}")
            print(f"RequestType: {extracted_data.get('RequestType', 'None')}")
            
            is_deactivation = False
            reason = "none"
            
            if extracted_data and (
                extracted_data.get('type') == 'compliance_deactivation' or 
                (approval.Identifier and 'COMP-DEACTIVATE' in approval.Identifier)
            ):
                is_deactivation = True
                reason = "matched type or identifier"
            elif extracted_data and extracted_data.get('RequestType') == 'Change Status to Inactive':
                is_deactivation = True
                reason = "matched RequestType"
                
            print(f"Is deactivation? {is_deactivation} (Reason: {reason})")
            
            if is_deactivation:
                print(f"Found deactivation request: {approval.Identifier}")
                # Make sure we don't duplicate approvals
                duplicate = False
                for a in approvals:
                    if a['ApprovalId'] == approval.ApprovalId:
                        duplicate = True
                        print(f"Skipping duplicate approval {approval.ApprovalId}")
                        break
                
                if not duplicate:
                    approval_dict = {
                        'ApprovalId': approval.ApprovalId,
                        'Identifier': approval.Identifier,
                        'ExtractedData': approval.ExtractedData,
                        'UserId': approval.UserId,
                        'ReviewerId': approval.ReviewerId,
                        'ApprovedNot': approval.ApprovedNot,
                        'Version': approval.Version,
                        'ApprovedDate': approval.ApprovedDate.strftime('%Y-%m-%d %H:%M:%S') if approval.ApprovedDate and hasattr(approval.ApprovedDate, 'strftime') else None,
                        'ApprovalDueDate': approval.ApprovalDueDate.strftime('%Y-%m-%d') if approval.ApprovalDueDate and hasattr(approval.ApprovalDueDate, 'strftime') else None
                    }
                    approvals.append(approval_dict)
                    print(f"Added deactivation request {approval.Identifier} to response")
        
        # Also fetch recently approved compliances (last 30)
        print("\n=== QUERYING APPROVED COMPLIANCES ===")
        print("Fetching recently approved compliances...")
        
        # Get approved compliances from the database
        approved_compliances = Compliance.objects.filter(
            Status='Approved'
        ).select_related('SubPolicy').order_by('-CreatedByDate')[:30]
        
        print(f"Found {approved_compliances.count()} approved compliances in database")
        
        # For each approved compliance, get the latest approval record
        for compliance in approved_compliances:
            # Find the approval record for this compliance
            latest_approval = PolicyApproval.objects.filter(
                Identifier=compliance.Identifier,
                ReviewerId=reviewer_id,
                ApprovedNot=True
            ).order_by('-ApprovalId').first()
            
            if latest_approval:
                print(f"Found approval for approved compliance {compliance.Identifier}")
                
                # Make sure we don't duplicate approvals
                if not any(a['ApprovalId'] == latest_approval.ApprovalId for a in approvals):
                    # Format for JSON serialization
                    approval_dict = {
                        'ApprovalId': latest_approval.ApprovalId,
                        'Identifier': latest_approval.Identifier,
                        'ExtractedData': latest_approval.ExtractedData,
                        'UserId': latest_approval.UserId,
                        'ReviewerId': latest_approval.ReviewerId,
                        'ApprovedNot': latest_approval.ApprovedNot,
                        'Version': latest_approval.Version,
                        'ApprovedDate': latest_approval.ApprovedDate.strftime('%Y-%m-%d %H:%M:%S') if latest_approval.ApprovedDate and hasattr(latest_approval.ApprovedDate, 'strftime') else None,
                        'ApprovalDueDate': latest_approval.ApprovalDueDate.strftime('%Y-%m-%d') if latest_approval.ApprovalDueDate and hasattr(latest_approval.ApprovalDueDate, 'strftime') else None
                    }
                    
                    # Ensure the ExtractedData has the correct status
                    if approval_dict['ExtractedData']:
                        approval_dict['ExtractedData']['Status'] = 'Approved'
                        approval_dict['ExtractedData']['ActiveInactive'] = 'Active'
                    
                    approvals.append(approval_dict)
        
        # Alternative: get directly from PolicyApproval table
        recently_approved = PolicyApproval.objects.filter(
            ReviewerId=reviewer_id,
            ApprovedNot=True
        ).order_by('-ApprovalId')[:30]  # Limit to last 30
        
        print(f"Found {recently_approved.count()} approved policy approvals")
        
        for approval in recently_approved:
            # Make sure we don't duplicate approvals
            if not any(a['ApprovalId'] == approval.ApprovalId for a in approvals):
                # Format for JSON serialization
                approval_dict = {
                    'ApprovalId': approval.ApprovalId,
                    'Identifier': approval.Identifier,
                    'ExtractedData': approval.ExtractedData,
                    'UserId': approval.UserId,
                    'ReviewerId': approval.ReviewerId,
                    'ApprovedNot': approval.ApprovedNot,
                    'Version': approval.Version,
                    'ApprovedDate': approval.ApprovedDate.strftime('%Y-%m-%d %H:%M:%S') if approval.ApprovedDate and hasattr(approval.ApprovedDate, 'strftime') else None,
                    'ApprovalDueDate': approval.ApprovalDueDate.strftime('%Y-%m-%d') if approval.ApprovalDueDate and hasattr(approval.ApprovalDueDate, 'strftime') else None
                }
                
                # Ensure the ExtractedData has the correct status
                if approval_dict['ExtractedData']:
                    approval_dict['ExtractedData']['Status'] = 'Approved'
                    approval_dict['ExtractedData']['ActiveInactive'] = 'Active'
                
                approvals.append(approval_dict)
                print(f"Added approved policy {approval.Identifier} to response")
        
        # Debug: print identifiers of all items in the response
        print("\n=== FINAL RESPONSE CONTENTS ===")
        print(f"Total approvals to return: {len(approvals)}")
        
        print("Identifiers in final response:")
        for item in approvals:
            print(f" - {item['Identifier']} | Type: {item['ExtractedData'].get('type', 'unknown')} | ApprovedNot: {item['ApprovedNot']}")
        
        # Debug: count how many approved items we're returning
        approved_count = sum(1 for a in approvals if a.get('ApprovedNot') is True)
        print(f"Returning {approved_count} approved items in the response")
        
        # Get counts
        counts = {
            'pending': sum(1 for a in approvals if a['ApprovedNot'] is None),
            'approved': PolicyApproval.objects.filter(ReviewerId=reviewer_id, ApprovedNot=True).count(),
            'rejected': PolicyApproval.objects.filter(ReviewerId=reviewer_id, ApprovedNot=False).count()
        }
        
        print(f"Approval counts: {counts}")
        print("==== END DEBUGGING DEACTIVATION REQUESTS ====\n\n")
        
        return Response({
            'success': True,
            'data': approvals,
            'counts': counts
        })
        
    except Exception as e:
        print(f"Error in get_policy_approvals_by_reviewer: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
def get_rejected_approvals(request, reviewer_id):
    try:
        print(f"Fetching rejected approvals for reviewer_id: {reviewer_id}")
        
        # Get all policy approvals that have been rejected for this reviewer
        approvals = PolicyApproval.objects.filter(
            ReviewerId=reviewer_id,
            ApprovedNot=False
        ).order_by('-ApprovalId')
       
        print(f"Found {approvals.count()} rejected approvals for reviewer {reviewer_id}")
        
        # Convert to list for JSON serialization
        approvals_list = []
        for approval in approvals:
            # Create a dictionary with approval data
            approval_dict = {
                'ApprovalId': approval.ApprovalId,
                'Identifier': approval.Identifier,
                'ExtractedData': approval.ExtractedData,
                'UserId': approval.UserId,
                'ReviewerId': approval.ReviewerId,
                'ApprovedNot': approval.ApprovedNot,
                'Version': approval.Version,
                'rejection_reason': approval.ExtractedData.get('compliance_approval', {}).get('remarks', ''),
                'ApprovalDueDate': approval.ApprovalDueDate.strftime('%Y-%m-%d') if approval.ApprovalDueDate and hasattr(approval.ApprovalDueDate, 'strftime') else None
            }
            
            # Properly handle the ApprovedDate field if it exists
            if approval.ApprovedDate:
                # Convert to string to avoid JSON serialization issues
                approval_dict['ApprovedDate'] = approval.ApprovedDate.strftime('%Y-%m-%d %H:%M:%S') if hasattr(approval.ApprovedDate, 'strftime') else str(approval.ApprovedDate)
            
            # Check if this approval is already in a resubmission process
            is_resubmitted = approval.ExtractedData.get('compliance_approval', {}).get('inResubmission', False)
            
            # Only include if not already resubmitted
            if not is_resubmitted:
                # Check if this is the latest version for this identifier to avoid duplicates
                latest_approval = PolicyApproval.objects.filter(
                    Identifier=approval.Identifier,
                    ApprovedNot=False
                ).order_by('-ApprovalId').first()
                
                if latest_approval and latest_approval.ApprovalId == approval.ApprovalId:
                    approvals_list.append(approval_dict)
                    print(f"Added rejection for {approval.Identifier} (ID: {approval.ApprovalId})")
                else:
                    print(f"Skipping {approval.Identifier} (ID: {approval.ApprovalId}) as it's not the latest rejected version")
            else:
                print(f"Skipping {approval.Identifier} as it's already in resubmission process")
           
        print(f"Returning {len(approvals_list)} rejections")
        return Response(approvals_list)
       
    except Exception as e:
        print("Error in get_rejected_approvals:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
def get_all_users(request):
    """
    Get all users from the database except system user.
    Returns a list of users with their IDs and usernames only.
    """
    try:
        from django.db import connection
        from .models import Users   
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Get all users except system user, only UserId and UserName
        users = Users.objects.exclude(UserId=1).values('UserId', 'UserName')
        
        # Convert to list
        users_list = list(users)
        
        return Response({
            'success': True,
            'users': users_list,
            'total_count': len(users_list)
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in get_all_users: {error_msg}")
        
        return Response({
            'success': False,
            'message': 'Failed to fetch users',
            'error': error_msg
        }, status=500)
 
@api_view(['POST'])
def toggle_compliance_version(request, compliance_id):
    try:
        print(f"\n=== TOGGLE_COMPLIANCE_VERSION DEBUG ===")
        print(f"Toggling compliance with ID: {compliance_id}")
        
        # Get the target compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        print(f"Found compliance: {compliance.Identifier}, Status: {compliance.Status}, ActiveInactive: {compliance.ActiveInactive}")
       
        # Only allow toggling if compliance is approved
        if compliance.Status != 'Approved':
            print(f"Cannot toggle - compliance status is {compliance.Status}, not Approved")
            return Response({
                'success': False,
                'message': 'Only approved compliances can be toggled'
            }, status=status.HTTP_400_BAD_REQUEST)
 
        # Function to get all related versions by identifier
        def get_all_versions_by_identifier(identifier):
            try:
                # Get all compliances with the same identifier
                versions = Compliance.objects.filter(Identifier=identifier, Status='Approved')
                print(f"Found {versions.count()} related versions with identifier {identifier}")
                return versions
            except Exception as e:
                print(f"Error getting versions by identifier: {str(e)}")
                return []
 
        # Get all versions with the same identifier
        all_versions = get_all_versions_by_identifier(compliance.Identifier)
        
        if not all_versions:
            print(f"No related versions found for identifier {compliance.Identifier}")
            all_versions = [compliance]  # Fallback to just the current compliance
       
        # Determine action based on current status
        is_deactivating = compliance.ActiveInactive == 'Active'
        print(f"Action: {'Deactivating' if is_deactivating else 'Activating'} compliance {compliance_id}")
       
        # Sort versions by version number (descending)
        sorted_versions = sorted(
            all_versions,
            key=lambda v: float(v.ComplianceVersion) if v.ComplianceVersion else 0,
            reverse=True
        )
        
        # Print the sorted versions for debugging
        print("Sorted versions (descending):")
        for v in sorted_versions:
            print(f"  ID: {v.ComplianceId}, Version: {v.ComplianceVersion}, Status: {v.ActiveInactive}")
        
        # If deactivating the current active version, find the next highest version to activate
        if is_deactivating:
            # Find the next highest version after the current one
            next_highest_version = None
            for v in sorted_versions:
                if v.ComplianceId != compliance_id and v.Status == 'Approved':
                    next_highest_version = v
                    break
            
            if next_highest_version:
                print(f"Will activate next highest version: {next_highest_version.ComplianceId} (v{next_highest_version.ComplianceVersion})")
            else:
                print("No other approved version found to activate")
        
        # Update all versions
        updated_count = 0
        for version in all_versions:
            try:
                if is_deactivating:
                    if version.ComplianceId == compliance_id:
                        # Deactivate the target compliance
                        version.ActiveInactive = 'Inactive'
                        print(f"Setting compliance {version.ComplianceId} to Inactive")
                    elif next_highest_version and version.ComplianceId == next_highest_version.ComplianceId:
                        # Activate the next highest version
                        version.ActiveInactive = 'Active'
                        print(f"Setting next highest compliance {version.ComplianceId} to Active")
                    else:
                        # Keep other versions as they are
                        print(f"Keeping compliance {version.ComplianceId} as {version.ActiveInactive}")
                else:
                    # When activating a specific version, deactivate all others
                    if version.ComplianceId == compliance_id:
                        version.ActiveInactive = 'Active'
                        print(f"Setting target compliance {version.ComplianceId} to Active")
                    else:
                        version.ActiveInactive = 'Inactive'
                        print(f"Setting other compliance {version.ComplianceId} to Inactive")
                
                version.save()
                updated_count += 1
            except Exception as version_error:
                print(f"Error updating version {version.ComplianceId}: {str(version_error)}")
                # Continue with other versions

        print(f"Successfully updated {updated_count} out of {len(all_versions)} versions")

        # Send notification to affected users
        try:
            from .notification_service import NotificationService
            notification_service = NotificationService()
            
            # Get affected users (creator and reviewer)
            affected_users = set()
            
            # Add creator's email - assuming CreatedByName contains user ID
            try:
                creator_id = compliance.CreatedByName
                creator_email, creator_name = notification_service.get_user_email_by_id(creator_id)
                if creator_email:
                    affected_users.add(creator_email)
            except Exception as ce:
                print(f"Error getting creator email: {str(ce)}")
            
            # Add reviewer's email from policy approval
            try:
                policy_approval = PolicyApproval.objects.filter(
                    Identifier=compliance.Identifier
                ).first()
                if policy_approval:
                    reviewer_email, reviewer_name = notification_service.get_user_email_by_id(policy_approval.ReviewerId)
                    if reviewer_email:
                        affected_users.add(reviewer_email)
            except Exception as re:
                print(f"Error getting reviewer email: {str(re)}")
            
            if affected_users:
                # Send notifications
                notification_result = notification_service.send_compliance_version_toggle_notification(
                    compliance=compliance,
                    affected_users=list(affected_users)
                )
                print(f"Version toggle notification result: {notification_result}")
            else:
                print("No affected users found for notifications")
        except Exception as e:
            print(f"Error sending version toggle notification: {str(e)}")
            # Continue even if notification fails
       
        new_status = 'Inactive' if is_deactivating else 'Active'
        print("=== END TOGGLE_COMPLIANCE_VERSION DEBUG ===\n")
        return Response({
            'success': True,
            'message': f'Compliance version {compliance.ComplianceVersion} {new_status.lower()}d successfully',
            'compliance_id': compliance_id,
            'new_status': new_status
        })
        
    except Compliance.DoesNotExist:
        print(f"Compliance with ID {compliance_id} not found")
        return Response({
            'success': False,
            'message': f'Compliance with ID {compliance_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in toggle_compliance_version: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def deactivate_compliance(request, compliance_id):
    try:
        print("\n\n==== DEBUGGING DEACTIVATE_COMPLIANCE ====")
        print(f"Received deactivation request for compliance_id: {compliance_id}")
        print(f"Request data: {request.data}")
        
        # Get the target compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        print(f"Found compliance: {compliance.Identifier}, Status: {compliance.Status}")
        
        # Only allow deactivation for active compliances
        if compliance.ActiveInactive != 'Active':
            return Response({
                'success': False,
                'message': 'Only active compliances can be deactivated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the reason from the request
        reason = request.data.get('reason', 'No longer needed')
        
        # Get reviewer ID from the request
        reviewer_id = request.data.get('reviewer_id', 1)  # Default to admin reviewer
        print(f"Using reviewer_id: {reviewer_id}")
        
        # Create a unique identifier for this deactivation request
        deactivation_identifier = f"COMP-DEACTIVATE-{compliance.Identifier}"
        print(f"Created deactivation identifier: {deactivation_identifier}")
        
        # Build the ExtractedData for the deactivation request
        extracted_data = {
            'type': 'compliance_deactivation',
            'compliance_id': compliance_id,
            'identifier': compliance.Identifier,
            'version': compliance.ComplianceVersion,
            'reason': reason,
            'current_status': 'Active',
            'requested_status': 'Inactive',
            'RequestType': 'Change Status to Inactive',
            'affected_policies_count': 0,  # Could be updated with actual count
            'cascade_to_policies': 'Yes' if request.data.get('cascade_to_policies', True) else 'No'
        }
        
        # Log the extracted data
        print(f"ExtractedData: {extracted_data}")
        
        # Create a PolicyApproval record for the deactivation request
        approval = PolicyApproval.objects.create(
            Identifier=deactivation_identifier,
            UserId=request.data.get('user_id', 1),  # Default to admin user
            ReviewerId=reviewer_id,
            Version=compliance.ComplianceVersion,
            ApprovedNot=None,  # Null initially
            PolicyId=compliance.SubPolicy.Policy.PolicyId if hasattr(compliance, 'SubPolicy') and hasattr(compliance.SubPolicy, 'Policy') else None,
            ExtractedData=extracted_data
        )
        
        print(f"Created PolicyApproval record: {approval.ApprovalId}, ReviewerId: {approval.ReviewerId}")
        
        # Verify the approval was created correctly
        try:
            verify_approval = PolicyApproval.objects.get(ApprovalId=approval.ApprovalId)
            print(f"Verification - ApprovalId: {verify_approval.ApprovalId}, Identifier: {verify_approval.Identifier}")
            print(f"Verification - ReviewerId: {verify_approval.ReviewerId}, ApprovedNot: {verify_approval.ApprovedNot}")
            print(f"Verification - ExtractedData type: {verify_approval.ExtractedData.get('type', 'Not set')}")
        except Exception as ve:
            print(f"Error verifying approval: {str(ve)}")
            
        # Send notification to reviewer
        try:
            from .notification_service import NotificationService
            notification_service = NotificationService()
            
            # Get reviewer's email
            reviewer_email, reviewer_name = notification_service.get_user_email_by_id(reviewer_id)
            
            if reviewer_email:
                # Send notification
                notification_data = {
                    'notification_type': 'compliance_creation',  # Reuse creation template
                    'email': reviewer_email,
                    'email_type': 'gmail',  # Default to gmail
                    'template_data': [
                        reviewer_name or reviewer_email.split('@')[0],  # Use name or extract from email
                        compliance.ComplianceId,
                        f"REQUEST TO DEACTIVATE: {compliance.ComplianceItemDescription or 'No description provided'}",
                        compliance.ComplianceVersion,
                        compliance.CreatedByName or "Unknown",
                        datetime.now().strftime('%Y-%m-%d')
                    ]
                }
                
                # Send the notification
                result = notification_service.send_multi_channel_notification(notification_data)
                print(f"Deactivation request notification sent to {reviewer_email}: {result}")
            else:
                print(f"No email found for reviewer ID {reviewer_id}")
        except Exception as e:
            print(f"Error sending deactivation request notification: {str(e)}")
            # Continue even if notification fails
        
        print("==== END DEBUGGING DEACTIVATE_COMPLIANCE ====\n\n")
        
        return Response({
            'success': True,
            'message': 'Deactivation request submitted successfully. Awaiting approval.',
            'approval_id': approval.ApprovalId
        })
        
    except Exception as e:
        print(f"Error in deactivate_compliance: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def approve_compliance_deactivation(request, approval_id):
    try:
        print(f"\n\n==== DEBUGGING APPROVE_DEACTIVATION ====")
        print(f"Approving deactivation request for approval_id: {approval_id}")
        
        # Get the approval record
        approval = get_object_or_404(PolicyApproval, ApprovalId=approval_id)
        print(f"Found approval: {approval.Identifier}")
        
        # Verify it's a compliance deactivation request
        extracted_data = approval.ExtractedData
        if extracted_data.get('type') != 'compliance_deactivation' or extracted_data.get('RequestType') != 'Change Status to Inactive':
            return Response({
                'success': False,
                'message': 'Invalid approval request type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the compliance record
        compliance_id = extracted_data.get('compliance_id')
        print(f"Looking for compliance ID: {compliance_id}")
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        print(f"Found compliance: {compliance.Identifier}, Current status: {compliance.ActiveInactive}")
        
        # Update the compliance status
        compliance.ActiveInactive = 'Inactive'
        compliance.save()
        print(f"Updated compliance {compliance.Identifier} to Inactive")
        
        # Update the approval status
        approval.ApprovedNot = True
        approval.ApprovedDate = timezone.now()
        
        # Update ExtractedData to reflect the changed status
        extracted_data['current_status'] = 'Inactive'
        approval.ExtractedData = extracted_data
        
        # If cascade to policies is enabled, deactivate related policies
        if extracted_data.get('cascade_to_policies') == 'Yes':
            print("Cascade to policies enabled - would deactivate related policies here")
            # Implementation for cascading deactivation would go here
        
        approval.save()
        print(f"Updated approval status to Approved")
        
        # Send notification to compliance creator
        try:
            from .notification_service import NotificationService
            notification_service = NotificationService()
            
            # Get creator's email
            creator_id = approval.UserId
            creator_email, creator_name = notification_service.get_user_email_by_id(creator_id)
            
            if creator_email:
                # Send notification
                notification_result = notification_service.send_compliance_review_notification(
                    compliance=compliance,
                    reviewer_decision=True,  # Approved
                    creator_id=creator_id,
                    remarks="Your request to deactivate this compliance item has been approved."
                )
                print(f"Deactivation approval notification result: {notification_result}")
            else:
                print(f"No email found for creator ID {creator_id}")
        except Exception as e:
            print(f"Error sending deactivation approval notification: {str(e)}")
            # Continue even if notification fails
        
        print("==== END DEBUGGING APPROVE_DEACTIVATION ====\n\n")
        
        return Response({
            'success': True,
            'message': f'Compliance {compliance.Identifier} has been deactivated successfully',
            'compliance': {
                'ComplianceId': compliance.ComplianceId,
                'Identifier': compliance.Identifier,
                'Status': compliance.Status,
                'ActiveInactive': compliance.ActiveInactive
            }
        })
        
    except Exception as e:
        print(f"Error in approve_compliance_deactivation: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reject_compliance_deactivation(request, approval_id):
    try:
        print(f"\n\n==== DEBUGGING REJECT_DEACTIVATION ====")
        print(f"Rejecting deactivation request for approval_id: {approval_id}")
        
        # Get the approval record
        approval = get_object_or_404(PolicyApproval, ApprovalId=approval_id)
        print(f"Found approval: {approval.Identifier}")
        
        # Verify it's a compliance deactivation request
        extracted_data = approval.ExtractedData
        if extracted_data.get('type') != 'compliance_deactivation' or extracted_data.get('RequestType') != 'Change Status to Inactive':
            return Response({
                'success': False,
                'message': 'Invalid approval request type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the compliance ID from extracted data
        compliance_id = extracted_data.get('compliance_id')
        print(f"Referenced compliance ID: {compliance_id}")
        
        # Fetch compliance to notify about
        compliance = None
        try:
            compliance = Compliance.objects.get(ComplianceId=compliance_id)
            print(f"Found compliance: {compliance.Identifier}, Current status: {compliance.ActiveInactive}")
            
            # For clarity, explicitly make sure the compliance stays Active
            if compliance.ActiveInactive != 'Active':
                compliance.ActiveInactive = 'Active'
                compliance.save()
                print(f"Ensured compliance {compliance.Identifier} remains Active")
        except Compliance.DoesNotExist:
            # The compliance might not exist, but we can still reject the request
            print(f"Warning: Compliance with ID {compliance_id} not found")
        
        # Update the approval status
        approval.ApprovedNot = False
        approval.ApprovedDate = timezone.now()
        
        # Get rejection remarks
        remarks = request.data.get('remarks', 'No reason provided')
        
        # Add rejection remarks to ExtractedData
        if request.data.get('remarks'):
            extracted_data['rejection_remarks'] = remarks
            approval.ExtractedData = extracted_data
            print(f"Added rejection remarks: {remarks}")
        
        approval.save()
        print(f"Updated approval status to Rejected")
        
        # Send notification to compliance creator
        if compliance:
            try:
                from .notification_service import NotificationService
                notification_service = NotificationService()
                
                # Get creator's email
                creator_id = approval.UserId
                creator_email, creator_name = notification_service.get_user_email_by_id(creator_id)
                
                if creator_email:
                    # Send notification
                    notification_result = notification_service.send_compliance_review_notification(
                        compliance=compliance,
                        reviewer_decision=False,  # Rejected
                        creator_id=creator_id,
                        remarks=f"Your request to deactivate this compliance item has been rejected. Reason: {remarks}"
                    )
                    print(f"Deactivation rejection notification result: {notification_result}")
                else:
                    print(f"No email found for creator ID {creator_id}")
            except Exception as e:
                print(f"Error sending deactivation rejection notification: {str(e)}")
                # Continue even if notification fails
        
        print("==== END DEBUGGING REJECT_DEACTIVATION ====\n\n")
        
        return Response({
            'success': True,
            'message': 'Deactivation request has been rejected'
        })
        
    except Exception as e:
        print(f"Error in reject_compliance_deactivation: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
def test_analytics_endpoint(request):
    return Response({
        'success': True,
        'message': 'Analytics endpoint is reachable'
    })

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def get_compliance_analytics(request):
    try:
        print("Received analytics request with data:", request.data)
        x_axis = request.data.get('xAxis')
        y_axis = request.data.get('yAxis')

        if not x_axis or not y_axis:
            return Response({
                'success': False,
                'message': 'Both X and Y axis parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset
        queryset = Compliance.objects.all()
        
        # Get counts for dashboard metrics
        total_compliances = queryset.count()
        approved_compliances = queryset.filter(Status='Approved').count()
        active_compliances = queryset.filter(ActiveInactive='Active').count()
        under_review_compliances = queryset.filter(Status='Under Review').count()

        # Calculate approval rate
        approval_rate = (approved_compliances / total_compliances * 100) if total_compliances > 0 else 0

        # Initialize chart data based on Y axis selection
        labels = []
        data = []

        if y_axis == 'Criticality':
            counts = queryset.values('Criticality').annotate(
                count=models.Count('ComplianceId')
            ).exclude(Criticality__isnull=True).exclude(Criticality='')
            labels = ['High', 'Medium', 'Low']
            data = [
                next((item['count'] for item in counts if item['Criticality'] == 'High'), 0),
                next((item['count'] for item in counts if item['Criticality'] == 'Medium'), 0),
                next((item['count'] for item in counts if item['Criticality'] == 'Low'), 0)
            ]

        elif y_axis == 'Status':
            counts = queryset.values('Status').annotate(
                count=models.Count('ComplianceId')
            ).exclude(Status__isnull=True).exclude(Status='')
            labels = ['Approved', 'Under Review', 'Rejected', 'Active']
            data = [
                next((item['count'] for item in counts if item['Status'] == 'Approved'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Under Review'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Rejected'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Active'), 0)
            ]

        elif y_axis == 'ActiveInactive':
            counts = queryset.values('ActiveInactive').annotate(
                count=models.Count('ComplianceId')
            ).exclude(ActiveInactive__isnull=True).exclude(ActiveInactive='')
            labels = ['Active', 'Inactive']
            data = [
                next((item['count'] for item in counts if item['ActiveInactive'] == 'Active'), 0),
                next((item['count'] for item in counts if item['ActiveInactive'] == 'Inactive'), 0)
            ]

        elif y_axis == 'ManualAutomatic':
            counts = queryset.values('ManualAutomatic').annotate(
                count=models.Count('ComplianceId')
            ).exclude(ManualAutomatic__isnull=True).exclude(ManualAutomatic='')
            labels = ['Manual', 'Automatic']
            data = [
                next((item['count'] for item in counts if item['ManualAutomatic'] == 'Manual'), 0),
                next((item['count'] for item in counts if item['ManualAutomatic'] == 'Automatic'), 0)
            ]

        elif y_axis == 'MandatoryOptional':
            counts = queryset.values('MandatoryOptional').annotate(
                count=models.Count('ComplianceId')
            ).exclude(MandatoryOptional__isnull=True).exclude(MandatoryOptional='')
            labels = ['Mandatory', 'Optional']
            data = [
                next((item['count'] for item in counts if item['MandatoryOptional'] == 'Mandatory'), 0),
                next((item['count'] for item in counts if item['MandatoryOptional'] == 'Optional'), 0)
            ]

        elif y_axis == 'MaturityLevel':
            counts = queryset.values('MaturityLevel').annotate(
                count=models.Count('ComplianceId')
            ).exclude(MaturityLevel__isnull=True).exclude(MaturityLevel='')
            labels = ['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing']
            data = [
                next((item['count'] for item in counts if item['MaturityLevel'] == level), 0)
                for level in labels
            ]

        # Prepare dashboard data
        dashboard_data = {
            'status_counts': {
                'approved': approved_compliances,
                'active': active_compliances,
                'under_review': under_review_compliances
            },
            'total_count': total_compliances,
            'total_findings': queryset.filter(IsRisk=True).count(),
            'approval_rate': round(approval_rate, 2)
        }

        # Prepare chart data
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': f'Compliance by {y_axis.replace("By ", "")}',
                'data': data
            }]
        }

        print("Sending response with dashboard_data:", dashboard_data)
        print("Chart data:", chart_data)

        return Response({
            'success': True,
            'chartData': chart_data,
            'dashboardData': dashboard_data
        })

    except Exception as e:
        print(f"Error in get_compliance_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
 #---------------------------------KPI Dashboard---------------------------------
 
@api_view(['GET'])
def get_compliance_kpi(request):
    try:
        # Get all compliances
        compliances = Compliance.objects.all()
        
        # Calculate KPIs
        total_compliances = compliances.count()
        active_compliances = compliances.filter(ActiveInactive='Active').count()
        approved_compliances = compliances.filter(Status='Approved').count()
        
        # Calculate compliance rate
        compliance_rate = (approved_compliances / total_compliances * 100) if total_compliances > 0 else 0
        
        # Get risk distribution
        high_risk = compliances.filter(Criticality='High').count()
        medium_risk = compliances.filter(Criticality='Medium').count()
        low_risk = compliances.filter(Criticality='Low').count()
        
        # Calculate maturity levels distribution
        maturity_levels = {
            'Initial': compliances.filter(MaturityLevel='Initial').count(),
            'Developing': compliances.filter(MaturityLevel='Developing').count(),
            'Defined': compliances.filter(MaturityLevel='Defined').count(),
            'Managed': compliances.filter(MaturityLevel='Managed').count(),
            'Optimizing': compliances.filter(MaturityLevel='Optimizing').count()
        }
        
        # Calculate average maturity score
        maturity_scores = {
            'Initial': 1,
            'Developing': 2,
            'Defined': 3,
            'Managed': 4,
            'Optimizing': 5
        }
        total_score = sum(maturity_scores[level] * count for level, count in maturity_levels.items())
        avg_maturity = total_score / total_compliances if total_compliances > 0 else 0
        
        # Get control types distribution
        manual_controls = compliances.filter(ManualAutomatic='Manual').count()
        automatic_controls = compliances.filter(ManualAutomatic='Automatic').count()
        
        # Get mandatory vs optional distribution
        mandatory_controls = compliances.filter(MandatoryOptional='Mandatory').count()
        optional_controls = compliances.filter(MandatoryOptional='Optional').count()
        
        return Response({
            'success': True,
            'data': {
                'compliance_rate': round(compliance_rate, 2),
                'active_controls': active_compliances,
                'maturity_score': round(avg_maturity, 2),
                'risk_distribution': {
                    'high': high_risk,
                    'medium': medium_risk,
                    'low': low_risk
                },
                'maturity_levels': maturity_levels,
                'control_types': {
                    'manual': manual_controls,
                    'automatic': automatic_controls
                },
                'control_requirements': {
                    'mandatory': mandatory_controls,
                    'optional': optional_controls
                },
                'total_compliances': total_compliances,
                'approved_compliances': approved_compliances
            }
        })
        
    except Exception as e:
        print(f"Error in get_compliance_kpi: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_maturity_level_kpi(request):
    try:
        # Get only active and approved compliances
        compliances = Compliance.objects.filter(
            ActiveInactive='Active',
            Status='Approved'
        )
        
        # Calculate counts for each maturity level
        maturity_counts = {
            'Initial': compliances.filter(MaturityLevel='Initial').count(),
            'Developing': compliances.filter(MaturityLevel='Developing').count(),
            'Defined': compliances.filter(MaturityLevel='Defined').count(),
            'Managed': compliances.filter(MaturityLevel='Managed').count(),
            'Optimizing': compliances.filter(MaturityLevel='Optimizing').count()
        }
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_by_maturity': maturity_counts,
                    'total_compliances': compliances.count()
                }
            }
        })
        
    except Exception as e:
        print(f"Error in get_maturity_level_kpi: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_non_compliance_count(request):
    try:
        # Count records with non-zero count
        non_compliance_count = LastChecklistItemVerified.objects.filter(
            Count__gt=0
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'non_compliance_count': non_compliance_count
            }
        })
        
    except Exception as e:
        print(f"Error in get_non_compliance_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_mitigated_risks_count(request):
    try:
        # Count risks that have been mitigated (MitigationStatus = 'Completed')
        mitigated_count = RiskInstance.objects.filter(
            MitigationStatus=RiskInstance.MITIGATION_COMPLETED
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'mitigated_count': mitigated_count
            }
        })
        
    except Exception as e:
        print(f"Error in get_mitigated_risks_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_automated_controls_count(request):
    try:
        # Get base queryset for active and approved compliances
        base_query = Compliance.objects.filter(
            Status='Approved',
            ActiveInactive='Active'
        )
        
        # Count automated and manual controls
        automated_count = base_query.filter(ManualAutomatic='Automatic').count()
        manual_count = base_query.filter(ManualAutomatic='Manual').count()
        
        # Calculate percentages
        total = automated_count + manual_count
        automated_percentage = round((automated_count / total * 100) if total > 0 else 0, 1)
        manual_percentage = round((manual_count / total * 100) if total > 0 else 0, 1)
        
        return Response({
            'success': True,
            'data': {
                'automated_count': automated_count,
                'manual_count': manual_count,
                'total_count': total,
                'automated_percentage': automated_percentage,
                'manual_percentage': manual_percentage
            }
        })
        
    except Exception as e:
        print(f"Error in get_automated_controls_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_non_compliance_repetitions(request):
    try:
        # Get items with non-zero count
        repetitions = LastChecklistItemVerified.objects.filter(
            Count__gt=0
        ).order_by('-Count')

        # Calculate statistics
        total_items = repetitions.count()
        max_repetitions = repetitions.aggregate(max_count=models.Max('Count'))['max_count'] or 0
        avg_repetitions = repetitions.aggregate(avg_count=models.Avg('Count'))['avg_count'] or 0

        # Get distribution of repetitions
        distribution = {}
        for item in repetitions:
            count = item.Count
            if count in distribution:
                distribution[count] += 1
            else:
                distribution[count] = 1

        # Convert distribution to sorted list for chart
        chart_data = [
            {'repetitions': count, 'occurrences': freq}
            for count, freq in sorted(distribution.items())
        ]

        return Response({
            'success': True,
            'data': {
                'total_items': total_items,
                'max_repetitions': max_repetitions,
                'avg_repetitions': round(avg_repetitions, 1),
                'distribution': chart_data
            }
        })
        
    except Exception as e:
        print(f"Error in get_non_compliance_repetitions: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#----------------------------------Compliance List---------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_frameworks(request):
    """
    API endpoint to get all frameworks for AllPolicies.vue component.
    """
    try:
        frameworks = Framework.objects.all()
       
        frameworks_data = []
        for framework in frameworks:
            framework_data = {
                'id': framework.FrameworkId,
                'name': framework.FrameworkName,
                'category': framework.Category,
                'status': framework.ActiveInactive,
                'description': framework.FrameworkDescription,
                'versions': []
            }
           
            # Get versions for this framework
            versions = FrameworkVersion.objects.filter(FrameworkId=framework)
            version_data = []
            for version in versions:
                version_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            framework_data['versions'] = version_data
            frameworks_data.append(framework_data)
           
        return Response(frameworks_data)
   
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_framework_version_policies(request, version_id):
    """
    API endpoint to get all policies for a specific framework version for AllPolicies.vue component.
    """
    try:
        # Get the framework version
        framework_version = get_object_or_404(FrameworkVersion, VersionId=version_id)
        framework = framework_version.FrameworkId
       
        # Get policies for this framework
        policies = Policy.objects.filter(
            Framework=framework,
            CurrentVersion=framework_version.Version
        )
       
        policies_data = []
        for policy in policies:
            policy_data = {
                'id': policy.PolicyId,
                'name': policy.PolicyName,
                'category': policy.Department,
                'status': policy.Status,
                'description': policy.PolicyDescription,
                'versions': []
            }
           
            # Get versions for this policy
            policy_versions = PolicyVersion.objects.filter(PolicyId=policy)
            versions_data = []
            for version in policy_versions:
                versions_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            policy_data['versions'] = versions_data
            policies_data.append(policy_data)
           
        return Response(policies_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policies(request):
    """
    API endpoint to get all policies for AllPolicies.vue component.
    """
    try:
        # Optional framework filter
        framework_id = request.GET.get('framework_id')
       
        # Start with all policies
        policies_query = Policy.objects.all()
       
        # Apply framework filter if provided
        if framework_id:
            policies_query = policies_query.filter(FrameworkId=framework_id)
       
        policies_data = []
        for policy in policies_query:
            policy_data = {
                'id': policy.PolicyId,
                'name': policy.PolicyName,
                'category': policy.Department,
                'status': policy.Status,
                'description': policy.PolicyDescription,
                'versions': []
            }
           
            # Get versions for this policy
            policy_versions = PolicyVersion.objects.filter(PolicyId=policy)
            versions_data = []
            for version in policy_versions:
                versions_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            policy_data['versions'] = versions_data
            policies_data.append(policy_data)
           
        return Response(policies_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policy_versions(request, policy_id):
    """
    API endpoint to get all versions of a specific policy for AllPolicies.vue component.
    Implements a dedicated version that handles version chains through PreviousVersionId.
    """
    try:
        print(f"Request received for policy versions, policy_id: {policy_id}, type: {type(policy_id)}")
       
        # Ensure we have a valid integer ID
        try:
            policy_id = int(policy_id)
        except (ValueError, TypeError):
            return Response({'error': f'Invalid policy ID format: {policy_id}'},
                           status=status.HTTP_400_BAD_REQUEST)
       
        # Get the base policy
        try:
            policy = Policy.objects.get(PolicyId=policy_id)
            print(f"Found policy: {policy.PolicyName} (ID: {policy.PolicyId})")
        except Policy.DoesNotExist:
            print(f"Policy with ID {policy_id} not found")
            return Response({'error': f'Policy with ID {policy_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get the direct policy version
        try:
            direct_version = PolicyVersion.objects.get(PolicyId=policy)
            print(f"Found direct policy version: {direct_version.VersionId}")
        except PolicyVersion.DoesNotExist:
            print(f"No policy version found for policy ID {policy_id}")
            return Response({'error': f'No version found for policy with ID {policy_id}'},
                           status=status.HTTP_404_NOT_FOUND)
        except PolicyVersion.MultipleObjectsReturned:
            # If there are multiple versions, get all of them
            direct_versions = list(PolicyVersion.objects.filter(PolicyId=policy))
            print(f"Found {len(direct_versions)} direct versions for policy {policy_id}")
            direct_version = direct_versions[0]  # Just use the first one for starting the chain
       
        # Start building version chain
        all_versions = {}
        visited = set()
        to_process = [direct_version.VersionId]
       
        # Find all versions in the chain
        while to_process:
            current_id = to_process.pop(0)
           
            if current_id in visited:
                continue
               
            visited.add(current_id)
           
            try:
                current_version = PolicyVersion.objects.get(VersionId=current_id)
                all_versions[current_id] = current_version
               
                # Follow PreviousVersionId chain backward
                if current_version.PreviousVersionId and current_version.PreviousVersionId not in visited:
                    to_process.append(current_version.PreviousVersionId)
                   
                # Find versions that reference this one as their previous version
                next_versions = PolicyVersion.objects.filter(PreviousVersionId=current_id)
                for next_ver in next_versions:
                    if next_ver.VersionId not in visited:
                        to_process.append(next_ver.VersionId)
            except PolicyVersion.DoesNotExist:
                print(f"Version with ID {current_id} not found")
                continue
       
        versions_data = []
        for version_id, version in all_versions.items():
            try:
                # Get the policy this version belongs to
                version_policy = version.PolicyId
               
                # Count subpolicies for this policy
                subpolicy_count = SubPolicy.objects.filter(PolicyId=version_policy).count()
               
                # Get previous version details if available
                previous_version = None
                if version.PreviousVersionId:
                    try:
                        previous_version = PolicyVersion.objects.get(VersionId=version.PreviousVersionId)
                    except PolicyVersion.DoesNotExist:
                        pass
               
                # Create a descriptive name
                formatted_name = f"{version.PolicyName} v{version.Version}" if version.PolicyName else f"{version_policy.PolicyName} v{version.Version}"
               
                version_data = {
                    'id': version.VersionId,
                    'policy_id': version_policy.PolicyId,
                    'name': formatted_name,
                    'version': version.Version,
                    'category': version_policy.Department or 'General',
                    'status': version_policy.Status or 'Unknown',
                    'description': version_policy.PolicyDescription or '',
                    'created_date': version.CreatedDate,
                    'created_by': version.CreatedBy,
                    'subpolicy_count': subpolicy_count,
                    'previous_version_id': version.PreviousVersionId,
                    'previous_version_name': previous_version.PolicyName + f" v{previous_version.Version}" if previous_version else None
                }
                versions_data.append(version_data)
                print(f"Added version: {version.VersionId} - {formatted_name}, Previous: {version.PreviousVersionId}")
            except Exception as e:
                print(f"Error processing version {version_id}: {str(e)}")
                # Continue to next version
       
        # Sort versions by version number (descending)
        versions_data.sort(key=lambda x: float(x['version']), reverse=True)
 
       
       
        print(f"Returning {len(versions_data)} policy versions")
        return Response(versions_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_policy_versions: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicies(request):
    """
    API endpoint to get all subpolicies for AllPolicies.vue component.
    """
    try:
        print("Request received for all subpolicies")
       
        # Optional framework filter
        framework_id = request.GET.get('framework_id')
        print(f"Framework filter: {framework_id}")
       
        # Start with all subpolicies
        subpolicies_query = SubPolicy.objects.all()
       
        # If framework filter is provided, filter through policies
        if framework_id:
            try:
                policy_ids = Policy.objects.filter(FrameworkId=framework_id).values_list('PolicyId', flat=True)
                print(f"Found {len(policy_ids)} policies for framework {framework_id}")
                subpolicies_query = subpolicies_query.filter(PolicyId__in=policy_ids)
            except Exception as e:
                print(f"Error filtering by framework: {str(e)}")
                # Continue with all subpolicies if framework filtering fails
       
        print(f"Found {subpolicies_query.count()} subpolicies")
       
        subpolicies_data = []
        for subpolicy in subpolicies_query:
            try:
                # Get the policy this subpolicy belongs to
                try:
                    policy = subpolicy.PolicyId  # Use the ForeignKey relationship directly
                    policy_name = policy.PolicyName
                    department = policy.Department
                except (Policy.DoesNotExist, AttributeError):
                    print(f"Policy not found for subpolicy {subpolicy.SubPolicyId}")
                    policy_name = "Unknown Policy"
                    department = "Unknown"
               
                subpolicy_data = {
                    'id': subpolicy.SubPolicyId,
                    'name': subpolicy.SubPolicyName,
                    'category': department or 'General',
                    'status': subpolicy.Status or 'Unknown',
                    'description': subpolicy.Description or '',
                    'control': subpolicy.Control or '',
                    'identifier': subpolicy.Identifier,
                    'permanent_temporary': subpolicy.PermanentTemporary,
                    'policy_id': subpolicy.PolicyId.PolicyId,  # Get the actual PolicyId value
                    'policy_name': policy_name,
                    'created_by': subpolicy.CreatedByName,
                    'created_date': subpolicy.CreatedByDate
                }
                subpolicies_data.append(subpolicy_data)
                print(f"Added subpolicy: {subpolicy.SubPolicyId} - {subpolicy.SubPolicyName}")
            except Exception as e:
                print(f"Error processing subpolicy {subpolicy.SubPolicyId}: {str(e)}")
                # Continue to next subpolicy
       
        print(f"Returning {len(subpolicies_data)} subpolicies")
        return Response(subpolicies_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_subpolicies: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicy_details(request, subpolicy_id):
    """
    API endpoint to get details of a specific subpolicy for AllPolicies.vue component.
    """
    try:
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
        policy = subpolicy.PolicyId
       
        subpolicy_data = {
            'id': subpolicy.SubPolicyId,
            'name': subpolicy.SubPolicyName,
            'category': policy.Department,
            'status': subpolicy.Status,
            'description': subpolicy.Description,
            'control': subpolicy.Control,
            'identifier': subpolicy.Identifier,
            'permanent_temporary': subpolicy.PermanentTemporary,
            'policy_id': policy.PolicyId,
            'policy_name': policy.PolicyName
        }
       
        return Response(subpolicy_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_framework_versions(request, framework_id):
    try:
        print(f"Request received for framework versions, framework_id: {framework_id}")
       
        # Get the base framework
        try:
            framework = Framework.objects.get(FrameworkId=framework_id)
            print(f"Found framework: {framework.FrameworkName}")
        except Framework.DoesNotExist:
            print(f"Framework with ID {framework_id} not found")
            return Response({'error': f'Framework with ID {framework_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get direct versions that belong to this framework
        direct_versions = list(FrameworkVersion.objects.filter(FrameworkId=framework))
        print(f"Found {len(direct_versions)} direct versions")
       
        versions_data = []
        for version in direct_versions:
            try:
                # Count policies for this framework version
                policy_count = Policy.objects.filter(
                    Framework=framework
                ).count()
               
                # Get previous version details if available
                previous_version = None
                if version.PreviousVersionId:
                    try:
                        previous_version = FrameworkVersion.objects.get(VersionId=version.PreviousVersionId)
                    except FrameworkVersion.DoesNotExist:
                        pass
               
                formatted_name = f"{version.FrameworkName} v{version.Version}"
               
                version_data = {
                    'id': version.VersionId,
                    'name': formatted_name,
                    'version': version.Version,
                    'category': framework.Category or 'General',
                    'status': framework.ActiveInactive or 'Unknown',
                    'description': framework.FrameworkDescription or '',
                    'created_date': version.CreatedDate,
                    'created_by': version.CreatedBy,
                    'policy_count': policy_count,
                    'previous_version_id': version.PreviousVersionId,
                    'previous_version_name': previous_version.FrameworkName + f" v{previous_version.Version}" if previous_version else None,
                    'framework_id': framework.FrameworkId
                }
                versions_data.append(version_data)
                print(f"Added version: {version.VersionId} - {formatted_name}")
            except Exception as e:
                print(f"Error processing version {version.VersionId}: {str(e)}")
                continue
       
        # Sort versions by version number (descending)
        versions_data.sort(key=lambda x: float(x['version']), reverse=True)
       
        print(f"Returning {len(versions_data)} versions")
        return Response(versions_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_framework_versions: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policy_version_subpolicies(request, version_id):
    """
    API endpoint to get all subpolicies for a specific policy version for AllPolicies.vue component.
    Implements a dedicated version instead of using the existing get_policy_version_subpolicies function.
    """
    try:
        print(f"Request received for policy version subpolicies, version_id: {version_id}, type: {type(version_id)}")
       
        # Ensure we have a valid integer ID
        try:
            version_id = int(version_id)
        except (ValueError, TypeError):
            print(f"Invalid version ID format: {version_id}")
            return Response({'error': f'Invalid version ID format: {version_id}'},
                           status=status.HTTP_400_BAD_REQUEST)
       
        # Get the policy version
        try:
            policy_version = PolicyVersion.objects.get(VersionId=version_id)
            print(f"Found policy version: {policy_version.VersionId} for policy {policy_version.PolicyId_id}")
        except PolicyVersion.DoesNotExist:
            print(f"Policy version with ID {version_id} not found")
            return Response({'error': f'Policy version with ID {version_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get the policy this version belongs to
        try:
            policy = Policy.objects.get(PolicyId=policy_version.PolicyId_id)
            print(f"Found policy: {policy.PolicyName} (ID: {policy.PolicyId})")
        except Policy.DoesNotExist:
            print(f"Policy with ID {policy_version.PolicyId_id} not found")
            return Response({'error': f'Policy with ID {policy_version.PolicyId_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get subpolicies for this policy
        subpolicies = SubPolicy.objects.filter(PolicyId=policy)
        print(f"Found {len(subpolicies)} subpolicies for policy {policy.PolicyId}")
       
        subpolicies_data = []
        for subpolicy in subpolicies:
            try:
                subpolicy_data = {
                    'id': subpolicy.SubPolicyId,
                    'name': subpolicy.SubPolicyName,
                    'category': policy.Department or 'General',
                    'status': subpolicy.Status or 'Unknown',
                    'description': subpolicy.Description or '',
                    'control': subpolicy.Control or '',
                    'identifier': subpolicy.Identifier,
                    'permanent_temporary': subpolicy.PermanentTemporary,
                    'policy_id': policy.PolicyId,
                    'policy_name': policy.PolicyName,
                    'created_by': subpolicy.CreatedByName,
                    'created_date': subpolicy.CreatedByDate
                }
                subpolicies_data.append(subpolicy_data)
                print(f"Added subpolicy: {subpolicy.SubPolicyId} - {subpolicy.SubPolicyName}")
            except Exception as e:
                print(f"Error processing subpolicy {subpolicy.SubPolicyId}: {str(e)}")
                # Continue to next subpolicy
       
        print(f"Returning {len(subpolicies_data)} subpolicies")
        return Response(subpolicies_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_policy_version_subpolicies: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicy_compliances(request, subpolicy_id):
    """Get all compliances for a specific subpolicy"""
    try:
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
        compliances = Compliance.objects.filter(
            SubPolicy=subpolicy_id
        ).select_related('SubPolicy', 'SubPolicy__PolicyId', 'SubPolicy__PolicyId__FrameworkId')
        
        compliances_data = []
        for compliance in compliances:
            compliances_data.append({
                'ComplianceId': compliance.ComplianceId,
                'ComplianceItemDescription': compliance.ComplianceItemDescription,
                'Status': compliance.Status,
                'Criticality': compliance.Criticality,
                'MaturityLevel': compliance.MaturityLevel,
                'MandatoryOptional': compliance.MandatoryOptional,
                'ManualAutomatic': compliance.ManualAutomatic,
                'CreatedByName': compliance.CreatedByName,
                'CreatedByDate': compliance.CreatedByDate.strftime('%Y-%m-%d') if compliance.CreatedByDate else None,
                'ComplianceVersion': compliance.ComplianceVersion,
                'Identifier': compliance.Identifier,
                'SubPolicyName': compliance.SubPolicy.SubPolicyName,
                'PolicyName': compliance.SubPolicy.PolicyId.PolicyName,
                'FrameworkName': compliance.SubPolicy.PolicyId.FrameworkId.FrameworkName
            })
        
        return Response({
            'success': True,
            'name': subpolicy.SubPolicyName,
            'compliances': compliances_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_compliance_versions(request, compliance_id):
    """
    API endpoint to get all versions of a specific compliance.
    """
    try:
        # Get the initial compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Initialize list to store all versions
        versions = []
        current = compliance
        
        # First, get all previous versions
        while current:
            versions.append(current)
            current = current.PreviousComplianceVersionId
            
        # Then, get all next versions
        current = compliance
        while True:
            next_versions = Compliance.objects.filter(PreviousComplianceVersionId=current.ComplianceId)
            if not next_versions.exists():
                break
            current = next_versions.first()
            versions.append(current)
            
        # Sort versions by version number
        versions.sort(key=lambda x: float(x.ComplianceVersion), reverse=True)
        
        # Convert to response format
        versions_data = []
        for version in versions:
            version_data = {
                'ComplianceId': version.ComplianceId,
                'ComplianceVersion': version.ComplianceVersion,
                'ComplianceItemDescription': version.ComplianceItemDescription,
                'Status': version.Status,
                'Criticality': version.Criticality,
                'MaturityLevel': version.MaturityLevel,
                'ActiveInactive': version.ActiveInactive,
                'CreatedByName': version.CreatedByName,
                'CreatedByDate': version.CreatedByDate.isoformat() if version.CreatedByDate else None,
                'Identifier': version.Identifier,
                'IsRisk': version.IsRisk,
                'MandatoryOptional': version.MandatoryOptional,
                'ManualAutomatic': version.ManualAutomatic,
                'PreviousVersionId': version.PreviousComplianceVersionId.ComplianceId if version.PreviousComplianceVersionId else None
            }
            versions_data.append(version_data)
            
        return Response(versions_data)
        
    except Exception as e:
        print(f"Error in all_policies_get_compliance_versions: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.db import connection
import logging

@api_view(['GET'])
def get_framework_compliances(request, framework_id):
    """Get all compliances under a framework"""

    logging.info(f"Getting compliances for framework_id: {framework_id}")
    try:
        framework = get_object_or_404(Framework, FrameworkId=framework_id)
        logging.info(f"Found framework: {framework.FrameworkName}")

        # Log the SQL query before executing it
        compliances = Compliance.objects.filter(
            SubPolicy__PolicyId__FrameworkId=framework
        ).select_related('SubPolicy', 'SubPolicy__PolicyId')
        
        logging.info(f"SQL Query: {connection.queries[-1]}")
        
        compliances_data = []
        for compliance in compliances:
            compliances_data.append({
                'ComplianceId': compliance.ComplianceId,
                'ComplianceItemDescription': compliance.ComplianceItemDescription,
                'Status': compliance.Status,
                'Criticality': compliance.Criticality,
                'MaturityLevel': compliance.MaturityLevel,
                'MandatoryOptional': compliance.MandatoryOptional,
                'ManualAutomatic': compliance.ManualAutomatic,
                'CreatedByName': compliance.CreatedByName,
                'CreatedByDate': compliance.CreatedByDate,
                'ComplianceVersion': compliance.ComplianceVersion,
                'Identifier': compliance.Identifier,
                'PermanentTemporary': compliance.PermanentTemporary,
                'SubPolicyName': compliance.SubPolicy.SubPolicyName,
                'PolicyName': compliance.SubPolicy.PolicyId.PolicyName
            })
        
        return Response({
            'success': True,
            'name': framework.FrameworkName,
            'compliances': compliances_data
        })
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['GET'])
def get_policy_compliances(request, policy_id):
    """Get all compliances under a policy"""
    try:
        policy = get_object_or_404(Policy, PolicyId=policy_id)
        compliances = Compliance.objects.filter(
            SubPolicy__PolicyId=policy
        ).select_related('SubPolicy')
        
        compliances_data = []
        for compliance in compliances:
            compliances_data.append({
                'ComplianceId': compliance.ComplianceId,
                'ComplianceItemDescription': compliance.ComplianceItemDescription,
                'Status': compliance.Status,
                'Criticality': compliance.Criticality,
                'MaturityLevel': compliance.MaturityLevel,
                'MandatoryOptional': compliance.MandatoryOptional,
                'ManualAutomatic': compliance.ManualAutomatic,
                'CreatedByName': compliance.CreatedByName,
                'CreatedByDate': compliance.CreatedByDate,
                'ComplianceVersion': compliance.ComplianceVersion,
                'Identifier': compliance.Identifier,
                'PermanentTemporary': compliance.PermanentTemporary,
                'SubPolicyName': compliance.SubPolicy.SubPolicyName
            })
        
        return Response({
            'success': True,
            'name': policy.PolicyName,
            'compliances': compliances_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@csrf_exempt
@permission_classes([AllowAny])
def export_compliances(request, export_format, item_type=None, item_id=None):
    """Export compliances based on format and optional filters"""
    try:
        # Get user ID from request
        user_id = request.user.id if request.user.is_authenticated else 1  # Default to system user
        
        # Create export task
        export_task = ExportTask.objects.create(
            export_data={
                'file_type': export_format,
                'user_id': str(user_id),
                'item_type': item_type,
                'item_id': item_id
            },
            file_type=export_format,
            user_id=str(user_id),
            status='pending'
        )
        
        # Get user email for notification
        try:
            from .notification_service import NotificationService
            notification_service = NotificationService()
            user_email, user_name = notification_service.get_user_email_by_id(user_id)
        except Exception as e:
            print(f"Error getting user email: {str(e)}")
            user_email = None
            user_name = None
        
        # Process the export
        try:
            # Fetch compliance data based on filters
            compliances_data = []
            
            if item_type == 'framework' and item_id:
                # Export all compliances for a specific framework
                compliances = Compliance.objects.filter(
                    SubPolicy__PolicyId__FrameworkId=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            elif item_type == 'policy' and item_id:
                # Export all compliances for a specific policy
                compliances = Compliance.objects.filter(
                    SubPolicy__PolicyId=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            elif item_type == 'subpolicy' and item_id:
                # Export all compliances for a specific subpolicy
                compliances = Compliance.objects.filter(
                    SubPolicy_id=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            else:
                # Export all compliances
                compliances = Compliance.objects.all().select_related(
                    'SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework'
                )
            
            # Format compliance data for export
            for compliance in compliances:
                compliances_data.append({
                    'Compliance ID': compliance.ComplianceId,
                    'Description': compliance.ComplianceItemDescription or '',
                    'Status': compliance.Status or '',
                    'Criticality': compliance.Criticality or '',
                    'Maturity Level': compliance.MaturityLevel or '',
                    'Type': compliance.ComplianceType or '',
                    'Implementation': compliance.ManualAutomatic or '',
                    'Created By': compliance.CreatedByName or '',
                    'Created Date': compliance.CreatedByDate.strftime('%Y-%m-%d') if compliance.CreatedByDate else '',
                    'Version': compliance.ComplianceVersion or '',
                    'Identifier': compliance.Identifier or '',
                    'Active/Inactive': compliance.ActiveInactive or '',
                    'Is Risk': 'Yes' if compliance.IsRisk else 'No',
                    'SubPolicy': compliance.SubPolicy.SubPolicyName if compliance.SubPolicy else '',
                    'Policy': compliance.SubPolicy.Policy.PolicyName if compliance.SubPolicy and compliance.SubPolicy.Policy else '',
                    'Framework': compliance.SubPolicy.Policy.Framework.FrameworkName if compliance.SubPolicy and compliance.SubPolicy.Policy and compliance.SubPolicy.Policy.Framework else ''
                })
            
            # Use the export_data function from export_service
            from .export_service import export_data
            result = export_data(
                data=compliances_data,
                file_format=export_format,
                user_id=str(user_id),
                options={'item_type': item_type, 'item_id': item_id},
                export_id=export_task.id
            )
            
            # Task is already updated by export_data function
            # Just refresh the task to get updated values
            export_task.refresh_from_db()
            
            # Send completion notification if we have user email
            if user_email:
                try:
                    from .notification_service import NotificationService
                    notification_service = NotificationService()
                    notification_result = notification_service.send_export_completion_notification(
                        user_id=user_id,
                        export_details={
                            'id': export_task.id,
                            'file_name': export_task.file_name,
                            'file_type': export_task.file_type,
                            's3_url': export_task.s3_url,
                            'completed_at': export_task.completed_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )
                    print(f"Export completion notification result: {notification_result}")
                except Exception as e:
                    print(f"Error sending export completion notification: {str(e)}")
            
        except Exception as e:
            # Update task with error
            export_task.status = 'failed'
            export_task.error = str(e)
            export_task.save()
            raise
        
        return Response({
            'success': True,
            'message': 'Export completed successfully',
            'task_id': export_task.id,
            'download_url': export_task.s3_url
        })
        
    except Exception as e:
        print(f"Error in export_compliances: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@shared_task
def process_export_task(task_id, item_type=None, item_id=None):
    try:
        # Get the task
        task = ExportTask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()
        
        # Process the export
        try:
            # Fetch compliance data based on filters
            compliances_data = []
            
            if item_type == 'framework' and item_id:
                # Export all compliances for a specific framework
                compliances = Compliance.objects.filter(
                    SubPolicy__Policy__FrameworkId=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            elif item_type == 'policy' and item_id:
                # Export all compliances for a specific policy
                compliances = Compliance.objects.filter(
                    SubPolicy__PolicyId=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            elif item_type == 'subpolicy' and item_id:
                # Export all compliances for a specific subpolicy
                compliances = Compliance.objects.filter(
                    SubPolicy_id=item_id
                ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
            else:
                # Export all compliances
                compliances = Compliance.objects.all().select_related(
                    'SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework'
                )
            
            # Format compliance data for export
            for compliance in compliances:
                compliances_data.append({
                    'Compliance ID': compliance.ComplianceId,
                    'Description': compliance.ComplianceItemDescription or '',
                    'Status': compliance.Status or '',
                    'Criticality': compliance.Criticality or '',
                    'Maturity Level': compliance.MaturityLevel or '',
                    'Type': compliance.ComplianceType or '',
                    'Implementation': compliance.ManualAutomatic or '',
                    'Created By': compliance.CreatedByName or '',
                    'Created Date': compliance.CreatedByDate.strftime('%Y-%m-%d') if compliance.CreatedByDate else '',
                    'Version': compliance.ComplianceVersion or '',
                    'Identifier': compliance.Identifier or '',
                    'Active/Inactive': compliance.ActiveInactive or '',
                    'Is Risk': 'Yes' if compliance.IsRisk else 'No',
                    'SubPolicy': compliance.SubPolicy.SubPolicyName if compliance.SubPolicy else '',
                    'Policy': compliance.SubPolicy.Policy.PolicyName if compliance.SubPolicy and compliance.SubPolicy.Policy else '',
                    'Framework': compliance.SubPolicy.Policy.Framework.FrameworkName if compliance.SubPolicy and compliance.SubPolicy.Policy and compliance.SubPolicy.Policy.Framework else ''
                })
            
            # Use the export_data function from export_service
            from .export_service import export_data
            result = export_data(
                data=compliances_data,
                file_format=task.file_type,
                user_id=task.user_id,
                options={'item_type': item_type, 'item_id': item_id},
                export_id=task.id
            )
            
            # Task is already updated by export_data function
            # Just refresh the task to get updated values
            task.refresh_from_db()
            
            # Send notification
            try:
                from .notification_service import NotificationService
                notification_service = NotificationService()
                
                # Send notification directly with user_id
                notification_result = notification_service.send_export_completion_notification(
                    user_id=int(task.user_id),
                    export_details={
                        'id': task.id,
                        'file_name': task.file_name,
                        'file_type': task.file_type,
                        's3_url': task.s3_url,
                        'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else None
                    }
                )
                print(f"Export completion notification result: {notification_result}")
            except Exception as e:
                print(f"Error sending export completion notification: {str(e)}")
                # Continue even if notification fails
            
        except Exception as e:
            # Update task with error
            task.status = 'failed'
            task.error = str(e)
            task.save()
            raise
            
    except ExportTask.DoesNotExist:
        print(f"Export task {task_id} not found")
    except Exception as e:
        print(f"Error processing export task: {str(e)}")
        # Ensure task is marked as failed
        try:
            task = ExportTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error = str(e)
            task.save()
        except:
            pass

@api_view(['GET'])
def get_subpolicy_compliances(request, subpolicy_id):
    """Get all compliances for a specific subpolicy"""
    try:
        subpolicy = get_object_or_404(SubPolicy, id=subpolicy_id)
        compliances = Compliance.objects.filter(
            SubPolicy=subpolicy
        ).select_related('SubPolicy', 'SubPolicy__Policy', 'SubPolicy__Policy__Framework')
        
        compliances_data = []
        for compliance in compliances:
            compliances_data.append({
                'ComplianceId': compliance.id,
                'ComplianceItemDescription': compliance.description,
                'Status': compliance.status,
                'Criticality': compliance.criticality,
                'MaturityLevel': compliance.maturity_level,
                'MandatoryOptional': compliance.mandatory_optional,
                'ManualAutomatic': compliance.manual_automatic,
                'CreatedByName': compliance.created_by_name,
                'CreatedByDate': compliance.created_at.strftime('%Y-%m-%d') if compliance.created_at else None,
                'ComplianceVersion': compliance.version,
                'Identifier': compliance.identifier,
                'SubPolicyName': compliance.SubPolicy.name,
                'PolicyName': compliance.SubPolicy.Policy.name,
                'FrameworkName': compliance.SubPolicy.Policy.Framework.name
            })
        
        return Response({
            'success': True,
            'compliances': compliances_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def get_ontime_mitigation_percentage(request):
    try:
        # Get all risk instances that have been completed
        completed_risks = RiskInstance.objects.filter(
            MitigationStatus=RiskInstance.MITIGATION_COMPLETED,
            MitigationDueDate__isnull=False,
            MitigationCompletedDate__isnull=False
        )
        
        total_completed = completed_risks.count()
        if total_completed == 0:
            return Response({
                'success': True,
                'data': {
                    'on_time_percentage': 0,
                    'total_completed': 0,
                    'completed_on_time': 0,
                    'completed_late': 0
                }
            })
        
        # Count how many were completed on or before due date
        completed_on_time = completed_risks.filter(
            MitigationCompletedDate__lte=models.F('MitigationDueDate')
        ).count()
        
        # Calculate percentage
        on_time_percentage = (completed_on_time / total_completed) * 100
        completed_late = total_completed - completed_on_time
        
        return Response({
            'success': True,
            'data': {
                'on_time_percentage': round(on_time_percentage, 1),
                'total_completed': total_completed,
                'completed_on_time': completed_on_time,
                'completed_late': completed_late
            }
        })
        
    except Exception as e:
        print(f"Error in get_ontime_mitigation_percentage: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_compliance_status_overview(request):
    try:
        # Get all compliances
        compliances = Compliance.objects.all()
        
        # Get counts for different statuses
        status_counts = {
            'Approved': compliances.filter(Status='Approved').count(),
            'Under Review': compliances.filter(Status='Under Review').count(),
            'Active': compliances.filter(Status='Active').count(),
            'Rejected': compliances.filter(Status='Rejected').count()
        }
        
        # Calculate percentages
        total = sum(status_counts.values())
        status_percentages = {
            status: round((count / total * 100), 1) if total > 0 else 0
            for status, count in status_counts.items()
        }
        
        return Response({
            'success': True,
            'data': {
                'counts': status_counts,
                'percentages': status_percentages,
                'total': total
            }
        })
        
    except Exception as e:
        print(f"Error in get_compliance_status_overview: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_reputational_impact_assessment(request):
    try:
        import json
        from django.db import connection
        
        # Use raw SQL to avoid Django ORM timezone conversion issues
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT RiskFormDetails 
                FROM risk_instance 
                WHERE RiskFormDetails IS NOT NULL
            """)
            rows = cursor.fetchall()
        
        # Initialize counters for each impact level
        impact_counts = {
            'low': 0,
            'medium': 0,
            'high': 0
        }
        
        # Process each row to extract reputationalimpact values
        for row in rows:
            try:
                # Parse JSON if it's a string
                risk_details = row[0]
                if isinstance(risk_details, str):
                    risk_details = json.loads(risk_details)
                
                # Extract reputationalimpact value if exists
                if risk_details and 'reputationalimpact' in risk_details:
                    impact_level = risk_details['reputationalimpact'].lower()
                    if impact_level in impact_counts:
                        impact_counts[impact_level] += 1
            except Exception as e:
                print(f"Error processing risk details: {str(e)}")
                continue
        
        # Calculate total risks and percentages
        total_risks = sum(impact_counts.values())
        impact_percentages = {
            level: round((count / total_risks * 100), 2) if total_risks > 0 else 0
            for level, count in impact_counts.items()
        }
        
        return Response({
            'success': True,
            'data': {
                'impact_counts': impact_counts,
                'impact_percentages': impact_percentages,
                'total_risks': total_risks
            }
        })
        
    except Exception as e:
        print(f"Error in get_reputational_impact_assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_compliance_audit_info(request, compliance_id):
    """
    Get audit information for a specific compliance:
    1. Audit Performed By: UserId from lastchecklistitemverified
    2. Audit Approved By: UserId from audit_version
    3. Date of Audit Completion: Date from lastchecklistitemverified
    4. Audit Findings Status: Complied from lastchecklistitemverified
    """
    try:
        print(f"Fetching audit info for compliance ID: {compliance_id}")
        
        # First, get the LastChecklistItemVerified record for this compliance
        try:
            checklist_item = LastChecklistItemVerified.objects.filter(
                ComplianceId=compliance_id
            ).order_by('-Date', '-Time').first()
            
            if not checklist_item:
                print(f"No audit information found for compliance ID {compliance_id}")
                return Response({
                    'success': False,
                    'message': f'No audit information found for compliance ID {compliance_id}'
                }, status=404)
            
            print(f"Found checklist item: {checklist_item.id}, User: {checklist_item.User}, Date: {checklist_item.Date}")
                
            # Get audit findings record if it exists
            audit_findings_id = checklist_item.AuditFindingsId
            audit_approver = None
            
            if audit_findings_id:
                try:
                    print(f"Found audit findings ID: {audit_findings_id}")
                    # Get the audit findings
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT AuditId 
                            FROM audit_findings 
                            WHERE AuditFindingsId = %s
                        """, [audit_findings_id])
                        result = cursor.fetchone()
                        
                        if result:
                            audit_id = result[0]
                            print(f"Found audit ID: {audit_id}")
                            
                            # Get the audit version record for this audit
                            cursor.execute("""
                                SELECT ApproverId
                                FROM audit_versions
                                WHERE AuditId = %s
                                ORDER BY Date DESC
                                LIMIT 1
                            """, [audit_id])
                            approver_result = cursor.fetchone()
                            
                            if approver_result:
                                audit_approver = approver_result[0]
                                print(f"Found audit approver: {audit_approver}")
                except Exception as e:
                    print(f"Error getting audit approver: {str(e)}")
                    # Continue without audit approver
            
            # Get user names if possible
            performer_name = None
            approver_name = None
            
            try:
                with connection.cursor() as cursor:
                    if checklist_item.User:
                        cursor.execute("""
                            SELECT UserName FROM users WHERE UserId = %s
                        """, [checklist_item.User])
                        user_result = cursor.fetchone()
                        if user_result:
                            performer_name = user_result[0]
                            print(f"Found performer name: {performer_name}")
                    
                    if audit_approver:
                        cursor.execute("""
                            SELECT UserName FROM users WHERE UserId = %s
                        """, [audit_approver])
                        approver_result = cursor.fetchone()
                        if approver_result:
                            approver_name = approver_result[0]
                            print(f"Found approver name: {approver_name}")
            except Exception as e:
                print(f"Error getting user names: {str(e)}")
                # Continue without user names
            
            # Map compliance status
            compliance_status_map = {
                '0': 'Non Compliant',
                '1': 'Partially Compliant',
                '2': 'Fully Compliant',
                '3': 'Not Applicable'
            }
            
            compliance_status = compliance_status_map.get(checklist_item.Complied, 'Unknown')
            print(f"Compliance status: {compliance_status} (from value: {checklist_item.Complied})")
            
            # Build response data
            response_data = {
                'audit_performer_id': checklist_item.User,
                'audit_performer_name': performer_name,
                'audit_approver_id': audit_approver,
                'audit_approver_name': approver_name,
                'audit_date': checklist_item.Date.strftime('%Y-%m-%d') if checklist_item.Date else None,
                'audit_time': checklist_item.Time.strftime('%H:%M:%S') if checklist_item.Time else None,
                'audit_findings_status': compliance_status,
                'audit_findings_id': audit_findings_id,
                'comments': checklist_item.Comments
            }
            
            print(f"Returning audit data: {response_data}")
            
            # Return the audit information
            return Response({
                'success': True,
                'data': response_data
            })
            
        except LastChecklistItemVerified.DoesNotExist:
            print(f"LastChecklistItemVerified.DoesNotExist for compliance ID {compliance_id}")
            return Response({
                'success': False,
                'message': f'No audit information found for compliance ID {compliance_id}'
            }, status=404)
            
    except Exception as e:
        print(f"Error in get_compliance_audit_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_compliance_details(request, compliance_id):
    """
    Get detailed information for a specific compliance by ID.
    This endpoint returns all fields of the compliance model.
    """
    try:
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Prepare the detailed response with all available fields
        response_data = {
            'ComplianceId': compliance.ComplianceId,
            'ComplianceTitle': compliance.ComplianceTitle,
            'ComplianceItemDescription': compliance.ComplianceItemDescription,
            'ComplianceType': compliance.ComplianceType,
            'Scope': compliance.Scope,
            'Objective': compliance.Objective,
            'BusinessUnitsCovered': compliance.BusinessUnitsCovered,
            'IsRisk': compliance.IsRisk,
            'PossibleDamage': compliance.PossibleDamage,
            'mitigation': compliance.mitigation,
            'Criticality': compliance.Criticality,
            'MandatoryOptional': compliance.MandatoryOptional,
            'ManualAutomatic': compliance.ManualAutomatic,
            'Impact': compliance.Impact,
            'Probability': compliance.Probability,
            'MaturityLevel': compliance.MaturityLevel,
            'ActiveInactive': compliance.ActiveInactive,
            'PermanentTemporary': compliance.PermanentTemporary,
            'Status': compliance.Status,
            'ComplianceVersion': compliance.ComplianceVersion,
            'Identifier': compliance.Identifier,
            'Applicability': compliance.Applicability,
            'CreatedByName': compliance.CreatedByName,
            'CreatedByDate': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
            'SubPolicy': compliance.SubPolicy_id,
            'PotentialRiskScenarios': compliance.PotentialRiskScenarios,
            'RiskType': compliance.RiskType,
            'RiskCategory': compliance.RiskCategory,
            'RiskBusinessImpact': compliance.RiskBusinessImpact
        }
        
        # Add the subpolicy and policy names
        try:
            response_data['SubPolicyName'] = compliance.SubPolicy.SubPolicyName
            response_data['PolicyName'] = compliance.SubPolicy.Policy.PolicyName
        except Exception as e:
            print(f"Error getting related names: {str(e)}")
            # Continue without related names
            
        return Response({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        print(f"Error in get_compliance_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def get_remediation_cost_kpi(request):
    try:
        import json
        from django.db import connection
        from datetime import datetime, timedelta
        
        # Use raw SQL to get all risk instances with RiskFormDetails
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT RiskFormDetails, Date
                FROM risk_instance 
                WHERE RiskFormDetails IS NOT NULL
                ORDER BY Date
            """)
            rows = cursor.fetchall()
        
        # Initialize data structure
        cost_data = {
            'total_cost': 0,
            'average_cost': 0,
            'cost_by_category': {},
            'cost_by_month': {},
            'count': 0
        }
        
        # Process each row to extract cost values
        for row in rows:
            try:
                # Parse JSON if it's a string
                risk_details = row[0]
                risk_date = row[1]
                
                if isinstance(risk_details, str):
                    risk_details = json.loads(risk_details)
                
                # Extract cost value if exists
                if risk_details and 'cost' in risk_details:
                    try:
                        cost_value = float(risk_details['cost'])
                        cost_data['total_cost'] += cost_value
                        cost_data['count'] += 1
                        
                        # Add to category if exists
                        if 'category' in risk_details:
                            category = risk_details['category']
                            if category not in cost_data['cost_by_category']:
                                cost_data['cost_by_category'][category] = 0
                            cost_data['cost_by_category'][category] += cost_value
                        
                        # Format date to month-year
                        if risk_date:
                            if isinstance(risk_date, str):
                                date_obj = datetime.strptime(risk_date.split(' ')[0], '%Y-%m-%d')
                            else:
                                date_obj = risk_date
                                
                            month_year = date_obj.strftime('%b %Y')
                            if month_year not in cost_data['cost_by_month']:
                                cost_data['cost_by_month'][month_year] = 0
                            cost_data['cost_by_month'][month_year] += cost_value
                    except (ValueError, TypeError):
                        # Skip if cost is not a valid number
                        continue
            except Exception as e:
                print(f"Error processing risk details: {str(e)}")
                continue
        
        # Calculate average cost
        if cost_data['count'] > 0:
            cost_data['average_cost'] = round(cost_data['total_cost'] / cost_data['count'], 2)
        
        # Sort month-year data chronologically
        sorted_months = {}
        month_entries = sorted([(datetime.strptime(k, '%b %Y'), k, v) for k, v in cost_data['cost_by_month'].items()])
        for _, month_str, value in month_entries:
            sorted_months[month_str] = value
        
        cost_data['cost_by_month'] = sorted_months
        
        # Format for chart display
        chart_data = {
            'labels': list(sorted_months.keys()),
            'values': list(sorted_months.values())
        }
        
        # Get top categories by cost
        top_categories = sorted(cost_data['cost_by_category'].items(), key=lambda x: x[1], reverse=True)
        category_chart = {
            'labels': [cat for cat, _ in top_categories[:5]],  # Top 5 categories
            'values': [val for _, val in top_categories[:5]]
        }
        
        return Response({
            'success': True,
            'data': {
                'cost_summary': cost_data,
                'time_series_chart': chart_data,
                'category_chart': category_chart
            }
        })
        
    except Exception as e:
        print(f"Error in get_remediation_cost_kpi: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_non_compliant_incidents_by_time(request):
    try:
        # Get time period filter from request
        time_period = request.query_params.get('period', 'month')  # Default to last month
        print(f"Received request for non-compliant incidents with period: {time_period}")
        
        # Current date for calculations
        current_date = timezone.now().date()
        
        # Calculate date ranges based on period filter
        if time_period == 'week':
            # Last 7 days
            start_date = current_date - timedelta(days=7)
            period_name = 'Last 7 Days'
        elif time_period == 'month':
            # Last 30 days
            start_date = current_date - timedelta(days=30)
            period_name = 'Last 30 Days'
        elif time_period == 'quarter':
            # Last 90 days
            start_date = current_date - timedelta(days=90)
            period_name = 'Last 3 Months'
        elif time_period == 'year':
            # Last 365 days
            start_date = current_date - timedelta(days=365)
            period_name = 'Last 12 Months'
        else:
            # Invalid period, default to month
            print(f"Invalid time period: {time_period}, defaulting to month")
            start_date = current_date - timedelta(days=30)
            period_name = 'Last 30 Days'
            time_period = 'month'
            
        print(f"Using period: {period_name}, start_date: {start_date}, end_date: {current_date}")
            
        # Query non-compliant records within the date range
        # Non-compliant is where Complied = '0'
        non_compliant_records = LastChecklistItemVerified.objects.filter(
            Date__gte=start_date,
            Date__lte=current_date,
            Complied='0'
        )
        
        print(f"Found {non_compliant_records.count()} non-compliant records")
        
        # Get the count
        non_compliant_count = non_compliant_records.count()
        
        # Get compliance item details grouped by item (ComplianceId)
        non_compliant_items = {}
        compliance_ids = set()
        
        for record in non_compliant_records:
            compliance_id = record.ComplianceId
            compliance_ids.add(compliance_id)
            
            if compliance_id not in non_compliant_items:
                non_compliant_items[compliance_id] = {
                    'count': 0,
                    'compliance_id': compliance_id,
                    'last_date': None,
                    'comments': []
                }
                
            non_compliant_items[compliance_id]['count'] += 1
            
            # Track most recent date
            record_date = record.Date
            if not non_compliant_items[compliance_id]['last_date'] or record_date > non_compliant_items[compliance_id]['last_date']:
                non_compliant_items[compliance_id]['last_date'] = record_date
                
            # Store comments (limit to avoid excessive data)
            if record.Comments and len(non_compliant_items[compliance_id]['comments']) < 5:
                non_compliant_items[compliance_id]['comments'].append(record.Comments)
        
        # Convert to list and sort by count
        non_compliant_list = sorted(
            list(non_compliant_items.values()),
            key=lambda x: x['count'],
            reverse=True
        )
        
        # Get compliance item details for top 10 items
        top_items_with_details = []
        for item in non_compliant_list[:10]:  # Limit to top 10
            try:
                compliance = Compliance.objects.get(ComplianceId=item['compliance_id'])
                item_details = {
                    'compliance_id': item['compliance_id'],
                    'count': item['count'],
                    'last_date': item['last_date'].isoformat() if item['last_date'] else None,
                    'comments': item['comments'],
                    'description': compliance.ComplianceItemDescription,
                    'criticality': compliance.Criticality,
                    'maturity_level': compliance.MaturityLevel
                }
                top_items_with_details.append(item_details)
            except Compliance.DoesNotExist:
                # Just add the basic item without compliance details
                item_details = {
                    'compliance_id': item['compliance_id'],
                    'count': item['count'],
                    'last_date': item['last_date'].isoformat() if item['last_date'] else None,
                    'comments': item['comments'],
                    'description': 'Unknown Compliance Item',
                    'criticality': 'Unknown',
                    'maturity_level': 'Unknown'
                }
                top_items_with_details.append(item_details)
        
        # Get trend data by grouping counts by day or week depending on period
        trend_data = {}
        if time_period in ['week', 'month']:
            # Group by day
            for record in non_compliant_records:
                day_key = record.Date.isoformat()
                if day_key not in trend_data:
                    trend_data[day_key] = 0
                trend_data[day_key] += 1
        else:
            # Group by week
            for record in non_compliant_records:
                # Get the week start date (Monday)
                week_start = record.Date - timedelta(days=record.Date.weekday())
                week_key = week_start.isoformat()
                if week_key not in trend_data:
                    trend_data[week_key] = 0
                trend_data[week_key] += 1
        
        # Sort the trend data by date
        sorted_trend = sorted(trend_data.items())
        
        # Format for chart display
        chart_data = {
            'labels': [item[0] for item in sorted_trend],
            'values': [item[1] for item in sorted_trend]
        }
        
        # Calculate percentage change from previous period
        previous_start_date = start_date - (current_date - start_date)
        previous_count = LastChecklistItemVerified.objects.filter(
            Date__gte=previous_start_date,
            Date__lt=start_date,
            Complied='0'
        ).count()
        
        if previous_count > 0:
            percentage_change = ((non_compliant_count - previous_count) / previous_count) * 100
        else:
            percentage_change = 100 if non_compliant_count > 0 else 0
        
        # Format percentage with proper sign
        percentage_formatted = f"{'+' if percentage_change > 0 else ''}{percentage_change:.1f}%"
        
        print(f"Sending response with non_compliant_count: {non_compliant_count}, unique_items: {len(compliance_ids)}")
        
        response_data = {
            'success': True,
            'data': {
                'non_compliant_count': non_compliant_count,
                'period': period_name,
                'start_date': start_date.isoformat(),
                'end_date': current_date.isoformat(),
                'percentage_change': percentage_formatted,
                'previous_period_count': previous_count,
                'top_non_compliant_items': top_items_with_details,
                'trend_data': chart_data,
                'unique_compliance_items': len(compliance_ids)
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in get_non_compliant_incidents_by_time: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_notification(request):
    """Test endpoint to check if notifications are working"""
    try:
        from .notification_service import NotificationService
        from .models import Notification
        
        notification_service = NotificationService()
        
        # Test parameters
        test_email = request.query_params.get('email', 'test@example.com')
        notification_type = request.query_params.get('type', 'all')
        
        results = {}
        
        # Test compliance creation notification
        if notification_type in ['all', 'creation']:
            creation_data = {
                'notification_type': 'compliance_creation',
                'email': test_email,
                'email_type': 'gmail',
                'template_data': [
                    'Test Reviewer',
                    '12345',
                    'This is a test compliance description',
                    '1.0',
                    'Test Creator',
                    '2023-06-10'
                ]
            }
            results['creation'] = notification_service.send_multi_channel_notification(creation_data)
            
        # Test compliance edit notification
        if notification_type in ['all', 'edit']:
            edit_data = {
                'notification_type': 'compliance_edit',
                'email': test_email,
                'email_type': 'gmail',
                'template_data': [
                    'Test Reviewer',
                    '12345',
                    'Updated compliance description',
                    '1.1',
                    '1.0',
                    'Test Editor',
                    '2023-06-12'
                ]
            }
            results['edit'] = notification_service.send_multi_channel_notification(edit_data)
            
        # Test compliance approval notification
        if notification_type in ['all', 'approval']:
            approval_data = {
                'notification_type': 'compliance_review',
                'email': test_email,
                'email_type': 'gmail',
                'template_data': [
                    'Test Creator',
                    '12345',
                    'Approved compliance description',
                    '1.0',
                    'approved',
                    'This compliance looks good!'
                ]
            }
            results['approval'] = notification_service.send_multi_channel_notification(approval_data)
            
        # Test compliance rejection notification
        if notification_type in ['all', 'rejection']:
            rejection_data = {
                'notification_type': 'compliance_review',
                'email': test_email,
                'email_type': 'gmail',
                'template_data': [
                    'Test Creator',
                    '12345',
                    'Rejected compliance description',
                    '1.0',
                    'rejected',
                    'This compliance needs more work.'
                ]
            }
            results['rejection'] = notification_service.send_multi_channel_notification(rejection_data)
            
        # Test version toggle notification
        if notification_type in ['all', 'toggle']:
            toggle_data = {
                'notification_type': 'policyStatusChange',
                'email': test_email,
                'email_type': 'gmail',
                'template_data': [
                    'Test User',
                    'Compliance COMP-12345 v1.0',
                    'Activated',
                    'Administrator',
                    '2023-06-15'
                ]
            }
            results['toggle'] = notification_service.send_multi_channel_notification(toggle_data)
        
        # Check if notifications were logged in the database
        recent_notifications = Notification.objects.filter(recipient=test_email).order_by('-created_at')[:10]
        notification_records = [{
            'id': n.id,
            'type': n.type,
            'channel': n.channel,
            'success': n.success,
            'created_at': n.created_at.isoformat() if n.created_at else None
        } for n in recent_notifications]
        
        return Response({
            'success': True,
            'message': 'Test notifications sent',
            'email': test_email,
            'results': results,
            'notification_records': notification_records,
            'db_record_count': recent_notifications.count()
        })
    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'message': f'Error testing notification: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)

@api_view(['GET'])
def get_compliance_framework_info(request, compliance_id):
    """
    Get framework information for a compliance item to restrict copying within the same framework
    """
    try:
        # Get the source compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Get the framework information
        try:
            subpolicy = SubPolicy.objects.get(SubPolicyId=compliance.SubPolicy_id)
            policy = subpolicy.Policy
            framework = policy.Framework
            
            return Response({
                'success': True,
                'data': {
                    'compliance_id': compliance.ComplianceId,
                    'framework_id': framework.FrameworkId,
                    'framework_name': framework.FrameworkName,
                    'policy_id': policy.PolicyId,
                    'policy_name': policy.PolicyName,
                    'subpolicy_id': subpolicy.SubPolicyId,
                    'subpolicy_name': subpolicy.SubPolicyName
                }
            })
        except Exception as e:
            print(f"Error getting framework info: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error retrieving framework information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Compliance.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Compliance not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_values(request, source):
    """
    Get all values for a specific category source from CategoryBusinessUnit table
    """
    try:
        from .models import CategoryBusinessUnit
        
        # Validate source parameter
        allowed_sources = ['BusinessUnitsCovered', 'RiskType', 'RiskCategory', 'RiskBusinessImpact']
        if source not in allowed_sources:
            return Response({
                'success': False,
                'message': f'Invalid source. Allowed sources: {", ".join(allowed_sources)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get values for the specified source
        categories = CategoryBusinessUnit.objects.filter(source=source).values_list('value', flat=True).distinct().order_by('value')
        
        return Response({
            'success': True,
            'data': list(categories)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching category values: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_http_methods(["POST"])
@csrf_exempt
def add_category_value(request):
    """
    Add a new value to CategoryBusinessUnit table
    """
    try:
        from .models import CategoryBusinessUnit
        
        # Parse JSON data from request body
        try:
            data = json.loads(request.body.decode('utf-8'))
            source = data.get('source')
            value = data.get('value')
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        
        # Validate required fields
        if not source or not value:
            return JsonResponse({
                'success': False,
                'message': 'Both source and value are required'
            }, status=400)
        
        # Validate source parameter
        allowed_sources = ['BusinessUnitsCovered', 'RiskType', 'RiskCategory', 'RiskBusinessImpact']
        if source not in allowed_sources:
            return JsonResponse({
                'success': False,
                'message': f'Invalid source. Allowed sources: {", ".join(allowed_sources)}'
            }, status=400)
        
        # Check if the value already exists for this source
        existing = CategoryBusinessUnit.objects.filter(source=source, value=value).first()
        if existing:
            return JsonResponse({
                'success': True,
                'message': 'Value already exists',
                'data': {'id': existing.id, 'source': existing.source, 'value': existing.value}
            })
        
        # Create new category entry
        new_category = CategoryBusinessUnit.objects.create(
            source=source,
            value=value.strip()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Category value added successfully',
            'data': {'id': new_category.id, 'source': new_category.source, 'value': new_category.value}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding category value: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def initialize_default_categories(request):
    print("Initializing default categories")
    try:
        from .models import CategoryBusinessUnit

        # Log incoming request data
        print(f"Request Data: {request.data}")

        # Default values for each source
        default_values = {
            'BusinessUnitsCovered': [
                'Sales & Marketing',
                'Finance & Accounting',
                'Human Resources',
                'Information Technology',
                'Operations',
                'Legal & Compliance',
                'Customer Service',
                'Research & Development',
                'Procurement',
                'Risk Management'
            ],
            'RiskType': [
                'Operational Risk',
                'Financial Risk',
                'Strategic Risk',
                'Compliance Risk',
                'Reputational Risk',
                'Technology Risk',
                'Market Risk',
                'Credit Risk',
                'Legal Risk',
                'Environmental Risk'
            ],
            'RiskCategory': [
                'People Risk',
                'Process Risk',
                'Technology Risk',
                'External Risk',
                'Information Risk',
                'Physical Risk',
                'Systems Risk',
                'Vendor Risk',
                'Regulatory Risk',
                'Fraud Risk'
            ],
            'RiskBusinessImpact': [
                'Revenue Loss',
                'Customer Impact',
                'Operational Disruption',
                'Brand Damage',
                'Regulatory Penalties',
                'Legal Costs',
                'Data Loss',
                'Service Downtime',
                'Productivity Loss',
                'Compliance Violations'
            ]
        }

        added_count = 0
        for source, values in default_values.items():
            for value in values:
                # Check if the value already exists
                existing = CategoryBusinessUnit.objects.filter(source=source, value=value).first()
                if not existing:
                    CategoryBusinessUnit.objects.create(source=source, value=value)
                    added_count += 1

        return Response({
            'success': True,
            'message': f'Default categories initialized. Added {added_count} new values.',
            'added_count': added_count
        })

    except Exception as e:
        # Log the error and the exception message
        print(f"Error initializing default categories: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error initializing default categories: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_business_units(request):
    """
    API endpoint to get CategoryBusinessUnit values by source
    """
    try:
        from .models import CategoryBusinessUnit
        
        source = request.query_params.get('source')
        if not source:
            return Response({"error": "Source parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        units = CategoryBusinessUnit.objects.filter(source=source)
        units_data = [{"id": unit.id, "value": unit.value} for unit in units]
        
        return Response({
            "success": True,
            "data": units_data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_category_business_unit(request):
    """
    API endpoint to add a new CategoryBusinessUnit
    """
    try:
        from .models import CategoryBusinessUnit
        
        data = request.data
        source = data.get('source')
        value = data.get('value')
        
        if not source or not value:
            return Response({"error": "Both source and value are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the value already exists for this source
        if CategoryBusinessUnit.objects.filter(source=source, value=value).exists():
            return Response({"error": f"Value '{value}' already exists for source '{source}'"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new record
        new_unit = CategoryBusinessUnit.objects.create(source=source, value=value)
        
        return Response({
            "success": True,
            "data": {
                "id": new_unit.id,
                "source": new_unit.source,
                "value": new_unit.value
            }
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def edit_compliance(request, compliance_id):
    """
    Edit an existing compliance item
    """
    try:
        # Get the compliance item
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Get version type from request data
        version_type = request.data.get('versionType')
        if version_type not in ['Major', 'Minor']:
            return Response({
                'success': False,
                'message': 'Invalid version type. Must be either Major or Minor'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse current version
        try:
            major, minor = compliance.ComplianceVersion.split('.')
            current_major = int(major)
            current_minor = int(minor)
        except (ValueError, AttributeError):
            # If version is not in correct format, start with 1.0
            current_major = 1
            current_minor = 0

        # Calculate new version based on version type
        if version_type == 'Major':
            new_version = f"{current_major + 1}.0"
        else:  # Minor version
            new_version = f"{current_major}.{current_minor + 1}"

        # Get the policy through the subpolicy relationship
        policy = compliance.SubPolicy.PolicyId

        # Create a new compliance instance with updated data
        new_compliance = Compliance.objects.create(
            SubPolicy=compliance.SubPolicy,  # Use the ForeignKey field directly
            ComplianceTitle=request.data.get('ComplianceTitle', ''),
            ComplianceItemDescription=request.data.get('ComplianceItemDescription', ''),
            ComplianceType=request.data.get('ComplianceType', ''),
            Scope=request.data.get('Scope', ''),
            Objective=request.data.get('Objective', ''),
            BusinessUnitsCovered=request.data.get('BusinessUnitsCovered', ''),
            IsRisk=request.data.get('IsRisk', False),
            PossibleDamage=request.data.get('PossibleDamage', ''),
            mitigation=request.data.get('mitigation', {}),
            PotentialRiskScenarios=request.data.get('PotentialRiskScenarios', ''),
            RiskType=request.data.get('RiskType', ''),
            RiskCategory=request.data.get('RiskCategory', ''),
            RiskBusinessImpact=request.data.get('RiskBusinessImpact', ''),
            Criticality=request.data.get('Criticality', 'Medium'),
            MandatoryOptional=request.data.get('MandatoryOptional', 'Mandatory'),
            ManualAutomatic=request.data.get('ManualAutomatic', 'Manual'),
            Impact=request.data.get('Impact', '5.0'),
            Probability=request.data.get('Probability', '5.0'),
            Status='Under Review',
            ComplianceVersion=new_version,
            Applicability=request.data.get('Applicability', ''),
            MaturityLevel=request.data.get('MaturityLevel', 'Initial'),
            ActiveInactive='Active',
            PermanentTemporary=request.data.get('PermanentTemporary', 'Permanent'),
            CreatedByName=request.data.get('CreatedByName', ''),
            CreatedByDate=datetime.date.today(),
            Identifier=compliance.Identifier  # Preserve the original identifier
        )

        # Create extracted data for PolicyApproval
        extracted_data = {
            'type': 'compliance',
            'compliance_id': new_compliance.ComplianceId,  # Use compliance_id instead of ComplianceId
            'ComplianceTitle': new_compliance.ComplianceTitle,
            'ComplianceItemDescription': new_compliance.ComplianceItemDescription,
            'ComplianceType': new_compliance.ComplianceType,
            'Scope': new_compliance.Scope,
            'Objective': new_compliance.Objective,
            'BusinessUnitsCovered': new_compliance.BusinessUnitsCovered,
            'IsRisk': new_compliance.IsRisk,
            'PossibleDamage': new_compliance.PossibleDamage,
            'mitigation': new_compliance.mitigation,
            'Criticality': new_compliance.Criticality,
            'Status': new_compliance.Status,
            'version_type': version_type,
            'Identifier': new_compliance.Identifier
        }

        # Create PolicyApproval for the new version
        policy_approval = PolicyApproval.objects.create(
            Identifier=new_compliance.Identifier,
            ExtractedData=extracted_data,
            UserId=request.data.get('UserId', 1),  # Default to 1 if not provided
            ReviewerId=request.data.get('ReviewerId', 2),  # Default to 2 if not provided
            Version=f"u{new_version}",  # Use u prefix for user version
            ApprovedNot=None,  # Set to None for pending approval
            ApprovalDueDate=datetime.date.today() + datetime.timedelta(days=7),  # Due in 7 days
            PolicyId=policy  # Set the policy relationship correctly
        )

        return Response({
            'success': True,
            'message': 'Compliance updated successfully',
            'data': {
                'ComplianceId': new_compliance.ComplianceId,
                'Version': new_version,
                'Status': new_compliance.Status,
                'ApprovalId': policy_approval.ApprovalId
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update compliance: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def clone_compliance(request, compliance_id):
    """
    Clone an existing compliance item
    """
    try:
        print(f"\n=== CLONE_COMPLIANCE DEBUG ===")
        print(f"Cloning compliance ID: {compliance_id}")
        print(f"Request data: {request.data}")
        
        # Get the source compliance
        source_compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        print(f"Found source compliance: {source_compliance.ComplianceId}, {source_compliance.ComplianceTitle}")
        
        # Get data from request
        data = request.data.copy()
        
        # Get target subpolicy ID from request data
        target_subpolicy_id = data.get('target_subpolicy_id') or data.get('SubPolicy')
        if not target_subpolicy_id:
            print(f"ERROR: No target subpolicy ID provided in request")
            return Response({
                'success': False,
                'message': 'Target SubPolicy ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        print(f"Target SubPolicy ID: {target_subpolicy_id}")
        
        # Verify target subpolicy exists
        try:
            target_subpolicy = SubPolicy.objects.get(SubPolicyId=target_subpolicy_id)
            print(f"Found target subpolicy: {target_subpolicy.SubPolicyId}, {target_subpolicy.SubPolicyName}")
        except SubPolicy.DoesNotExist:
            print(f"ERROR: Target SubPolicy {target_subpolicy_id} not found")
            return Response({
                'success': False,
                'message': f'Target SubPolicy with ID {target_subpolicy_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Set default values if not provided
        data.setdefault('Status', 'Under Review')
        data.setdefault('ActiveInactive', 'Active')
        data.setdefault('CreatedByDate', datetime.date.today())
        data.setdefault('ComplianceVersion', '1.0')
        
        # Get ComplianceTitle from request or use source compliance title
        compliance_title = data.get('ComplianceTitle', source_compliance.ComplianceTitle)
        print(f"Using compliance title: {compliance_title}")
        
        # Process mitigation data to ensure it's in JSON format
        mitigation_data = data.get('mitigation', source_compliance.mitigation)
        formatted_mitigation = {}
        
        # If mitigation is already a dict, use it
        if isinstance(mitigation_data, dict):
            formatted_mitigation = mitigation_data
            print(f"Mitigation is already a dict: {formatted_mitigation}")
        # If it's a string, try to parse as JSON
        elif isinstance(mitigation_data, str) and mitigation_data.strip():
            try:
                # Try to parse as JSON
                if mitigation_data.strip().startswith('{'):
                    formatted_mitigation = json.loads(mitigation_data)
                    print(f"Parsed mitigation from JSON string: {formatted_mitigation}")
                else:
                    # Not JSON, use as single entry
                    formatted_mitigation = {"1": mitigation_data}
                    print(f"Created numbered mitigation from string: {formatted_mitigation}")
            except json.JSONDecodeError:
                # Not valid JSON, use as single entry
                formatted_mitigation = {"1": mitigation_data}
                print(f"Created numbered mitigation from invalid JSON: {formatted_mitigation}")
        else:
            # Default empty object
            formatted_mitigation = {}
            print("Using empty mitigation object")
        
        # Ensure mitigation is serialized as JSON string for storage
        mitigation_json = json.dumps(formatted_mitigation)
        print(f"Final mitigation JSON: {mitigation_json}")
        
        # Create new compliance instance
        new_compliance = Compliance.objects.create(
            SubPolicy_id=target_subpolicy_id,  # Use target subpolicy ID from request
            ComplianceTitle=compliance_title,
            ComplianceItemDescription=data.get('ComplianceItemDescription', source_compliance.ComplianceItemDescription),
            ComplianceType=data.get('ComplianceType', source_compliance.ComplianceType),
            Scope=data.get('Scope', source_compliance.Scope),
            Objective=data.get('Objective', source_compliance.Objective),
            BusinessUnitsCovered=data.get('BusinessUnitsCovered', source_compliance.BusinessUnitsCovered),
            IsRisk=data.get('IsRisk', source_compliance.IsRisk),
            PossibleDamage=data.get('PossibleDamage', source_compliance.PossibleDamage),
            mitigation=mitigation_json,  # Use the JSON string
            PotentialRiskScenarios=data.get('PotentialRiskScenarios', source_compliance.PotentialRiskScenarios),
            RiskType=data.get('RiskType', source_compliance.RiskType),
            RiskCategory=data.get('RiskCategory', source_compliance.RiskCategory),
            RiskBusinessImpact=data.get('RiskBusinessImpact', source_compliance.RiskBusinessImpact),
            Criticality=data.get('Criticality', source_compliance.Criticality),
            MandatoryOptional=data.get('MandatoryOptional', source_compliance.MandatoryOptional),
            ManualAutomatic=data.get('ManualAutomatic', source_compliance.ManualAutomatic),
            Impact=data.get('Impact', source_compliance.Impact),
            Probability=data.get('Probability', source_compliance.Probability),
            Status='Under Review',
            ActiveInactive='Active',
            PermanentTemporary=data.get('PermanentTemporary', source_compliance.PermanentTemporary),
            CreatedByDate=datetime.date.today(),
            ComplianceVersion='1.0',
            MaturityLevel=data.get('MaturityLevel', source_compliance.MaturityLevel),
            CreatedByName=data.get('CreatedByName', source_compliance.CreatedByName),
            Applicability=data.get('Applicability', source_compliance.Applicability)
        )
        
        print(f"Created new compliance with ID: {new_compliance.ComplianceId}")
        
        # Generate a new identifier
        identifier = f"COMP-{target_subpolicy_id}-{datetime.date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"
        new_compliance.Identifier = identifier
        new_compliance.save()
        print(f"Generated identifier: {identifier}")
        
        # Get reviewer ID from request
        reviewer_id = data.get('reviewer_id') or data.get('reviewer', 1)  # Default to 1 if not provided
        print(f"Using reviewer ID: {reviewer_id}")
        
        # Get the policy through the subpolicy relationship
        policy = target_subpolicy.PolicyId
        print(f"Using policy ID: {policy.PolicyId}")
        
        # Set approval due date
        approval_due_date = data.get('ApprovalDueDate', (datetime.date.today() + datetime.timedelta(days=7)).isoformat())
        print(f"Using approval due date: {approval_due_date}")
        
        # Create extracted data for PolicyApproval
        extracted_data = {
            'type': 'compliance',
            'ComplianceTitle': new_compliance.ComplianceTitle,
            'ComplianceItemDescription': new_compliance.ComplianceItemDescription,
            'Criticality': new_compliance.Criticality,
            'Impact': new_compliance.Impact,
            'Probability': new_compliance.Probability,
            'mitigation': formatted_mitigation,  # Use the formatted mitigation object (not the JSON string)
            'PossibleDamage': new_compliance.PossibleDamage,
            'IsRisk': new_compliance.IsRisk,
            'MandatoryOptional': new_compliance.MandatoryOptional,
            'ManualAutomatic': new_compliance.ManualAutomatic,
            'CreatedByName': new_compliance.CreatedByName,
            'CreatedByDate': new_compliance.CreatedByDate.isoformat(),
            'Status': new_compliance.Status,
            'ComplianceId': new_compliance.ComplianceId,
            'ComplianceVersion': new_compliance.ComplianceVersion,
            'SubPolicy': target_subpolicy_id,
            'compliance_approval': {
                'approved': None,
                'remarks': '',
                'ApprovalDueDate': approval_due_date
            }
        }
        
        # Create PolicyApproval entry
        policy_approval = PolicyApproval.objects.create(
            PolicyId=policy,
            Identifier=identifier,
            ExtractedData=extracted_data,
            UserId=data.get('UserId', 1),  # Default to 1 if not provided
            ReviewerId=reviewer_id,
            Version='u1',
            ApprovedNot=None,  # Not yet approved
            ApprovalDueDate=approval_due_date
        )
        
        print(f"Created policy approval with ID: {policy_approval.ApprovalId}")
        
        # Send notification to reviewer
        try:
            print("=== NOTIFICATION DEBUGGING - COMPLIANCE CLONE ===")
            from .notification_service import NotificationService
            notification_service = NotificationService()
            
            # Make sure reviewer has a valid email
            try:
                reviewer = Users.objects.get(UserId=reviewer_id)
                if not reviewer.Email or '@' not in reviewer.Email:
                    reviewer.Email = f"reviewer{reviewer_id}@example.com"
                    reviewer.save()
                    print(f"Updated reviewer {reviewer_id} with email {reviewer.Email}")
                
                print(f"Found reviewer: {reviewer.UserName} with email: {reviewer.Email}")
            except Users.DoesNotExist:
                print(f"ERROR: Reviewer with ID {reviewer_id} does not exist")
            
            # Send notification
            print(f"Sending clone notification for compliance {new_compliance.ComplianceId} to reviewer {reviewer_id}")
            notification_result = notification_service.send_compliance_clone_notification(
                compliance=new_compliance,
                reviewer_id=reviewer_id
            )
            
            if notification_result.get('success'):
                print(f"Successfully sent compliance clone notification to reviewer {reviewer_id}")
            else:
                print(f"Failed to send notification: {notification_result.get('error', 'Unknown error')}")
                print(f"Error details: {notification_result.get('errors', [])}") 
            
            # Log the notification directly in the database
            from .models import Notification
            try:
                reviewer_email, reviewer_name = notification_service.get_user_email_by_id(reviewer_id)
                if reviewer_email:
                    Notification.objects.create(
                        recipient=reviewer_email,
                        type='compliance_clone',
                        channel='email',
                        success=notification_result.get('success', False)
                    )
                    print(f"Created clone notification record for {reviewer_email}")
            except Exception as db_error:
                print(f"ERROR creating notification record: {str(db_error)}")
                
            print("=== END NOTIFICATION DEBUGGING ===")
        except Exception as e:
            print(f"Error sending compliance clone notification: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Continue even if notification fails
        
        print("=== END CLONE_COMPLIANCE DEBUG ===\n")
        return Response({
            'success': True,
            'message': 'Compliance cloned successfully and sent for review',
            'compliance_id': new_compliance.ComplianceId,
            'Identifier': identifier,
            'version': new_compliance.ComplianceVersion,
            'reviewer_id': reviewer_id
        }, status=status.HTTP_201_CREATED)
        
    except Compliance.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Source compliance not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in clone_compliance: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# for temporary use

@api_view(['GET'])
def get_compliances_by_type(request, type, id):
    print(f"\n=== GET_COMPLIANCES_BY_TYPE DEBUG ===")
    print(f"Received type: '{type}', id: {id} (type: {type(id)})")
    
    try:
        compliances = None
        
        if type == 'framework':
            print(f"Getting compliances for framework {id}")
            compliances = Compliance.objects.filter(SubPolicy__PolicyId__FrameworkId=id)
        elif type == 'policy':
            print(f"Getting compliances for policy {id}")
            compliances = Compliance.objects.filter(SubPolicy__PolicyId=id)
        elif type == 'subpolicy':
            print(f"Getting compliances for subpolicy {id}")
            compliances = Compliance.objects.filter(SubPolicy=id)
        else:
            print(f"Invalid type: {type}")
            return Response({
                'success': False,
                'message': f'Invalid type: {type}. Valid types are: framework, policy, subpolicy'
            }, status=400)
        
        print(f"Found {compliances.count()} compliances for {type} {id}")
        
        # Debug: Print each compliance
        for comp in compliances:
            print(f"Compliance: ID={comp.ComplianceId}, Title={comp.ComplianceTitle}, Status={comp.Status}")
        
        # Serialize the data
        serializer = ComplianceListSerializer(compliances, many=True)
        serialized_data = serializer.data
        
        print(f"Serialized {len(serialized_data)} compliances")
        
        # Format the response
        response_data = {
            'success': True, 
            'compliances': serialized_data,
            'count': len(serialized_data)
        }
        
        print(f"Final response: {response_data}")
        print("=== END GET_COMPLIANCES_BY_TYPE DEBUG ===\n")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in get_compliances_by_type: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error fetching compliances: {str(e)}'
        }, status=500)