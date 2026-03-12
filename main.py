import telebot
import os

from processor.pdf_processor import process_pdf
from processor.fonts import handle_font_update

# Papkalarni yaratish
os.makedirs("temp", exist_ok=True)
os.makedirs("fonts", exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "PDF tarjima botiga xush kelibsiz!\nPDF yuboring.")

# /font_update
@bot.message_handler(commands=['font_update'])
def font_update(message):
    bot.reply_to(message, "Zip faylni yuboring (faqat .zip)")

# Fayl qabul qilish
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    doc = message.document

    # ZIP → shrift yuklash
    if doc.file_name.endswith(".zip"):
        file_path = f"temp/{doc.file_name}"

        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open(file_path, "wb") as f:
            f.write(downloaded)

        fonts = handle_font_update(file_path)

        if not fonts:
            bot.reply_to(message, "Zip ichida shrift topilmadi!")
        else:
            bot.reply_to(message, "Yangi shriftlar yuklandi:\n" + "\n".join(fonts))

        return

    # PDF → tarjima
    if doc.file_name.endswith(".pdf"):
        input_path = f"temp/{doc.file_name}"
        output_path = f"temp/output_{doc.file_name}"

        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open(input_path, "wb") as f:
            f.write(downloaded)

        bot.reply_to(message, "PDF qayta ishlanmoqda, kuting...")

        try:
            process_pdf(input_path, output_path)
        except Exception as e:
            bot.reply_to(message, f"Xatolik yuz berdi:\n{e}")
            return

        bot.send_document(message.chat.id, open(output_path, "rb"))
        return

    bot.reply_to(message, "Faqat PDF yoki ZIP yuboring.")
    

bot.infinity_polling(skip_pending=True)
