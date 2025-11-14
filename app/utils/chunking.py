"""
Text chunking utility.
"""
from typing import List, Tuple
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS
import logging

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Splits text into chunks with line tracking."""
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or SEPARATORS
    
    def chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Split text into chunks with line tracking."""
        if not text or not text.strip():
            return []
        lines = text.splitlines()
        total_lines = len(lines)
        logger.debug(f"Chunking text with {total_lines} lines")
        chunks = []
        current_position = 0
        iteration_count = 0
        max_iterations = len(text) * 2  # Safety limit
        while current_position < len(text) and iteration_count < max_iterations:
            iteration_count += 1
            
            # Calculate chunk end position
            chunk_end = min(current_position + self.chunk_size, len(text))
            
            # Extract chunk with potential extension to chunk_size
            chunk_text = text[current_position:chunk_end]
            
            # If not at end, try to find a good split point
            if chunk_end < len(text):
                chunk_text = self._find_split_point(
                    text[current_position:],
                    self.chunk_size
                )
            
            # Calculate line numbers for this chunk
            start_line, end_line = self._get_line_numbers(
                text, current_position, current_position + len(chunk_text)
            )
            
            # Store original length before stripping
            original_chunk_length = len(chunk_text)
            
            chunks.append((chunk_text.strip(), start_line, end_line))
            
            # Move to next chunk with overlap (use original length)
            progress = max(1, original_chunk_length - self.chunk_overlap)
            current_position += progress
            
            # Debug: ensure we're making forward progress
            if progress <= 0:
                logger.warning(f"Zero progress detected at position {current_position}, forcing +1")
                current_position += 1
        
        if iteration_count >= max_iterations:
            logger.warning(f"Chunking hit max iterations ({max_iterations}), stopping early")
        
        logger.info(f"Created {len(chunks)} chunks from {total_lines} lines")
        return chunks
    
    def _find_split_point(self, text: str, max_length: int) -> str:
        """
        Find the best split point using separator priority.
        
        Args:
            text: Text to split
            max_length: Maximum length for the chunk
            
        Returns:
            The chunk text up to the best split point
        """
        if len(text) <= max_length:
            return text
        
        # Try each separator in priority order
        for separator in self.separators:
            # Find the last occurrence of separator before max_length
            search_text = text[:max_length + len(separator)]
            last_sep_idx = search_text.rfind(separator)
            
            if last_sep_idx != -1 and last_sep_idx > 0:
                # Found a good split point
                return text[:last_sep_idx + len(separator)]
        
        # No separator found, hard split at max_length
        logger.debug(f"Hard split at {max_length} characters")
        return text[:max_length]
    
    def _get_line_numbers(
        self, full_text: str, start_pos: int, end_pos: int
    ) -> Tuple[int, int]:
        """
        Calculate line numbers for a character range.
        
        Args:
            full_text: The complete text
            start_pos: Starting character position
            end_pos: Ending character position
            
        Returns:
            Tuple of (start_line, end_line) - 1-indexed
        """
        # Count newlines before start_pos
        start_line = full_text[:start_pos].count('\n') + 1
        
        # Count newlines between start_pos and end_pos
        end_line = full_text[:end_pos].count('\n') + 1
        
        return start_line, end_line


def chunk_with_sections(
    text: str,
    section_pattern: str = None,
    chunk_size: int = CHUNK_SIZE
) -> List[Tuple[str, int, int, str]]:
    """
    Chunk text while tracking section headings.
    
    Args:
        text: Input text
        section_pattern: Regex pattern for section headings
        chunk_size: Target chunk size
        
    Returns:
        List of tuples: (chunk_text, start_line, end_line, section_title)
    """
    import re
    from app.config import SECTION_HEADING_PATTERN
    
    pattern = section_pattern or SECTION_HEADING_PATTERN
    chunker = SemanticChunker(chunk_size=chunk_size)
    
    # Get base chunks
    base_chunks = chunker.chunk_text(text)
    
    # Add section information
    lines = text.splitlines()
    chunks_with_sections = []
    
    for chunk_text, start_line, end_line in base_chunks:
        # Find the most recent section heading before this chunk
        section_title = ""
        for line_num in range(start_line - 1, 0, -1):
            if line_num <= len(lines):
                line = lines[line_num - 1]
                if re.match(pattern, line.strip()):
                    section_title = line.strip()
                    break
        
        chunks_with_sections.append((
            chunk_text, start_line, end_line, section_title
        ))
    
    return chunks_with_sections
