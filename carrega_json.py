import json

# Abrir o arquivo orders.json
with open("orders.json") as file:
    # Carregar seu conteúdo e torná-lo um novo dicionário
    data = json.load(file)
    print(data)
    # Excluir o par chave-valor "client" de cada pedido
    for order in data["orders"]:
        del order["client"]

# Abrir (ou criar) um arquivo orders_new.json 
# e armazenar a nova versão dos dados.
with open("orders_new.json", 'w') as file:
    json.dump(data, file)
    print(data)

with open("orders_new.json") as file:
    # Carregar seu conteúdo e torná-lo um novo dicionário
    data = json.loads(file, indent=4)    



print('##################################')
print(data)
print('##################################')
#print(data2)
print('##################################')