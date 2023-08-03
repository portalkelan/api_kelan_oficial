import requests
import json
import mysql.connector
import time
import pegar_data_hora
from teste import process_request_and_update_db

data_hora = pegar_data_hora.data_hora()

# Função para armazenar a resposta no banco de dados e contar as atribuições bem-sucedidas
def armazenar_resposta(resposta):
    #global contador_atribuicoes  # Adicionar a declaração 'global' aqui

    # Estabelecer conexão com o banco de dados
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan'
    )

    # Criar uma tabela se ela ainda não existir
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS respostas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_pergunta VARCHAR(255),
        seller_id VARCHAR(255),
        pergunta TEXT,
        id_item VARCHAR(255)
    )
    '''
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()

    # Verificar se a pergunta já existe no banco de dados
    select_query = '''
    SELECT id_pergunta FROM respostas WHERE id_pergunta = %s
    '''
    cursor.execute(select_query, (resposta['id_pergunta'],))
    result = cursor.fetchone()

    if result:
        print("A pergunta já existe no banco de dados. Não será adicionada novamente.")
        
    else:
        # Inserir os valores na tabela
        insert_query = '''
        INSERT INTO respostas (id_pergunta, seller_id, pergunta, id_item)
        VALUES (%s, %s, %s, %s)
        '''
        values = (resposta['id_pergunta'], resposta['seller_id'], resposta['pergunta'], resposta['id_item'])
        cursor.execute(insert_query, values)
        conn.commit()
        print('Resposta armazenada no banco de dados com sucesso!','Data e Hora: ', pegar_data_hora.data_hora())

        # Incrementar o contador de atribuições bem-sucedidas
        contador_atribuicoes += 1

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

global contador_requisicoes
global contador_atribuicoes

# Contador para as atribuições bem-sucedidas
contador_atribuicoes = 0
contador_requisicoes = 0
contador_sem_resposta = 0
 
# Loop infinito para obter e armazenar as respostas
while True:
    time.sleep(30)
    r = requests.post('https://kelanapi.azurewebsites.net/message/question')
    if r.status_code == 200:
        contador_requisicoes += 1
        p = r.json()

        if 'questionData' in p:
            data = p['questionData']
            resposta = {
                'id_pergunta': data['id'],
                'seller_id': data['seller_id'],
                'pergunta': data['text'],
                'id_item': data['item_id']
            }
            armazenar_resposta(resposta)
            
    else:
        print("Erro na requisição. Código de status:", r.status_code)
        contador_sem_resposta += 1
    print('###########################################')
    # Imprimir o contador de atribuições bem-sucedidas
    print("Total de atribuições bem-sucedidas:", contador_atribuicoes)
    print("Total de atribuições não-sucedidas:", contador_sem_resposta)
    print("Total de requisições repetidas:", contador_requisicoes - contador_atribuicoes)
    print("Total de requisições total:", contador_requisicoes)
    print('###########################################')
    pegar_data_hora.data_hora()
    #process_request_and_update_db()
    print('######################################################################')
    print('######################################################################')
    process_request_and_update_db()