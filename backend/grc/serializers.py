from rest_framework import serializers
from .models import Framework, Policy, SubPolicy, PolicyApproval, ExportTask, Notification, S3File, PolicyCategory ,Entity
from datetime import date
from django.contrib.auth.models import User
from datetime import date

# Import all models
from .models import (
    Audit, Framework, Policy, GRCLog, Users, SubPolicy, Compliance, 
    AuditFinding, Incident, Risk, RiskInstance, Workflow, PolicyApproval, 
    ExportTask, LastChecklistItemVerified, Notification, S3File, 
    PolicyCategory, RiskAssignment
)

# =============================================================================
# FRAMEWORK MODULE SERIALIZERS
# =============================================================================

class FrameworkSerializer(serializers.ModelSerializer):
    policies = serializers.SerializerMethodField()
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Reviewer = serializers.CharField(required=False, allow_blank=True)
    
    def get_policies(self, obj):
        # Filter policies to only include Approved and Active ones
        policies = obj.policy_set.filter(Status='Approved', ActiveInactive='Active')
        return PolicySerializer(policies, many=True).data
    
    class Meta:
        model = Framework
        fields = [
            'FrameworkId', 'FrameworkName', 'CurrentVersion', 'FrameworkDescription',
            'EffectiveDate', 'CreatedByName', 'CreatedByDate', 'Category',
            'DocURL', 'Identifier', 'StartDate', 'EndDate', 'Status',
            'ActiveInactive', 'policies', 'Reviewer'
        ]


# =============================================================================
# POLICY MODULE SERIALIZERS
# =============================================================================



class PolicySerializer(serializers.ModelSerializer):
    FrameworkCategory = serializers.CharField(source='FrameworkId.Category', read_only=True)
    FrameworkName = serializers.CharField(source='FrameworkId.FrameworkName', read_only=True)
    subpolicies = serializers.SerializerMethodField()
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Reviewer = serializers.CharField(required=False, allow_blank=True)
    Status = serializers.CharField(required=False, default='Under Review')
    ActiveInactive = serializers.CharField(required=False, default='Inactive')
    CoverageRate = serializers.FloatField(required=False, allow_null=True)

    def get_subpolicies(self, obj):
        # Get all subpolicies without filtering by status
        subpolicies = obj.subpolicy_set.all()
        return SubPolicySerializer(subpolicies, many=True).data

    class Meta:
        model = Policy
        fields = [
            'PolicyId', 'CurrentVersion', 'Status', 'PolicyName', 'PolicyDescription',
            'StartDate', 'EndDate', 'Department', 'CreatedByName', 'CreatedByDate',
            'Applicability', 'DocURL', 'Scope', 'Objective', 'Identifier',
            'PermanentTemporary', 'ActiveInactive', 'FrameworkId', 'Reviewer',
            'FrameworkCategory', 'FrameworkName', 'subpolicies', 'CoverageRate','PolicyType',
            'PolicyCategory', 'PolicySubCategory', 'Entities'
        ]


class PolicyApprovalSerializer(serializers.ModelSerializer):
    ApprovedDate = serializers.DateField(read_only=True)
    PolicyId = serializers.PrimaryKeyRelatedField(source='PolicyId.PolicyId', read_only=True)
    
    class Meta:
        model = PolicyApproval
        fields = [
            'ApprovalId', 'ExtractedData', 'UserId', 
            'ReviewerId', 'Version', 'ApprovedNot', 'ApprovedDate', 'PolicyId'
        ]


class PolicyAllocationSerializer(serializers.Serializer):
    framework = serializers.IntegerField(required=True, error_messages={'required': 'Framework is required', 'invalid': 'Framework must be a valid integer'})
    policy = serializers.IntegerField(required=False, allow_null=True)
    subpolicy = serializers.IntegerField(required=False, allow_null=True)
    assignee = serializers.IntegerField(required=True, error_messages={'required': 'Assignee is required', 'invalid': 'Assignee must be a valid user ID'})
    auditor = serializers.IntegerField(required=True, error_messages={'required': 'Auditor is required', 'invalid': 'Auditor must be a valid user ID'})
    reviewer = serializers.IntegerField(required=False, allow_null=True)
    duedate = serializers.DateField(required=True, error_messages={'required': 'Due date is required', 'invalid': 'Due date must be in YYYY-MM-DD format'})
    frequency = serializers.IntegerField(required=True, error_messages={'required': 'Frequency is required', 'invalid': 'Frequency must be a valid integer'})
    audit_type = serializers.CharField(max_length=1, required=True, error_messages={'required': 'Audit type is required', 'invalid': 'Audit type must be either Internal (I) or External (E)'})
   
    def validate_policy(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value
   
    def validate_subpolicy(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value
   
    def validate_reviewer(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value
 
    # Custom validation for due date
    def validate_duedate(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
   
    def validate_audit_type(self, value):
        # Convert 'Internal' to 'I' and 'External' to 'E'
        if value == 'Internal':
            return 'I'
        elif value == 'External':
            return 'E'
        # If already the single character, just return it
        elif value in ['I', 'E']:
            return value
        else:
            raise serializers.ValidationError("Invalid audit type. Must be 'Internal' or 'External'.")


class PolicyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCategory
        fields = '__all__'  # Includes: Id, PolicyType, PolicyCategory, PolicySubCategory


# =============================================================================
# SUB-POLICY MODULE SERIALIZERS
# =============================================================================

class SubPolicySerializer(serializers.ModelSerializer):
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Status = serializers.CharField(required=False, default='Under Review')
    PermanentTemporary = serializers.CharField(required=False, default='Permanent')

    class Meta:
        model = SubPolicy
        fields = [
            'SubPolicyId', 'SubPolicyName', 'CreatedByName', 'CreatedByDate',
            'Identifier', 'Description', 'Status', 'PermanentTemporary',
            'Control', 'PolicyId'
        ]


# =============================================================================
# COMPLIANCE MODULE SERIALIZERS
# =============================================================================

class ComplianceSerializer(serializers.ModelSerializer):
    Impact = serializers.CharField(max_length=50, required=True)
    Probability = serializers.CharField(max_length=50, required=True)
    ComplianceTitle = serializers.CharField(max_length=145, required=True)
    ComplianceItemDescription = serializers.CharField(required=True)
    ComplianceType = serializers.CharField(max_length=100, required=True)
    Scope = serializers.CharField(required=True)
    Objective = serializers.CharField(required=True)
    Criticality = serializers.ChoiceField(choices=['High', 'Medium', 'Low'], required=True)
    MandatoryOptional = serializers.ChoiceField(choices=['Mandatory', 'Optional'], required=False)
    ManualAutomatic = serializers.ChoiceField(choices=['Manual', 'Automatic'], required=False)
    MaturityLevel = serializers.ChoiceField(
        choices=['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing'],
        required=False
    )
    Status = serializers.CharField(default='Under Review')
    ActiveInactive = serializers.CharField(default='Active')
    ComplianceVersion = serializers.CharField(required=True)
    mitigation = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = Compliance
        fields = '__all__'

    def validate_ComplianceTitle(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        if len(value) > 145:
            raise serializers.ValidationError("Title cannot exceed 145 characters")
        return value

    def validate_ComplianceItemDescription(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value

    def validate_Scope(self, value):
        if len(value) < 15:
            raise serializers.ValidationError("Scope must be at least 15 characters long")
        return value

    def validate_Objective(self, value):
        if len(value) < 15:
            raise serializers.ValidationError("Objective must be at least 15 characters long")
        return value

    def validate_Impact(self, value):
        try:
            impact = float(value)
            if not (0 <= impact <= 10):
                raise serializers.ValidationError("Impact must be between 0 and 10")
        except ValueError:
            raise serializers.ValidationError("Impact must be a number between 0 and 10")
        return str(impact)

    def validate_Probability(self, value):
        try:
            probability = float(value)
            if not (0 <= probability <= 10):
                raise serializers.ValidationError("Probability must be between 0 and 10")
        except ValueError:
            raise serializers.ValidationError("Probability must be a number between 0 and 10")
        return str(probability)

    def validate_mitigation(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Mitigation must be a dictionary")
        # Ensure all values are strings and not empty
        cleaned = {}
        for key, step in value.items():
            if isinstance(step, str) and step.strip():
                cleaned[key] = step.strip()
        return cleaned


class ComplianceCreateSerializer(serializers.ModelSerializer):
    SubPolicyId = serializers.PrimaryKeyRelatedField(queryset=SubPolicy.objects.all())
    Identifier = serializers.CharField(max_length=50)
    IsRisk = serializers.BooleanField()
    Criticality = serializers.ChoiceField(choices=['High', 'Medium', 'Low'])
    ManualAutomatic = serializers.ChoiceField(choices=['Manual', 'Automatic'])
    
    # Change these to CharFields to match the model
    Impact = serializers.CharField(max_length=50)
    Probability = serializers.CharField(max_length=50)
    
    ActiveInactive = serializers.ChoiceField(choices=['Active', 'Inactive'], required=False)
    PermanentTemporary = serializers.ChoiceField(choices=['Permanent', 'Temporary'])
    Status = serializers.ChoiceField(choices=['Approved', 'Active', 'Schedule', 'Rejected', 'Under Review'], required=False)
    
    class Meta:
        model = Compliance
        fields = [
            'SubPolicyId', 'Identifier', 'ComplianceItemDescription', 'IsRisk',
            'PossibleDamage', 'mitigation', 'Criticality',
            'MandatoryOptional', 'ManualAutomatic', 'Impact',
            'Probability', 'ActiveInactive', 'PermanentTemporary',
            'Status'
        ]
    
    def create(self, validated_data):
        # Auto-generate ComplianceVersion
        subpolicy = validated_data['SubPolicyId']
        latest = Compliance.objects.filter(SubPolicyId=subpolicy).order_by('-ComplianceVersion').first()
        
        if latest:
            try:
                current_version = float(latest.ComplianceVersion)
                new_version = current_version + 0.1
                validated_data['ComplianceVersion'] = f"{new_version:.1f}"
            except (ValueError, TypeError):
                validated_data['ComplianceVersion'] = "1.0"
        else:
            validated_data['ComplianceVersion'] = "1.0"
        
        return super().create(validated_data)


class ComplianceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = [
            'ComplianceId', 'SubPolicy', 'ComplianceItemDescription', 'IsRisk',
            'PossibleDamage', 'mitigation', 'Criticality', 'MandatoryOptional',
            'ManualAutomatic', 'Impact', 'Probability', 'MaturityLevel', 'ActiveInactive',
            'PermanentTemporary', 'ComplianceVersion', 'Status', 'Identifier', 
            'PreviousComplianceVersionId', 'CreatedByName', 'CreatedByDate',
            'PotentialRiskScenarios', 'RiskType', 'RiskCategory', 'RiskBusinessImpact',
            'ComplianceTitle', 'Scope', 'Objective', 'BusinessUnitsCovered', 'Applicability'
        ]


class LastChecklistItemVerifiedSerializer(serializers.ModelSerializer):
    framework_name = serializers.CharField(source='FrameworkId.FrameworkName', read_only=True)
    
    class Meta:
        model = LastChecklistItemVerified
        fields = ['FrameworkId', 'ComplianceId', 'PolicyId', 'SubPolicyId', 'Date', 
                 'Time', 'User', 'Complied', 'Comments', 'count', 'framework_name']


# =============================================================================
# AUDIT MODULE SERIALIZERS
# =============================================================================

class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = ['AuditId', 'Assignee', 'Auditor', 'Reviewer', 'FrameworkId', 'PolicyId', 'DueDate', 'Frequency', 'AuditType', 'Status']


class AuditFindingSerializer(serializers.ModelSerializer):
    ComplianceDetails = serializers.SerializerMethodField()
    compliance_name = serializers.SerializerMethodField()
    compliance_mitigation = serializers.SerializerMethodField()
    comments = serializers.CharField(source='Comments', required=False)

    class Meta:
        model = AuditFinding
        fields = '__all__'

    def get_ComplianceDetails(self, obj):
        if obj.ComplianceId:
            return {
                'description': obj.ComplianceId.ComplianceItemDescription,
                'mitigation': obj.ComplianceId.mitigation if hasattr(obj.ComplianceId, 'mitigation') else None,
            }
        return None

    def get_compliance_name(self, obj):
        return obj.ComplianceId.ComplianceItemDescription if obj.ComplianceId else "No description"

    def get_compliance_mitigation(self, obj):
        return obj.ComplianceId.mitigation if obj.ComplianceId and hasattr(obj.ComplianceId, 'mitigation') else None


# =============================================================================
# INCIDENT MODULE SERIALIZERS
# =============================================================================

class IncidentSerializer(serializers.ModelSerializer):
    has_risk_instance = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = '__all__'
    
    def get_has_risk_instance(self, obj):
        return RiskInstance.objects.filter(IncidentId=obj.IncidentId).exists()


# =============================================================================
# RISK MODULE SERIALIZERS
# =============================================================================

class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = [
            'RiskId', 'ComplianceId', 'RiskTitle', 'Criticality', 'PossibleDamage', 
            'Category', 'RiskType', 'BusinessImpact', 'RiskPriority', 'RiskDescription', 
            'RiskLikelihood', 'RiskImpact', 'RiskExposureRating', 'RiskMitigation', 
            'CreatedAt'
        ]  # Explicitly list fields that exist in the model


class RiskInstanceSerializer(serializers.ModelSerializer):
    # Add this custom field to handle any format of RiskMitigation
    RiskMitigation = serializers.JSONField(required=False, allow_null=True)
    # Use DateField for MitigationDueDate instead of relying on auto-conversion
    MitigationDueDate = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")
    # Handle other date/datetime fields to prevent conversion issues
    MitigationCompletedDate = serializers.DateTimeField(required=False, allow_null=True, format="%Y-%m-%d %H:%M:%S")
    ModifiedMitigations = serializers.JSONField(required=False, allow_null=True)
    RiskFormDetails = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = RiskInstance
        fields = '__all__'
    
    def to_internal_value(self, data):
        # Convert the QueryDict or dict to a mutable dict
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Remove Date field if present as it's been replaced with CreatedAt
        if 'Date' in mutable_data:
            mutable_data.pop('Date')
        
        # Set default values for required fields
        if not mutable_data.get('RiskOwner'):
            mutable_data['RiskOwner'] = 'System Owner'
        
        if not mutable_data.get('RiskStatus'):
            mutable_data['RiskStatus'] = 'Open'
        
        # Handle RiskMitigation if it's present but empty
        if 'RiskMitigation' in mutable_data and not mutable_data['RiskMitigation']:
            mutable_data['RiskMitigation'] = {}
            
        # Handle ModifiedMitigations if it's present but empty
        if 'ModifiedMitigations' in mutable_data and not mutable_data['ModifiedMitigations']:
            mutable_data['ModifiedMitigations'] = None
            
        # Handle RiskFormDetails if it's present but empty
        if 'RiskFormDetails' in mutable_data and not mutable_data['RiskFormDetails']:
            mutable_data['RiskFormDetails'] = None
        
        return super().to_internal_value(mutable_data)
    
    def create(self, validated_data):
        # Clean up the data before creating the instance
        for field in ['RiskMitigation', 'ModifiedMitigations', 'RiskFormDetails']:
            if field in validated_data and validated_data[field] == '':
                if field == 'RiskMitigation':
                    validated_data[field] = {}
                else:
                    validated_data[field] = None
        
        # Create the instance with cleaned data
        return RiskInstance.objects.create(**validated_data)
        
    def to_representation(self, instance):
        """
        Override to ensure date fields are properly serialized
        """
        # First get the default representation
        representation = super().to_representation(instance)
        
        # Handle each date field to ensure it's properly formatted
        for field in ['MitigationDueDate', 'MitigationCompletedDate']:
            # If the field exists and has a value
            if field in representation and representation[field] is not None:
                # Convert date objects to strings to avoid serialization issues
                if hasattr(instance, field):
                    value = getattr(instance, field)
                    if hasattr(value, 'isoformat'):
                        try:
                            representation[field] = value.isoformat()
                        except:
                            # If conversion fails, keep as is
                            pass
        
        return representation


class RiskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssignment
        fields = '__all__'


class RiskWorkflowSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    
    class Meta:
        model = Risk
        fields = ['id', 'title', 'description', 'severity', 'status', 'assigned_to']
        
    def get_assigned_to(self, obj):
        assignment = obj.assignments.first()
        if assignment:
            return assignment.assigned_to.username
        return None


# =============================================================================
# USER & SYSTEM MODULE SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = Users
        fields = ['UserId', 'UserName', 'CreatedAt', 'UpdatedAt', 'role']
    
    def get_role(self, obj):
        # Assign roles based on UserName patterns or UserId
        # This is a temporary solution until role field is added to the database
        name = obj.UserName.lower()
        user_id = obj.UserId
        
        # Assign roles based on name patterns or user ID
        if 'admin' in name or 'manager' in name:
            return 'Security Manager'
        elif 'analyst' in name or user_id % 4 == 1:
            return 'Security Analyst'
        elif 'auditor' in name or 'audit' in name or user_id % 4 == 2:
            return 'Audit Manager'
        elif 'compliance' in name or user_id % 4 == 3:
            return 'Compliance Officer'
        elif 'specialist' in name or 'senior' in name:
            return 'Senior Analyst'
        elif 'risk' in name:
            return 'Risk Analyst'
        elif 'operations' in name:
            return 'Operations Manager'
        else:
            # Default roles for other users
            roles = ['Security Analyst', 'Risk Analyst', 'Compliance Officer', 'IT Security Specialist']
            return roles[user_id % len(roles)]


class GRCLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRCLog
        fields = '__all__'


class ExportTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportTask
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class S3FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3File
        fields = '__all__'


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'  # Includes: Id, EntityName, Location

