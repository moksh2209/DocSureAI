from pathlib import Path
from core.image_processor import preprocess_document, detect_document_boundary, perspective_correction, enhance_document
from core.quality_assessment import assess_document_quality

def main():
    print("DocScan project initialized successfully.")
    
    # Get project root assuming main.py is in src/
    project_root = Path(__file__).resolve().parent.parent
    
    input_image = project_root / "data" / "input" / "document.jpg"
    output_dir = project_root / "data" / "output"
    
    print("\nRunning DocScan Pipeline...")
    
    # Step 3: Preprocess Image
    original_img, edges_img = preprocess_document(input_image, output_dir)
    
    if original_img is None or edges_img is None:
        print("Pipeline aborted during preprocessing.")
        return
        
    # Step 4: Detect Document Boundary
    corners, boundary_status = detect_document_boundary(original_img, edges_img, output_dir)
    
    if corners is None:
        print("\nDocument boundary detection failed entirely. Aborting pipeline.")
        return
        
    # Step 5: Perspective Correction
    warped_img = perspective_correction(original_img, corners, output_dir)
    
    if warped_img is None:
        print("\nPipeline Step 5 (Perspective Correction) Failed. Aborting pipeline.")
        return
        
    # Step 7: Document Quality Assessment
    quality_report = assess_document_quality(warped_img, output_dir)
    
    if quality_report is not None:
        print("\nPipeline Step 7 (Quality Assessment) Passed.")
    else:
        print("\nPipeline Step 7 (Quality Assessment) Failed.")
        return
        
    # Step 6: Image Enhancement
    success_enh = enhance_document(warped_img, output_dir)
    
    if success_enh:
        print("\nPipeline Step 6 (Image Enhancement) Passed.")
    else:
        print("\nPipeline Step 6 (Image Enhancement) Failed.")
        return
        
    # Step 8: OCR All Candidate Versions
    from core.ocr_engine import initialize_ocr_engine, perform_ocr
    from core.ocr_analysis import (
        analyze_ocr_results,
        print_comparison_table,
        save_analysis_report,
    )
    import json

    print("\n--- Starting Step 8: Multi-Version OCR Evaluation ---")
    ocr_engine = initialize_ocr_engine()
    if ocr_engine is None:
        print("Failed to initialize OCR engine. Aborting pipeline.")
        return

    candidates = [
        "document_scanned.jpg",
        "document_scan_grayscale.jpg",
        "document_scan_clahe.jpg",
        "document_scan_denoised.jpg",
        "document_scan_threshold.jpg",
        "document_scan_sharpened.jpg",
    ]

    all_results = []

    for candidate in candidates:
        cand_path = output_dir / candidate
        if not cand_path.exists():
            print(f"Candidate missing, skipping: {candidate}")
            continue

        print(f"Running OCR on {candidate}...")
        res = perform_ocr(ocr_engine, cand_path)
        if res is not None and res["average_confidence"] > 0:
            all_results.append(res)
            print(f"  -> Average Confidence: {res['average_confidence']:.2f}%")
        else:
            print(f"  -> Failed to OCR or no text found for {candidate}")

    if not all_results:
        print("All OCR attempts failed or found no text.")
        return

    # Save raw OCR results (preserves ocr_results.json exactly as before)
    # Sort by confidence to match original behaviour
    all_results_sorted_by_conf = sorted(
        all_results, key=lambda x: x["average_confidence"], reverse=True
    )
    ocr_report = {
        "results": [
            {
                "image_name": r["image_name"],
                "average_confidence": r["average_confidence"],
                "extracted_text": r["extracted_text"],
            }
            for r in all_results_sorted_by_conf
        ],
        "best_candidate": {
            "image_name": all_results_sorted_by_conf[0]["image_name"],
            "average_confidence": all_results_sorted_by_conf[0]["average_confidence"],
        },
    }
    report_path = output_dir / "ocr_results.json"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(ocr_report, f, indent=4, ensure_ascii=False)
        print(f"Saved OCR multi-version results to: {report_path.absolute()}")
    except Exception as e:
        print(f"Error saving OCR report: {e}")

    print("--- OCR Evaluation Completed ---")
    print("\nPipeline Step 8 (OCR Integration) Passed.")

    # ------------------------------------------------------------------
    # Step 9: Intelligent OCR Result Analysis & Candidate Selection
    # ------------------------------------------------------------------
    print("\n--- Starting Step 9: Intelligent OCR Result Analysis ---")

    analyzed_results = analyze_ocr_results(all_results)

    if not analyzed_results:
        print("OCR analysis produced no results. Aborting Step 9.")
        return

    # Print comparison table to terminal
    print_comparison_table(analyzed_results)

    # Select best candidate (first non-empty, highest overall quality score)
    best_analyzed = next(
        (a for a in analyzed_results if not a.get("flags", {}).get("is_empty")),
        None,
    )

    if best_analyzed is None:
        print("All OCR candidates returned empty text. Cannot select a best candidate.")
        return

    print(
        f"Best Candidate (Overall Quality Score): "
        f"{best_analyzed['image_name']} "
        f"(Score: {best_analyzed['overall_ocr_quality_score']:.2f}, "
        f"Confidence: {best_analyzed['average_confidence']:.2f}%)"
    )

    # Retrieve original extracted text for the selected candidate
    # (stored as private key '_extracted_text' during analysis)
    best_text = best_analyzed.get("_extracted_text", "")

    # Save ocr_analysis.json (does NOT touch ocr_results.json)
    save_analysis_report(analyzed_results, output_dir)

    # Write extracted_text.txt from the newly selected best candidate
    text_path = output_dir / "extracted_text.txt"
    try:
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(best_text)
        print(f"Saved best extracted text to: {text_path.absolute()}")
    except Exception as e:
        print(f"Error saving extracted text: {e}")

    print("--- Analysis Completed ---")
    print("\nPipeline Step 9 (OCR Result Analysis) Passed.")

    # ------------------------------------------------------------------
    # Step 10: Structured Document Analysis
    # ------------------------------------------------------------------
    print("\n--- Starting Step 10: Structured Document Analysis ---")

    try:
        from core.document_structure import analyze_document_structure, save_structure_report

        structure = analyze_document_structure(text_path)

        if structure is None:
            print("  [Step 10] Structured analysis returned no result. Skipping.")
        else:
            stats = structure.get("statistics", {})
            title = structure.get("document_title") or "(not detected)"

            print(f"  Detected Title      : {title}")
            print(f"  Sections found      : {stats.get('section_count', 0)}")
            print(f"  Paragraphs found    : {stats.get('paragraph_count', 0)}")
            print(f"  Bullet lists found  : {stats.get('bullet_list_count', 0)}")
            print(f"  Numbered lists found: {stats.get('numbered_list_count', 0)}")

            save_structure_report(structure, output_dir)
            print("--- Structured Analysis Completed ---")
            print("\nPipeline Step 10 (Structured Document Analysis) Passed.")

    except Exception as step10_err:
        print(f"  [Step 10] Structured analysis failed: {step10_err}")
        print("  Continuing without structured analysis output.")

    # ------------------------------------------------------------------
    # Step 11A: Sensitive Information Detection
    # ------------------------------------------------------------------
    print("\n--- Starting Step 11A: Sensitive Information Detection ---")
    try:
        from core.redaction import run_sensitive_data_detection
        success_11a = run_sensitive_data_detection(output_dir, ocr_engine)
        if success_11a:
            print("\nPipeline Step 11A (Sensitive Information Detection) Passed.")
        else:
            print("\nPipeline Step 11A (Sensitive Information Detection) Failed.")
    except Exception as step11a_err:
        print(f"  [Step 11A] Detection failed: {step11a_err}")
        print("\nPipeline Step 11A (Sensitive Information Detection) Failed.")

    # ------------------------------------------------------------------
    # Step 11B: Visual Redaction
    # ------------------------------------------------------------------
    try:
        from core.redaction import run_visual_redaction
        success_11b = run_visual_redaction(output_dir)
        if success_11b:
            print("\nPipeline Step 11B (Visual Redaction) Passed.")
        else:
            print("\nPipeline Step 11B (Visual Redaction) Failed.")
    except Exception as step11b_err:
        print(f"  [Step 11B] Visual redaction failed: {step11b_err}")
        print("\nPipeline Step 11B (Visual Redaction) Failed.")

if __name__ == "__main__":
    main()
