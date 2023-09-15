import mysql.connector

def connect():
    # código para se conectar ao banco de dados
    global conexao
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan',
    )
    global cursor
    cursor = conexao.cursor()

def close():
    # código para fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()
        



   


    