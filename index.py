import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash_bootstrap_templates
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objs as go
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import ThemeSwitchAIO
import mysql.connector
from sqlalchemy import create_engine

# Configuração da conexão com o banco de dados
DATABASE_URI = "mysql+mysqlclient://root:@localhost/kelan"
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kelan'
}

def fetch_data():
    connection = mysql.connector.connect(**config)
    query = "SELECT * FROM api_kelan_mlb, api_may_mlb ORDER BY date_created DESC"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def generate_card(row):
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(str(row['question_id']), md=4, xs=12),
                dbc.Col(str(row['seller_id']), md=4, xs=12, className='text-center'),
                dbc.Col(str(row['date_created']), md=4, xs=12, className='text-right'),
            ]),
            html.Hr(),
            dbc.Row([
                dbc.Col(str(row['item_id']), md=6, xs=12),
                dbc.Col(str(row['itemName']), md=6, xs=12, className='text-center'),
            ]),
            html.Hr(),
            dbc.Col(str(row['item_Description']), md=12),
            html.Hr(),
            dbc.Col(str(row['question_text']), md=12),
            html.Hr(),
            dbc.Col(str(row['response_json']), md=12),
        ],style={'font-size': '15px'})
    ], className='bg-dark text-white mb-3', style={'border': '1px solid white', 'padding': '10px', 'margin': '10px', 'color': 'white'})

def generate_tab_content():
    return dbc.Card([
        html.Div([
            html.H4('Dashboard Kelan Móveis', style={'display': 'inline-block'}),
            html.Button('Atualizar', id='update-button', style={'align': 'left','width': '10%'}),
            html.Div(id='cards-container', children=[
                generate_card(row) for _, row in df.iterrows()
            ], style={'overflowY': 'scroll', 'height': '38vh', 'padding': '10px'}),
            html.Div([
                html.H4('Quantidade de Dados'),
                html.Div(f'Total de registros: {len(df)}')
            ])
        ], style={'padding': '20px'})
    ], style={'width': '98%'})

template_theme1 = "quartz"
template_theme2 = "zephyr"
url_theme1 = dbc.themes.QUARTZ
url_theme2 = dbc.themes.ZEPHYR
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

app = dash.Dash(__name__)
server = app.server
df = fetch_data()

app.layout = html.Div([
    dbc.Navbar(
        html.Div([
            html.A(
                dbc.Row([
                    dbc.Col([
                        dbc.Row(html.Img(src=PLOTLY_LOGO, height="50px", style={'align':'left'})),
                    ]),
                    dbc.Col([
                        dbc.Row(dbc.NavbarBrand("Dashboard para análise"), style={'height':'20%'}),
                    ]),
                    dbc.Col(
                        ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                        width="auto",
                    ),
                ]),
                href="",
                style={"textDecoration": "none"},
            ),
        ],style={'align':'left'}),
        color="dark",
        dark=True,
    ),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Img(src=app.get_asset_url('../assets/img1.jpg'), className="img-fluid", style={"display": "flex", "justify-content": "center"}),
                html.Hr(),
            ], style={"margin": "20px", "padding": "20px", "height": "84vh"})
        ], md=3, xs=12),
        dbc.Col([
            dbc.Row([
                dbc.Tabs([
                    dbc.Tab(generate_tab_content(), label="Aba 1"),
                    dbc.Tab(generate_tab_content(), label="Aba 2")
                ])
            ])
        ], md=9, xs=12),
    ]),
])

@app.callback(
    Output('cards-container', 'children'),
    Input('update-button', 'n_clicks')
)
def update_data(n):
    if n is None:
        raise dash.exceptions.PreventUpdate
    df = fetch_data()
    return [generate_card(row) for _, row in df.iterrows()]

if __name__=="__main__":
    app.run_server(debug=True, port=8050, host='172.20.20.33')
