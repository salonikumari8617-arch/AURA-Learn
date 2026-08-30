import os
import io

from PIL import Image
import pytesseract


# --------------------------------------------------
# TESSERACT CONFIGURATION
# --------------------------------------------------

TESSERACT_PATH=r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd=TESSERACT_PATH


# --------------------------------------------------
# IMAGE OCR
# --------------------------------------------------

def extract_text_from_image(image):
    """
    Extract text from a PIL Image using Tesseract OCR.
    """

    try:
        text=pytesseract.image_to_string(image)
        return text.strip()

    except Exception as e:
        return f"OCR Error: {str(e)}"


# --------------------------------------------------
# FILE OCR
# --------------------------------------------------

def extract_text(file):
    """
    Extract text from an uploaded image or PDF.

    Supported formats:
    PNG, JPG, JPEG, PDF
    """

    try:
        file_name=file.name.lower()

        # ------------------------------------------
        # IMAGE FILE
        # ------------------------------------------

        if file_name.endswith((".png",".jpg",".jpeg")):

            image=Image.open(file)

            return extract_text_from_image(
                image
            )

        # ------------------------------------------
        # PDF FILE
        # ------------------------------------------

        elif file_name.endswith(".pdf"):

            import fitz

            pdf_bytes=file.read()

            document=fitz.open(
                stream=pdf_bytes,
                filetype="pdf"
            )

            all_text=[]

            for page in document:

                # First try normal PDF text extraction
                text=page.get_text().strip()

                if text:

                    all_text.append(
                        text
                    )

                else:

                    # Scanned PDF -> OCR
                    pix=page.get_pixmap(
                        matrix=fitz.Matrix(
                            2,
                            2
                        )
                    )

                    image_bytes=pix.tobytes(
                        "png"
                    )

                    image=Image.open(
                        io.BytesIO(
                            image_bytes
                        )
                    )

                    ocr_text=extract_text_from_image(
                        image
                    )

                    if (
                        ocr_text
                        and
                        not ocr_text.startswith(
                            "OCR Error:"
                        )
                    ):

                        all_text.append(
                            ocr_text
                        )

            document.close()

            if not all_text:

                return (
                    "OCR Error: No readable text "
                    "could be extracted from the PDF."
                )

            return "\n\n".join(
                all_text
            ).strip()

        # ------------------------------------------
        # UNSUPPORTED FORMAT
        # ------------------------------------------

        else:

            return (
                "Unsupported file format. "
                "Please upload a PNG, JPG, JPEG, or PDF."
            )

    except Exception as e:

        return f"Error processing file: {str(e)}"


# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

def clean_ocr_text(text):
    """
    Remove unnecessary blank lines from OCR output.
    """

    if not text:
        return ""

    # Preserve error messages
    if (
        text.startswith("OCR Error:")
        or
        text.startswith("Error processing file:")
        or
        text.startswith("Unsupported file format")
    ):
        return text

    lines=[]

    for line in text.splitlines():

        line=line.strip()

        if line:
            lines.append(
                line
            )

    return "\n".join(
        lines
    )