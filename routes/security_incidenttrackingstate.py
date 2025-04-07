from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.security_incidenttrackingstate import SecurityIncidentTrackingState
from typing import List
from pydantic import BaseModel
from datetime import datetime

# Define the response schema
class SecurityIncidentTrackingStateResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    incident_id: int
    status_id: int

    class Config:
        from_attributes = True  # Pydantic v2 compatibility

# Create the router
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/incident_tracking_states/{incident_id}", response_model=List[SecurityIncidentTrackingStateResponse])
def get_tracking_states_by_incident_id(incident_id: int, db: Session = Depends(get_db)):
    # Query the database for all tracking states with the given incident_id
    tracking_states = (
        db.query(SecurityIncidentTrackingState)
        .filter(SecurityIncidentTrackingState.incident_id == incident_id)
        .order_by(SecurityIncidentTrackingState.created_at.asc())
        .all()
    )
    if not tracking_states:
        raise HTTPException(status_code=404, detail="No tracking states found for the given incident_id")
    return tracking_states