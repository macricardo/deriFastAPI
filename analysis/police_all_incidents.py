import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import json
from typing import Dict, List, Any, Optional

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from settings import settings  # Import settings

BASE_URL = settings.API_URL   # URL de la API.

def analyze_police_incidents(police_id: int, output_dir: str = "./outputs") -> Dict[str, Any]:
    """
    Recupera y analiza todos los incidentes de un oficial de policía específico.

    Se ejecuta:
    -----------
    python analysis/police_all_incidents.py <police_id>
    
    Parámetros:
    -----------
    police_id : int
        El ID del oficial de policía a analizar.
    output_dir : str
        Directorio donde se guardarán las gráficas generadas (por defecto: "./outputs").
        
    Returns:
    --------
    Dict[str, Any]
        Resultados del análisis, incluyendo estadísticas resumidas y gráficas.
    """
    # Asegurarse de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener detalles del oficial de policía
    try:
        police_response = requests.get(f"{BASE_URL}/security_police/{police_id}")
        police_response.raise_for_status()
        police_data = police_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al recuperar datos del oficial de policía: {e}")
        return {"error": f"No se pudieron recuperar los datos del oficial de policía: {str(e)}"}
    
    # Obtener todos los incidentes de este oficial de policía
    try:
        incidents_response = requests.get(f"{BASE_URL}/security_incident/police/{police_id}/analysis")
        incidents_response.raise_for_status()
        analysis_data = incidents_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al recuperar incidentes: {e}")
        return {"error": f"No se pudieron recuperar los datos de los incidentes: {str(e)}"}
    
    # Extraer datos para el procesamiento
    incidents = pd.DataFrame(analysis_data["incidents"])
    summary_stats = analysis_data["summary_statistics"]
    
    # Procesar tiempos de atención
    def time_to_seconds(time_str):
        if time_str is None or time_str == "null" or pd.isna(time_str):
            return np.nan
        
        if isinstance(time_str, str) and ":" in time_str:
            # Formato: "HH:MM:SS"
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
        
        # Intentar convertir como flotante
        try:
            return float(time_str)
        except (ValueError, TypeError):
            return np.nan
    
    # Procesar tiempos de atención en segundos para el análisis
    incidents['attention_time_seconds'] = incidents['attention_time'].apply(time_to_seconds)
    
    # Filtrar valores NaN para graficar
    plot_data = incidents.dropna(subset=['attention_time_seconds'])
    
    if plot_data.empty:
        print("No hay datos válidos de tiempo de atención para graficar")
        return {
            "police_id": police_id,
            "error": "No hay datos válidos de tiempo de atención para graficar",
            "summary": summary_stats
        }
    
    # Crear figura con dos subgráficas (tamaño más grande para mejor visibilidad)
    plt.figure(figsize=(16, 10))
    
    # Calcular estadísticas para datos válidos
    mean_time = plot_data['attention_time_seconds'].mean()
    median_time = plot_data['attention_time_seconds'].median()
    
    # Gráfica 1: Gráfico de barras vertical de tiempos de atención
    plt.subplot(2, 1, 1)
    bars = plt.bar(
        plot_data['incident_id'].astype(str), 
        plot_data['attention_time_seconds'],
        color='skyblue',
        alpha=0.7
    )
    
    # Agregar línea horizontal para el promedio
    plt.axhline(y=mean_time, color='r', linestyle='-', 
                label=f'Promedio: {mean_time/60:.2f} minutos')
    plt.axhline(y=median_time, color='g', linestyle='--', 
                label=f'Mediana: {median_time/60:.2f} minutos')
    
    # Título con información del oficial
    officer_title = (f"ID Policía: {police_id}" +
                    f" | Grado: {police_data.get('grade', 'Desconocido')}" +
                    f" | Incidentes: {len(incidents)}")
    
    plt.title(f"Análisis de Tiempos de Atención\n{officer_title}", fontsize=14)
    plt.ylabel("Tiempo de Atención (segundos)", fontsize=12)
    plt.xlabel("ID del Incidente", fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Gráfica 2: Tiempo de atención por vector (si los datos de vector están disponibles)
    plt.subplot(2, 1, 2)
    
    # Agrupar por vector_id y calcular tiempo promedio de atención
    if 'vector_id' in plot_data.columns and not plot_data['vector_id'].isna().all():
        # Rellenar vector_id NaN con "Desconocido" para propósitos de análisis
        plot_data['vector_id'] = plot_data['vector_id'].fillna('Desconocido')
        
        vector_analysis = plot_data.groupby('vector_id')['attention_time_seconds'].agg(['mean', 'count']).reset_index()
        
        # Ordenar por el tiempo promedio más alto
        vector_analysis = vector_analysis.sort_values('mean', ascending=False)
        
        # Graficar barras con ancho basado en el conteo para énfasis visual
        plt.bar(
            vector_analysis['vector_id'].astype(str), 
            vector_analysis['mean'],
            alpha=0.7,
            width=0.6,  # Ancho fijo para mejor legibilidad
            color='lightgreen'
        )
        
        # Agregar etiquetas de conteo encima de las barras
        for i, (_, row) in enumerate(vector_analysis.iterrows()):
            plt.text(
                i, row['mean'] + 5, 
                f"n={int(row['count'])}", 
                ha='center', va='bottom',
                fontsize=9
            )
            
        plt.title("Tiempo Promedio de Atención por Vector", fontsize=14)
        plt.ylabel("Tiempo Promedio de Atención (segundos)", fontsize=12)
        plt.xlabel("ID del Vector", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, "No hay datos de vector disponibles", ha='center', va='center', fontsize=14)
        plt.axis('off')
    
    # Ajustar diseño y guardar figura
    plt.tight_layout()
    
    # Guardar gráfica en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{output_dir}/police_id_{police_id}_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Análisis completo. Gráfica guardada en {plot_filename}")
    
    # Retornar resultados del análisis
    return {
        "police_id": police_id,
        "officer_info": {
            "grade": police_data.get("grade", "Desconocido"),
            "is_supervisor": police_data.get("is_supervisor", False),
        },
        "plot_path": plot_filename,
        "summary_statistics": summary_stats,
        "vector_statistics": analysis_data.get("vector_analysis", {}),
        "status_distribution": analysis_data.get("status_distribution", {})
    }

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        try:
            police_id = int(sys.argv[1])
            analyze_police_incidents(police_id)
        except ValueError:
            print("Error: El ID de policía debe ser un número entero")
            sys.exit(1)
    else:
        # Modo interactivo
        try:
            police_id = int(input("Ingrese el ID del policía a analizar: "))
            analyze_police_incidents(police_id)
        except ValueError:
            print("Error: El ID de policía debe ser un número entero")