import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from collections import Counter
import re

# Load the input file containing the 1000 similar questions
input_file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Similar_Questions.csv"
df = pd.read_csv(input_file_path)

# Load Sentence-BERT Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert Questions to Embeddings
embeddings = model.encode(df["Matched Question"].astype(str), batch_size=128, show_progress_bar=True)

# Set Number of Clusters (Auto-Categorization)
num_clusters = 10  # You can adjust this number based on dataset size
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df["Cluster"] = kmeans.fit_predict(embeddings)

# Save Clustered Data
clustered_file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Clustered_Questions.csv"
df.to_csv(clustered_file_path, index=False)

print(f"✅ AI-based clustering completed & saved to: {clustered_file_path}")
