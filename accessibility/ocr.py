
import io
import os

from PIL import Image, ImageOps
import pytesseract


# --------------------------------------------------
# TESSERACT CONFIGURATION
# --------------------------------------------------

# Update this path if Tesseract is installed elsewhere.
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.isfile(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

SUPPORTED_IMAGE_FORMATS = (".png", ".jpg", ".jpeg")
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS + (".pdf",)

OCR_ERROR_PREFIX = "OCR Error:"
FILE_ERROR_PREFIX = "Error processing file:"
UNSUPPORTED_FORMAT_PREFIX = "Unsupported file format"


# --------------------------------------------------
# IMAGE OCR
# --------------------------------------------------

def extract_text_from_image(image):
    """
    Extract text from a PIL Image using Tesseract OCR.

    Args:
        image: A PIL Image object.

    Returns:
        Extracted text, or an error message if OCR fails.
    """
    if image is None:
        return f"{OCR_ERROR_PREFIX} No image was provided."

    try:
        # Correct the image orientation when EXIF metadata is available.
        image = ImageOps.exif_transpose(image)

        # Convert to RGB to handle images with alpha or unusual modes.
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image)
        return text.strip()

    except pytesseract.TesseractNotFoundError:
        return (
            f"{OCR_ERROR_PREFIX} Tesseract was not found. "
            "Install Tesseract OCR and configure TESSERACT_PATH."
        )

    except Exception as error:
        return f"{OCR_ERROR_PREFIX} {error}"


# --------------------------------------------------
# PDF OCR
# --------------------------------------------------

def _extract_text_from_pdf(file_bytes):
    """
    Extract text from selectable-text PDFs and scanned PDF pages.

    Pages with selectable text use normal PDF extraction.
    Pages without selectable text are rendered and processed with OCR.
    """
    try:
        import fitz
    except ImportError:
        return (
            f"{FILE_ERROR_PREFIX} PDF support requires PyMuPDF. "
            "Install it using: pip install PyMuPDF"
        )

    all_text = []

    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as document:

            if document.needs_pass:
                return (
                    f"{FILE_ERROR_PREFIX} This PDF is password-protected. "
                    "Please upload an accessible, unlocked PDF."
                )

            for page_number, page in enumerate(document, start=1):

                # First, extract selectable text.
                page_text = page.get_text("text").strip()

                if page_text:
                    all_text.append(page_text)
                    continue

                # If no selectable text exists, treat the page as scanned.
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                image_bytes = pixmap.tobytes("png")

                with Image.open(io.BytesIO(image_bytes)) as image:
                    ocr_text = extract_text_from_image(image)

                if ocr_text.startswith(OCR_ERROR_PREFIX):
                    return (
                        f"{OCR_ERROR_PREFIX} OCR failed on PDF page "
                        f"{page_number}. {ocr_text}"
                    )

                if ocr_text.strip():
                    all_text.append(ocr_text.strip())

        if not all_text:
            return (
                f"{OCR_ERROR_PREFIX} No readable text could be "
                "extracted from the PDF."
            )

        return "\n\n".join(all_text).strip()

    except Exception as error:
        return f"{FILE_ERROR_PREFIX} Unable to read PDF: {error}"


# --------------------------------------------------
# FILE OCR
# --------------------------------------------------

def extract_text(file):
    """
    Extract text from an uploaded image or PDF.

    Supported formats:
        PNG, JPG, JPEG, PDF

    Args:
        file: A Streamlit UploadedFile or a compatible file object.

    Returns:
        Extracted text or a readable error message.
    """
    if file is None:
        return f"{FILE_ERROR_PREFIX} No file was provided."

    try:
        file_name = getattr(file, "name", "")
        file_name = os.path.basename(str(file_name)).lower()

        if not file_name.endswith(SUPPORTED_FORMATS):
            return (
                f"{UNSUPPORTED_FORMAT_PREFIX} Please upload "
                "a PNG, JPG, JPEG, or PDF."
            )

        # Read the uploaded bytes once. This also avoids depending on
        # the current read position of the uploaded file.
        file_bytes = file.getvalue() if hasattr(file, "getvalue") else file.read()

        if not file_bytes:
            return f"{FILE_ERROR_PREFIX} The uploaded file is empty."

        # ------------------------------------------
        # IMAGE FILE
        # ------------------------------------------

        if file_name.endswith(SUPPORTED_IMAGE_FORMATS):
            try:
                with Image.open(io.BytesIO(file_bytes)) as image:
                    image.load()
                    return extract_text_from_image(image)

            except Exception as error:
                return (
                    f"{FILE_ERROR_PREFIX} Unable to open image: {error}"
                )

        # ------------------------------------------
        # PDF FILE
        # ------------------------------------------

        if file_name.endswith(".pdf"):
            return _extract_text_from_pdf(file_bytes)

    except Exception as error:
        return f"{FILE_ERROR_PREFIX} {error}"

    return (
        f"{UNSUPPORTED_FORMAT_PREFIX} Please upload "
        "a PNG, JPG, JPEG, or PDF."
    )


# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

def clean_ocr_text(text):
    """
    Remove unnecessary blank lines and surrounding whitespace
    from OCR output while preserving error messages.
    """
    if not text:
        return ""

    error_prefixes = (
        OCR_ERROR_PREFIX,
        FILE_ERROR_PREFIX,
        UNSUPPORTED_FORMAT_PREFIX,
    )

    if text.startswith(error_prefixes):
        return text

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)
