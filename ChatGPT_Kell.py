import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from ultima_pergunta import pergunta, detalhe_item, titulo_item
from catalogo_kelan import catalogo

openai.api_key='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'

def process_data():
    # PEGANDO A pergunta do cliente
    pergunta_cliente = pergunta

    # PEGANDO A titulo do itens 
    itemName = titulo_item

    # PEGANDO A  DESCRIÇÃO 
    itemDescription = detalhe_item

## CHAT FORMULA RESPOSTA 
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja Kelan Móveis na plataforma Mercado Livre, você é a Kel, assistente virtual da Kelan. Ao final de mensagem, escreva: Att, Kel Equipe Kelan. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre ou pelas nossas redes sociais, será um prazer ajudá-lo!' Caso o cliente não consiga entrar em contato através das mensagens, explique: Infelizmente, de acordo com as regras da plataforma, não podemos direcioná-lo para nossos canais de atendimento, o que você pode fazer é pesquisar nosso nome afim de nos encontrar em outros canais. Não responda perguntas sobre preços, não invente respostas, siga as informações do catalogo e descrição à risca! Catalogo: {itemDescription} + {catalogo}"}
    ]

    message = itemDescription
    
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})

while True:
    print("buscando perguntas...")  # Mensagem informando que está buscando perguntas
    process_data()
    time.sleep(300)

#POSTA A RESPOSTA NO MELI
#url = 'https://kelanapi.azurewebsites.net/chat'
#headers = {'Content-Type': 'application/json'}
#response = requests.post(url, data=json.dumps(response_dict), headers=headers)
#if response.status_code == 200:
#    print(f'POST BEM SUCEDIDO: {response.status_code} - {response.text}')