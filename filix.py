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
        'link': "https://t.me/wortersyxyz" # Örnek link, gerçek link ile değiştirilmeli
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
    'star_ios': {
        'name': "Star iOS",
        'gunluk': "285₺",
        'haftalik': "870₺",
        'aylik': "1200₺",
        'link': "https://t.me/wortersyxyz" # Bu linki de gerçek linkinle değiştir
    },
    'king_ios': {
        'name': "King iOS",
        'gunluk': "385₺",
        'haftalik': "950₺",
        'aylik': "1500₺",
        'link': "https://t.me/wortersyxyz" # Bu linki de gerçek linkinle değiştir
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
    
    # --- Menü Navigasyonu ---
    if query.data == 'android':
        # Android menüsünü gösterirken Geri butonu eklemeye gerek yok, çünkü ana menüye dönülüyor.
        # Eğer Android alt menüsü olursa oraya eklenir.
        # Şimdilik Android'i direkt hile listesine götürüyoruz.
        # Eğer Android için de bir alt menü istersek, burayı düzenleriz.
        
        # Android için hile listesi (Eğer android için de bir alt menü varsa burası değişir)
        android_cheats_keyboard = [
            [InlineKeyboardButton("🔥 Monster Cheat", callback_data='monster')],
            [InlineKeyboardButton("✨ And Cheats", callback_data='andcheats')],
            [InlineKeyboardButton("💎 Zolo Cheat", callback_data='zolo')],
            # [InlineKeyboardButton("🌟 STAR", callback_data='star')], # Eğer STAR Android'de de varsa
            [InlineKeyboardButton("⬅️ Geri", callback_data='back_to_main')] # Ana menüye geri
        ]
        await query.edit_message_text(
            text="Android seçenekleri burada! 🤖 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(android_cheats_keyboard)
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
    
    # --- Hile Detayları ve Satın Alma ---
    elif query.data in HILE_DETAYLARI: # 'monster', 'andcheats', 'zolo', 'star_ios', 'king_ios'
        hile_info = HILE_DETAYLARI[query.data]
        
        # Hangi menüden geldiğini belirleyip geri butonu ona göre ayarlanacak
        back_callback = 'back_to_android' if query.data in ['monster', 'andcheats', 'zolo'] else 'back_to_ios' # Eğer android'de star varsa burası da değişmeli

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
    
    # Eğer Android menüsünde, hile listesinden ana menüye dönülmüşse burası çalışır.
    # Bu özel bir durum, çünkü Android menüsünde de geri butonu var.
    elif query.data == 'back_to_android': # Burası sadece Android hilelerinden geri dönmek için
         await query.edit_message_text(
            text="Android seçenekleri burada! 🤖 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(ANDROID_MENU_KEYBOARD)
        )

    # IOS menüsünden Geri tuşuna basıldığında buraya düşer
    elif query.data == 'back_to_ios':
        await query.edit_message_text(
            text="iOS seçenekleri burada! 📱 Lütfen istediğin hileyi seç:",
            reply_markup=InlineKeyboardMarkup(IOS_MENU_KEYBOARD)
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
