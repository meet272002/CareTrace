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
    """Load the speech and translation models when the backend starts.

    With PRELOAD_BLOCKING (default) the server accepts requests only once both
    are loaded, so the first recording is as fast as any other."""
    from backend.services.transcription import preload_models
    from backend.services.translation import preload_translation_model
    from config.settings import PRELOAD_BLOCKING

    threads = [
        threading.Thread(target=task, daemon=True)
        for task in (preload_models, preload_translation_model)
    ]
    for thread in threads:  # both load in parallel
        thread.start()

    if PRELOAD_BLOCKING:
        print("Loading models... the backend will be ready when this finishes.")
        for thread in threads:
            thread.join()
        print("Models loaded. CareTrace backend is ready.")

@app.get("/")
def root():
    return {
        "message" : "Welcome to CareTrace API.",
        "status" : "running",
        "docs" : "/docs",
    }

