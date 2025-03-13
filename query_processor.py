from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import preprocess_text

class QueryProcessor:
    """
    A class to process search queries using an inverted index and rank relevant documents using TF-IDF and cosine similarity.
    """

    def __init__(self, publications, inverted_index):
        """
        Initialize the QueryProcessor.

        :param publications: Dictionary containing document metadata
        :param inverted_index: Dictionary mapping tokens to sets of document IDs.
        """
        self.publications = publications
        self.inverted_index = inverted_index

    def search(self, query):
        """
        Search for documents relevant to the given query.

        :param query: User input query string.
        :return: List of tuples (document_id, similarity_score), sorted in descending order of relevance.
        """
        # Preprocess the query (e.g., tokenization, stopword removal, stemming)
        query_tokens = preprocess_text(query)
        relevant_docs = set()  # Set to store document IDs containing query tokens

        # Identify documents containing query tokens using the inverted index
        for token in query_tokens:
            if token in self.inverted_index:
                relevant_docs.update(self.inverted_index[token])

        # If relevant documents are found, rank them using TF-IDF and cosine similarity
        if relevant_docs:
            # Extract document titles for TF-IDF vectorization
            documents = [self.publications[doc_id]["title"] for doc_id in relevant_docs]

            # Initialize TF-IDF vectorizer
            vectorizer = TfidfVectorizer()

            # Convert documents into TF-IDF feature vectors
            doc_vectors = vectorizer.fit_transform(documents)

            # Transform the query into a TF-IDF vector
            query_vector = vectorizer.transform([query])

            # Compute cosine similarity between the query and document vectors
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()

            # Pair document IDs with their similarity scores
            ranked_docs = [(doc_id, score) for doc_id, score in zip(relevant_docs, similarities)]

            # Sort documents by similarity score in descending order
            ranked_docs.sort(key=lambda x: x[1], reverse=True)

            return ranked_docs  # Return ranked results

        else:
            return []  # Return an empty list if no relevant documents are found
