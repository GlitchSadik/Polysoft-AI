# RAG-Based Company Policy Chatbot

AI chatbot for answering questions about company policy documents using Retrieval-Augmented Generation. Built with FastAPI backend and React frontend.

## Features

- Question answering using OpenAI GPT-4o-mini with RAG
- Citation filtering - displays only sources referenced in the response
- Conversation history with automatic title generation
- PDF document upload with automatic chunking and embedding
- Document management interface
- Semantic search using ChromaDB vector database

## Architecture

### Tech Stack

Backend:
- FastAPI 0.109.0
- SQLModel (SQLite)
- ChromaDB 0.4.22
- OpenAI API (GPT-4o-mini)
- sentence-transformers 5.1.2 (all-MiniLM-L6-v2)
- pdfplumber

Frontend:
- React 18.2.0
- Vite 5.0.0
- Tailwind CSS 3.3.6
- Axios

### RAG Pipeline

1. Document Ingestion: PDF text extraction and semantic chunking
2. Embedding: Generate vector embeddings using sentence-transformers
3. Storage: Store vectors in ChromaDB, metadata in SQLite
4. Query Processing: Embed user question and retrieve top-K chunks
5. Response Generation: Generate response from context and conversation history

### Project Structure

```
.
├── app/                    # Backend application
│   ├── main.py            # FastAPI application entry
│   ├── config.py          # Configuration settings
│   ├── db.py              # Database setup
│   ├── models/            # SQLModel database models
│   │   ├── documents.py   # Document model
│   │   ├── chunks.py      # Chunk model
│   │   ├── conversations.py  # Conversation model (with title, updated_at)
│   │   └── messages.py    # Message model
│   ├── routers/           # API route handlers
│   │   ├── docs_router.py    # Document upload endpoints
│   │   ├── chat_router.py    # Chat/RAG endpoints
│   │   └── health_router.py  # Health check
│   ├── services/          # Business logic
│   │   ├── document_service.py  # Document ingestion
│   │   ├── rag_service.py       # RAG query logic (with citation filtering)
│   │   └── llm_service.py       # OpenAI integration
│   └── utils/             # Helper utilities
│       ├── pdf_utils.py       # PDF/TXT extraction
│       ├── text_utils.py      # Text processing
│       └── chunking.py        # Semantic recursive chunking
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── ChatArea.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Message.jsx
│   │   │   ├── UploadModal.jsx
│   │   │   └── DocumentsModal.jsx
│   │   ├── services/      # API client
│   │   └── App.jsx
│   └── public/            # Static assets (bot-avatar.png)
├── storage/               # File storage
│   └── docs/              # Uploaded PDFs
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## Installation

git clone <your-repo-url>
cd "Softvence Assesment"
### Prerequisites
- Docker
- OpenAI API key

### Quick Start with Docker

1. Clone the repository
```bash
git clone https://github.com/GlitchSadik/Polysoft-AI.git
cd Polysoft-AI
```

2. Copy and edit environment variables
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. Build and run the app with Docker
```bash
docker build -t polysoft-ai .
docker run -p 8000:8000 --env-file .env polysoft-ai
```

Backend: http://localhost:8000
Frontend: http://localhost:8000/frontend/dist/
API docs: http://localhost:8000/docs

---
**Common Setup Issues:**
- If you see errors about missing environment variables, make sure `.env` is present and correct.
- If ports are busy, use a different port: `docker run -p 8001:8000 ...`
- If you get CORS errors, update allowed origins in `main.py`.

## Usage

### Upload Documents
1. Click "Upload PDF" in the sidebar
2. Select a PDF file
3. Wait for processing (chunking and embedding)
4. Document appears in "Manage PDFs" list

### Chat
1. Type your question in the input field
2. Press Enter or click send
3. View response with source citations
4. Click citations to view document excerpts
5. Only sources referenced by the LLM are shown

### Manage Documents
1. Click "Manage PDFs" to view uploaded documents
2. Click delete icon to remove documents

### Conversations
- Click "New Chat" to start a new conversation
- Previous conversations are saved with auto-generated titles
- Click any conversation to resume

## Configuration

Key environment variables in `.env`:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Embedding Model
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=100
RETRIEVAL_TOP_K=4
CONVERSATION_HISTORY_LENGTH=5

# Database
DATABASE_URL=sqlite:///./policy_chatbot.db
```

## API Endpoints

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed reference.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/query` | Send a message and get AI response |
| GET | `/chat/conversations` | List all conversations |
| GET | `/chat/conversations/{id}/messages` | Get conversation history |
| POST | `/docs/upload` | Upload PDF document |
| GET | `/docs/list` | List uploaded documents |
| DELETE | `/docs/{id}` | Delete a document |
| GET | `/health` | Health check |

## Key Features

### Smart Citation Filtering
- LLM is instructed to cite sources using [1], [2] markers
- Backend parses citations from response using regex
- Only referenced sources shown to user (not all 4 retrieved chunks)
- Improves citation quality and relevance

### Conversation Management
- Each conversation has unique ID and auto-generated title
- Title is first 50 characters of first user message
- Messages linked to conversations with timestamps
- Updated timestamp tracked on new messages

### Readable Snippets
- Citation snippets start at sentence boundaries
- Regex-based sentence detection for better readability
- Shows context around relevant information

## Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test
```

### Code Quality
```bash
# Backend linting
ruff check app/

# Frontend linting
cd frontend && npm run lint
```

## Troubleshooting

Port already in use:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

ChromaDB issues:
```bash
# Delete and recreate vector database
rm -rf chroma_db/
# Restart backend to recreate
```

Database schema errors:
```bash
# Delete database (will lose data - re-upload documents)
rm policy_chatbot.db
# Restart backend to recreate with new schema
```

Empty conversation list:
- Check browser console for errors
- Verify backend is running on port 8000
- Check that Conversation model has `title` and `updated_at` fields

Citations showing all sources:
- Verify LLM is using citation markers [1], [2] in responses
- Check `_filter_cited_sources()` in `rag_service.py`

## Production Considerations

- CORS: Configure `allow_origins` in `main.py` for your domain
- File Storage: Consider cloud storage (S3, Azure Blob)
- Database: Migrate to PostgreSQL for production
- Authentication: Add API key or OAuth
- Rate Limiting: Implement request throttling
- Monitoring: Add APM (DataDog, New Relic)
- Vector Database: Consider Pinecone/Weaviate for scale
- Environment Variables: Use secrets manager (AWS Secrets Manager, Azure Key Vault)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License
