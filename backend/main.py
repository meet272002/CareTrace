import threading

from fastapi import FastAPI
from backend.api.routes import router
from backend.database import (
    create_health_records_table,
    create_health_issues_tables,
)
from backend.api.records_routes import router as record_router
from backend.api.issues_routes import router as issues_router

app = FastAPI(title="CareTrace API",
              description=("BackEnd API for voice enabled personal health"
                            "timeline generation in Hindi and Gujarati"),
              version="1.0.0",
            )

app.include_router(record_router, prefix="/api/v1")
app.include_router(issues_router, prefix="/api/v1")
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def initialize_database():
    create_health_records_table()
    create_health_issues_tables()


@app.on_event("startup")
def warm_up_models():
    """Load speech + translation models in the background so the API
    starts immediately and the first user request does not wait."""
    from backend.services.transcription import preload_models
    from backend.services.translation import preload_translation_model

    for task in (preload_models, preload_translation_model):
        threading.Thread(target=task, daemon=True).start()

@app.get("/")
def root():
    return {
        "message" : "Welcome to CareTrace API.",
        "status" : "running",
        "docs" : "/docs",
    }

