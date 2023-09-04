import os
import mysql.connector
from mysql.connector import Error
import requests
import openai
import time
from datetime import datetime
import logging
import json

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Configurações
API_KEY = os.environ.get('OPENAI_API_KEY')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'kelan_db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', '')
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 300))

openai.api_key = API_KEY

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados."""
    try:
        con = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        return con
    except Error as e:
        logging.error(f"Erro ao conectar ao MySQL: {e}")
        return None

def insert_into_database(con, data):
    """Insere os dados no banco de dados."""
    try:
        cursor = con.cursor()
        query = """
        INSERT IGNORE INTO chat_db 
        (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, data)
        con.commit()
        logging.info(f"{cursor.rowcount} Registro inserido.")
    except Error as e:
        logging.error(f"Erro ao inserir no banco de dados: {e}")

def process_queue(queue):
    """Processa a fila de perguntas."""
    if not queue:
        return

    itemName, question_data = queue.pop(0)
    process_data(itemName, question_data)

def process_data(itemName, question_data):
    """Processa os dados e interage com a API."""
    # ... (restante do código, similar ao original, mas com tratamento de erros e logging)
    question_text = question_data['questionData']['text']
    question_id = question_data['questionData']['id']
    seller_id = question_data['questionData']['seller_id']
    item_id = question_data['questionData']['item_id']
    #date_created = converter_formato_com_hora(question_data['questionData']['date_created'])

    print(f"Produto: {itemName}")
    print(f"Seller ID: {seller_id}")
    print(f"Question ID: {question_id}")
    #print(f"Date Created: {date_created}")
    print(f"Item ID: {item_id}")
    print(f"Texto da pergunta: {question_text}")

## DESCRIÇÃO DO ANÚNCIO 
    url = 'https://kelanapi.azurewebsites.net/items/info'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Erro ao chamar a API (Descrição do item): {response.status_code} - {response.text}")
        return

    item = response.json()
    itemDescription = item['itemData']['plain_text']
    print(itemDescription)

## CHAT FORMULA RESPOSTA 
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja Kelan Móveis na plataforma Mercado Livre, você é a Kel, assistente virtual da Kelan. Ao final de mensagem, escreva: Att, Kel Equipe Kelan. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre ou pelas nossas redes sociais, será um prazer ajudá-lo!' Caso o cliente não consiga entrar em contato através das mensagens, explique: Infelizmente, de acordo com as regras da plataforma, não podemos direcioná-lo para nossos canais de atendimento, o que você pode fazer é pesquisar nosso nome afim de nos encontrar em outros canais. Não responda perguntas sobre preços, não invente respostas, siga as informações do catalogo e descrição à risca! Catalogo: {itemDescription} + {catalogo}"}
    ]
    message = question_text
    print(f"Message: {message}")
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

## POSTA A RESPOSTA NO MELI
        url = 'https://kelanapi.azurewebsites.net/chat'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
        if response.status_code == 200:
            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

## GUARDA AS CHAVES NO BANCO DE DADOS
        insert_into_database(question_id, seller_id, item_id, question_text, itemName, itemDescription, reply)


def fetch_data_to_queue():
    """Busca dados da API e adiciona à fila."""
    # ... (restante do código, similar ao original, mas com tratamento de erros e logging)
    global previous_question_id

##  NOME DO ITEM/ANÚNCIO
    url = 'https://kelanapi.azurewebsites.net/name/title'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Erro ao chamar a API (Nome do item): {response.status_code} - {response.text}")
        return

    Name = response.json()
    itemName = Name['newItemData']['title']

##  PERGUNTA
    url = 'https://kelanapi.azurewebsites.net/message/question'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Erro ao chamar a API (Pergunta): {response.status_code} - {response.text}")
        return

    question_data = response.json()
    if question_data['questionData']['id'] != previous_question_id:
        #queue.append((itemName, question_data))
        previous_question_id = question_data['questionData']['id']


def main():
    """Loop principal para buscar e processar perguntas."""
    while True:
        logging.info("Buscando perguntas...")
        fetch_data_to_queue()
        process_queue()
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()
