import re
import numpy as np
import pandas as pd

import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB

from sklearn.metrics import accuracy_score, confusion_matrix

import pickle

# Reading dataset from a CSV file
dataset = pd.read_csv('./dataset/nyt_article_data.csv', sep='\t')

# Merging the title and snippet into a single text column for processing
dataset['Text'] = dataset['Title'] + ' ' + dataset['Snippet']

# Replacing non-alphabetical characters with whitespace to clean the text
dataset['Text'] = dataset['Text'].str.replace('[^a-zA-Z]', ' ')

# Converting all text to lowercase to maintain uniformity
dataset['Text'] = [word.lower() for word in dataset['Text']]

# Applying tokenization to split text into individual words
dataset['Text'] = dataset['Text'].apply(nltk.tokenize.WhitespaceTokenizer().tokenize)

# Removing common stopwords (e.g., "the", "is", "and") to focus on meaningful words
dataset['Text'] = dataset['Text'].apply(lambda words: [word for word in words if not word in stopwords.words('english')])

# Initializing the WordNet lemmatizer for stemming words to their base forms
lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    # Lemmatizing words in the text to their base forms (e.g., "running" -> "run")
    return (lemmatizer.lemmatize(word) for word in text)

# Applying lemmatization to the text dataset
dataset['Text'] = dataset['Text'].apply(lemmatize_text)

# Creating a new column 'lematized_title' by joining the lemmatized words into a string
dataset['lematized_title'] = dataset['Text'].apply(lambda words: ' '.join(words))

# Preparing training data and target labels
train_data = dataset['lematized_title'].values
target = dataset['Category'].values

# Converting text data into numerical representations using TF-IDF Vectorization
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform(train_data)
Y_train = target

# Initializing and training a Naive Bayes classifier on the processed text data
naive_clf = MultinomialNB()
naive_clf.fit(X_train, Y_train)

# Saving the trained model and vectorizer to disk using pickle for future use
pickle.dump(naive_clf, open('text_clf.sav', 'wb'))
pickle.dump(vectorizer, open('text__vectorizer.sav', 'wb'))


