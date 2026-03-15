import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

# Load the input file containing 1000 similar questions
input_file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Similar_Questions.csv"
df = pd.read_csv(input_file_path)

# Load Sentence-BERT Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert Questions to Embeddings
embeddings = model.encode(df["Matched Question"].astype(str), batch_size=128, show_progress_bar=True)

# Set Number of Clusters (Auto-Categorization)
num_clusters = 25  # Adjust based on dataset size
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df["Cluster"] = kmeans.fit_predict(embeddings)

# ---------------------------- #
# **🔹 Step 2: Assign Category Names from Clusters** #
# ---------------------------- #

# Function to get representative question for each cluster
def get_representative_question(cluster_id):
    cluster_indices = df[df["Cluster"] == cluster_id].index
    cluster_embeddings = embeddings[cluster_indices]
    centroid = kmeans.cluster_centers_[cluster_id]
    
    # Find the closest question to the cluster centroid
    closest_index, _ = pairwise_distances_argmin_min([centroid], cluster_embeddings)
    
    return df.loc[cluster_indices[closest_index[0]], "Matched Question"]

# Assign Representative Question as Category Name
df["Category"] = df["Cluster"].apply(get_representative_question)

# Save AI-Generated Categorized Data
categorized_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/AI_Categorized_Questions.csv"
df.to_csv(categorized_path, index=False)

print(f"✅ AI-generated categorized questions saved to: {categorized_path}")
