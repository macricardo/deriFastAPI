from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import engine
from models.security_police import SecurityPolice
from sqlalchemy.orm import sessionmaker
from schemas.security_police import SecurityPoliceResponse
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

@router.get("/security_police/{id}", response_model=SecurityPoliceResponse)
def get_security_police_by_id(id: int, db: Session = Depends(get_db)):
    # Query the database for the record with the given id
    security_police = db.query(SecurityPolice).filter(SecurityPolice.id == id).first()
    if not security_police:
        raise HTTPException(status_code=404, detail="SecurityPolice record not found")
    return security_police  # FastAPI will use the Pydantic model to serialize the response