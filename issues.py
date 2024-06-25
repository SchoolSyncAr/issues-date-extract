import requests
import pandas as pd
import re

# Configura tu token de acceso personal de GitHub
GITHUB_TOKEN = ''

# Lee el archivo TSV de issues
try:
    issues_df = pd.read_csv('issues.tsv', sep='\t')
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

# Función para obtener la fecha de creación y cierre de un issue
def get_issue_dates(repo_owner, repo_name, issue_number):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        issue_data = response.json()
        return issue_data['created_at'], issue_data.get('closed_at')
    else:
        print(f'Error al obtener el issue {issue_number} del repositorio {repo_name}: {response.status_code}')
        return None, None

# Añadir las columnas de fechas de creación y cierre al DataFrame
creation_dates = []
closure_dates = []
for index, row in issues_df.iterrows():
    issue_url = row['URL']
    match = re.search(r'https://github.com/([^/]+)/([^/]+)/issues/(\d+)', issue_url)
    if match:
        repo_owner = match.group(1)
        repo_name = match.group(2)
        issue_number = match.group(3)
        creation_date, closure_date = get_issue_dates(repo_owner, repo_name, issue_number)
        creation_dates.append(creation_date)
        closure_dates.append(closure_date)
    else:
        creation_dates.append(None)
        closure_dates.append(None)
        print(f'Error al extraer información del URL: {issue_url}')

issues_df['Creation Date'] = creation_dates
issues_df['Closure Date'] = closure_dates

# Guardar el DataFrame actualizado en un nuevo archivo TSV
issues_df.to_csv('updated_issues.tsv', sep='\t', index=False)

print('Archivo actualizado con las fechas de creación y cierre guardado como updated_issues.tsv')
