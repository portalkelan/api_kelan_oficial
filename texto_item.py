import requests
import mysql.connector
import time

def check_and_store_item_title(title):
    # Conecte-se ao banco de dados MySQL
    cnx = mysql.connector.connect(user='root', password='',
                                  host='localhost',
                                  database='kelan')
    cursor = cnx.cursor()

    # Verifique se o título já existe na tabela
    query = ("SELECT title_item FROM respostas WHERE title_item = %s")
    cursor.execute(query, (title,))

    # Se o título não existir, insira-o na tabela
    if cursor.fetchone() is None:
        add_title = ("INSERT INTO respostas (title_item) VALUES (%s)")
        cursor.execute(add_title, (title,))
        cnx.commit()

    cursor.close()
    cnx.close()

while True:
    time.sleep(3)
    r = requests.post('https://kelanapi.azurewebsites.net/name/title')
    if r.status_code == 200:
        p = r.json()
        item_title = p.get('itemTitle', '')
        if item_title:
            check_and_store_item_title(item_title)
    else:
        print("Erro na requisição. Código de status:", r.status_code)
