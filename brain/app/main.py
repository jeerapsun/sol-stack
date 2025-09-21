from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, profile, memory, rag, admin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SOL-Stack Brain Service",
    description="Local + Cloud Agent Brain with RAG and Memory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.on_event("startup")
async def startup_event():
    logger.info("SOL-Stack Brain Service starting up...")
    # Initialize any required services here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SOL-Stack Brain Service shutting down...")