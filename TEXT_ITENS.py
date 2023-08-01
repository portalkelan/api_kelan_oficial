import requests
import json
import mysql.connector
import time
import pegar_data_hora

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kelan'
}

# Function to establish a database connection
def create_db_connection():
    return mysql.connector.connect(**db_config)

# Function to close a database connection
def close_db_connection(conn, cursor):
    cursor.close()
    conn.close()

# Function to create a table if it doesn't exist
def create_table_if_not_exists(conn, cursor, create_table_query):
    cursor.execute(create_table_query)
    conn.commit()

# Function to check if a question already exists in the database
def question_exists_in_db(conn, cursor, select_query, question_id):
    cursor.execute(select_query, (question_id,))
    return cursor.fetchone()

# Function to insert a new question into the database
def insert_question_into_db(conn, cursor, insert_query, values):
    cursor.execute(insert_query, values)
    conn.commit()

# Function to fetch and store the title
def fetch_and_store_title(conn, cursor):
    r = requests.get('https://kelanapi.azurewebsites.net/message/title')
    if r.status_code == 200:
        title = r.json()['title']
        insert_query = '''
        INSERT INTO title_item (title)
        VALUES (%s)
        '''
        insert_question_into_db(conn, cursor, insert_query, (title,))
        print('Title fetched and stored successfully!')

# Main function
def main():
    conn = create_db_connection()
    cursor = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS respostas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_pergunta VARCHAR(255),
        seller_id VARCHAR(255),
        pergunta TEXT,
        id_item VARCHAR(255)
    )
    '''
    create_table_if_not_exists(conn, cursor, create_table_query)

    while True:
        time.sleep(30)
        r = requests.post('https://kelanapi.azurewebsites.net/message/question')
        if r.status_code == 200:
            p = r.json()

            if 'questionData' in p:
                data = p['questionData']
                question_id = data['id']

                select_query = '''
                SELECT id_pergunta FROM respostas WHERE id_pergunta = %s
                '''
                if not question_exists_in_db(conn, cursor, select_query, question_id):
                    insert_query = '''
                    INSERT INTO respostas (id_pergunta, seller_id, pergunta, id_item)
                    VALUES (%s, %s, %s, %s)
                    '''
                    values = (question_id, data['seller_id'], data['text'], data['item_id'])
                    insert_question_into_db(conn, cursor, insert_query, values)
                    print('Question stored successfully!')

        fetch_and_store_title(conn, cursor)

    close_db_connection(conn, cursor)

if __name__ == "__main__":
    main()
