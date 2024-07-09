import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from datetime import datetime, timedelta

# Leer el archivo TSV de issues
issues_df = pd.read_csv('updated_issues.tsv', sep='\t')

# Convertir las columnas de fecha a tipo datetime con información de zona horaria
issues_df['Creation Date'] = pd.to_datetime(issues_df['Creation Date'], utc=True)
issues_df['Done Date'] = pd.to_datetime(issues_df['Done Date'], utc=True)

# Configuración de los sprints
sprints = {
    "Sprint 05: Finalización de la Base del Proyecto": {"start": "2024-06-07", "end": "2024-06-26"}
}

# Constantes para colores
COLOR_PROGRESO_IDEAL = '#ffbb33'
COLOR_TITULO = '#1f77b4'
COLOR_ETIQUETAS = 'black'
COLOR_LEYENDA = 'black'
COLOR_FONDO = '#f0f0f0'

# Función para generar el burndown chart para un sprint específico
def generate_burndown_chart(sprint_name, start_date, end_date):
    # Convertir las fechas del sprint a "tz-aware"
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)
    
    # Filtrar los issues dentro del rango de fechas del sprint
    sprint_df = issues_df[(issues_df['Creation Date'] >= start_date) & (issues_df['Creation Date'] <= end_date)]
    
    if sprint_df.empty:
        print(f"No se encontraron datos para el sprint {sprint_name}")
        return

    # Generar una serie de fechas desde el inicio hasta el fin del sprint
    dates = pd.date_range(start=start_date, end=end_date)

    # Inicializar un DataFrame para el trabajo restante
    burndown_df = pd.DataFrame(index=dates)
    burndown_df['Remaining Work'] = 0

    # Calcular el trabajo restante por día
    total_work = sprint_df['Weight'].sum()
    burndown_df.at[start_date, 'Remaining Work'] = total_work

    for date in dates:
        closed_issues = sprint_df[(sprint_df['Done Date'] <= date)]
        completed_work = closed_issues['Weight'].sum()
        burndown_df.at[date, 'Remaining Work'] = total_work - completed_work

    # Llenar hacia adelante para las fechas sin cambios
    burndown_df['Remaining Work'] = burndown_df['Remaining Work'].ffill()

    # Calcular el progreso ideal
    ideal_progress = [total_work - (total_work / (len(dates) - 1)) * i for i in range(len(dates))]

    # Crear gradiente de color
    cmap = LinearSegmentedColormap.from_list('custom_gradient', ['#33b2ff', '#87cefa'])

    plt.figure(figsize=(12, 8))
    colors = cmap(np.linspace(0, 1, len(burndown_df)))
    plt.bar(burndown_df.index, burndown_df['Remaining Work'], color=colors, label='Progreso Real (Trabajo Restante)')
    plt.plot(dates, ideal_progress, linestyle='--', color=COLOR_PROGRESO_IDEAL, label='Progreso Ideal', linewidth=2)

    # Añadir detalles de estilo
    plt.title(f'Burndown Chart - {sprint_name}', fontsize=16, color=COLOR_TITULO)
    plt.xlabel('Fecha', fontsize=14, color=COLOR_ETIQUETAS)
    plt.ylabel('Trabajo Restante (Story Points)', fontsize=14, color=COLOR_ETIQUETAS)
    plt.xticks(rotation=45)
    plt.legend(facecolor=COLOR_FONDO, edgecolor=COLOR_LEYENDA, fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.gcf().autofmt_xdate()  # Ajustar automáticamente el formato de la fecha

    # Guardar el gráfico como una imagen
    plt.savefig(f'burndown_chart_{sprint_name.replace(" ", "_").replace(":", "")}.png')
    plt.show()

# Generar los burndown charts para cada sprint
for sprint_name, dates in sprints.items():
    start_date = dates['start']
    end_date = dates['end']
    generate_burndown_chart(sprint_name, start_date, end_date)
