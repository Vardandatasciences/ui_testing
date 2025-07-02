// Script to test file uploads to the S3 microservice
require("dotenv").config();
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const axios = require('axios');

console.log('===============================================');
console.log('S3 MICROSERVICE UPLOAD TEST');
console.log('===============================================\n');

// Create a test file
const testFilePath = path.join(__dirname, 'test-upload.txt');
const testContent = 'This is a test file for S3 upload. Generated at ' + new Date().toISOString();

async function testUpload() {
  try {
    // Create test file
    fs.writeFileSync(testFilePath, testContent);
    console.log('✅ Test file created');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fs.createReadStream(testFilePath));
    formData.append('userId', 'test-user');
    formData.append('fileName', 'test-upload.txt');
    formData.append('test_param', 'test_value');
    
    console.log('Uploading test file to S3 microservice...');
    
    // Upload file
    const port = process.env.AWS_PORT || 5000;
    const response = await axios.post(`http://localhost:${port}/api/upload`, formData, {
      headers: {
        ...formData.getHeaders()
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });
    
    if (response.data.success) {
      console.log('✅ File upload successful!');
      console.log(`File URL: ${response.data.file.url}`);
      console.log(`File ID: ${response.data.file.id}`);
      
      // Get file metadata
      console.log('\nFetching file metadata...');
      const metadataResponse = await axios.get(`http://localhost:${port}/api/file/${response.data.file.id}`);
      
      if (metadataResponse.data.success) {
        console.log('✅ File metadata retrieved successfully');
        console.log(JSON.stringify(metadataResponse.data.file, null, 2));
      } else {
        console.error('❌ Failed to retrieve file metadata');
      }
      
      // Delete the file
      console.log('\nDeleting file from S3...');
      const deleteResponse = await axios.delete(`http://localhost:${port}/api/file/${response.data.file.id}`);
      
      if (deleteResponse.data.success) {
        console.log('✅ File deleted successfully');
      } else {
        console.error('❌ Failed to delete file');
      }
    } else {
      console.error('❌ File upload failed');
      console.error(`Error: ${response.data.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error('❌ Error during file upload test:');
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error(`Status: ${error.response.status}`);
      console.error(`Response data: ${JSON.stringify(error.response.data)}`);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
      console.error('Make sure the S3 microservice is running:');
      console.error('node start-s3-service.js');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error(`Error message: ${error.message}`);
    }
  } finally {
    // Clean up test file if it exists
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
      console.log('\n✅ Test file cleaned up');
    }
  }
}

testUpload(); 