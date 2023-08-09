import requests
import json
import mysql.connector
import time
from pegar_data_hora import get_current_datetime
from texto_item import process_request_and_update_db
import texto_item

current_datetime = get_current_datetime()

global contador_requisicoes
global contador_sem_resposta

contador_atribuicoes = 0
contador_requisicoes = 0
contador_sem_resposta = 0

def connect_to_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan'
    )
    return conn

def create_table_if_not_exists(conn):
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS respostas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_pergunta VARCHAR(255),
        seller_id VARCHAR(255),
        pergunta TEXT,
        id_item VARCHAR(255),
        datas_horas DATETIME
    )
    '''

    # Cria um cursor para executar consultas SQL
    cursor = conn.cursor(buffered=True)
    #cursor = conn.cursor()
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
        conn.commit()

def response_exists(conn, id_pergunta):
    select_query = 'SELECT id_pergunta FROM respostas WHERE id_pergunta = %s'
    cursor = conn.cursor(buffered=True)
    with conn.cursor() as cursor:
        cursor.execute(select_query, (id_pergunta,))
        result = cursor.fetchone()
    return bool(result)

def store_response(conn, resposta, current_datetime):
    global contador_atribuicoes

    if response_exists(conn, resposta['id_pergunta']):
        print("A pergunta já existe no banco de dados. Não será adicionada novamente.")
    else:
        insert_query = '''
        INSERT INTO respostas (id_pergunta, seller_id, pergunta, id_item, datas_horas)
        VALUES (%s, %s, %s, %s, %s)
        '''
        values = (resposta['id_pergunta'], resposta['seller_id'], resposta['pergunta'], resposta['id_item'], current_datetime)
        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()

        print('Resposta armazenada no banco de dados com sucesso!', 'Data e Hora: ', current_datetime)
        contador_atribuicoes += 1

while True:
    time.sleep(30)
    
    try:
        r = requests.post('https://kelanapi.azurewebsites.net/message/question')
        contador_requisicoes += 1
        if r.status_code == 200:
            p = r.json()
            if 'questionData' in p:
                data = p['questionData']
                resposta = {
                    'id_pergunta': data['id'],
                    'seller_id': data['seller_id'],
                    'pergunta': data['text'],
                    'id_item': data['item_id']
                }
                #titulo_itens = ['newItemData']['title']
                current_datetime = get_current_datetime()
                try:
                    conn = connect_to_db()
                    create_table_if_not_exists(conn)
                    store_response(conn, resposta, current_datetime)
                    conn.close()
                except mysql.connector.Error as err:
                    print("Erro ao conectar ao MySQL", err)
        else:
            print("Erro na requisição. Código de status:", r.status_code)
            contador_sem_resposta += 1
    except requests.exceptions.RequestException as err:
        print("Erro na solicitação", err)

    pergunta = p['questionData']['text']
    
    print('###########################################')
    print("Total de atribuições bem-sucedidas:", contador_atribuicoes)
    print("Total de atribuições não-sucedidas:", contador_sem_resposta)
    print("Total de requisições repetidas:", contador_requisicoes - contador_atribuicoes)
    print("Total de requisições total:", contador_requisicoes)
    print('###########################################')
    
    print(current_datetime)
    print('######################################################################')
    print('######################################################################')
    process_request_and_update_db()
