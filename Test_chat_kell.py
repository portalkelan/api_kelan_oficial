import mysql.connector
from mysql.connector import Error
import requests
import openai
import json
import time
from ultima_pergunta import pergunta, detalhe_item, titulo_item
from catalogo_kelan import catalogo
import queue  # Importando a biblioteca queue

openai.api_key = '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'

# Criando a fila, a lista de requisições processadas e a lista de requisições esquecidas
request_queue = queue.Queue()
processed_requests = []
forgotten_requests = []
last_question = None  # Armazena a última pergunta processada

def process_data():
    global last_question

    # PEGANDO A pergunta do cliente
    pergunta_cliente = pergunta

    # Se a pergunta for igual à anterior, adicione à lista de requisições esquecidas e retorne
    if pergunta_cliente == last_question:
        forgotten_requests.append(pergunta_cliente)
        return

    last_question = pergunta_cliente  # Atualiza a última pergunta processada

    # ... (restante do código original)

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
