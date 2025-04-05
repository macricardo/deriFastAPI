from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship
from config.db import meta
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from config.db import Base

class SecurityPolice(Base):
    __tablename__ = "security_police"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    license_plate = Column(String(20), nullable=True)
    point = Column(String, nullable=True)  # USER-DEFINED type, adjust as needed
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    supervisor_id = Column(Integer, ForeignKey("supervisors.id"), nullable=True)
    vector_id = Column(Integer, ForeignKey("vectors.id"), nullable=True)
    is_outside = Column(Boolean, nullable=False)
    armament_id = Column(Integer, ForeignKey("armaments.id"), nullable=True)
    bulletprof_vest_id = Column(Integer, ForeignKey("bulletproof_vests.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    is_supervisor = Column(Boolean, nullable=False)
    radio_id = Column(Integer, ForeignKey("radios.id"), nullable=True)
    turn_id = Column(Integer, ForeignKey("turns.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("security_zone.id"), nullable=True)
    status_staff_id = Column(Integer, ForeignKey("status_staff.id"), nullable=True)
    is_chief = Column(Boolean, nullable=False)
    is_sergeant = Column(Boolean, nullable=False)
    grade = Column(String(15), nullable=False)
    grouping_id = Column(Integer, ForeignKey("groupings.id"), nullable=True)
    is_assignable = Column(Boolean, nullable=False)
    special_group_police_id = Column(Integer, ForeignKey("special_group_police.id"), nullable=True)
    last_tracking_location = Column(TIMESTAMP(timezone=True), nullable=True)
    
    zone = relationship("SecurityZone", back_populates="police_assigned")