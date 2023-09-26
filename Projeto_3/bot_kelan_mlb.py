import openai
from datetime import datetime
from botcity.core import DesktopBot
import json
import logging
import mysql.connector
from mysql.connector import Error
import requests
import time

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para converter a notação da hora para o padrão brasileiro
def converter_formato_com_hora(data_iso):
    data_objeto = datetime.fromisoformat(data_iso)
    data_br = data_objeto.strftime('%d/%m/%y %H:%M:%S')
    return data_br

# Configuração da OpenAI
openai.api_key = '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'

# Funções do segundo documento
previous_question_id = ""
queue = []

def fetch_data_to_queue():
    global previous_question_id
        # NOME DO ITEM/ANÚNCIO
    url = 'https://kelanapi.azurewebsites.net/kelan/name/title'
    response = requests.post(url, timeout=60)
    if response.status_code != 200:
        logger.error(f"Erro ao chamar a API (Nome do item): {response.status_code} - {response.text}")
        return

    Name = response.json()
    itemName = Name['newItemData']['title']

    # PERGUNTA
    url = 'https://kelanapi.azurewebsites.net/kelan/message/question'
    response = requests.post(url, timeout=60)
    if response.status_code != 200:
        logger.error(f"Erro ao chamar a API (Pergunta): {response.status_code} - {response.text}")
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

def process_data(itemName, question_data):
    question_text = question_data['questionData']['text']
    question_id = question_data['questionData']['id']
    seller_id = question_data['questionData']['seller_id']
    item_id = question_data['questionData']['item_id']
    date_created = converter_formato_com_hora(question_data['questionData']['date_created'])

    # DESCRIÇÃO DO ANÚNCIO 
    url = 'https://kelanapi.azurewebsites.net/kelan/items/info'
    response = requests.post(url, timeout=60)
    if response.status_code != 200:
        logger.error(f"Erro ao chamar a API (Descrição do item): {response.status_code} - {response.text}")
        return

    item = response.json()
    itemDescription = item['itemData']['plain_text']
    logger.info(f"Descrição do item obtida: {itemDescription}")

    link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

    # CHAT FORMULA RESPOSTA 
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja KELAN MOVEIS na plataforma Mercado Livre, você é a Kel, assistente virtual da KELAN MOVEIS. Ao final de mensagem, escreva: Att, Kel Equipe KELAN MOVEIS. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. NÃO RESPONDA A PERGUNTAS SOBRE OS PREÇOS DOS ITENS, PEÇA AO CLIENTE PARA CONFERIR NO ANÚNCIO. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!'.RECLAMAÇÕES:'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!' Horário de atendimento: Seg à Sex das 8h às 18h. Em caso de problemas com o produto, peça que o cliente não abra uma  reclamação e tente entrar em contato conosoco. Não responda perguntas sobre preços, não responda perguntas sobre as notas fiscais, não invente respostas, siga as informações da descrição à risca! NOME DO PRODUTO: {itemName}, DESCRIÇAO: {itemDescription}"}
    ]
    message = question_text
    logger.info(f"Message: {message}")
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
    if seller_id == 65131481:
        # POSTA A RESPOSTA NO MELI
        url = 'https://kelanapi.azurewebsites.net/may/chat'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(response_dict), headers=headers)
        if response.status_code == 200:
            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
    else:
        print("Execução interrompida")

        # GUARDA AS CHAVES NO BANCO DE DADOS
        insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply)

def insert_into_database(question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply):
    try:
        con = mysql.connector.connect(host='localhost', database='kelan', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO api_kelan_mlb (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (question_id, seller_id, date_created, item_id, question_text, itemName, itemDescription, reply)
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

# Classe Bot do primeiro documento
class Bot(DesktopBot):
    def action(self, execution=None):
        logger.info("Buscando perguntas...")
        fetch_data_to_queue()
        process_queue()

    def not_found(self, label):
        print(f"Element not found: {label}")

# Loop principal do primeiro documento
if __name__ == '__main__':
    while True:
        Bot.main()
        logger.info("entrou no loop depois de iniciar")
        time.sleep(300)
