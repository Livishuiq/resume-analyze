"""Unit tests for text_preprocessor module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.text_preprocessor import (
    clean_text,
    extract_ngrams,
    get_vocabulary,
    lemmatize,
    normalize_text,
    preprocess,
    remove_stopwords,
    tokenize,
)


class TestCleanText:
    def test_removes_urls(self):
        result = clean_text("Visit https://example.com for info")
        assert "https" not in result

    def test_removes_emails(self):
        result = clean_text("Contact me at john@example.com")
        assert "@" not in result

    def test_normalizes_whitespace(self):
        result = clean_text("Hello    World")
        assert "  " not in result

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_strips_leading_trailing(self):
        assert clean_text("  hello  ") == "hello"


class TestNormalizeText:
    def test_lowercase(self):
        result = normalize_text("Hello World")
        assert result == result.lower()

    def test_strips_whitespace(self):
        assert normalize_text("  hi  ") == "hi"


class TestTokenize:
    def test_splits_words(self):
        tokens = tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens

    def test_empty_string(self):
        result = tokenize("")
        assert isinstance(result, list)


class TestRemoveStopwords:
    def test_removes_common_stopwords(self):
        tokens = ["the", "a", "is", "python"]
        result = remove_stopwords(tokens)
        assert "the" not in result
        assert "a" not in result
        assert "python" in result

    def test_removes_domain_stopwords(self):
        tokens = ["experience", "python", "years"]
        result = remove_stopwords(tokens)
        assert "experience" not in result
        assert "python" in result


class TestLemmatize:
    def test_lemmatizes_plural(self):
        result = lemmatize(["developers"])
        assert "developer" in result

    def test_lemmatizes_verb(self):
        result = lemmatize(["running"])
        assert result[0] in {"run", "running"}  # NLTK lemmatizer behavior

    def test_preserves_unknown(self):
        result = lemmatize(["python"])
        assert "python" in result


class TestPreprocess:
    def test_returns_list(self):
        result = preprocess("Python developer with 5 years experience")
        assert isinstance(result, list)

    def test_no_stopwords_by_default(self):
        result = preprocess("the quick brown fox")
        assert "the" not in result

    def test_technical_terms_preserved(self):
        result = preprocess("experienced python developer")
        assert "python" in result

    def test_with_stopwords_when_disabled(self):
        result = preprocess("the python", remove_stops=False)
        assert "the" in result


class TestExtractNgrams:
    def test_bigrams(self):
        tokens = ["machine", "learning", "engineer"]
        bigrams = extract_ngrams(tokens, 2)
        assert "machine learning" in bigrams
        assert "learning engineer" in bigrams

    def test_empty_list(self):
        result = extract_ngrams([], 2)
        assert result == []


class TestGetVocabulary:
    def test_returns_set(self):
        result = get_vocabulary("Python developer")
        assert isinstance(result, set)

    def test_contains_python(self):
        result = get_vocabulary("Python developer machine learning")
        assert "python" in result
