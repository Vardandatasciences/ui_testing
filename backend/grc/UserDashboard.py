from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Audit, AuditFinding, Framework
from datetime import datetime, timedelta
from calendar import monthrange
from django.db.models import Count, Q
from django.utils import timezone

__all__ = [
    'get_audit_completion_rate',
    'get_total_audits',
    'get_open_audits',
    'get_completed_audits',
    'audit_completion_trend',
    'audit_compliance_trend',
    'audit_finding_trend',
    'framework_performance',
    'category_performance',
    'status_distribution',
    'recent_audit_activities'
]

@api_view(['GET'])
def get_audit_completion_rate(request):
    # Get the current date
    today = datetime.today()

    # Get the first and last day of the current month
    first_day_current_month = today.replace(day=1)
    last_day_current_month = (first_day_current_month.replace(month=first_day_current_month.month % 12 + 1, year=first_day_current_month.year + first_day_current_month.month // 12) - timedelta(days=1))

    # Get the first and last day of the previous month
    first_day_previous_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)

    # Current month completion rate
    current_month_data = Audit.objects.filter(AssignedDate__range=[first_day_current_month, last_day_current_month])
    planned_count_current = current_month_data.count()
    completed_count_current = current_month_data.filter(Status='Completed').count()
    current_month_rate = round((completed_count_current / planned_count_current * 100), 2) if planned_count_current else 0

    # Previous month completion rate
    previous_month_data = Audit.objects.filter(AssignedDate__range=[first_day_previous_month, last_day_previous_month])
    planned_count_previous = previous_month_data.count()
    completed_count_previous = previous_month_data.filter(Status='Completed').count()
    previous_month_rate = round((completed_count_previous / planned_count_previous * 100), 2) if planned_count_previous else 0

    # Calculate the change in rate
    change_in_rate = round(current_month_rate - previous_month_rate, 2)

    return Response({
        'current_month_rate': current_month_rate,
        'previous_month_rate': previous_month_rate,
        'change_in_rate': change_in_rate,
        'is_positive_change': change_in_rate >= 0
    })

@api_view(['GET'])
def get_total_audits(request):
    # Get the current date
    today = datetime.today()

    # Get the first and last day of the current month
    first_day_current_month = today.replace(day=1)
    last_day_current_month = (first_day_current_month.replace(month=first_day_current_month.month % 12 + 1, year=first_day_current_month.year + first_day_current_month.month // 12) - timedelta(days=1))

    # Get the first and last day of the previous month
    first_day_previous_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)

    # Get total audits for current month
    total_current_month = Audit.objects.filter(AssignedDate__range=[first_day_current_month, last_day_current_month]).count()

    # Get total audits for previous month
    total_previous_month = Audit.objects.filter(AssignedDate__range=[first_day_previous_month, last_day_previous_month]).count()

    # Calculate change in total audits
    change_in_total = total_current_month - total_previous_month

    return Response({
        'total_current_month': total_current_month,
        'total_previous_month': total_previous_month,
        'change_in_total': change_in_total,
        'is_positive_change': change_in_total >= 0
    })

@api_view(['GET'])
def get_open_audits(request):
    # Get current date
    today = datetime.today()
    
    # Current week range: Monday to Sunday
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Last week range: Monday to Sunday
    start_of_last_week = start_of_week - timedelta(days=7)
    end_of_last_week = start_of_week - timedelta(seconds=1)

    # Current week open audits (not completed)
    open_this_week = Audit.objects.filter(
        AssignedDate__range=[start_of_week, end_of_week]
    ).exclude(Status='Completed').count()

    # Last week open audits (not completed)
    open_last_week = Audit.objects.filter(
        AssignedDate__range=[start_of_last_week, end_of_last_week]
    ).exclude(Status='Completed').count()

    # Change in open audits
    change_in_open = open_this_week - open_last_week

    # True if we have fewer open audits this week (improvement)
    is_improvement = change_in_open < 0

    # Optional: Percent change
    if open_last_week > 0:
        percent_change = round((change_in_open / open_last_week) * 100, 2)
    else:
        percent_change = 100 if open_this_week > 0 else 0

    return Response({
        'open_this_week': open_this_week,
        'open_last_week': open_last_week,
        'change_in_open': change_in_open,
        'percent_change': percent_change,
        'is_improvement': is_improvement
    })

@api_view(['GET'])
def get_completed_audits(request):
    today = datetime.today()

    # Week range: Monday to Sunday
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Last week range
    start_of_last_week = start_of_week - timedelta(days=7)
    end_of_last_week = start_of_week - timedelta(seconds=1)

    # This week's completed audits
    this_week_count = Audit.objects.filter(
        AssignedDate__range=[start_of_week, end_of_week],
        Status='Completed'
    ).count()

    # Last week's completed audits
    last_week_count = Audit.objects.filter(
        AssignedDate__range=[start_of_last_week, end_of_last_week],
        Status='Completed'
    ).count()

    # Change and trend direction
    change_in_completed = this_week_count - last_week_count
    is_improvement = change_in_completed > 0  # More completed audits is better

    # Optional: percentage change
    if last_week_count > 0:
        percent_change = round((change_in_completed / last_week_count) * 100, 2)
    else:
        percent_change = 100 if this_week_count > 0 else 0

    return Response({
        'this_week_count': this_week_count,
        'last_week_count': last_week_count,
        'change_in_completed': change_in_completed,
        'percent_change': percent_change,
        'is_improvement': is_improvement
    })

@api_view(['GET'])
def audit_completion_trend(request):
    current_year = datetime.today().year
    result = []

    # From January to current month (or you can set it as range(1, 13) for full year)
    for month in range(1, 8):  # Jan to July
        first_day = datetime(current_year, month, 1)
        last_day = datetime(current_year, month, monthrange(current_year, month)[1])

        audits = Audit.objects.filter(AssignedDate__range=[first_day, last_day])
        total = audits.count()
        completed = audits.filter(Status='Completed').count()

        rate = round((completed / total) * 100, 2) if total else 0

        result.append({
            "month": first_day.strftime('%b'),  # Jan, Feb, ...
            "completion_rate": rate
        })

    return Response(result)

@api_view(['GET'])
def audit_compliance_trend(request):
    current_year = datetime.today().year
    result = []

    # From January to current month
    for month in range(1, 8):  # Jan to July
        first_day = datetime(current_year, month, 1)
        last_day = datetime(current_year, month, monthrange(current_year, month)[1])

        # Get all audit findings for this month
        findings = AuditFinding.objects.filter(AssignedDate__range=[first_day, last_day])
        total_findings = findings.count()
        
        # Using Impact field instead of ComplianceStatus since ComplianceStatus doesn't exist
        # Assuming findings with 'Low' Impact are considered compliant
        compliant_findings = findings.filter(Impact='Low').count()

        compliance_rate = round((compliant_findings / total_findings) * 100, 2) if total_findings else 0

        result.append({
            "month": first_day.strftime('%b'),  # Jan, Feb, ...
            "compliance_rate": compliance_rate
        })

    return Response(result)

@api_view(['GET'])
def audit_finding_trend(request):
    current_year = datetime.today().year
    result = []

    # From January to current month
    for month in range(1, 8):  # Jan to July
        first_day = datetime(current_year, month, 1)
        last_day = datetime(current_year, month, monthrange(current_year, month)[1])

        # Get all findings for this month
        total_findings = AuditFinding.objects.filter(AssignedDate__range=[first_day, last_day]).count()
        major_findings = AuditFinding.objects.filter(
            AssignedDate__range=[first_day, last_day], 
            Impact__in=['Critical', 'Major']
        ).count()
        minor_findings = total_findings - major_findings

        result.append({
            "month": first_day.strftime('%b'),  # Jan, Feb, ...
            "total_findings": total_findings,
            "major_findings": major_findings,
            "minor_findings": minor_findings
        })

    return Response(result)

@api_view(['GET'])
def framework_performance(request):
    # Get frameworks from the frameworks table instead of hardcoded values
    from django.db.models import Count, Q
    from .models import Framework, Audit
    
    # Fetch active frameworks from the database
    frameworks = Framework.objects.filter(ActiveInactive='Active').values('FrameworkName', 'FrameworkId')
    
    # If no frameworks are found, try with different field names (database column might be different)
    if not frameworks.exists():
        try:
            # Try with different possible field names for active status
            frameworks = Framework.objects.all().values('FrameworkName', 'FrameworkId')
        except Exception as e:
            # Log the error and return empty result
            print(f"Error fetching frameworks: {e}")
            return Response([])
    
    result = []

    for framework in frameworks:
        framework_id = framework['FrameworkId']
        framework_name = framework['FrameworkName']
        
        # Get audits for this framework - use FrameworkId_id instead of Framework
        audits = Audit.objects.filter(FrameworkId_id=framework_id)
        total = audits.count()
        
        if total > 0:
            # Count audits by status
            completed = audits.filter(Status='Completed').count()
            in_progress = audits.filter(Status='In Progress').count()
            yet_to_start = total - (completed + in_progress)
            
            # Calculate completion rate
            completion_rate = round((completed / total) * 100, 2)
            
            result.append({
                "framework": framework_name,
                "framework_id": framework_id,
                "completion_rate": completion_rate,
                "completed": completed,
                "in_progress": in_progress,
                "yet_to_start": yet_to_start
            })

    # Sort by framework name if there are results
    if result:
        result = sorted(result, key=lambda x: x['framework'])
        
    return Response(result)

@api_view(['GET'])
def category_performance(request):
    # Get unique categories from the frameworks table
    from django.db.models import Count, Q
    from .models import Framework, Audit
    
    # Fetch distinct categories from frameworks
    try:
        # Get distinct categories from the Framework model
        categories = Framework.objects.values_list('Category', flat=True).distinct()
        
        # If no categories found, use default categories
        if not categories:
            categories = ['Information Security', 'Data Protection', 'Risk Assessment', 'Access Control', 'Change Management']
    except Exception as e:
        # Log the error and use default categories
        print(f"Error fetching categories: {e}")
        categories = ['Information Security', 'Data Protection', 'Risk Assessment', 'Access Control', 'Change Management']
    
    result = []

    for category in categories:
        if not category:  # Skip empty categories
            continue
            
        # Get audits for this category through the framework
        framework_ids = Framework.objects.filter(Category=category).values_list('FrameworkId', flat=True)
        
        # Use FrameworkId_id instead of Framework__in based on error message
        audits = Audit.objects.filter(FrameworkId_id__in=framework_ids)
        
        total = audits.count()
        completed = audits.filter(Status='Completed').count()
        
        # Calculate completion rate
        completion_rate = round((completed / total) * 100, 2) if total else 0
        
        result.append({
            "category": category,
            "completion_rate": completion_rate,
            "total": total,
            "completed": completed
        })
    
    # Sort by category name
    result = sorted(result, key=lambda x: x['category'])
    
    return Response(result)

@api_view(['GET'])
def status_distribution(request):
    # Count audits by status
    total = Audit.objects.count()
    completed = Audit.objects.filter(Status='Completed').count()
    in_progress = Audit.objects.filter(Status='In Progress').count()
    yet_to_start = total - (completed + in_progress)

    # Calculate percentages
    completed_percent = round((completed / total) * 100, 2) if total else 0
    in_progress_percent = round((in_progress / total) * 100, 2) if total else 0
    yet_to_start_percent = round((yet_to_start / total) * 100, 2) if total else 0

    return Response({
        "completed": completed,
        "in_progress": in_progress,
        "yet_to_start": yet_to_start,
        "completed_percent": completed_percent,
        "in_progress_percent": in_progress_percent,
        "yet_to_start_percent": yet_to_start_percent
    })

@api_view(['GET'])
def recent_audit_activities(request):
    """
    Fetch recent audit activities including:
    - Recently completed audits
    - Recently received reviews
    - Audits with approaching due dates
    """
    try:
        from datetime import datetime, timedelta
        from django.db.models import F, Q
        from .models import Audit, Framework
        from django.utils import timezone
        
        today = timezone.now()
        
        # Get audits completed in the last 7 days
        try:
            # Try with CompletionDate field first
            recent_completed = Audit.objects.filter(
                Status='Completed',
                CompletionDate__isnull=False
            ).order_by('-CompletionDate')[:5]
            
            # If query returns no results, try alternative field names
            if not recent_completed.exists():
                print("No completed audits found with CompletionDate, trying alternative field names")
                # Try with alternative field name if it exists
                field_names = [f.name for f in Audit._meta.get_fields()]
                if 'CompletedDate' in field_names:
                    recent_completed = Audit.objects.filter(
                        Status='Completed',
                        CompletedDate__isnull=False
                    ).order_by('-CompletedDate')[:5]
                elif 'completiondate' in field_names:
                    recent_completed = Audit.objects.filter(
                        Status='Completed',
                        completiondate__isnull=False
                    ).order_by('-completiondate')[:5]
        except Exception as e:
            print(f"Error fetching completed audits: {e}")
            recent_completed = []
        
        # Get audits that received reviews in the last 7 days
        try:
            # Try with ReviewDate field first
            recent_reviews = Audit.objects.filter(
                ReviewStatus__isnull=False,
                ReviewDate__isnull=False
            ).order_by('-ReviewDate')[:5]
            
            # If query returns no results, try alternative field names
            if not recent_reviews.exists():
                print("No reviewed audits found with ReviewDate, trying alternative field names")
                # Try with alternative field name if it exists
                field_names = [f.name for f in Audit._meta.get_fields()]
                if 'ReviewedDate' in field_names:
                    recent_reviews = Audit.objects.filter(
                        ReviewStatus__isnull=False,
                        ReviewedDate__isnull=False
                    ).order_by('-ReviewedDate')[:5]
                elif 'reviewdate' in field_names:
                    recent_reviews = Audit.objects.filter(
                        ReviewStatus__isnull=False,
                        reviewdate__isnull=False
                    ).order_by('-reviewdate')[:5]
        except Exception as e:
            print(f"Error fetching reviewed audits: {e}")
            recent_reviews = []
        
        # Get audits with due dates approaching in the next 7 days
        try:
            approaching_due = Audit.objects.filter(
                Status__in=['In Progress', 'Not Started'],
                DueDate__isnull=False
            ).order_by('DueDate')[:5]
        except Exception as e:
            print(f"Error fetching approaching due audits: {e}")
            approaching_due = []
        
        # Prepare the result
        result = []
        
        # Add completed audits
        for audit in recent_completed:
            # Get framework name
            framework_name = "Unknown Framework"
            try:
                if audit.FrameworkId_id:
                    # Get only the necessary fields to avoid issues with unknown columns
                    framework = Framework.objects.filter(FrameworkId=audit.FrameworkId_id).values('FrameworkId', 'FrameworkName').first()
                    if framework and 'FrameworkName' in framework:
                        framework_name = framework['FrameworkName']
            except Exception as e:
                print(f"Error fetching framework: {e}")
            
            # Handle CompletionDate - ensure it's a string if it exists
            completion_date = None
            if audit.CompletionDate:
                try:
                    time_ago = get_time_ago(audit.CompletionDate)
                    completion_date = audit.CompletionDate.isoformat() if hasattr(audit.CompletionDate, 'isoformat') else str(audit.CompletionDate)
                except Exception as e:
                    print(f"Error formatting completion date: {e}")
                    time_ago = "Recently"
                    completion_date = None
            else:
                time_ago = "Recently"
            
            result.append({
                'type': 'completed',
                'audit_id': audit.AuditId,
                'title': 'Audit Completed',
                'description': f"{framework_name} - {audit.AuditType or 'Compliance Audit'}",
                'time_ago': time_ago,
                'timestamp': completion_date
            })
        
        # Add recently reviewed audits
        for audit in recent_reviews:
            # Get framework name
            framework_name = "Unknown Framework"
            try:
                if audit.FrameworkId_id:
                    # Get only the necessary fields to avoid issues with unknown columns
                    framework = Framework.objects.filter(FrameworkId=audit.FrameworkId_id).values('FrameworkId', 'FrameworkName').first()
                    if framework and 'FrameworkName' in framework:
                        framework_name = framework['FrameworkName']
            except Exception as e:
                print(f"Error fetching framework: {e}")
            
            # Handle ReviewDate
            review_date = None
            if audit.ReviewDate:
                try:
                    time_ago = get_time_ago(audit.ReviewDate)
                    review_date = audit.ReviewDate.isoformat() if hasattr(audit.ReviewDate, 'isoformat') else str(audit.ReviewDate)
                except Exception as e:
                    print(f"Error formatting review date: {e}")
                    time_ago = "Recently"
                    review_date = None
            else:
                time_ago = "Recently"
            
            result.append({
                'type': 'review',
                'audit_id': audit.AuditId,
                'title': 'Review Received',
                'description': f"{framework_name} {audit.AuditType or 'Compliance Audit'}",
                'time_ago': time_ago,
                'timestamp': review_date
            })
        
        # Add due dates approaching
        for audit in approaching_due:
            # Get framework name
            framework_name = "Unknown Framework"
            try:
                if audit.FrameworkId_id:
                    # Get only the necessary fields to avoid issues with unknown columns
                    framework = Framework.objects.filter(FrameworkId=audit.FrameworkId_id).values('FrameworkId', 'FrameworkName').first()
                    if framework and 'FrameworkName' in framework:
                        framework_name = framework['FrameworkName']
            except Exception as e:
                print(f"Error fetching framework: {e}")
            
            # Handle DueDate
            due_date = None
            if audit.DueDate:
                try:
                    time_ago = get_time_ago(audit.DueDate, future=True)
                    due_date = audit.DueDate.isoformat() if hasattr(audit.DueDate, 'isoformat') else str(audit.DueDate)
                except Exception as e:
                    print(f"Error formatting due date: {e}")
                    time_ago = "Soon"
                    due_date = None
            else:
                time_ago = "Soon"
            
            result.append({
                'type': 'due',
                'audit_id': audit.AuditId,
                'title': 'Due Date Approaching',
                'description': f"{framework_name} {audit.AuditType or 'Compliance Audit'}",
                'time_ago': time_ago,
                'timestamp': due_date
            })
        
        # Sort by timestamp (newest first)
        try:
            result.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            print(f"Error sorting activities: {e}")
            # Don't sort if there's an error
        
        # Limit to 10 most recent activities
        result = result[:10]
        
        return Response(result)
    except Exception as e:
        print(f"Error in recent_audit_activities: {e}")
        # Return an empty list if there was an error
        return Response([])

def get_time_ago(date_time, future=False):
    """Helper function to format time difference in a human-readable format"""
    if not date_time:
        return ""
    
    # Make sure date_time is timezone-aware
    if timezone.is_naive(date_time):
        date_time = timezone.make_aware(date_time)
    
    now = timezone.now()
    
    try:
        if future:
            diff = date_time - now  # Time until the due date
        else:
            diff = now - date_time  # Time since the event
        
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 30:
            months = days // 30
            return f"{months} {'month' if months == 1 else 'months'} {'until' if future else 'ago'}"
        elif days > 0:
            return f"{days} {'day' if days == 1 else 'days'} {'until' if future else 'ago'}"
        elif hours > 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'} {'until' if future else 'ago'}"
        elif minutes > 0:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} {'until' if future else 'ago'}"
        else:
            return "Just now"
    except Exception as e:
        print(f"Error calculating time difference: {e}")
        return "Recently" if not future else "Soon"