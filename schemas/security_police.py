from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SecurityPoliceResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
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
    zone_name: Optional[str]  # Add this field to include only the name of the zone
    status_staff_id: Optional[int]
    is_chief: bool
    is_sergeant: bool
    grade: str
    grouping_id: Optional[int]
    is_assignable: bool
    special_group_police_id: Optional[int]
    last_tracking_location: Optional[datetime]

    class Config:
        from_attributes = True  # Pydantic v2 compatibility