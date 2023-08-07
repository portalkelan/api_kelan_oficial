import requests
import time
import json

while True:
    time.sleep(3)
    def fazer_requisicao(url):
        try:
            resposta = requests.post(url)
            print(resposta)
            resposta.raise_for_status()  # Verifica se houve algum erro na requisição
            return resposta.text
            
        except requests.exceptions.RequestException as e:
            print(f"Ocorreu um erro na requisição: {e}")
            return None
    
    # Exemplo de uso
    url_servidor = "https://kelanapi.azurewebsites.net/notification/teste"
    resposta_servidor = fazer_requisicao(url_servidor)
    print(resposta_servidor)
    with open("json_perguntas/todas_notification.json", 'w') as file:
        json.dump(resposta_servidor, file, indent=4)

    if resposta_servidor:
        print("Resposta do servidor:")
        print("########################################################")
    else:
        print("Não foi possível obter a resposta do servidor.")

