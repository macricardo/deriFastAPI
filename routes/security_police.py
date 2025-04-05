from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from config.db import engine
from models.security_police import SecurityPolice
from sqlalchemy.orm import sessionmaker
from schemas.security_police import SecurityPoliceResponse

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
    security_police = (
        db.query(SecurityPolice)
        .options(joinedload(SecurityPolice.zone))  # Eagerly load the zone relationship
        .filter(SecurityPolice.id == id)
        .first()
    )
    if not security_police:
        raise HTTPException(status_code=404, detail="SecurityPolice record not found")
    
    # Extract the zone name
    zone_name = security_police.zone.name if security_police.zone else None

    # Return the response with the zone_name field
    return {
        "id": security_police.id,
        "created_at": security_police.created_at,
        "updated_at": security_police.updated_at,
        "position_id": security_police.position_id,
        "license_plate": security_police.license_plate,
        "point": security_police.point,
        "profile_id": security_police.profile_id,
        "status_id": security_police.status_id,
        "supervisor_id": security_police.supervisor_id,
        "vector_id": security_police.vector_id,
        "is_outside": security_police.is_outside,
        "armament_id": security_police.armament_id,
        "bulletprof_vest_id": security_police.bulletprof_vest_id,
        "device_id": security_police.device_id,
        "is_supervisor": security_police.is_supervisor,
        "radio_id": security_police.radio_id,
        "turn_id": security_police.turn_id,
        "vehicle_id": security_police.vehicle_id,
        "zone_name": zone_name,  # Include only the zone name
        "status_staff_id": security_police.status_staff_id,
        "is_chief": security_police.is_chief,
        "is_sergeant": security_police.is_sergeant,
        "grade": security_police.grade,
        "grouping_id": security_police.grouping_id,
        "is_assignable": security_police.is_assignable,
        "special_group_police_id": security_police.special_group_police_id,
        "last_tracking_location": security_police.last_tracking_location,
    }