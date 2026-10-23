"""Search over the knowledge base articles in data/city_info/.

This is the "R" in RAG (retrieval-augmented generation): find the most
relevant articles, hand them to Claude, and Claude answers using them instead
of guessing.

Search method: TF-IDF + cosine similarity (same idea as the classifier).
Cosine similarity measures how much two vectors point the same way:
1 = same words in the same proportions, 0 = nothing in common.
No API calls, no vector database needed at this size (~20 articles).
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import config


class KnowledgeBase:
    def __init__(self, folder=config.CITY_INFO_DIR):
        self.articles = []
        for path in sorted(folder.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            text = path.read_text(encoding="utf-8")
            first_line = text.splitlines()[0]
            self.articles.append({
                "file": path.name,
                "title": first_line.lstrip("# ").strip(),
                "text": text,
            })

        # Learn the vocabulary of all articles, then turn each article into a vector.
        # Character chunks (like the classifier) beat whole words here: 85% vs 75%
        # right-article-first on eval/retrieval_questions.csv.
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.article_vectors = self.vectorizer.fit_transform([a["text"] for a in self.articles])

    def search(self, query, k=2):
        """Return the k most similar articles, each with a similarity score from 0 to 1."""
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.article_vectors)[0]

        ranked = sorted(zip(scores, self.articles), key=lambda pair: pair[0], reverse=True)
        results = []
        for score, article in ranked[:k]:
            results.append({
                "file": article["file"],
                "title": article["title"],
                "score": round(float(score), 3),
                "text": article["text"],
            })
        return results
