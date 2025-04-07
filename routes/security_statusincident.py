from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.security_statusincident import SecurityStatusIncident
from typing import List, Dict
from pydantic import BaseModel

# Define the response schema
class SecurityStatusIncidentResponse(BaseModel):
    id: int
    name: str

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

@router.get("/status_incidents", response_model=Dict[int, str])
def get_status_id_name_mapping(db: Session = Depends(get_db)):
    """
    Retrieve a mapping of status_id to their corresponding names.

    Returns:
    --------
    Dict[int, str]
        A dictionary where keys are status IDs and values are their names.
    """
    try:
        status_incidents = db.query(SecurityStatusIncident).all()
        if not status_incidents:
            raise HTTPException(status_code=404, detail="No status incidents found")
        return {incident.id: incident.name for incident in status_incidents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")