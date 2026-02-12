# STORM API

FastAPI wrapper for Stanford STORM - a research project for generating Wikipedia-style articles from topics.

## Features

- RESTful API interface for STORM functionality
- Clean request/response validation with Pydantic
- CORS support for web applications
- Modular architecture (api/core/utils)
- Dependency management with Poetry

## Project Structure

```
storm-api/
├── main.py              # FastAPI application entry point
├── pyproject.toml       # Poetry dependency configuration
├── poetry.lock          # Locked dependency versions
├── api/
│   ├── models.py        # Pydantic request/response models
│   ├── routes.py        # API endpoints
│   └── service.py       # STORM service wrapper (placeholder)
├── core/                # Core logic for STORM integration
└── utils/               # Helper utilities
```

## Requirements

- Python 3.10 - 3.12
- Poetry (for dependency management)

## Installation

```bash
# Install dependencies
poetry install

# Or using pip
pip install fastapi uvicorn pydantic
```

## Usage

### Start the Server

```bash
poetry run uvicorn main:app --reload
```

Or without Poetry:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```
GET /
```

Returns API status.

#### Generate Article
```
POST /query
```

Request body:
```json
{
  "topic": "Artificial Intelligence",
  "stream": false
}
```

Response:
```json
{
  "result": "Fake result for Artificial Intelligence"
}
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI (interactive API documentation).

## Development

### Test with curl

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning"}'
```

### Run tests (when available)

```bash
poetry run pytest
```

## Current Status

- [x] Basic FastAPI setup
- [x] Pydantic models for request/response
- [x] API endpoint `/query`
- [x] Placeholder STORM service
- [ ] STORM integration (core logic)
- [ ] Streaming support
- [ ] Docker configuration
- [ ] Unit tests

## License

This project is a coding assignment for AI Engineer position.