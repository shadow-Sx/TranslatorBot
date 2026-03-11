import os
import zipfile

FONTS_DIR = "fonts"

def handle_font_update(zip_path):
    # 1) Papkani yaratib qo‘yamiz
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)

    extracted_fonts = []

    # 2) Zipni ochamiz
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            # faqat shrift fayllarini qabul qilamiz
            if file.endswith(".ttf") or file.endswith(".otf"):
                zip_ref.extract(file, FONTS_DIR)
                extracted_fonts.append(file)

    return extracted_fonts
