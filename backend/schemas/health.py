from pydantic import BaseModel

"""
Created by Meet Gandhi on 24/10/2026 HealthResponse Schema. 
"""
class HealthResponse(BaseModel):
    status: str
    service: str