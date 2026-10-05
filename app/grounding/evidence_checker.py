"""Claim-to-evidence grounding scorer."""
from __future__ import annotations

import re
from dataclasses import dataclass

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'and', 'or',
    'in', 'on', 'for', 'with', 'by', 'as', 'at', 'from', 'this', 'that',
    'it', 'be', 'has', 'have', 'had', 'their',
    'section', 'describes', 'concerns', 'deals', 'with',
}


def tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(
            r'[A-Za-z0-9][A-Za-z0-9._/%:-]*',
            text.lower()
        )
        if token not in STOPWORDS and len(token) > 1
    }


@dataclass
class ClaimSupport:
    claim: str
    score: float
    supported: bool
    evidence_chunk_ids: list[str]


@dataclass
class GroundingReport:
    overall_score: float
    supports: list[ClaimSupport]


class EvidenceChecker:
    def check(self, claims: list[str], evidence) -> GroundingReport:
        if not claims:
            return GroundingReport(0.0, [])

        supports = []

        for claim in claims:
            c_tokens = tokens(claim)

            best = 0.0
            best_ids: list[str] = []

            for item in evidence:
                e_tokens = tokens(item.chunk.text)

                if not c_tokens:
                    continue

                coverage = len(c_tokens & e_tokens) / len(c_tokens)

                if coverage > best:
                    best = coverage
                    best_ids = [item.chunk.chunk_id]

            supports.append(
                ClaimSupport(
                    claim=claim,
                    score=best,
                    supported=best >= 0.50,
                    evidence_chunk_ids=best_ids,
                )
            )

        overall_score = (
            sum(x.score for x in supports) / len(supports)
            if supports
            else 0.0
        )

        return GroundingReport(
            overall_score=overall_score,
            supports=supports,
        )