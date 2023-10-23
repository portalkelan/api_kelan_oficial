import dash
from dash import dcc, html, dash_table, Input, Output, exceptions
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
import mysql.connector
from sqlalchemy import create_engine
import logging
from dash.exceptions import PreventUpdate
import collections

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])

# Configuração da conexão com o banco de dados
DATABASE_URI = "mysql+mysqlclient://root:@localhost/kelan"
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_kelan'
}

def fetch_data():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            logging.info("Conexão com o banco de dados estabelecida com sucesso.")
            query = "SELECT * FROM chat_db ORDER BY date_created DESC"
            df = pd.read_sql(query, connection)
            logging.info(f"{len(df)} registros recuperados do banco de dados.")
            return df
        else:
            logging.error("Falha ao conectar ao banco de dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio
    except mysql.connector.Error as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return pd.DataFrame()  # Retorna um DataFrame vazio
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("Conexão com o banco de dados fechada.")

def fetch_data_by_seller_id(seller_id):
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            logging.info("Conexão com o banco de dados estabelecida com sucesso.")
            query = f"SELECT * FROM chat_db WHERE seller_id = '{seller_id}' ORDER BY date_created DESC"
            df = pd.read_sql(query, connection)
            logging.info(f"{len(df)} registros recuperados do banco de dados para seller_id = {seller_id}.")
            return df
        else:
            logging.error("Falha ao conectar ao banco de dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio
    except mysql.connector.Error as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return pd.DataFrame()  # Retorna um DataFrame vazio
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("Conexão com o banco de dados fechada.")

def count_data_by_seller_id():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            logging.info("Conexão com o banco de dados estabelecida com sucesso.")
            query = "SELECT seller_id, COUNT(*) as count FROM chat_db GROUP BY seller_id"
            df = pd.read_sql(query, connection)
            logging.info(f"Quantidade de registros por seller_id obtida com sucesso.")
            return df
        else:
            logging.error("Falha ao conectar ao banco de dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio
    except mysql.connector.Error as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return pd.DataFrame()  # Retorna um DataFrame vazio
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("Conexão com o banco de dados fechada.")

def fetch_interactions_data():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            logging.info("Conexão com o banco de dados estabelecida com sucesso.")
            query = "SELECT seller_id, date_created FROM chat_db"
            df = pd.read_sql(query, connection)
            logging.info(f"{len(df)} registros recuperados do banco de dados.")
            return df
        else:
            logging.error("Falha ao conectar ao banco de dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio
    except mysql.connector.Error as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return pd.DataFrame()  # Retorna um DataFrame vazio
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("Conexão com o banco de dados fechada.")


# ========= App ============== #
FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

df_counts = count_data_by_seller_id()

# Atribuir um ID ao DataFrame
df_counts['id'] = range(1, len(df_counts) + 1)
print(df_counts)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc_css])
app.scripts.config.serve_locally = True
server = app.server
df = fetch_data()

# ========== Styles ============ #

template_theme1 = "pulse"
template_theme2 = "vapor"
url_theme1 = dbc.themes.PULSE
url_theme2 = dbc.themes.VAPOR

tab_card = {'height':'100%'}

# ===== Reading n cleaning File ====== #
#df_main = pd.read_csv("C:/Users/thumb/OneDrive/Área de Trabalho/dash_kelan_1.0/GasPrices-Dash/data_gas.csv")
#df_main.info()
#df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'])
#df_main['DATA FINAL'] = pd.to_datetime(df_main['DATA FINAL'])
#df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL'])/2) + df_main['DATA INICIAL']
#df_main = df_main.sort_values(by='DATA MEDIA', ascending=True)
#df_main.rename(columns= {'DATA MEDIA':'DATA'}, inplace=True)
#df_main.rename(columns= {'PREÇO MÉDIO REVENDA':'VALOR REVENDA (R$/L)'}, inplace=True)
#df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))
#df_main = df_main[df_main.PRODUTO == "GASOLINA COMUM"]
#df_main = df_main.reset_index()
#df_main.info()
#df_main.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA',
#              'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO','PREÇO MÍNIMO DISTRIBUIÇÃO',
#              'MARGEM MÉDIA REVENDA','PREÇO MÍNIMO REVENDA','PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA',
#              'PRODUTO', 'PREÇO MÉDIO DISTRIBUIÇÃO'],inplace=True, axis=1)
#
#df_store = dbc.df_main.to_dict()

# ==========Layout das funçoes ==========
def generate_card(row):
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(str(row['question_id']), md=3, xs=12),
                dbc.Col(str(row['seller_id']), md=3, xs=12),
                dbc.Col(str(row['date_created']), md=3, xs=12),
                dbc.Col(str(row['foi_respondida']), md=3, xs=12),
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
            #html.Hr(),
            #dbc.Col(str(row['foi_respondida']), md=12),
        ],style={'font-size': '15px', 'heigt':''})
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

# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    #dcc.Interval(
    #    id='interval-component',
    #    interval=5*1000,  # em milissegundos, então 5*1000 = 5 segundos
    #    n_intervals=0
    #),
    #dcc.Store(id='dataset', data=df_store),
    #dcc.Store(id='dataset_fixed', data=df_store),

    # Layout
    # Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        html.Img(src="assets/img_card1.jpg", height="70px", style={'align':'top'}),
                        html.Hr()
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Legend("Análise de vendas", style={'font-size':'24px'})
                        ], sm=8),
                        dbc.Col([
                            html.I(className='fa fa-filter', style={'font-size':'300%'})
                        ],sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                            html.Legend("Grupo Kelan LTDA")
                        ])
                    ], style={'margin-top':'10px'}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Atualizar", id="update-button", className="mb-3", style={'width':'100%','font-size':'18px','align':'center'}),
                        ])
                    ], style={'margin-top':'10px'}),
                ])
            ], style={'align':'left'})
        ],sm=4, lg=2,),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Kelan Movéis", tab_id="tab-1_kelan"),
                                dbc.Tab(label="May_Store", tab_id="tab-2_may"),
                                dbc.Tab(label="Ozzy Store", tab_id="tab-3_ozzy"),
                                dbc.Tab(label="Decor Home", tab_id="tab-4_decorhome"),
                                dbc.Tab(label="5 Conta", tab_id="tab-5")
                            ],
                            id="card-tabs",
                            active_tab="tab-1",
                        )
                    ),
                    dbc.CardBody(
                            html.P(id="card-content", className="card-text"),
                            style={
                                'height': '300px',  # Defina a altura desejada aqui
                                'overflowY': 'auto',  # Isso permitirá a rolagem vertical quando o conteúdo exceder a altura definida
                                'overflowX': 'hidden'  # Isso esconderá a rolagem horizontal, mas você pode mudar para 'auto' se quiser que seja visível quando necessário
                            }
                        )

                    ]
                )
            ],style={'align':'center'}),
        ]),
        
        dbc.Row([
            dbc.Col([
                
            ]),
            dbc.Col([
                dbc.Card([
                    dcc.Graph(id='static-counts')
                ])
            ])
        ]) 
    
    ], fluid=True, style={'height': '100%'})

# ======== Callbacks ========== #

@app.callback(
    Output('card-content', 'children'),
    Input('card-tabs', 'active_tab')
)
def update_tab_content(active_tab):
    df = pd.DataFrame()  # Inicialize df com um DataFrame vazio como padrão

    # Aqui, você pode definir lógica específica para cada aba, se necessário.
    # Por exemplo, se diferentes abas precisam buscar dados de diferentes tabelas.
    if active_tab == "tab-1_kelan":
        df = fetch_data_by_seller_id("65131481")
    elif active_tab == "tab-2_may":
        df = fetch_data_by_seller_id("271842978")
    if active_tab == "tab-3_ozzy":
        df = fetch_data_by_seller_id("20020278")
    elif active_tab == "tab-4_decorhome":
        df = fetch_data_by_seller_id("271839457")
    elif active_tab == "tab-5":
        df = fetch_data_by_seller_id("")
    # Se o DataFrame não estiver vazio, gere os cartões
    if not df.empty:
        return [generate_card(row) for _, row in df.iterrows()]
    else:
        return [html.Div("Nenhum dado recuperado do banco de dados.")]
    
###
@app.callback(
    Output('static-counts', 'figure'),
    Input('update-button', 'n_clicks')
)
def update_graph(n):
    # Gerar um DataFrame usando a função count_data_by_seller_id
    #df_counts = count_data_by_seller_id()
    df_interactions = fetch_interactions_data()
    
    df_grouped = df_interactions.groupby(['seller_id', 'date_created']).size().reset_index(name='counts')
    df_pivot = df_grouped.pivot(index='date_created', columns='seller_id', values='counts').fillna(0)

    fig = px.line(df_pivot, 
                  x=df_pivot.index, 
                  y=df_pivot.columns, 
                  title='Interações por Data para Cada Seller ID')
    fig = px.line(df_pivot, 
              x=df_pivot.index, 
              y=df_pivot.columns, 
              title='Interações por Data para Cada Seller ID')

    # Ajustar o tamanho do gráfico
    fig.update_layout(height=600, width=1000)

    # Melhorar a estilização
    fig.update_traces(mode='lines+markers')  # Adiciona marcadores aos pontos de dados

    # Adicionar tooltips
    fig.update_traces(hoverinfo='x+y+name')  # Mostra x, y e nome (seller_id) no tooltip

    # Legendas interativas já são padrão em plotly

    # Para permitir zoom e pan, certifique-se de que o modo de arrasto esteja definido como 'zoom' (que é o padrão)

    return fig


# Run server
if __name__ == '__main__':
    app.run_server(debug=True,threaded=True,port=8050, host='192.168.18.7')

### Alertas

#dbc.Alert("This is a primary alert", color="primary"),
#dbc.Alert("This is a secondary alert", color="secondary"),
#dbc.Alert("This is a success alert! Well done!", color="success"),
#dbc.Alert("This is a warning alert... be careful...", color="warning"),
#dbc.Alert("This is a danger alert. Scary!", color="danger"),
#dbc.Alert("This is an info alert. Good to know!", color="info"),
#dbc.Alert("This is a light alert", color="light"),
#dbc.Alert("This is a dark alert", color="dark"),