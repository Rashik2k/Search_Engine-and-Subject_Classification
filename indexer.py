from collections import defaultdict
from utils import preprocess_text
import json

class Indexer:
    """
    A class to build, save, and load an inverted index for efficient text search.
    """

    def __init__(self, publications, index_file="inverted_index.json"):
        """
        Initialize the Indexer.

        :param publications: List of dictionaries containing document metadata (e.g., titles).
        :param index_file: Name of the file where the inverted index will be stored.
        """
        self.publications = publications  # Store the list of publications
        self.index_file = index_file  # Define the index file name
        self.inverted_index = defaultdict(list)  # Dictionary to store the inverted index

    def build_index(self):
        """
        Build the inverted index from the provided publications.

        The index maps tokens (words) to lists of document IDs containing those tokens.
        """
        print("Building inverted index...")

        # Iterate over all publications and extract tokens from their titles
        for doc_id, pub in enumerate(self.publications):
            title_tokens = preprocess_text(pub["title"])  # Preprocess the title to extract tokens
            for token in title_tokens:
                self.inverted_index[token].append(doc_id)  # Store document ID under the corresponding token

        # Save the constructed inverted index to a file
        self.save_index()

    def save_index(self):
        """
        Save the inverted index to a JSON file for later use.
        """
        with open(self.index_file, "w") as f:
            json.dump(self.inverted_index, f, indent=4)  # Save the index in a readable JSON format
        print(f"Inverted index built and saved to {self.index_file}.")

    def load_index(self):
        """
        Load the inverted index from a JSON file.

        If the index file does not exist, notify the user to build the index first.
        """
        try:
            with open(self.index_file, "r") as f:
                self.inverted_index = json.load(f)  # Load the inverted index from file
        except FileNotFoundError:
            print("No existing index found. Please build the index first.")  # Notify the user if the index is missing
