# bot_jarox.py
import os
import logging
import random
import string
import json  # JSON kütüphanesini ekledik
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import datetime

# -------- CONFIG --------
TOKEN = "8370508611:AAEg3PaLlkMuE9Eww0tG1PPUkv3dGTDCFWY"
IMG_LINK = "https://i.ibb.co/DHJVsNDW/resimadi.png"
LOGFILE = "logs.txt"
DATAFILE = "admin_data.json"  # Veri dosyasını tanımladık
# ------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global state variables
awaiting_admin_key = set()
awaiting_ban = set()
awaiting_unban = set()
banned_users = set()

# admin_keys ve user_sessions artık kalıcı hale gelecek
admin_keys = {}
user_sessions = dict()

def add_log(txt: str):
    """Appends a log entry to the log file."""
    line = f"[{datetime.utcnow().isoformat()}Z] {txt}\n"
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(line)

def save_data():
    """Saves admin keys and banned users to a file."""
    data = {
        "admin_keys": admin_keys,
        "banned_users": list(banned_users)
    }
    with open(DATAFILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    add_log("Veriler dosyaya kaydedildi.")

def load_data():
    """Loads admin keys and banned users from a file."""
    global admin_keys, banned_users
    if os.path.exists(DATAFILE):
        with open(DATAFILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            admin_keys = data.get("admin_keys", {"jarox31": "Ana Admin"})
            banned_users = set(data.get("banned_users", []))
    else:
        # Eğer dosya yoksa, ilk admin keyini oluştur
        admin_keys["jarox31"] = "Ana Admin"
    add_log("Veriler dosyadan yüklendi.")


def build_start_keyboard():
    """Builds the keyboard for the initial start menu."""
    keyboard = [
        [InlineKeyboardButton("👑 Admin Giriş", callback_data="admin_enter"),
         InlineKeyboardButton("🧑‍💻 Misafir", callback_data="guest_enter")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_admin_keyboard(level):
    """Builds the admin panel keyboard based on the admin's level."""
    keyboard = []
    keyboard.append([InlineKeyboardButton("📄 Log Kayıtlarını Gör", callback_data="show_logs")])
    if level == "Ana Admin":
        keyboard.append([InlineKeyboardButton("➕ Yeni Admin Key", callback_data="create_admin_key")])
        keyboard.append([InlineKeyboardButton("🔍 Admin İzleme", callback_data="admin_monitor")])
    keyboard.append([InlineKeyboardButton("🗝️ Admin Key Görüntüle", callback_data="view_admin_keys")])
    if level in ["Ana Admin", "Yardımcı"]:
        keyboard.append([InlineKeyboardButton("⛔ Kullanıcı Banla", callback_data="ban_user")])
        keyboard.append([InlineKeyboardButton("✅ Ban Kaldır", callback_data="unban_user")])
    keyboard.append([InlineKeyboardButton("➕ Yeni Özellik Ekle", callback_data="add_feature")])
    keyboard.append([InlineKeyboardButton("🔙 Geri", callback_data="back_start")])
    return InlineKeyboardMarkup(keyboard)

def build_guest_keyboard():
    """Builds the keyboard for the guest menu."""
    keyboard = [
        [InlineKeyboardButton("🛠️ H!le Panel", callback_data="hile_panel")],
        [InlineKeyboardButton("🔙 Geri", callback_data="back_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_hile_keyboard():
    """Builds the keyboard for the 'hile' (cheat) panel."""
    keyboard = [
        [InlineKeyboardButton("And Cheats", url="https://andcheats.corex.sbs"),
         InlineKeyboardButton("AfkHoti", url="https://afkhoti.com")],
        [InlineKeyboardButton("Astor Panelleri", url="https://afkhoti.com")],
        [InlineKeyboardButton("🎁 Hile Al", callback_data="hile_al")],
        [InlineKeyboardButton("🔙 Geri", callback_data="guest_enter")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, showing the initial welcome message."""
    user = update.effective_user
    if user.id in banned_users:
        return
    name = user.first_name or user.username or "Kanka"
    caption = f"Merhaba {name}!\n\nJarox Tool — Hoşgeldin.\nDenemek İçin Giriş Yapın."
    add_log(f"{user.id} ({name}) komut: /start")
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=IMG_LINK,
            caption=caption,
            reply_markup=build_start_keyboard()
        )
    except Exception as e:
        logger.warning("Foto gönderilemedi, metin ile gönderiliyor: %s", e)
        await update.message.reply_text(f"{caption}\n\nResim: {IMG_LINK}", reply_markup=build_start_keyboard())

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes callback queries from inline keyboard buttons."""
    query = update.callback_query
    user = query.from_user
    uid = user.id
    data = query.data
    await query.answer()
    add_log(f"{uid} ({user.first_name}) callback: {data}")

    if uid in banned_users:
        await context.bot.send_message(chat_id=uid, text="🚫 Banlısınız, işlem yapamazsınız.")
        return

    user_level = user_sessions.get(uid, None)

    if data == "admin_enter":
        awaiting_admin_key.add(uid)
        await context.bot.send_message(chat_id=uid, text="🔐 Lütfen Key Girin:")
        return

    if data == "guest_enter":
        await context.bot.send_message(chat_id=uid,
            text="Ne yapmak istersiniz?",
            reply_markup=build_guest_keyboard())
        return

    if data == "back_start":
        await context.bot.send_message(chat_id=uid,
            text="Geri döndün. Ana menü:",
            reply_markup=build_start_keyboard())
        return

    if data == "show_logs":
        if not os.path.exists(LOGFILE):
            await context.bot.send_message(chat_id=uid, text="Henüz log dosyası yok.")
            return
        try:
            await context.bot.send_document(chat_id=uid, document=open(LOGFILE, "rb"))
        except Exception as e:
            logger.error("Log gönderilemedi: %s", e)
            await context.bot.send_message(chat_id=uid, text="Log dosyası gönderilemedi.")
        return

    if data == "admin_monitor":
        if user_level != "Ana Admin":
            await context.bot.send_message(chat_id=uid, text="❌ Sadece Ana Admin görebilir.")
            return
        if not os.path.exists(LOGFILE):
            await context.bot.send_message(chat_id=uid, text="Henüz log dosyası yok.")
            return
        try:
            with open(LOGFILE, "r", encoding="utf-8") as f:
                logs = f.read()
            await context.bot.send_message(chat_id=uid, text=f"📊 Admin İzleme Logları:\n{logs}")
        except Exception as e:
            logger.error("Admin log gönderilemedi: %s", e)
            await context.bot.send_message(chat_id=uid, text="Admin logları gösterilemedi.")
        return

    if data == "hile_panel":
        await context.bot.send_message(chat_id=uid,
            text="Aşağıdaki panelleri inceleyebilirsin:",
            reply_markup=build_hile_keyboard())
        return

    if data == "hile_al":
        await context.bot.send_message(chat_id=uid,
            text="Uygun Fiyata Hile Almak İçin @wortersyxyz\nSponsor Olmak İçin @JaroxOrj")
        return

    if data == "add_feature":
        await context.bot.send_message(chat_id=uid, text="Yeni özellik eklendi ✅")
        return

    if data == "ban_user":
        if user_level not in ["Ana Admin", "Yardımcı"]:
            await context.bot.send_message(chat_id=uid, text="❌ Bu yetkiye sahip değilsin.")
            return
        awaiting_ban.add(uid)
        await context.bot.send_message(chat_id=uid, text="Banlamak istediğiniz kullanıcının ID’sini yazın:")
        return

    if data == "unban_user":
        if user_level not in ["Ana Admin", "Yardımcı"]:
            await context.bot.send_message(chat_id=uid, text="❌ Bu yetkiye sahip değilsin.")
            return
        awaiting_unban.add(uid)
        await context.bot.send_message(chat_id=uid, text="Banı kaldırmak istediğiniz kullanıcının ID’sini yazın:")
        return

    if data == "create_admin_key":
        if user_level != "Ana Admin":
            await context.bot.send_message(chat_id=uid, text="❌ Sadece Ana Admin yeni key oluşturabilir.")
            return
        keyboard = [
            [InlineKeyboardButton("1 - Ana Admin", callback_data="key_level_1")],
            [InlineKeyboardButton("2 - Yardımcı", callback_data="key_level_2")],
            [InlineKeyboardButton("3 - Çaylak", callback_data="key_level_3")],
        ]
        await context.bot.send_message(chat_id=uid, text="Hangi admin seviyesi vermek istiyorsun?", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("key_level_"):
        if user_level != "Ana Admin":
             await context.bot.send_message(chat_id=uid, text="❌ Bu yetkiye sahip değilsin.")
             return
        level_map = {"key_level_1": "Ana Admin", "key_level_2": "Yardımcı", "key_level_3": "Çaylak"}
        level = level_map[data]
        new_key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        admin_keys[new_key] = level
        save_data()  # Veriyi kaydet
        await context.bot.send_message(chat_id=uid, text=f"Yeni Admin Key Oluşturuldu: {new_key}\nSeviye: {level}")
        add_log(f"{uid} ({user.first_name}) yeni key oluşturdu: {new_key} ({level})")
        return

    if data == "view_admin_keys":
        if not admin_keys:
            await context.bot.send_message(chat_id=uid, text="Aktif admin key yok.")
            return
        msg = "Aktif Admin Keyler:\n"
        for k, v in admin_keys.items():
            msg += f"{k} → {v}\n"
        msg += "\nİptal etmek için /delkey <key> komutunu kullanabilirsiniz."
        await context.bot.send_message(chat_id=uid, text=msg)
        return

# -------- TEXT HANDLER --------
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages, checking for admin keys, bans, and other commands."""
    user = update.effective_user
    text = update.message.text.strip()
    uid = user.id
    user_level = user_sessions.get(uid, None)

    if uid in banned_users:
        return

    # Admin key giriş
    if uid in awaiting_admin_key:
        awaiting_admin_key.discard(uid)
        level = admin_keys.get(text, None)
        if level:
            user_sessions[uid] = level
            await context.bot.send_message(chat_id=uid,
                text=f"✅ Merhaba {level}!\nAdmin paneline erişmek için butona tıkla.",
                reply_markup=build_admin_keyboard(level))
            add_log(f"{uid} ({user.first_name}) başarılı admin girişi: {text} ({level})")
        else:
            await context.bot.send_message(chat_id=uid, text="🚫 Hatalı key. Ana menüye dönülüyor.", reply_markup=build_start_keyboard())
            add_log(f"{uid} ({user.first_name}) hatalı admin key girişi: {text}")
        return

    # Banlama
    if uid in awaiting_ban:
        try:
            ban_id = int(text)
            banned_users.add(ban_id)
            save_data()  # Veriyi kaydet
            await context.bot.send_message(chat_id=uid, text=f"Kullanıcı {ban_id} banlandı ✅")
            add_log(f"{uid} ({user.first_name}) kullanıcı {ban_id} banladı.")
        except ValueError:
            await context.bot.send_message(chat_id=uid, text="Geçerli bir ID girin.")
        awaiting_ban.discard(uid)
        return

    # Ban kaldırma
    if uid in awaiting_unban:
        try:
            unban_id = int(text)
            if unban_id in banned_users:
                banned_users.remove(unban_id)
                save_data()  # Veriyi kaydet
                await context.bot.send_message(chat_id=uid, text=f"Kullanıcı {unban_id} banı kaldırıldı ✅")
                add_log(f"{uid} ({user.first_name}) kullanıcı {unban_id} ban kaldırdı.")
            else:
                await context.bot.send_message(chat_id=uid, text="Bu kullanıcı banlı değil.")
        except ValueError:
            await context.bot.send_message(chat_id=uid, text="Geçerli bir ID girin.")
        awaiting_unban.discard(uid)
        return

    # Key silme
    if text.startswith("/delkey"):
        if user_level != "Ana Admin":
            await context.bot.send_message(chat_id=uid, text="❌ Sadece Ana Admin key silebilir.")
            return

        parts = text.split()
        if len(parts) == 2:
            key_to_delete = parts[1]
            if key_to_delete in admin_keys:
                del admin_keys[key_to_delete]
                save_data()  # Veriyi kaydet
                await context.bot.send_message(chat_id=uid, text=f"Key {key_to_delete} iptal edildi ✅")
            else:
                await context.bot.send_message(chat_id=uid, text="Böyle bir key yok.")
        else:
            await context.bot.send_message(chat_id=uid, text="Doğru kullanım: /delkey <key>")
        return

    add_log(f"{uid} ({user.first_name}) mesaj: {text}")
    await update.message.reply_text("Knk: komutları kullan veya /start ile başla. 🫡")

# -------- ERROR HANDLER --------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Logs errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# -------- MAIN --------
def main():
    """Starts the bot."""
    load_data()  # Bot başlarken verileri yükle
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    app.add_error_handler(error_handler)

    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    if not os.path.exists(LOGFILE):
        open(LOGFILE, "w", encoding="utf-8").close()
    main()
