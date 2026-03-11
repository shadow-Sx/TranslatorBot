import fitz
from PIL import Image
import os

from .ocr import ocr_extract
from .blocks import group_into_blocks, draw_wrapped_text
from .fonts import pick_best_font
from .utils import save_image_as_pdf, preprocess_image


def is_image_pdf(page):
    """Matnli yoki rasmli PDF ekanini aniqlash"""
    text = page.get_text().strip()
    return text == ""


def process_text_page(page, page_index):
    """Matnli PDF sahifani qayta ishlash (OCR kerak emas)"""
    # Sahifani rasmga aylantiramiz
    pix = page.get_pixmap(dpi=300)
    img_path = f"temp/page_{page_index}.png"
    pix.save(img_path)

    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # Matn bloklarini PyMuPDF orqali olish
    blocks = page.get_text("blocks")

    for block in blocks:
        x0, y0, x1, y1, text, *_ = block

        if not text.strip():
            continue

        # Tarjima
        translated = translate_block(text)

        # Shrift tanlash
        font = pick_best_font(
            translated,
            x1 - x0,
            y1 - y0
        )

        # Remove
        draw.rectangle((x0, y0, x1, y1), fill="white")

        # Wrap bilan qayta yozish
        draw_wrapped_text(draw, translated, font, x0, y0, x1 - x0)

    # PDFga aylantirish
    output_pdf = f"temp/page_{page_index}.pdf"
    save_image_as_pdf(img, output_pdf)
    return output_pdf


def process_image_page(page, page_index):
    """Rasmli PDF sahifani qayta ishlash (OCR rejimi)"""
    pix = page.get_pixmap(dpi=600)
    img_path = f"temp/page_{page_index}.png"
    pix.save(img_path)

    # Preprocessing (OCR aniqligini oshirish)
    img = Image.open(img_path)
    img = preprocess_image(img)

    # OCR
    data = ocr_extract(img)

    # Bloklash
    blocks = group_into_blocks(data)

    draw = ImageDraw.Draw(img)

    # Har bir blokni qayta ishlash
    for block in blocks:
        x0, y0, x1, y1 = block["x0"], block["y0"], block["x1"], block["y1"]

        # Tarjima
        translated = translate_block(block["text"])

        # Shrift tanlash
        font = pick_best_font(
            translated,
            x1 - x0,
            y1 - y0
        )

        # Remove
        draw.rectangle((x0, y0, x1, y1), fill="white")

        # Wrap bilan qayta yozish
        draw_wrapped_text(draw, translated, font, x0, y0, x1 - x0)

    # PDFga aylantirish
    output_pdf = f"temp/page_{page_index}.pdf"
    save_image_as_pdf(img, output_pdf)
    return output_pdf


def process_pdf(input_pdf, output_pdf):
    """Asosiy PDF qayta ishlash funksiyasi"""
    doc = fitz.open(input_pdf)
    output_pages = []

    for i in range(len(doc)):
        page = doc.load_page(i)

        if is_image_pdf(page):
            print(f"{i+1}-sahifa: Rasmli PDF (OCR rejimi)")
            processed_page = process_image_page(page, i)
        else:
            print(f"{i+1}-sahifa: Matnli PDF (text-based rejim)")
            processed_page = process_text_page(page, i)

        output_pages.append(processed_page)

    # Barcha sahifalarni bitta PDFga yig‘ish
    final_doc = fitz.open()
    for p in output_pages:
        final_doc.insert_pdf(fitz.open(p))

    final_doc.save(output_pdf)
    final_doc.close()
