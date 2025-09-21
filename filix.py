import telegram
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import asyncio

# --- API Anahtarlarınızı Buraya Girin ---
TOKEN = "8448966224:AAH3CwxDRNkHmtrC1gvyCUcTi9Ibd0vave0"
GEMINI_API_KEY = "AIzaSyAAfSX-4rNJcluag6iWvI4GE_a1dE8f0PI"
VIP_KEY = "Rushexvip11"
# --------------------------------------

# Gemini API'yi yapılandırın
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Model adını 'gemini-pro-vision' olarak değiştiriyoruz
    model = genai.GenerativeModel('gemini-pro-vision')
except Exception as e:
    print(f"Gemini API yapılandırması başarısız: {e}")
    exit()

# Kullanıcı verilerini depolamak için sözlük
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data[user.id] = {"guest_count": 0, "is_vip": False}
    
    keyboard = [[KeyboardButton("Misafir"), KeyboardButton("VIP")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Merhaba {user.first_name}! Denemek için key girin.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text
    
    # VIP ve Misafir butonlarının yönetimi
    if text == "VIP":
        await update.message.reply_text("Lütfen VIP anahtarınızı girin.")
        return
        
    if text == VIP_KEY:
        if user.id in user_data:
            user_data[user.id]["is_vip"] = True
            await update.message.reply_text("VIP erişiminiz onaylandı. Artık sınırsız kod gönderebilirsiniz.")
        return

    if text == "Misafir":
        await update.message.reply_text("Misafir olarak devam ediyorsunuz. Lütfen kodunuzu gönderin. Sadece 5 deneme hakkınız var.", reply_markup=ReplyKeyboardRemove())
        return
        
    # Kod analizi ve Gemini entegrasyonu
    if user.id in user_data:
        current_user = user_data[user.id]

        if not current_user["is_vip"]:
            if current_user["guest_count"] >= 5:
                await update.message.reply_text("Limitiniz doldu. Misafir olarak 5 deneme hakkınızı doldurdunuz.")
                return
            current_user["guest_count"] += 1
            
        await update.message.reply_text("Kodunuz Gemini ile analiz ediliyor...")
        
        prompt = f"""
        Aşağıdaki Python kodunu analiz et. Kodda bir hata varsa, hatayı açıkla ve hatanın nedenini belirt. Ayrıca, kodun hatasız, düzeltilmiş halini sun. Eğer kodda hata yoksa, kodun ne işe yaradığını kısaca açıkla. Cevaplarını Türkçe olarak ver.
        
        ```python
        {text}
        ```
        """
        
        try:
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            if response and response.text:
                await update.message.reply_text(response.text)
            else:
                await update.message.reply_text("Üzgünüm, kodunuzu analiz edemedim. Lütfen daha sonra tekrar deneyin.")
                
        except Exception as e:
            await update.message.reply_text(f"Gemini ile iletişimde bir sorun oluştu: {e}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
