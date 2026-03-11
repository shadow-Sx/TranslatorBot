import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import LibreTranslator

# 1) PDF sahifani rasmga aylantirish
def pdf_to_image(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # faqat 1-sahifa
    pix = page.get_pixmap(dpi=300)
    img_path = "page.png"
    pix.save(img_path)
    return img_path

# 2) OCR orqali matn + koordinatalar olish
def ocr_extract(image_path):
    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    return data, img

# 3) Matnni tarjima qilish (auto → uz)
def translate_text(text):
    translator = LibreTranslator(source="auto", target="uz")
    return translator.translate(text)

# 4) Eski matnni o‘chirish (remove)
def remove_text(img, data):
    draw = ImageDraw.Draw(img)

    for i in range(len(data['text'])):
        word = data['text'][i]
        if word.strip() == "":
            continue

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

        # Matn joyini oq rang bilan tozalaymiz
        draw.rectangle((x, y, x + w, y + h), fill="white")

    return img

# 5) Tarjima qilingan matnni qayta yozish
def write_translated(img, data):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 20)  # vaqtincha default shrift

    for i in range(len(data['text'])):
        word = data['text'][i]
        if word.strip() == "":
            continue

        translated = translate_text(word)

        x, y = data['left'][i], data['top'][i]
        draw.text((x, y), translated, fill="black", font=font)

    return img

# 6) Rasmni PDFga aylantirish
def image_to_pdf(img, output_pdf):
    img.convert("RGB").save(output_pdf, "PDF", resolution=300.0)

# --- MAIN ---
pdf_path = "input.pdf"

# 1) PDF → rasm
img_path = pdf_to_image(pdf_path)

# 2) OCR
data, img = ocr_extract(img_path)

# 3) Remove
clean_img = remove_text(img, data)

# 4) Tarjima + qayta yozish
final_img = write_translated(clean_img, data)

# 5) PDFga aylantirish
image_to_pdf(final_img, "output.pdf")

print("Tayyor: output.pdf")
