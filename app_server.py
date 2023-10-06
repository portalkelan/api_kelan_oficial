# Importando as bibliotecas necessárias
from flask import Flask, jsonify, request

app = Flask(__name__)

# Definindo a rota '/data' que aceita requisições GET
@app.route('/data', methods=['POST'])
def get_data():
    # Aqui você pode processar ou buscar os dados que deseja retornar
    data = {
        "message": "Olá, este é um exemplo de rota em Flask!"
    }
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=False, port=8050, host='172.20.20.33')