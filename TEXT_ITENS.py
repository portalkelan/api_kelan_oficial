import requests
import json
import mysql.connector
import time

while True:
    time.sleep(3)
    r = requests.post('https://kelanapi.azurewebsites.net/name/title')
    if r.status_code == 200:
        p = r.json()
        print(p)
    else:
        print("Erro na requisição. Código de status:", r.status_code)
   