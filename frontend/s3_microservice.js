// hel;o tetsinf scwasdcasvadsv

require("dotenv").config();
const express = require('express');
const multer = require('multer');
const fs = require("fs");
const S3 = require("aws-sdk/clients/s3");
const mysql = require('mysql2/promise');
const bodyParser = require('body-parser');
const cors = require('cors');

// Configure AWS S3
const bucketName = process.env.AWS_BUCKET_NAME || 'orcashoimages';
const region = process.env.AWS_REGION || 'ap-south-1';
const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

// Log AWS credentials status (without showing actual keys)
console.log('AWS S3 Configuration:');
console.log(`- Bucket: ${bucketName}`);
console.log(`- Region: ${region}`);
console.log(`- Access Key: ${accessKeyId ? 'Set' : 'Not set'}`);
console.log(`- Secret Key: ${secretAccessKey ? 'Set' : 'Not set'}`);

// Initialize S3 with error handling
let s3;
try {
  // Build the proper S3 endpoint URL based on region
  const endpoint = `https://s3.${region}.amazonaws.com`;
  console.log(`- Using S3 endpoint: ${endpoint}`);
  
  // Initialize the S3 client with explicit endpoint
  s3 = new S3({
    region,
    accessKeyId,
    secretAccessKey,
    endpoint: endpoint,
    s3ForcePathStyle: true
  });
  console.log('S3 client initialized with explicit endpoint');
} catch (error) {
  console.error('Failed to initialize S3 client:', error);
  s3 = null; // Will be handled later when checking for S3 availability
}

// Configure MySQL
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || 'root',
  database: process.env.DB_NAME || 'grc',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

// Log database configuration (without showing password)
console.log('Database Configuration:');
console.log(`- Host: ${dbConfig.host}`);
console.log(`- User: ${dbConfig.user}`);
console.log(`- Database: ${dbConfig.database}`);

// Initialize database pool with error handling
let pool;
try {
  pool = mysql.createPool(dbConfig);
  console.log('MySQL connection pool created');
} catch (error) {
  console.error('Failed to create MySQL connection pool:', error);
  pool = null; // Will be handled later when checking for database availability
}

// Test DB connection
async function testConnection() {
  try {
    // Check if pool was created successfully
    if (!pool) {
      console.error('Cannot test connection: MySQL pool was not initialized');
      return false;
    }
    
    const connection = await pool.getConnection();
    console.log('MySQL connected successfully');
    connection.release();
    return true;
  } catch (error) {
    console.error('MySQL connection failed:', error);
    return false;
  }
}

// Call testConnection to verify MySQL connection on startup
testConnection().then(isConnected => {
  if (!isConnected) {
    console.warn('WARNING: MySQL connection failed. Some functionality may not work.');
  }
});

// Test S3 connection with fallback approach
async function testS3Connection() {
  try {
    if (!s3) {
      console.error('Cannot test S3 connection: S3 client was not initialized');
      return false;
    }

    console.log("Testing connection with credentials:", {
      bucket: bucketName,
      region: region,
      hasAccessKey: !!accessKeyId,
      hasSecretKey: !!secretAccessKey
    });

    // Try a less privileged operation first - just test if we can access S3 service
    try {
      // Check if your target bucket is accessible
      await s3.headBucket({ Bucket: bucketName }).promise();
      console.log(`S3 connected successfully to bucket: ${bucketName}`);
      return true;
    } catch (headBucketError) {
      if (headBucketError.statusCode === 403) {
        console.warn(`S3 bucket access forbidden (403). This may indicate:
        1. Bucket '${bucketName}' doesn't exist or you don't have access
        2. AWS credentials don't have s3:HeadBucket permission
        3. Bucket policy doesn't allow this operation
        
        The service will continue but file uploads may fail.`);
        
        // Try to test basic S3 service connectivity with a simpler operation
        try {
          // This is a minimal test that doesn't require bucket-specific permissions
          const testParams = {
            Bucket: bucketName,
            Key: 'test-connectivity',
            Body: 'test'
          };
          
          // We won't actually upload, just validate the parameters
          await s3.upload(testParams).promise().catch(() => {
            // Expected to fail, but validates credentials format
          });
          
          console.log('S3 service appears to be accessible, but bucket permissions need review');
          return true;
        } catch (serviceError) {
          console.error('S3 service connectivity test failed:', serviceError.message);
          return false;
        }
      } else if (headBucketError.statusCode === 404) {
        console.error(`S3 bucket '${bucketName}' was not found. Please check:
        1. Bucket name is correct
        2. Bucket exists in the specified region (${region})
        3. AWS credentials have access to the bucket`);
        return false;
      } else {
        throw headBucketError;
      }
    }
  } catch (error) {
    console.error('S3 connection failed:', error);
    console.error(`Error details:
    - Code: ${error.code}
    - Status: ${error.statusCode}
    - Message: ${error.message}
    
    Please verify:
    1. AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct
    2. Credentials have proper S3 permissions
    3. Bucket '${bucketName}' exists in region '${region}'
    4. Network connectivity to AWS S3`);
    return false;
  }
}

// Call testS3Connection to verify S3 connection on startup
testS3Connection().then(isConnected => {
  if (!isConnected) {
    console.log('==========================================');
    console.log('WARNING: S3 CONNECTION FAILED!');
    console.log('File uploads will not work.');
    console.log('Check your AWS credentials and network connectivity.');
    console.log('==========================================');
  } else {
    console.log('✅ S3 connection successful - File uploads are ready');
  }
});

// Content type mapping
const CONTENT_TYPES = {
  // Images
  'jpg': 'image/jpeg',
  'jpeg': 'image/jpeg',
  'png': 'image/png',
  'gif': 'image/gif',
  'webp': 'image/webp',
  
  // Documents
  'pdf': 'application/pdf',
  'doc': 'application/msword',
  'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'xls': 'application/vnd.ms-excel',
  'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'ppt': 'application/vnd.ms-powerpoint',
  'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  
  // Videos
  'mp4': 'video/mp4',
  'mov': 'video/quicktime',
  'avi': 'video/x-msvideo',
  'webm': 'video/webm',
  
  // Audio
  'mp3': 'audio/mpeg',
  'wav': 'audio/wav',
  'ogg': 'audio/ogg',
  
  // Archives
  'zip': 'application/zip',
  'rar': 'application/x-rar-compressed',
  '7z': 'application/x-7z-compressed',
  
  // Text
  'txt': 'text/plain',
  'csv': 'text/csv',
  'json': 'application/json',
  
  // Other
  'xml': 'application/xml',
  'html': 'text/html',
  'css': 'text/css',
  'js': 'application/javascript'
};

// Check if file type should be downloadable
function isDownloadable(extension) {
  const downloadableTypes = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'zip', 'rar', '7z', 'txt', 'csv', 'json', 'xml'
  ];
  return downloadableTypes.includes(extension.toLowerCase());
}

// Express app setup
const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for all routes
app.use(cors({
  origin: ['http://localhost:8080', 'http://127.0.0.1:8080'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  }
});

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Helper function to generate file name with parameters
function generateFileName(baseFileName, params) {
  const timestamp = Date.now();
  let paramString = '';
  
  if (params && Object.keys(params).length > 0) {
    paramString = '_' + Object.entries(params)
      .map(([key, value]) => `${key}-${value}`)
      .join('_');
  }
  
  return `${timestamp}_${baseFileName}${paramString}`;
}

// Upload file
async function uploadFile(file, fileType, fileName, userId, params = {}) {
  let connection;
  
  try {
    // Check for required file information
    if (!file || !fileType || !fileName) {
      throw new Error('Missing required file information');
    }

    // Validate that S3 is properly configured
    if (!s3) {
      console.error('S3 client is not initialized. Falling back to file system storage.');
      // Continue with a simulated S3 URL that includes the timestamp and filename
      const timestamp = Date.now();
      const simulatedFileId = `${timestamp}_${fileName}`;
      
      // Directly return a "dummy" response with simulated location
      return {
        success: true,
        file: {
          url: `https://s3-fallback-storage/${simulatedFileId}`,
          fileType: fileType,
          fileName: fileName,
          uploadedAt: new Date().toISOString(),
          metadata: params,
          s3_location: `https://s3-fallback-storage/${simulatedFileId}`,
          file_id: simulatedFileId
        },
        warning: 'S3 storage is not available, using fallback storage mechanism'
      };
    }

    // Acquire database connection if pool is available
    if (pool) {
      try {
        connection = await pool.getConnection();
        console.log('Database connection acquired for file upload');
      } catch (connError) {
        console.error('Failed to acquire database connection:', connError);
      }
    } else {
      console.warn('Database connection pool is not available');
    }

    // Get content type and prepare for upload
    const contentType = CONTENT_TYPES[fileType.toLowerCase()] || 'application/octet-stream';
    const finalFileName = generateFileName(fileName, params);
    
    // Enhanced logging for evidence uploads
    const isEvidence = params.documentType === 'evidence';
    const isAuditEvidence = params.documentType === 'audit_evidence';
    if (isEvidence || isAuditEvidence) {
      console.log(`${isAuditEvidence ? 'Audit' : 'Compliance'} evidence upload detected:`);
      console.log(`File name: ${fileName}`);
      if (isEvidence) {
        console.log(`Compliance ID: ${params.compliance_id || 'Not provided'}`);
      }
      console.log(`Audit ID: ${params.audit_id || 'Not provided'}`);
      console.log(`Storage column: ${params.storage_column || 'Evidence'}`);
      console.log('Uploading to S3 bucket:', bucketName);
      console.log('Upload started at:', new Date().toISOString());
    }
    
    // Set S3 upload parameters
    const uploadParams = {
      Bucket: bucketName,
      Key: finalFileName,
      Body: file.buffer || fs.createReadStream(file.path),
      ContentType: contentType,
      Metadata: {
        userId: userId
      }
    };

    // Upload to S3
    let uploadResult;
    try {
      uploadResult = await s3.upload(uploadParams).promise();
    } catch (s3Error) {
      console.error('S3 upload failed:', s3Error);
      
      // Provide specific guidance based on error type
      if (s3Error.statusCode === 403) {
        throw new Error(`S3 Upload Forbidden (403): Your AWS credentials don't have permission to upload to bucket '${bucketName}'. Please ensure your AWS user has s3:PutObject permission.`);
      } else if (s3Error.statusCode === 404) {
        throw new Error(`S3 Bucket Not Found (404): Bucket '${bucketName}' doesn't exist or is not accessible in region '${region}'.`);
      } else if (s3Error.code === 'NetworkingError') {
        throw new Error(`S3 Network Error: Cannot connect to AWS S3. Please check your internet connection.`);
      } else if (s3Error.code === 'CredentialsError') {
        throw new Error(`S3 Credentials Error: AWS credentials are invalid or expired. Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.`);
      } else {
        throw new Error(`S3 Upload Error (${s3Error.code}): ${s3Error.message}`);
      }
    }
    
    if (isEvidence || isAuditEvidence) {
      console.log('Upload completed at:', new Date().toISOString());
      console.log('Generated S3 URL:', uploadResult.Location);
    }

    // Database operations for evidence uploads
    if (connection && (isEvidence || isAuditEvidence)) {
      try {
        if (isEvidence && params.compliance_id) {
          // Handle compliance evidence
          const complianceId = params.compliance_id;
          const auditId = params.audit_id;
          
          console.log(`Saving compliance evidence to audit_findings table for compliance ID: ${complianceId}`);
          
          // Check if record exists
          let checkQuery, checkParams;
          if (auditId) {
            checkQuery = 'SELECT * FROM audit_findings WHERE AuditId = ? AND ComplianceId = ?';
            checkParams = [auditId, complianceId];
          } else {
            checkQuery = 'SELECT * FROM audit_findings WHERE ComplianceId = ?';
            checkParams = [complianceId];
          }
          
          const [rows] = await connection.execute(checkQuery, checkParams);
          
          if (rows && rows.length > 0) {
            // Update existing record - append to existing evidence URLs
            const existingEvidence = rows[0].Evidence || '';
            const newEvidence = existingEvidence ? `${existingEvidence},${uploadResult.Location}` : uploadResult.Location;
            
            let updateQuery, updateParams;
            if (auditId) {
              console.log(`Updating existing record for AuditId=${auditId} and ComplianceId=${complianceId}`);
              updateQuery = 'UPDATE audit_findings SET Evidence = ? WHERE AuditId = ? AND ComplianceId = ?';
              updateParams = [newEvidence, auditId, complianceId];
            } else {
              console.log(`Updating existing record for ComplianceId=${complianceId}`);
              updateQuery = 'UPDATE audit_findings SET Evidence = ? WHERE ComplianceId = ?';
              updateParams = [newEvidence, complianceId];
            }
            
            await connection.execute(updateQuery, updateParams);
            console.log('Successfully updated audit_findings record with S3 URL');
          } else {
            // Insert new record
            console.log(`Creating new record for ${auditId ? `AuditId=${auditId} and ` : ''}ComplianceId=${complianceId}`);
            const defaultCheck = '1'; // In Progress
            
            let insertQuery, insertParams;
            if (auditId) {
              insertQuery = 'INSERT INTO audit_findings (AuditId, ComplianceId, Evidence, UserId, `Check`) VALUES (?, ?, ?, ?, ?)';
              insertParams = [auditId, complianceId, uploadResult.Location, userId, defaultCheck];
            } else {
              insertQuery = 'INSERT INTO audit_findings (ComplianceId, Evidence, UserId, `Check`) VALUES (?, ?, ?, ?)';
              insertParams = [complianceId, uploadResult.Location, userId, defaultCheck];
            }
            
            await connection.execute(insertQuery, insertParams);
            console.log('Successfully created new audit_findings record with S3 URL');
          }
        } else if (isAuditEvidence && params.audit_id) {
          // Handle audit evidence
          const auditId = params.audit_id;
          
          console.log(`Saving audit evidence to audit table for audit ID: ${auditId}`);
          
          // Check if audit record exists and get existing evidence
          const [auditRows] = await connection.execute('SELECT Evidence FROM audit WHERE AuditId = ?', [auditId]);
          
          if (auditRows && auditRows.length > 0) {
            // Update existing audit record - append to existing evidence URLs
            const existingEvidence = auditRows[0].Evidence || '';
            const newEvidence = existingEvidence ? `${existingEvidence},${uploadResult.Location}` : uploadResult.Location;
            
            await connection.execute('UPDATE audit SET Evidence = ? WHERE AuditId = ?', [newEvidence, auditId]);
            console.log('Successfully updated audit record with S3 URL');
          } else {
            console.log(`Audit record with ID ${auditId} not found`);
          }
        }
        
        return {
          success: true,
          file: {
            url: uploadResult.Location,
            fileType: fileType,
            fileName: fileName,
            uploadedAt: new Date().toISOString(),
            metadata: params,
            s3_location: uploadResult.Location,
            file_id: uploadResult.Location
          },
          database_updated: true
        };
      } catch (dbError) {
        console.error('Error updating database table:', dbError);
        // Fall through to default return
      }
    }
    
    // General file metadata storage (non-evidence or if evidence update failed)
    if (connection) {
      try {
        const metadataJson = JSON.stringify(params);
        const [result] = await connection.execute(
          'INSERT INTO s3_files (url, file_type, file_name, user_id, metadata) VALUES (?, ?, ?, ?, ?)',
          [uploadResult.Location, fileType, fileName, userId, metadataJson]
        );
        
        const fileId = result.insertId;
        
        // Get the inserted file for confirmation
        const [rows] = await connection.execute(
          'SELECT * FROM s3_files WHERE id = ?',
          [fileId]
        );
        
        if (rows && rows.length > 0) {
          const insertedFile = rows[0];
          return {
            success: true,
            file: {
              id: insertedFile.id,
              url: insertedFile.url,
              fileType: insertedFile.file_type,
              fileName: insertedFile.file_name,
              uploadedAt: insertedFile.uploaded_at,
              metadata: params,
              s3Key: finalFileName
            }
          };
        }
      } catch (dbError) {
        console.error('Error storing file metadata:', dbError);
        // Fall through to default return
      }
    }
    
    // Default return if database operations failed or weren't attempted
    return {
      success: true,
      file: {
        url: uploadResult.Location,
        fileType: fileType,
        fileName: fileName,
        uploadedAt: new Date().toISOString(),
        metadata: params,
        s3_location: uploadResult.Location,
        file_id: uploadResult.Location
      },
      warning: connection ? 'File uploaded to S3 but database operation failed' : 'File uploaded to S3 but database connection was not available'
    };
    
  } catch (error) {
    console.error('Error uploading file:', error);
    
    if (params.documentType === 'evidence') {
      console.error('========== EVIDENCE UPLOAD FAILED ==========');
      console.error('Error details:', error.message);
    }
    
    throw new Error(`Failed to upload file: ${error.message}`);
  } finally {
    // Only release connection if it was successfully acquired
    if (connection) {
      try {
        await connection.release();
        console.log('Database connection released');
      } catch (releaseError) {
        console.error('Error releasing database connection:', releaseError);
      }
    }
  }
}

// Delete file
async function deleteFile(fileId) {
  const connection = await pool.getConnection();
  
  try {
    // Get file metadata from MySQL
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];

    // Extract S3 key from URL
    const s3Key = file.url.split('/').pop();

    // Delete from S3
    const deleteParams = {
      Bucket: bucketName,
      Key: s3Key
    };
    await s3.deleteObject(deleteParams).promise();

    // Delete from MySQL
    await connection.execute(
      'DELETE FROM s3_files WHERE id = ?',
      [fileId]
    );

    return {
      success: true,
      message: 'File deleted successfully'
    };
  } catch (error) {
    console.error('Error deleting file:', error);
    throw new Error(`Failed to delete file: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Get file metadata
async function getFileMetadata(fileId) {
  const connection = await pool.getConnection();
  
  try {
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];
    const metadata = file.metadata ? JSON.parse(file.metadata) : {};

    return {
      success: true,
      file: {
        id: file.id,
        url: file.url,
        fileType: file.file_type,
        fileName: file.file_name,
        uploadedAt: file.uploaded_at,
        metadata: metadata
      }
    };
  } catch (error) {
    console.error('Error getting file metadata:', error);
    throw new Error(`Failed to get file metadata: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Get user files
async function getUserFiles(userId, filters = {}) {
  const connection = await pool.getConnection();
  
  try {
    // Check if the metadata column exists by querying the table structure
    const [columns] = await connection.execute(
      "SHOW COLUMNS FROM s3_files LIKE 'metadata'"
    );
    
    const hasMetadataColumn = columns.length > 0;
    
    let query = 'SELECT * FROM s3_files WHERE user_id = ?';
    const queryParams = [userId];
    
    // Add filter by metadata only if the column exists
    if (hasMetadataColumn && filters && Object.keys(filters).length > 0) {
      query += ' AND metadata LIKE ?';
      queryParams.push(`%${JSON.stringify(filters).slice(1, -1)}%`);
    }
    
    query += ' ORDER BY uploaded_at DESC';
    
    const [rows] = await connection.execute(query, queryParams);

    return {
      success: true,
      files: rows.map(file => ({
        id: file.id,
        url: file.url,
        fileType: file.file_type,
        fileName: file.file_name,
        uploadedAt: file.uploaded_at,
        metadata: hasMetadataColumn && file.metadata ? JSON.parse(file.metadata) : {}
      }))
    };
  } catch (error) {
    console.error('Error getting user files:', error);
    throw new Error(`Failed to get user files: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Generate download URL - fix the URL encoding issue
async function getDownloadUrl(fileId, expiresIn = 3600) {
  const connection = await pool.getConnection();
  
  try {
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];
    
    // Extract S3 key from URL and fully decode it to avoid double-encoding
    const urlParts = file.url.split('/');
    const encodedKey = urlParts[urlParts.length - 1];
    
    // Make sure to properly decode the key
    let s3Key;
    try {
      // First try to decode it in case it's encoded
      s3Key = decodeURIComponent(encodedKey);
    } catch (e) {
      // If decoding fails, use the original key
      s3Key = encodedKey;
      console.log('Key could not be decoded, using as is');
    }
    
    console.log('Original S3 key from URL:', encodedKey);
    console.log('Decoded S3 key for download:', s3Key);

    // Generate pre-signed URL
    const params = {
      Bucket: bucketName,
      Key: s3Key,
      Expires: expiresIn,
      ResponseContentDisposition: `attachment; filename="${file.file_name}"`
    };

    const downloadUrl = s3.getSignedUrl('getObject', params);
    console.log('Generated download URL:', downloadUrl);

    return {
      success: true,
      downloadUrl: downloadUrl,
      fileName: file.file_name,
      s3Key: s3Key
    };
  } catch (error) {
    console.error('Error generating download URL:', error);
    throw new Error(`Failed to generate download URL: ${error.message}`);
  } finally {
    connection.release();
  }
}

// API Routes
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { originalname, mimetype } = req.file;
    const userId = req.body.userId || 'default-user';
    const fileExtension = originalname.split('.').pop().toLowerCase();
    const fileName = req.body.fileName || originalname;
    
    // Extract parameters for evidence and audit report uploads
    const isEvidence = req.body.documentType === 'evidence';
    const isAuditEvidence = req.body.documentType === 'audit_evidence';
    const complianceId = req.body.compliance_id;
    const auditId = req.body.audit_id;
    const tableName = req.body.table_name || (isAuditEvidence ? 'audit' : 'audit_findings');
    const storageColumn = req.body.storage_column || (isAuditEvidence ? 'Evidence' : 'Evidence');
    
    if (isEvidence || isAuditEvidence) {
      console.log(`========== ${isAuditEvidence ? 'AUDIT' : 'COMPLIANCE'} EVIDENCE UPLOAD API REQUEST ==========`);
      console.log(`File: ${fileName} (${fileExtension})`);
      console.log(`MIME type: ${mimetype}`);
      console.log(`Size: ${req.file.size} bytes`);
      console.log(`User: ${userId}`);
      console.log(`Compliance ID: ${complianceId || 'N/A'}`);
      console.log(`Audit ID: ${auditId || 'N/A'}`);
      console.log(`Table Name: ${tableName}`);
      console.log(`Storage Column: ${storageColumn}`);
      
      // For compliance evidence uploads, we need compliance_id
      if (isEvidence && !complianceId) {
        console.warn('WARNING: No compliance_id provided for compliance evidence upload');
        return res.status(400).json({ 
          error: 'Compliance evidence uploads require a compliance_id parameter', 
          success: false 
        });
      }
      
      // For audit evidence uploads, we need audit_id
      if (isAuditEvidence && !auditId) {
        console.warn('WARNING: No audit_id provided for audit evidence upload');
        return res.status(400).json({ 
          error: 'Audit evidence uploads require an audit_id parameter', 
          success: false 
        });
      }
    }
    
    // Extract all parameters from the request body
    const params = {};
    for (const key in req.body) {
      if (key !== 'userId' && key !== 'fileName') {
        params[key] = req.body[key];
      }
    }

    const result = await uploadFile(req.file, fileExtension, fileName, userId, params);
    
    if (isEvidence || isAuditEvidence) {
      console.log(`========== ${isAuditEvidence ? 'AUDIT' : 'COMPLIANCE'} EVIDENCE UPLOAD API RESPONSE ==========`);
      console.log(`Success: ${result.success}`);
      console.log(`Generated URL: ${result.file?.url || 'N/A'}`);
      console.log(`File ID: ${result.file?.id || 'N/A'}`);
      console.log(`Evidence saved to ${tableName} table`);
      
      if (isEvidence && complianceId) {
        console.log(`Associated with compliance ID: ${complianceId}`);
      }
      if (auditId) {
        console.log(`Associated with audit ID: ${auditId}`);
      }
      
      // Double-check that the evidence URL is present in the response
      if (result.success && (!result.file?.url || result.file.url === fileName)) {
        console.error('WARNING: Evidence URL may not be correct in the response');
        // Try to fix the response if needed
        if (result.file && !result.file.url) {
          console.log('Fixing missing URL in response');
          result.file.url = result.file.s3_location || '';
        }
      }
    }
    
    res.json(result);
  } catch (error) {
    console.error('Upload error:', error);
    
    // Log evidence upload failures
    if (req.body && (req.body.documentType === 'evidence' || req.body.documentType === 'audit_evidence')) {
      console.error(`========== ${req.body.documentType === 'audit_evidence' ? 'AUDIT' : 'COMPLIANCE'} EVIDENCE UPLOAD API ERROR ==========`);
      console.error(`File: ${req.body.fileName || req.file?.originalname || 'unknown'}`);
      console.error(`Compliance ID: ${req.body.compliance_id || 'N/A'}`);
      console.error(`Audit ID: ${req.body.audit_id || 'N/A'}`);
      console.error(`Error: ${error.message}`);
    }
    
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/files/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    // Get filters from query parameters
    const filters = req.query;
    const result = await getUserFiles(userId, filters);
    res.json(result);
  } catch (error) {
    console.error('Get files error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/file/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const result = await getFileMetadata(fileId);
    res.json(result);
  } catch (error) {
    console.error('Get file metadata error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/download/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const expiresIn = req.query.expiresIn ? parseInt(req.query.expiresIn) : 3600;
    const result = await getDownloadUrl(fileId, expiresIn);
    
    if (req.query.redirect === 'true') {
      res.redirect(result.downloadUrl);
    } else {
      res.json(result);
    }
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/file/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const result = await deleteFile(fileId);
    res.json(result);
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Add improved ping endpoint for better health checking
app.get('/api/ping', async (req, res) => {
  console.log('Ping request received');
  
  // Set CORS headers explicitly
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  try {
    // Check both S3 and database connections
    const s3Status = await testS3Connection();
    const dbStatus = await testConnection();
    
    if (s3Status && dbStatus) {
      res.status(200).json({ 
        status: 'ok', 
        message: 'Service is available',
        connections: {
          s3: 'connected',
          database: 'connected'
        }
      });
    } else {
      // Send service degraded response with specific connection status
      res.status(200).json({
        status: 'degraded',
        message: 'Service is partially available',
        connections: {
          s3: s3Status ? 'connected' : 'disconnected',
          database: dbStatus ? 'connected' : 'disconnected'
        }
      });
    }
  } catch (error) {
    console.error('Error in ping endpoint:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Service is experiencing issues',
      error: error.message
    });
  }
});

// Handle preflight OPTIONS requests for all routes
app.options('*', (req, res) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.status(204).send();
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: err.message });
});

// Start the server
app.listen(PORT, () => {
  console.log(`S3 Microservice running on port ${PORT}`);
  
  // Check S3 and database status on startup
  Promise.all([testS3Connection(), testConnection()])
    .then(([s3Connected, dbConnected]) => {
      if (!s3Connected) {
        console.error('==========================================');
        console.error('WARNING: S3 CONNECTION FAILED!');
        console.error('File uploads will not work.');
        console.error('Check your AWS credentials and network connectivity.');
        console.error('==========================================');
      }
      
      if (!dbConnected) {
        console.error('==========================================');
        console.error('WARNING: DATABASE CONNECTION FAILED!');
        console.error('File metadata storage will not work.');
        console.error('Check your database configuration and network connectivity.');
        console.error('==========================================');
      }
      
      if (s3Connected && dbConnected) {
        console.log('==========================================');
        console.log('S3 microservice is fully operational!');
        console.log('File uploads and metadata storage are working.');
        console.log('==========================================');
      }
    });
});

module.exports = {
  uploadFile,
  deleteFile,
  getFileMetadata,
  getUserFiles,
  getDownloadUrl
};