"""
document_structure.py — Step 10: Structured Document Analysis
=============================================================

Analyzes the structure of OCR-extracted text using deterministic
pattern matching and heuristics only.

No machine learning, no LLM APIs, no cloud services.

DETECTED STRUCTURAL ELEMENTS:
  - Document title
  - Numbered section headings  (e.g. "1. Introduction", "2.1 Background")
  - Unnumbered ALL-CAPS headings (e.g. "CHAPTER 1", "OBJECTIVES")
  - Paragraph blocks
  - Bullet lists   (lines starting with -, •, *, ◦)
  - Numbered lists (lines starting with 1., 2., a., b., i., ii.)

LIMITATIONS:
  - Heuristic-based; results depend on OCR quality.
  - Short OCR-error lines may be misclassified.
  - Table rows are treated as plain paragraphs.
  - Does not perform semantic understanding.
"""

import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns (compile once)
# ---------------------------------------------------------------------------

# Numbered section heading: "1. Title", "2.1 Title", "1.1.2 Title"
# Requires an explicit separator (. ) :) between the number and the heading text
# to avoid matching table rows like "3 Weeks" or "2 Days".
_RE_NUMBERED_HEADING = re.compile(
    r"^\s*(\d+(?:\.\d+)*)\s*[.\):]\s+([A-Z][^\n]{0,80})\s*$"
)

# All-caps heading (≥ 3 uppercase letters, no lowercase)
_RE_CAPS_HEADING = re.compile(
    r"^\s*([A-Z][A-Z\s\d\-]{2,60})\s*$"
)

# Bullet list item: -, •, *, ◦ followed by non-empty text
_RE_BULLET = re.compile(r"^\s*[-•*◦]\s+(.+)$")

# Numbered list item: "1.", "2)", "a.", "b)", "i.", "ii." etc.
_RE_NUMBERED_LIST = re.compile(
    r"^\s*(?:\d+[.\)]|[a-zA-Z][.\)]|[ivxlIVXL]+[.\)])\s+(.+)$"
)

# Lines that look like section headings but were written without a number
# (Title Case, short, not ending with sentence punctuation)
_RE_TITLE_CASE_HEADING = re.compile(
    r"^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,5})\s*$"
)

# Minimum words for a line to be considered a paragraph (not a fragment)
_PARA_MIN_WORDS = 4


# ---------------------------------------------------------------------------
# 1. Load text
# ---------------------------------------------------------------------------

def load_extracted_text(text_path: str | Path) -> str | None:
    """
    Load the OCR-extracted text file.

    Args:
        text_path: Path to extracted_text.txt

    Returns:
        String content, or None if the file is missing / unreadable.
    """
    path = Path(text_path)
    if not path.exists():
        logger.error("Extracted text file not found: %s", path)
        print(f"  [Step 10] Error: extracted_text.txt not found at {path}")
        return None

    try:
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            logger.warning("Extracted text file is empty: %s", path)
            print("  [Step 10] Warning: extracted_text.txt is empty.")
            return None
        return content
    except Exception as exc:
        logger.error("Failed to read extracted text: %s", exc)
        print(f"  [Step 10] Error reading extracted text: {exc}")
        return None


# ---------------------------------------------------------------------------
# 2. Clean text
# ---------------------------------------------------------------------------

def clean_text(raw: str) -> list[str]:
    """
    Normalize the raw OCR text into a list of clean lines.

    - Normalises Windows/Mac line endings to \\n
    - Strips leading/trailing whitespace per line
    - Removes completely blank lines at the boundary
    - Preserves internal blank lines (they help detect paragraph breaks)

    Returns:
        List of strings (one per line).
    """
    # Normalise line endings
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    # Strip trailing/leading whitespace per line but keep blank lines intact
    return [ln.rstrip() for ln in lines]


# ---------------------------------------------------------------------------
# 3. Heading detection helpers
# ---------------------------------------------------------------------------

def is_numbered_heading(line: str) -> tuple[bool, str | None]:
    """
    Returns (True, heading_text) if the line is a numbered section heading.
    Examples: "1. Introduction", "2.1 Background", "3. Scope"
    """
    m = _RE_NUMBERED_HEADING.match(line)
    if m:
        return True, line.strip()
    return False, None


def is_caps_heading(line: str) -> tuple[bool, str | None]:
    """
    Returns (True, heading_text) if the line is an ALL-CAPS heading.
    Requires at least 3 characters, no lowercase letters.
    """
    stripped = line.strip()
    if len(stripped) < 3:
        return False, None
    if stripped == stripped.upper() and re.search(r"[A-Z]{2,}", stripped):
        # Exclude lines that are just numbers or single words that are OCR noise
        if len(stripped.split()) >= 1 and not re.fullmatch(r"[\d\s\W]+", stripped):
            return True, stripped
    return False, None


def is_heading(line: str) -> tuple[bool, str | None]:
    """
    Master heading classifier.

    Priority:
      1. Numbered heading  ("1. Introduction")
      2. ALL-CAPS heading  ("OBJECTIVES")

    Returns (True, heading_text) or (False, None).
    """
    ok, text = is_numbered_heading(line)
    if ok:
        return True, text
    ok, text = is_caps_heading(line)
    if ok:
        return True, text
    return False, None


# ---------------------------------------------------------------------------
# 4. Title detection
# ---------------------------------------------------------------------------

def detect_document_title(lines: list[str]) -> str | None:
    """
    Heuristic title detection.

    Strategy:
      - Scan the first 5 non-empty lines.
      - Prefer a line that:
          • is NOT a numbered heading itself
          • is short (≤ 10 words)
          • has Title Case OR All Caps
          • appears before the first numbered section heading

    Falls back to the first non-empty line if no better candidate found.

    Returns:
        Title string or None if text is empty.
    """
    candidates = []
    first_numbered_heading_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Record where numbered headings start
        ok_num, _ = is_numbered_heading(stripped)
        if ok_num and first_numbered_heading_idx is None:
            first_numbered_heading_idx = i
            break

        word_count = len(stripped.split())
        if word_count <= 10:
            candidates.append((i, stripped))

    if not candidates:
        # Fall back: first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()
        return None

    # Prefer a Title Case or ALL-CAPS candidate among the early lines
    for idx, cand in candidates:
        words = cand.split()
        # Title Case: most words start with uppercase
        upper_words = sum(1 for w in words if w and w[0].isupper())
        if upper_words >= max(1, len(words) // 2):
            return cand

    # Fall back to first candidate
    return candidates[0][1]


# ---------------------------------------------------------------------------
# 5. Sections
# ---------------------------------------------------------------------------

def detect_sections(lines: list[str]) -> list[dict]:
    """
    Group lines into sections under their detected headings.

    Algorithm:
      - Walk lines top to bottom.
      - When a heading is detected, start a new section.
      - All non-heading lines until the next heading become the section content.
      - Lines before any heading are placed in a virtual "preamble" section
        with heading = None (these are usually the title / intro paragraph).

    Returns:
        List of dicts: {"heading": str|None, "content": [str]}
    """
    sections: list[dict] = []
    current_heading: str | None = None
    current_content: list[str] = []

    for line in lines:
        stripped = line.strip()
        ok, heading_text = is_heading(stripped)

        if ok:
            # Save previous section
            if current_heading is not None or current_content:
                sections.append({
                    "heading": current_heading,
                    "content": [l for l in current_content if l.strip()],
                })
            current_heading = heading_text
            current_content = []
        else:
            if stripped:
                current_content.append(stripped)

    # Flush last section
    if current_heading is not None or current_content:
        sections.append({
            "heading": current_heading,
            "content": [l for l in current_content if l.strip()],
        })

    return sections


# ---------------------------------------------------------------------------
# 6. Bullet lists
# ---------------------------------------------------------------------------

def detect_bullet_lists(lines: list[str]) -> list[list[str]]:
    """
    Find runs of consecutive bullet list items.

    Supports: -  •  *  ◦

    Returns:
        List of groups; each group is a list of item text strings.
    """
    lists: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        m = _RE_BULLET.match(line)
        if m:
            current.append(m.group(1).strip())
        else:
            if current:
                lists.append(current)
                current = []

    if current:
        lists.append(current)

    return lists


# ---------------------------------------------------------------------------
# 7. Numbered lists
# ---------------------------------------------------------------------------

def detect_numbered_lists(lines: list[str]) -> list[list[str]]:
    """
    Find runs of consecutive numbered list items.

    Supports: 1.  2)  a.  b)  i.  ii.  etc.

    NOTE: Numbered *section headings* (e.g. "1. Introduction") are excluded
    because they match is_numbered_heading() first.  Only lines that are
    NOT section headings are scanned here.

    Returns:
        List of groups; each group is a list of item text strings.
    """
    lists: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        # Skip lines that are section headings
        ok_heading, _ = is_numbered_heading(line.strip())
        if ok_heading:
            if current:
                lists.append(current)
                current = []
            continue

        m = _RE_NUMBERED_LIST.match(line)
        if m:
            current.append(m.group(1).strip())
        else:
            if current:
                lists.append(current)
                current = []

    if current:
        lists.append(current)

    return lists


# ---------------------------------------------------------------------------
# 8. Paragraphs
# ---------------------------------------------------------------------------

def detect_paragraphs(lines: list[str]) -> list[str]:
    """
    Identify paragraph blocks from the text.

    Strategy:
      - Group consecutive non-empty, non-heading lines into a block.
      - A heading line acts as a paragraph boundary (like a blank line).
      - A block qualifies as a paragraph if:
          * it contains at least _PARA_MIN_WORDS words total
          * every line is NOT a bullet/numbered list item

    This approach handles OCR text that has no blank lines between sections
    by using heading detection as the primary block separator.

    Returns:
        List of paragraph strings (each may span multiple original lines).
    """
    paragraphs: list[str] = []
    current_block: list[str] = []

    def flush():
        if not current_block:
            return
        block_text = " ".join(current_block)
        word_count = len(block_text.split())

        # Exclude if every line is a bullet or numbered-list item
        all_list = all(
            _RE_BULLET.match(l) or _RE_NUMBERED_LIST.match(l)
            for l in current_block
        )
        if all_list:
            return

        if word_count >= _PARA_MIN_WORDS:
            paragraphs.append(block_text)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Blank line — flush current block
            flush()
            current_block = []
        else:
            ok_h, _ = is_heading(stripped)
            if ok_h:
                # Heading line — flush current block, do NOT add heading to block
                flush()
                current_block = []
            else:
                current_block.append(stripped)

    flush()
    return paragraphs


# ---------------------------------------------------------------------------
# 9. Document statistics
# ---------------------------------------------------------------------------

def calculate_document_statistics(
    raw_text: str,
    sections: list[dict],
    paragraphs: list[str],
    bullet_lists: list[list[str]],
    numbered_lists: list[list[str]],
) -> dict:
    """
    Calculate basic document-level statistics.

    Returns:
        dict with character_count, word_count, line_count,
        section_count, paragraph_count, bullet_list_count,
        numbered_list_count.
    """
    stripped_text = raw_text.strip()
    lines = [l for l in stripped_text.splitlines() if l.strip()]

    # Count only sections that have an actual heading (not preamble)
    named_sections = [s for s in sections if s.get("heading")]

    return {
        "character_count":    len(stripped_text),
        "word_count":         len(stripped_text.split()),
        "line_count":         len(lines),
        "section_count":      len(named_sections),
        "paragraph_count":    len(paragraphs),
        "bullet_list_count":  len(bullet_lists),
        "numbered_list_count": len(numbered_lists),
    }


# ---------------------------------------------------------------------------
# 10. Master analysis function
# ---------------------------------------------------------------------------

def analyze_document_structure(text_path: str | Path) -> dict | None:
    """
    Run the full structural analysis pipeline on the extracted text file.

    Args:
        text_path: Path to data/output/extracted_text.txt

    Returns:
        A structured dict, or None if the file could not be loaded.
    """
    raw_text = load_extracted_text(text_path)
    if raw_text is None:
        return None

    lines = clean_text(raw_text)

    title         = detect_document_title(lines)
    sections      = detect_sections(lines)
    bullet_lists  = detect_bullet_lists(lines)
    numbered_lists = detect_numbered_lists(lines)
    paragraphs    = detect_paragraphs(lines)
    statistics    = calculate_document_statistics(
        raw_text, sections, paragraphs, bullet_lists, numbered_lists
    )

    return {
        "document_title":  title,
        "sections":        sections,
        "bullet_lists":    bullet_lists,
        "numbered_lists":  numbered_lists,
        "paragraphs":      paragraphs,
        "statistics":      statistics,
        "analysis_notes": (
            "Heuristic-based structural analysis. "
            "Results depend on OCR quality and document formatting. "
            "No semantic understanding is performed."
        ),
    }


# ---------------------------------------------------------------------------
# 11. Save report
# ---------------------------------------------------------------------------

def save_structure_report(structure: dict, output_dir: str | Path) -> Path | None:
    """
    Save the document structure analysis to data/output/document_structure.json.

    Args:
        structure:  Dict returned by analyze_document_structure().
        output_dir: Path to the output directory.

    Returns:
        Path to the saved file, or None on failure.
    """
    output_path = Path(output_dir) / "document_structure.json"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=4, ensure_ascii=False)
        print(f"  Saved structure report to: {output_path.absolute()}")
        return output_path
    except Exception as exc:
        logger.error("Failed to save document structure report: %s", exc)
        print(f"  [Step 10] Error saving structure report: {exc}")
        return None
