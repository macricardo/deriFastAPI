from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings  # Import settings

# Database connection
DATABASE_URL = settings.DATABASE_URL 
engine = create_engine(DATABASE_URL)

# Metadata and Base
meta = MetaData()
Base = declarative_base()

# Import all models to register them with Base
from models import *  # Import all models from the models package

# Create (bind) tablas
Base.metadata.create_all(bind=engine)

# Session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Connection
conn = engine.connect()
