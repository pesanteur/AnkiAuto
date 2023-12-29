import fitz  # PyMuPDF
import os
import re
import sys

def process_caption(caption):
    # Remove unwanted line breaks within sentences
    caption = re.sub(r'\n(?!\n)', ' ', caption)
    # Replace multiple spaces with a single space
    caption = re.sub(r'\s+', ' ', caption)
    # Strip spaces at the beginning and end
    return caption.strip()

def extract_images_and_captions(pdf_path):
    doc = fitz.open(pdf_path)
    paper_name = os.path.splitext(os.path.basename(pdf_path))[0]
    folder_path = os.path.join(os.getcwd(), paper_name)
    os.makedirs(folder_path, exist_ok=True)
    captions_file = open(os.path.join(folder_path, "captions.txt"), "w")

    # Regular expression for matching captions
    caption_pattern = re.compile(r'Figure \d+\..*?(?=\n\n|\Z)', re.DOTALL)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        captions = [process_caption(caption) for caption in caption_pattern.findall(text)]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)  # pixmap from the image xref

            # Check if source pixmap's colorspace is valid
            if pix.colorspace:
                # Force into RGB if not already in RGB
                if pix.n < 5:  # this is GRAY or RGB
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                else:  # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)

                image_filename = f"{paper_name}_figure_{page_num}_{img_index}.png"
                pix1.save(os.path.join(folder_path, image_filename))  # Corrected method
                pix1 = None  # free Pixmap resources

            pix = None  # also free original Pixmap resources

            # Associate caption with the image
            if captions:
                caption = captions.pop(0) if img_index <= len(captions) else "Caption not found."
                captions_file.write(f"{image_filename}: {caption}\n")

    captions_file.close()
    doc.close()

# Check for command-line argument for the PDF path
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
    extract_images_and_captions(pdf_path)
else:
    print("No PDF file specified. Please provide a PDF file path as an argument.")


