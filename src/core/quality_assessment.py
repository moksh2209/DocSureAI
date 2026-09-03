import cv2
import numpy as np
import json
from pathlib import Path

def assess_sharpness(gray_img: np.ndarray, thresholds: tuple = (100, 500)) -> dict:
    score = float(cv2.Laplacian(gray_img, cv2.CV_64F).var())
    if score < thresholds[0]:
        status = "Blurry"
    elif score < thresholds[1]:
        status = "Moderate"
    else:
        status = "Sharp"
        
    # Normalize score (0-100 heuristic). Cap at 1000 for calculation.
    norm_score = min(max(score / 10.0, 0), 100)
    return {"score": score, "normalized": norm_score, "status": status}

def assess_brightness(gray_img: np.ndarray, thresholds: tuple = (50, 100, 200, 240)) -> dict:
    score = float(np.mean(gray_img))
    if score < thresholds[0]:
        status = "Too Dark"
    elif score < thresholds[1]:
        status = "Dark"
    elif score < thresholds[2]:
        status = "Good"
    elif score < thresholds[3]:
        status = "Bright"
    else:
        status = "Too Bright"
        
    # Normalize score (0-100 heuristic). Ideal brightness around 150.
    dist_from_ideal = abs(score - 150)
    norm_score = max(100 - dist_from_ideal, 0)
    return {"score": score, "normalized": norm_score, "status": status}

def assess_contrast(gray_img: np.ndarray, thresholds: tuple = (20, 40, 60)) -> dict:
    score = float(np.std(gray_img))
    if score < thresholds[0]:
        status = "Low"
    elif score < thresholds[1]:
        status = "Moderate"
    elif score < thresholds[2]:
        status = "Good"
    else:
        status = "High"
        
    # Normalize score (0-100 heuristic). Ideal is >= 60.
    norm_score = min(max((score / 60.0) * 100, 0), 100)
    return {"score": score, "normalized": norm_score, "status": status}

def assess_resolution(img: np.ndarray, thresholds: tuple = (500000, 1000000)) -> dict:
    h, w = img.shape[:2]
    pixels = int(h * w)
    if pixels < thresholds[0]:
        status = "Low Resolution"
    elif pixels < thresholds[1]:
        status = "Medium Resolution"
    else:
        status = "Good Resolution"
        
    # Normalize score (0-100 heuristic). Ideal >= 1,000,000.
    norm_score = min(max((pixels / 1000000.0) * 100, 0), 100)
    return {"width": w, "height": h, "pixels": pixels, "normalized": norm_score, "status": status}

def assess_document_quality(image: np.ndarray, output_dir: str | Path = None) -> dict | None:
    if image is None:
        print("Error: Invalid image provided for quality assessment.")
        return None
        
    print(f"\n--- Starting Step 7: Document Quality Assessment ---")
    
    # Convert to grayscale for metrics if it's not already
    if len(image.shape) == 3:
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = image
        
    sharpness = assess_sharpness(gray_img)
    brightness = assess_brightness(gray_img)
    contrast = assess_contrast(gray_img)
    resolution = assess_resolution(image)
    
    # Weights: Sharpness: 35%, Brightness: 20%, Contrast: 25%, Resolution: 20%
    overall_score = (
        sharpness["normalized"] * 0.35 +
        brightness["normalized"] * 0.20 +
        contrast["normalized"] * 0.25 +
        resolution["normalized"] * 0.20
    )
    
    if overall_score < 40:
        overall_status = "Poor"
        recommendation = "Image quality is poor. Re-capture if possible, or expect very low OCR accuracy."
    elif overall_score < 65:
        overall_status = "Fair"
        recommendation = "Image may benefit from enhancement before OCR."
    elif overall_score < 85:
        overall_status = "Good"
        recommendation = "Document quality is suitable for OCR."
    else:
        overall_status = "Excellent"
        recommendation = "Document quality is excellent for OCR."
        
    report = {
        "sharpness": {
            "score": sharpness["score"],
            "status": sharpness["status"]
        },
        "brightness": {
            "score": brightness["score"],
            "status": brightness["status"]
        },
        "contrast": {
            "score": contrast["score"],
            "status": contrast["status"]
        },
        "resolution": {
            "width": resolution["width"],
            "height": resolution["height"],
            "pixels": resolution["pixels"],
            "status": resolution["status"]
        },
        "overall_score": float(overall_score),
        "overall_status": overall_status,
        "recommendation": recommendation
    }
    
    # Print readable report
    print(f"Overall Quality Score: {overall_score:.2f}/100 ({overall_status})")
    print(f"Recommendation: {recommendation}")
    print(f"Metrics:")
    print(f"  - Sharpness: {sharpness['score']:.2f} ({sharpness['status']})")
    print(f"  - Brightness: {brightness['score']:.2f} ({brightness['status']})")
    print(f"  - Contrast: {contrast['score']:.2f} ({contrast['status']})")
    print(f"  - Resolution: {resolution['width']}x{resolution['height']} ({resolution['status']})")
    
    if output_dir:
        out_dir = Path(output_dir)
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            report_path = out_dir / "document_quality_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4)
            print(f"Saved quality report to: {report_path.absolute()}")
        except Exception as e:
            print(f"Error: Failed to save quality report: {e}")
            
    print(f"--- Document Quality Assessment Completed ---")
    return report
