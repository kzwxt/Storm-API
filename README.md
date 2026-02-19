# STORM API

FastAPI wrapper for Stanford STORM with streaming, monitoring, and in-memory storage.

---

## 🚀 Features

- RESTful API with streaming support
- Real-time progress tracking via streaming
- Health check endpoint for monitoring
- Request ID tracing for debugging
- Structured JSON logging
- In-memory file storage (no disk writes)
- Modular architecture (api/core/utils/tests)
- Dependency management with Poetry
- Environment configuration

---

## 📁 Project Structure

```text
storm-api/
├── main.py                          # FastAPI entry point
├── pyproject.toml                   # Poetry dependencies
├── poetry.lock
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── api/
│   ├── __init__.py
│   ├── models.py                    # Request/response schemas with Pydantic
│   └── routes.py                    # API endpoints with async handlers
├── core/
│   ├── __init__.py
│   ├── storm_service.py             # STORM wrapper with in-memory storage
│   └── streaming_callback.py        # STORM progress callbacks for streaming
├── utils/
│   ├── __init__.py
│   ├── helpers.py                   # Helper utilities
│   ├── logging_config.py            # Structured JSON logging configuration
│   └── middleware.py                # Request ID middleware for tracing
├── tests/
│   ├── __init__.py
│   ├── test_stream.py               # Manual streaming test script
│   ├── test_in_memory_storage.py    # In-memory storage unit tests
│   ├── test_integration.py          # API integration tests
│   ├── test_request_id_middleware.py # Middleware unit tests
│   ├── test_storm_service.py        # StormService unit tests
│   └── test_streaming_callback.py   # Streaming callback unit tests
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
poetry install
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run server
```bash
poetry run uvicorn main:app --reload
```

Open API docs:
```
http://localhost:8000/docs
```

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": 3600
}
```

---

### Generate Article (Non-Streaming)
```bash
POST /query
Content-Type: application/json

{
  "topic": "Artificial Intelligence",
  "stream": false
}
```

**Response:**
```json
{
  "result": "# Artificial Intelligence\n\nGenerated article..."
}
```

---

### Generate Article (Streaming)
```bash
POST /query/stream
Content-Type: application/json

{
  "topic": "Artificial Intelligence"
}
```

**Response:** Real-time text stream of progress and article

---

## 🔒 Environment Variables

Create `.env` file:

```bash
# LLM Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Search Configuration
SERPER_API_KEY=your_serper_api_key_here

# STORM Configuration
MAX_CONV_TURN=2
MAX_PERSPECTIVE=2
MAX_SEARCH_QUERIES_PER_TURN=2
SEARCH_TOP_K=2
RETRIEVE_TOP_K=2
MAX_THREAD_NUM=2

# Pipeline Control
DO_RESEARCH=true
DO_GENERATE_OUTLINE=true
DO_GENERATE_ARTICLE=true
DO_POLISH_ARTICLE=true
```

---

## 🧠 Architecture

```
Client → Request ID Middleware → Routes → Service Layer → STORM Engine
                                    ↓
                              Structured Logging
                                    ↓
                              In-Memory Storage
```

- **Middleware:** Generates unique request IDs for tracing
- **Routes:** Handle HTTP requests/responses
- **Service:** Wraps STORM logic with in-memory storage
- **STORM:** Performs research and article generation

---

## 📊 Logging

All logs are structured JSON format:

```json
{
  "level": "INFO",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Query request received",
  "event": "query_request_received",
  "request_id": "abc123",
  "topic": "Python Programming"
}
```

**Request ID:** Included in all logs and response headers for tracing.

---

## 🔍 Testing

### Run all fast tests (unit + fast integration)
```bash
poetry run pytest tests/ -v -m "not slow"
```

### Run all tests (including slow integration tests)
```bash
poetry run pytest tests/ -v
```

### Run only integration tests
```bash
poetry run pytest tests/test_integration.py -v
```

### Run only slow integration tests (full STORM pipeline)
```bash
poetry run pytest tests/test_integration.py -v -m "slow"
```

### Test streaming endpoint manually
```bash
cd tests
python test_stream.py
```

---

## 📌 Tech Stack

- FastAPI
- Pydantic
- Poetry
- Python 3.11+
- Stanford STORM
- DeepSeek (LLM)
- Serper (Search)
- Pytest (Testing)

---

## 📊 Test Coverage

| Component | Tests | Type | Status |
|-----------|-------|------|--------|
| Request Validation | 7 | Unit | ✅ Complete |
| StormService | 7 (4 fast, 3 slow) | Unit | ✅ Complete |
| In-Memory Storage | 7 | Unit | ✅ Complete |
| Streaming Callback | 13 | Unit | ✅ Complete |
| Request ID Middleware | 10 | Unit | ✅ Complete |
| Integration Tests | 14 (11 fast, 3 slow) | Integration | ✅ Complete |
| **Total** | **58 (48 fast, 10 slow)** | - | ✅ **All Pass** |

### Test Types
- **Unit Tests (44)**: Fast, isolated tests with mocked dependencies (~10s)
- **Integration Tests (14)**: End-to-end API tests
  - **Fast (11)**: HTTP validation, headers, error handling (~10s)
  - **Slow (3)**: Full STORM pipeline execution (~700s)

---

## 👤 Author

Amirul Mifzal
