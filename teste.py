import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import mysql.connector

app = dash.Dash(__name__)
server = app.server

# Conectar ao banco de dados MySQL
def connect_to_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='kelan'
    )
    return conn

# Obter dados do banco de dados
def get_data_from_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id_item, title_item, pergunta FROM respostas')
    data = cursor.fetchall()
    conn.close()
    return data

data = get_data_from_db()
df = pd.DataFrame(data, columns=['ID', 'TÃ­tulo', 'Pergunta'])

app.layout = html.Div([
    html.H1('Dashboard de VisualizaÃ§Ã£o de Dados', className='text-center'),
    dash_table.DataTable(
        id='table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
#Ask AI to edit or generate...
