import random, time, json, os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "TOKEN_BURAYA"

ADMIN_IDS = [123456789]  # KENDİ ID'Nİ YAZ

DATA_FILE = "data.json"

# ================= VERİ =================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        DATA = json.load(f)
else:
    DATA = {"balance": {}, "daily": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f)

def get_balance(uid):
    uid = str(uid)
    if uid not in DATA["balance"]:
        DATA["balance"][uid] = 1000
        save_data()
    return DATA["balance"][uid]

def set_balance(uid, amount):
    DATA["balance"][str(uid)] = amount
    save_data()

def is_admin(uid):
    return uid in ADMIN_IDS
# =======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    bal = get_balance(uid)

    await update.message.reply_text(
        f"🎰 *Casino Bot*\n\n"
        f"👤 ID: `{uid}`\n"
        f"💰 Bakiye: {bal}\n\n"
        f"Oyunlar:\n"
        f"/slot <miktar>\n"
        f"/zar <miktar>\n"
        f"/yazitura <miktar>\n\n"
        f"Diğer:\n"
        f"/bakiye\n"
        f"/gunluk\n"
        f"/transfer <id> <miktar>\n"
        f"/top\n",
        parse_mode="Markdown"
    )

async def bakiye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"💰 Bakiyen: {get_balance(uid)}")

# ---------- GÜNLÜK ----------
async def gunluk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    now = time.time()

    if uid in DATA["daily"] and now - DATA["daily"][uid] < 86400:
        return await update.message.reply_text("⏳ Günlük ödülü aldın.")

    DATA["daily"][uid] = now
    DATA["balance"][uid] = get_balance(uid) + 300
    save_data()
    await update.message.reply_text("🎁 Günlük +300 coin!")

# ---------- OYUNLAR ----------
async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        bet = int(context.args[0])
    except:
        return await update.message.reply_text("❌ /slot <miktar>")

    bal = get_balance(uid)
    if bet <= 0 or bet > bal:
        return await update.message.reply_text("❌ Geçersiz miktar.")

    DATA["balance"][str(uid)] -= bet
    spin = [random.choice(["🍒","🍋","🍉","⭐","🔔"]) for _ in range(3)]

    if spin.count(spin[0]) == 3:
        win = bet * 3
        DATA["balance"][str(uid)] += win
        msg = f"🎉 JACKPOT +{win}"
    else:
        msg = f"❌ Kaybettin -{bet}"

    save_data()
    await update.message.reply_text(
        f"🎰 {' | '.join(spin)}\n{msg}\n💰 {get_balance(uid)}"
    )

async def zar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        bet = int(context.args[0])
    except:
        return await update.message.reply_text("❌ /zar <miktar>")

    bal = get_balance(uid)
    if bet <= 0 or bet > bal:
        return await update.message.reply_text("❌ Geçersiz miktar.")

    DATA["balance"][str(uid)] -= bet
    dice = random.randint(1, 6)

    if dice >= 4:
        win = bet * 2
        DATA["balance"][str(uid)] += win
        msg = f"🎉 Kazandın +{win}"
    else:
        msg = f"❌ Kaybettin -{bet}"

    save_data()
    await update.message.reply_text(
        f"🎲 Zar: {dice}\n{msg}\n💰 {get_balance(uid)}"
    )

async def yazitura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        bet = int(context.args[0])
    except:
        return await update.message.reply_text("❌ /yazitura <miktar>")

    bal = get_balance(uid)
    if bet <= 0 or bet > bal:
        return await update.message.reply_text("❌ Geçersiz miktar.")

    DATA["balance"][str(uid)] -= bet
    if random.choice([True, False]):
        win = bet * 2
        DATA["balance"][str(uid)] += win
        msg = f"🎉 Kazandın +{win}"
    else:
        msg = f"❌ Kaybettin -{bet}"

    save_data()
    await update.message.reply_text(f"🪙 Yazı/Tura\n{msg}\n💰 {get_balance(uid)}")

# ---------- TRANSFER ----------
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(context.args) < 2:
        return await update.message.reply_text("❌ /transfer <id> <miktar>")

    try:
        target = context.args[0]
        amount = int(context.args[1])
    except:
        return await update.message.reply_text("❌ Hatalı kullanım.")

    if amount <= 0 or amount > get_balance(uid):
        return await update.message.reply_text("❌ Yetersiz bakiye.")

    DATA["balance"][str(uid)] -= amount
    DATA["balance"][target] = get_balance(target) + amount
    save_data()

    await update.message.reply_text(f"✅ {amount} coin gönderildi.")

# ---------- TOP ----------
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_users = sorted(
        DATA["balance"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    msg = "🏆 *Top 10 Zenginler*\n\n"
    for i, (uid, bal) in enumerate(sorted_users, 1):
        msg += f"{i}. `{uid}` → {bal}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------- ADMIN ----------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "👑 *Admin Panel*\n\n"
        "/para <id> <miktar>\n"
        "/bak <id>\n"
        "/sifirla <id>\n",
        parse_mode="Markdown"
    )

async def para(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    target = context.args[0]
    amount = int(context.args[1])
    DATA["balance"][target] = get_balance(target) + amount
    save_data()

    await update.message.reply_text("✅ Para gönderildi.")

async def bak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    uid = context.args[0]
    await update.message.reply_text(f"💰 {uid} → {get_balance(uid)}")

async def sifirla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    uid = context.args[0]
    DATA["balance"][uid] = 1000
    save_data()
    await update.message.reply_text("🔄 Bakiye sıfırlandı.")

def main():
    app = Application.builder().token(TOKEN).build()

    for cmd, func in [
        ("start", start), ("bakiye", bakiye), ("gunluk", gunluk),
        ("slot", slot), ("zar", zar), ("yazitura", yazitura),
        ("transfer", transfer), ("top", top),
        ("admin", admin), ("para", para), ("bak", bak), ("sifirla", sifirla)
    ]:
        app.add_handler(CommandHandler(cmd, func))

    print("🎰 Casino Bot FULL Aktif")
    app.run_polling()

if __name__ == "__main__":
    main()