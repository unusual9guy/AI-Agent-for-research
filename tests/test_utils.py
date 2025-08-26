from tools import sanitize_topic_for_filename


def test_sanitize_topic_for_filename_basic():
    # Current sanitizer collapses spaces to single underscores and removes punctuation
    assert sanitize_topic_for_filename("AI: risks & rewards!") == "AI_risks_rewards"


def test_sanitize_topic_for_filename_spaces():
    assert sanitize_topic_for_filename("  Quantum  Computing   101  ") == "Quantum_Computing_101"


