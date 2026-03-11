import os
import zipfile
from PIL import ImageFont

FONTS_DIR = "fonts"


def handle_font_update(zip_path: str):
    """
    ZIP fayldan .ttf / .otf shriftlarni chiqarib, FONTS_DIR ichiga joylaydi.
    Qaytadi: topilgan shrift fayllari ro‘yxati.
    """
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)

    extracted_fonts = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            lower = file.lower()
            if lower.endswith(".ttf") or lower.endswith(".otf"):
                # ichki papkalar bo‘lsa ham, faqat fayl nomini olamiz
                filename = os.path.basename(file)
                if not filename:
                    continue

                target_path = os.path.join(FONTS_DIR, filename)

                with zip_ref.open(file) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())

                extracted_fonts.append(filename)

    return extracted_fonts


def _load_fonts():
    """FONTS_DIR ichidagi barcha shrift fayllarini ro‘yxat qilib qaytaradi."""
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)

    fonts = []
    for f in os.listdir(FONTS_DIR):
        lower = f.lower()
        if lower.endswith(".ttf") or lower.endswith(".otf"):
            fonts.append(os.path.join(FONTS_DIR, f))

    return fonts


def pick_best_font(text: str, block_width: int, block_height: int):
    """
    Berilgan blok o‘lchamiga (width, height) eng mos shriftni tanlaydi.
    - FONTS_DIR ichidagi shriftlar orasidan tanlaydi
    - Matn zichligi bo‘yicha eng yaqinini oladi
    """
    fonts = _load_fonts()

    # Agar shrift bo‘lmasa — fallback
    if not fonts:
        size = max(10, int(block_height * 0.8))
        return ImageFont.truetype("arial.ttf", size)  # yoki sen tanlagan default

    best_font = None
    best_score = float("inf")

    # Matn bo‘sh bo‘lsa, oddiy shrift qaytaramiz
    if not text.strip():
        size = max(10, int(block_height * 0.8))
        return ImageFont.truetype(fonts[0], size)

    for font_path in fonts:
        # Blok balandligiga mos taxminiy size
        size = max(10, int(block_height * 0.8))

        try:
            font = ImageFont.truetype(font_path, size)
        except Exception:
            continue

        try:
            text_width = font.getlength(text)
        except Exception:
            continue

        # Zichlik: kenglik / belgilar soni
        if len(text) == 0:
            continue

        density = text_width / len(text)
        ocr_density = block_width / len(text)

        score = abs(density - ocr_density)

        if score < best_score:
            best_score = score
            best_font = font

    # Agar hech biri ishlamasa — fallback
    if best_font is None:
        size = max(10, int(block_height * 0.8))
        best_font = ImageFont.truetype(fonts[0], size)

    return best_font
