import openai
import time
from ultima_pergunta import pergunta, detalhe_item, titulo_item
from catalogo_kelan import catalogo
import queue

# Configuração da chave da API da OpenAI
# (Recomendo mover isso para uma variável de ambiente ou arquivo de configuração)
openai.api_key = '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'

# Criando a fila e a lista de requisições processadas
request_queue = queue.Queue()
processed_requests = []

def generate_response(pergunta_cliente, itemDescription):
    """
    Gera uma resposta usando a API da OpenAI com base na pergunta do cliente e na descrição do item.
    
    Args:
    - pergunta_cliente (str): A pergunta feita pelo cliente.
    - itemDescription (str): Descrição do item em questão.
    
    Returns:
    - str: Resposta gerada.
    """
    temperature = 0
    max_tokens = 256
    messages = [
        {"role": "system", "content": "... (conteúdo anterior removido para brevidade) ... Catalogo: {itemDescription}"}
    ]

    messages.append({"role": "user", "content": pergunta_cliente})
    
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return chat.choices[0].message.content

def process_data():
    """
    Processa a pergunta do cliente, verifica se já foi processada anteriormente e, se não, gera uma resposta.
    """
    pergunta_cliente = pergunta

    if pergunta_cliente not in processed_requests:
        processed_requests.append(pergunta_cliente)
        
        itemName = titulo_item
        itemDescription = detalhe_item
        
        reply = generate_response(pergunta_cliente, itemDescription)
        print(f"ChatGPT: {reply}")

def handle_request():
    """
    Manipula as requisições na fila, processando-as uma por uma.
    """
    while True:
        print("Buscando perguntas...")
        
        if not request_queue.empty():
            next_request = request_queue.get()
            process_data()
            request_queue.task_done()
            
        time.sleep(30)

def main():
    """
    Função principal que adiciona requisições à fila e inicia o processamento.
    """
    # Adicionando requisições à fila (por exemplo, adicionando 10 requisições à fila)
    for _ in range(10):
        request_queue.put("request")

    # Iniciando o processamento das requisições
    handle_request()

if __name__ == "__main__":
    main()