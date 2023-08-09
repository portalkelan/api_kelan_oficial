import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from ultima_pergunta import 
from texto_item import 

openai.api_key='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'

def process_data():
    # PEGANDO A PERGUNTA 

    # PEGANDO A  DESCRIÇÃO 
    
    # CHAT FORMULA RESPOSTA
    temperature = 0.5
    max_tokens = 256
    messages=[
        {"role": "system", "content": f"Você é o assistente virtual da empresa KELAN MÓVEIS, e deve responder as perguntas do cliente utilizando as seguintes informações: {itemName} e {itemDescription}.Gere respostas curtas e objetivas, utilizando  no maximo 200 tokens. Ao final de cada mensagem, escreva: Att, Kel da KELAN. CAso não encontre as respostas para a pergunta nas variáveis instanciadas acima,  aqui estão alguns scripts úteis: Caso lhe perguntem sobre frete, responda: O frete dos produtos é calculado pelo Mercado Livre, e pode variar dependendo da distância entre a cidade do comprador da nossa sede em SP.Toda a responsabilidade sobre a entrega fica sob a transportadora do Mercado Livre.Caso receba algum produto danificado ou tenha outros problemas, por favor entre em contato através das mensagens. Caso lhe perguntem se trabalhamos com Dropshipping, responda que sim. Caso lhe perguntem se fazemos móveis com medidas diferentes das descritas nos anúncios, se desculpe e diga que não. Caso não encontre a resposta para a pergunta com as informações que você possui, explique que não possui tal informação e instrua o cliente a entrar em contato conosco. Caso o cliente tenha algum problema com o produto, o instrua a entrar em contato pelas mensagens. SOBRE A KELAN:A Kelan Indústria e Comércio de Móveis LTDA, consolidada no mercado desde 2016, com sede em Penápolis SP, já atendeu mais de 500 mil clientes, sendo reconhecida nacionalmente e internacionalmente pela sua excelência em cada detalhe no desenvolvimento de seus produtos.Prezamos sempre o bem-estar e satisfação de nossos clientes, além da sustentabilidade.Nossos produtos contam com design sofisticado e moderno, permitindo que você tenha total liberdade para deixar seu ambiente ainda mais elegante."}
    ]

    message = question_text
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

        # Criar um dicionário com a resposta
        response_dict = {"ChatGPT": reply}

        # Converter o dicionário em uma string JSON
        response_json = json.dumps(response_dict)

        #ENVIANDO A RESPOSTA PARA O MELI
        url = 'https://kelanapi.azurewebsites.net/chat'

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(response_dict), headers=headers)

        #ENVIAR PARA O BANCO DE DADOS
        def insert_into_database(question_text, itemName, itemDescription, reply):
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
                    
        insert_into_database(reply)

while True:
    process_data()