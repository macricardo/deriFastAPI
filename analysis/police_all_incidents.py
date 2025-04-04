import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import json
from typing import Dict, List, Any, Optional

BASE_URL = "http://localhost:8000/api"  # Adjust if your API is hosted elsewhere

def analyze_police_incidents(police_id: int, output_dir: str = "./outputs") -> Dict[str, Any]:
    """
    Retrieve and analyze all incidents for a specific police officer.
    
    Parameters:
    -----------
    police_id : int
        The ID of the police officer to analyze
    output_dir : str
        Directory to save generated plots (default: "./outputs")
        
    Returns:
    --------
    Dict[str, Any]
        Analysis results including summary statistics and plots
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get police officer details
    try:
        police_response = requests.get(f"{BASE_URL}/security_police/{police_id}")
        police_response.raise_for_status()
        police_data = police_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving police officer data: {e}")
        return {"error": f"Failed to retrieve police officer data: {str(e)}"}
    
    # Get all incidents for this police officer
    try:
        incidents_response = requests.get(f"{BASE_URL}/security_incident/police/{police_id}/analysis")
        incidents_response.raise_for_status()
        analysis_data = incidents_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving incidents: {e}")
        return {"error": f"Failed to retrieve incident data: {str(e)}"}
    
    # Extract data for processing
    incidents = pd.DataFrame(analysis_data["incidents"])
    summary_stats = analysis_data["summary_statistics"]
    
    # Process attention times
    def time_to_seconds(time_str):
        if time_str is None or time_str == "null" or pd.isna(time_str):
            return np.nan
        
        if isinstance(time_str, str) and ":" in time_str:
            # Format: "HH:MM:SS"
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
        
        # Try to convert as float
        try:
            return float(time_str)
        except (ValueError, TypeError):
            return np.nan
    
    # Process attention times into seconds for analysis
    incidents['attention_time_seconds'] = incidents['attention_time'].apply(time_to_seconds)
    
    # Filter out NaN values for plotting
    plot_data = incidents.dropna(subset=['attention_time_seconds'])
    
    if plot_data.empty:
        print("No valid attention time data to plot")
        return {
            "police_id": police_id,
            "error": "No valid attention time data to plot",
            "summary": summary_stats
        }
    
    # Create figure with two subplots (larger size for better visibility)
    plt.figure(figsize=(16, 10))
    
    # Calculate statistics for valid data
    mean_time = plot_data['attention_time_seconds'].mean()
    median_time = plot_data['attention_time_seconds'].median()
    
    # Plot 1: Vertical bar chart of attention times
    plt.subplot(2, 1, 1)
    bars = plt.bar(
        plot_data['incident_id'].astype(str), 
        plot_data['attention_time_seconds'],
        color='skyblue',
        alpha=0.7
    )
    
    # Add horizontal line for average
    plt.axhline(y=mean_time, color='r', linestyle='-', 
                label=f'Mean: {mean_time/60:.2f} minutes')
    plt.axhline(y=median_time, color='g', linestyle='--', 
                label=f'Median: {median_time/60:.2f} minutes')
    
    # Title with officer information
    officer_title = (f"Police ID: {police_id}" +
                    f" | Grade: {police_data.get('grade', 'Unknown')}" +
                    f" | Incidents: {len(incidents)}")
    
    plt.title(f"Attention Times Analysis\n{officer_title}", fontsize=14)
    plt.ylabel("Attention Time (seconds)", fontsize=12)
    plt.xlabel("Incident ID", fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Plot 2: Attention time by vector (if vector data is available)
    plt.subplot(2, 1, 2)
    
    # Group by vector_id and calculate mean attention time
    if 'vector_id' in plot_data.columns and not plot_data['vector_id'].isna().all():
        # Fill NaN vector_id with "Unknown" for analysis purposes
        plot_data['vector_id'] = plot_data['vector_id'].fillna('Unknown')
        
        vector_analysis = plot_data.groupby('vector_id')['attention_time_seconds'].agg(['mean', 'count']).reset_index()
        
        # Sort by highest mean time
        vector_analysis = vector_analysis.sort_values('mean', ascending=False)
        
        # Plot bars with count-based width for visual emphasis
        plt.bar(
            vector_analysis['vector_id'].astype(str), 
            vector_analysis['mean'],
            alpha=0.7,
            width=0.6,  # Fixed width for better readability
            color='lightgreen'
        )
        
        # Add count labels on top of bars
        for i, (_, row) in enumerate(vector_analysis.iterrows()):
            plt.text(
                i, row['mean'] + 5, 
                f"n={int(row['count'])}", 
                ha='center', va='bottom',
                fontsize=9
            )
            
        plt.title("Average Attention Time by Vector", fontsize=14)
        plt.ylabel("Mean Attention Time (seconds)", fontsize=12)
        plt.xlabel("Vector ID", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, "No vector data available", ha='center', va='center', fontsize=14)
        plt.axis('off')
    
    # Tight layout and save figure
    plt.tight_layout()
    
    # Save plot to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{output_dir}/police_id_{police_id}_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Analysis complete. Plot saved to {plot_filename}")
    
    # Return analysis results
    return {
        "police_id": police_id,
        "officer_info": {
            "grade": police_data.get("grade", "Unknown"),
            "is_supervisor": police_data.get("is_supervisor", False),
        },
        "plot_path": plot_filename,
        "summary_statistics": summary_stats,
        "vector_statistics": analysis_data.get("vector_analysis", {}),
        "status_distribution": analysis_data.get("status_distribution", {})
    }

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        try:
            police_id = int(sys.argv[1])
            analyze_police_incidents(police_id)
        except ValueError:
            print("Error: Police ID must be an integer")
            sys.exit(1)
    else:
        # Interactive mode
        try:
            police_id = int(input("Enter police ID to analyze: "))
            analyze_police_incidents(police_id)
        except ValueError:
            print("Error: Police ID must be an integer")