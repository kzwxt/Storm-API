# STORM API

FastAPI wrapper for Stanford STORM with streaming, monitoring, and in-memory storage.

---

## 🚀 Features

- RESTful API with streaming support
- Real-time progress tracking
- Health check endpoint
- Request ID tracing
- Structured JSON logging
- In-memory storage
- Modular architecture
- Docker support

---

## 🎓 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/kzwxt/Storm-API.git
cd Storm-API
cp .env.example .env
docker-compose up
```

### Python
```bash
git clone https://github.com/kzwxt/Storm-API.git
cd Storm-API
poetry install
poetry run uvicorn main:app --reload
```

**Access:** http://localhost:8000/docs

---

## 📁 Project Structure

```
storm-api/
├── main.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── api/
│   ├── models.py
│   └── routes.py
├── core/
│   ├── storm_service.py
│   └── streaming_callback.py
├── utils/
│   ├── logging_config.py
│   └── middleware.py
└── tests/
    ├── test_integration.py
    ├── test_storm_service.py
    └── ...
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/query` | POST | Generate article |
| `/query/stream` | POST | Stream article generation |

---

## 🔒 Environment Variables

```bash
DEEPSEEK_API_KEY=your_key
SERPER_API_KEY=your_key
```

---

## 🧠 Architecture

```
Client → Middleware → Routes → Service → STORM
                  ↓
              Logging
                  ↓
            In-Memory Storage
```

---

## 📊 Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Request Validation | 7 | ✅ |
| StormService | 7 | ✅ |
| In-Memory Storage | 7 | ✅ |
| Streaming Callback | 13 | ✅ |
| Request ID Middleware | 10 | ✅ |
| Integration Tests | 14 | ✅ |
| **Total** | **58** | ✅ |

**Run Tests:**
```bash
poetry run pytest tests/ -v -m "not slow"
```

---

## 📌 Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- Poetry
- Stanford STORM
- Pytest
- Docker

---

## 👤 About

**Amirul Mifzal** - AI Engineer

Production-ready API with clean architecture, type safety, and comprehensive testing.