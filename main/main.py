from turtle import update
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from functions import get_available_chats, shorten_string
from messages import add_message, remove_message, get_first_message
from payments import add_payment, remove_payment, get_first_payment


TOKEN: Final = "6496118596:AAHE7ELJ5j_ZIwANSR99wNg8Nb5oeFJUrK8"
ADMIN_IDS: list[int] = [885083447, 5363870762]

# Storage of chats, messages and available admins
active_chats: dict[int:int or None] = {}  # Active chats in {user_id: admin_id} format
active_admin_chats: dict[int:int] = {}  # Active chats in {admin_id: user_id} format
available_admins: list[int] = []  # List of available admins
users_sending_questions: list[int] = []  # List of users sending questions to the database
users_sending_payments: list[int] = []  # List of users sending questions to the database
admins_reading_questions: dict[int:dict or None] = {}  # List of admins answering questions from the database
admins_reading_payments: dict[int:dict or None] = {}  # List of admins answering questions from the database


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   buttons = [
        [InlineKeyboardButton("Задать вопрос на стрим", callback_data='question')],
        [InlineKeyboardButton("Связь с нами", callback_data='chat')],
        [InlineKeyboardButton("Библиотека", callback_data='lib')],
        [InlineKeyboardButton("Вступить в сообщество", callback_data='subscribe')]
    ]
   buttons_admin = [
        [InlineKeyboardButton("Вопросы на стрим", callback_data='question')],
        [InlineKeyboardButton("Чат с пользователями", callback_data='chat')],
        [InlineKeyboardButton("Библиотека", callback_data='lib')],
        [InlineKeyboardButton("Вступить в сообщество", callback_data='subscribe')]
    ]
   if update.message.from_user.id in ADMIN_IDS:
        reply_markup = InlineKeyboardMarkup(buttons_admin)
   else:
       reply_markup = InlineKeyboardMarkup(buttons)
   await update.message.reply_photo(photo = "Tg Bot cover.png", caption = 'Добро пожаловать в Midas Hall bot!', reply_markup=reply_markup)



async def button_click(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'question':
        await help_command(update, context)
    elif query.data == 'chat':
        await chat_command(update, context)
    elif query.data == 'lib':
        await lib_command(update, context)
    elif query.data == 'subscribe':
        await subscribe_command(update, context)
    elif query.data == 'payment':
        await payment_command(update, context)


async def show_stored_message(admin_id: int, update: Update):
    first_message = get_first_message()
    if first_message is None:
        await update.message.reply_text("Нет заданных вопросов.")
        if admin_id in admins_reading_questions:
            admins_reading_questions.pop(admin_id)
    else:
        admins_reading_questions[admin_id] = first_message
        await update.message.reply_text(f"Сообщение от пользователя {first_message['username']}:\n{first_message['message']}")

async def show_stored_payments(admin_id: int, update: Update):
    first_message = get_first_payment()
    if first_message is None:
        await update.message.reply_text("Нет информации об оплате.")
        if admin_id in admins_reading_payments:
            admins_reading_payments.pop(admin_id)
    else:
        admins_reading_payments[admin_id] = first_message
        await update.message.reply_text(f"Информация об оплате от пользователя {first_message['username']}:\n{first_message['message']}")
        await update.message.reply_text(f"Для продолжения напишите команду /paid")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message):
        user_id = update.message.from_user.id
    else:
       user_id = update.callback_query.from_user.id
       update = update.callback_query
    if user_id in ADMIN_IDS:
        if user_id not in admins_reading_questions:
            admins_reading_questions[user_id] = None

        await show_stored_message(user_id, update)
    else:
        users_sending_questions.append(user_id)
        await update.message.reply_text('Задайте свой вопрос:')


async def lib_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message):
        user_id = update.message.from_user.id
    else:
       user_id = update.callback_query.from_user.id
       update = update.callback_query
    await update.message.reply_text('Наша библиотека - midashall.notion.site')


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message):
        user_id = update.message.from_user.id
    else:
       user_id = update.callback_query.from_user.id
       update = update.callback_query
    """buttons = [
        [InlineKeyboardButton("Я оплатил", callback_data='payment')]
    ]
    buttons_admin = [
        [InlineKeyboardButton("Информация об оплате", callback_data='payment')]
    ]
    if user_id in ADMIN_IDS:
        reply_markup = InlineKeyboardMarkup(buttons_admin)
        await update.message.reply_text('Нажмите на кнопку чтобы просмотреть информацию об оплате.', reply_markup = reply_markup)
    else:
        reply_markup = InlineKeyboardMarkup(buttons)"""
    await update.message.reply_text('К сожалению пока что приобретение подписки недоступно.')
        #await update.message.reply_text('Реквизиты для оплаты в USDT TRC-20:')
        #await update.message.reply_photo(photo = "qr.png", caption = 'TCiakj1tv596hVXrwr27NSy3ddKF9YZjoN', reply_markup = reply_markup)

async def payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message):
        user_id = update.message.from_user.id
    else:
       user_id = update.callback_query.from_user.id
       update = update.callback_query
    if user_id in ADMIN_IDS:
        if user_id not in admins_reading_payments:
            admins_reading_payments[user_id] = None

        await show_stored_payments(user_id, update)
    else:
        users_sending_payments.append(user_id)
        await update.message.reply_text('Напишите свой ник в Discord и электронную почту:')



def get_available_chats() -> list[int]:
    return [key for key, value in active_chats.items() if value is None]


async def connect_admin_to_chat(admin_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_chats = get_available_chats()
    if len(available_chats) > 0:
        first_chat = available_chats[0]

        active_chats[first_chat] = admin_id
        active_admin_chats[admin_id] = first_chat

        await update.message.reply_text(
            f"Вы подключены к чату с пользователем {first_chat}. Напишите '/end' что бы завершить.")
        await context.bot.send_message(
            chat_id=first_chat,
            text="Вы подключены к чату с Midas Hall. Что вас интересует?"
        )
    else:
        if admin_id not in available_admins:
            available_admins.append(admin_id)
        await update.message.reply_text("Ожидайте вопросов от пользователей. Напишите '/leave' если хотите выйти.")


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message):
        user_id = update.message.from_user.id
    else:
       user_id = update.callback_query.from_user.id
       update = update.callback_query
    if user_id in ADMIN_IDS:
        await connect_admin_to_chat(user_id, update, context)
    else:
        if len(available_admins) > 0:
            first_admin = available_admins[0]
            active_chats[user_id] = first_admin
            active_admin_chats[first_admin] = user_id
            available_admins.remove(first_admin)
            await context.bot.send_message(
                chat_id=first_admin,
                text=f"Вы подключены к чату с пользователем {user_id}. Напишите '/end' что бы завершить."
            )
            await update.message.reply_text("Вы начали чат с Midas Hall. Пожалуйста, задайте ваш вопрос и "
                                            "ожидайте ответ.")
        else:
            active_chats[user_id] = None
            await update.message.reply_text(f"Пожалуйста подождите, вы {len(get_available_chats())} в очереди.")

    print(active_chats, active_admin_chats, available_admins)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(active_chats)
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message = update.message.text
    if user_id in active_chats:
        admin_chat_id = active_chats[user_id]
        if admin_chat_id is None:
            await update.message.reply_text("На данный момент нет администраторов онлайн. Попробуйте снова позже.")
        else:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=f"Сообщение от пользователя {update.message.from_user.username}:\n{message}"
            )
    elif user_id in users_sending_questions:
        add_message(user_id, username, message)
        users_sending_questions.remove(user_id)
        await update.message.reply_text("Мы с радостью рассмотрим ваш вопрос на конференции!")
    elif user_id in users_sending_payments:
        add_payment(user_id, username, message)
        users_sending_payments.remove(user_id)
        await update.message.reply_text("Информация об оплате отправлена!")
    else:
        await update.message.reply_text("Неизвестная команда.")


async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(admins_reading_questions)
    text_message = update.message.text
    admin_id = update.message.from_user.id
    user_id = active_admin_chats.get(admin_id, None)
    if text_message == '/end':
        if admin_id not in active_admin_chats and user_id not in active_chats:
            await update.message.reply_text('Вы не подключены к чату.')
        else:
            active_chats.pop(user_id)
            active_admin_chats.pop(admin_id)
            await update.message.reply_text(f'Чат с {user_id} завершен.')
            await context.bot.send_message(
                chat_id=user_id,
                text="Чат с Midas Hall завершен."
            )
            await connect_admin_to_chat(admin_id, update, context)
            print(active_chats, active_admin_chats, available_admins)
    elif text_message == '/leave':
        if admin_id in available_admins:
            available_admins.remove(admin_id)
            await update.message.reply_text('Вы вышли из режима чатов.')
        else:
            await update.message.reply_text('Вы не в режиме чатов.')
    elif text_message == '/done':
        if admin_id in admins_reading_questions:
            message_id = admins_reading_questions[admin_id]['message_id']
            remove_message(message_id)
            if admin_id in admins_reading_questions:
                admins_reading_questions.pop(admin_id)
            await update.message.reply_text('Вопрос закрыт.')
            await show_stored_message(admin_id, update)
        else:
            await update.message.reply_text('Вы не в режиме чтения вопросов.')
    elif text_message == '/paid':
        if admin_id in admins_reading_payments:
            message_id = admins_reading_payments[admin_id]['message_id']
            remove_payment(message_id)
            if admin_id in admins_reading_payments:
               admins_reading_payments.pop(admin_id)
            await update.message.reply_text('Оплачено!')
            await show_stored_payments(admin_id, update)
        else:
            await update.message.reply_text('Вы не в режиме оплаты.')
    else:
        if user_id is None:
            await update.message.reply_text('Вы не подключены к чату.')
        else:
            await context.bot.send_message(chat_id=user_id, text=update.message.text)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')


if __name__ == '__main__':
    print('starting bot')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('lib', lib_command))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("subsribe", subscribe_command))
    app.add_handler(CommandHandler("payment", payment_command))

    # Messages
    app.add_handler(MessageHandler(filters.User(ADMIN_IDS), handle_admin_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=1)

