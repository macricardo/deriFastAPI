from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from config.db import engine
from models.security_incident import SecurityIncident
from sqlalchemy.orm import sessionmaker
from schemas.security_incident import SecurityIncidentResponse
import pandas as pd
import numpy as np
from datetime import datetime, time
import re

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/security_incident/{id}", response_model=SecurityIncidentResponse)
def get_security_incident_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a security incident by its ID.
    
    Parameters:
    - id: The ID of the security incident to retrieve
    
    Returns:
    - SecurityIncident: The security incident with the requested ID
    
    Raises:
    - 404 Not Found: If the security incident doesn't exist
    """
    # Query the database for the record with the given id
    security_incident = db.query(SecurityIncident).filter(SecurityIncident.id == id).first()
    if not security_incident:
        raise HTTPException(status_code=404, detail="SecurityIncident record not found")
    return security_incident  # FastAPI will use the Pydantic model to serialize the response

@router.get("/security_incident/police/{police_id}", response_model=List[SecurityIncidentResponse])
def get_police_incidents(
    police_id: int, 
    limit: int = Query(50, ge=1, le=100), 
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retrieve all security incidents assigned to a specific police officer.
    
    Parameters:
    - police_id: The ID of the police officer
    - limit: Maximum number of records to return (default: 50, max: 100)
    - offset: Number of records to skip (for pagination)
    
    Returns:
    - List[SecurityIncidentResponse]: List of security incidents assigned to the police officer
    
    Raises:
    - 404 Not Found: If no incidents are found for the specified police officer
    """
    # Query the database for incidents assigned to the given police_id
    incidents = db.query(SecurityIncident)\
                  .filter(SecurityIncident.police_id == police_id)\
                  .order_by(SecurityIncident.created_at.desc())\
                  .offset(offset)\
                  .limit(limit)\
                  .all()
    
    if not incidents:
        raise HTTPException(
            status_code=404, 
            detail=f"No security incidents found for police officer with ID {police_id}"
        )
        
    return incidents  # FastAPI will use the Pydantic model to serialize the response

@router.get("/security_incident/police/{police_id}/analysis")
def analyze_police_incidents(
    police_id: int,
    db: Session = Depends(get_db)
):
    """
    Analyze incidents assigned to a specific police officer and return statistics
    with attention time analysis.
    
    Parameters:
    - police_id: The ID of the police officer
    
    Returns:
    - Dict with analysis results including:
        - summary statistics
        - attention time average
        - incident details
    """
    # Query all incidents for this police officer (no limit for analysis)
    incidents = db.query(SecurityIncident)\
                  .filter(SecurityIncident.police_id == police_id)\
                  .all()
    
    if not incidents:
        raise HTTPException(
            status_code=404, 
            detail=f"No security incidents found for police officer with ID {police_id}"
        )
    
    # Create DataFrame from incidents
    incidents_data = []
    for incident in incidents:
        incidents_data.append({
            "incident_id": incident.id,
            "police_id": incident.police_id,
            "status_id": incident.status_id,
            "vector_id": incident.vector_id,
            "zone_id": incident.zone_id,
            "attention_time": incident.atention_time
        })
    
    df = pd.DataFrame(incidents_data)
    
    # Convert "00:00:00" formatted attention_time to seconds
    def time_to_seconds(time_str):
        if not time_str or time_str == 'null':
            return np.nan
        
        # Handle various time formats
        # Format: "HH:MM:SS"
        time_match = re.match(r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$', str(time_str))
        if time_match:
            h, m, s = map(int, time_match.groups())
            return h * 3600 + m * 60 + s
        
        # Format: numeric string (already in seconds/minutes)
        try:
            return float(time_str)
        except (ValueError, TypeError):
            return np.nan
    
    # Apply conversion and handle NaN values
    df['attention_time_seconds'] = df['attention_time'].apply(time_to_seconds)
    
    # Calculate statistics (ignoring NaN values)
    avg_attention_time_seconds = df['attention_time_seconds'].mean()
    
    # Format time stats
    def format_seconds_to_time(seconds):
        if pd.isna(seconds):
            return "00:00:00"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Create summary statistics
    summary_stats = {
        "total_incidents": len(df),
        "average_attention_time_seconds": float(avg_attention_time_seconds) if not pd.isna(avg_attention_time_seconds) else 0,
        "average_attention_time_formatted": format_seconds_to_time(avg_attention_time_seconds),
        "min_attention_time_seconds": float(df['attention_time_seconds'].min()) if not pd.isna(df['attention_time_seconds'].min()) else 0,
        "max_attention_time_seconds": float(df['attention_time_seconds'].max()) if not pd.isna(df['attention_time_seconds'].max()) else 0,
        "median_attention_time_seconds": float(df['attention_time_seconds'].median()) if not pd.isna(df['attention_time_seconds'].median()) else 0
    }
    
    # Add percentile statistics for more detailed analysis
    percentiles = [25, 50, 75, 90, 95]
    for p in percentiles:
        percentile_value = df['attention_time_seconds'].quantile(p/100)
        summary_stats[f"p{p}_attention_time_seconds"] = float(percentile_value) if not pd.isna(percentile_value) else 0
    
    # Calculate count of incidents by status_id for analysis
    status_counts = df['status_id'].value_counts().to_dict()
    
    # Calculate zone-based statistics
    zone_stats = {}
    for zone in df['zone_id'].dropna().unique():
        zone_df = df[df['zone_id'] == zone]
        zone_avg_time = zone_df['attention_time_seconds'].mean()
        zone_stats[str(int(zone))] = {
            "count": len(zone_df),
            "avg_attention_time_seconds": float(zone_avg_time) if not pd.isna(zone_avg_time) else 0,
            "avg_attention_time_formatted": format_seconds_to_time(zone_avg_time)
        }
    
    # Return results with detailed analysis
    return {
        "police_id": police_id,
        "summary_statistics": summary_stats,
        "status_distribution": {str(k): v for k, v in status_counts.items()},
        "zone_analysis": zone_stats,
        "incidents": df.fillna("null").to_dict(orient='records')
    }