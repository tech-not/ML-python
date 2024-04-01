import database

conn = database.create_connection()

database.create_users_table(conn)
database.create_results_table(conn)