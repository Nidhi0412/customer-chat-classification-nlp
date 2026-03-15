import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# File path (Make sure it's an Excel file)
file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Combined_Cleaned_Chats.xlsx"

# Load a specific sheet
df = pd.read_excel(file_path, sheet_name="Combined_Cleaned_Chats")

# Load Sentence-BERT Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate Embeddings (Batch Processing for Large Data)
embeddings = model.encode(df["Visitor_Messages"], batch_size=128, show_progress_bar=True)

# Save Embeddings for Reuse
np.save("/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Text_Embeddings_new.npy", embeddings)

print(f"✅ Stored {len(embeddings)} embeddings.")

# Create FAISS Index for Fast Retrieval
dimension = embeddings.shape[1]  # Embedding dimension
index = faiss.IndexFlatL2(dimension)  # L2 Distance (Euclidean)

# Add Embeddings to FAISS Index
index.add(embeddings)

# Save FAISS Index
faiss.write_index(index, "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Embeddings_FAISS_new.index")

print("✅ FAISS Index created & stored for fast searches.")
