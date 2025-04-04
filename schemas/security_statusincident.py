from pydantic import BaseModel
from typing import Optional

class SecurityStatusIncidentBase(BaseModel):
    name: str
    slug: Optional[str] = None

class SecurityStatusIncidentCreate(SecurityStatusIncidentBase):
    pass

class SecurityStatusIncidentResponse(SecurityStatusIncidentBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 compatibility