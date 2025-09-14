# Filix.py
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# .env dosyasını yükle (Render kullanıyorsan environment variables otomatik okunur)
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Sipariş Ver", callback_data='order')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Merhaba, logo yaptırmak için butonlara tıklayın:", reply_markup=reply_markup)

# Buton tıklama işlemi
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "order":
        await query.message.reply_text("Lütfen logo örneğini gönderin.")

# Kullanıcının resim göndermesi
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{user.id}_logo.png"
    await photo_file.download_to_drive(file_path)
    await update.message.reply_text("Sipariş alındı, 24 saat içinde hazır olacak.")
    await context.bot.send_photo(chat_id=OWNER_ID, photo=open(file_path, 'rb'), caption=f"{user.first_name} kullanıcısından logo siparişi")
    os.remove(file_path)  # Gönderimden sonra dosyayı sil

# Bot uygulaması
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, photo))

# Botu çalıştır
print("Bot çalışıyor...")
app.run_polling()
