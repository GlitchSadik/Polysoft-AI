"""
Text processing utilities.
"""
import re
from typing import List
from app.config import SECTION_HEADING_PATTERN
import logging

logger = logging.getLogger(__name__)


def detect_section_headings(lines: List[str], pattern: str = None) -> List[tuple]:
    """Detect section headings in lines."""
    pattern = pattern or SECTION_HEADING_PATTERN
    headings = []
    for i, line in enumerate(lines, 1):
        if re.match(pattern, line.strip()):
            headings.append((i, line.strip()))
    logger.debug(f"Found {len(headings)} section headings")
    return headings


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def format_snippet(text: str, max_length: int = 200) -> str:
    """Create a display snippet from text."""
        max_length: Maximum snippet length
        
    Returns:
        Truncated text snippet
    """
    if len(text) <= max_length:
        return text
    
    snippet = text[:max_length].rsplit(' ', 1)[0]
    return snippet + "..."


def count_lines(text: str) -> int:
    """
    Count the number of lines in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of lines
    """
    if not text:
        return 0
    return len(text.splitlines())
