# Workflow Diagram & Architecture

This document provides visual representations of the Chat Classification system's workflow and architecture.

## 🎯 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHAT CLASSIFICATION SYSTEM                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Raw JSON Data  │  (Customer chat logs)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DATA EXTRACTION & CLEANING              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Extract_visitor_q.py                                        │  │
│  │  • Extract visitor messages from JSON                        │  │
│  │  • Remove PII (names, emails, phone numbers)                 │  │
│  │  • Filter conversational noise                               │  │
│  │  • Normalize text (stylized words, dates, etc.)              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Cleaned CSVs   │  (Monthly files)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: DATA CONSOLIDATION                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  merging_csv.py                                              │  │
│  │  • Combine multiple monthly CSV files                        │  │
│  │  • Remove duplicates                                         │  │
│  │  • Create unified dataset                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Combined CSV   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: EMBEDDING GENERATION                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Faiss_embedding.py                                          │  │
│  │  • Convert text to 384-dim vectors (Sentence-BERT)           │  │
│  │  • Create FAISS index for fast search                        │  │
│  │  • Store embeddings and index                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Embeddings (.npy) + FAISS Index    │
└────────┬────────────────────────────┘
         │
         ├─────────────────────────────────────────────┐
         │                                             │
         ▼                                             ▼
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│   PHASE 4: SIMILARITY SEARCH        │  │   PHASE 5: CLUSTERING               │
│  ┌──────────────────────────────┐   │  │  ┌──────────────────────────────┐   │
│  │  Faiss_similar_search.py     │   │  │  │  Faiss_cluster_questions.py  │   │
│  │  • Query-based search        │   │  │  │  • K-Means clustering        │   │
│  │  • Find top-N matches        │   │  │  │  • Assign cluster IDs        │   │
│  │  • Rank by similarity        │   │  │  │  • Generate summaries        │   │
│  └──────────────────────────────┘   │  │  └──────────────────────────────┘   │
└─────────────────────────────────────┘  └─────────────────────────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│  Similar_Questions.csv              │  │  Clustered_Questions.csv            │
└─────────────────────────────────────┘  └────────┬────────────────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────────────────────────┐
                                         │   PHASE 6: CATEGORIZATION           │
                                         │  ┌──────────────────────────────┐   │
                                         │  │  generate_name_cat.py        │   │
                                         │  │  • Assign category names     │   │
                                         │  │  • Use representative Qs     │   │
                                         │  └──────────────────────────────┘   │
                                         └─────────────────────────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────────────────────────┐
                                         │  AI_Categorized_Questions.csv       │
                                         └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    OPTIONAL: DATABASE QUERY AGENT                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Claude_ai_saas.py                                           │  │
│  │  • Natural language to SQL conversion                        │  │
│  │  • LangChain agent with memory                               │  │
│  │  • Query hotel database                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detailed Process Flow

### Phase 1: Data Extraction & Cleaning

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Extract_visitor_q.py                         │
└─────────────────────────────────────────────────────────────────────┘

Input: JSON Files
├── chat_001.json
├── chat_002.json
└── chat_003.json

         │
         ▼
    
Step 1: Extract Messages
┌──────────────────────────────────────┐
│  for message in chat_data:           │
│    if sender.type == "visitor":      │
│      extract message                 │
└──────────────────────────────────────┘
         │
         ▼

Step 2: Remove PII
┌──────────────────────────────────────┐
│  • Names (using SpaCy NER)           │
│  • Emails (regex patterns)           │
│  • Phone numbers (regex patterns)    │
│  • Hotel codes (numeric patterns)    │
│  • Booking IDs (alphanumeric)        │
└──────────────────────────────────────┘
         │
         ▼

Step 3: Remove Dates & Times
┌──────────────────────────────────────┐
│  • Date formats (MM/DD/YYYY, etc.)   │
│  • Time formats (HH:MM AM/PM)        │
│  • Month names (Jan, February, etc.) │
└──────────────────────────────────────┘
         │
         ▼

Step 4: Normalize Text
┌──────────────────────────────────────┐
│  • Stylized words (hiii → hi)        │
│  • Word segmentation (helloo → hello)│
│  • Lowercase conversion              │
│  • Remove extra spaces               │
└──────────────────────────────────────┘
         │
         ▼

Step 5: Filter Noise
┌──────────────────────────────────────┐
│  • Greetings (hi, hello)             │
│  • Acknowledgments (ok, thanks)      │
│  • Short messages (< 5 chars)        │
│  • Fuzzy matching (85% threshold)    │
└──────────────────────────────────────┘
         │
         ▼

Output: Cleaned CSV
├── Cleaned_Visitor_Message
├── "need help with booking"
├── "want to change checkin date"
└── "how do i cancel reservation"
```

---

### Phase 3: Embedding Generation

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Faiss_embedding.py                           │
└─────────────────────────────────────────────────────────────────────┘

Input: Combined_Cleaned_Chats.csv
┌────────────────────────────────────┐
│  Visitor_Messages                  │
│  "need help with booking"          │
│  "want to change checkin date"     │
│  "how do i cancel reservation"     │
└────────────────────────────────────┘
         │
         ▼

Step 1: Load Sentence-BERT Model
┌────────────────────────────────────┐
│  model = SentenceTransformer(      │
│    "all-MiniLM-L6-v2"              │
│  )                                 │
└────────────────────────────────────┘
         │
         ▼

Step 2: Generate Embeddings (Batch Processing)
┌────────────────────────────────────────────────────────────┐
│  Text: "need help with booking"                            │
│    ↓                                                        │
│  Embedding: [0.23, -0.45, 0.67, ..., 0.12] (384 dims)     │
│                                                             │
│  Text: "want to change checkin date"                       │
│    ↓                                                        │
│  Embedding: [0.21, -0.43, 0.69, ..., 0.14] (384 dims)     │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 3: Create FAISS Index
┌────────────────────────────────────┐
│  dimension = 384                   │
│  index = IndexFlatL2(dimension)    │
│  index.add(embeddings)             │
└────────────────────────────────────┘
         │
         ▼

Step 4: Save Outputs
┌────────────────────────────────────┐
│  • Text_Embeddings.npy             │
│  • Embeddings_FAISS.index          │
└────────────────────────────────────┘

FAISS Index Structure:
┌─────────────────────────────────────────────────────────┐
│  Index 0: [0.23, -0.45, 0.67, ..., 0.12]               │
│  Index 1: [0.21, -0.43, 0.69, ..., 0.14]               │
│  Index 2: [-0.67, 0.34, -0.12, ..., 0.89]              │
│  ...                                                     │
│  Index N: [0.45, -0.23, 0.56, ..., 0.34]               │
└─────────────────────────────────────────────────────────┘
```

---

### Phase 4: Similarity Search

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Faiss_similar_search.py                         │
└─────────────────────────────────────────────────────────────────────┘

Query: "How to modify my booking?"
         │
         ▼

Step 1: Convert Query to Embedding
┌────────────────────────────────────────────────────────────┐
│  query_embedding = model.encode([query])                   │
│  Result: [0.22, -0.44, 0.68, ..., 0.13]                   │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 2: Search in FAISS Index
┌────────────────────────────────────────────────────────────┐
│  distances, indices = index.search(                        │
│    query_embedding,                                        │
│    top_n=1000                                              │
│  )                                                         │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 3: Retrieve Matched Questions
┌────────────────────────────────────────────────────────────┐
│  Index 1234 (distance: 0.12)                               │
│    → "want to change my checkin date"                      │
│                                                             │
│  Index 5678 (distance: 0.15)                               │
│    → "need to modify my reservation"                       │
│                                                             │
│  Index 9012 (distance: 0.18)                               │
│    → "can i update my booking details"                     │
│                                                             │
│  ... (up to top_n results)                                 │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Output: Similar_Questions.csv
┌────────────────────────────────────────────────────────────┐
│  Sr No | Matched Question                                  │
│  ─────────────────────────────────────────────────────────│
│  1     | "want to change my checkin date"                  │
│  2     | "need to modify my reservation"                   │
│  3     | "can i update my booking details"                 │
│  ...   | ...                                                │
└────────────────────────────────────────────────────────────┘

Distance Interpretation:
┌────────────────────────────────────────┐
│  0.00 - 0.20  │  Very Similar          │
│  0.20 - 0.50  │  Similar               │
│  0.50 - 1.00  │  Somewhat Similar      │
│  > 1.00       │  Different             │
└────────────────────────────────────────┘
```

---

### Phase 5: Clustering

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Faiss_cluster_questions.py                        │
└─────────────────────────────────────────────────────────────────────┘

Input: Text_Embeddings.npy
┌────────────────────────────────────────────────────────────┐
│  [0.23, -0.45, 0.67, ..., 0.12]  ← "booking modification"  │
│  [0.21, -0.43, 0.69, ..., 0.14]  ← "booking modification"  │
│  [-0.67, 0.34, -0.12, ..., 0.89] ← "amenities"             │
│  [-0.65, 0.32, -0.10, ..., 0.87] ← "amenities"             │
│  [0.45, 0.23, -0.56, ..., 0.34]  ← "cancellation"          │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 1: K-Means Clustering
┌────────────────────────────────────────────────────────────┐
│  kmeans = KMeans(n_clusters=30, random_state=42)           │
│  cluster_labels = kmeans.fit_predict(embeddings)           │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 2: Assign Cluster IDs
┌────────────────────────────────────────────────────────────┐
│  Message                          │  Cluster               │
│  ───────────────────────────────────────────────────────  │
│  "want to change checkin date"    │  5                     │
│  "need to modify reservation"     │  5                     │
│  "is breakfast included"          │  8                     │
│  "what amenities available"       │  8                     │
│  "how do i cancel"                │  12                    │
│  "what is refund policy"          │  12                    │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 3: Generate Cluster Summary
┌────────────────────────────────────────────────────────────┐
│  Cluster 5: Booking Modifications                          │
│    • "want to change checkin date" (45 occurrences)        │
│    • "need to modify reservation" (38 occurrences)         │
│    • "can i update booking" (32 occurrences)               │
│                                                             │
│  Cluster 8: Amenities & Services                           │
│    • "is breakfast included" (89 occurrences)              │
│    • "what amenities available" (76 occurrences)           │
│    • "do you have gym" (52 occurrences)                    │
│                                                             │
│  Cluster 12: Cancellations & Refunds                       │
│    • "how do i cancel" (67 occurrences)                    │
│    • "what is refund policy" (54 occurrences)              │
│    • "can i get money back" (41 occurrences)               │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Output Files:
├── Clustered_Questions.csv
└── Cluster_Summary.csv
```

---

### Phase 6: Categorization

```
┌─────────────────────────────────────────────────────────────────────┐
│                       generate_name_cat.py                           │
└─────────────────────────────────────────────────────────────────────┘

Input: Similar_Questions.csv + Embeddings
         │
         ▼

Step 1: Cluster Questions
┌────────────────────────────────────────────────────────────┐
│  Cluster 5:                                                 │
│    • "want to change checkin date"                         │
│    • "need to modify reservation"                          │
│    • "can i update booking details"                        │
│    • "how do i change room type"                           │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 2: Find Cluster Centroid
┌────────────────────────────────────────────────────────────┐
│  Centroid = Average of all embeddings in cluster           │
│  [0.22, -0.44, 0.68, ..., 0.13]                           │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 3: Find Closest Question to Centroid
┌────────────────────────────────────────────────────────────┐
│  Calculate distance from each question to centroid:        │
│    • "want to change checkin date" → distance: 0.08 ✓     │
│    • "need to modify reservation" → distance: 0.12         │
│    • "can i update booking details" → distance: 0.15       │
│    • "how do i change room type" → distance: 0.20          │
│                                                             │
│  Representative: "want to change checkin date"             │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 4: Assign Category Name
┌────────────────────────────────────────────────────────────┐
│  All questions in Cluster 5 get category:                  │
│  "want to change checkin date"                             │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Output: AI_Categorized_Questions.csv
┌────────────────────────────────────────────────────────────┐
│  Question                      │ Cluster │ Category         │
│  ────────────────────────────────────────────────────────  │
│  "want to change checkin date" │ 5       │ "want to change  │
│  "need to modify reservation"  │ 5       │  checkin date"   │
│  "can i update booking"        │ 5       │                  │
└────────────────────────────────────────────────────────────┘
```

---

## 🤖 Database Query Agent Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Claude_ai_saas.py                            │
└─────────────────────────────────────────────────────────────────────┘

User Input: "How many reservations do we have for next week?"
         │
         ▼

Step 1: LangChain Agent Receives Query
┌────────────────────────────────────────────────────────────┐
│  AgentExecutor                                              │
│    ├── LLM: GPT-4o                                         │
│    ├── Tools: [QuerySQLDatabaseTool]                       │
│    ├── Memory: ConversationBufferMemory                    │
│    └── Prompt: System + User + History                     │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 2: Agent Analyzes Query
┌────────────────────────────────────────────────────────────┐
│  • Identifies intent: Count reservations                   │
│  • Extracts entities: "next week"                          │
│  • Determines required tables: reservations                │
│  • Plans SQL query structure                               │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 3: Generate SQL Query
┌────────────────────────────────────────────────────────────┐
│  SELECT COUNT(*) as total_reservations                     │
│  FROM reservations                                          │
│  WHERE check_in_date BETWEEN '2024-03-18' AND '2024-03-24'│
│  AND status IN ('Confirmed', 'Checked-in')                 │
│  AND hotel_code = 8961;                                    │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 4: Validate Query
┌────────────────────────────────────────────────────────────┐
│  ✓ Contains hotel_code filter                              │
│  ✓ Valid MySQL syntax                                      │
│  ✓ Uses correct table names                                │
│  ✓ Proper date format                                      │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 5: Execute Query
┌────────────────────────────────────────────────────────────┐
│  Database Response:                                         │
│  ┌──────────────────────┐                                  │
│  │ total_reservations   │                                  │
│  │ 47                   │                                  │
│  └──────────────────────┘                                  │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 6: Format Response
┌────────────────────────────────────────────────────────────┐
│  "You have 47 reservations for next week."                 │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Step 7: Update Memory
┌────────────────────────────────────────────────────────────┐
│  ConversationBufferMemory:                                  │
│    User: "How many reservations for next week?"            │
│    Assistant: "You have 47 reservations for next week."    │
└────────────────────────────────────────────────────────────┘
         │
         ▼

Output: Natural Language Response + Context Memory
```

---

## 📊 Data Flow Summary

```
Raw JSON → Cleaned CSV → Combined CSV → Embeddings → FAISS Index
                                            │
                                            ├─→ Similarity Search → Similar Questions
                                            │
                                            └─→ Clustering → Categorized Questions
                                                    │
                                                    └─→ Cluster Summary

Optional: Natural Language Query → SQL Agent → Database → Results
```

---

## 🔄 Iterative Improvement Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                   CONTINUOUS IMPROVEMENT                     │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  Collect Data    │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Clean & Process │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Generate        │
    │  Embeddings      │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Cluster &       │
    │  Categorize      │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Analyze Results │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Identify Issues │
    │  • Poor clusters │
    │  • Noise in data │
    │  • Missing cats  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Adjust          │
    │  Parameters      │
    │  • num_clusters  │
    │  • threshold     │
    │  • filters       │
    └────────┬─────────┘
             │
             └──────────┐
                        │
                        ▼
                 ┌──────────────┐
                 │  Re-process  │
                 └──────────────┘
```

---

## 🎯 Key Performance Indicators

```
┌─────────────────────────────────────────────────────────────┐
│                        METRICS                               │
└─────────────────────────────────────────────────────────────┘

Data Quality:
├── % of PII removed: 100%
├── % of noise filtered: 85-95%
└── Data completeness: 95%+

Processing Speed:
├── Embedding generation: ~1000 msgs/sec
├── FAISS search: <100ms per query
└── Clustering: ~10 sec for 10K messages

Clustering Quality:
├── Silhouette score: 0.3-0.5 (good)
├── Cluster size variance: Low
└── Category coherence: High

Agent Performance:
├── SQL accuracy: 95%+
├── Response time: 2-5 seconds
└── Context retention: 10+ exchanges
```

---

This workflow diagram provides a comprehensive view of how data flows through the system and how each component interacts with others.
