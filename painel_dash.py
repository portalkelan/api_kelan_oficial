import mysql.connector
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Configuração da conexão com o banco de dados
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kelan'
}

# Estabelecer conexão
connection = mysql.connector.connect(**config)

# Buscar dados
query = "SELECT * FROM api_kelan_mlb"
df = pd.read_sql(query, connection)

# Fechar conexão
connection.close()

# Inicializar o app Dash
app = dash.Dash(__name__)

# Layout do app
app.layout = html.Div([
    html.H1('Dashboard Kelan Móveis'),
    
    # Tabela
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10
        )
    ]),
    
    # Dashboards
    html.Div([
        html.H2('Quantidade de Dados'),
        html.Div(id='data-count')
    ])
])

# Callback para atualizar o dashboard
@app.callback(
    Output('data-count', 'children'),
    Input('table', 'data')
)
def update_dashboard(data):
    return f'Total de registros: {len(data)}'

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='172.20.20.33')
