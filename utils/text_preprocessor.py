"""
Text preprocessing utilities for resume analysis.
Handles tokenization, stopword removal, lemmatization, and normalization.
"""

import re
import string
from typing import List, Set

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download required NLTK data (safe to call multiple times)
def _download_nltk_data() -> None:
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


_download_nltk_data()

_lemmatizer = WordNetLemmatizer()
_STOP_WORDS: Set[str] = set(stopwords.words("english"))

# Domain-specific stopwords that add noise in resume/JD context
_DOMAIN_STOP_WORDS: Set[str] = {
    "experience", "years", "year", "work", "working", "worked",
    "strong", "excellent", "good", "great", "ability", "skills",
    "knowledge", "understanding", "proven", "seeking", "looking",
    "position", "role", "opportunity", "team", "company", "organization",
    "responsibilities", "duties", "required", "preferred", "plus",
    "etc", "including", "related", "relevant", "various",
}

ALL_STOP_WORDS = _STOP_WORDS | _DOMAIN_STOP_WORDS


def clean_text(text: str) -> str:
    """Remove noise characters, normalize whitespace."""
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)
    # Remove phone numbers
    text = re.sub(r"\+?\d[\d\s\-\(\)]{7,}\d", " ", text)
    # Remove special characters but keep hyphens in compound words
    text = re.sub(r"[^\w\s\-\+\#\.]", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_text(text: str) -> str:
    """Lowercase and clean text."""
    return clean_text(text.lower())


def tokenize(text: str) -> List[str]:
    """Tokenize text into words."""
    cleaned = normalize_text(text)
    try:
        tokens = word_tokenize(cleaned)
    except Exception:
        tokens = cleaned.split()
    return tokens


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove stopwords from token list."""
    return [t for t in tokens if t not in ALL_STOP_WORDS and len(t) > 1]


def lemmatize(tokens: List[str]) -> List[str]:
    """Lemmatize a list of tokens."""
    return [_lemmatizer.lemmatize(t) for t in tokens]


def preprocess(text: str, remove_stops: bool = True, do_lemmatize: bool = True) -> List[str]:
    """
    Full preprocessing pipeline.
    Returns a list of processed tokens.
    """
    tokens = tokenize(text)
    # Keep only alphabetic tokens and known tech tokens (e.g., "c++", "node.js")
    tokens = [t for t in tokens if re.match(r"^[a-z][a-z0-9\-\+\#\.]*$", t)]
    if remove_stops:
        tokens = remove_stopwords(tokens)
    if do_lemmatize:
        tokens = lemmatize(tokens)
    return tokens


def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extract n-grams from a token list."""
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def get_vocabulary(text: str) -> Set[str]:
    """Return unique preprocessed tokens from text."""
    return set(preprocess(text))
