import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load FAISS Index & Stored Embeddings
index = faiss.read_index("/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Embeddings_FAISS.index")

# Load SBERT Model (Important: This was missing!)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Chat Data
file_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Combined_Cleaned_Chats.csv"
df = pd.read_csv(file_path)


#  Function to Find Similar Questions & Save Results
def find_similar_questions(query, top_n=1000, save_path=None):
    query_embedding = model.encode([query])  # Convert query to embedding
    _, indices = index.search(query_embedding, top_n)  # Get top N closest matches

    # Extract matched questions
    matched_questions = df.iloc[indices[0]]["Visitor_Messages"].tolist()

    # Create DataFrame with Sr No, Matched Questions, and Rank
    results_df = pd.DataFrame({
        "Sr No": range(1, top_n + 1),
        "Matched Question": matched_questions
    })

    # Save to CSV if a save path is provided
    if save_path:
        results_df.to_csv(save_path, index=False)
        print(f"✅ Similar questions saved to: {save_path}")

    return results_df  # Return DataFrame

# Example: Find Similar Questions for "How to modify my booking?"
query = "How to modify my booking?"
save_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Similar_Questions.csv"
similar_questions_df = find_similar_questions(query, top_n=1000, save_path=save_path)

# ✅ Display DataFrame using Pandas (instead of ace_tools)
print(similar_questions_df.head())  # Show first 5 rows

