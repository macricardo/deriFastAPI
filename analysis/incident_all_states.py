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

    # Fetch the status_id to name mapping
    try:
        mapping_response = requests.get(f"{BASE_URL}/status_incidents")
        mapping_response.raise_for_status()
        status_id_name_mapping = mapping_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving status ID to name mapping: {e}")
        return {"error": f"Failed to retrieve status ID to name mapping: {str(e)}"}

    # Ensure the status_id column and the keys in the mapping have the same type
    status_time['status_id'] = status_time['status_id'].astype(str)  # Convert to string
    status_id_name_mapping = {str(k): v for k, v in status_id_name_mapping.items()}  # Convert keys to string

    # Replace status_id with the corresponding name in the DataFrame
    status_time['status_name'] = status_time['status_id'].map(status_id_name_mapping)

    print(status_time)

    # Generate the horizontal stacked bar chart
    plt.figure(figsize=(12, 8))  # Adjusted figure size to accommodate the table
    plt.barh(
        y=["Status Time"], 
        width=status_time['percentage'], 
        left=status_time['percentage'].cumsum() - status_time['percentage'], 
        color=plt.cm.tab20.colors[:len(status_time)], 
        edgecolor="black"
    )

    # Add labels for each segment
    for i, row in status_time.iterrows():
        left_position = status_time['percentage'].iloc[:i].sum()
        center_position = left_position + (row['percentage'] / 2)

        if row['percentage'] > 2:
            plt.text(
                center_position,
                0,
                f"{row['status_name']} ({row['time_spent']:.1f})",
                ha="center",
                va="center",
                fontsize=10,
                color="white",
                weight="bold",
                rotation=90
            )

    # Chart title and labels
    plt.title(f"Time Distribution Across Statuses for Incident {incident_id}", fontsize=14)
    plt.xlabel("Percentage of Total Time (%)", fontsize=12)
    plt.ylabel("Incident Status", fontsize=12)

    # Add the table below the chart
    table_data = status_time[['status_name', 'time_spent', 'percentage']].copy()
    table_data['time_spent'] = table_data['time_spent'].apply(lambda x: f"{x:.1f} s")  # Format time_spent
    table_data['percentage'] = table_data['percentage'].apply(lambda x: f"{x:.1f} %")  # Format percentage

    # Convert the DataFrame to a list of lists for the table
    table_data_list = table_data.values.tolist()
    column_labels = ['Status Name', 'Time Spent', 'Percentage']

    # Add the table to the plot
    plt.table(
        cellText=table_data_list,
        colLabels=column_labels,
        cellLoc='center',
        loc='bottom',
        bbox=[0.0, -0.4, 1.0, 0.3]  # Adjust position and size of the table
    )

    plt.subplots_adjust(bottom=0.3)  # Adjust the bottom margin to fit the table
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