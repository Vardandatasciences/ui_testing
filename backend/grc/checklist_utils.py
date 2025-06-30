from django.db import connection
from django.utils import timezone
import logging
from .notification_service import NotificationService
from .logging_service import send_log
from datetime import timedelta

logger = logging.getLogger(__name__)

def update_lastchecklistitem_verified(audit_id):
    """
    Update lastchecklistitemverified table when an audit is approved and completed.
    This function:
    1. Gets all compliance items from audit_findings for the given audit
    2. For each compliance, gets the associated policy hierarchy
    3. Updates or inserts records in lastchecklistitemverified table
    4. Prints records where check value is "0" or "1"
    """
    try:
        # Log the start of the update process
        send_log(
            module="Checklist",
            actionType="UPDATE_CHECKLIST_START",
            description=f"Starting update of lastchecklistitemverified for audit ID {audit_id}",
            entityType="Audit",
            entityId=str(audit_id)
        )
        
        current_datetime = timezone.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        with connection.cursor() as cursor:
            # Get audit and user details for notification
            cursor.execute("""
                SELECT 
                    a.assignee,
                    a.auditor,
                    a.reviewer,
                    u_assignee.Email as assignee_email,
                    u_auditor.Email as auditor_email,
                    u_reviewer.Email as reviewer_email,
                    u_assignee.UserName as assignee_name,
                    u_auditor.UserName as auditor_name,
                    u_reviewer.UserName as reviewer_name
                FROM 
                    audit a
                LEFT JOIN users u_assignee ON a.assignee = u_assignee.UserId
                LEFT JOIN users u_auditor ON a.auditor = u_auditor.UserId
                LEFT JOIN users u_reviewer ON a.reviewer = u_reviewer.UserId
                WHERE 
                    a.AuditId = %s
            """, [audit_id])
            
            user_row = cursor.fetchone()
            if user_row:
                assignee_id, auditor_id, reviewer_id, assignee_email, auditor_email, reviewer_email, assignee_name, auditor_name, reviewer_name = user_row
                
                # Log user details retrieved
                send_log(
                    module="Checklist",
                    actionType="AUDIT_USERS_RETRIEVED",
                    description=f"Retrieved user details for audit ID {audit_id}",
                    userId=auditor_id,  # Use auditor as the actor
                    entityType="Audit",
                    entityId=str(audit_id),
                    additionalInfo={
                        "assignee_id": assignee_id,
                        "auditor_id": auditor_id,
                        "reviewer_id": reviewer_id
                    }
                )
            
            # First get all the audit findings for this audit
            cursor.execute("""
                SELECT 
                    af.AuditFindingsId,
                    af.ComplianceId,
                    af.UserId,
                    af.`Check`,
                    af.Comments,
                    c.SubPolicyId,
                    sp.PolicyId,
                    p.FrameworkId
                FROM 
                    audit_findings af
                JOIN 
                    compliance c ON af.ComplianceId = c.ComplianceId
                JOIN 
                    subpolicies sp ON c.SubPolicyId = sp.SubPolicyId
                JOIN 
                    policies p ON sp.PolicyId = p.PolicyId
                WHERE 
                    af.AuditId = %s
            """, [audit_id])
            
            findings = cursor.fetchall()
            
            # Log findings retrieved
            send_log(
                module="Checklist",
                actionType="FINDINGS_RETRIEVED",
                description=f"Retrieved {len(findings)} findings for audit ID {audit_id}",
                entityType="Audit",
                entityId=str(audit_id),
                additionalInfo={"finding_count": len(findings)}
            )
            
            # Count non-compliant findings
            non_compliant_count = 0
            compliant_count = 0
            updated_records = 0
            inserted_records = 0
            
            for finding in findings:
                audit_findings_id, compliance_id, user_id, check_value, comments, subpolicy_id, policy_id, framework_id = finding
                
                # Count non-compliant findings
                if check_value == "0":
                    non_compliant_count += 1
                elif check_value == "1":
                    compliant_count += 1
                
                # Check if a record already exists for this compliance
                cursor.execute("""
                    SELECT COUNT(*), Count 
                    FROM lastchecklistitemverified 
                    WHERE ComplianceId = %s
                """, [compliance_id])
                
                result = cursor.fetchone()
                exists = result[0] > 0
                current_count = result[1] if exists else 0
                
                # Increment count if check value is "0" or "1"
                new_count = current_count
                if check_value in ["0", "1"]:
                    new_count = current_count + 1
                
                if exists:
                    # Update existing record
                    cursor.execute("""
                        UPDATE lastchecklistitemverified
                        SET 
                            SubPolicyId = %s,
                            PolicyId = %s,
                            FrameworkId = %s,
                            Date = %s,
                            Time = %s,
                            User = %s,
                            Complied = %s,
                            Comments = %s,
                            Count = %s,
                            AuditFindingsId = %s
                        WHERE ComplianceId = %s
                    """, [
                        subpolicy_id,
                        policy_id,
                        framework_id,
                        current_date,
                        current_time,
                        user_id,
                        check_value,
                        comments,
                        new_count,
                        audit_findings_id,
                        compliance_id
                    ])
                    updated_records += 1
                    
                    # Log record update
                    if check_value in ["0", "1"]:
                        send_log(
                            module="Checklist",
                            actionType="CHECKLIST_RECORD_UPDATED",
                            description=f"Updated checklist record for compliance ID {compliance_id}",
                            userId=user_id,
                            entityType="Compliance",
                            entityId=str(compliance_id),
                            additionalInfo={
                                "audit_id": audit_id,
                                "complied": check_value,
                                "count": new_count
                            }
                        )
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO lastchecklistitemverified (
                            ComplianceId,
                            SubPolicyId,
                            PolicyId,
                            FrameworkId,
                            Date,
                            Time,
                            User,
                            Complied,
                            Comments,
                            Count,
                            AuditFindingsId
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        compliance_id,
                        subpolicy_id,
                        policy_id,
                        framework_id,
                        current_date,
                        current_time,
                        user_id,
                        check_value,
                        comments,
                        new_count,
                        audit_findings_id
                    ])
                    inserted_records += 1
                    
                    # Log record insertion
                    if check_value in ["0", "1"]:
                        send_log(
                            module="Checklist",
                            actionType="CHECKLIST_RECORD_INSERTED",
                            description=f"Inserted new checklist record for compliance ID {compliance_id}",
                            userId=user_id,
                            entityType="Compliance",
                            entityId=str(compliance_id),
                            additionalInfo={
                                "audit_id": audit_id,
                                "complied": check_value,
                                "count": new_count
                            }
                        )
                
                # Print record if check value is "0" or "1"
                if check_value in ["0", "1"]:
                    cursor.execute("""
                        SELECT * FROM lastchecklistitemverified
                        WHERE ComplianceId = %s
                    """, [compliance_id])
                    record = cursor.fetchone()
                    print(f"Updated/Inserted record for ComplianceId {compliance_id}: {record}")
            
            # Log summary of updates
            send_log(
                module="Checklist",
                actionType="CHECKLIST_UPDATE_SUMMARY",
                description=f"Completed checklist updates for audit ID {audit_id}",
                entityType="Audit",
                entityId=str(audit_id),
                additionalInfo={
                    "updated_records": updated_records,
                    "inserted_records": inserted_records,
                    "compliant_count": compliant_count,
                    "non_compliant_count": non_compliant_count
                }
            )
            
            # Send notification about audit completion with findings summary
            try:
                if assignee_email and auditor_email:
                    notification_service = NotificationService()
                    
                    # Notify assignee about audit completion
                    notification_data = {
                        'notification_type': 'auditCompleted',
                        'email': assignee_email,
                        'email_type': 'gmail',
                        'template_data': [
                            reviewer_name or "Reviewer",
                            f"Audit #{audit_id}",
                            auditor_name or "Auditor",
                            (current_datetime + timedelta(days=7)).strftime('%Y-%m-%d')
                        ]
                    }
                    notification_service.send_multi_channel_notification(notification_data)
                    
                    # Log notification sent
                    send_log(
                        module="Checklist",
                        actionType="NOTIFICATION_SENT",
                        description=f"Sent audit completion notification to assignee for audit ID {audit_id}",
                        entityType="Notification",
                        entityId=str(audit_id),
                        additionalInfo={"recipient": assignee_email}
                    )
                    
                    # Notify management if there are non-compliant findings
                    if non_compliant_count > 0:
                        # Get management emails (you can customize this logic)
                        cursor.execute("""
                            SELECT Email FROM users WHERE Role = 'Manager' OR Role = 'Admin'
                        """)
                        
                        managers = cursor.fetchall()
                        for manager in managers:
                            manager_email = manager[0]
                            notification_data = {
                                'notification_type': 'auditNonCompliance',
                                'email': manager_email,
                                'email_type': 'gmail',
                                'template_data': [
                                    "Manager",
                                    f"Audit #{audit_id}",
                                    str(non_compliant_count),
                                    auditor_name or "Auditor"
                                ]
                            }
                            notification_service.send_multi_channel_notification(notification_data)
                            
                            # Log management notification
                            send_log(
                                module="Checklist",
                                actionType="MANAGEMENT_NOTIFICATION_SENT",
                                description=f"Sent non-compliance notification to management for audit ID {audit_id}",
                                entityType="Notification",
                                entityId=str(audit_id),
                                additionalInfo={
                                    "recipient": manager_email,
                                    "non_compliant_count": non_compliant_count
                                }
                            )
            except Exception as e:
                logger.error(f"Failed to send notification: {str(e)}")
                send_log(
                    module="Checklist",
                    actionType="NOTIFICATION_ERROR",
                    description=f"Failed to send notifications: {str(e)}",
                    entityType="Notification",
                    entityId=str(audit_id),
                    logLevel="ERROR",
                    additionalInfo={"error": str(e)}
                )
        
        # Log successful completion
        send_log(
            module="Checklist",
            actionType="UPDATE_CHECKLIST_COMPLETE",
            description=f"Successfully updated lastchecklistitemverified for audit ID {audit_id}",
            entityType="Audit",
            entityId=str(audit_id)
        )
        
        return True
    except Exception as e:
        logger.error(f"Error in update_lastchecklistitem_verified: {str(e)}")
        print(f"ERROR: Failed to update lastchecklistitemverified table: {str(e)}")
        
        # Log error
        send_log(
            module="Checklist",
            actionType="UPDATE_CHECKLIST_ERROR",
            description=f"Error updating lastchecklistitemverified: {str(e)}",
            entityType="Audit",
            entityId=str(audit_id) if 'audit_id' in locals() else None,
            logLevel="ERROR",
            additionalInfo={"error": str(e)}
        )
        
        return False 