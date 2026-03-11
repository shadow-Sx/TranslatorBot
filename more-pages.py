import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import LibreTranslator

translator = LibreTranslator(source="auto", target="uz")

def translate_text(text):
    try:
        return translator.translate(text)
    except:
        return text  # xatolik bo‘lsa original matnni qaytaradi

def process_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    output_pages = []

    for page_index in range(len(doc)):
        print(f"{page_index+1}-sahifa qayta ishlanmoqda...")

        # 1) Sahifani rasmga aylantirish
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=300)
        img_path = f"page_{page_index}.png"
        pix.save(img_path)

        # 2) OCR
        img = Image.open(img_path)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 20)

        # 3) Remove + tarjima + qayta yozish
        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            if word == "":
                continue

            x, y = data['left'][i], data['top'][i]
            w, h = data['width'][i], data['height'][i]

            # REMOVE: eski matnni o‘chirish
            draw.rectangle((x, y, x + w, y + h), fill="white")

            # Tarjima
            translated = translate_text(word)

            # Qayta yozish
            draw.text((x, y), translated, fill="black", font=font)

        # 4) Sahifani PDFga aylantirish
        page_pdf_path = f"page_{page_index}.pdf"
        img.convert("RGB").save(page_pdf_path, "PDF", resolution=300.0)
        output_pages.append(page_pdf_path)

    # 5) Barcha sahifalarni bitta PDFga yig‘ish
    final_doc = fitz.open()
    for p in output_pages:
        final_doc.insert_pdf(fitz.open(p))

    final_doc.save(output_pdf)
    final_doc.close()

    print("Tayyor:", output_pdf)


# Ishga tushirish
process_pdf("input.pdf", "output.pdf")
