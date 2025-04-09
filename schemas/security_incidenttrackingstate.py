from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityIncidentTrackingStateBase(BaseModel):
    incident_id: Optional[int] = None
    status_id: Optional[int] = None

class SecurityIncidentTrackingStateCreate(SecurityIncidentTrackingStateBase):
    pass

# Define the response schema
class SecurityIncidentTrackingStateResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    incident_id: int
    status_id: int

    class Config:
        from_attributes = True  # Pydantic v2 compatibility