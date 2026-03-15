import os
import pandas as pd

# Define the folder where all cleaned CSV files are stored
folder_path = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/"

# List all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

# Sort the files to maintain order (optional)
csv_files.sort()

# Combine all CSVs into one DataFrame
df_list = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)

# Save the Combined Data
combined_csv_path = os.path.join(folder_path, "Combined_Cleaned_Chats.csv")
combined_df.to_csv(combined_csv_path, index=False)

print(f"✅ Combined {len(csv_files)} CSV files into 'Combined_Cleaned_Chats.csv'")
print(f"📂 Total Rows: {len(combined_df)}")
