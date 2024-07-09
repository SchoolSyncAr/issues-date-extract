import requests
import pandas as pd
import re

# Configura tu token de acceso personal de GitHub

# Lee el archivo TSV de issues
try:
    issues_df = pd.read_csv('issues-todos.tsv', sep='\t')
    print("Archivo leído correctamente.")
except pd.errors.EmptyDataError:
    print("Error: El archivo 'issues.tsv' está vacío o no contiene datos legibles.")
    exit(1)
except FileNotFoundError:
    print("Error: El archivo 'issues.tsv' no se encontró.")
    exit(1)

# Define la cabecera para la autenticación en la API de GitHub
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Función para obtener la fecha de creación y la fecha en que el issue se marcó como "DONE"
def get_issue_dates(repo_owner, repo_name, issue_number):
    issue_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}'
    response = requests.get(issue_url, headers=headers)
    if response.status_code == 200:
        issue_data = response.json()
        print("procesando: " + issue_data['title'])
        created_at = issue_data['created_at']
    else:
        print(f'Error al obtener el issue {issue_number} del repositorio {repo_name}: {response.status_code}')
        return None, None
    
    events_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/events'
    response = requests.get(events_url, headers=headers)
    if response.status_code == 200:
        events = response.json()
        for event in events:
            if event['event'] == 'closed':
                done_at = event['created_at']
                return created_at, done_at
    else:
        print(f'Error al obtener los eventos del issue {issue_number} del repositorio {repo_name}: {response.status_code}')
    
    return created_at, None

# Añadir las columnas de fechas de creación y "DONE" al DataFrame
creation_dates = []
done_dates = []
for index, row in issues_df.iterrows():
    issue_url = row['URL']
    match = re.search(r'https://github.com/([^/]+)/([^/]+)/issues/(\d+)', issue_url)
    if match:
        repo_owner = match.group(1)
        repo_name = match.group(2)
        issue_number = match.group(3)
        creation_date, done_date = get_issue_dates(repo_owner, repo_name, issue_number)
        creation_dates.append(creation_date)
        done_dates.append(done_date)
    else:
        creation_dates.append(None)
        done_dates.append(None)
        print(f'Error al extraer información del URL: {issue_url}')

issues_df['Creation Date'] = creation_dates
issues_df['Done Date'] = done_dates

# Guardar el DataFrame actualizado en un nuevo archivo TSV
issues_df.to_csv('updated_issues.tsv', sep='\t', index=False)

print('Archivo actualizado con las fechas de creación y "DONE" guardado como updated_issues.tsv')
