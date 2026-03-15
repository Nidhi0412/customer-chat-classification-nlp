# Quick Start Guide

Get up and running with the Chat Classification system in under 10 minutes!

## ⚡ 5-Minute Setup

### 1. Install Python Dependencies

```bash
# Clone repository
git clone https://github.com/yourusername/Chat_Classification.git
cd Chat_Classification

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm
```

### 2. Prepare Your Data

```bash
# Create data directory
mkdir -p data/raw_chats

# Place your JSON chat files in data/raw_chats/
# Example structure:
# data/
#   └── raw_chats/
#       ├── chat_001.json
#       ├── chat_002.json
#       └── ...
```

### 3. Update Configuration

Edit the file paths in `Extract_visitor_q.py`:

```python
# Line 17: Set your data directory
root_directory = "data/raw_chats"

# Line 163: Set output path
output_file = "data/processed/Cleaned_Visitor_Messages.csv"
```

### 4. Run the Pipeline

```bash
# Step 1: Extract and clean messages
python Extract_visitor_q.py

# Step 2: Merge CSV files (if you have multiple)
python Chat_preprocessing/merging_csv.py

# Step 3: Generate embeddings
python Chat_preprocessing/Faiss_embedding.py

# Step 4: Cluster questions
python Chat_preprocessing/Faiss_cluster_questions.py

# Step 5: Generate categories
python Chat_preprocessing/generate_name_cat.py
```

### 5. View Results

```bash
# Check output files
ls -lh Chat_preprocessing/results/

# View categorized questions
head -n 20 Chat_preprocessing/results/AI_Categorized_Questions.csv
```

---

## 🎯 Common Use Cases

### Use Case 1: Find Similar Questions

**Scenario:** You want to find all questions similar to "How do I cancel my booking?"

```bash
# Edit Faiss_similar_search.py
# Change line 39:
query = "How do I cancel my booking?"

# Run similarity search
python Chat_preprocessing/Faiss_similar_search.py

# View results
cat Chat_preprocessing/results/Similar_Questions.csv
```

### Use Case 2: Analyze Question Categories

**Scenario:** You want to see what types of questions customers ask most

```bash
# Run clustering
python Chat_preprocessing/Faiss_cluster_questions.py

# View cluster summary
cat Chat_preprocessing/results/Cluster_Summary.csv
```

### Use Case 3: Clean New Chat Data

**Scenario:** You have new chat logs to process

```bash
# Update root_directory in Extract_visitor_q.py
root_directory = "data/new_chats"

# Run extraction
python Extract_visitor_q.py

# Output will be in:
# data/processed/Cleaned_Visitor_Messages.csv
```

---

## 🔧 Quick Configuration

### Adjust Number of Clusters

Edit `Faiss_cluster_questions.py`:

```python
# Line 17: Change number of clusters
num_clusters = 30  # Increase for more granular categories
```

**Guidelines:**
- 1,000 messages: 10-20 clusters
- 10,000 messages: 30-50 clusters
- 100,000 messages: 100-200 clusters

### Adjust Similarity Threshold

Edit `Extract_visitor_q.py`:

```python
# Line 151: Change fuzzy matching threshold
if fuzz.partial_ratio(text, phrase) > 85:  # 85% similarity
```

**Guidelines:**
- 90-100: Very strict (may keep noise)
- 80-90: Balanced (recommended)
- 70-80: Lenient (may remove useful data)

### Change Batch Size

Edit `Faiss_embedding.py`:

```python
# Line 17: Adjust batch size
embeddings = model.encode(df["Visitor_Messages"], batch_size=128)
```

**Guidelines:**
- 32: Low memory systems
- 128: Balanced (recommended)
- 256: High memory systems

---

## 📊 Understanding Output Files

### 1. Cleaned_Visitor_Messages.csv

**What it is:** Raw messages after PII removal and cleaning

**Format:**
```csv
Cleaned Visitor Message
"need help with my booking"
"want to change my checkin date"
```

**Use for:** Reviewing cleaning quality, manual analysis

### 2. Combined_Cleaned_Chats.csv

**What it is:** All cleaned messages merged into one file

**Format:**
```csv
Visitor_Messages
"need help with my booking"
"want to change my checkin date"
```

**Use for:** Input to embedding and clustering

### 3. Similar_Questions.csv

**What it is:** Questions similar to your query, ranked by similarity

**Format:**
```csv
Sr No,Matched Question
1,"want to change my checkin date"
2,"need to modify my reservation"
```

**Use for:** Finding related questions, building FAQ

### 4. Clustered_Questions.csv

**What it is:** All questions with assigned cluster IDs

**Format:**
```csv
Visitor_Messages,Cluster
"want to change my checkin date",5
"need to modify my reservation",5
```

**Use for:** Understanding question groupings

### 5. AI_Categorized_Questions.csv

**What it is:** Questions with human-readable category names

**Format:**
```csv
Visitor_Messages,Cluster,Category
"want to change my checkin date",5,"want to change my checkin date"
"need to modify my reservation",5,"want to change my checkin date"
```

**Use for:** Final categorization, reporting, dashboards

### 6. Cluster_Summary.csv

**What it is:** Summary of most common questions per cluster

**Format:**
```csv
Cluster,Top_Questions
5,"[('want to change my checkin date', 45), ...]"
```

**Use for:** Quick overview of main topics

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install X
# or
pip install -r requirements.txt
```

### Issue: "OSError: [E050] Can't find model 'en_core_web_sm'"

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "FileNotFoundError: No such file or directory"

**Solution:**
Check and update file paths in the script:
```python
# Make sure paths exist
import os
os.makedirs("data/processed", exist_ok=True)
```

### Issue: "MemoryError" during embedding generation

**Solution:**
Reduce batch size in `Faiss_embedding.py`:
```python
batch_size = 32  # Instead of 128
```

### Issue: Clustering produces poor results

**Solution:**
Adjust number of clusters:
```python
# Try different values
num_clusters = 20  # Start lower
num_clusters = 50  # Or higher
```

---

## 💡 Pro Tips

### Tip 1: Start Small

Process a small sample first to verify everything works:

```bash
# Copy 10-20 chat files to test directory
mkdir data/test_chats
cp data/raw_chats/chat_00{1..9}.json data/test_chats/

# Update path in script
root_directory = "data/test_chats"

# Run pipeline
python Extract_visitor_q.py
```

### Tip 2: Monitor Progress

Use `tqdm` progress bars to track processing:

```python
from tqdm import tqdm

for file in tqdm(files, desc="Processing files"):
    # Process file
    pass
```

### Tip 3: Save Intermediate Results

Don't reprocess everything if one step fails:

```python
# Save after each major step
df.to_csv("checkpoint_step1.csv", index=False)
```

### Tip 4: Version Your Data

Keep track of different processing runs:

```bash
# Create dated output directories
mkdir -p results/2024-03-15
python Extract_visitor_q.py
mv output.csv results/2024-03-15/
```

### Tip 5: Validate Results

Always spot-check output:

```bash
# Random sample of 10 results
shuf -n 10 output.csv
```

---

## 📈 Next Steps

After completing the quick start:

1. **Review Results**
   - Check categorization quality
   - Identify any issues
   - Adjust parameters if needed

2. **Customize Cleaning**
   - Add domain-specific filters
   - Update PII patterns
   - Adjust noise removal

3. **Optimize Performance**
   - Tune batch sizes
   - Adjust cluster counts
   - Enable GPU if available

4. **Integrate with Systems**
   - Export to dashboard
   - Connect to ticketing system
   - Automate pipeline

5. **Monitor and Maintain**
   - Track processing times
   - Monitor data quality
   - Update models periodically

---

## 📚 Learn More

- **Full Documentation:** See `README.md`
- **Detailed Setup:** See `SETUP_GUIDE.md`
- **Configuration Options:** See `CONFIGURATION.md`
- **Example Data:** See `EXAMPLE_DATA.md`
- **Security Guidelines:** See `SECURITY.md`

---

## 🆘 Need Help?

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the full documentation
3. Search existing GitHub issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information

---

## ✅ Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] SpaCy model downloaded
- [ ] Data directory created
- [ ] File paths updated
- [ ] First extraction completed
- [ ] Results validated

---

**Congratulations!** 🎉 You're now ready to use the Chat Classification system!

For more advanced usage, see the full documentation in `README.md`.
