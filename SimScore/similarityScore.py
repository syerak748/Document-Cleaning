from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Define the texts to compare
texts = ["This is a sample text.", "This is a simple text."]

# Create a TF-IDF vectorizer and transform the texts into TF-IDF vectors
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(texts)

# Compute the cosine similarity between the first and second text
similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

# Print the similarity score
print(f"Similarity score with sklearn: {similarity[0][0]}")

# Extract the feature names (terms)
feature_names = vectorizer.get_feature_names_out()

# Convert the TF-IDF vectors to a DataFrame for better visualization
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=['Text1', 'Text2'], columns=feature_names).T
print("\nTF-IDF Matrix:")
print(tfidf_df)

# Highlight differences
differences = tfidf_df.T.diff().iloc[1].abs().sort_values(ascending=False)
print("\nTerm Discrepancies (sorted by absolute difference):")
print(differences)