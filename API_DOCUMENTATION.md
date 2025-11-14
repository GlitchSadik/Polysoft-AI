# API Documentation

API reference for the RAG-based Company Policy Chatbot.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication is required. For production, implement API key or OAuth.

## Endpoints

### 1. Health Check

Check API and database connectivity.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "chromadb": "connected"
}
```

### 2. Upload Document

Upload a PDF document for processing and indexing.

**Endpoint:** `POST /docs/upload`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload with key `file`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/docs/upload" \
  -F "file=@company_policy.pdf"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document 'company_policy.pdf' processed successfully",
  "document_id": 1,
  "document_name": "company_policy.pdf",
  "line_count": 450,
  "character_count": 25680,
  "chunk_count": 32
}
```

**Error Response:**
```json
{
  "detail": "Only PDF and TXT files are allowed"
}
```

**Status Codes:**
- `200 OK` - Document uploaded and processed successfully
- `400 Bad Request` - Invalid file type
- `413 Payload Too Large` - File exceeds maximum size (50MB)
- `500 Internal Server Error` - Processing error

### 3. List Documents

Get a list of all uploaded documents.

**Endpoint:** `GET /docs/list`

**cURL Example:**
```bash
curl "http://localhost:8000/docs/list"
```

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "name": "company_policy.pdf",
      "path": "storage/docs/company_policy.pdf",
      "created_at": "2024-01-15T10:30:00",
      "chunk_count": 32
    },
    {
      "id": 2,
      "name": "employee_handbook.pdf",
      "path": "storage/docs/employee_handbook.pdf",
      "created_at": "2024-01-16T14:20:00",
      "chunk_count": 45
    }
  ]
}
```

### 4. Delete Document

Delete a document and all its associated chunks.

**Endpoint:** `DELETE /docs/{document_id}`

**Parameters:**
- `document_id` (path parameter) - The ID of the document to delete

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/docs/1"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document and associated chunks deleted successfully"
}
```

**Error Response:**
```json
{
  "detail": "Document not found"
}
```

**Status Codes:**
- `200 OK` - Document deleted successfully
- `404 Not Found` - Document with specified ID doesn't exist

### 5. Chat Query

Send a message and get an AI-generated response with citations.

**Endpoint:** `POST /chat/query`

**Request Body:**
```json
{
  "message": "What is the remote work policy?",
  "conversation_id": null
}
```

**Parameters:**
- `message` (string, required) - The user's question
- `conversation_id` (integer, optional) - ID of existing conversation to continue. If `null`, creates a new conversation.

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the remote work policy?",
    "conversation_id": null
  }'
```

**Response:**
```json
{
  "conversation_id": 1,
  "answer": "According to the company policy, employees may work remotely up to 3 days per week with manager approval [1]. Remote work requests must be submitted at least 48 hours in advance [2].",
  "citations": [
    {
      "doc_name": "company_policy.pdf",
      "section_title": "5. Remote Work Policy",
      "start_line": 125,
      "end_line": 138,
      "snippet": "Employees may work remotely up to 3 days per week with prior manager approval. All remote work arrangements must maintain productivity standards..."
    },
    {
      "doc_name": "company_policy.pdf",
      "section_title": "5.2 Remote Work Procedures",
      "start_line": 145,
      "end_line": 152,
      "snippet": "Remote work requests must be submitted at least 48 hours in advance through the HR portal. Managers will review and approve based on business needs..."
    }
  ]
}
```

**Citation Format:**
- The `answer` field contains citation markers like `[1]`, `[2]`
- The `citations` array contains only sources actually referenced in the answer (smart filtering)
- Each citation includes:
  - `doc_name`: Source document filename
  - `section_title`: Section heading (if detected)
  - `start_line`: Starting line number in original document
  - `end_line`: Ending line number
  - `snippet`: Relevant text excerpt (starts at sentence boundary for readability)

**Status Codes:**
- `200 OK` - Response generated successfully
- `404 Not Found` - Conversation ID doesn't exist
- `500 Internal Server Error` - Processing error

### 6. List Conversations

Get all conversations with metadata.

**Endpoint:** `GET /chat/conversations`

**cURL Example:**
```bash
curl "http://localhost:8000/chat/conversations"
```

**Response:**
```json
{
  "conversations": [
    {
      "id": 1,
      "title": "What is the remote work policy?",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:35:00"
    },
    {
      "id": 2,
      "title": "Tell me about vacation days",
      "created_at": "2024-01-16T14:20:00",
      "updated_at": "2024-01-16T14:25:00"
    }
  ]
}
```

Notes:
- `title` is auto-generated from the first 50 characters of the first user message
- `updated_at` is updated every time a new message is added
- Conversations are ordered by `updated_at` descending

### 7. Get Conversation Messages

Retrieve all messages in a specific conversation.

**Endpoint:** `GET /chat/conversations/{conversation_id}/messages`

**Parameters:**
- `conversation_id` (path parameter) - The ID of the conversation

**cURL Example:**
```bash
curl "http://localhost:8000/chat/conversations/1/messages"
```

**Response:**
```json
{
  "conversation_id": 1,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "What is the remote work policy?",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "According to the company policy, employees may work remotely up to 3 days per week with manager approval [1]...",
      "created_at": "2024-01-15T10:30:15"
    },
    {
      "id": 3,
      "role": "user",
      "content": "How do I request remote work?",
      "created_at": "2024-01-15T10:35:00"
    },
    {
      "id": 4,
      "role": "assistant",
      "content": "To request remote work, submit your request at least 48 hours in advance through the HR portal [1]...",
      "created_at": "2024-01-15T10:35:10"
    }
  ]
}
```

Notes:
- Messages are ordered by `created_at` ascending
- `role` is either `"user"` or `"assistant"`

**Error Response:**
```json
{
  "detail": "Conversation not found"
}
```

**Status Codes:**
- `200 OK` - Messages retrieved successfully
- `404 Not Found` - Conversation doesn't exist

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Download OpenAPI specification

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200 OK` - Request successful
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File too large
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently no rate limiting is implemented. For production, consider:
- Rate limiting per IP address
- API key-based quotas
- Concurrent request limits

## CORS Configuration

The API allows requests from `http://localhost:3000` by default. Update `allow_origins` in `app/main.py` for production domains.

## Data Models

### Document
```python
{
  "id": int,
  "name": str,
  "path": str,
  "created_at": datetime
}
```

### Chunk
```python
{
  "id": int,
  "document_id": int,
  "chunk_id": str,
  "content": str,
  "start_line": int,
  "end_line": int,
  "section_title": str | None
}
```

### Conversation
```python
{
  "id": int,
  "title": str,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Message
```python
{
  "id": int,
  "conversation_id": int,
  "role": "user" | "assistant",
  "content": str,
  "created_at": datetime
}
```

## Example Workflow

1. **Upload a document:**
```bash
curl -X POST "http://localhost:8000/docs/upload" -F "file=@policy.pdf"
```

2. **Start a conversation:**
```bash
curl -X POST "http://localhost:8000/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the working hours?", "conversation_id": null}'
```
Returns `conversation_id: 1`

3. **Continue the conversation:**
```bash
curl -X POST "http://localhost:8000/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"message": "Are there flexible hours?", "conversation_id": 1}'
```

4. **View conversation history:**
```bash
curl "http://localhost:8000/chat/conversations/1/messages"
```

5. **List all conversations:**
```bash
curl "http://localhost:8000/chat/conversations"
```

6. **Delete a document:**
```bash
curl -X DELETE "http://localhost:8000/docs/1"
```

## Python Client Example

```python
import requests

class PolicyChatbot:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.conversation_id = None
    
    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/docs/upload", files=files)
            response.raise_for_status()
            return response.json()
    
    def ask(self, question):
        payload = {
            "message": question,
            "conversation_id": self.conversation_id
        }
        response = requests.post(f"{self.base_url}/chat/query", json=payload)
        response.raise_for_status()
        
        data = response.json()
        self.conversation_id = data['conversation_id']
        return data
    
    def list_conversations(self):
        response = requests.get(f"{self.base_url}/chat/conversations")
        response.raise_for_status()
        return response.json()

# Usage
chatbot = PolicyChatbot()

# Upload a document
result = chatbot.upload_document("policy.pdf")
print(f"Uploaded {result['document_name']}, created {result['chunk_count']} chunks")

# Start a conversation
response = chatbot.ask("What is the remote work policy?")
print(f"Answer: {response['answer']}")
print(f"Citations: {len(response['citations'])} sources")

# Continue the conversation
response = chatbot.ask("How do I request remote work?")
print(f"Answer: {response['answer']}")

# List all conversations
conversations = chatbot.list_conversations()
print(f"Total conversations: {len(conversations['conversations'])}")
```

## Configuration

Key settings (configurable via environment variables):

- **CHUNK_SIZE**: 500 characters (default)
- **CHUNK_OVERLAP**: 100 characters (default)
- **RETRIEVAL_TOP_K**: 4 chunks (default)
- **CONVERSATION_HISTORY_LENGTH**: 5 messages (default)
- **MAX_FILE_SIZE**: 50MB (default)
- **OPENAI_MODEL**: gpt-4o-mini (default)
- **OPENAI_TEMPERATURE**: 0.7 (default)
- **OPENAI_MAX_TOKENS**: 1000 (default)

## Notes

- Maximum file size: 50MB
- Supported file types: PDF, TXT
- Chunk size: 500 characters (configurable)
- Top-K retrieval: 4 chunks (configurable)
- Conversation history: Last 5 messages (configurable)
- Citation filtering: Only sources cited in LLM response are returned
- Snippets start at sentence boundaries for better readability
