from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import engine
from models.security_police import SecurityPolice
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define a Pydantic model for the response
class SecurityPoliceResponse(BaseModel):
    id: int
    created_at: datetime  # Changed from str to datetime
    updated_at: datetime  # Changed from str to datetime
    position_id: Optional[int]
    license_plate: Optional[str]
    point: Optional[str]
    profile_id: Optional[int]
    status_id: Optional[int]
    supervisor_id: Optional[int]
    vector_id: Optional[int]
    is_outside: bool
    armament_id: Optional[int]
    bulletprof_vest_id: Optional[int]
    device_id: Optional[int]
    is_supervisor: bool
    radio_id: Optional[int]
    turn_id: Optional[int]
    vehicle_id: Optional[int]
    zone_id: Optional[int]
    status_staff_id: Optional[int]
    is_chief: bool
    is_sergeant: bool
    grade: str
    grouping_id: Optional[int]
    is_assignable: bool
    special_group_police_id: Optional[int]
    last_tracking_location: Optional[datetime]  # Changed from str to datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2 compatibility

@router.get("/security_police/{id}", response_model=SecurityPoliceResponse)
def get_security_police_by_id(id: int, db: Session = Depends(get_db)):
    # Query the database for the record with the given id
    security_police = db.query(SecurityPolice).filter(SecurityPolice.id == id).first()
    if not security_police:
        raise HTTPException(status_code=404, detail="SecurityPolice record not found")
    return security_police  # FastAPI will use the Pydantic model to serialize the response