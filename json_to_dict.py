# Importar o módulo
import json

# String em formato JSON
with open("orders.json") as file:
    # Carregar seu conteúdo e torná-lo um novo dicionário
    data = json.load(file)

data2 = data["orders"]
print(data2)

# Obter uma string formatada em JSON
client_JSON = json.dumps(data2, indent=4)
print(client_JSON)

with open("ths.json", 'w') as file:
    json.dump(client_JSON, file, indent=4)
    
