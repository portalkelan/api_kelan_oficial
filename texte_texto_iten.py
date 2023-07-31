import mysql.connector
import json
import time
import requests

# Função para extrair 'id' e 'title' do JSON
def extract_id_and_title(json_data):
    data = json.loads(json_data)
    item_id = data['itemData']['id']
    item_title = data['itemData']['title']
    return item_id, item_title

# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="kelan"
)

# Cria um cursor para executar consultas SQL
cursor = conn.cursor()

while True:
    try:
        # Código para obter a requisição (substitua este trecho pelo seu código real para obter a requisição)
        # Exemplo usando um JSON fixo como no código original:
        json_data = '''
        {
            "itemData": {
                "id": "MLB1093239349",
                "title": "Cabideiro Prateleira Araras Roupas 60x20x25 Cm Mdf Branco"
            }
        }
        '''
        
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
        else:
            # Se o valor 'id' não existe, inserir na tabela 'respostas'
            insert_query = "INSERT INTO respostas (id_item, title_item) VALUES (%s, %s)"
            cursor.execute(insert_query, (item_id, item_title))

        # Commit das alterações no banco de dados
        conn.commit()

        # Mostrar mensagem de requisição bem-sucedida
        print("Requisição bem-sucedida.")

    except Exception as e:
        # Mostrar mensagem de erro se algo deu errado na requisição
        print("Erro na requisição:", str(e))

    # Aguardar 30 segundos antes de fazer a próxima verificação
    time.sleep(30)

# Fechar cursor e conexão com o banco de dados
cursor.close()
conn.close()
