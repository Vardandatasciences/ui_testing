# S3 Microservice Setup

This microservice handles file uploads to Amazon S3 for the GRC application.

## Prerequisites

- Node.js 14+ installed
- MySQL database
- Amazon S3 bucket with proper permissions

## Setup

1. Install dependencies:
   ```
   cp s3-microservice-package.json package.json
   npm install
   ```

2. Create a `.env` file in the `frontend` directory with the following content:

```
# AWS S3 Configuration
AWS_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=your-aws-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_PORT=5000

# Database Configuration
DB_HOST=localhost
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=grc
```

3. Replace the placeholder values with your actual AWS S3 credentials and database information.

4. Make sure your database has the `s3_files` table with the following structure:

```sql
CREATE TABLE IF NOT EXISTS s3_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  url VARCHAR(255) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  user_id VARCHAR(100) NOT NULL,
  metadata JSON,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running the Microservice

Start the microservice with:

```
npm start
```

Or directly:

```
node start-s3-service.js
```

The service will run on port 5000 by default (or the port specified in your .env file).

## API Endpoints

- `POST /api/upload`: Upload a file to S3
- `GET /api/files/:userId`: Get all files for a user
- `GET /api/file/:fileId`: Get file metadata
- `GET /api/download/:fileId`: Get a download URL for a file
- `DELETE /api/file/:fileId`: Delete a file
- `GET /api/health`: Check the health of the service

## Verification Scripts

We've included several scripts to help you verify your configuration:

1. **check-s3-service.js**: Checks if the S3 microservice is running
   ```
   npm run check
   ```

2. **verify-aws-config.js**: Verifies your AWS S3 credentials and bucket configuration
   ```
   npm run verify-aws
   ```

3. **verify-db-config.js**: Verifies your MySQL database connection and creates the necessary table if it doesn't exist
   ```
   npm run verify-db
   ```

4. **troubleshoot-s3.js**: Comprehensive troubleshooting script that checks all aspects of the S3 microservice
   ```
   npm run troubleshoot
   ```

5. **test-upload.js**: Tests file upload, retrieval, and deletion
   ```
   npm run test-upload
   ```

## Troubleshooting

If you encounter issues with file uploads:

1. **S3 Microservice Not Running**
   - Check that the S3 microservice is running on port 5000
   - Run `npm run check` to verify the service status
   - If not running, start it with `npm start`

2. **AWS Credentials Issues**
   - Run `npm run verify-aws` to check your AWS credentials
   - Make sure your AWS credentials have permissions to access the S3 bucket
   - Verify that the bucket name is correct and the bucket exists
   - Check that your IAM user has the following permissions:
     - s3:PutObject
     - s3:GetObject
     - s3:DeleteObject
     - s3:ListBucket

3. **Database Connection Issues**
   - Run `npm run verify-db` to check your database connection
   - Make sure MySQL is running and accessible
   - Verify that the database exists and the user has proper permissions
   - Check if the s3_files table exists with the correct structure

4. **Upload Errors in CreatePolicy.vue**
   - Check the browser console for specific error messages
   - Verify that the upload URL is correct (http://localhost:5000/api/upload)
   - Make sure the FormData object is correctly formatted with 'file' as the key for the file

5. **Common Error Messages**
   - "Access Denied" - Check your AWS credentials and bucket permissions
   - "No Such Bucket" - Verify that the bucket name is correct and exists
   - "Connection Refused" - Make sure the S3 microservice is running
   - "Database Connection Failed" - Check your database configuration

6. **Checking Logs**
   - Look for error messages in the console when running the S3 microservice
   - Check the browser console for network request errors
   - Examine the response from the S3 microservice for specific error details 