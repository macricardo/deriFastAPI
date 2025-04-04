from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityIncidentResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    sku: Optional[str] = None
    citizen_affected: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    assigned_at: Optional[datetime] = None
    report: Optional[str] = None
    assigned_by_id: Optional[int] = None
    citizen_id: Optional[int] = None
    monitor_id: Optional[int] = None
    police_id: Optional[int] = None
    status_id: Optional[int] = None
    is_open: bool
    is_verified: bool
    incident_type_id: Optional[int] = None
    vector_id: Optional[int] = None
    zone_id: Optional[int] = None
    is_affected: bool
    is_rated: bool
    is_police_arrived: bool
    is_police_confirm: bool
    is_possible_duplicate: bool
    is_read: bool
    is_monitor_open: bool
    is_from_call: bool
    atention_time: str
    social_proximity_id: Optional[int] = None

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility in Pydantic v2