from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Doğru import

API_TOKEN = '8487383178:AAF488Ea6UXzeuJXSKR6u0nzUZzcLNB6PM8'
ADMIN_ID = 8392023129  # Admin ID

# Kullanıcıların sırası
user_queue = {}

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hoşgeldin {user.first_name} 🎉! Sipariş vermek için aşağıdaki butona tıklayın.",
        reply_markup=ReplyKeyboardMarkup([["Sipariş Ver"]], resize_keyboard=True)  # "Sipariş Ver" butonu
    )

async def add_gift(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    # Kullanıcıya hediyeleri göndermesi hatırlatılır
    await update.message.reply_text(
        "@rushexStore'a 15 yıldızlık 2 hediye gönderin, ardından admin onayı için butona tıklayın. 🎁",
        reply_markup=ReplyKeyboardMarkup([["Attım"]], resize_keyboard=True)
    )

async def attim(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_queue[user.id] = {'status': 'waiting_for_admin_approval'}
    
    # Admin'e onay isteği gönderilir
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{user.first_name} ({user.id}) logo için onay bekliyor. Onaylamak için evet, reddetmek için hayır yazın. 🔥",
    )
    await update.message.reply_text(
        "Hediye göndermeniz başarıyla alındı. Admin onayını bekleyin. ⏳"
    )

async def admin_approval(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if update.message.text.lower() == "evet" and user_queue:
        # Admin onay verirse
        user_id = list(user_queue.keys())[0]
        user_queue[user_id]['status'] = 'approved'

        await context.bot.send_message(
            chat_id=user_id,
            text="Logo işleminiz onaylandı! Şimdi logo üzerinde ne yazmasını istediğinizi belirtin. 🖋️"
        )
        await update.message.reply_text("Onay verildi, işlemi devam ettiriyorum.")
    elif update.message.text.lower() == "hayır" and user_queue:
        # Admin reddederse
        user_id = list(user_queue.keys())[0]
        await context.bot.send_message(
            chat_id=user_id,
            text="Üzgünüz, logo talebiniz reddedildi. 🙁"
        )
        await update.message.reply_text("Logo talebi reddedildi.")

async def process_logo_text(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.id not in user_queue or user_queue[user.id].get('status') != 'approved':
        return

    # Kullanıcıdan logo metni alınır
    logo_text = update.message.text
    user_queue[user.id]['logo_text'] = logo_text

    await update.message.reply_text(
        f"Logo metniniz: '{logo_text}' sırasına alındı. Admin'e bildirildi. ✅"
    )

    # Admin'e logo talebi bildirildi
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{user.first_name} logo talebinde bulundu: '{logo_text}'."
    )

async def admin_send_logo(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        return

    # Admin logo gönderdiğinde
    if update.message.photo:
        user_id = list(user_queue.keys())[0]
        logo = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=user_id, photo=logo, caption="Logo hazır! 🎨✨")

        # Admin'e bildirim
        await context.bot.send_message(chat_id=ADMIN_ID, text="Logo başarıyla gönderildi! 🖼️")

        # Kullanıcıya bildirim
        await context.bot.send_message(chat_id=user_id, text="Logo başarıyla oluşturuldu ve gönderildi! 🎉")

async def main():
    application = Application.builder().token(API_TOKEN).build()

    # /start komutu
    application.add_handler(CommandHandler('start', start))

    # Kullanıcı "Sipariş Ver" butonuna tıkladığında
    application.add_handler(MessageHandler(filters.Regex('^Sipariş Ver$'), add_gift))

    # Kullanıcı "Attım" butonuna tıkladığında
    application.add_handler(MessageHandler(filters.Regex('^Attım$'), attim))

    # Admin onay isteği
    application.add_handler(MessageHandler(filters.Text() & filters.User(user_id=ADMIN_ID), admin_approval))

    # Logo metni alma
    application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), process_logo_text))

    # Admin logo gönderdiğinde
    application.add_handler(MessageHandler(filters.Photo() & filters.User(user_id=ADMIN_ID), admin_send_logo))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
