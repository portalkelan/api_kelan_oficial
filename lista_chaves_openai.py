import time

# Lista de chaves da API da OpenAI
api_keys = [
    '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',
    'nova_chave_1',
    'nova_chave_2',
]

# Índice da chave atual
current_key_index = 0

def get_current_api_key():
    global current_key_index
    return api_keys[current_key_index]

def rotate_api_keys():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(api_keys)

def update_api_key_periodically(interval_minutes):
    while True:
        time.sleep(interval_minutes * 60)  # Espera por 'interval_minutes' minutos
        rotate_api_keys()
        print(f'Chave da API atualizada para: {get_current_api_key()}')

# Inicie a atualização periódica da chave da API a cada 60 minutos
update_api_key_periodically(60)
