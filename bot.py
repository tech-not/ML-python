from telegram import Bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import requests

TOKEN = '6942242200:AAF_WESsuFbDmrWXr1paMAcYB2Jr3O4UJpo'
API_URL = 'http://localhost:8000'

def start(update: Update, context: CallbackContext) -> None:
    #keyboard = [
    #    [InlineKeyboardButton("Старт", callback_data='start')],
    #]
    #reply_markup = InlineKeyboardMarkup(keyboard)
    #update.message.reply_text('Привет! Я ваш бот.', reply_markup=reply_markup)
    #update.message.reply_text('Привет! Я ваш бот.')
    response = requests.get(f'{API_URL}/start', params={'user_id': update.effective_user.id})
    update.message.reply_text(text=f"Список команд:\n/start\n/help\n/balance\n/add X\n/check_status")


def button(update: Update, context: CallbackContext) -> None:
    pass
    '''
    print("C")
    query = update.callback_query
    query.answer()
    print("D")
    if query.data == 'start':
        print('A')
        response = requests.post(f'{API_URL}/start', data={'user_id': update.effective_user.id})
        print('B')
        query.edit_message_text(text=f"Список команд:\n/start\n/help\n/balance\n/add X")
    '''

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Список команд:\n/start\n/help\n/balance\n/add X')

def balance(update: Update, context: CallbackContext) -> None:
    response = requests.get(f'{API_URL}/balance', params={'user_id': update.effective_user.id})
    update.message.reply_text(response.text)

def add(update: Update, context: CallbackContext) -> None:
    credits = int(context.args[0])
    response = requests.get(f'{API_URL}/add', params={'user_id': update.effective_user.id, 'credits': credits})
    update.message.reply_text(response.text)

def handle_document(update: Update, context: CallbackContext) -> None:
    file = context.bot.getFile(update.message.document.file_id)
    file_name = update.message.document.file_name
    file_content = file_content[file_name] = file.download_as_bytearray().decode("utf-8")
    temp_file = io.BytesIO(file_content[file_name].encode("utf-8"))
    
    response = requests.post(f'{API_URL}/process-csv/{update.effective_user.id}', files={file_name: temp_file})
    update.message.reply_text(response.text)

def check_file_status(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    response = requests.get(f'{API_URL}/get-results/{user_id}')
    if response.status_code == 200:
        # Save the file locally
        with open(f"{user_id}_results.csv", 'wb') as f:
            f.write(response.content)
        # Send the file to the user
        with open(f"{user_id}_results.csv", 'rb') as f:
            context.bot.send_document(chat_id=user_id, document=f)
    else:
        update.message.reply_text("API не вернула код 200")
def main() -> None:
    bot = Bot(TOKEN)
    updater = Updater(bot=bot)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("check_status", check_file_status))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
