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

# Configuração da conexão com o banco de dados
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kelan'
}

# Função para buscar dados do banco
def fetch_data():
    connection = mysql.connector.connect(**config)
    query = "SELECT * FROM api_kelan_mlb ORDER BY date_created ASC"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Função para criar um card para cada linha do DataFrame
def generate_card(row):
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(str(row['question_id'])),
                dbc.Col(str(row['seller_id']), className='text-center'),
                dbc.Col(str(row['date_created']), className='text-right'),
            ]),
            html.Hr(),
            dbc.Row([
                dbc.Col(str(row['item_id'])),
                dbc.Col(str(row['itemName']), className='text-center'),
            ]),
            html.Hr(),
            dbc.Col(str(row['item_Description'])),
            html.Hr(),
            dbc.Col(str(row['question_text'])),
            html.Hr(),
            dbc.Col(str(row['response_json'])),
        ],style={'font-size': '15px'})
    #], className='bg-dark text-white mb-3')
    ], className='bg-dark text-white mb-3', style={'border': '1px solid white', 'padding': '10px', 'margin': '10px', 'color': 'white'})


template_theme1 = "quartz"
template_theme2 = "zephyr"
url_theme1 = dbc.themes.QUARTZ
url_theme2 = dbc.themes.ZEPHYR

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
           ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

app = dash.Dash(__name__)
server = app.server

df = fetch_data()
#==================== Layout ====================
app.layout = html.Div([
        dbc.Navbar(
        html.Div(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
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
                        ],
                    ),
                    href="",
                    style={"textDecoration": "none"},
                ),
                
            ],style={'align':'left'},
        ),
        color="dark",
    dark=True,
    ),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                [
                    html.Img(src=app.get_asset_url('logo_kelan2.png'),style={"display": "flex", "justify-content": "center","lenght":"50%", "width":"70%"}),
            
                    html.Hr(),
                    
                ], style={"margin": "20px", "padding": "20px", "height": "84vh"})
        ], md=3),
        dbc.Col([
            dbc.Row([
                dbc.Card([
                html.H4("Menu Principal"),
                html.Div(html.Button('Atualizar', id='update-button', style={'align': 'left','width': '10%'}))
                
                ], style={"margin": "20px", "padding": "20px",'width': '96%'}),
                dbc.Card([
                        html.Div([
                        html.H4('Dashboard Kelan Móveis', style={'display': 'inline-block'}),
                        
                        # Cards
                        html.Div(id='cards-container', children=[
                            generate_card(row) for _, row in df.iterrows()
                        ], style={'overflowY': 'scroll', 'height': '38vh', 'padding': '10px'}),
                        
                        # Dashboards
                        html.Div([
                            html.H4('Quantidade de Dados'),
                            html.Div(f'Total de registros: {len(df)}')
                            ])
                        ], style={'padding': '20px'})
                        
                    ],style={'width': '98%'}),
                ])
            ]),
            
            ]),
        ])
#, style={"display": "flex", "justify-content": "top"}
#============ Call Backs ===============
# Callback para atualizar os dados quando o botão for clicado
@app.callback(
    Output('cards-container', 'children'),
    Input('update-button', 'n_clicks')
)
def update_data(n):
    if n is None:
        raise dash.exceptions.PreventUpdate

    df = fetch_data()
    return [generate_card(row) for _, row in df.iterrows()]




#================ Run Server ==============
if __name__=="__main__":
    app.run_server(debug=True, port=8050, host='172.20.20.33')

