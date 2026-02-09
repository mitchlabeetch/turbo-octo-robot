"""Watermarking utilities for documents."""

from pathlib import Path
from datetime import datetime
from io import BytesIO
import mimetypes

# Try to import PyPDF2 for PDF watermarking, fall back to stub if not available
try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_WATERMARK_LIBS = True
except ImportError:
    HAS_WATERMARK_LIBS = False


def add_watermark_text(pdf_path: str, viewer_email: str, output_path: str) -> str:
    """
    Add watermark text to PDF with viewer email and timestamp.
    
    If watermarking libraries aren't available, returns the original path.
    In production, install PyPDF2 and reportlab.
    """
    if not HAS_WATERMARK_LIBS:
        # Fallback: return original if libraries unavailable
        return pdf_path
    
    try:
        # Create watermark
        watermark_text = f"CONFIDENTIAL - Viewed by {viewer_email} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        # Read original PDF
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
        
        # Create watermark PDF
        watermark_buffer = BytesIO()
        from reportlab.lib.units import inch
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.rotate(45)
        c.setFillAlpha(0.1)
        c.drawString(200, 100, watermark_text)
        c.save()
        watermark_buffer.seek(0)
        
        # Apply watermark to each page
        watermark_reader = PdfReader(watermark_buffer)
        watermark_page = watermark_reader.pages[0]
        
        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Write output
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    except Exception as e:
        # On any error, return original
        return pdf_path


def should_watermark(content_type: str) -> bool:
    """Check if document type should be watermarked."""
    return content_type in [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]


def get_watermark_status() -> dict:
    """Get information about watermarking capabilities."""
    return {
        'watermarking_enabled': HAS_WATERMARK_LIBS,
        'message': 'Watermarking ready' if HAS_WATERMARK_LIBS else 'PyPDF2 and reportlab not installed. Install with: pip install PyPDF2 reportlab'
    }
