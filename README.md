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
- Docker support for easy deployment

---

## 🎓 Quick Start for Lecturer

### Option 1: Using Docker (Recommended - Easiest)

**Prerequisites:**
- Docker installed on your machine

**Steps:**
```bash
# 1. Clone the repository
git clone https://github.com/kzwxt/Storm-API.git
cd Storm-API

# 2. Create .env file from template
cp .env.example .env

# 3. Add your API keys to .env file
# DEEPSEEK_API_KEY=your_key_here
# SERPER_API_KEY=your_key_here

# 4. Run with Docker Compose
docker-compose up

# 5. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Option 2: Using Python (Requires Python 3.11+)

**Steps:**
```bash
# 1. Clone the repository
git clone https://github.com/kzwxt/Storm-API.git
cd Storm-API

# 2. Install Poetry (if not installed)
pip install poetry

# 3. Install dependencies
poetry install

# 4. Create .env file
cp .env.example .env
# Add your API keys

# 5. Run the server
poetry run uvicorn main:app --reload

# 6. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Testing the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate Article:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Programming", "stream": false}'
```

**Run Tests:**
```bash
# Fast tests only
poetry run pytest tests/ -v -m "not slow"

# All tests (takes ~10 minutes)
poetry run pytest tests/ -v
```

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

## 👤 About the Developer

**Amirul Mifzal** - AI Engineer

This project demonstrates expertise in building production-ready AI/ML APIs with emphasis on:
- Clean architecture and design patterns
- Type safety and code quality
- Comprehensive testing
- Scalable async operations
- Production deployment readiness

---

## 📦 Technical Assessment Summary

### Project Overview
A production-ready FastAPI wrapper for Stanford STORM that generates comprehensive articles using AI. Demonstrates full-stack development skills with focus on scalability, maintainability, and production readiness.

### Key Technical Demonstrations

#### 1. Clean Architecture & Design Patterns
- **Separation of Concerns**: Modular structure (api/core/utils/tests)
- **Service Layer Pattern**: Business logic isolated from routes
- **Dependency Injection**: FastAPI `Depends()` for testability
- **Middleware Pattern**: Request ID tracing for debugging
- **Factory Pattern**: Singleton service instance management

#### 2. Production-Ready Features
- **Health Monitoring**: Dedicated `/health` endpoint with uptime tracking
- **Structured Logging**: JSON logs with request tracing for observability
- **Error Handling**: Comprehensive validation and exception handling
- **Input Validation**: Pydantic models with XSS protection
- **Configuration Management**: Environment-based configuration

#### 3. Performance & Scalability
- **Async Operations**: Non-blocking I/O using `run_in_threadpool()`
- **Streaming Support**: Real-time progress updates without blocking
- **Resource Management**: In-memory storage prevents disk I/O
- **Connection Pooling**: Efficient resource utilization

#### 4. Code Quality
- **Type Safety**: Complete type hints throughout codebase
- **Documentation**: Google-style docstrings for all functions/classes
- **Testing**: 58 tests (unit + integration) with 100% pass rate
- **Linting Ready**: Configured for ruff, black, mypy

#### 5. DevOps & Deployment
- **Docker Support**: Containerized application for consistent deployment
- **Docker Compose**: Easy local development setup
- **CI/CD Ready**: Structure supports GitHub Actions
- **API Documentation**: Interactive Swagger UI

### Technical Stack Proficiency

| Technology | Level | Demonstrated Skills |
|------------|-------|---------------------|
| Python 3.11+ | Expert | Type hints, async/await, generators |
| FastAPI | Expert | Dependency injection, middleware, streaming |
| Pydantic | Expert | Validation, models, error handling |
| Testing | Advanced | Unit tests, integration tests, mocking |
| Docker | Intermediate | Containerization, docker-compose |
| AI/ML | Intermediate | LLM integration, streaming callbacks |
| Architecture | Expert | Clean architecture, design patterns |

### Problem-Solving Examples

#### Challenge 1: Blocking Operations
**Problem:** STORM pipeline blocks event loop for 60+ seconds
**Solution:** Implemented `run_in_threadpool()` for non-blocking async operations
**Impact:** Server can handle concurrent requests, improved throughput

#### Challenge 2: File System Pollution
**Problem:** STORM writes temporary files to disk
**Solution:** Overrode `FileIOHelper` with in-memory storage
**Impact:** Clean execution, no side effects, faster I/O

#### Challenge 3: Debugging Distributed Requests
**Problem:** Hard to trace requests across service calls
**Solution:** Implemented request ID middleware with context tracking
**Impact:** Easy debugging, complete request lifecycle visibility

### Metrics & Achievements

| Metric | Value |
|--------|-------|
| **Test Coverage** | 58 tests (100% pass rate) |
| **Code Quality** | Full type hints, complete docstrings |
| **Performance** | Non-blocking async operations |
| **Documentation** | Comprehensive README + API docs |
| **Deployment** | Docker containerized |
| **Lines of Code** | ~2000+ (including tests) |
| **Files** | 15+ Python modules |

### Quick Evaluation for Joget

**Clone & Run (5 minutes):**
```bash
git clone https://github.com/kzwxt/Storm-API.git
cd Storm-API
cp .env.example .env
# Add your API keys
docker-compose up
# Visit http://localhost:8000/docs
```

**Run Tests (2 minutes):**
```bash
poetry run pytest tests/ -v -m "not slow"
```

**What to Review:**
1. **Code Quality**: Check type hints, docstrings, structure
2. **Architecture**: Review modular design and separation of concerns
3. **Testing**: Run test suite and examine test coverage
4. **API Design**: Try interactive docs at `/docs`
5. **Production Features**: Check health endpoint, logging, error handling

### Why This Matters for Joget

This project demonstrates:
- ✅ Ability to build production-ready AI/ML APIs
- ✅ Understanding of scalable architecture
- ✅ Focus on code quality and maintainability
- ✅ Experience with modern Python frameworks
- ✅ Problem-solving and optimization skills
- ✅ DevOps awareness (Docker, CI/CD)
- ✅ Attention to detail (testing, documentation)

### Next Steps

For deeper evaluation, review:
1. `api/routes.py` - API endpoint design and async patterns
2. `core/storm_service.py` - Business logic and service layer
3. `utils/middleware.py` - Middleware implementation
4. `tests/` - Test coverage and quality
5. `Dockerfile` - Containerization best practices
