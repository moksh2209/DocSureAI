import cv2
import numpy as np
from pathlib import Path

def load_and_validate_image(image_path: str | Path):
    """
    Validates file existence and loads an image using OpenCV.
    Returns (image, None) if successful, or (None, error_message) on failure.
    """
    img_path = Path(image_path)
    if not img_path.exists() or not img_path.is_file():
        return None, f"Image file does not exist at {img_path.absolute()}"
        
    image = cv2.imread(str(img_path))
    if image is None:
        return None, f"Failed to load the image at {img_path.absolute()}. It may be corrupted or not a valid image format."
        
    return image, None

def test_image_processing(image_path: str | Path, output_dir: str | Path) -> bool:
    """
    Reads an image, validates it, prints its properties, and saves a copy.
    """
    out_dir = Path(output_dir)
    img_path = Path(image_path)
    print(f"--- Starting Image Processing Test ---")
    
    image, error_msg = load_and_validate_image(img_path)
    if error_msg:
        print(f"Error: {error_msg}")
        return False
        
    print(f"File found and loaded successfully: {img_path.absolute()}")
    
    # Get image info
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1
    
    print(f"Image width: {width} pixels")
    print(f"Image height: {height} pixels")
    print(f"Number of channels: {channels}")
    print(f"Image shape: {image.shape}")
    
    # Ensure output directory exists
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Failed to create output directory {out_dir.absolute()}: {e}")
        return False
        
    # Save a copy
    output_path = out_dir / img_path.name
    success = cv2.imwrite(str(output_path), image)
    
    if not success:
        print(f"Error: Failed to save the image to {output_path.absolute()}")
        return False
        
    print(f"Successfully saved a copy to: {output_path.absolute()}")
    print(f"--- Image Processing Test Completed Successfully ---")
    return True

def preprocess_document(image_path: str | Path, output_dir: str | Path, 
                        blur_kernel: tuple = (5, 5), 
                        canny_thresholds: tuple = (75, 200)) -> tuple[np.ndarray | None, np.ndarray | None]:
    """
    Preprocesses a document image by applying grayscale, Gaussian blur, and Canny edge detection.
    Saves all intermediate results.
    Returns (original_image, edges_image) or (None, None) if it fails.
    """
    out_dir = Path(output_dir)
    img_path = Path(image_path)
    
    print(f"\n--- Starting Step 3: Image Preprocessing Pipeline ---")
    
    # 1. Load and validate
    print(f"[1/4] Loading image from {img_path.absolute()}")
    image, error_msg = load_and_validate_image(img_path)
    if error_msg:
        print(f"Error: {error_msg}")
        return None, None
        
    # Ensure output directory exists
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Failed to create output directory {out_dir.absolute()}: {e}")
        return None, None

    def save_intermediate(img, filename):
        path = out_dir / filename
        if not cv2.imwrite(str(path), img):
            print(f"Error: Failed to save {filename} to {path.absolute()}")
            return False
        print(f"      Saved: {filename}")
        return True

    if not save_intermediate(image, "document_original.jpg"): return None, None

    # 2. Grayscale
    print(f"[2/4] Converting to grayscale...")
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if not save_intermediate(gray_img, "document_grayscale.jpg"): return None, None
    
    # 3. Gaussian Blur
    print(f"[3/4] Applying Gaussian Blur with kernel {blur_kernel}...")
    blurred_img = cv2.GaussianBlur(gray_img, blur_kernel, 0)
    if not save_intermediate(blurred_img, "document_blurred.jpg"): return None, None
    
    # 4. Canny Edge Detection
    print(f"[4/4] Applying Canny Edge Detection with thresholds {canny_thresholds}...")
    edges_img = cv2.Canny(blurred_img, canny_thresholds[0], canny_thresholds[1])
    if not save_intermediate(edges_img, "document_edges.jpg"): return None, None
    
    print(f"--- Image Preprocessing Completed Successfully ---")
    return image, edges_img

def detect_document_boundary(image: np.ndarray, edges: np.ndarray, output_dir: str | Path) -> tuple[np.ndarray | None, str]:
    """
    Detects the document boundary in the image.
    Returns a tuple of (4 corner points, status string).
    """
    print(f"\n--- Starting Step 4: Document Boundary Detection ---")
    out_dir = Path(output_dir)
    
    # Find contours using OpenCV
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Total number of contours found: {len(contours)}")
    
    # Sort contours by area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Examine the largest plausible contours
    candidates = contours[:5]
    print(f"Number of candidate contours examined: {len(candidates)}")
    
    document_contour = None
    
    # For each candidate contour
    for c in candidates:
        area = cv2.contourArea(c)
        # Add reasonable validation so that very small contours are ignored
        if area < 5000:
            continue
            
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        
        # Check whether the approximation has exactly 4 points
        if len(approx) == 4:
            document_contour = approx
            print(f"Detected document contour area: {area:.2f}")
            print(f"Detected corner coordinates:\n{approx.reshape(4, 2)}")
            break
            
    status = "contour_detected"
    # Handle failure gracefully with fallback
    if document_contour is None:
        print("Failed to find a valid 4-corner document contour in the candidate contours.")
        print("Document contour not detected. Using full image as fallback document boundary.")
        status = "full_image_fallback"
        h, w = image.shape[:2]
        document_contour = np.array([
            [[0, 0]],
            [[w - 1, 0]],
            [[w - 1, h - 1]],
            [[0, h - 1]]
        ], dtype=np.int32)
        
    # If a document boundary is detected, draw it on a copy of the original image
    img_copy = image.copy()
    cv2.drawContours(img_copy, [document_contour], -1, (0, 255, 0), 3)
    
    # Save the result
    output_path = out_dir / "document_detected.jpg"
    success = cv2.imwrite(str(output_path), img_copy)
    if success:
        print(f"Saved detection visualization to: {output_path.absolute()}")
    else:
        print(f"Error: Failed to save detection visualization to {output_path.absolute()}")
        
    print(f"--- Document Boundary Detection Completed ---")
    return document_contour, status

def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Orders a list of 4 points in top-left, top-right, bottom-right, bottom-left order.
    """
    # Reshape just in case it comes directly from approxPolyDP which has shape (4, 1, 2)
    pts = pts.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    # Top-left has smallest sum, bottom-right has largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # Top-right has smallest diff (y-x), bottom-left has largest diff
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def perspective_correction(image: np.ndarray, corners: np.ndarray, output_dir: str | Path) -> np.ndarray | None:
    """
    Applies perspective transformation to flatten the detected document.
    """
    print(f"\n--- Starting Step 5: Perspective Correction ---")
    out_dir = Path(output_dir)
    
    raw_pts = corners.reshape(4, 2)
    print(f"Raw detected corner points:\n{raw_pts}")
    
    rect = order_points(corners)
    print(f"Ordered corner points (TL, TR, BR, BL):\n{rect}")
    
    (tl, tr, br, bl) = rect
    
    # Calculate output width: max of bottom width and top width
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # Calculate output height: max of right height and left height
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    print(f"Calculated output width: {maxWidth}")
    print(f"Calculated output height: {maxHeight}")
    
    # Destination points for top-down view
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    
    # Calculate perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    
    # Warp perspective
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    # Save the flattened document
    output_path = out_dir / "document_scanned.jpg"
    success = cv2.imwrite(str(output_path), warped)
    
    if success:
        print(f"Perspective transformation successful.")
        print(f"Saved scanned document to: {output_path.absolute()}")
    else:
        print(f"Error: Failed to save scanned document to {output_path.absolute()}")
        return None
        
    print(f"--- Perspective Correction Completed ---")
    return warped

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_clahe(image_gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(image_gray)

def denoise_document(image_gray: np.ndarray, h: float = 10.0) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image_gray, None, h=h, templateWindowSize=7, searchWindowSize=21)

def adaptive_threshold(image_gray: np.ndarray, block_size: int = 31, c: int = 10) -> np.ndarray:
    if block_size % 2 == 0:
        block_size += 1
    return cv2.adaptiveThreshold(
        image_gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        block_size, c
    )

def sharpen_document(image_gray: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    return cv2.filter2D(image_gray, -1, kernel)

def enhance_document(image: np.ndarray, output_dir: str | Path) -> bool:
    """
    Applies multiple image enhancements to a perspective-corrected document image.
    Generates Grayscale, CLAHE, Denoised, Threshold, and Sharpened versions.
    """
    print(f"\n--- Starting Step 6: Image Enhancement ---")
    out_dir = Path(output_dir)
    
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Failed to create output directory {out_dir.absolute()}: {e}")
        return False
        
    print(f"Input image dimensions: {image.shape}")
    
    def save_enhanced(img, filename):
        path = out_dir / filename
        if not cv2.imwrite(str(path), img):
            print(f"Error: Failed to save {filename} to {path.absolute()}")
            return False
        print(f"      Saved: {filename}")
        return True

    # A. Grayscale
    print(f"[1/5] Converting to grayscale...")
    gray_img = convert_to_grayscale(image)
    if not save_enhanced(gray_img, "document_scan_grayscale.jpg"): return False

    # B. CLAHE
    print(f"[2/5] Applying CLAHE (clipLimit=2.0, tileGridSize=(8, 8))...")
    clahe_img = apply_clahe(gray_img, clip_limit=2.0, tile_grid_size=(8, 8))
    if not save_enhanced(clahe_img, "document_scan_clahe.jpg"): return False

    # C. Denoising
    print(f"[3/5] Applying Denoising (fastNlMeansDenoising, h=10.0)...")
    denoised_img = denoise_document(gray_img, h=10.0)
    if not save_enhanced(denoised_img, "document_scan_denoised.jpg"): return False

    # D. Adaptive Thresholding
    print(f"[4/5] Applying Adaptive Thresholding (block_size=31, C=10)...")
    thresh_img = adaptive_threshold(clahe_img, block_size=31, c=10)
    if not save_enhanced(thresh_img, "document_scan_threshold.jpg"): return False

    # E. Sharpening
    print(f"[5/5] Applying Sharpening...")
    sharpened_img = sharpen_document(gray_img)
    if not save_enhanced(sharpened_img, "document_scan_sharpened.jpg"): return False

    print(f"--- Image Enhancement Completed Successfully ---")
    return True
