import re
from collections import Counter


def summarize(text, max_sentences=4):
    """
    Produce an extractive summary by ranking sentences
    according to the frequency of meaningful words.
    """

    if not text or not text.strip():
        return "No article text was available to summarize."

    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip().split()) >= 5
    ]

    if not sentences:
        return text[:500]

    stop_words = {
        "the", "a", "an", "and", "or", "but", "if", "then",
        "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "in", "on", "at", "by", "for", "from",
        "with", "as", "it", "its", "this", "that", "these",
        "those", "he", "she", "they", "them", "their", "his",
        "her", "we", "our", "you", "your", "i", "who", "which",
        "what", "when", "where", "how", "will", "would", "can",
        "could", "has", "have", "had", "not", "also", "than",
        "after", "before", "into", "about", "over", "under"
    }

    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    frequencies = Counter(
        word for word in words if word not in stop_words
    )

    if not frequencies:
        return " ".join(sentences[:max_sentences])

    max_frequency = max(frequencies.values())

    scores = []

    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(
            r"\b[a-zA-Z]{2,}\b", sentence.lower()
        )

        meaningful_words = [
            word for word in sentence_words
            if word not in stop_words
        ]

        if meaningful_words:
            score = sum(
                frequencies[word] / max_frequency
                for word in meaningful_words
            ) / len(meaningful_words)
        else:
            score = 0

        scores.append((index, score, sentence))

    ranked = sorted(
        scores,
        key=lambda item: item[1],
        reverse=True
    )[:max_sentences]

    # Restore the original order of selected sentences.
    ranked.sort(key=lambda item: item[0])

    return " ".join(item[2] for item in ranked)
