import requests
import openai
from datetime import datetime
from botcity.core import DesktopBot
import json
import logging
import mysql.connector
from mysql.connector import Error
import time

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para converter a notação da hora para o padrão brasileiro
def get_current_datetime():
    # Obtenha a data e hora atual
    now = datetime.now()
    # Formate a data e hora no formato apropriado para o MySQL
    formatted_now = now.strftime('%H:%M:%S')
    return formatted_now

openai.api_key = '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'
link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

## CRia uma lista das contascom os links para postagens
global postagem
postagem = [{
    '65131481':'https://kelanapi.azurewebsites.net/kelan/chat', '271842978':'https://kelanapi.azurewebsites.net/may/chat', '20020278':'https://kelanapi.azurewebsites.net/oz/chat', '271839457':'https://kelanapi.azurewebsites.net/decorhome/chat'
}]

def process():
    url = (postagem)
    
    response = requests.post(url, timeout=60)

    if response.status_code != 200:
        logger.error(f"Erro ao chamar a API (Nome do item): {response.status_code} - {response.text}")
    else:
        # Transforma o conteúdo da resposta em um objeto JSON (dicionário ou lista)
        data = response.json()
        ##SEPARANDO OS DADOS 
        seller_id = data['allInfo']['seller_id']
        questionId = data['allInfo']['questionId']
        itemName = data['allInfo']['item_name']
        itemId = data['allInfo']['itemId']
        date_created = data['allInfo']['date_created']
        question_text = data['allInfo']['question_text']
        foi_respondida = data['allInfo']['foi_respondida']
        itemDescription = data['allInfo']['itemDescription']

        print(f"Conta:{seller_id}")
        print(f"Question ID:{questionId}")
        print(f"Anúncio: {itemName}")
        print(f"Item ID: {itemId}")
        print(f"Data/Hora: {date_created}")
        print(f"Pergunta: {question_text}")
        print(f"Status: {foi_respondida}")
        print(f"Descrição: {itemDescription}")

    # Verifique se a pergunta foi respondida
    if foi_respondida == "Answered":
        # Armazene a pergunta em uma lista de perguntas descartadas
        perguntas_descartadas.append(question_text)
        logger.info("Pergunta descartada: foi respondida anteriormente.")
    else:
        # CHAT FORMULA RESPOSTA
        temperature = 0
        max_tokens = 256
        messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja KELAN MOVEIS na plataforma Mercado Livre.Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!'.RECLAMAÇÕES:'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!' Horário de atendimento: Seg à Sex das 8h às 18h. Em caso de problemas com o produto, peça que o cliente não abra uma  reclamação e tente entrar em contato conosoco. Não responda perguntas sobre preços, não responda perguntas sobre as notas fiscais, não invente respostas, siga as informações da descrição à risca! NOME DO PRODUTO: {itemName}, DESCRIÇAO: {itemDescription}"}
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
        logger.info(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})
        response_dict = {"/": reply}

    insert_into_database(questionId, seller_id, date_created, itemId, question_text, itemName, itemDescription, reply, foi_respondida)

    # POSTA A RESPOSTA NO MELI
    url = (postagem)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(response_dict), headers=headers, timeout=60)
    if response.status_code == 200:
        logger.info(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
    else:
        logger.error(f'Erro ao postar resposta: {response.status_code} - {response.text}')

# Lista para armazenar perguntas descartadas
perguntas_descartadas = []

# GUARDA AS CHAVES NO BANCO DE DADOS
    
### Conexão e inserir no banco
def insert_into_database(questionId, seller_id, date_created, itemId, question_text, itemName, itemDescription, reply, foi_respondida):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO api_kelan_mlb (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (questionId, seller_id, date_created, itemId, question_text, itemName, itemDescription, reply, foi_respondida)
            cursor.execute(query, values)
            con.commit()
            logger.info(f"{cursor.rowcount} Registro inserido.")
    except Error as e:
        logger.error(f"Erro ao conectar ao MySQL: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            logger.info("Conexão com o MySQL encerrada")

# Loop principal do primeiro documento

while True:
    logger.info("Buscando perguntas...")
    process()
    logger.info("entrou no loop depois de iniciar")
    time.sleep(180)