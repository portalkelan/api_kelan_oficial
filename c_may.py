import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from datetime import datetime

#import painel_dash
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
    url = 'https://kelanapi.azurewebsites.net/may/name/title'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Erro ao chamar a API (Nome do item): {response.status_code} - {response.text}")
        return

    Name = response.json()
    itemName = Name['newItemData']['title']

##  PERGUNTA
    url = 'https://kelanapi.azurewebsites.net/may/message/question'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Erro ao chamar a API (Pergunta): {response.status_code} - {response.text}")
        return

    question_data = response.json()

    if question_data['questionData']['id'] != previous_question_id:
        queue.append((itemName, question_data))
        previous_question_id = question_data['questionData']['id']

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

## DESCRIÇÃO DO ANÚNCIO 
    url = 'https://kelanapi.azurewebsites.net/may/items/info'
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
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja Kelan Móveis na plataforma Mercado Livre, você é a Kel, assistente virtual da Kelan. Ao final de mensagem, escreva: Att, Kel Equipe Kelan. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre ou pelas nossas redes sociais, será um prazer ajudá-lo!' Caso o cliente não consiga entrar em contato através das mensagens, explique: Infelizmente, de acordo com as regras da plataforma, não podemos direcioná-lo para nossos canais de atendimento, o que você pode fazer é pesquisar nosso nome afim de nos encontrar em outros canais. Não responda perguntas sobre preços, não invente respostas, siga as informações do catalogo e descrição à risca! Catalogo: {itemDescription}"}
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
        url = 'https://kelanapi.azurewebsites.net/may/chat'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
        if response.status_code == 200:
            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

## GUARDA AS CHAVES NO BANCO DE DADOS
        insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply)

def insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO api_may_mlb (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
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