import os
import uuid
from PIL import Image
import numpy as np
import cv2


TEMP_DIR = "temp"
FONTS_DIR = "fonts"


def ensure_dirs():
    """Kerakli papkalarni avtomatik yaratish."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)


def random_filename(ext="png"):
    """Kolliziyasiz tasodifiy fayl nomi yaratish."""
    return f"{uuid.uuid4().hex}.{ext}"


def save_image_as_pdf(pil_img: Image.Image, output_path: str):
    """PIL rasmni PDF formatida saqlash."""
    pil_img.convert("RGB").save(output_path, "PDF", resolution=300.0)


def pil_to_cv2(pil_img: Image.Image):
    """PIL → CV2 formatiga o‘tkazish."""
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv_img):
    """CV2 → PIL formatiga o‘tkazish."""
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


def load_image(path: str):
    """Rasmni xavfsiz ochish."""
    try:
        return Image.open(path)
    except Exception:
        return None


def clean_temp():
    """temp/ papkasini tozalash."""
    if not os.path.exists(TEMP_DIR):
        return

    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except:
            pass
