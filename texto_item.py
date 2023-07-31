import requests
import time
import json

def armazenar_resposta():
    r = requests.post('https://kelanapi.azurewebsites.net/items/info')
    
    response_json = r.json()
    print(response_json)
    
armazenar_resposta()