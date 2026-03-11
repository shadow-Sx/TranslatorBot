from PIL import ImageDraw


def group_into_blocks(data):
    """
    OCR natijasidagi so‘zlarni:
    1) qatorlarga ajratadi
    2) qatorlarni paragraf bloklarga birlashtiradi
    3) har bir blok uchun matn + koordinatalarni qaytaradi
    """

    words = []

    # OCR natijasini tozalash
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

    if not words:
        return []

    # 1) So‘zlarni Y bo‘yicha sort qilish
    words = sorted(words, key=lambda x: x["y"])

    # 2) Qatorlarga ajratish
    lines = []
    current_line = []
    line_threshold = 12  # y farqi shu qiymatdan kichik bo‘lsa — bir qatorda

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

    # 3) Har bir qatorni X bo‘yicha sort qilish
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

    # 5) Har bir blokni matn + koordinatalarga aylantirish
    final_blocks = []

    for block in blocks:
        block_text = " ".join([" ".join([w["text"] for w in line]) for line in block])

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


def draw_wrapped_text(draw: ImageDraw.Draw, text, font, x, y, max_width, line_spacing=1.2):
    """
    Tarjima qilingan matnni blok ichida wrap qilish:
    - matnni so‘zlarga bo‘lish
    - satrga sig‘masa yangi satr ochish
    - har bir satrni chizish
    """

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        w = font.getlength(test_line)

        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Har bir satrni chizish
    line_height = font.size * line_spacing

    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, fill="black", font=font)
