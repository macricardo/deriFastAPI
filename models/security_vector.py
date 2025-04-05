from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from config.db import Base

class SecurityVector(Base):
    __tablename__ = "security_vector"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    sku = Column(String, nullable=True)
    name = Column(String, nullable=True)
    poly = Column(String, nullable=True)  # USER-DEFINED PostgreSQL type represented as String
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("security_zone.id"), nullable=True)
    description = Column(String, nullable=True)
    
    # Define relationships if needed
    # zone = relationship("SecurityZone", back_populates="vectors")
    # incidents = relationship("SecurityIncident", back_populates="vector")