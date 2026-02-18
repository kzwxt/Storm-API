import os
import time
from utils.logging_config import setup_logging, get_logger
from utils.middleware import RequestIDMiddleware, get_request_id
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

load_dotenv()

START_TIME = time.time()
setup_logging(level="INFO")
logger = get_logger(__name__)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

app = FastAPI(
    title="STORM API",
    description="FastAPI wrapper for Stanford STORM",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.include_router(router)

@app.get("/")
async def root():
    request_id = get_request_id()
    logger.info("Root endpoint accessed", extra={"event": "root_accessed", "request_id": request_id})
    return {"status": "ok", "message": "STORM API is running"}