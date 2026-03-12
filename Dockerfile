FROM python:3.10-slim

# Tesseract o‘rnatish
RUN apt-get update && apt-get install -y tesseract-ocr

# Ishchi papka
WORKDIR /app

# Fayllarni konteynerga ko‘chirish
COPY . .

# Python kutubxonalarini o‘rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Papkalarni yaratish
RUN mkdir -p temp fonts

# Botni ishga tushirish
CMD ["python", "main.py"]
