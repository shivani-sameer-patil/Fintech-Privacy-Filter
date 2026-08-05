"""
Production-grade FastAPI Web Application Server for FinTech Privacy Filter.

Serves static UI assets and provides REST API endpoints:
- POST /api/process : Processes document text using FinTechPrivacyPipeline
- GET /health       : System health checks
- GET /metrics      : API and pipeline telemetry statistics
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_server")

PORT = 8050
WEB_DIR = Path(__file__).resolve().parent

# Initialize FastAPI App
app = FastAPI(
    title="FinTech Privacy Filter Web Studio API",
    description="Enterprise-grade privacy filtering system API with multilingual support",
    version="1.0.0",
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline engine
pipeline_engine = FinTechPrivacyPipeline()

# In-memory metrics counters
METRICS = {
    "total_requests": 0,
    "total_errors": 0,
    "total_entities_detected": 0,
    "total_processing_time_ms": 0.0,
    "detector_total_latencies": {
        "regex": 0.0,
        "presidio": 0.0,
        "spacy": 0.0,
        "keyword": 0.0,
        "gliner": 0.0,
    },
}


class ProcessRequest(BaseModel):
    text: str


@app.get("/health", tags=["Monitoring"])
def health_check() -> Dict[str, str]:
    """Exposes the service health status."""
    return {"status": "healthy", "timestamp": str(time.time())}


@app.get("/metrics", tags=["Monitoring"])
def get_metrics() -> Dict[str, Any]:
    """Exposes real-time API and pipeline performance telemetry metrics."""
    avg_latency = (
        METRICS["total_processing_time_ms"] / METRICS["total_requests"]
        if METRICS["total_requests"] > 0
        else 0.0
    )
    
    avg_detector_latencies = {}
    for det, val in METRICS["detector_total_latencies"].items():
        avg_detector_latencies[det] = (
            val / METRICS["total_requests"]
            if METRICS["total_requests"] > 0
            else 0.0
        )

    return {
        "total_requests": METRICS["total_requests"],
        "total_errors": METRICS["total_errors"],
        "total_entities_detected": METRICS["total_entities_detected"],
        "average_pipeline_latency_ms": round(avg_latency, 2),
        "average_detector_latencies_ms": {k: round(v, 2) for k, v in avg_detector_latencies.items()},
    }


@app.post("/api/process", tags=["Sanitization"])
def process_text(payload: ProcessRequest) -> Dict[str, Any]:
    """Analyzes and masks PII/financial credentials inside a document."""
    METRICS["total_requests"] += 1
    try:
        start_time = time.perf_counter()
        output = pipeline_engine.process(payload.text)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Update metrics database
        METRICS["total_entities_detected"] += len(output.detected_entities)
        METRICS["total_processing_time_ms"] += duration_ms

        for k, v in output.detector_latencies.items():
            if k in METRICS["detector_total_latencies"]:
                METRICS["detector_total_latencies"][k] += v

        return output.to_dict()
    except Exception as e:
        METRICS["total_errors"] += 1
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount index.html at root "/"
@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


# Mount the remaining static files from the Web Directory
app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="static")


def start_server():
    import uvicorn
    logger.info(f"==================================================")
    logger.info(f"FINTECH PRIVACY FILTER WEB STUDIO SERVER ACTIVE")
    logger.info(f"==================================================")
    logger.info(f"Server URL: http://localhost:{PORT}")
    logger.info(f"Swagger Documentation: http://localhost:{PORT}/docs")
    logger.info(f"Serving UI from: {WEB_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    start_server()
