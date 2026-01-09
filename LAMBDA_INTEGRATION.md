# Lambda Integration Guide

This guide explains how to integrate Lambda-based async document processing into your FastAPI backend.

## What Changed?

### Before (Blocking):
```
User uploads PDF → FastAPI processes (30-60s) → Returns result
```

### After (Async with Lambda):
```
User uploads PDF → FastAPI uploads to S3 (2s) → Returns immediately
S3 event → Lambda processes in background → Updates MongoDB
```

## Integration Steps

### Step 1: Deploy Lambda Function

1. Go to `lambda_folder/document-processor/`
2. Follow instructions in `README.md` to deploy
3. Configure S3 trigger for your bucket
4. Set environment variables in Lambda console

### Step 2: Update FastAPI Code

You have **two options**:

#### Option A: Replace existing service (Recommended for new deployments)

```bash
# Backup original files
cp app/components/rag/service.py app/components/rag/service_old.py
cp app/components/rag/routes.py app/components/rag/routes_old.py

# Replace with Lambda versions
cp app/components/rag/service_lambda.py app/components/rag/service.py
cp app/components/rag/routes_lambda.py app/components/rag/routes.py
```

#### Option B: Keep both versions (Recommended for gradual migration)

Update `app/main.py`:

```python
# Option 1: Use Lambda version
from app.components.rag.routes_lambda import router as RagRouter

# Option 2: Use original version
from app.components.rag.routes import router as RagRouter
```

Update `app/helpers/dependencies.py`:

```python
# Option 1: Use Lambda version
from app.components.rag.service_lambda import RagService

# Option 2: Use original version
from app.components.rag.service import RagService
```

### Step 3: Update Frontend

The frontend needs to:

1. **Poll for document status** after upload
2. **Show processing indicator** while Lambda is working
3. **Handle "processing" state** when querying

#### Example Frontend Code

**Upload with status polling:**

```javascript
// Upload document
const uploadResponse = await fetch('/api/rag/upload', {
  method: 'POST',
  body: formData,
  headers: { 'Authorization': `Bearer ${token}` }
});

const { document_id } = await uploadResponse.json();

// Poll for status
const pollStatus = async () => {
  const statusResponse = await fetch(`/api/rag/documents/${document_id}/status`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const status = await statusResponse.json();

  if (status.status === 'indexed') {
    console.log('Document ready!');
    return true;
  } else if (status.status === 'error') {
    console.error('Processing failed:', status.error_message);
    return false;
  } else {
    // Still processing, poll again in 3 seconds
    setTimeout(pollStatus, 3000);
  }
};

pollStatus();
```

**Updated document list UI:**

```javascript
const DocumentList = ({ documents }) => {
  return documents.map(doc => (
    <div key={doc.document_id}>
      <h3>{doc.filename}</h3>
      <Status status={doc.status} />
      {doc.status === 'processing' && <Spinner />}
      {doc.status === 'indexed' && <CheckIcon />}
      {doc.status === 'error' && <ErrorIcon message={doc.error_message} />}
    </div>
  ));
};
```

### Step 4: Environment Variables

Update `.env` file (if not already set):

```env
# S3 Configuration
BUCKET_NAME=your-bucket-name
S3_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# MongoDB (already configured)
MONGODB_URI=mongodb+srv://...

# Pinecone (already configured)
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...

# HuggingFace (for embeddings)
HUGGINGFACE_API_KEY=...
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Document Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Step 5: Test the Integration

1. **Test upload endpoint:**
   ```bash
   curl -X POST http://localhost:8000/rag/upload \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test.pdf"
   ```

   Should return immediately with `status: "processing"`

2. **Test status endpoint:**
   ```bash
   curl http://localhost:8000/rag/documents/{document_id}/status \
     -H "Authorization: Bearer $TOKEN"
   ```

3. **Check Lambda logs:**
   - Go to CloudWatch Logs
   - Look for `/aws/lambda/document-processor`
   - Verify processing completed

4. **Test query endpoint:**
   ```bash
   curl -X POST http://localhost:8000/rag/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is this document about?"}'
   ```

## API Changes

### New Endpoint

**GET `/rag/documents/{document_id}/status`**

Response:
```json
{
  "document_id": "uuid",
  "filename": "sample.pdf",
  "status": "indexed",  // or "processing" or "error"
  "chunk_count": 42,
  "upload_date": "2024-01-09T10:30:00",
  "processed_at": "2024-01-09T10:31:30",
  "error_message": null
}
```

### Modified Endpoint

**POST `/rag/upload`**

Response now returns immediately:
```json
{
  "success": true,
  "document_id": "uuid",
  "filename": "sample.pdf",
  "chunks_created": 0,  // Not yet processed
  "message": "Document uploaded successfully. Processing in background..."
}
```

### Updated Endpoint

**GET `/rag/documents`**

Response now includes status summary:
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "sample.pdf",
      "status": "indexed",
      "chunk_count": 42
    }
  ],
  "total": 1,
  "status_summary": {
    "processing": 0,
    "indexed": 1,
    "error": 0
  }
}
```

## Backward Compatibility

If you need to support both sync and async processing:

### Feature Flag Approach

```python
# In .env
USE_LAMBDA_PROCESSING=true

# In service.py
import os

USE_LAMBDA = os.getenv('USE_LAMBDA_PROCESSING', 'false').lower() == 'true'

if USE_LAMBDA:
    from app.components.rag.service_lambda import RagService
else:
    from app.components.rag.service import RagService
```

## Monitoring

### Check Processing Status

```python
# Add endpoint to check overall processing health
@router.get("/processing/stats")
async def get_processing_stats(service: RagService = Depends(get_rag_service)):
    processing_count = await service.db.documents.count_documents({"status": "processing"})
    indexed_count = await service.db.documents.count_documents({"status": "indexed"})
    error_count = await service.db.documents.count_documents({"status": "error"})

    return {
        "processing": processing_count,
        "indexed": indexed_count,
        "errors": error_count
    }
```

### Lambda Monitoring

- CloudWatch Logs: `/aws/lambda/document-processor`
- Metrics: Invocations, Duration, Errors, Throttles
- Set up CloudWatch Alarms for errors

## Troubleshooting

### Document stuck in "processing"

1. Check Lambda CloudWatch logs
2. Check if Lambda has correct permissions
3. Verify environment variables are set in Lambda
4. Check MongoDB connection from Lambda

### S3 trigger not working

1. Verify S3 event notification is configured
2. Check Lambda execution role has S3 read permissions
3. Verify prefix/suffix filters match uploaded files

### Can't query documents

1. Check document status is "indexed"
2. Verify Pinecone has the vectors
3. Check MongoDB has correct metadata

## Rollback Plan

If Lambda integration causes issues:

```bash
# Restore original files
cp app/components/rag/service_old.py app/components/rag/service.py
cp app/components/rag/routes_old.py app/components/rag/routes.py

# Restart FastAPI
# Documents will be processed synchronously again
```

## Next Steps

1. Deploy Lambda function
2. Update FastAPI code
3. Test with sample PDF
4. Update frontend to show processing status
5. Deploy to EC2
6. Monitor Lambda CloudWatch logs

## Support

For issues:
1. Check Lambda CloudWatch logs first
2. Verify S3 trigger configuration
3. Check environment variables in both FastAPI and Lambda
4. Test with a small PDF (< 1MB) first
