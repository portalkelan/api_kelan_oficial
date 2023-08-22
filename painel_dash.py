from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template


df_data = pd.read_csv("supermarket_sales.csv")
df_data["Date"] = pd.to_datetime(df_data["Date"])

app = dash.Dash(__name__)
server = app.server

# Conectar ao banco de dados MySQL
def connect_to_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan'
    )
    return conn

# Obter dados do banco de dados
def get_data_from_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id_item, pergunta, title_item, datas_horas FROM respostas')
    data = cursor.fetchall()
    conn.close()
    return data

data = get_data_from_db()
df = pd.DataFrame(data, columns=['ID', 'Pergunta', 'Ti­tulo', 'Datas e Horas'])

app.layout = html.Div([
    html.H1('Dashboard de VisualizaÃ§Ã£o de Dados', className='text-center'),
    dash_table.DataTable(
        id='table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records')
    )
])

if __name__ == "__main__":
    app.run_server(port=8050,debug=True)
#Ask AI to edit or generate...