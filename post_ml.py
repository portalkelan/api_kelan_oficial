import requests
import json

def enviar_arquivo_json(url, arquivo_json):
    try:
        with open(arquivo_json, 'r') as arquivo:
            dados = json.load(arquivo)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=dados, headers=headers)
        response.raise_for_status()  # Verifica se ocorreu algum erro na requisição
        print("Arquivo JSON enviado com sucesso!")
    except (IOError, requests.exceptions.RequestException) as e:
        print("Ocorreu um erro ao enviar o arquivo JSON:", e)

# URL do servidor/API para enviar a solicitação POST
url_servidor = "https://kelanapi.azurewebsites.net/chat"

# Caminho para o arquivo JSON que será enviado
arquivo_json = "json_perguntas/dados_perguntas.json"

# Chamando a função para enviar o arquivo JSON
enviar_arquivo_json(url_servidor, arquivo_json)


# Exemplo de uso
    #url_servidor = "https://kelanapi.azurewebsites.net/notification/teste"
    #resposta_servidor = fazer_requisicao(url_servidor)
    #with open("json_perguntas/todas_notification.json", 'w') as file:
    #    json.dump(resposta_servidor, file, indent=4)