import fitz
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import LibreTranslator

translator = LibreTranslator(source="auto", target="uz")

def translate_block(text):
    try:
        return translator.translate(text)
    except:
        return text

# --- BLOKLASH ALGORITMI ---
def group_into_blocks(data):
    words = []

    # OCR natijasini tozalab olamiz
    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if word == "":
            continue

        x = data['left'][i]
        y = data['top'][i]
        w = data['width'][i]
        h = data['height'][i]

        words.append({
            "text": word,
            "x": x,
            "y": y,
            "w": w,
            "h": h
        })

    # 1) So‘zlarni Y bo‘yicha sort qilamiz
    words = sorted(words, key=lambda x: x["y"])

    lines = []
    current_line = []
    line_threshold = 12  # y farqi shu qiymatdan kichik bo‘lsa — bir qatorda

    # 2) Qatorlarga ajratish
    for w in words:
        if not current_line:
            current_line.append(w)
            continue

        if abs(w["y"] - current_line[-1]["y"]) < line_threshold:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]

    if current_line:
        lines.append(current_line)

    # 3) Har bir qatorni X bo‘yicha sort qilamiz
    for line in lines:
        line.sort(key=lambda x: x["x"])

    # 4) Qatorlarni paragraf bloklarga birlashtirish
    blocks = []
    current_block = []
    block_threshold = 25  # qatorlar orasidagi masofa

    for line in lines:
        if not current_block:
            current_block.append(line)
            continue

        prev_line = current_block[-1]
        if abs(line[0]["y"] - prev_line[0]["y"]) < block_threshold:
            current_block.append(line)
        else:
            blocks.append(current_block)
            current_block = [line]

    if current_block:
        blocks.append(current_block)

    # 5) Har bir blokni matnga aylantiramiz
    final_blocks = []
    for block in blocks:
        block_text = " ".join([" ".join([w["text"] for w in line]) for line in block])

        # Blok koordinatalari
        min_x = min(w["x"] for line in block for w in line)
        min_y = min(w["y"] for line in block for w in line)
        max_x = max(w["x"] + w["w"] for line in block for w in line)
        max_y = max(w["y"] + w["h"] for line in block for w in line)

        final_blocks.append({
            "text": block_text,
            "x0": min_x,
            "y0": min_y,
            "x1": max_x,
            "y1": max_y
        })

    return final_blocks


# --- ASOSIY PDF PROCESSOR ---
def process_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    output_pages = []

    for page_index in range(len(doc)):
        print(f"{page_index+1}-sahifa...")

        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=300)
        img_path = f"page_{page_index}.png"
        pix.save(img_path)

        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 22)

        # OCR
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        # BLOKLASH
        blocks = group_into_blocks(data)

        # HAR BIR BLOKNI QAYTA ISHLASH
        for block in blocks:
            x0, y0, x1, y1 = block["x0"], block["y0"], block["x1"], block["y1"]

            # REMOVE
            draw.rectangle((x0, y0, x1, y1), fill="white")

            # TARJIMA
            translated = translate_block(block["text"])

            # QAYTA YOZISH
            draw.text((x0, y0), translated, fill="black", font=font)

        # PDFGA AYLANISH
        page_pdf_path = f"page_{page_index}.pdf"
        img.convert("RGB").save(page_pdf_path, "PDF", resolution=300.0)
        output_pages.append(page_pdf_path)

    # YIG‘ISH
    final_doc = fitz.open()
    for p in output_pages:
        final_doc.insert_pdf(fitz.open(p))

    final_doc.save(output_pdf)
    final_doc.close()

    print("Tayyor:", output_pdf)


# ISHGA TUSHIRISH
process_pdf("input.pdf", "output.pdf")
