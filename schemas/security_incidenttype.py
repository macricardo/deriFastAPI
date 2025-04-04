from pydantic import BaseModel
from typing import Optional

class SecurityIncidentTypeBase(BaseModel):
    sku: Optional[str] = None
    name: str
    slug: Optional[str] = None
    level: str
    active: bool

class SecurityIncidentTypeCreate(SecurityIncidentTypeBase):
    pass

class SecurityIncidentTypeUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    level: Optional[str] = None
    active: Optional[bool] = None

class SecurityIncidentTypeResponse(SecurityIncidentTypeBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 compatibility