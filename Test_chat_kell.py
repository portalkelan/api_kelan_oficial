import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from datetime import datetime
from catalogo_kelan import catalogo
from ultima_pergunta import pergunta, detalhe_item, titulo_item

## Converte a notação da hora para o padrão brasileiro 
def converter_formato_com_hora(data_iso):
    data_objeto = datetime.fromisoformat(data_iso)
    data_br = data_objeto.strftime('%d/%m/%y %H:%M:%S')
    return data_br

openai.api_key = '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'  # Sua chave da API OpenAI

## Cria o sistema de fila a partir do id da pergunta
previous_question_id = ""
queue = []

## Inicia as requisições
def fetch_data_to_queue():
    global previous_question_id

##  NOME DO ITEM/ANÚNCIO
# PEGANDO A pergunta do cliente
pergunta_cliente = pergunta

# PEGANDO A titulo do itens 
itemName = titulo_item

# PEGANDO A  DESCRIÇÃO 
itemDescription = detalhe_item

def process_queue():
    if not queue:
        return

    itemName, question_data = queue.pop(0)
    process_data(itemName, question_data)

## Separa as chaves que serão usadas para formular resposta ou guardar no banco de dados
def process_data(itemName, question_data):
    question_text = question_data['questionData']['text']
    question_id = question_data['questionData']['id']
    seller_id = question_data['questionData']['seller_id']
    item_id = question_data['questionData']['item_id']
    date_created = converter_formato_com_hora(question_data['questionData']['date_created'])

    print(f"Produto: {itemName}")
    print(f"Seller ID: {seller_id}")
    print(f"Question ID: {question_id}")
    print(f"Date Created: {date_created}")
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
insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply)

def insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan_db', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO chat_db (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply)
            cursor.execute(query, values)
            con.commit()
            print(cursor.rowcount, "Registro inserido.")
    except Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            print("Conexão com o MySQL encerrada")
            
## LOOP 5 EM 5 MINUTOS
while True:
    print("buscando perguntas...")  # Mensagem informando que está buscando perguntas
    fetch_data_to_queue()
    process_queue()
    time.sleep(300)