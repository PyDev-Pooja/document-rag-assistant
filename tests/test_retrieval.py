from app.retrieval.hybrid_retriever import HybridRetriever


def test_score_normalization():
    scores = HybridRetriever._normalize({'a': 10.0, 'b': 20.0, 'c': 10.0})
    assert scores['b'] == 1.0
    assert scores['a'] == 0.0
