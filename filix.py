import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
from dotenv import load_dotenv

# .env dosyasından bot token'ını yükleyin
load_dotenv()
API_TOKEN = os.getenv("8487383178:AAF488Ea6UXzeuJXSKR6u0nzUZzcLNB6PM8")
ADMIN_ID = 8392023129  # Admin ID

# Botu başlatın
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Logger ayarları
logging.basicConfig(level=logging.INFO)

# Kullanıcıların sırası
user_queue = {}

# /start komutu
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = message.from_user
    await message.answer(
        f"Hoşgeldin {user.first_name} 🎉! Sipariş vermek için aşağıdaki butona tıklayın.",
        reply_markup=types.ReplyKeyboardMarkup(
            [[types.KeyboardButton("Sipariş Ver")]], resize_keyboard=True, one_time_keyboard=True
        )
    )

# "Sipariş Ver" butonuna tıklandığında
@dp.message_handler(lambda message: message.text == "Sipariş Ver")
async def add_gift(message: types.Message):
    await message.answer(
        "@rushexStore'a 15 yıldızlık 2 hediye gönderin, ardından admin onayı için butona tıklayın. 🎁",
        reply_markup=types.ReplyKeyboardMarkup(
            [[types.KeyboardButton("Attım")]], resize_keyboard=True, one_time_keyboard=True
        )
    )

# "Attım" butonuna tıklandığında
@dp.message_handler(lambda message: message.text == "Attım")
async def attim(message: types.Message):
    user_id = message.from_user.id
    user_queue[user_id] = {'status': 'waiting_for_admin_approval'}

    # Admin'e onay isteği gönderilir
    await bot.send_message(
        ADMIN_ID,
        f"{message.from_user.first_name} ({user_id}) logo için onay bekliyor. Onaylamak için 'evet', reddetmek için 'hayır' yazın. 🔥",
    )
    await message.answer(
        "Hediye göndermeniz başarıyla alındı. Admin onayını bekleyin. ⏳"
    )

# Admin onayını almak
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID)
async def admin_approval(message: types.Message):
    if message.text.lower() == "evet" and user_queue:
        user_id = list(user_queue.keys())[0]
        user_queue[user_id]['status'] = 'approved'
        await bot.send_message(
            user_id,
            "Logo işleminiz onaylandı! Şimdi logo üzerinde ne yazmasını istediğinizi belirtin. 🖋️"
        )
        await message.answer("Onay verildi, işlemi devam ettiriyorum.")
    elif message.text.lower() == "hayır" and user_queue:
        user_id = list(user_queue.keys())[0]
        await bot.send_message(user_id, "Üzgünüz, logo talebiniz reddedildi. 🙁")
        await message.answer("Logo talebi reddedildi.")

# Kullanıcıdan logo metnini almak
@dp.message_handler(lambda message: message.from_user.id in user_queue and user_queue[message.from_user.id].get('status') == 'approved')
async def process_logo_text(message: types.Message):
    logo_text = message.text
    user_id = message.from_user.id
    user_queue[user_id]['logo_text'] = logo_text

    await message.answer(
        f"Logo metniniz: '{logo_text}' sırasına alındı. Admin'e bildirildi. ✅"
    )

    # Admin'e logo talebi bildirildi
    await bot.send_message(
        ADMIN_ID,
        f"{message.from_user.first_name} logo talebinde bulundu: '{logo_text}'."
    )

# Admin'in logo göndermesi
@dp.message_handler(content_types=['photo'], lambda message: message.from_user.id == ADMIN_ID)
async def admin_send_logo(message: types.Message):
    user_id = list(user_queue.keys())[0]
    if message.photo:
        logo = message.photo[-1].file_id
        await bot.send_photo(chat_id=user_id, photo=logo, caption="Logo hazır! 🎨✨")

        # Admin'e bildirim
        await bot.send_message(ADMIN_ID, "Logo başarıyla gönderildi! 🖼️")

        # Kullanıcıya bildirim
        await bot.send_message(user_id, "Logo başarıyla oluşturuldu ve gönderildi! 🎉")

# Botu çalıştırmak için
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
