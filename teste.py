import requests
import time
import json

r = requests.post('https://kelanapi.azurewebsites.net/items/info')
p = r.json()
dados_itens = p['itemData']['plain_text']
print(dados_itens)


# Criar um dicionário com a resposta
        response_dict = {"ChatGPT": reply}

        # Converter o dicionário em uma string JSON
        response_json = json.dumps(response_dict)

        #ENVIANDO A RESPOSTA PARA O MELI
        #url = 'https://kelanapi.azurewebsites.net/chat'

        #headers = {'Content-Type': 'application/json'}
        #response = requests.post(url, data=json.dumps(response_dict), headers=headers)

        #ENVIAR PARA O BANCO DE DADOS
        """def insert_into_database(question_text, itemName, itemDescription, reply):
            try:
                con  = mysql.connector.connect(host='localhost', database = 'kelan_db', user = 'root', password= '')
                if con.is_connected():
                    cursor = con.cursor()
                    query = "INSERT IGNORE INTO chat_db (question_text, itemName, item_Description, response_json) VALUES (%s, %s, %s, %s)"
                    values = (question_text, itemName, itemDescription, reply)
                    cursor.execute(query, values)
                    con.commit()
                    print(cursor.rowcount, "Registro inserido.")
            except Error as e:
                print("Erro ao conectar ao MySQL", e)
            finally:
                if con.is_connected():
                    cursor.close()
                    con.close()
                    print("Conexão com o MySQL encerrada")
                    
        insert_into_database(reply)"""