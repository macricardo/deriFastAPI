from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityVectorBase(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    poly: Optional[str] = None
    status_id: Optional[int] = None
    zone_id: Optional[int] = None
    description: Optional[str] = None

class SecurityVectorCreate(SecurityVectorBase):
    pass

class SecurityVectorResponse(SecurityVectorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 compatibility