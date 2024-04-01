import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        print(f'successful connection with sqlite version {sqlite3.version}')
    except Error as e:
        print(f'an error {e} occurred')
        
    return conn


def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    except Error as e:
        print(f'an error {e} occurred')

def create_users_table(conn):
    query = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        credits INTEGER NOT NULL,
        file_content TEXT,
        is_processing INTEGER DEFAULT 0
    );
    """
    execute_query(conn, query)

def create_results_table(conn):
    query = """
    CREATE TABLE results (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        lr_pred TEXT,
        rf_pred TEXT,
        gb_pred TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    execute_query(conn, query)


def update_file_content(conn, id, file_content):
    query = f"""
    UPDATE users
    SET file_content = '{file_content}'
    WHERE id = {id};
    """
    execute_query(conn, query)

def update_is_processing(conn, id, is_processing):
    query = f"""
    UPDATE users
    SET is_processing = {is_processing}
    WHERE id = {id};
    """
    execute_query(conn, query)

def add_result(conn, user_id, file_name, lr_pred, rf_pred, gb_pred):
    query = f"""
    INSERT INTO results(user_id, file_name, lr_pred, rf_pred, gb_pred)
    VALUES({user_id}, '{file_name}', '{lr_pred}', '{rf_pred}', '{gb_pred}');
    """
    execute_query(conn, query)

def get_results(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM results WHERE user_id={user_id}")
    return cursor.fetchall()


def add_user(conn, id, credits):
    query = f"""
    INSERT INTO users(id, credits)
    VALUES({id}, {credits});
    """
    execute_query(conn, query)

def get_user(conn, id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id={id}")
    return cursor.fetchone()

def update_credits(conn, id, credits):
    query = f"""
    UPDATE users
    SET credits = {credits}
    WHERE id = {id};
    """
    execute_query(conn, query)
