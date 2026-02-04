"""PDF text extraction utilities for resume screening"""

import io
from typing import Optional, Dict, Any
import tempfile
import os

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2
        PYPDF2_AVAILABLE = True
        PYPDF_AVAILABLE = False
    except ImportError:
        PYPDF2_AVAILABLE = False
        PYPDF_AVAILABLE = False

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class PDFExtractor:
    """Extract text content from PDF files"""
    
    def __init__(self):
        if not PDFPLUMBER_AVAILABLE and not PYPDF_AVAILABLE and not PYPDF2_AVAILABLE:
            raise ImportError("A PDF processing library is required. Install with: pip install pdfplumber pypdf")
    
    def extract_text_from_pdf(self, pdf_file_content: bytes) -> str:
        """
        Extract text from PDF file content
        
        Args:
            pdf_file_content: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        try:
            # Try pdfplumber first (most reliable)
            if PDFPLUMBER_AVAILABLE:
                return self._extract_with_pdfplumber(pdf_file_content)
            # Try newer pypdf library
            elif PYPDF_AVAILABLE:
                return self._extract_with_pypdf(pdf_file_content)
            # Fallback to PyPDF2
            elif PYPDF2_AVAILABLE:
                return self._extract_with_pypdf2(pdf_file_content)
            else:
                raise ImportError("No PDF extraction library available")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> str:
        """Extract text using pdfplumber library"""
        import pdfplumber
        
        text_content = []
        
        try:
            # Use BytesIO to avoid file system issues
            with io.BytesIO(pdf_content) as pdf_stream:
                with pdfplumber.open(pdf_stream) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            # Fallback to temporary file approach with better cleanup
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    temp_file_path = tmp_file.name
                    tmp_file.write(pdf_content)
                    tmp_file.flush()
                
                # Ensure file is closed before opening with pdfplumber
                with pdfplumber.open(temp_file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
            finally:
                # Clean up temporary file with retry logic
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except (PermissionError, FileNotFoundError):
                        # File might still be in use, try again after a brief delay
                        import time
                        time.sleep(0.1)
                        try:
                            os.unlink(temp_file_path)
                        except (PermissionError, FileNotFoundError):
                            logger.warning(f"Could not delete temporary file: {temp_file_path}")
        
        return '\n\n'.join(text_content)
    
    def _extract_with_pypdf(self, pdf_content: bytes) -> str:
        """Extract text using pypdf library (newer)"""
        from pypdf import PdfReader
        
        text_content = []
        
        with io.BytesIO(pdf_content) as pdf_stream:
            pdf_reader = PdfReader(pdf_stream)
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
        
        return '\n\n'.join(text_content)
    
    def _extract_with_pypdf2(self, pdf_content: bytes) -> str:
        """Extract text using PyPDF2 library"""
        import PyPDF2
        
        text_content = []
        
        with io.BytesIO(pdf_content) as pdf_stream:
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
        
        return '\n\n'.join(text_content)
    
    def extract_text_and_analyze(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Extract text and provide basic analysis
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted text and basic analysis
        """
        try:
            text = self.extract_text_from_pdf(pdf_content)
            
            # Basic analysis
            word_count = len(text.split())
            char_count = len(text)
            line_count = len(text.split('\n'))
            
            return {
                "text": text,
                "analysis": {
                    "word_count": word_count,
                    "character_count": char_count,
                    "line_count": line_count,
                    "estimated_pages": max(1, word_count // 250),  # Rough estimate
                    "extraction_successful": True
                }
            }
        except Exception as e:
            logger.error(f"Error in PDF text extraction and analysis: {e}")
            return {
                "text": "",
                "analysis": {
                    "word_count": 0,
                    "character_count": 0,
                    "line_count": 0,
                    "estimated_pages": 0,
                    "extraction_successful": False,
                    "error": str(e)
                }
            }

def create_pdf_extractor() -> PDFExtractor:
    """Factory function to create PDF extractor instance"""
    return PDFExtractor()