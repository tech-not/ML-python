# uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse
import pandas as pd
import io
import database  # предполагается, что ваш код для работы с базой данных находится в файле database.py

import csv

from worker import process_csv_file

app = FastAPI()


@app.get("/start")
def start(user_id: str):
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    print(user)
    if user is None:
        database.add_user(conn, user_id, 0)
    return {"message": "Пользователь создан"}

@app.get("/help")
def help_command():
    return {"message": 'Список команд:\n/start\n/help\n/balance\n/add X'}

@app.get("/balance")
def get_balance(user_id: str):
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"balance": user['credits']}

@app.get("/add")
def add(user_id: str, credits: int):
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    database.update_credits(conn, user_id, user['credits'] + credits)
    return {"message": f"Начислено {credits} кредитов. Теперь у вас {user['credits'] + credits} кредитов"}

@app.post("/process-csv/{user_id}")
async def process_csv(user_id: str, file: UploadFile = File(...)):
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user['is_processing'] == 1:
        return {"message": "У вас уже идет обработка файла. Пожалуйста, дождитесь ее завершения."}

    file_data = await file.read()
    data = pd.read_csv(io.BytesIO(file_data))

    if len(data) > user['credits']:
        return {"message": "У вас недостаточно кредитов для обработки этого файла"}

    # Сохраняем содержимое файла в базе данных и устанавливаем статус обработки в 1
    database.update_file_content(conn, user_id, file_data.decode())
    database.update_is_processing(conn, user_id, 1)

    process_csv_file.delay(user_id, file.filename)

    return {"message": "Ваш файл был добавлен в очередь на обработку. Вы получите результаты, как только они будут готовы."}

@app.get("/get-results/{user_id}")
async def get_results(user_id: str):
    conn = database.create_connection()
    user = database.get_user(conn, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Check if the user has a file being processed
    if user['is_processing'] == 1:
        return {"message": "Ваш файл все еще обрабатывается. Пожалуйста, подождите."}

    # Get the results from the database
    results = database.get_results(conn, user_id)
    if results is None:
        return {"message": "У вас нет результатов для загрузки."}

    # Write the results to a CSV file
    with open(f"{user_id}_results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(['file_name', 'lr_pred', 'rf_pred', 'gb_pred'])
        for result in results:
            writer.writerow([result['file_name'], result['lr_pred'], result['rf_pred'], result['gb_pred']])

    # Return the CSV file
    return FileResponse(f"{user_id}_results.csv", media_type='application/csv', filename=f"{user_id}_results.csv")
