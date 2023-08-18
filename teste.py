import requests
import json

r = requests.post('https://kelanapi.azurewebsites.net/name/title')
p = r.json()
detalhe_item = p['newItemData']['title']
print(detalhe_item)
