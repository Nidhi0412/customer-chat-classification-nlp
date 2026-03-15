import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

# Load FAISS Index & Stored Embeddings
index = faiss.read_index("/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Embeddings_FAISS.index")

# Load SBERT Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load **Entire Dataset** for Diverse Categorization
file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Combined_Cleaned_Chats.csv"
df = pd.read_csv(file_path)

# Convert ALL Questions into Embeddings
all_embeddings = model.encode(df["Visitor_Messages"].astype(str), batch_size=32, show_progress_bar=True)

# **Cluster the Entire Dataset (Not Just top_n Matches)**
num_clusters = 25  # Adjust based on dataset size
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df["Cluster"] = kmeans.fit_predict(all_embeddings)

# ---------------------------- #
# **🔹 Step 2: Assign Representative Questions per Cluster** #
# ---------------------------- #

# Function to get the most representative question per cluster
def get_representative_question(cluster_id):
    cluster_indices = df[df["Cluster"] == cluster_id].index
    cluster_embeddings = all_embeddings[cluster_indices]
    centroid = kmeans.cluster_centers_[cluster_id]
    
    # Find the closest question to the cluster centroid
    closest_index, _ = pairwise_distances_argmin_min([centroid], cluster_embeddings)
    return df.loc[cluster_indices[closest_index[0]], "Visitor_Messages"]

# Assign Representative Question as Category Name
df["Category"] = df["Cluster"].apply(get_representative_question)

# Save AI-Generated Categorized Data
if len(df) > 10000:  # Save a partial result after 10,000 rows
    temp_save_path = categorized_path.replace(".csv", "_partial.csv")
    df.to_csv(temp_save_path, index=False)
    print(f"⏳ Partial save completed at: {temp_save_path}")

