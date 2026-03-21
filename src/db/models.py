from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

Base = declarative_base()

class DBTelemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50))
    person_count = Column(Integer)
    crowd_density = Column(Float)
    timestamp = Column(DateTime)
    analysis_summary = Column(TEXT, nullable=True)
    # Location Intelligence - Neel
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

class DBAlert(Base):
    __tablename__ = "alerts"
    id = Column(String(50), primary_key=True)
    severity = Column(String(20))
    location = Column(String(100))
    timestamp = Column(DateTime)
    description = Column(TEXT)
    recommended_action = Column(TEXT)
    # Location Intelligence - Neel
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

# Set up the engine and session
# Using PostgreSQL if configured, otherwise falls back to a dummy or fails early
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)