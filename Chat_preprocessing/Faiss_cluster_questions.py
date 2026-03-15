import pandas as pd
import numpy as np
import faiss
from sklearn.cluster import KMeans
from collections import Counter

# Load FAISS Embeddings (Fix: Allow Pickle)
embeddings_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Text_Embeddings.npy"
embeddings = np.load(embeddings_path, allow_pickle=True)  # ✅ FIXED

# Load Chat Data
file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Combined_Cleaned_Chats.csv"
df = pd.read_csv(file_path)


# Set Number of Clusters (Optimal: 10-20)
num_clusters = 30
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df["Cluster"] = kmeans.fit_predict(embeddings)

# Save Clustered Data
clustered_csv_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Clustered_Questions.csv"
df.to_csv(clustered_csv_path, index=False)

print(f"✅ Clustering completed & saved to: {clustered_csv_path}")

# ---------------------------- #
# **🔹 Step 2: Generate Cluster Summary** #
# ---------------------------- #

# Find Most Common Questions per Cluster
cluster_summary = df.groupby("Cluster")["Visitor_Messages"].apply(lambda x: Counter(x).most_common(3)).reset_index()

# Save Summary
summary_csv_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Cluster_Summary.csv"
cluster_summary.to_csv(summary_csv_path, index=False)

print(f"✅ Cluster summary saved to: {summary_csv_path}")
