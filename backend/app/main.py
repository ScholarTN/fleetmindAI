from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import add_exception_handlers

from app.api.routes.auth import router as auth_router
from app.api.routes.drivers import router as drivers_router
from app.api.routes.fleet import router as fleet_router
from app.api.routes.truck import router as truck_router
from app.api.routes.trailer import router as trailers_router
from app.api.routes.load import router as load_router
from app.api.routes.incident import router as incident_router
from app.api.routes.dispatch import router as dispatch_router
from app.routes.ai import router as ai_router

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FleetMind AI",
    version="0.1.0",
    description="Enterprise Logistics Operations Copilot",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

add_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# auth router already declares prefix="/auth"
app.include_router(auth_router, prefix="/api/v1")

# drivers router already declares prefix="/drivers"
app.include_router(drivers_router, prefix="/api/v1")

# trucks router already declares prefix="/trucks"
app.include_router(truck_router, prefix="/api/v1")

# fleet router has no prefix — we assign /fleet here
app.include_router(fleet_router, prefix="/api/v1/fleet")

#trailers router
app.include_router(trailers_router, prefix="/api/v1")

#Load router
app.include_router(load_router, prefix="/api/v1")

#incident router
app.include_router(incident_router, prefix="/api/v1")

#Dispatch router
app.include_router(dispatch_router, prefix="/api/v1")

app.include_router(ai_router)

# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    return {
        "project": "FleetMind AI",
        "version": "0.1.0",
        "description": "Enterprise Logistics Operations Copilot",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy"}



logger.info("FleetMind AI application loaded")
