"""
ocr_analysis.py — Step 9: Intelligent OCR Result Analysis & Candidate Selection
================================================================================

This module analyzes structured OCR results produced by ocr_engine.py and
selects the best candidate image using a transparent, weighted heuristic.

NOTE ON SCORING:
  All scores are heuristics intended to be interpretable and configurable.
  They are NOT scientifically validated ground-truth metrics.
  The weights and thresholds below were chosen to keep OCR confidence as the
  dominant factor while giving meaningful secondary weight to text quantity.

SCORING WEIGHTS (must sum to 1.0):
  OCR Confidence    : 0.50  (most important — provided by EasyOCR)
  Text Completeness : 0.30  (reward extracting more usable text)
  Detection Coverage: 0.20  (reward finding more individual text regions)
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — adjust thresholds without touching the logic
# ---------------------------------------------------------------------------

# Weights for overall quality score (must sum to 1.0)
WEIGHT_CONFIDENCE   = 0.50
WEIGHT_COMPLETENESS = 0.30
WEIGHT_DETECTION    = 0.20

# Completeness sub-component saturation points
# (score plateaus once these values are reached)
COMPLETENESS_WORD_SATURATION       = 50    # words
COMPLETENESS_CHAR_SATURATION       = 300   # characters
COMPLETENESS_DETECTION_SATURATION  = 20    # detection regions

# Detection coverage saturation (standalone component)
DETECTION_COVERAGE_SATURATION      = 30    # detection regions

# Thresholds for suspicious-result flags
SUSPICIOUS_MIN_WORDS = 5
SUSPICIOUS_MIN_CHARS = 20


# ---------------------------------------------------------------------------
# A. Text length metrics
# ---------------------------------------------------------------------------

def calculate_text_metrics(text: str) -> dict:
    """
    Calculate character count, word count, and line count from extracted text.

    Handles empty/whitespace-only text safely — all counts return 0.

    Args:
        text: The raw string extracted by EasyOCR.

    Returns:
        dict with keys: character_count, word_count, line_count
    """
    if not text or not text.strip():
        return {"character_count": 0, "word_count": 0, "line_count": 0}

    # Strip leading/trailing whitespace but keep internal structure
    stripped = text.strip()

    char_count  = len(stripped)
    word_count  = len(stripped.split())
    line_count  = len([ln for ln in stripped.splitlines() if ln.strip()])

    return {
        "character_count": char_count,
        "word_count":      word_count,
        "line_count":      line_count,
    }


# ---------------------------------------------------------------------------
# B. Text Completeness Score (0–100)
# ---------------------------------------------------------------------------

def calculate_text_completeness_score(
    word_count: int,
    char_count: int,
    detection_count: int,
) -> float:
    """
    Heuristic text completeness score from 0 to 100.

    PURPOSE:
      Penalise candidates that have very high OCR confidence but captured
      only a tiny fragment of text.  A candidate with 90% confidence on
      3 words should score lower overall than one with 88% confidence on
      150 words.

    FORMULA (three additive sub-components, each normalised to a max):
      word_score      = min(word_count  / WORD_SAT,  1.0) × 50
      char_score      = min(char_count  / CHAR_SAT,  1.0) × 30
      detection_score = min(det_count   / DET_SAT,   1.0) × 20
      total           = word_score + char_score + detection_score  (max 100)

    The weights (50 / 30 / 20) keep word count as the strongest signal
    while still rewarding character density and detection breadth.

    Args:
        word_count:      Number of words in extracted text.
        char_count:      Number of characters in extracted text.
        detection_count: Number of EasyOCR bounding-box detections.

    Returns:
        Float in [0, 100].
    """
    word_score = (
        min(word_count  / COMPLETENESS_WORD_SATURATION,      1.0) * 50.0
    )
    char_score = (
        min(char_count  / COMPLETENESS_CHAR_SATURATION,      1.0) * 30.0
    )
    detection_score = (
        min(detection_count / COMPLETENESS_DETECTION_SATURATION, 1.0) * 20.0
    )

    return round(word_score + char_score + detection_score, 2)


# ---------------------------------------------------------------------------
# C. Detection Coverage Score (0–100)
# ---------------------------------------------------------------------------

def calculate_detection_coverage_score(detection_count: int) -> float:
    """
    Normalised score (0–100) based on the number of bounding-box detections.

    Plateaus at DETECTION_COVERAGE_SATURATION detections — beyond that point
    the score remains 100.  This prevents a noisy image with many tiny
    fragmented detections from dominating.

    Args:
        detection_count: Number of EasyOCR detections.

    Returns:
        Float in [0, 100].
    """
    return round(
        min(detection_count / DETECTION_COVERAGE_SATURATION, 1.0) * 100.0,
        2,
    )


# ---------------------------------------------------------------------------
# D. Suspicious / Empty OCR Detection
# ---------------------------------------------------------------------------

def detect_suspicious_ocr(
    text: str,
    avg_confidence: float,
    detection_count: int,
) -> dict:
    """
    Identify potentially invalid or low-quality OCR outputs.

    Checks performed:
      • is_empty              — no text at all (empty string or whitespace only)
      • is_suspiciously_short — fewer than SUSPICIOUS_MIN_WORDS words
                                OR fewer than SUSPICIOUS_MIN_CHARS chars
      • zero_detections       — no bounding-box regions detected
      • invalid_confidence    — confidence is NaN, None, negative, or > 100

    Args:
        text:           Extracted text string.
        avg_confidence: Average OCR confidence (0–100 scale).
        detection_count: Number of detections.

    Returns:
        dict with keys: is_empty (bool), is_suspiciously_short (bool),
        issues (list[str]).
    """
    issues        = []
    is_empty      = False
    is_short      = False

    # Empty / whitespace-only check
    if not text or not text.strip():
        is_empty = True
        issues.append("No text extracted — result is empty or whitespace only.")

    else:
        stripped   = text.strip()
        word_count = len(stripped.split())
        char_count = len(stripped)

        if word_count < SUSPICIOUS_MIN_WORDS:
            is_short = True
            issues.append(
                f"Suspiciously low word count ({word_count} words; "
                f"threshold: {SUSPICIOUS_MIN_WORDS})."
            )

        if char_count < SUSPICIOUS_MIN_CHARS:
            is_short = True
            issues.append(
                f"Suspiciously low character count ({char_count} chars; "
                f"threshold: {SUSPICIOUS_MIN_CHARS})."
            )

    # Zero detections
    if detection_count == 0:
        issues.append("Zero bounding-box detections found.")

    # Invalid confidence
    try:
        conf_val = float(avg_confidence)
        if conf_val < 0 or conf_val > 100:
            issues.append(
                f"Confidence value out of expected range: {conf_val:.2f} "
                "(expected 0–100)."
            )
    except (TypeError, ValueError):
        issues.append(f"Invalid confidence value: {avg_confidence!r}.")

    return {
        "is_empty":              is_empty,
        "is_suspiciously_short": is_short,
        "issues":                issues,
    }


# ---------------------------------------------------------------------------
# E. Overall OCR Quality Score (0–100)
# ---------------------------------------------------------------------------

def calculate_overall_quality_score(
    avg_confidence:       float,
    completeness_score:   float,
    detection_cov_score:  float,
) -> float:
    """
    Weighted heuristic quality score from 0 to 100.

    FORMULA:
      score = (WEIGHT_CONFIDENCE   × avg_confidence)
            + (WEIGHT_COMPLETENESS × completeness_score)
            + (WEIGHT_DETECTION    × detection_cov_score)

    Weights (defined at module top):
      Confidence    50% — dominant; higher confidence → higher score
      Completeness  30% — rewards extracting more words/chars
      Detection     20% — rewards detecting more text regions

    All three inputs must already be on a 0–100 scale.

    Args:
        avg_confidence:      EasyOCR average confidence (0–100).
        completeness_score:  Text completeness score (0–100).
        detection_cov_score: Detection coverage score (0–100).

    Returns:
        Float in [0, 100], rounded to 2 dp.
    """
    score = (
        WEIGHT_CONFIDENCE   * avg_confidence
      + WEIGHT_COMPLETENESS * completeness_score
      + WEIGHT_DETECTION    * detection_cov_score
    )
    # Guard against floating-point drift outside [0, 100]
    return round(max(0.0, min(100.0, score)), 2)


# ---------------------------------------------------------------------------
# Analyse a single OCR result dict
# ---------------------------------------------------------------------------

def analyze_single_result(ocr_result: dict) -> dict:
    """
    Compute full quality metrics for one OCR candidate result.

    Expected input keys (matching ocr_engine.perform_ocr output):
      image_name        (str)
      extracted_text    (str)
      average_confidence (float, 0–100)
      detections        (list of detection dicts)

    Returns a flat analysis dict with all metrics + flags.
    """
    image_name      = ocr_result.get("image_name", "unknown")
    text            = ocr_result.get("extracted_text", "")
    avg_conf        = ocr_result.get("average_confidence", 0.0)
    detections      = ocr_result.get("detections", [])
    detection_count = len(detections) if isinstance(detections, list) else 0

    # --- Validate and clamp confidence ---
    try:
        avg_conf = float(avg_conf)
        avg_conf = max(0.0, min(100.0, avg_conf))
    except (TypeError, ValueError):
        avg_conf = 0.0

    # --- Component calculations ---
    text_metrics       = calculate_text_metrics(text)
    word_count         = text_metrics["word_count"]
    char_count         = text_metrics["character_count"]
    line_count         = text_metrics["line_count"]

    completeness_score = calculate_text_completeness_score(
        word_count, char_count, detection_count
    )
    detection_cov_score = calculate_detection_coverage_score(detection_count)

    overall_score = calculate_overall_quality_score(
        avg_conf, completeness_score, detection_cov_score
    )

    flags = detect_suspicious_ocr(text, avg_conf, detection_count)

    return {
        "image_name":                image_name,
        "average_confidence":        round(avg_conf, 4),
        "character_count":           char_count,
        "word_count":                word_count,
        "line_count":                line_count,
        "detection_count":           detection_count,
        "text_completeness_score":   completeness_score,
        "detection_coverage_score":  detection_cov_score,
        "overall_ocr_quality_score": overall_score,
        "flags":                     flags,
    }


# ---------------------------------------------------------------------------
# Analyse and rank all candidates
# ---------------------------------------------------------------------------

def analyze_ocr_results(results: list) -> list:
    """
    Analyse every OCR candidate and return them sorted by overall quality.

    Candidates with empty OCR output (is_empty=True) are pushed to the
    bottom of the ranking so they are never accidentally selected.

    Args:
        results: List of OCR result dicts (from ocr_engine.perform_ocr).

    Returns:
        List of analysis dicts, ranked best-first.  Each dict includes a
        'rank' key (1-indexed).
    """
    if not results:
        logger.warning("analyze_ocr_results: received empty results list.")
        return []

    analyzed = []
    for res in results:
        try:
            analysis = analyze_single_result(res)
            # Preserve original extracted text so main.py can write it out
            analysis["_extracted_text"] = res.get("extracted_text", "")
            analyzed.append(analysis)
        except Exception as exc:
            logger.error(
                "Failed to analyse result for %r: %s",
                res.get("image_name", "unknown"),
                exc,
            )

    # Sort: valid (non-empty) results by score descending; empty results last
    def sort_key(a: dict):
        is_empty = a.get("flags", {}).get("is_empty", True)
        score    = a.get("overall_ocr_quality_score", 0.0)
        return (0 if is_empty else 1, score)   # empty → 0 → sorted last

    analyzed.sort(key=sort_key, reverse=True)

    for rank, item in enumerate(analyzed, start=1):
        item["rank"] = rank

    return analyzed


# ---------------------------------------------------------------------------
# Terminal comparison table
# ---------------------------------------------------------------------------

def print_comparison_table(analyzed: list) -> None:
    """
    Print a formatted comparison table of all OCR candidates to the terminal.

    Columns: Rank | Image Name | Avg Confidence | Word Count |
             Detection Count | Completeness Score | Overall Score
    """
    if not analyzed:
        print("No OCR analysis results to display.")
        return

    # Column widths
    col_name  = max(len(a["image_name"]) for a in analyzed)
    col_name  = max(col_name, len("Image Name"))

    header = (
        f"{'Rank':>4}  "
        f"{'Image Name':<{col_name}}  "
        f"{'Avg Conf':>8}  "
        f"{'Words':>6}  "
        f"{'Dets':>5}  "
        f"{'Complet.':>8}  "
        f"{'Quality':>7}"
    )
    separator = "-" * len(header)

    print("\n" + separator)
    print("  OCR Candidate Comparison (Step 9 — Heuristic Ranking)")
    print(separator)
    print(header)
    print(separator)

    for a in analyzed:
        flags      = a.get("flags", {})
        empty_flag = " [EMPTY]" if flags.get("is_empty") else ""
        short_flag = " [SHORT]" if flags.get("is_suspiciously_short") else ""

        row = (
            f"{a['rank']:>4}  "
            f"{a['image_name']:<{col_name}}  "
            f"{a['average_confidence']:>7.2f}%  "
            f"{a['word_count']:>6}  "
            f"{a['detection_count']:>5}  "
            f"{a['text_completeness_score']:>8.2f}  "
            f"{a['overall_ocr_quality_score']:>7.2f}"
            f"{empty_flag}{short_flag}"
        )
        print(row)

    print(separator)

    best = next((a for a in analyzed if not a.get("flags", {}).get("is_empty")), None)
    if best:
        print(
            f"\n  >> Selected Best Candidate (heuristic): "
            f"{best['image_name']}  "
            f"(Overall Score: {best['overall_ocr_quality_score']:.2f})"
        )
    print(separator + "\n")


# ---------------------------------------------------------------------------
# Save analysis report
# ---------------------------------------------------------------------------

def save_analysis_report(analyzed: list, output_dir: Path) -> Path | None:
    """
    Persist the full analysis results to data/output/ocr_analysis.json.

    Does NOT overwrite ocr_results.json.

    Args:
        analyzed:   Ranked list of analysis dicts from analyze_ocr_results.
        output_dir: Path to the output directory.

    Returns:
        Path to the saved file, or None on failure.
    """
    output_path = Path(output_dir) / "ocr_analysis.json"

    # Determine best candidate (first non-empty result)
    best = next(
        (a for a in analyzed if not a.get("flags", {}).get("is_empty")),
        analyzed[0] if analyzed else None,
    )

    # Strip the private _extracted_text key from the JSON output
    def clean(a: dict) -> dict:
        return {k: v for k, v in a.items() if not k.startswith("_")}

    report = {
        "scoring_methodology": {
            "description": (
                "Weighted heuristic — NOT scientifically validated. "
                "Weights and thresholds are configurable in ocr_analysis.py."
            ),
            "weights": {
                "ocr_confidence":    f"{WEIGHT_CONFIDENCE * 100:.0f}%",
                "text_completeness": f"{WEIGHT_COMPLETENESS * 100:.0f}%",
                "detection_coverage": f"{WEIGHT_DETECTION * 100:.0f}%",
            },
            "completeness_saturation_points": {
                "word_count":      COMPLETENESS_WORD_SATURATION,
                "char_count":      COMPLETENESS_CHAR_SATURATION,
                "detection_count": COMPLETENESS_DETECTION_SATURATION,
            },
            "detection_coverage_saturation": DETECTION_COVERAGE_SATURATION,
            "suspicious_thresholds": {
                "min_words": SUSPICIOUS_MIN_WORDS,
                "min_chars": SUSPICIOUS_MIN_CHARS,
            },
        },
        "candidates": [clean(a) for a in analyzed],
        "best_candidate": clean(best) if best else None,
        "total_candidates_analyzed": len(analyzed),
        "candidates_excluded_empty": sum(
            1 for a in analyzed if a.get("flags", {}).get("is_empty")
        ),
    }

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"Saved OCR analysis report to: {output_path.absolute()}")
        return output_path
    except Exception as exc:
        logger.error("Failed to save OCR analysis report: %s", exc)
        print(f"Error saving OCR analysis report: {exc}")
        return None
