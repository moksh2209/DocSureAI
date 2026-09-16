import logging
from pathlib import Path

# Suppress verbose torch/easyocr logs
logging.getLogger("easyocr").setLevel(logging.ERROR)

def initialize_ocr_engine(languages: list = ['en']):
    """
    Initialize the EasyOCR reader.
    Returns the reader object or None on failure.
    """
    try:
        import easyocr
        print(f"Initializing EasyOCR (languages: {languages})...")
        # gpu=False ensures CPU-only mode for maximum compatibility
        reader = easyocr.Reader(languages, gpu=False, verbose=False)
        print("EasyOCR engine initialized successfully.")
        return reader
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        return None

def perform_ocr(ocr_engine, image_path: str | Path) -> dict | None:
    """
    Run OCR on a single image file.
    Returns a structured dict with extracted text, confidence, and detections.
    """
    try:
        img_path = Path(image_path)
        if not img_path.exists():
            print(f"Error: Image file does not exist: {img_path}")
            return None

        # EasyOCR returns a list of (bbox, text, confidence) tuples
        raw_results = ocr_engine.readtext(str(img_path), detail=1)

        if not raw_results:
            print(f"  No text detected in {img_path.name}")
            return {
                "image_name": img_path.name,
                "extracted_text": "",
                "average_confidence": 0.0,
                "detections": []
            }

        text_lines = []
        confidences = []
        detections = []

        for (bbox, text, conf) in raw_results:
            text_lines.append(text)
            confidences.append(float(conf))
            detections.append({
                "box": [list(pt) for pt in bbox],
                "text": text,
                "confidence": float(conf)
            })

        avg_confidence = (sum(confidences) / len(confidences)) * 100.0

        return {
            "image_name": img_path.name,
            "extracted_text": "\n".join(text_lines),
            "average_confidence": avg_confidence,
            "detections": detections
        }

    except Exception as e:
        print(f"  OCR processing failed for {image_path}: {e}")
        return None
