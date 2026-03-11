from PIL import Image
import cv2
import numpy as np
import pytesseract


# Tesseract konfiguratsiyasi
TESS_LANGS = "eng+rus+de+fr+es+it+tr"  # xohlagancha kengaytirishing mumkin
TESS_CONFIG = r"--oem 3 --psm 6"       # LSTM + block of text


def deskew(pil_img: Image.Image) -> Image.Image:
    """Rasmni avtomatik tekislash (deskew)"""
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)
    coords = np.column_stack(np.where(img < 255))

    if coords.size == 0:
        return pil_img

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return Image.fromarray(rotated)


def preprocess_image(pil_img: Image.Image) -> Image.Image:
    """OCR uchun rasmni tayyorlash: gray, contrast, blur, threshold, deskew"""
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)

    # Kontrastni oshirish
    img = cv2.equalizeHist(img)

    # Shovqinni kamaytirish
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # Threshold (Otsu)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    pil = Image.fromarray(img)

    # Istesang deskew’ni yoqib qo‘yasan:
    pil = deskew(pil)

    return pil


def ocr_extract(pil_img: Image.Image):
    """
    Rasmni OCR qilish:
    - preprocessing
    - Tesseract image_to_data
    - koordinatalar bilan dict qaytaradi
    """
    pre = preprocess_image(pil_img)

    data = pytesseract.image_to_data(
        pre,
        lang=TESS_LANGS,
        config=TESS_CONFIG,
        output_type=pytesseract.Output.DICT
    )

    return data
