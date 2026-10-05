from app.grounding.evidence_checker import EvidenceChecker
from app.ingestion.models import DocumentChunk, RetrievalResult


def test_claim_grounding():
    chunk = DocumentChunk(
        text='Employees are entitled to 25 days of annual leave.',
        document_id='d1',
        chunk_id='c1',
        filename='policy.pdf',
        page_number=14,
        section='Annual Leave',
    )
    report = EvidenceChecker().check(
        ['Employees are entitled to 25 days of annual leave.'],
        [RetrievalResult(chunk=chunk, score=1.0)],
    )
    assert report.overall_score >= 0.5
    assert report.supports[0].supported
