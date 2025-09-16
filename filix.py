from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

# Token'ını buraya ekle! ASLA kimseyle paylaşma! 🔒
TOKEN = "8307191859:AAEMTY6V1QSCDlxunPG_MmFv9H7TCiNQ4jg"

# Ana menü ve Android menüsü butonlarını tutacak sabitler
MAIN_MENU_KEYBOARD = [
    [InlineKeyboardButton("🚀 Android", callback_data='android')],
    [InlineKeyboardButton("🍎 iOS", callback_data='ios')]
]

ANDROID_MENU_KEYBOARD = [
    [InlineKeyboardButton("🔥 Monster Cheat", callback_data='monster')],
    [InlineKeyboardButton("✨ And Cheats", callback_data='andcheats')],
    [InlineKeyboardButton("💎 Zolo Cheat", callback_data='zolo')],
    [InlineKeyboardButton("🌟 STAR", callback_data='star')],
    [InlineKeyboardButton("⬅️ Geri", callback_data='back_to_main')]
]

async def start(update: Update, context: CallbackContext):
    """Kullanıcı botu başlattığında gönderilecek başlangıç mesajı."""
    user_name = update.effective_user.first_name
    
    await update.message.reply_text(
        text=f"Selam {user_name}! 👋\n\nSenin için en iyi hileleri seçmeye hazırız! 🎮 Lütfen platformunu seç:",
        reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD)
    )

async def button(update: Update, context: CallbackContext):
    """Kullanıcının bastığı butonlara göre işlem yapar."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'android':
        await query.edit_message_text(
            text="Android seçenekleri burada! 🤖 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(ANDROID_MENU_KEYBOARD)
        )
    
    elif query.data == 'ios':
        await query.edit_message_text(
            text="📱 iOS kullanıcıları için harika hileler yakında geliyor! Sabırsızlanıyoruz! ✨",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data='back_to_main')]])
        )
    
    elif query.data == 'back_to_main':
        await query.edit_message_text(
            text="Hile almak için tür seçin:",
            reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD)
        )

    elif query.data == 'back_to_android':
        await query.edit_message_text(
            text="Android seçenekleri burada! 🤖 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(ANDROID_MENU_KEYBOARD)
        )

    elif query.data in ['monster', 'andcheats', 'zolo', 'star']:
        if query.data == 'monster':
            text = "Monster Cheat\n\n" \
                   "🌟 **Günlük:** 230₺\n" \
                   "🌟 **Haftalık:** 650₺\n" \
                   "🌟 **Aylık:** 900₺"
        elif query.data == 'andcheats':
            text = "And Cheats\n\n" \
                   "🚀 **Günlük:** 210₺\n" \
                   "🚀 **Haftalık:** 600₺\n" \
                   "🚀 **Aylık:** 800₺"
        elif query.data == 'zolo':
            text = "Zolo Cheat\n\n" \
                   "💎 **Günlük:** 450₺\n" \
                   "💎 **Haftalık:** 700₺\n" \
                   "💎 **Aylık:** 950₺"
        elif query.data == 'star':
            text = "STAR\n\n" \
                   "✨ **Günlük:** 285₺\n" \
                   "✨ **Haftalık:** 870₺\n" \
                   "✨ **Aylık:** 1200₺"
        
        # Her alt menüde geri butonu olacak şekilde düzenlendi
        back_button = [[InlineKeyboardButton("⬅️ Geri", callback_data='back_to_android')]]
        buy_button = [
            [InlineKeyboardButton("🛒 HEMEN SATIN AL", url="https://t.me/wortersyxyz")],
            [InlineKeyboardButton("⬅️ Geri", callback_data='back_to_android')]
        ]

        await query.edit_message_text(
            text=text, 
            reply_markup=InlineKeyboardMarkup(buy_button),
            parse_mode='Markdown'
        )

# --- Bot Başlatma Fonksiyonu ---

def main():
    """Botu başlatır ve çalıştırır."""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    print("Bot çalışmaya başladı! /start komutuyla test edebilirsiniz.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
