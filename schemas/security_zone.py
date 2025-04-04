from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityZoneBase(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    poly: Optional[str] = None
    status_id: Optional[int] = None
    description: Optional[str] = None
    vector_final: int
    vector_initial: int
    zone_type: int

class SecurityZoneCreate(SecurityZoneBase):
    pass

class SecurityZoneResponse(SecurityZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 compatibility