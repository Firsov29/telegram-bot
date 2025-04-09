# main.py
from keep_alive import keep_alive
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔑 ДАННЫЕ
TOKEN = '7501058690:AAHvSQQxiL-9KymG46lg7b90RrTFGsGBjXg'
CHANNEL_USERNAME = '@ibragim_firsov'
ARTICLE_LINK = 'https://teletype.in/@ibragimfirsov/IbragimMoneyondesign'
PHOTO_FILE_ID = 'AgACAgIAAxkBAAOEZ_V_CERE4A1ozgyWt6ZnrE6MzLUAApbuMRtN4LBLJl0aPexTpBwBAAMCAAN4AAM2BA'

bot = telebot.TeleBot(TOKEN)

# 🧠 ПОДКЛЮЧЕНИЕ К GOOGLE SHEETS
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('graphic-segment-456309-n3-64bdb79ff4e4.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1nwFFM6cg6VBOTT6EqWF0QfTSvhGUvku_zU9t0RYTdXU').worksheet("Лист1")

# 🔷 ФУНКЦИЯ ЗАПИСИ В ТАБЛИЦУ
def log_to_sheet(user):
    username = f"@{user.username}" if user.username else "[no username]"
    sheet.append_row([
        user.first_name,
        username,
        str(user.id),
        datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ])

# 🔐 ПРОВЕРКА ПОДПИСКИ
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# 📍 КОМАНДА /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton('✅ Готово', callback_data='check_sub')
    markup.add(btn)

    caption = (
        "Привет! Чтобы получить статью — подпишись на канал @ibragim_firsov и нажми кнопку ниже\n\n"
        "📌 «Как мы собрали 50 человек на продукт с нуля»"
    )
    bot.send_photo(user_id, PHOTO_FILE_ID, caption=caption, reply_markup=markup)

# 🔹 ОБРАБОТЧИК КНОПКИ "ГОТОВО"
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        log_to_sheet(call.from_user)
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="🎉 Вижу твою подписку. Забирай статью:\n\n" + ARTICLE_LINK
        )
    else:
        bot.answer_callback_query(call.id, text="Ты ещё не подписан!")
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton('✅ Готово', callback_data='check_sub')
        markup.add(btn)
        bot.send_message(
            call.message.chat.id,
            f"Ты всё ещё не подписан(а) на {CHANNEL_USERNAME}. Пожалуйста, подпишись и нажми кнопку «Готово».",
            reply_markup=markup
        )

# 🚀 ЗАПУСК
keep_alive()
bot.infinity_polling()
