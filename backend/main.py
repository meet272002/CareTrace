from fastapi import FastAPI
from backend.api.routes import router
from backend.database import create_health_records_table
from backend.api.records_routes import router as record_router

app = FastAPI(title="CareTrace API",
              description=("BackEnd API for voice enabled personal health"
                            "timeline generation in Hindi and Gujarati"),
              version="1.0.0",
            )

app.include_router(record_router, prefix="/api/v1")
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def initialize_database():
    create_health_records_table()

@app.get("/")
def root():
    return {
        "message" : "Welcome to CareTrace API.",
        "status" : "running",
        "docs" : "/docs",
    }

