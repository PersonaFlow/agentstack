import hashlib
from typing import Tuple

import tiktoken


def get_tiktoken_length(text: str) -> int:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def check_content_is_useful(
    document_content: str,
    min_word_count: int = 10,
    max_number_ratio: float = 0.3,
    information_density_ratio: float = 0.5,
    max_density_word_count: int = 200,
) -> Tuple[bool, str]:
    words = document_content.split(" ")
    print(f"WORDS={len(words)}")
    if document_content == "" or not words or not len(words):
        return False, "No words in content"

    # Check min word length
    word_count = len(words)
    if word_count < min_word_count:
        return False, f"word_count={word_count} < threshold={min_word_count}"

    # Check information density
    density_ratio = len(set(words)) / len(words)
    if (
        word_count < max_density_word_count
        and density_ratio < information_density_ratio
    ):
        return (
            False,
            f"density_ratio={density_ratio} < threshold={information_density_ratio}",
        )

    # Check that this chunk is not full of useless numbers
    number_count = sum(word.replace(".", "").isdigit() for word in words)
    number_ratio = number_count / word_count if word_count > 0 else 0
    if number_ratio > max_number_ratio:
        return False, f"number_ratio={number_ratio} > threshold={max_number_ratio}"

    return True, "Document content passes checks."


def sentence_hash(sentence):
    """Create a hash for a sentence, ignoring whitespace and capitalization."""
    return hashlib.md5(sentence.strip().lower().encode()).hexdigest()


def deduplicate_chunk(chunk: str) -> str:
    # TODO: employ more advanced strategy here, perhaps with NLTK or Spacy
    if not chunk:
        return chunk

    final_chunk = ""
    memory = {}
    for sentence in chunk.split("."):
        # end of chunk
        if not sentence.strip():
            final_chunk += "."
            continue
        hash_value = sentence_hash(sentence.strip())
        if hash_value in memory:
            continue
        final_chunk += f".{sentence}" if final_chunk else sentence
        memory[hash_value] = 1

    return final_chunk
