"""
SentinelX FastAPI Application
Main entry point for the backend REST API.
"""
import os
import time
import resource
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from backend.config import settings
from backend.database import init_db
from backend.routers import auth, threats, search, otx, analytics

# Simple request counter for monitoring
_metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "start_time": time.time(),
}

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cyber Threat Intelligence Sharing Platform — REST API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    """Simple middleware to count requests for Prometheus metrics."""
    _metrics["requests_total"] += 1
    response = await call_next(request)
    if response.status_code >= 400:
        _metrics["errors_total"] += 1
    return response


# Register routers
app.include_router(auth.router)
app.include_router(threats.router)
app.include_router(search.router)
app.include_router(otx.router)
app.include_router(analytics.router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    init_db()
    print(f"[{settings.APP_NAME}] Backend started on {settings.BACKEND_URL}")
    print(f"[{settings.APP_NAME}] API docs: {settings.BACKEND_URL}/docs")


@app.get("/", tags=["Health"])
def root():
    """API health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": f"{settings.BACKEND_URL}/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    from backend.services.otx_service import is_otx_available
    return {
        "status": "healthy",
        "database": "connected",
        "otx_integration": "live" if is_otx_available() else "demo",
    }


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics endpoint."""
    uptime = time.time() - _metrics["start_time"]

    # CPU usage — process CPU time in seconds (built-in)
    cpu_seconds = time.process_time()

    # RAM usage — resident memory in bytes (built-in resource module)
    # ru_maxrss is in KB on Linux
    ram_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024

    # Disk usage — /data volume (built-in os module)
    try:
        disk = os.statvfs("/data")
        disk_total = disk.f_blocks * disk.f_frsize
        disk_used = (disk.f_blocks - disk.f_bfree) * disk.f_frsize
    except OSError:
        disk_total = 0
        disk_used = 0

    output = (
        f'# HELP sentinelx_requests_total Total HTTP requests\n'
        f'# TYPE sentinelx_requests_total counter\n'
        f'sentinelx_requests_total {_metrics["requests_total"]}\n'
        f'# HELP sentinelx_uptime_seconds Server uptime in seconds\n'
        f'# TYPE sentinelx_uptime_seconds gauge\n'
        f'sentinelx_uptime_seconds {uptime:.1f}\n'
        f'# HELP sentinelx_cpu_seconds_total Process CPU time in seconds\n'
        f'# TYPE sentinelx_cpu_seconds_total counter\n'
        f'sentinelx_cpu_seconds_total {cpu_seconds:.2f}\n'
        f'# HELP sentinelx_memory_bytes Process memory usage in bytes\n'
        f'# TYPE sentinelx_memory_bytes gauge\n'
        f'sentinelx_memory_bytes {ram_bytes}\n'
        f'# HELP sentinelx_disk_total_bytes Total disk space in bytes\n'
        f'# TYPE sentinelx_disk_total_bytes gauge\n'
        f'sentinelx_disk_total_bytes {disk_total}\n'
        f'# HELP sentinelx_disk_used_bytes Used disk space in bytes\n'
        f'# TYPE sentinelx_disk_used_bytes gauge\n'
        f'sentinelx_disk_used_bytes {disk_used}\n'
    )
    return PlainTextResponse(output, media_type="text/plain")


