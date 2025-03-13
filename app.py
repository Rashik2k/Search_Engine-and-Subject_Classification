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


# Constants
BASE_URL = "https://pureportal.coventry.ac.uk/"
DATA_FILE = "publications.json"
INDEX_FILE = "inverted_index.json"
MODEL_FILE = "text_clf.sav"
VECTORIZER_FILE = "text__vectorizer.sav"
TRAIN_SCRIPT = "model_train.py"



@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(VECTORIZER_FILE):
        print("Model files not found. Training model...")
        subprocess.run([sys.executable, TRAIN_SCRIPT], check=True)

    with open(MODEL_FILE, 'rb') as model_file:
        model = pickle.load(model_file)
    
    with open(VECTORIZER_FILE, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    
    return model, vectorizer


# Initialize components
@st.cache_resource
def initialize_components():
    crawler = Crawler(BASE_URL, data_file=DATA_FILE)
    crawler.load_data()

    # Only crawl if no existing data is found
    if not crawler.publications:
        st.write("No existing data found. Starting crawl...")
        crawler.crawl_publications()

    indexer = Indexer(crawler.publications, index_file=INDEX_FILE)
    indexer.load_index()

    # Only build index if no existing index is found
    if not indexer.inverted_index:
        st.write("No existing index found. Building index...")
        indexer.build_index()

    query_processor = QueryProcessor(crawler.publications, indexer.inverted_index)
    return query_processor


# Function to preprocess text
def text_tokenize_lemmatize(text):
    text = re.sub('[^a-zA-Z]', ' ', text)
    lower_text = text.lower()
    tokenizer = nltk.tokenize.WhitespaceTokenizer()
    tokenized = tokenizer.tokenize(lower_text)
    lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in tokenized])
    return lemmatized_output


# Streamlit app

def main():
    # Display the Coventry University logo
    st.image("coventry_logo.png", use_column_width=True)  

    # Sidebar navigation menu
    menu = ["Search Publications", "Text Classification"]
    choice = st.sidebar.radio("Select an Option", menu)

    if choice == "Search Publications":
        st.title("Coventry University Publications Search Engine")
        st.subheader("Find publications by faculty members")

        # Initialize components
        query_processor = initialize_components()

        # Search input
        st.markdown("### Search for Publications")
        query = st.text_input("Enter your search query:", placeholder="e.g. Accounting, Economics, Finance, Business...")

        if query:
            # Perform search
            relevant_docs = query_processor.search(query)

            # Display results
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

    elif choice == "Text Classification":
        st.title("Text Classification")
        st.subheader("Classify text into: Business, Health, or Politics")

        model, vectorizer = load_model()

        # Input text area
        input_text = st.text_area("Enter text to classify:", height=150, placeholder="Type or paste your text here...")

        # Centering the button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Classify Text"):
                if input_text:
                    processed_text = text_tokenize_lemmatize(input_text)
                    vectorized_text = vectorizer.transform([processed_text])
                    predicted_classification = model.predict(vectorized_text)[0]
                    st.write(f"The text belongs to: **{predicted_classification}**")
                else:
                    st.write("Please enter some text to classify.")

if __name__ == "__main__":
    main()
