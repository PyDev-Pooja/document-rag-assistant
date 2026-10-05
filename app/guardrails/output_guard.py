"""Final output gate for claim grounding, citations and conflicts."""
from __future__ import annotations

from app.config import settings
from app.grounding.claim_extractor import extract_claims
from app.grounding.evidence_checker import EvidenceChecker
from app.grounding.citation_validator import CitationValidator
from app.grounding.conflict_detector import ConflictDetector
#from app.ingestion.models import RetrievalResult
from app.schemas.retrieval import RetrievalResult
from app.rag.generator import GroundedResponse
from app.guardrails.generation_guard import GenerationGuard


class OutputGuard:
    def __init__(self):
        self.generation_guard = GenerationGuard()
        self.evidence_checker = EvidenceChecker()
        self.citation_validator = CitationValidator()
        self.conflict_detector = ConflictDetector()

    def validate(self, response: GroundedResponse, evidence: list[RetrievalResult]) -> GroundedResponse:
        response = self.generation_guard.validate(response)
        if not response.claims:
            response.claims = extract_claims(response.answer)

        grounding = self.evidence_checker.check(response.claims, evidence)
        citations = self.citation_validator.validate(response.citations, evidence)
        conflicts = self.conflict_detector.detect(evidence)

        if grounding.overall_score < settings.min_grounding_score:
            response.grounded = False
            response.warning = (
                'The response did not meet the grounding threshold. '
                'Only evidence-supported information can be returned.'
            )
        elif not citations.allowed:
            response.grounded = False
            response.warning = citations.message
        else:
            response.grounded = True
            response.confidence = max(response.confidence, grounding.overall_score)
            if conflicts:
                response.warning = 'The retrieved evidence contains potentially conflicting factual values; verify the cited sources.'

        response.citations = citations.valid_citations or []
        return response
