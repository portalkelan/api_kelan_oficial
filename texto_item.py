import requests

def armazenar_title_item():
    r = requests.post('https://kelanapi.azurewebsites.net/name/title')
    
    response_title = r.json()
    print(response_title)

armazenar_title_item()