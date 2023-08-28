import requests
import time
import json

while True:
    try:
        r = requests.post("https://testeappi.azurewebsites.net/notification/teste")
        if r.status_code == 200:
            p = r.json()
            print(p)
            topic = p['topic']
            resource = p['resource']
            user_id = p['user_id']
            received = p['received']
            
            #print(f"Tipo da Notificação: {topic}, Recursos: {resource}, Conta: {user_id}, hora recebida: {received}")
            time.sleep(20)

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
