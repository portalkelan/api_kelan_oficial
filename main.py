import requests
import json

def requisicao_e_selecao():
    # Faz a requisição GET para o servidor
    url = 'https://kelanapi.azurewebsites.net/message/question'
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida (código de resposta 200)
    if response.status_code == 200:
        # Obtém a resposta em formato JSON
        dados_json = response.json()

        # Seleciona as chaves desejadas (id, seller_id e text)
        dados_selecionados = []
        for item in dados_json:
            dados_selecionados.append({
                'id': item.get('id'),
                'seller_id': item.get('seller_id'),
                'text': item.get('text')
            })

        # Gera o JSON com as chaves selecionadas
        json_selecionado = json.dumps(dados_selecionados)

        # Retorna o JSON resultante
        return json_selecionado

    else:
        # Caso a requisição não seja bem-sucedida, retorna None
        return None

# Chama a função para fazer a requisição e seleção
resultado = requisicao_e_selecao()

# Verifica se obteve um resultado válido
if resultado:
    print(resultado)
else:
    print('Falha na requisição.')
