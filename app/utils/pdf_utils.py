"""
PDF text extraction utilities.
"""
import pdfplumber
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extract text from a PDF file."""
    try:
        logger.info(f"Extracting text from PDF: {pdf_path.name}")
        
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.debug(f"PDF has {total_pages} pages")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                
                if page_text:
                    text_content.append(page_text)
                    logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                else:
                    logger.warning(f"No text found on page {page_num}")
        
        full_text = "\n".join(text_content)
        logger.info(
            f"Successfully extracted {len(full_text)} characters "
            f"from {total_pages} pages"
        )
        
        return full_text
    
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {pdf_path.name}: {e}")
        raise


def extract_text_from_txt(txt_path: Path) -> Optional[str]:
    """
    Extract text content from a text file.
    
    Args:
        txt_path: Path to the text file
        
    Returns:
        File content as a string, or None if reading fails
        
    Raises:
        Exception: If file cannot be read
    """
    try:
        logger.info(f"Reading text file: {txt_path.name}")
        
        with open(txt_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
        
        logger.info(f"Successfully read {len(content)} characters from {txt_path.name}")
        return content
    
    except Exception as e:
        logger.error(f"Failed to read text file {txt_path.name}: {e}")
        raise


def extract_text(file_path: Path) -> str:
    """
    Extract text from a file (PDF or TXT).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is not supported
        Exception: If extraction fails
    """
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(file_path)
    elif suffix == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
