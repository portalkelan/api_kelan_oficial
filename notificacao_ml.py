import requests
import time
import json

while True:
    time.sleep(3)
    try:
        r = requests.post("https://testeappi.azurewebsites.net/notification/teste")
        if r.status_code == 200:
            p = r.json()
            print(p)
            
            data1 = p['topic']
            data2 = p['resource']
            data3 = p['user_id']
            data4 = p['received']
            
            #print(f"Tipo da Notificação: {data1}, Recursos: {data2}, Conta: {data3}, hora recebida: {data4}")
            
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
