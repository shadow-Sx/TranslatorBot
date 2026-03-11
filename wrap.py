def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing=1.2):
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
