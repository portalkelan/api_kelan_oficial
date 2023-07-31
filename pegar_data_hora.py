import datetime as dt

# Pegar data e hora
def data_hora():
    agora = dt.datetime.now()
    data_hora = agora.strftime("%A %d %B %y %I:%M:%S")
    print(data_hora)
