import requests
import openai
import json
import time
from collections import deque
import logging
import mysql.connector
from mysql.connector import Error

# Configuração do Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### Chave da API Open_AI
openai.api_key = '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'

# Link de Reclamação
link_reclamaçao = 'myaccount.mercadolivre.com.br/my_purchases/list'

request_queue = deque()
processed_questions = set()

def fetch_and_process_data():
    logging.info("Buscando perguntas...")
    url = 'https://kelanapi.azurewebsites.net/kelan/info/info'
    try:
        response = requests.post(url)
        response.raise_for_status()

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

            temperature = 0
            max_tokens = 256
            messages = [
              {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja KELAN MOVEIS na plataforma Mercado Livre.Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!'.RECLAMAÇÕES:'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre neste link: {link_reclamaçao}, será um prazer ajudá-lo!' Horário de atendimento: Seg à Sex das 8h às 18h. Em caso de problemas com o produto, peça que o cliente não abra uma  reclamação e tente entrar em contato conosoco. Não responda perguntas sobre preços, não responda perguntas sobre as notas fiscais, não invente respostas, siga as informações da descrição à risca! NOME DO PRODUTO: {itemName}, DESCRIÇAO: {itemDescription}"}
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
                        url = 'https://kelanapi.azurewebsites.net/oz/chat'
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, data= json.dumps(response_dict), headers=headers)
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

            elif seller_id == kelan_id: 
                        url = 'https://kelanapi.azurewebsites.net/kelan/chat'
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, data= json.dumps(response_dict), headers=headers)
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')

            elif seller_id == may_id:
                        url = 'https://kelanapi.azurewebsites.net/may/chat'
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, data= json.dumps(response_dict), headers=headers)
                        if response.status_code == 200:
                            print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')
                            
            elif seller_id == decorhome_id:  
                        url = 'https://kelanapi.azurewebsites.net/decorhome/chat'
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, data= json.dumps(response_dict), headers=headers)
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
        con = mysql.connector.connect(host='localhost', database='kelan', user='root', password='')
        if con.is_connected():
            cursor = con.cursor()
            query = "INSERT IGNORE INTO api_kelan_mlb (question_id, seller_id, date_created, item_id, question_text, itemName, item_Description, response_json, foi_respondida) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

while True:
    request_queue.append({})
    if request_queue:
        fetch_and_process_data()
        request_queue.popleft()
    time.sleep(180)
