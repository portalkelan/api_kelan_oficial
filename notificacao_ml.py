import requests
import time
import json

while True:
    time.sleep(3)
    try:
        r = requests.get('https://testeskelan.azurewebsites.net/notification/teste')
        print(r)
        if r.status_code == 200:
            p = r.json()
            print(p)

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")

    # Exemplo de uso
    #url_servidor = "https://kelanapi.azurewebsites.net/notification/teste"
    #resposta_servidor = fazer_requisicao(url_servidor)
    #with open("json_perguntas/todas_notification.json", 'w') as file:
    #    json.dump(resposta_servidor, file, indent=4)
