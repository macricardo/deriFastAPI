from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from config.db import Base

class SecurityStatusIncident(Base):
    __tablename__ = "security_statusincident"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    
    # Define relationships if needed
    # incidents = relationship("SecurityIncident", back_populates="status")