from mysql.connector import Error
import openai
import time
from ultima_pergunta import pergunta, detalhe_item, titulo_item
from catalogo_kelan import catalogo
import queue  # Importando a biblioteca queue

openai.api_key = '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'

# Criando a fila e a lista de requisições processadas
request_queue = queue.Queue()
processed_requests = []

def process_data():
    # PEGANDO A pergunta do cliente
    pergunta_cliente = pergunta

    # Se a pergunta já foi processada, retorne e não processe novamente
    if pergunta_cliente in processed_requests:
        processed_requests.append(pergunta_cliente)
        return

    # PEGANDO A titulo do itens 
    itemName = titulo_item

    # PEGANDO A  DESCRIÇÃO 
    itemDescription = detalhe_item

    ## CHAT FORMULA RESPOSTA 
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content":f"Atue como um profissional de atendimento ao cliente e responda as perguntas sobre os produtos da loja Kelan Móveis na plataforma Mercado Livre, você é a Kel, assistente virtual da Kelan. Ao final de mensagem, escreva: Att, Kel Equipe Kelan. Responda as perguntas dos clientes utilizando o catalogo como parametro de resposta. Caso a resposta para a pergunta não esteja no prompt, cole a seguinte mensagem 'Olá, infelizmente não encontrei uma resposta para a sua pergunta nos meus dados de treinamento, por favor, entre em contato conosco através das mensagens do Mercado Livre ou pelas nossas redes sociais, será um prazer ajudá-lo!' Caso o cliente não consiga entrar em contato através das mensagens, explique: Infelizmente, de acordo com as regras da plataforma, não podemos direcioná-lo para nossos canais de atendimento, o que você pode fazer é pesquisar nosso nome afim de nos encontrar em outros canais. Não responda perguntas sobre preços, não invente respostas, siga as informações do catalogo e descrição à risca! Catalogo: {itemDescription}"}
    ]

    message = pergunta_cliente
    
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

def handle_request():
    while True:
        print("buscando perguntas...")  # Mensagem informando que está buscando perguntas
        
        # Verifica se há itens na fila
        if not request_queue.empty():
            # Pega o próximo item da fila
            next_request = request_queue.get()
            
            # Processa a requisição
            process_data()
            
            # Indica que a tarefa foi concluída
            request_queue.task_done()
            
        time.sleep(30)

# Adicionando requisições à fila (por exemplo, adicionando 10 requisições à fila)
for _ in range(10):
    request_queue.put("request")

# Iniciando o processamento das requisições
handle_request()
