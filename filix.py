import telebot
from telebot import types
from PIL import Image

TOKEN = "7955274406:AAH8dB_u7AFsSXaxDJvcgIUznXcEv7F1goo"
OWNER_ID = 8392023129

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Sipariş Ver", callback_data="order")
    keyboard.add(button)
    bot.send_message(message.chat.id, "Merhaba, logo yaptırmak için butonlara tıklayın:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "order":
        bot.send_message(call.message.chat.id, "Lütfen logo örneğini gönderin.")

def save_photo(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except:
        return False

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f"{message.from_user.id}_logo.png"
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    
    if save_photo(file_path):
        bot.send_message(message.chat.id, "Sipariş alındı, 24 saat içinde hazır olacak.")
        bot.send_photo(OWNER_ID, open(file_path, 'rb'), caption=f"{message.from_user.first_name} kullanıcısından logo siparişi")
    else:
        bot.send_message(message.chat.id, "Geçersiz resim, lütfen tekrar deneyin.")

bot.polling(none_stop=True)