import requests
import openai
import json
import time
from collections import deque
import logging
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template
import threading
from collections import deque
import dash
from dash import dcc, html, dash_table, Input, Output, exceptions
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
from sqlalchemy import create_engine
from dash.exceptions import PreventUpdate

# Configuração do Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
logger = logging.getLogger(__name__)

# Configuração da conexão com o banco de dados
DATABASE_URI = "mysql+mysqlclient://root:@localhost/kelan"
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kelan1'
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

### Chave da API Open_AI
openai.api_key = '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'

# Link de Reclamação
link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

request_queue = deque()
processed_questions = set()

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
        ],style={'font-size': '15px', 'heigt':'100%'})
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
                
            ], style={'margin-top':'10px'}),
            dbc.Col([
                dbc.Card([
                    dcc.Graph(id='static-counts')
                ], style={'margin-top':'10px'})
            ])
        ], style={'margin-top':'10px'}) 
    
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
    fig.update_layout(height=400, width=600)

    # Melhorar a estilização
    fig.update_traces(mode='lines+markers')  # Adiciona marcadores aos pontos de dados

    # Adicionar tooltips
    fig.update_traces(hoverinfo='x+y+name')  # Mostra x, y e nome (seller_id) no tooltip

    # Legendas interativas já são padrão em plotly

    # Para permitir zoom e pan, certifique-se de que o modo de arrasto esteja definido como 'zoom' (que é o padrão)

    return fig

# Funções do robo
def fetch_and_process_data():
    logging.info("Buscando perguntas...")
    url = 'https://testeappi.azurewebsites.net/kelan/info/info'
    logging.info("Antes da resposta recebida da API.")
    try:
        
        logging.info("Chamando a API...")
        response = requests.post(url)
        logging.info("Resposta recebida da API.")
        response.raise_for_status()
        logging.info("Depois da resposta recebida da API.")

        data = response.json()

        seller_id = data['allInfo']['seller_id']
        question_id = data['allInfo']['questionId']
        itemName = data['allInfo']['item_name']
        item_id = data['allInfo']['itemId']
        date_created = data['allInfo']['date_created']
        question_text = data['allInfo']['question_text']
        foi_respondida = data['allInfo']['foi_respondida']
        itemDescription = data['allInfo']['itemDescription']

        if question_id in processed_questions:
            logging.info(f"Descartando pergunta {question_id} pois já foi processada.")
        else:
            logging.info(f"Conta:{seller_id}")
            logging.info(f"Question ID:{question_id}")
            logging.info(f"Anúncio: {itemName}")
            logging.info(f"Item ID: {item_id}")
            logging.info(f"Data/Hora: {date_created}")
            logging.info(f"Pergunta: {question_text}")
            logging.info(f"Status: {foi_respondida}")
            logging.info(f"Descrição: {itemDescription}")

            kelan_id = 65131481
            may_id = 271842978
            oz_id = 20020278
            decorhome_id = 271839457

            temperature = 0
            max_tokens = 256
            messages = [
               {"role": "system", "content": f"Atue como atendente e responda sobre produtos de uma loja no Mercado Livre usando o catálogo: CATALOGO: {itemDescription} e NOME DO PRODUTO: {itemName} . Se não souber, responda: 'Olá, não tenho essa informação disponível no momento. Não invente. Use o catálogo fielmente. Caso a pergunta seja uma reclamação, use este link {link_reclamaçao}. Por favor, confira as informações na descrição do anúncio ou contate-nos no Mercado Livre ou redes sociais. Limite: 256 caracteres. NÃO fale sobre preços, envios full, notas fiscais."} 
            ]

            if seller_id == kelan_id: 
                messages.append({"role": "system", "content": 'No final de cada resposta, adicione a seguinte mensagem: Att Kel, equipe Kelan'})
            elif seller_id == oz_id:
                messages.append({"role": "system", "content": 'No final de cada resposta, adicione a seguinte mensagem: Att Ozzy, equipe OZ STORE'})
            elif seller_id == may_id:
                messages.append({"role": "system", "content": 'No final de cada resposta, adicione a seguinte mensagem: Att May, equipe MAY STORE'})
            elif seller_id == decorhome_id:
                messages.append({"role": "system", "content": 'No final de cada resposta, adicione a seguinte mensagem: Att Deco, equipe DECORE HOME STORE'})
                   
            message = question_text
            print(f"Message: {message}")

            if 'preço' in message or 'valor' in message:
                reply = 'Olá! O preço dos produtos está identificado no próprio anúncio. Att'
            elif 'frete' in message or 'entrega' in message or 'envio' in message:
                reply = 'O cálculo do frete e entrega pela transportadora são responsabilidade da plataforma, portanto recomendo que entre em contato com o suporte do Meli para mais informações, ou entre em contato conosco através das mensagens para que possamos tentar resolver da melhor forma! Att'
            elif 'full' in message:
                reply = 'Olá! Como assistente virtual, não possuo acesso às informações sobre os envios full (um envio é full quando o produto já se encontra no centro de distribuição, e a entrega é feita pela transportadora do Meli), caso queira mais informações sobre os envios full, contate o suporte do Mercado Livre ou confira as informações do anúncio! Att'
                
            if message:
                messages.append(
                    {"role": "user", "content": message},
                )
                chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                reply = chat.choices[0].message.content
                print(f"ChatGPT: {reply}")
                messages.append({"role": "assistant", "content": reply})
                
                response_dict = {"/": reply}

            insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida)

            # POSTA A RESPOSTA NO MELI
            if seller_id == oz_id:
                        url = 'https://testeappi.azurewebsites.net/oz/chat'
                        headers = {'Content-Type': 'application/json'}
                        logging.info(f"Postando resposta para a URL: {url}...")
                        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
                        logging.info(f"Resposta postada com status: {response.status_code}.")
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

            elif seller_id == kelan_id: 
                        url = 'https://testeappi.azurewebsites.net/kelan/chat'
                        headers = {'Content-Type': 'application/json'}
                        logging.info(f"Postando resposta para a URL: {url}...")
                        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
                        logging.info(f"Resposta postada com status: {response.status_code}.")
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

            elif seller_id == may_id:
                        url = 'https://testeappi.azurewebsites.net/may/chat'
                        headers = {'Content-Type': 'application/json'}
                        logging.info(f"Postando resposta para a URL: {url}...")
                        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
                        logging.info(f"Resposta postada com status: {response.status_code}.")
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
                            
            elif seller_id == decorhome_id:  
                        url = 'https://testeappi.azurewebsites.net/decorhome/chat'
                        headers = {'Content-Type': 'application/json'}
                        logging.info(f"Postando resposta para a URL: {url}...")
                        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
                        logging.info(f"Resposta postada com status: {response.status_code}.")
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
            else:
                        print("Execução interrompida")

        processed_questions.add(question_id)

    except requests.RequestException as e:
        logging.error(f"Erro ao chamar a API: {e}")
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar a resposta JSON.")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")

### Conexão e inserir no banco
def insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan1', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO chat_db (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json, foi_respondida) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida)
            logging.info(f"Tentando inserir a pergunta {question_id} no banco de dados...")
            cursor.execute(query, values)
            logging.info(f"Pergunta {question_id} inserida com sucesso.")
            con.commit()
            logger.info(f"{cursor.rowcount} Registro inserido.")
    except Error as e:
        logger.error(f"Erro ao conectar ao MySQL: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            logger.info("Conexão com o MySQL encerrada")

def loop_function():
    logging.info("Iniciando loop_function...")
    while True:
        request_queue.append({})
        if request_queue:
            fetch_and_process_data()
            request_queue.popleft()
        time.sleep(150)
logging.info("Finalizando loop_function...")
# Crie uma thread para o loop
loop_thread = threading.Thread(target=loop_function)

# Inicie a thread do loop
loop_thread.start()
# Run server
if __name__ == '__main__':
    logging.info("Iniciando o aplicativo...")
    # Run server
if __name__ == '__main__':
    app.run_server(debug=True,threaded=True,port=8050, host='172.20.20.37')


### Alertas
#dbc.Alert("This is a primary alert", color="primary"),
#dbc.Alert("This is a secondary alert", color="secondary"),
#dbc.Alert("This is a success alert! Well done!", color="success"),
#dbc.Alert("This is a warning alert... be careful...", color="warning"),
#dbc.Alert("This is a danger alert. Scary!", color="danger"),
#dbc.Alert("This is an info alert. Good to know!", color="info"),
#dbc.Alert("This is a light alert", color="light"),
#dbc.Alert("This is a dark alert", color="dark"),