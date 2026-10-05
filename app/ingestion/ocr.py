"""OCR service with PaddleOCR and Tesseract fallback."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class OCRResult:
    text: str
    confidence: float
    lines: list[dict[str, Any]]
    provider: str


class OCRService:
    """Lazy-loading OCR wrapper.

    PaddleOCR 3.x is preferred. Tesseract can be used as an explicit fallback
    when the PaddleOCR stack is unavailable.
    """

    def __init__(self, provider: str = "paddle", language: str = "en") -> None:
        self.provider = provider.lower()
        self.language = language
        self._paddle = None

    def _get_paddle(self):
        if self._paddle is None:
            try:
                from paddleocr import PaddleOCR
            except ImportError as exc:
                raise RuntimeError(
                    "PaddleOCR is not installed. Install paddleocr and a compatible "
                    "PaddlePaddle runtime, or use provider='tesseract'."
                ) from exc
            self._paddle = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang=self.language,
                engine="paddle",
            )
        return self._paddle

    @staticmethod
    def _parse_paddle_result(result: Any) -> OCRResult:
        """Parse PaddleOCR 3.x result objects defensively."""
        text_lines: list[dict[str, Any]] = []
        scores: list[float] = []

        iterable = result if isinstance(result, (list, tuple)) else [result]
        for item in iterable:
            payload = getattr(item, "json", None)
            if callable(payload):
                payload = payload()
            if payload is None and isinstance(item, dict):
                payload = item
            if payload is None:
                payload = getattr(item, "res", None)
            if payload is None:
                continue

            if isinstance(payload, str):
                try:
                    import json
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if isinstance(payload, dict) and "res" in payload and isinstance(payload["res"], dict):
                payload = payload["res"]

            texts = payload.get("rec_texts", []) if isinstance(payload, dict) else []
            confs = payload.get("rec_scores", []) if isinstance(payload, dict) else []
            boxes = payload.get("rec_boxes", []) if isinstance(payload, dict) else []

            for index, text in enumerate(texts):
                score = float(confs[index]) if index < len(confs) else 1.0
                if index < len(boxes):
                    box_value = boxes[index]
                    box = box_value.tolist() if hasattr(box_value, "tolist") else box_value
                else:
                    box = None
                text_lines.append({"text": str(text), "confidence": score, "box": box})
                scores.append(score)

        joined = "\n".join(line["text"] for line in text_lines).strip()
        confidence = sum(scores) / len(scores) if scores else 0.0
        return OCRResult(joined, confidence, text_lines, "paddle")

    def _ocr_paddle(self, image: Path | Any) -> OCRResult:
        result = self._get_paddle().predict(str(image) if isinstance(image, Path) else image)
        return self._parse_paddle_result(result)

    def _ocr_tesseract(self, image: Path | Any) -> OCRResult:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("pytesseract and Pillow are required for Tesseract OCR") from exc

        pil_image = Image.open(image) if isinstance(image, Path) else image
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
        lines: list[dict[str, Any]] = []
        confidences: list[float] = []
        for text, conf in zip(data["text"], data["conf"]):
            text = text.strip()
            try:
                score = float(conf) / 100.0
            except (ValueError, TypeError):
                score = 0.0
            if text:
                lines.append({"text": text, "confidence": score})
                if score >= 0:
                    confidences.append(score)
        joined = " ".join(item["text"] for item in lines).strip()
        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return OCRResult(joined, confidence, lines, "tesseract")

    def extract(self, image: Path | Any) -> OCRResult:
        if self.provider == "tesseract":
            return self._ocr_tesseract(image)
        if self.provider != "paddle":
            raise ValueError(f"Unsupported OCR provider: {self.provider}")
        try:
            return self._ocr_paddle(image)
        except RuntimeError:
            raise
        except Exception as exc:
            try:
                return self._ocr_tesseract(image)
            except Exception as fallback_exc:
                raise RuntimeError("Both PaddleOCR and Tesseract OCR failed") from fallback_exc
