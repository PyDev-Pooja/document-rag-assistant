"""Golden test-case template for the application."""

TEST_CASES = [
    {
        'question': 'What is the annual leave entitlement?',
        'expected_answer': '',
        'expected_chunk_ids': [],
        'expected_document_ids': [],
        'should_refuse': False,
    },
    {
        'question': 'Who is the CEO?',
        'expected_answer': '',
        'expected_chunk_ids': [],
        'expected_document_ids': [],
        'should_refuse': True,
    },
]
