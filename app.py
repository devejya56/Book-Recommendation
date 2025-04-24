import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv('books.csv', on_bad_lines='skip')
    df['publisher'].fillna('Unknown', inplace=True)
    df['authors'].fillna('Unknown', inplace=True)
    df['combined_features'] = df['title'].astype(str) + " " + df['authors'].astype(str) + " " + df['publisher'].astype(str)
    return df

@st.cache_data
def calculate_similarity(df):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_books(title, cosine_sim, df):
    try:
        # Attempt to find the exact title
        idx = df[df['title'] == title].index[0]
    except IndexError:
        try:
            # If exact title not found, try a partial match
            idx = df[df['title'].str.contains(title, case=False)].index[0]  # case=False for case-insensitive search
        except (IndexError, KeyError):  # Handle KeyError as well
            st.error(f"Book '{title}' not found.")
            return None

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    book_indices = [i[0] for i in sim_scores]
    return df['title'].iloc[book_indices]


# Streamlit App
def main():
    st.title("Book Recommendation System")

    df = load_data()
    cosine_sim = calculate_similarity(df)

    book_title = st.text_input("Enter a book title:")

    if st.button("Recommend"):
        if book_title:
            recommendations = recommend_books(book_title, cosine_sim, df)
            if recommendations is not None:
                st.write(f"Books similar to '{book_title}':")
                for i, book in enumerate(recommendations):
                    st.write(f"{i+1}. {book}")
        else:
            st.warning("Please enter a book title.")


if __name__ == "__main__":
    main()
