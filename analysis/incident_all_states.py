import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"  # Adjust if your API is hosted elsewhere

def analyze_incident_states(incident_id: int, output_dir: str = "./outputs") -> Dict[str, Any]:
    """
    Analyze the time spent in each status for a given incident and generate a horizontal stacked bar chart.

    Parameters:
    -----------
    incident_id : int
        The ID of the incident to analyze.
    output_dir : str
        Directory to save the generated plot (default: "./outputs").

    Returns:
    --------
    Dict[str, Any]
        Analysis results including the time spent in each status and the path to the generated plot.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Query the API to get tracking states for the given incident_id
    try:
        response = requests.get(f"{BASE_URL}/incident_tracking_states/{incident_id}")
        response.raise_for_status()
        tracking_states = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tracking states: {e}")
        return {"error": f"Failed to retrieve tracking states: {str(e)}"}

    # Extract only the fields we need: status_id and created_at
    data = [{"status_id": item["status_id"], "created_at": item["created_at"]} for item in tracking_states]

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Ensure there are tracking states to analyze
    if df.empty:
        print(f"No tracking states found for incident_id {incident_id}")
        return {"error": f"No tracking states found for incident_id {incident_id}"}

    # Convert created_at to datetime and sort by it
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at')

# Calculate the time spent in each status using the next row's created_at
    df['time_spent'] = df['created_at'].shift(-1) - df['created_at']
    df['time_spent'] = df['time_spent'].dt.total_seconds()  # Convert timedelta to seconds
    df['time_spent'] = df['time_spent'].fillna(0)  # Fill NaN for the last row with 0

    # Group by status_id and calculate total time spent in each status
    status_time = df.groupby('status_id')['time_spent'].sum().reset_index()

    # Calculate the percentage of time spent in each status
    total_time = status_time['time_spent'].sum()
    status_time['percentage'] = (status_time['time_spent'] / total_time) * 100
    print(status_time)
    
    # Generate the horizontal stacked bar chart
    # Generate the horizontal stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(
        y=["Status Time"], 
        width=status_time['percentage'], 
        left=status_time['percentage'].cumsum() - status_time['percentage'], 
        color=plt.cm.tab20.colors[:len(status_time)], 
        edgecolor="black"
    )

    # Add labels for each segment
    for i, row in status_time.iterrows():
        # Calculate the center position of the current segment
        left_position = status_time['percentage'].iloc[:i].sum()  # Sum of all previous segments
        center_position = left_position + (row['percentage'] / 2)  # Center of the current segment

        # Only add labels if the segment is wide enough
        if row['percentage'] > 2:  # Skip labels for segments smaller than 5% of the total width
            plt.text(
                center_position,  # Horizontal position
                0,  # Vertical position
                f"{row['status_id']:.0f} ({row['time_spent']:.1f})",  # Label text
                ha="center",  # Horizontal alignment
                va="center",  # Vertical alignment
                fontsize=10,  # Font size
                color="white",  # Text color
                weight="bold",  # Font weight
                rotation=90  # Rotate the text vertically
            )

    # Chart title and labels
    plt.title(f"Time Distribution Across Statuses for Incident {incident_id}", fontsize=14)
    plt.xlabel("Percentage of Total Time (%)", fontsize=12)
    plt.ylabel("Incident Status", fontsize=12)
    plt.tight_layout()

    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{output_dir}/incident_{incident_id}_status_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Analysis complete. Plot saved to {plot_filename}")

    # Return analysis results
    return {
        "incident_id": incident_id,
        "status_time": status_time.to_dict(orient="records"),
        "plot_path": plot_filename
    }

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        try:
            incident_id = int(sys.argv[1])
            analyze_incident_states(incident_id)
        except ValueError:
            print("Error: Incident ID must be an integer")
            sys.exit(1)
    else:
        # Interactive mode
        try:
            incident_id = int(input("Enter incident ID to analyze: "))
            analyze_incident_states(incident_id)
        except ValueError:
            print("Error: Incident ID must be an integer")