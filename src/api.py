import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
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

# Mount output directory for static file serving
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

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

        # Determine best candidate confidence
        ocr_confidence = None
        if ocr_analysis and "best_candidate" in ocr_analysis and ocr_analysis["best_candidate"]:
            ocr_confidence = ocr_analysis["best_candidate"].get("average_confidence")

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
                "redacted": "/outputs/document_redacted.jpg"
            }
        }
        return JSONResponse(content=response_data)

    finally:
        _is_processing = False
