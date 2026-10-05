"""Custom grounding evaluation metrics."""
from __future__ import annotations

from statistics import mean
from app.grounding.evidence_checker import EvidenceChecker


def evaluate_grounding(cases: list[dict]) -> dict:
    checker = EvidenceChecker()
    scores = []
    supported_claim_rates = []
    for case in cases:
        report = checker.check(case.get('claims', []), case.get('evidence', []))
        scores.append(report.overall_score)
        if report.supports:
            supported_claim_rates.append(
                sum(s.supported for s in report.supports) / len(report.supports)
            )
    return {
        'cases': len(scores),
        'mean_grounding_score': mean(scores) if scores else 0.0,
        'supported_claim_rate': mean(supported_claim_rates) if supported_claim_rates else 0.0,
        'pass_rate_at_0_80': sum(score >= 0.80 for score in scores) / len(scores) if scores else 0.0,
    }
