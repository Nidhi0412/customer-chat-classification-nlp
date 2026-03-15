import os
import json
import re
import pandas as pd
import spacy
from wordsegment import load, segment
import emoji
from fuzzywuzzy import fuzz

# Load SpaCy NLP model (English)
nlp = spacy.load("en_core_web_sm")

# Load word segmentation (for detecting shortened/misspelled words)
load()

# Define the root directory where JSON files are stored
root_directory = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Sep"

# Function to read all JSON files from all folders & subfolders
def extract_json_files(root_directory):
    json_files = []
    for foldername, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith(".json"):  # Only process JSON files
                json_files.append(os.path.join(foldername, filename))
    return json_files

# Get all JSON files
all_json_files = extract_json_files(root_directory)
print(f"✅ Found {len(all_json_files)} JSON files.")

# Function to extract and clean visitor messages
def extract_and_clean_visitor_messages(json_files):
    extracted_messages = []

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                chat_data = json.load(file)

                # Extract visitor messages
                for message in chat_data.get("messages", []):
                    if message.get("sender", {}).get("t") == "v":  # Only visitor messages
                        text = message.get("msg", "").strip()

                        # Ignore messages containing URLs or attachments
                        if "http" in text or "www." in text:
                            continue

                        # Clean the extracted message
                        cleaned_text = remove_unwanted_info(text)
                        if cleaned_text:  # Ensure message isn't empty after cleaning
                            extracted_messages.append(cleaned_text)

            except json.JSONDecodeError:
                print(f"⚠️ Error decoding JSON file: {file_path}")
    
    return extracted_messages

# Function to remove names, emojis, short forms, login details, and stylized words
def remove_unwanted_info(text):
    text = str(text).lower().strip()  # Convert to lowercase

    # Remove emojis
    text = emoji.replace_emoji(text, replace="")

        # Remove personal details
    text = re.sub(r'(?i)("?\s*name\s*:\s*[a-zA-Z\s]+"?\s*)', '', text)  # "Name : Kamal Advani"
    text = re.sub(r'(?i)("?\s*hotel\s*code\s*:\s*\d+"?\s*)', '', text)  # "Hotel code : 42441"
    text = re.sub(r'(?i)("?\s*email\s*:\s*[\w\.-]+@[\w\.-]+\.\w+"?\s*)', '', text)  # "Email : md@tulipsooty.com"
    text = re.sub(r'(?i)("?\s*phone\s*:\s*\d+"?\s*)', '', text)  # "Phone : 7094898989"
    text = re.sub(r'\b\d{5,}\b', '', text)  # Remove long numeric values (Hotel IDs, Booking Codes)
    text = re.sub(r'(?i)(username|login|password)\s*[:=\s]+\S+', '', text)  # Remove login credentials

    # Remove dates & timestamps (multiple formats)
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)  # Formats like 12/03/2024, 03-15-23
    text = re.sub(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s\d{1,2},?\s\d{2,4}\b', '', text)  # "March 15, 2023"
    text = re.sub(r'\b\d{1,2}:\d{2}\s?(?:am|pm)?\b', '', text)  # Time format like "10:30 AM"

    # Remove special characters except ".com" and double quotes
    text = re.sub(r'[^a-zA-Z\s".com]', '', text)

    # Remove numbers completely (hotel codes, IDs, phone numbers)
    text = re.sub(r'\b\d+\b', '', text)

    # Remove login-related words
    login_related_words = ["userid", "password", "login", "id"]
    text = " ".join([word for word in text.split() if word not in login_related_words])

    # Normalize stretched words (e.g., "hiiii" → "hi", "yesss" → "yes")
    text = normalize_stylized_words(text)

    # Remove dynamically detected names
    text = remove_names_using_ner(text)

    # Remove conversational noise
    if is_unwanted_conversation(text):
        return None  # Remove completely if message is not useful

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text if text else None  # Return None if text is empty after cleaning

# Function to normalize stylized words (e.g., "hellooo" → "hello")
def normalize_stylized_words(text):
    words = text.split()
    normalized_words = []
    for word in words:
        if len(set(word)) == 1:  # If a word is repeated characters (e.g., "ooooooh"), remove it
            continue
        segmented = segment(word)  # Use AI segmentation to correct short forms
        normalized_words.append("".join(segmented))  # Join segmented parts
    return " ".join(normalized_words)

# Function to remove names dynamically using NLP Named Entity Recognition (NER)
def remove_names_using_ner(text):
    doc = nlp(text)
    cleaned_tokens = [token.text for token in doc if token.ent_type_ != "PERSON"]
    return " ".join(cleaned_tokens)

# Function to remove common conversational noise using fuzzy matching
# Function to check if text contains common conversational phrases
def is_unwanted_conversation(text):
    # Convert text to lowercase
    text = text.lower().strip()

    # List of unwanted conversational words/phrases
    common_phrases = [
        "hi", "hello", "hii", "hiii", "ok", "okay", "okkk", "sure", "yes", "yess", "no", "nooo", "thanks", 
        "thank you", "done", "i will", "welcome", "good morning", "good evening", "good night", 
        "oh", "ohh", "ohhh", "umm", "hmm", "know", "are you there", "phone", "tapan"
    ]

    # Remove extra spaces and punctuation except .com and quotes
    text = re.sub(r'[^a-zA-Z\s".com]', '', text)

    # Tokenize text into words
    words = text.split()

    # 1️⃣ **Check if text is an exact match with a common phrase**
    if text in common_phrases:
        return True  # Remove the text

    # 2️⃣ **Check if any word in the text is in common phrases**
    if any(word in common_phrases for word in words):
        return True  # Remove text if a word is in the list

    # 3️⃣ **Use fuzzy matching for partial matches**
    for phrase in common_phrases:
        if fuzz.partial_ratio(text, phrase) > 85:  # 85% similarity threshold
            return True  # Remove text if it's close to unwanted words

    return False  # Keep the text

# Extract and clean visitor messages
cleaned_messages_list = extract_and_clean_visitor_messages(all_json_files)

# Convert to DataFrame
messages_df = pd.DataFrame(cleaned_messages_list, columns=["Cleaned Visitor Message"])

# Save extracted messages
output_file = "/home/nidhi/Langchain_tutorials/Chat_Classification/Chat_preprocessing/Cleaned_Visitor_Messages.csv"
messages_df.to_csv(output_file, index=False)

print(f"✅ AI-Powered Cleaning Completed! Cleaned messages saved to: {output_file}")
