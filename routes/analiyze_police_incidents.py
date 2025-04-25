import os
from fastapi.responses import JSONResponse
from pathlib import Path
from analysis.police_all_incidents import analyze_police_incidents as analyze_police_incidents_script
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from config.db import engine
from models.security_incident import SecurityIncident
from sqlalchemy.orm import sessionmaker
from schemas.security_incident import SecurityIncidentResponse


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
    # Define the output directory for the analysis
    output_dir = "./analysis/police_all_incidents/outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Call the analysis function from police_all_incidents.py
    analysis_result = analyze_police_incidents_script(police_id, output_dir=output_dir)

    # Check if an error occurred during the analysis
    if "error" in analysis_result:
        raise HTTPException(status_code=400, detail=analysis_result["error"])

    # Construct the URL for the generated image
    image_filename = Path(analysis_result["plot_path"]).name
    image_url = f"/static/analysis/police_all_incidents/outputs/{image_filename}"

    # Include the image URL in the response
    analysis_result["image_url"] = image_url

    return JSONResponse(content=analysis_result)