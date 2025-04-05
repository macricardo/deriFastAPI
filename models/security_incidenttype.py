from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from config.db import Base


class SecurityIncidentType(Base):
    __tablename__ = "security_incidenttype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, nullable=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    level = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)

    # Define relationships if needed
    # incidents = relationship("SecurityIncident", back_populates="incident_type")