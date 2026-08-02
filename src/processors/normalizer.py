import logging
import re

logger = logging.getLogger(__name__)

class TextNormalizer:
    def normalize(self, raw_text: str, ocr_text: str = "", stt_text: str = "") -> str:
        """
        Consolidates text outputs from different modalities, cleans formatting,
        and returns a normalized unified string representation.
        """
        parts = []
        
        # Add raw text if present
        if raw_text and str(raw_text).strip() and str(raw_text).lower() != "nan":
            parts.append(str(raw_text).strip())
            
        # Add OCR contents if present
        if ocr_text and str(ocr_text).strip():
            parts.append(f"[Image Text: {str(ocr_text).strip()}]")
            
        # Add STT transcript if present
        if stt_text and str(stt_text).strip():
            parts.append(f"[Voice Transcript: {str(stt_text).strip()}]")
            
        # Join sections with space
        combined = " ".join(parts).strip()
        
        # Clean up double spaces or tabs
        combined = re.sub(r'\s+', ' ', combined)
        
        logger.debug(f"Normalized message body generated: length={len(combined)}")
        return combined
