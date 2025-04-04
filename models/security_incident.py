from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SecurityIncident(Base):
    __tablename__ = "security_incident"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    sku = Column(String, nullable=True)
    citizen_affected = Column(Text, nullable=True)
    location = Column(String, nullable=True)  # USER-DEFINED type in PostgreSQL
    address = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    assigned_at = Column(TIMESTAMP(timezone=True), nullable=True)
    report = Column(Text, nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=True)
    police_id = Column(Integer, ForeignKey("security_police.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    is_open = Column(Boolean, nullable=False)
    is_verified = Column(Boolean, nullable=False)
    incident_type_id = Column(Integer, ForeignKey("incident_types.id"), nullable=True)
    vector_id = Column(Integer, ForeignKey("vectors.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    is_affected = Column(Boolean, nullable=False)
    is_rated = Column(Boolean, nullable=False)
    is_police_arrived = Column(Boolean, nullable=False)
    is_police_confirm = Column(Boolean, nullable=False)
    is_possible_duplicate = Column(Boolean, nullable=False)
    is_read = Column(Boolean, nullable=False)
    is_monitor_open = Column(Boolean, nullable=False)
    is_from_call = Column(Boolean, nullable=False)
    atention_time = Column(String, nullable=False)
    social_proximity_id = Column(Integer, ForeignKey("social_proximities.id"), nullable=True)
    
    # Define relationships if needed
    # police = relationship("SecurityPolice", back_populates="incidents")
    # status = relationship("Status", back_populates="incidents")
    # incident_type = relationship("IncidentType", back_populates="incidents")