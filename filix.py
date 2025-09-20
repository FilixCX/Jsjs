from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

# Token'ını buraya ekle! ASLA kimseyle paylaşma! 🔒
TOKEN = "8307191859:AAEMTY6V1QSCDlxunPG_MmFv9H7TCiNQ4jg"

# --- Sabit Menüler ---
MAIN_MENU_KEYBOARD = [
    [InlineKeyboardButton("🚀 Android", callback_data='android')],
    [InlineKeyboardButton("🍎 iOS", callback_data='ios')]
]

ANDROID_MENU_KEYBOARD = [
    [InlineKeyboardButton("🔥 Monster Cheat", callback_data='monster')],
    [InlineKeyboardButton("✨ And Cheats", callback_data='andcheats')],
    [InlineKeyboardButton("💎 Zolo Cheat", callback_data='zolo')],
    [InlineKeyboardButton("🌟 Astor Cheat", callback_data='astor_cheat')],  # Astor Cheat eklendi
    [InlineKeyboardButton("⬅️ Geri", callback_data='back_to_main')]
]

IOS_MENU_KEYBOARD = [
    [InlineKeyboardButton("✨ Star iOS", callback_data='star_ios')],
    [InlineKeyboardButton("👑 King iOS", callback_data='king_ios')],
    [InlineKeyboardButton("⬅️ Geri", callback_data='back_to_main')]
]

# Hile Detayları
HILE_DETAYLARI = {
    'monster': {
        'name': "Monster Cheat",
        'gunluk': "230₺",
        'haftalik': "650₺",
        'aylik': "900₺",
        'link': "https://t.me/wortersyxyz"
    },
    'andcheats': {
        'name': "And Cheats",
        'gunluk': "210₺",
        'haftalik': "600₺",
        'aylik': "800₺",
        'link': "https://t.me/wortersyxyz"
    },
    'zolo': {
        'name': "Zolo Cheat",
        'gunluk': "450₺",
        'haftalik': "700₺",
        'aylik': "950₺",
        'link': "https://t.me/wortersyxyz"
    },
    'astor_cheat': {  # Astor Cheat detayları eklendi
        'name': "Astor Cheat",
        'gunluk': "230₺",
        'haftalik': "650₺",
        'aylik': "900₺",
        'link': "https://t.me/wortersyxyz"
    },
    'star_ios': {
        'name': "Star iOS",
        'gunluk': "285₺",
        'haftalik': "870₺",
        'aylik': "1200₺",
        'link': "https://t.me/wortersyxyz"
    },
    'king_ios': {
        'name': "King iOS",
        'gunluk': "385₺",
        'haftalik': "950₺",
        'aylik': "1500₺",
        'link': "https://t.me/wortersyxyz"
    }
}

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
            text="iOS seçenekleri burada! 📱 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(IOS_MENU_KEYBOARD)
        )
    
    elif query.data == 'back_to_main':
        await query.edit_message_text(
            text="Hile almak için platformunu seç:",
            reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD)
        )
    
    elif query.data in HILE_DETAYLARI:
        hile_info = HILE_DETAYLARI[query.data]
        
        # Hangi menüden geldiğini belirleyip geri butonu ona göre ayarlanacak
        back_callback = 'back_to_android' if query.data in ['monster', 'andcheats', 'zolo', 'astor_cheat'] else 'back_to_ios'

        buy_button = [
            [InlineKeyboardButton("🛒 HEMEN SATIN AL", url=hile_info['link'])],
            [InlineKeyboardButton("⬅️ Geri", callback_data=back_callback)]
        ]
        
        await query.edit_message_text(
            text=f"{hile_info['name']}\n\n"
                 f"🌟 **Günlük:** {hile_info['gunluk']}\n"
                 f"🌟 **Haftalık:** {hile_info['haftalik']}\n"
                 f"🌟 **Aylık:** {hile_info['aylik']}",
            reply_markup=InlineKeyboardMarkup(buy_button),
            parse_mode='Markdown'
        )
    
    elif query.data == 'back_to_android':
         await query.edit_message_text(
            text="Android seçenekleri burada! 🤖 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(ANDROID_MENU_KEYBOARD)
        )

    elif query.data == 'back_to_ios':
        await query.edit_message_text(
            text="iOS seçenekleri burada! 📱 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(IOS_MENU_KEYBOARD)
        )

def main():
    """Botu başlatır ve çalıştırır."""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    print("Bot çalışmaya başladı! /start komutuyla test edebilirsiniz.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
