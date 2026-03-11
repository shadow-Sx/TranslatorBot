from PIL import ImageFont
import os

def pick_best_font(block_text, block_width, block_height, fonts_folder="fonts"):
    fonts = [f for f in os.listdir(fonts_folder) if f.endswith(".ttf") or f.endswith(".otf")]

    if not fonts:
        return ImageFont.truetype("fonts/Roboto-Regular.ttf", int(block_height * 0.8))

    best_font = None
    best_score = float("inf")

    for font_file in fonts:
        font_path = os.path.join(fonts_folder, font_file)

        # Shrift o‘lchamini taxminan blok balandligiga moslaymiz
        size = max(10, int(block_height * 0.8))
        font = ImageFont.truetype(font_path, size)

        # Matn kengligini o‘lchaymiz
        try:
            text_width = font.getlength(block_text)
        except:
            continue

        # Zichlik
        if len(block_text) == 0:
            continue

        density = text_width / len(block_text)
        ocr_density = block_width / len(block_text)

        score = abs(density - ocr_density)

        if score < best_score:
            best_score = score
            best_font = font

    return best_font
