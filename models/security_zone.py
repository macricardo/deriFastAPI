from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from config.db import Base

class SecurityZone(Base):
    __tablename__ = "security_zone"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    sku = Column(String, nullable=True)
    name = Column(String, nullable=True)
    poly = Column(String, nullable=True)  # USER-DEFINED PostgreSQL type represented as String
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    description = Column(String, nullable=True)
    vector_final = Column(Integer, nullable=False)
    vector_initial = Column(Integer, nullable=False)
    zone_type = Column(Integer, nullable=False)
    
    # Define relationships if needed
    # vectors = relationship("SecurityVector", back_populates="zone")
    # incidents = relationship("SecurityIncident", back_populates="zone")

    police_assigned = relationship("SecurityPolice", back_populates="zone")