from datetime import datetime

def get_current_datetime():
    # Obtenha a data e hora atual
    now = datetime.now()

    # Formate a data e hora no formato apropriado para o MySQL
    formatted_now = now.strftime('%H:%M:%S')

    return formatted_now

get_current_datetime()

