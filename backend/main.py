from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="CareTrace API",
              description=("BackEnd API for voice enabled personal health"
                            "timeline generation in Hindi and Gujarati"),
              version="1.0.0",
            )

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message" : "Welcome to CareTrace API.",
        "status" : "running",
        "docs" : "/docs",
    }