# Setup Guide

Complete step-by-step guide to set up and run the Chat Classification system.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **pip** package manager
- **Git** (for cloning the repository)
- **4GB+ RAM** (8GB+ recommended for large datasets)
- **OpenAI API key** (if using the database query agent)
- **MySQL database** (if using the database query agent)

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Chat_Classification.git
cd Chat_Classification
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

### 5. Test Installation

```bash
# Run test script
python test_setup.py
```

---

## 📦 Detailed Installation

### Step 1: System Requirements

#### Check Python Version

```bash
python --version
# Should be 3.8 or higher
```

#### Check pip Version

```bash
pip --version
# Should be 20.0 or higher
```

#### Update pip (if needed)

```bash
python -m pip install --upgrade pip
```

---

### Step 2: Install Core Dependencies

#### Install in Order

```bash
# 1. Install NumPy first (required by many packages)
pip install numpy>=1.23.0

# 2. Install data processing libraries
pip install pandas>=1.5.0 openpyxl>=3.0.0

# 3. Install NLP libraries
pip install spacy>=3.0.0
python -m spacy download en_core_web_sm

# 4. Install ML libraries
pip install scikit-learn>=1.0.0
pip install sentence-transformers>=2.2.0

# 5. Install FAISS (choose one)
# For CPU:
pip install faiss-cpu>=1.7.0

# For GPU (if you have CUDA):
pip install faiss-gpu>=1.7.0

# 6. Install text processing
pip install wordsegment>=1.3.0 emoji>=2.0.0
pip install fuzzywuzzy>=0.18.0 python-Levenshtein>=0.20.0

# 7. Install LangChain (if using database agent)
pip install langchain>=0.1.0
pip install langchain-openai>=0.0.5
pip install langchain-community>=0.0.20

# 8. Install database libraries (if using database agent)
pip install pymysql>=1.1.0 sqlalchemy>=2.0.0

# 9. Install OpenAI (if using database agent)
pip install openai>=1.0.0 tiktoken>=0.5.0

# 10. Install utilities
pip install python-dotenv>=1.0.0 tqdm>=4.65.0
```

---

### Step 3: Verify Installation

Create `test_setup.py`:

```python
#!/usr/bin/env python3
"""Test script to verify all dependencies are installed correctly."""

import sys

def test_imports():
    """Test if all required packages can be imported."""
    
    tests = {
        "NumPy": "import numpy",
        "Pandas": "import pandas",
        "SpaCy": "import spacy",
        "Sentence Transformers": "from sentence_transformers import SentenceTransformer",
        "FAISS": "import faiss",
        "scikit-learn": "from sklearn.cluster import KMeans",
        "FuzzyWuzzy": "from fuzzywuzzy import fuzz",
        "Emoji": "import emoji",
        "WordSegment": "from wordsegment import load, segment",
    }
    
    print("Testing package imports...\n")
    
    failed = []
    for name, import_statement in tests.items():
        try:
            exec(import_statement)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_spacy_model():
    """Test if SpaCy model is downloaded."""
    print("\nTesting SpaCy model...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ SpaCy model loaded successfully!")
        return True
    except OSError:
        print("❌ SpaCy model not found")
        print("Run: python -m spacy download en_core_web_sm")
        return False

def test_sentence_transformer():
    """Test if Sentence Transformer can load a model."""
    print("\nTesting Sentence Transformer...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_text = "This is a test"
        embedding = model.encode([test_text])
        print(f"✅ Sentence Transformer working! Embedding shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ Sentence Transformer error: {e}")
        return False

def test_faiss():
    """Test if FAISS is working."""
    print("\nTesting FAISS...")
    try:
        import faiss
        import numpy as np
        
        # Create a simple index
        dimension = 128
        index = faiss.IndexFlatL2(dimension)
        
        # Add some vectors
        vectors = np.random.random((10, dimension)).astype('float32')
        index.add(vectors)
        
        # Search
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, 5)
        
        print(f"✅ FAISS working! Found {len(indices[0])} results")
        return True
    except Exception as e:
        print(f"❌ FAISS error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Chat Classification System - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(test_imports())
    results.append(test_spacy_model())
    results.append(test_sentence_transformer())
    results.append(test_faiss())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Setup is complete.")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Run the test:

```bash
python test_setup.py
```

---

## ⚙️ Configuration

### 1. Create Environment File

Create `.env` file in the project root:

```bash
# Database Configuration (Optional - only if using database agent)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# OpenAI API (Optional - only if using database agent)
OPENAI_API_KEY=your_openai_api_key

# Processing Configuration
BATCH_SIZE=128
NUM_CLUSTERS=30
TOP_N_SIMILAR=1000

# Model Configuration
SENTENCE_BERT_MODEL=all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm
```

### 2. Update File Paths

Edit each Python script to update file paths:

**Extract_visitor_q.py:**
```python
# Line 17: Update to your data directory
root_directory = "/path/to/your/json/files"

# Line 163: Update output path
output_file = "/path/to/output/Cleaned_Visitor_Messages.csv"
```

**merging_csv.py:**
```python
# Line 5: Update folder path
folder_path = "/path/to/csv/files"
```

**Faiss_embedding.py:**
```python
# Line 8: Update input file
file_path = "/path/to/Combined_Cleaned_Chats.xlsx"

# Line 20: Update embeddings output
embeddings_path = "/path/to/Text_Embeddings.npy"

# Line 32: Update FAISS index output
index_path = "/path/to/Embeddings_FAISS.index"
```

---

## 🏃 Running the System

### Phase 1: Extract and Clean Messages

```bash
# Run extraction script
python Extract_visitor_q.py

# Expected output:
# ✅ Found 150 JSON files.
# ✅ AI-Powered Cleaning Completed! Cleaned messages saved to: ...
```

### Phase 2: Merge CSV Files

```bash
# Run merge script
python Chat_preprocessing/merging_csv.py

# Expected output:
# ✅ Combined 12 CSV files into 'Combined_Cleaned_Chats.csv'
# 📂 Total Rows: 45678
```

### Phase 3: Generate Embeddings

```bash
# Run embedding generation
python Chat_preprocessing/Faiss_embedding.py

# Expected output:
# Batches: 100%|████████████| 357/357 [02:15<00:00, 2.63it/s]
# ✅ Stored 45678 embeddings.
# ✅ FAISS Index created & stored for fast searches.
```

### Phase 4: Find Similar Questions

```bash
# Run similarity search
python Chat_preprocessing/Faiss_similar_search.py

# Expected output:
# ✅ Similar questions saved to: Similar_Questions.csv
```

### Phase 5: Cluster Questions

```bash
# Run clustering
python Chat_preprocessing/Faiss_cluster_questions.py

# Expected output:
# ✅ Clustering completed & saved to: Clustered_Questions.csv
# ✅ Cluster summary saved to: Cluster_Summary.csv
```

### Phase 6: Generate Categories

```bash
# Run categorization
python Chat_preprocessing/generate_name_cat.py

# Expected output:
# Batches: 100%|████████████| 8/8 [00:15<00:00, 1.92s/it]
# ✅ AI-generated categorized questions saved to: AI_Categorized_Questions.csv
```

### Optional: Run Database Agent

```bash
# Set environment variables
export OPENAI_API_KEY="your_key"
export MYSQL_HOST="your_host"
export MYSQL_USER="your_user"
export MYSQL_PASSWORD="your_password"
export MYSQL_DATABASE="your_database"

# Run chatbot
python Claude_ai_saas.py

# Expected output:
# 🛠️ Creating Hotel Agent...
# ✅ Database connection successful.
# ✅ Hotel Agent created successfully.
# ✅ Chatbot initialized successfully.
# 
# Hotel Reservation Assistant (type 'exit' to quit)
# -------------------------------------------------
# 
# You: 
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. ImportError: No module named 'X'

**Solution:**
```bash
pip install X
# or
pip install -r requirements.txt
```

#### 2. SpaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

#### 3. FAISS installation fails

**Solution:**
```bash
# Try specific version
pip install faiss-cpu==1.7.4

# Or use conda
conda install -c conda-forge faiss-cpu
```

#### 4. Out of memory error

**Solution:**
Reduce batch size in scripts:
```python
# In Faiss_embedding.py
batch_size = 32  # Instead of 128
```

#### 5. Database connection error

**Solution:**
```bash
# Test connection
mysql -h your_host -u your_user -p your_database

# Check firewall
sudo ufw allow 3306

# Verify credentials in .env
```

#### 6. Sentence Transformer download fails

**Solution:**
```python
# Download manually
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder="./models")
```

#### 7. Permission denied errors

**Solution:**
```bash
# Fix file permissions
chmod +x *.py
chmod -R 755 Chat_preprocessing/

# Or run with sudo (not recommended)
sudo python script.py
```

---

## 📊 Verifying Results

### Check Output Files

```bash
# List generated files
ls -lh Chat_preprocessing/results/

# View first few rows
head -n 5 Chat_preprocessing/results/Combined_Cleaned_Chats.csv

# Count rows
wc -l Chat_preprocessing/results/*.csv
```

### Validate Data Quality

```python
import pandas as pd

# Load results
df = pd.read_csv("Chat_preprocessing/results/AI_Categorized_Questions.csv")

# Check data
print(f"Total questions: {len(df)}")
print(f"Unique clusters: {df['Cluster'].nunique()}")
print(f"Unique categories: {df['Category'].nunique()}")

# View sample
print(df.head())
```

---

## 🎓 Next Steps

After successful setup:

1. **Explore the data**: Review generated CSV files
2. **Adjust parameters**: Fine-tune clustering and filtering
3. **Customize cleaning**: Add domain-specific filters
4. **Integrate with systems**: Use results in your applications
5. **Monitor performance**: Track processing times and quality

---

## 📚 Additional Resources

- [README.md](README.md) - Project overview
- [CONFIGURATION.md](CONFIGURATION.md) - Detailed configuration
- [EXAMPLE_DATA.md](EXAMPLE_DATA.md) - Sample data formats
- [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) - Visual workflow

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages carefully
3. Search existing GitHub issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information
   - Configuration (without sensitive data)

---

## ✅ Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] SpaCy model downloaded
- [ ] Environment file configured
- [ ] File paths updated in scripts
- [ ] Test script passed
- [ ] First extraction completed successfully
- [ ] Embeddings generated
- [ ] Clustering completed
- [ ] Results validated

---

**Congratulations!** 🎉 You're ready to use the Chat Classification system!
