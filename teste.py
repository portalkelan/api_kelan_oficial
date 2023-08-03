import mysql.connector
import json
import time
import requests

# Função para extrair 'id' e 'title' do JSON
def extract_id_and_title(json_data):
    item_id = json_data['newItemData']['id']
    item_title = json_data['newItemData']['title']
    return item_id, item_title

def process_request_and_update_db():
    # Conectar ao banco de dados MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="kelan"
    )

    # Cria um cursor para executar consultas SQL
    cursor = conn.cursor()

    try:
        # Código para obter a requisição
        response = requests.post('https://kelanapi.azurewebsites.net/name/title')
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        json_data = response.json()  # Converte a resposta em JSON

        # Extrair 'id' e 'title' do JSON
        item_id, item_title = extract_id_and_title(json_data)

        # Consulta para verificar se o valor 'id' já existe na tabela 'respostas'
        query = "SELECT id_item FROM respostas WHERE id_item = %s"
        cursor.execute(query, (item_id,))

        # Verificar se o valor já existe no banco
        if cursor.fetchone() is not None:
            # Se o valor 'id' já existe, atualizar a coluna 'title_item'
            update_query = "UPDATE respostas SET title_item = %s WHERE id_item = %s"
            cursor.execute(update_query, (item_title, item_id))
            # Mostrar mensagem de requisição bem-sucedida
            print("Requisição bem-sucedida.")
        else:
            # Se o valor 'id' não existe, inserir na tabela 'respostas'
            insert_query = "INSERT INTO respostas (id_item, title_item) VALUES (%s, %s)"
            cursor.execute(insert_query, (item_id, item_title))

        # Commit das alterações no banco de dados
        conn.commit()

    except Exception as e:
        # Mostrar mensagem de erro se algo deu errado na requisição
        print("Erro na requisição:", str(e))

    finally:
        # Fechar cursor e conexão com o banco de dados
        cursor.close()
        conn.close()

# Chamar a função
if __name__ == "__main__":
    process_request_and_update_db()
