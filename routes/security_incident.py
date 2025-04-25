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
import os
from fastapi.responses import JSONResponse
from pathlib import Path
import matplotlib.pyplot as plt

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
    Regresa toda la información de un security_incident por su ID.
    
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
    Regresa todos los security_incidents asignados a un policía específico (por su police_id).
    
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
    Regresa un análisis de los security_incidents asignados a un policía específico (por su police_id).
    Este análisis incluye estadísticas de tiempo de atención, distribución de estados y un gráfico generado.
    
    Parameters:
    - police_id: The ID of the police officer
    
    Returns:
    - Dict with analysis results including:
        - summary statistics
        - attention time average
        - incident details
        - URL to the generated image
    """
    # Query all incidents for this police officer (NO LIMIT for analysis)
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
    
    # Filter valid data for plotting
    plot_data = df.dropna(subset=['attention_time_seconds'])
    if plot_data.empty:
        raise HTTPException(
            status_code=400,
            detail="No valid attention time data available for analysis."
        )
    
    # Calculate statistics
    avg_attention_time_seconds = plot_data['attention_time_seconds'].mean()
    median_attention_time_seconds = plot_data['attention_time_seconds'].median()
    
    # Create output directory for plots
    output_dir = "./analysis/police_all_incidents"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the plot
    plt.figure(figsize=(16, 10))
    
    # Plot 1: Attention time per incident
    plt.subplot(2, 1, 1)
    plt.bar(
        plot_data['incident_id'].astype(str),
        plot_data['attention_time_seconds'],
        color='skyblue',
        alpha=0.7
    )
    plt.axhline(y=avg_attention_time_seconds, color='r', linestyle='-', label=f'Promedio: {avg_attention_time_seconds/60:.2f} minutos')
    plt.axhline(y=median_attention_time_seconds, color='g', linestyle='--', label=f'Mediana: {median_attention_time_seconds/60:.2f} minutos')
    plt.title(f"Análisis de Tiempos de Atención para Policía ID {police_id}", fontsize=14)
    plt.ylabel("Tiempo de Atención (segundos)", fontsize=12)
    plt.xlabel("ID del Incidente", fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Plot 2: Average attention time by vector
    plt.subplot(2, 1, 2)
    if 'vector_id' in plot_data.columns and not plot_data['vector_id'].isna().all():
        plot_data['vector_id'] = plot_data['vector_id'].fillna('Desconocido')
        vector_analysis = plot_data.groupby('vector_id')['attention_time_seconds'].agg(['mean', 'count']).reset_index()
        vector_analysis = vector_analysis.sort_values('mean', ascending=False)
        plt.bar(
            vector_analysis['vector_id'].astype(str),
            vector_analysis['mean'],
            alpha=0.7,
            color='lightgreen'
        )
        plt.title("Tiempo Promedio de Atención por Vector", fontsize=14)
        plt.ylabel("Tiempo Promedio de Atención (segundos)", fontsize=12)
        plt.xlabel("ID del Vector", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, "No hay datos de vector disponibles", ha='center', va='center', fontsize=14)
        plt.axis('off')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{output_dir}/police_id_{police_id}_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Construct the image URL
    image_url = f"/static/analysis/police_all_incidents/{Path(plot_filename).name}"
    
    # Prepare the response
    response = {
        "police_id": police_id,
        "summary_statistics": {
            "total_incidents": len(df),
            "average_attention_time_seconds": avg_attention_time_seconds,
            "median_attention_time_seconds": median_attention_time_seconds
        },
        "image_url": image_url
    }
    
    return JSONResponse(content=response)