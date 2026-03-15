# Configuration Guide

This guide explains how to configure the Chat Classification system for your environment.

## 📋 Table of Contents

- [Environment Setup](#environment-setup)
- [File Paths Configuration](#file-paths-configuration)
- [Model Configuration](#model-configuration)
- [Database Configuration](#database-configuration)
- [Parameter Tuning](#parameter-tuning)
- [Security Best Practices](#security-best-practices)

---

## 🔧 Environment Setup

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# .env file (DO NOT commit this to Git!)

# Database Configuration
MYSQL_HOST=your_database_host
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database_name

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional: Model Configuration
SENTENCE_BERT_MODEL=all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm

# Optional: Processing Configuration
BATCH_SIZE=128
NUM_CLUSTERS=30
TOP_N_SIMILAR=1000
```

### 2. Load Environment Variables

Add to your Python scripts:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
db_host = os.getenv('MYSQL_HOST')
api_key = os.getenv('OPENAI_API_KEY')
```

---

## 📁 File Paths Configuration

### Extract_visitor_q.py

```python
# Input: Directory containing JSON chat files
root_directory = "/path/to/your/json/chat/files"

# Output: Where to save cleaned messages
output_file = "/path/to/output/Cleaned_Visitor_Messages.csv"
```

**Example Structure:**
```
/data/
  ├── chats/
  │   ├── 2024-01/
  │   │   ├── chat_001.json
  │   │   ├── chat_002.json
  │   └── 2024-02/
  │       ├── chat_003.json
  └── processed/
      └── Cleaned_Visitor_Messages.csv
```

### merging_csv.py

```python
# Input: Folder containing multiple CSV files
folder_path = "/path/to/csv/files"

# Output: Combined CSV file (saved in same folder)
# Output filename: Combined_Cleaned_Chats.csv
```

### Faiss_embedding.py

```python
# Input: Combined chat data
file_path = "/path/to/Combined_Cleaned_Chats.xlsx"  # or .csv

# Outputs:
embeddings_path = "/path/to/Text_Embeddings.npy"
faiss_index_path = "/path/to/Embeddings_FAISS.index"
```

### Faiss_similar_search.py

```python
# Inputs:
faiss_index = "/path/to/Embeddings_FAISS.index"
chat_data = "/path/to/Combined_Cleaned_Chats.csv"

# Output:
output_path = "/path/to/Similar_Questions.csv"
```

### Clustering Scripts

```python
# Faiss_cluster_questions.py
embeddings_path = "/path/to/Text_Embeddings.npy"
chat_data = "/path/to/Combined_Cleaned_Chats.csv"
output_clustered = "/path/to/Clustered_Questions.csv"
output_summary = "/path/to/Cluster_Summary.csv"

# generate_name_cat.py
input_file = "/path/to/Similar_Questions.csv"
output_file = "/path/to/AI_Categorized_Questions.csv"
```

---

## 🤖 Model Configuration

### Sentence-BERT Models

Choose based on your requirements:

```python
from sentence_transformers import SentenceTransformer

# Option 1: Fast & Lightweight (Default)
model = SentenceTransformer("all-MiniLM-L6-v2")
# Dimensions: 384
# Speed: Very Fast
# Quality: Good

# Option 2: Better Quality
model = SentenceTransformer("all-mpnet-base-v2")
# Dimensions: 768
# Speed: Moderate
# Quality: Better

# Option 3: Multilingual
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# Dimensions: 384
# Speed: Fast
# Quality: Good (supports 50+ languages)

# Option 4: Best Quality (Slower)
model = SentenceTransformer("all-roberta-large-v1")
# Dimensions: 1024
# Speed: Slow
# Quality: Best
```

### SpaCy Models

```bash
# Small (Default)
python -m spacy download en_core_web_sm

# Medium (Better accuracy)
python -m spacy download en_core_web_md

# Large (Best accuracy)
python -m spacy download en_core_web_lg
```

In code:
```python
import spacy

# Load model
nlp = spacy.load("en_core_web_sm")  # or md, lg
```

---

## 🗄️ Database Configuration

### Option 1: Using Environment Variables (Recommended)

```python
import os
from langchain_community.utilities.sql_database import SQLDatabase

def get_db_connection():
    db_uri = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
        f"{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:"
        f"{os.getenv('MYSQL_PORT')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
    )
    return SQLDatabase.from_uri(db_uri)
```

### Option 2: Using Configuration File

Create `config.yaml`:

```yaml
database:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: your_database
  
openai:
  api_key: your_api_key
  model: gpt-4o
  temperature: 0
  
processing:
  batch_size: 128
  num_clusters: 30
  top_n_similar: 1000
```

Load in Python:

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

db_host = config['database']['host']
```

### Database Schema Customization

Edit the `MANUAL_SCHEMA` in `Claude_ai_saas.py`:

```python
MANUAL_SCHEMA = """
DATABASE SCHEMA:
1. `your_table_name` (Description)
   - `column1` (type) PRIMARY KEY
   - `column2` (type) - Description
   ...

RELATIONSHIPS:
- `table1` → `table2` (via `foreign_key`)
...

CONSTRAINTS:
- Your specific business rules
- Calculation formulas
...
"""
```

---

## ⚙️ Parameter Tuning

### Data Cleaning Parameters

**Extract_visitor_q.py:**

```python
# Fuzzy matching threshold (0-100)
# Higher = stricter matching
FUZZY_THRESHOLD = 85  # Recommended: 80-90

# Conversational noise phrases
common_phrases = [
    "hi", "hello", "ok", "thanks",
    # Add your domain-specific noise words
]

# Minimum message length (characters)
MIN_MESSAGE_LENGTH = 5  # Adjust based on your data
```

### Embedding Generation

**Faiss_embedding.py:**

```python
# Batch size for encoding
# Larger = faster but more memory
BATCH_SIZE = 128  # Options: 32, 64, 128, 256

# Show progress bar
show_progress_bar = True  # Set False for production
```

### Clustering Parameters

**Faiss_cluster_questions.py:**

```python
# Number of clusters
# Rule of thumb: sqrt(n_samples) to n_samples/100
num_clusters = 30

# For 1,000 messages: 10-20 clusters
# For 10,000 messages: 30-50 clusters
# For 100,000 messages: 100-200 clusters

# Random state for reproducibility
random_state = 42  # Keep same for consistent results
```

### Similarity Search

**Faiss_similar_search.py:**

```python
# Number of similar questions to retrieve
top_n = 1000  # Adjust based on needs

# Distance metric
# L2 (Euclidean) - Default, good for most cases
index = faiss.IndexFlatL2(dimension)

# Or use Inner Product (Cosine similarity)
# index = faiss.IndexFlatIP(dimension)
```

### LangChain Agent

**Claude_ai_saas.py:**

```python
# Model selection
llm = ChatOpenAI(
    model="gpt-4o",  # or "gpt-4", "gpt-3.5-turbo"
    temperature=0,   # 0 = deterministic, 1 = creative
    max_tokens=None  # None = no limit
)

# Memory configuration
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="history",
    max_token_limit=2000  # Adjust based on needs
)
```

---

## 🔒 Security Best Practices

### 1. Never Commit Sensitive Data

Create `.gitignore`:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Database credentials
config.yaml
secrets.json

# API keys
*.key
*.pem

# Data files
*.csv
*.xlsx
*.json
*.npy
*.index

# Virtual environment
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

### 2. Use Environment Variables

```bash
# Set in terminal (temporary)
export OPENAI_API_KEY="your_key_here"

# Or add to ~/.bashrc or ~/.zshrc (permanent)
echo 'export OPENAI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Encrypt Sensitive Files

```bash
# Encrypt configuration file
gpg -c config.yaml  # Creates config.yaml.gpg

# Decrypt when needed
gpg config.yaml.gpg  # Creates config.yaml
```

### 4. Use Secret Management Tools

```python
# AWS Secrets Manager
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

# Usage
api_key = get_secret('openai_api_key')
```

### 5. Validate Input Data

```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    # Remove SQL injection attempts
    dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', '--', ';']
    for pattern in dangerous_patterns:
        if pattern.lower() in text.lower():
            raise ValueError("Potentially dangerous input detected")
    return text
```

---

## 🎛️ Performance Optimization

### 1. Use GPU Acceleration

```python
# Install GPU version of FAISS
# pip install faiss-gpu

import faiss

# Check GPU availability
print(f"Number of GPUs: {faiss.get_num_gpus()}")

# Use GPU for indexing
res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatL2(dimension)
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)
```

### 2. Batch Processing

```python
# Process large datasets in chunks
def process_in_batches(data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        yield batch

# Usage
for batch in process_in_batches(df['messages']):
    embeddings = model.encode(batch)
    # Process embeddings
```

### 3. Caching

```python
import pickle
from functools import lru_cache

# Cache embeddings
def save_cache(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_cache(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Cache function results
@lru_cache(maxsize=1000)
def get_embedding(text):
    return model.encode([text])[0]
```

---

## 📊 Monitoring & Logging

### Setup Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_classification.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Processing started")
logger.warning("Low memory warning")
logger.error("Failed to process file")
```

### Track API Costs

```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = chatbot.invoke({"input": query})
    
    print(f"Tokens used: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost:.4f}")
```

---

## 🧪 Testing Configuration

### Test Database Connection

```python
def test_db_connection():
    try:
        db = get_db_connection()
        result = db.run("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
```

### Test Model Loading

```python
def test_model_loading():
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_text = "This is a test"
        embedding = model.encode([test_text])
        print(f"✅ Model loaded successfully. Embedding shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False
```

---

## 📝 Configuration Checklist

Before running the project:

- [ ] Created `.env` file with all credentials
- [ ] Installed all dependencies from `requirements.txt`
- [ ] Downloaded SpaCy model
- [ ] Configured file paths in all scripts
- [ ] Set up database connection
- [ ] Tested database connectivity
- [ ] Tested model loading
- [ ] Added `.gitignore` to exclude sensitive files
- [ ] Verified API keys are valid
- [ ] Set appropriate parameter values
- [ ] Configured logging
- [ ] Set up backup strategy for data

---

## 🆘 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Install missing packages
pip install -r requirements.txt
```

**2. SpaCy Model Not Found**
```bash
# Solution: Download model
python -m spacy download en_core_web_sm
```

**3. FAISS Installation Issues**
```bash
# Solution: Install specific version
pip install faiss-cpu==1.7.4
```

**4. Database Connection Timeout**
```python
# Solution: Increase timeout
db_uri = f"{connection_string}?connect_timeout=30"
```

**5. Out of Memory**
```python
# Solution: Reduce batch size
batch_size = 32  # Instead of 128
```

---

## 📚 Additional Resources

- [Sentence-BERT Documentation](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [LangChain Documentation](https://python.langchain.com/)
- [SpaCy Documentation](https://spacy.io/)

---

**Need Help?** Open an issue in the repository with:
- Your configuration details (without sensitive data)
- Error messages
- Steps to reproduce the issue
