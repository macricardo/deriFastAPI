from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.security_statusincident import SecurityStatusIncident
from typing import List
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

@router.get("/status_incidents", response_model=List[SecurityStatusIncidentResponse])
def get_all_status_incidents(db: Session = Depends(get_db)):
    """
    Retrieve all status incidents from the database.

    Returns:
    --------
    List[SecurityStatusIncidentResponse]
        A list of all status incidents with their IDs and names.
    """
    try:
        status_incidents = db.query(SecurityStatusIncident).all()
        if not status_incidents:
            raise HTTPException(status_code=404, detail="No status incidents found")
        return status_incidents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")