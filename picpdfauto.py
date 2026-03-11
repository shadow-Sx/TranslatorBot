def process_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    output_pages = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)

        if is_image_pdf(page):
            print(f"{page_index+1}-sahifa: Rasmli PDF (OCR rejimi)")
            processed_page = process_image_page(page, page_index)
        else:
            print(f"{page_index+1}-sahifa: Matnli PDF (text-based rejim)")
            processed_page = process_text_page(page, page_index)

        output_pages.append(processed_page)

    # Yig‘ish
    final_doc = fitz.open()
    for p in output_pages:
        final_doc.insert_pdf(fitz.open(p))

    final_doc.save(output_pdf)
    final_doc.close()
