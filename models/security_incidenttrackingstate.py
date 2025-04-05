from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from config.db import Base

class SecurityIncidentTrackingState(Base):
    __tablename__ = "security_incidenttrackingstate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    incident_id = Column(Integer, ForeignKey("security_incident.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("security_statusincident.id"), nullable=True)
    
    # Define relationships if needed
    # incident = relationship("SecurityIncident", back_populates="tracking_states")
    # status = relationship("SecurityStatusIncident", back_populates="tracking_states")