import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Definir constantes para los colores
COLOR_TRABAJO_COMPLETADO = '#2E8B57'  # Color verde más agradable
COLOR_PROGRESO_IDEAL = '#FFD700'  # Color dorado
COLOR_FONDO = '#F5F5F5'  # Color de fondo más suave
COLOR_LINEAS = '#333333'  # Color de líneas más suave
COLOR_REJILLA = '#CCCCCC'  # Color de la rejilla
COLOR_TITULO = '#1D90B0'  # Color del título

# Leer el archivo TSV
issues_df = pd.read_csv('updated_issues.tsv', sep='\t')

# Convertir a formato de fecha
issues_df['Creation Date'] = pd.to_datetime(issues_df['Creation Date'])
issues_df['Closure Date'] = pd.to_datetime(issues_df['Closure Date'])

# Filtrar los datos para considerar solo los sprints válidos
valid_sprints = ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Sprint 5']
issues_df = issues_df[issues_df['Sprint'].isin(valid_sprints)]

# Extraer las fechas de inicio y fin de cada sprint
sprints = {
    sprint: (issues_df[issues_df['Sprint'] == sprint]['Creation Date'].min(),
             issues_df[issues_df['Sprint'] == sprint]['Closure Date'].max())
    for sprint in valid_sprints
}

# Ordenar los sprints por fechas de inicio
sprints = dict(sorted(sprints.items(), key=lambda x: x[1][0]))

# Función para calcular coeficientes de la línea recta por mínimos cuadrados
def calcular_recta_minimos_cuadrados(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x * y)
    sum_x_squared = sum(x ** 2)
    
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    b = (sum_y - m * sum_x) / n
    
    return m, b

# Función para generar gráfico de burnup con línea de progreso ideal por mínimos cuadrados
def generate_burnup_chart():
    total_backlog = issues_df['Weight'].sum()
    sprint_names = list(sprints.keys())
    completed_points = []
    
    for sprint in sprint_names:
        sprint_df = issues_df[issues_df['Sprint'] == sprint]
        completed_points.append(sprint_df['Weight'].sum())

    cumulative_points = [sum(completed_points[:i+1]) for i in range(len(completed_points))]
    
    # Calcular la línea de progreso ideal por mínimos cuadrados
    x_values = np.arange(len(sprint_names))
    m_ideal, b_ideal = calcular_recta_minimos_cuadrados(x_values, cumulative_points)
    regression_line_ideal = [m_ideal * x + b_ideal for x in x_values]
    
    plt.figure(figsize=(14, 8), facecolor=COLOR_FONDO)
    plt.plot(sprint_names, cumulative_points, label='Trabajo Completado', color=COLOR_TRABAJO_COMPLETADO, marker='o', linewidth=2)
    plt.plot(sprint_names, regression_line_ideal, label='Progreso Ideal (Mínimos Cuadrados)', color=COLOR_PROGRESO_IDEAL, linestyle='--', linewidth=2)
    
    plt.xlabel('Sprints', fontsize=14, color=COLOR_TITULO)
    plt.ylabel('Puntos de Historia', fontsize=14, color=COLOR_TITULO)
    plt.title('Burnup Chart', fontsize=18, color=COLOR_TITULO, pad=20)
    plt.legend(loc='upper left', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.7, color=COLOR_REJILLA)
    plt.tight_layout()
    plt.xticks(fontsize=12, color=COLOR_LINEAS)
    plt.yticks(fontsize=12, color=COLOR_LINEAS)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color(COLOR_LINEAS)
    plt.gca().spines['bottom'].set_color(COLOR_LINEAS)
    plt.gca().xaxis.label.set_color(COLOR_LINEAS)
    plt.gca().yaxis.label.set_color(COLOR_LINEAS)
    plt.show()

# Generar gráfico de burnup con línea de progreso ideal por mínimos cuadrados
generate_burnup_chart()
