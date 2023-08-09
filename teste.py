import requests
import time
import json


r = requests.post('https://kelanapi.azurewebsites.net/name/title')

p = r.json()

#pergunta = p['questionData']['text']
print(p)
