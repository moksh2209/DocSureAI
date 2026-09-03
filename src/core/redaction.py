import json
import re
import logging
from pathlib import Path
import cv2
import numpy as np
from core.ocr_engine import perform_ocr

logger = logging.getLogger(__name__)

# Patterns for sensitive data detection
PATTERNS = {
    # Standard email format
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    
    # OCR-tolerant email: allows one space before @, missing dot before TLD, or space instead of dot
    # e.g., "rahul sharma@example com" or "rahul sharma@examplecom"
    "EMAIL_OCR": re.compile(r"\b[A-Za-z0-9._%+-]+(?: [A-Za-z0-9._%+-]+)?@[A-Za-z0-9.-]+(?: |\.)?(?:com|org|net|in|co|edu|gov)\b", re.IGNORECASE),
    
    # Phone: optionally starts with +91, followed by 10 digits that may have a space/hyphen/dot in middle
    "PHONE": re.compile(r"(?:\+91[-\s.]?)?\b\d{5}[-\s.]?\d{5}\b"),
    
    # URL: starts with http, https or www.
    "URL": re.compile(r"\b(?:https?://|www\.)[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)"),
    
    # Card-like: 13-19 digits, can have spaces/hyphens
    "CARD_LIKE": re.compile(r"\b(?:\d[-\s]?){13,19}\b"),
    
    # Aadhaar-like: exactly 12 digits, can have spaces/hyphens
    "AADHAAR_LIKE": re.compile(r"\b(?:\d[-\s]?){12}\b")
}

def load_best_candidate(output_dir: Path) -> str | None:
    """Reads the best candidate image name from ocr_analysis.json."""
    analysis_path = output_dir / "ocr_analysis.json"
    if not analysis_path.exists():
        logger.error(f"Missing {analysis_path}")
        return None
        
    try:
        with open(analysis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("best_candidate", {}).get("image_name")
    except Exception as e:
        logger.error(f"Error reading ocr_analysis.json: {e}")
        return None

def detect_sensitive_type(text: str) -> list[tuple[str, str, str]]:
    """
    Checks text against sensitive data patterns.
    Returns a list of tuples: (pattern_type, matched_text, description)
    """
    detected = []
    
    # Track spans of CARD_LIKE to prevent AADHAAR_LIKE overlap
    card_spans = []
    
    # 1. Detect CARD_LIKE first
    for match in PATTERNS["CARD_LIKE"].finditer(text):
        m_text = match.group()
        clean = re.sub(r"[-\s]", "", m_text)
        if 13 <= len(clean) <= 19:
            card_spans.append(match.span())
            detected.append(("CARD_LIKE", m_text, "Card-like numeric pattern"))
            
    # 2. Detect AADHAAR_LIKE
    for match in PATTERNS["AADHAAR_LIKE"].finditer(text):
        m_text = match.group()
        span = match.span()
        clean = re.sub(r"[-\s]", "", m_text)
        if len(clean) == 12:
            # Reject if it overlaps with any CARD_LIKE span
            is_contained = any(c_start <= span[0] and span[1] <= c_end for c_start, c_end in card_spans)
            if not is_contained:
                detected.append(("AADHAAR_LIKE", m_text, "Aadhaar-like numeric pattern"))

    # 3. Detect others
    for p_type in ["EMAIL", "EMAIL_OCR", "PHONE", "URL"]:
        for match in PATTERNS[p_type].finditer(text):
            m_text = match.group()
            
            # Avoid duplicate email detections if both EMAIL and EMAIL_OCR match
            if p_type == "EMAIL_OCR":
                # Check if it was already caught by standard EMAIL
                if any(d[0] == "EMAIL" and d[1] in m_text for d in detected):
                    continue
                detected.append(("EMAIL", m_text, "Email address pattern detected (OCR normalized)"))
            elif p_type == "EMAIL":
                detected.append(("EMAIL", m_text, "Email address pattern detected"))
            elif p_type == "PHONE":
                detected.append(("PHONE", m_text, "Phone pattern detected"))
            elif p_type == "URL":
                detected.append(("URL", m_text, "URL pattern detected"))
            
    return detected

def extract_sensitive_regions(ocr_results: dict) -> list[dict]:
    """
    Extracts sensitive items from OCR detections.
    """
    sensitive_items = []
    detections = ocr_results.get("detections", [])
    
    for det in detections:
        text = det.get("text", "")
        confidence = det.get("confidence", 0.0)
        box = det.get("box", [])
        
        matches = detect_sensitive_type(text)
        for p_type, matched_text, desc in matches:
            sensitive_items.append({
                "type": p_type,
                "description": desc,
                "text": text,  # preserving original OCR text
                "matched_substring": matched_text,
                "confidence": round(confidence * 100, 2) if confidence <= 1.0 else confidence,
                "bounding_box": [
                    [int(coord) for coord in point]
                    for point in box
                ]
            })
            
    return sensitive_items

def generate_sensitive_data_report(source_image: str, regions: list[dict]) -> dict:
    """Generates the structured report dict."""
    return {
        "source_image": source_image,
        "total_sensitive_items": len(regions),
        "items": regions
    }

def save_sensitive_data_report(report: dict, output_dir: Path) -> Path | None:
    """Saves the JSON report."""
    output_path = output_dir / "sensitive_data_report.json"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        return output_path
    except Exception as e:
        logger.error(f"Error saving sensitive_data_report.json: {e}")
        print(f"Error saving sensitive_data_report.json: {e}")
        return None

def run_sensitive_data_detection(output_dir: Path, ocr_engine) -> bool:
    """
    Orchestrates Step 11A.
    """
    try:
        best_image_name = load_best_candidate(output_dir)
        if not best_image_name:
            print("  [Step 11A] Failed to determine best candidate from OCR analysis.")
            return False
            
        img_path = output_dir / best_image_name
        if not img_path.exists():
            print(f"  [Step 11A] Best candidate image not found: {img_path}")
            return False
            
        print(f"  Selected source image: {best_image_name}")
        
        # Run OCR to get coordinates and text
        ocr_results = perform_ocr(ocr_engine, img_path)
        if not ocr_results:
            print("  [Step 11A] Failed to run OCR on best candidate.")
            return False
            
        detections = ocr_results.get("detections", [])
        print(f"  OCR regions examined: {len(detections)}")
        
        sensitive_items = extract_sensitive_regions(ocr_results)
        print(f"  Sensitive items detected: {len(sensitive_items)}")
        
        for item in sensitive_items:
            print(f"    - [{item['type']}] '{item['matched_substring']}' Confidence: {item['confidence']}%")
            
        report = generate_sensitive_data_report(best_image_name, sensitive_items)
        out_file = save_sensitive_data_report(report, output_dir)
        
        if out_file:
            print(f"  Saved sensitive data report to: {out_file.absolute()}")
            return True
        return False
        
    except Exception as e:
        print(f"  [Step 11A] Error during sensitive data detection: {e}")
        return False

# ---------------------------------------------------------------------------
# Step 11B: Visual Redaction
# ---------------------------------------------------------------------------

def redact_sensitive_regions(image: np.ndarray, sensitive_data: list[dict], output_path: Path) -> tuple[bool, int]:
    """
    Draws solid black rectangles over sensitive regions.
    Returns (success, unique_regions_redacted_count).
    """
    if image is None:
        return False, 0
        
    img_copy = image.copy()
    h, w = img_copy.shape[:2]
    
    # Deduplicate bounding boxes to avoid drawing multiple times
    unique_boxes = set()
    for item in sensitive_data:
        box = item.get("bounding_box")
        if box and len(box) == 4:
            # Convert to a hashable tuple of tuples
            box_tuple = tuple(tuple(pt) for pt in box)
            unique_boxes.add(box_tuple)
            
    # Redact each unique box
    for box in unique_boxes:
        xs = [pt[0] for pt in box]
        ys = [pt[1] for pt in box]
        
        x_min = max(0, min(xs))
        y_min = max(0, min(ys))
        x_max = min(w - 1, max(xs))
        y_max = min(h - 1, max(ys))
        
        cv2.rectangle(img_copy, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
    success = cv2.imwrite(str(output_path), img_copy)
    return success, len(unique_boxes)

def save_redaction_report(report: dict, output_dir: Path) -> Path | None:
    """Saves the redaction report to JSON."""
    output_path = output_dir / "redaction_report.json"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        return output_path
    except Exception as e:
        logger.error(f"Error saving redaction_report.json: {e}")
        print(f"Error saving redaction_report.json: {e}")
        return None

def run_visual_redaction(output_dir: Path) -> bool:
    """
    Orchestrates Step 11B.
    """
    try:
        print("\n==================================================")
        print("STEP 11B — VISUAL REDACTION")
        print("==================================================")
        
        # 1. Load OCR analysis to find best candidate
        best_image_name = load_best_candidate(output_dir)
        if not best_image_name:
            print("Failed to determine best candidate from OCR analysis.")
            return False
            
        print(f"Source image: {best_image_name}")
            
        img_path = output_dir / best_image_name
        if not img_path.exists():
            print(f"Source image not found: {img_path}")
            return False
            
        # 2. Load sensitive data report
        report_path = output_dir / "sensitive_data_report.json"
        if not report_path.exists():
            print(f"Sensitive data report not found: {report_path}")
            return False
            
        with open(report_path, "r", encoding="utf-8") as f:
            sensitive_report = json.load(f)
            
        items = sensitive_report.get("items", [])
        print(f"Sensitive items detected: {len(items)}")
        
        if not items:
            print("No sensitive items to redact.")
            return True
            
        # 3. Load image
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"Failed to load image: {img_path}")
            return False
            
        # 4. Redact image
        output_img_path = output_dir / "document_redacted.jpg"
        success, unique_count = redact_sensitive_regions(image, items, output_img_path)
        
        if not success:
            print("Failed to save redacted image.")
            return False
            
        print(f"Unique regions redacted: {unique_count}")
        print("\nRedacted:")
        
        # Group detections by type for reporting
        types_redacted = {}
        for item in items:
            t = item.get("type", "UNKNOWN")
            types_redacted[t] = types_redacted.get(t, 0) + 1
            
        for t, count in types_redacted.items():
            print(f"- {t}: {count} instance(s)")
            
        print(f"\nSaved redacted document to:\n{output_img_path.absolute()}")
        
        # 5. Save redaction report
        redaction_report = {
            "source_image": best_image_name,
            "output_image": "document_redacted.jpg",
            "total_detected_items": len(items),
            "total_redacted_regions": unique_count,
            "redacted_regions": items  # including full detection info
        }
        
        out_report_path = save_redaction_report(redaction_report, output_dir)
        if out_report_path:
            print(f"\nSaved redaction report to:\n{out_report_path.absolute()}")
            
        return True
        
    except Exception as e:
        print(f"Error during visual redaction: {e}")
        return False
