import mysql.connector
import json
import requests

def extract_id_and_title(json_data):
    item_id = json_data['newItemData']['id']
    item_title = json_data['newItemData']['title']
    return item_id, item_title

def process_request_and_update_db(conn):
    with conn.cursor() as cursor:
        try:
            response = requests.post('https://kelanapi.azurewebsites.net/name/title')
            response.raise_for_status()
            json_data = response.json()
            
            item_id, item_title = extract_id_and_title(json_data)

            query = "SELECT id_item FROM respostas WHERE id_item = %s"
            cursor.execute(query, (item_id,))
            
            if cursor.fetchone():
                update_query = "UPDATE respostas SET title_item = %s WHERE id_item = %s"
                cursor.execute(update_query, (item_title, item_id))
                print("Requisição bem-sucedida e título atualizado.")
            else:
                insert_query = "INSERT INTO respostas (id_item, title_item) VALUES (%s, %s)"
                cursor.execute(insert_query, (item_id, item_title))
                print("Requisição bem-sucedida e novo item inserido.")
            
            conn.commit()
            return item_title

        except Exception as e:
            print("Erro na requisição:", str(e))
            return None
