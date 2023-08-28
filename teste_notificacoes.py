import requests
import time
import mysql.connector

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "kelan"
}

# Função para inserir dados no banco de dados
def insert_into_db(_id, topic, resource, user_id, received):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = ("INSERT INTO notificacoes (_id, topic, resource, user_id, received) "
                 "VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(query, (_id, topic, resource, user_id, received))

        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir no banco de dados: {err}")

while True:
    try:
        r = requests.post("https://testeappi.azurewebsites.net/notification/teste")
        if r.status_code == 200:
            p = r.json()
            
            _id = p['_id']
            topic = p['topic']
            resource = p['resource']
            user_id = p['user_id']
            received = p['received']
            
            print(f"ID: {_id}, Tipo da Notificação: {topic}, Recursos: {resource}, Conta: {user_id}, hora recebida: {received}")
            
            # Inserir dados no banco de dados
            insert_into_db(_id, topic, resource, user_id, received)
            
            time.sleep(20)
            
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
