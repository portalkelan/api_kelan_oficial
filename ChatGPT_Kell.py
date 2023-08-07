import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time

openai.api_key='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'

previous_itemName = ""
previous_question_text = ""
previous_itemDescription = ""

def process_data():
    global previous_itemName, previous_question_text, previous_itemDescription

    # PEGANDO O NOME DO ITEM  
    url = 'https://kelanapi.azurewebsites.net/name/title'
    response = requests.post(url)
    itemName= ""
    if response.status_code == 200:
        Name = response.json()
        itemName = Name['newItemData']['title']

    # Verificar se o nome do item é o mesmo que o anterior
    if itemName == previous_itemName:
        print("O nome do item é o mesmo que o anterior.")
    else:
        print(itemName)
    previous_itemName = itemName

    # PEGANDO A PERGUNTA 
    url = 'https://kelanapi.azurewebsites.net/message/question'
    response = requests.post(url)
    question_text = ""
    if response.status_code == 200:
        data = response.json()
        question_text = data['questionData']['text']

    # Verificar se o texto da pergunta é o mesmo que o anterior
    if question_text == previous_question_text:
        print("O texto da pergunta é o mesmo que o anterior.")
    else:
         print(f"Texto da pergunta: {question_text}")
    previous_question_text = question_text

    # PEGANDO A  DESCRIÇÃO 
    url = 'https://kelanapi.azurewebsites.net/items/info'
    response = requests.post(url)
    itemDescription=""
    if response.status_code == 200:
        item = response.json()
        itemDescription = item['itemData']['plain_text']

    # Verificar se a descrição do item é o mesma que a anterior
    if itemDescription == previous_itemDescription:
        print("A descrição do item é a mesma que a anterior.")
    else:
        print(itemDescription)
    previous_itemDescription = itemDescription

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

        # Agora você pode verificar a resposta
        if response.status_code == 200:
            print('POST foi bem-sucedido')
        else:
            print(f'Erro ao fazer POST: {response.status_code}') 
            
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
                    
        insert_into_database(question_text, itemName, itemDescription, reply)


while True:
    process_data()
    time.sleep(30)
