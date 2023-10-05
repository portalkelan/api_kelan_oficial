import requests
import openai
import json
import time
from collections import deque
import logging
import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Configuração do Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### Chave da API Open_AI
openai.api_key = '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'

# Link de Reclamação
link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

request_queue = deque()
processed_questions = set()

data = {}  # Inicializando 'data' como um dicionário vazio
url = data
@app.route('/data', methods=['POST'])
def receive_data():
    global data
    data = request.json  # Armazenando o JSON completo na variável 'data'
    print(data)
    return jsonify(data=data), 200

def fetch_and_process_data():
    logging.info("Buscando perguntas...")
    #url = 'https://kelanapi.azurewebsites.net/kelan/info/info'
    #url = request.json
    
    try:
        #response = requests.post(url)
        #response.raise_for_status()
        #data = response.json()

        seller_id = data['allInfo']['seller_id']
        question_id = data['allInfo']['questionId']
        itemName = data['allInfo']['item_name']
        item_id = data['allInfo']['itemId']
        date_created = data['allInfo']['date_created']
        question_text = data['allInfo']['question_text']
        foi_respondida = data['allInfo']['foi_respondida']
        itemDescription = data['allInfo']['itemDescription']

        if question_id in processed_questions:
            logging.info(f"Pergunta {question_id} já foi processada. Descartando...")
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
   
    except requests.RequestException as e:
        logging.error(f"Erro ao chamar a API: {e}")
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar a resposta JSON.")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")


### Conexão e inserir no banco


def loop_function():
    while True:
        request_queue.append({})
        if request_queue:
            fetch_and_process_data()
            request_queue.popleft()
        time.sleep(150)
    
# Crie uma thread para o loop
loop_thread = threading.Thread(target=loop_function)

# Inicie a thread do loop
loop_thread.start()

# Inicie o servidor Flask na thread principal
app.run(debug=False, port=8050, host='172.20.20.33')