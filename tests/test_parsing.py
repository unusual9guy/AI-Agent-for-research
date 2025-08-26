import json

from main import (
    _extract_brace_balanced_json,
    _extract_json_from_code_fences,
    _try_parse_json_candidates,
    _markdown_fallback,
    _chunk_text,
    ResearchResponse,
)


def test_extract_brace_balanced_json_simple():
    text = "Intro {\"a\": 1, \"b\": {\"c\": 2}} outro"
    extracted = _extract_brace_balanced_json(text)
    assert extracted == '{"a": 1, "b": {"c": 2}}'


def test_extract_json_from_code_fences_json_block():
    text = """
Preamble
```json
{"x": 10, "y": 20}
```
Footer
"""
    extracted = _extract_json_from_code_fences(text)
    assert extracted is not None
    data = json.loads(extracted)
    assert data == {"x": 10, "y": 20}


def test_try_parse_json_candidates_prefers_fenced():
    text = "Before\n```json\n{\n  \"k\": \"v\"\n}\n```\nAfter"
    data = _try_parse_json_candidates(text)
    assert data == {"k": "v"}


def test_chunk_text_lengths():
    blob = "a" * 25050
    chunks = _chunk_text(blob, max_len=12000)
    assert len(chunks) == 3
    assert len(chunks[0]) == 12000
    assert len(chunks[1]) == 12000
    assert len(chunks[2]) == 1050


def test_markdown_fallback_builds_structured_response():
    md = """
# AI in Supply Chains

## Abstract
This is a short abstract.

## Introduction
This is an introduction section explaining the context and scope.

## Detailed Research
### Subtopic A
Lots of detailed content here.

### Subtopic B
More detailed content here as well.

## Conclusion
Key takeaways and next steps.
"""
    result = _markdown_fallback(md)
    assert isinstance(result, ResearchResponse)
    assert result.topic.startswith("AI in Supply Chains")
    assert result.introduction
    assert result.detailed_research
    assert result.conclusion

