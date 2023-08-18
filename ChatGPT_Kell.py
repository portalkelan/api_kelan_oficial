import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from ultima_pergunta import pergunta, detalhe_item, titulo_item

openai.api_key='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'

def process_data():
    # PEGANDO A pergunta do cliente
    pergunta_cliente = pergunta

    # PEGANDO A titulo do itens 
    itemName = titulo_item

    # PEGANDO A  DESCRIÇÃO 
    itemDescription = detalhe_item

    # CHAT FORMULA RESPOSTA
    temperature = 0.5
    max_tokens = 256
    messages=[
        {"role": "system", "content": f"Você é o assistente virtual da empresa KELAN MÓVEIS, e deve responder as perguntas do cliente utilizando as seguintes informações: {itemName} e {itemDescription}.Gere respostas curtas e objetivas, utilizando  no maximo 200 tokens. Ao final de cada mensagem, escreva: Att, Kel da KELAN. CAso não encontre as respostas para a pergunta nas variáveis instanciadas acima,  aqui estão alguns scripts úteis: Caso lhe perguntem sobre frete, responda: O frete dos produtos é calculado pelo Mercado Livre, e pode variar dependendo da distância entre a cidade do comprador da nossa sede em SP.Toda a responsabilidade sobre a entrega fica sob a transportadora do Mercado Livre.Caso receba algum produto danificado ou tenha outros problemas, por favor entre em contato através das mensagens. Caso lhe perguntem se trabalhamos com Dropshipping, responda que sim. Caso lhe perguntem se fazemos móveis com medidas diferentes das descritas nos anúncios, se desculpe e diga que não. Caso não encontre a resposta para a pergunta com as informações que você possui, explique que não possui tal informação e instrua o cliente a entrar em contato conosco. Caso o cliente tenha algum problema com o produto, o instrua a entrar em contato pelas mensagens. SOBRE A KELAN:A Kelan Indústria e Comércio de Móveis LTDA, consolidada no mercado desde 2016, com sede em Penápolis SP, já atendeu mais de 500 mil clientes, sendo reconhecida nacionalmente e internacionalmente pela sua excelência em cada detalhe no desenvolvimento de seus produtos.Prezamos sempre o bem-estar e satisfação de nossos clientes, além da sustentabilidade.Nossos produtos contam com design sofisticado e moderno, permitindo que você tenha total liberdade para deixar seu ambiente ainda mais elegante."}
    ]

    message = pergunta_cliente
    print(f"Message: {message}")
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
    time.sleep(30)
    process_data()