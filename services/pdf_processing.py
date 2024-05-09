from PyPDF2 import PdfReader
import os
import io
from app.config import Config
import base64


IMAGE_SIZE_LIMIT = Config.IMAGE_SIZE_LIMIT  # 20 MB in bytes
def extract_images_and_text_from_pdf(pdf_path):
    """Extract images from a given PDF file and return them as a list of base64-encoded data URLs."""
    pdf = PdfReader(pdf_path)
    images_data_urls = []
    data_pages = []

    for page_number, page in enumerate(pdf.pages, start=1):


        for image in page.images:
            with open("/tmp/"+image.name, "wb") as fp:
                fp.write(image.data)
                file_path = "/tmp/"+image.name
                file_size = os.path.getsize(file_path)

                # Check if the file size is greater than 20 MB
                if file_size > IMAGE_SIZE_LIMIT:
                    print(f"Skipping this image, image in the pdf with page number {page_number} is larger than 20 MB.")
                    continue

                with open(file_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode("utf-8")
                    data_url = f"data:image/jpeg;base64,{encoded_image}"
                    images_data_urls.append(data_url)
                    data_pages.append(page_number)
                    os.remove(file_path)

    return images_data_urls,data_pages


