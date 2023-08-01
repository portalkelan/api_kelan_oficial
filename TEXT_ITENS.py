import requests
import json
import mysql.connector
import time
import pegar_data_hora

data_hora = pegar_data_hora.data_hora()

def armazenar_resposta(resposta):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan'
    )

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS respostas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_pergunta VARCHAR(255),
        seller_id VARCHAR(255),
        pergunta TEXT,
        id_item VARCHAR(255),
        title_item TEXT
    )
    '''
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()

    select_query = '''
    SELECT id_pergunta FROM respostas WHERE id_pergunta = %s
    '''
    cursor.execute(select_query, (resposta['id_pergunta'],))
    result = cursor.fetchone()

    if result:
        print("A pergunta já existe no banco de dados. Não será adicionada novamente.")
    else:
        insert_query = '''
        INSERT INTO respostas (id_pergunta, seller_id, pergunta, id_item, title_item)
        VALUES (%s, %s, %s, %s, %s)
        '''
        values = (resposta['id_pergunta'], resposta['seller_id'], resposta['pergunta'], resposta['id_item'], resposta['title_item'])
        cursor.execute(insert_query, values)
        conn.commit()
        print('Resposta armazenada no banco de dados com sucesso!','Data e Hora: ', pegar_data_hora.data_hora())

        global contador_atribuicoes
        contador_atribuicoes += 1

    cursor.close()
    conn.close()

def armazenar_title_item():
    r = requests.post('https://kelanapi.azurewebsites.net/name/title')
    
    if r.status_code == 200:
        response_title = r.json()
        print(response_title)
        return response_title
    else:
        print("Erro na requisição. Código de status:", r.status_code)
        return None

contador_atribuicoes = 0
contador_requisicoes = 0
contador_sem_resposta = 0
 
while True:
    time.sleep(30)
    r = requests.post('https://kelanapi.azurewebsites.net/message/question')
    if r.status_code == 200:
        contador_requisicoes += 1
        p = r.json()

        if 'questionData' in p:
            data = p['questionData']
            title_item = armazenar_title_item()
            resposta = {
                'id_pergunta': data['id'],
                'seller_id': data['seller_id'],
                'pergunta': data['text'],
                'id_item': data['item_id'],
                'title_item': title_item
            }
            armazenar_resposta(resposta)
    else:
        print("Erro na requisição. Código de status:", r.status_code)
        contador_sem_resposta += 1
    print('###########################################')
    print("Total de atribuições bem-sucedidas:", contador_atribuicoes)
    print("Total de atribuições não-sucedidas:", contador_sem_resposta)
    print("Total de requisições repetidas:", contador_requisicoes - contador_atribuicoes)
    print("Total de requisições total:", contador_requisicoes)
    print('###########################################')
    pegar_data_hora.data_hora()
    print('######################################################################')
    print('######################################################################')
