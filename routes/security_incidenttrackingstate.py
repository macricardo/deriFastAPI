import os
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.security_incidenttrackingstate import SecurityIncidentTrackingState
from schemas.security_incidenttrackingstate import SecurityIncidentTrackingStateResponse  # Import schema
from typing import List, Dict, Any
from fastapi.responses import FileResponse
from settings import settings  # Import settings

# Create the router
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BASE_URL = settings.API_URL

@router.get("/incident_tracking_states/{incident_id}", response_model=List[SecurityIncidentTrackingStateResponse])
def get_tracking_states_by_incident_id(incident_id: int, db: Session = Depends(get_db)):
    # Query the database for all tracking states with the given incident_id
    tracking_states = (
        db.query(SecurityIncidentTrackingState)
        .filter(SecurityIncidentTrackingState.incident_id == incident_id)
        .order_by(SecurityIncidentTrackingState.created_at.asc())
        .all()
    )
    if not tracking_states:
        raise HTTPException(status_code=404, detail="No tracking states found for the given incident_id")
    return tracking_states

@router.get("/incident_tracking_states/{incident_id}/analysis")
def analyze_incident_tracking_states(incident_id: int, db: Session = Depends(get_db)):
    """
    Analyze the time spent in each status for a specific incident and generate a plot.

    Parameters:
    - incident_id: The ID of the incident to analyze.

    Returns:
    - The generated plot image as a response.
    """
    # Query the database for all tracking states with the given incident_id
    tracking_states = (
        db.query(SecurityIncidentTrackingState)
        .filter(SecurityIncidentTrackingState.incident_id == incident_id)
        .order_by(SecurityIncidentTrackingState.created_at.asc())
        .all()
    )
    if not tracking_states:
        raise HTTPException(status_code=404, detail="No tracking states found for the given incident_id")

    # Extract relevant data
    data = [{"status_id": ts.status_id, "created_at": ts.created_at} for ts in tracking_states]
    df = pd.DataFrame(data)

    # Ensure the DataFrame is not empty
    if df.empty:
        raise HTTPException(status_code=400, detail="No valid data available for analysis.")

    # Convert created_at to datetime and sort
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at')

    # Calculate time spent in each status
    df['time_spent'] = df['created_at'].shift(-1) - df['created_at']
    df['time_spent'] = df['time_spent'].dt.total_seconds().fillna(0)  # Convert timedelta to seconds

    # Group by status_id and calculate total time spent
    status_time = df.groupby('status_id')['time_spent'].sum().reset_index()

    # Calculate percentages
    total_time = status_time['time_spent'].sum()
    status_time['percentage'] = (status_time['time_spent'] / total_time) * 100

    # Map status_id to status_name
    try:
        # Fetch the mapping from the API
        mapping_response = requests.get(f"{BASE_URL}/status_incidents")
        mapping_response.raise_for_status()
        status_id_name_mapping = mapping_response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve status ID to name mapping: {str(e)}")

    # Ensure the mapping is obtained
    status_time['status_id'] = status_time['status_id'].astype(str)  # Convert to string
    status_id_name_mapping = {str(k): v for k, v in status_id_name_mapping.items()}  # Convert keys to string

    # Replace status_id with status_name
    status_time['status_name'] = status_time['status_id'].map(status_id_name_mapping)

    # Generate the plot
    plt.figure(figsize=(12, 8))
    plt.barh(
        y=status_time['status_name'],  # Use status_name for labels
        width=status_time['percentage'],
        color=plt.cm.tab20.colors[:len(status_time)],
        edgecolor="black"
    )
    plt.title(f"Time Distribution Across Statuses for Incident {incident_id}", fontsize=14)
    plt.xlabel("Percentage of Total Time (%)", fontsize=12)
    plt.ylabel("Incident Status", fontsize=12)

    # Add labels to the bars
    for i, row in status_time.iterrows():
        plt.text(
            row['percentage'] / 2,
            i,
            f"{row['percentage']:.1f}%",
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            weight="bold"
        )

    # Save the plot
    output_dir = "./analysis/incident_all_states"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{output_dir}/incident_{incident_id}_status_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches="tight")
    plt.close()

    # Return the plot image as a response
    return FileResponse(plot_filename, media_type="image/png")