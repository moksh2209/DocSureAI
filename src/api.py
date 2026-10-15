import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="DocSureAI API")

allowed_origins_str = os.environ.get("DOCSUREAI_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
INPUT_FILE = INPUT_DIR / "document.jpg"
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

# Ensure output directory exists for static file serving
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

ASSETS_DIR = FRONTEND_DIST_DIR / "assets"
if ASSETS_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Global processing lock (single-user constraint)
_is_processing = False

def read_json_report(filename: str):
    path = OUTPUT_DIR / filename
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

@app.post("/api/process")
async def process_document(file: UploadFile = File(...)):
    global _is_processing
    if _is_processing:
        raise HTTPException(status_code=429, detail="Document processing is already in progress.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    _is_processing = True
    try:
        # Ensure directories exist
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Clear existing output files from previous runs to prevent stale data
        for old_file in OUTPUT_DIR.iterdir():
            if old_file.is_file():
                try:
                    old_file.unlink()
                except Exception:
                    pass

        # Save uploaded file to the fixed input location
        with open(INPUT_FILE, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Import the main pipeline dynamically so it runs in this thread
        from src import main
        
        # Execute the pipeline
        try:
            main.run_pipeline(INPUT_FILE, OUTPUT_DIR)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

        # Gather results
        quality = read_json_report("document_quality_report.json")
        ocr_results = read_json_report("ocr_results.json")
        ocr_analysis = read_json_report("ocr_analysis.json")
        structure = read_json_report("document_structure.json")
        sensitive_data = read_json_report("sensitive_data_report.json")
        redaction = read_json_report("redaction_report.json")

        if not any([quality, ocr_results, ocr_analysis, structure, sensitive_data, redaction]):
             raise HTTPException(status_code=500, detail="Pipeline completed but no output reports were found.")

        # Determine best candidate confidence and enhanced image
        ocr_confidence = None
        enhanced_image_name = None
        if ocr_analysis and "best_candidate" in ocr_analysis and ocr_analysis["best_candidate"]:
            ocr_confidence = ocr_analysis["best_candidate"].get("average_confidence")
            enhanced_image_name = ocr_analysis["best_candidate"].get("image_name")

        response_data = {
            "success": True,
            "filename": file.filename,
            "quality": quality,
            "ocr": {
                "results": ocr_results,
                "analysis": ocr_analysis,
                "confidence": ocr_confidence
            },
            "structure": structure,
            "sensitive_data": sensitive_data,
            "redaction": redaction,
            "images": {
                "original": "/outputs/document_original.jpg",
                "scanned": "/outputs/document_scanned.jpg",
                "enhanced": f"/outputs/{enhanced_image_name}" if enhanced_image_name else None,
                "redacted": "/outputs/document_redacted.jpg"
            }
        }
        return JSONResponse(content=response_data)

    finally:
        _is_processing = False


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found.")
    if full_path == "outputs" or full_path.startswith("outputs/"):
        raise HTTPException(status_code=404, detail="Output file not found.")

    frontend_root = FRONTEND_DIST_DIR.resolve()
    requested_file = (frontend_root / full_path).resolve()
    if not requested_file.is_relative_to(frontend_root):
        raise HTTPException(status_code=404, detail="Frontend file not found.")
    if requested_file.is_file():
        return FileResponse(requested_file)

    index_file = frontend_root / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="Frontend build not found.")
    return FileResponse(index_file)
