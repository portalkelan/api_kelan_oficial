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
    
    link_reclamaçao= ''

## CHAT FORMULA RESPOSTA 
    temperature = 0
    max_tokens = 256
    messages = [
   {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja MAY STORE na plataforma Mercado Livre, você é a May, assistente virtual da MAY STORE. Ao final de mensagem, escreva: Att, May Equipe MAY STORE. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!'.RECLAMAÇÕES:'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!' Horário de atendimento: Seg à Sex das 8h às 18h. Em caso de problemas com o produto, peça que o cliente não abra uma  reclamação e tente entrar em contato conosoco. Não responda perguntas sobre preços, não responda perguntas sobre as notas fiscais, não invente respostas, siga as informações da descrição à risca! NOME DO PRODUTO: {itemName}, DESCRIÇAO: {itemDescription}"}
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