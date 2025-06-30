-- Create s3_files table if it doesn't exist
CREATE TABLE IF NOT EXISTS `s3_files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `metadata` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id_idx` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add S3Location column to evidence table if it doesn't exist
ALTER TABLE `evidence` 
ADD COLUMN IF NOT EXISTS `S3Location` varchar(1024) DEFAULT NULL COMMENT 'S3 URL or file path';

-- Create evidence table if it doesn't exist
CREATE TABLE IF NOT EXISTS `evidence` (
  `EvidenceId` int(11) NOT NULL AUTO_INCREMENT,
  `ComplianceId` int(11) NOT NULL,
  `FileName` varchar(255) NOT NULL,
  `FileSize` int(11) DEFAULT NULL,
  `S3Location` varchar(1024) DEFAULT NULL,
  `UploadedBy` varchar(255) DEFAULT NULL,
  `UploadedOn` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`EvidenceId`),
  KEY `ComplianceId_idx` (`ComplianceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Make sure the audit_findings table has an Evidence column
ALTER TABLE `audit_findings` 
ADD COLUMN IF NOT EXISTS `Evidence` varchar(255) DEFAULT NULL COMMENT 'Evidence file name';

-- Add S3Location column to audit_findings if it doesn't exist
ALTER TABLE `audit_findings` 
ADD COLUMN IF NOT EXISTS `S3Location` varchar(1024) DEFAULT NULL COMMENT 'S3 URL or file path for evidence'; 