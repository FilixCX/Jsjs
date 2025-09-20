from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Doğru import

API_TOKEN = '8487383178:AAF488Ea6UXzeuJXSKR6u0nzUZzcLNB6PM8'
ADMIN_ID = 8392023129  # Admin ID

# Kullanıcıların sırası
user_queue = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f"Hoşgeldin {user.first_name} 🎉! Sipariş vermek için aşağıdaki butona tıklayın.",
        reply_markup=ReplyKeyboardMarkup([["Sipariş Ver"]], resize_keyboard=True)  # "Sipariş Ver" butonu
    )

def add_gift(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    # Kullanıcıya hediyeleri göndermesi hatırlatılır
    update.message.reply_text(
        "@rushexStore'a 15 yıldızlık 2 hediye gönderin, ardından admin onayı için butona tıklayın. 🎁",
        reply_markup=ReplyKeyboardMarkup([["Attım"]], resize_keyboard=True)
    )

def attim(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_queue[user.id] = {'status': 'waiting_for_admin_approval'}
    
    # Admin'e onay isteği gönderilir
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{user.first_name} ({user.id}) logo için onay bekliyor. Onaylamak için evet, reddetmek için hayır yazın. 🔥",
    )
    update.message.reply_text(
        "Hediye göndermeniz başarıyla alındı. Admin onayını bekleyin. ⏳"
    )

def admin_approval(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if update.message.text.lower() == "evet" and user_queue:
        # Admin onay verirse
        user_id = list(user_queue.keys())[0]
        user_queue[user_id]['status'] = 'approved'

        context.bot.send_message(
            chat_id=user_id,
            text="Logo işleminiz onaylandı! Şimdi logo üzerinde ne yazmasını istediğinizi belirtin. 🖋️"
        )
        update.message.reply_text("Onay verildi, işlemi devam ettiriyorum.")
    elif update.message.text.lower() == "hayır" and user_queue:
        # Admin reddederse
        user_id = list(user_queue.keys())[0]
        context.bot.send_message(
            chat_id=user_id,
            text="Üzgünüz, logo talebiniz reddedildi. 🙁"
        )
        update.message.reply_text("Logo talebi reddedildi.")

def process_logo_text(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.id not in user_queue or user_queue[user.id].get('status') != 'approved':
        return

    # Kullanıcıdan logo metni alınır
    logo_text = update.message.text
    user_queue[user.id]['logo_text'] = logo_text

    update.message.reply_text(
        f"Logo metniniz: '{logo_text}' sırasına alındı. Admin'e bildirildi. ✅"
    )

    # Admin'e logo talebi bildirildi
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{user.first_name} logo talebinde bulundu: '{logo_text}'."
    )

def admin_send_logo(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        return

    # Admin logo gönderdiğinde
    if update.message.photo:
        user_id = list(user_queue.keys())[0]
        logo = update.message.photo[-1].file_id
        context.bot.send_photo(chat_id=user_id, photo=logo, caption="Logo hazır! 🎨✨")

        # Admin'e bildirim
        context.bot.send_message(chat_id=ADMIN_ID, text="Logo başarıyla gönderildi! 🖼️")

        # Kullanıcıya bildirim
        context.bot.send_message(chat_id=user_id, text="Logo başarıyla oluşturuldu ve gönderildi! 🎉")

def main():
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # /start komutu
    dispatcher.add_handler(CommandHandler('start', start))

    # Kullanıcı "Sipariş Ver" butonuna tıkladığında
    dispatcher.add_handler(MessageHandler(filters.Regex('^Sipariş Ver$'), add_gift))

    # Kullanıcı "Attım" butonuna tıkladığında
    dispatcher.add_handler(MessageHandler(filters.Regex('^Attım$'), attim))

    # Admin onay isteği
    dispatcher.add_handler(MessageHandler(filters.Text() & filters.User(user_id=ADMIN_ID), admin_approval))

    # Logo metni alma
    dispatcher.add_handler(MessageHandler(filters.Text() & ~filters.Command(), process_logo_text))

    # Admin logo gönderdiğinde
    dispatcher.add_handler(MessageHandler(filters.Photo() & filters.User(user_id=ADMIN_ID), admin_send_logo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
