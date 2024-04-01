from joblib import load
import pandas as pd
import io
import database  # предполагается, что ваш код для работы с базой данных находится в файле database.py

from celery import Celery

celery_app = Celery('process_csv_file', broker='pyamqp://guest@localhost//')

# Загрузите обученные модели
lr = load('lr_model.joblib')
rf = load('rf_model.joblib')
gb = load('gb_model.joblib')


@celery_app.task(name='process_csv_file')
def process_csv_file(user_id, file_name):
    # Получаем текущую задачу

    print('A')

    # Загружаем данные из файла из базы данных
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    data = pd.read_csv(io.StringIO(user['file_content']))

    # Здесь вы вызываете свои модели машинного обучения для обработки данных

    print('B')
    lr_pred = lr.predict(data)
    rf_pred = rf.predict(data)
    #gb_pred = gb.predict(data)
    gb_pred = ''

    print('C')
    # Сохраняем результаты в базе данных

    # Обновляем баланс пользователя
    user = database.get_user(conn, user_id)
    if user is not None:
        database.update_credits(conn, user_id, user['credits'] - len(data))

    # Обновляем статус обработки файла в базе данных
    database.add_result(conn, user_id, file_name, lr_pred, rf_pred, gb_pred)
    database.update_is_processing(conn, user_id, 0)




if __name__ == '__main__':
    celery_app.worker_main(['worker', '--loglevel=info'])