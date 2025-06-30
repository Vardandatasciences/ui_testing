-- Direct SQL script to update the Evidence column
-- This script directly updates the Evidence column in the audit_findings table
-- for the specific compliance_id and audit_id combination

-- Set the URL to be saved
SET @evidence_url = 'https://grc-files-vardaan.s3.amazonaws.com/1749550184249_AY5911452126.pdf_compliance_id-12_documentType-evidence_table_name-audit_findings_storage_column-Evidence_audit_id-33_document_type-pdf_file_type-pdf';

-- Update the evidence URL for the specific compliance_id and audit_id
UPDATE audit_findings 
SET Evidence = @evidence_url
WHERE ComplianceId = 12 AND AuditId = 33;

-- If no rows were affected, insert a new record
INSERT INTO audit_findings (ComplianceId, AuditId, Evidence, UserId, `Check`)
SELECT 12, 33, @evidence_url, 1050, '1'
FROM dual
WHERE NOT EXISTS (
    SELECT 1 FROM audit_findings WHERE ComplianceId = 12 AND AuditId = 33
);

-- Verify the update
SELECT ComplianceId, AuditId, Evidence
FROM audit_findings
WHERE ComplianceId = 12 AND AuditId = 33; 