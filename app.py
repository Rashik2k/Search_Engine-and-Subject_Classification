import streamlit as st
from crawler import Crawler
from indexer import Indexer
from query_processor import QueryProcessor
import pickle
import re
import nltk
import os
import subprocess
import sys

# Load necessary NLTK components
nltk.download('wordnet')
nltk.download('omw-1.4')
lemmatizer = nltk.WordNetLemmatizer()

# Constants - Define key file paths and URLs
BASE_URL = "https://pureportal.coventry.ac.uk/"
DATA_FILE = "publications.json"
INDEX_FILE = "inverted_index.json"
MODEL_FILE = "text_clf.sav"
VECTORIZER_FILE = "text__vectorizer.sav"
TRAIN_SCRIPT = "model_train.py"

@st.cache_resource  # Cache model loading to optimize performance
def load_model():
    if not all(os.path.exists(f) for f in [MODEL_FILE, VECTORIZER_FILE]):
        print("Model files not found. Training model...")
        subprocess.run([sys.executable, TRAIN_SCRIPT], check=True)
    
    with open(MODEL_FILE, 'rb') as model_file, open(VECTORIZER_FILE, 'rb') as vectorizer_file:
        return pickle.load(model_file), pickle.load(vectorizer_file)

@st.cache_resource  # Cache initialization for efficiency
def initialize_components():
    crawler = Crawler(BASE_URL, data_file=DATA_FILE)
    crawler.load_data()

    if not crawler.publications:
        st.write("No existing data found. Starting crawl...")
        crawler.crawl_publications()

    indexer = Indexer(crawler.publications, index_file=INDEX_FILE)
    indexer.load_index()

    if not indexer.inverted_index:
        st.write("No existing index found. Building index...")
        indexer.build_index()

    return QueryProcessor(crawler.publications, indexer.inverted_index)

# Function to preprocess text
def text_tokenize_lemmatize(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text).lower()
    return ' '.join(lemmatizer.lemmatize(w) for w in nltk.tokenize.WhitespaceTokenizer().tokenize(text))

# Streamlit App
def main():
    st.image("coventry_logo.png", use_container_width=True)
    menu = ["Search Publications", "Subject Classification"]
    choice = st.sidebar.radio("Select an Option", menu)

    if choice == "Search Publications":
        st.title("Coventry University Publications Search Engine")
        st.subheader("Find publications by faculty members")
        query_processor = initialize_components()
        
        query = st.text_input("Enter your search query:", placeholder="e.g. Accounting, Economics, Finance, Business...")

        if query:
            relevant_docs = query_processor.search(query)
            if relevant_docs:
                st.write(f"Found {len(relevant_docs)} relevant publications:")
                for doc_id, score in relevant_docs:
                    pub = query_processor.publications[doc_id]
                    with st.expander(pub['title']):
                        st.write(f"**Authors:** {', '.join(author['name'] for author in pub['authors'])}")
                        st.write(f"**Year:** {pub['publication_year']}")
                        st.markdown(f"**[Publication Link]({pub['link']})**")
                        st.markdown(f"**[Author Profile]({', '.join(author['link'] for author in pub['authors'])})**")
                        st.write(f"**Relevance Score:** {score:.4f}")
            else:
                st.write("No relevant publications found. Try a different query.")

    elif choice == "Subject Classification":
        st.title("Subject Classification")
        st.subheader("Classify text into: Business, Health, or Politics")
        model, vectorizer = load_model()
        input_text = st.text_area("Enter text to classify:", height=150, placeholder="Type or paste your text here...")
        classify_button = st.button("Classify Text")

        if classify_button:
            if input_text:
                processed_text = text_tokenize_lemmatize(input_text)
                predicted_classification = model.predict(vectorizer.transform([processed_text]))[0]
                st.write(f"The text belongs to: **{predicted_classification}**")
            else:
                st.write("Please enter some text to classify.")

if __name__ == "__main__":
    main()