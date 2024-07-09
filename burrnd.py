import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo TSV
issues_df = pd.read_csv('updated_issues.tsv', sep='\t')

# Convertir a formato de fecha
issues_df['Creation Date'] = pd.to_datetime(issues_df['Creation Date'])
issues_df['Closure Date'] = pd.to_datetime(issues_df['Closure Date'])

# Extraer las fechas de inicio y fin de cada sprint
sprints = {
    sprint: (issues_df[issues_df['Sprint'] == sprint]['Creation Date'].min(),
             issues_df[issues_df['Sprint'] == sprint]['Closure Date'].max())
    for sprint in issues_df['Sprint'].unique()
}

# Función para generar gráfico de burndown
def generate_burndown_chart(sprint_name, start_date, end_date):
    sprint_df = issues_df[(issues_df['Creation Date'] >= start_date) & (issues_df['Creation Date'] <= end_date) & (issues_df['Sprint'] == sprint_name)]
    
    sprint_days = pd.date_range(start=start_date, end=end_date)
    ideal_burndown = [sprint_df['Weight'].sum() * (1 - i / len(sprint_days)) for i in range(len(sprint_days))]
    
    daily_remaining_sp = sprint_df.groupby('Closure Date')['Weight'].sum().reindex(sprint_days, fill_value=0).cumsum()[::-1]
    
    plt.figure(figsize=(12, 6))
    plt.plot(sprint_days, ideal_burndown, label='Progreso Ideal', linestyle='--', color='green')
    plt.bar(sprint_days, daily_remaining_sp, label='Progreso Real', color='blue')
    
    plt.xlabel('Días del Sprint')
    plt.ylabel('Esfuerzo Pendiente (sp)')
    plt.title(f'Burndown Chart - {sprint_name}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Generar gráficos de burndown para cada sprint
for sprint_name, (start_date, end_date) in sprints.items():
    generate_burndown_chart(sprint_name, start_date, end_date)
