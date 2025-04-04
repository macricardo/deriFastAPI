from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityIncidentTrackingStateBase(BaseModel):
    incident_id: Optional[int] = None
    status_id: Optional[int] = None

class SecurityIncidentTrackingStateCreate(SecurityIncidentTrackingStateBase):
    pass

class SecurityIncidentTrackingStateResponse(SecurityIncidentTrackingStateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 compatibility