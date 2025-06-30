-- SQL Script to update the audit_findings table schema
-- This script modifies the Evidence and S3Location columns to TEXT type
-- to ensure they can store long URLs without truncation

-- Check if Evidence column needs to be updated
ALTER TABLE audit_findings MODIFY COLUMN Evidence TEXT;

-- Update the specific evidence record for ComplianceId=12 and AuditId=33
UPDATE audit_findings 
SET Evidence = 'https://grc-files-vardaan.s3.amazonaws.com/1749549561613_cakes.pdf_compliance_id-12_documentType-evidence_table_name-audit_findings_storage_column-Evidence_audit_id-33_document_type-pdf_file_type-pdf'
WHERE ComplianceId = 12 AND AuditId = 33;

-- If no rows were affected, insert a new record
INSERT INTO audit_findings (ComplianceId, AuditId, Evidence, UserId, `Check`)
SELECT 12, 33, 
       'https://grc-files-vardaan.s3.amazonaws.com/1749549561613_cakes.pdf_compliance_id-12_documentType-evidence_table_name-audit_findings_storage_column-Evidence_audit_id-33_document_type-pdf_file_type-pdf',
       1050, '1'
WHERE NOT EXISTS (
    SELECT 1 FROM audit_findings WHERE ComplianceId = 12 AND AuditId = 33
);

-- Verify the update
SELECT ComplianceId, AuditId, Evidence, S3Location
FROM audit_findings
WHERE ComplianceId = 12 AND AuditId = 33; 