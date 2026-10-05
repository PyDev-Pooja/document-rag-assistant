"""Optional RAGAS adapter."""
from __future__ import annotations


def run_ragas(cases: list[dict]) -> dict:
    try:
        import ragas  # noqa: F401
    except ImportError:
        return {'available': False, 'cases': len(cases), 'message': 'Install ragas to enable RAGAS evaluation.'}
    return {
        'available': True,
        'cases': len(cases),
        'message': 'RAGAS is installed; bind the project dataset to the metrics required by your installed RAGAS version.',
    }
