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
def converter_formato_com_hora(data_iso):
    data_objeto = datetime.fromisoformat(data_iso)
    data_br = data_objeto.strftime('%d/%m/%y %H:%M:%S')
    return data_br

openai.api_key = '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'

link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

# Funções do segundo documento
previous_question_id = ""
queue = []

## FAZ A CHAMADA PARA O SERVIDOR E PEGA O JSON COM TODAS AS INFORMAÇÕES:
global postagem
postagem = {
    '65131481':'https://kelanapi.azurewebsites.net/kelan/chat', '271842978':'https://kelanapi.azurewebsites.net/may/chat', '20020278':'https://kelanapi.azurewebsites.net/oz/chat', '65131481':'https://kelanapi.azurewebsites.net/decorhome/chat'
    }

def fetch_data_to_queue():
    global previous_question_id
    url = 'https://testeappi.azurewebsites.net/oz/info/info'
    response = requests.post(url, timeout=60)

    if response.status_code != 200:
        logger.error(f"Erro ao chamar a API (Nome do item): {response.status_code} - {response.text}")
    else:
        # Transforma o conteúdo da resposta em um objeto JSON (dicionário ou lista)
        data = response.json()

        ##SEPARANDO OS DADOS 

        seller_id = data['allInfo']['seller_id']
        question_id = data['allInfo']['questionId']
        itemName = data['allInfo']['itemName']
        item_id = data['allInfo']['itemId']
        date_created = data['allInfo']['date_created']
        date_created = converter_formato_com_hora(['allInfo']['date_created'])
        question_text = data['allInfo']['question_text']
        foi_respondida = data['allInfo']['foi_respondida']
        itemDescription = data['allInfo']['itemDescription']

        print(f"Conta:{seller_id}")
        print(f"Question ID:{question_id}")
        print(f"Anúncio: {itemName}")
        print(f"Item ID: {item_id}")
        print(f"Data/Hora: {date_created}")
        print(f"Pergunta: {question_text}")
        print(f"Status: {foi_respondida}")
        print(f"Descrição: {itemDescription}")

    ## CHAT FORMULA RESPOSTA
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja KELAN MOVEIS na plataforma Mercado Livre, você é a Kel, assistente virtual da KELAN MOVEIS. Ao final de mensagem, escreva: Att, Kel Equipe KELAN MOVEIS. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!'.RECLAMAÇÕES:'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!' Horário de atendimento: Seg à Sex das 8h às 18h. Em caso de problemas com o produto, peça que o cliente não abra uma  reclamação e tente entrar em contato conosoco. Não responda perguntas sobre preços, não responda perguntas sobre as notas fiscais, não invente respostas, siga as informações da descrição à risca! NOME DO PRODUTO: {itemName}, DESCRIÇAO: {itemDescription}"}
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

        # POSTA A RESPOSTA NO MELI
        url = (postagem)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(response_dict), headers=headers, timeout=60)
        if response.status_code == 200:
            logger.info(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
        else:
            logger.error(f'Erro ao postar resposta: {response.status_code} - {response.text}')

        # GUARDA AS CHAVES NO BANCO DE DADOS
        insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida)

### Conexão e inserir no banco
def insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO api_kelan_mlb (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply, foi_respondida)
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


    ##CONECTAR COM O BANCO DE DADOS
    ## CRIAR O SISTEMA DE FILA
    ## CRIAR OS LOOPS
    '''CRIAR A FUNÇÃO: if SELLER_ID = X postar em https://kelanapi.azurewebsites.net/oz/chat
                    if SELLER_ID = Y postar em https://kelanapi.azurewebsites.net/kelan/chat (...)'''