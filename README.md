# DocSureAI

## Project Overview

DocSureAI is a computer-vision and OCR based document processing pipeline.

## Objectives

1. Develop a high-accuracy, deterministic document scanner pipeline.
2. Ensure automated perspective correction and enhancement.
3. Perform heuristic OCR quality assessment.
4. Extract structural information from documents.
5. Identify and redact sensitive personal information automatically.

## Implemented Pipeline

1. Image preprocessing
2. Document boundary detection
3. Perspective correction
4. Image enhancement
5. Document quality assessment
6. OCR
7. OCR result analysis
8. Document structure analysis
9. Sensitive information detection
10. Visual sensitive-data redaction

Step 4 has a full-image fallback for images where a document contour cannot be detected.

## Technologies Used

- Python
- OpenCV
- NumPy
- EasyOCR
- PyTorch
- Torchvision

## Project Structure

- `src/main.py`: Main entry point for the pipeline.
- `src/core/`: Contains the core logic for the pipeline (image processing, OCR, structure analysis, redaction).
- `src/utils/`: Utility functions.
- `data/input/`: Directory for input document images.
- `data/output/`: Directory for generated outputs (images and JSON reports).
- `tests/`: Directory for automated tests.

## Installation

1. Create a Python virtual environment named `venv`:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

Run the pipeline using:

```bash
python src/main.py
```

The current pipeline uses `data/input/document.jpg` as the input image.

## Generated Outputs

The following important outputs are generated under `data/output/`:

- Preprocessing images (grayscale, edges, etc.)
- Scanned image (perspective corrected)
- Enhanced images (CLAHE, denoised, sharpened, etc.)
- Quality report (`document_quality_report.json`)
- OCR results (`ocr_results.json`)
- OCR analysis (`ocr_analysis.json`)
- Document structure report (`document_structure.json`)
- Sensitive data report (`sensitive_data_report.json`)
- Redacted document (`document_redacted.jpg`)
- Redaction report (`redaction_report.json`)

Note: `data/output/` contains generated files and should not be committed to Git.

## OCR / Detection Limitations

- OCR can misread characters or punctuation.
- OCR errors can affect downstream pattern detection.
- URL detection is intentionally conservative.
- Pre-cropped digital images may use the full-image boundary fallback.

## Testing Status

- End-to-end baseline test passed.
- One unique document has been tested so far.
- Multi-document robustness has NOT been fully established because additional unique test documents were not available.

## Security / Privacy

- Sensitive information is detected using OCR text and pattern matching.
- Visual redaction uses solid black rectangles.
- Original/source images are preserved.
- Generated sensitive reports remain in `data/output/`.

## Development Status

The implementation is complete through Step 11B and the project is now in final cleanup/documentation/testing stage.
