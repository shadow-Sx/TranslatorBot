@dp.message_handler(commands=['font_update'])
async def font_update_handler(message: types.Message):
    await message.reply("Zip faylni yuboring (faqat .zip)")

@dp.message_handler(content_types=['document'])
async def font_zip_received(message: types.Message):
    doc = message.document

    if not doc.file_name.endswith(".zip"):
        return await message.reply("Faqat .zip fayl yuboring!")

    file_path = f"temp/{doc.file_name}"
    await doc.download(file_path)

    fonts = handle_font_update(file_path)

    if not fonts:
        return await message.reply("Zip ichida shrift topilmadi!")

    msg = "Yangi shriftlar yuklandi:\n" + "\n".join(fonts)
    await message.reply(msg)
