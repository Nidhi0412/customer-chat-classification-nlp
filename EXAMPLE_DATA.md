# Example Data Formats

This document provides example data formats for understanding the project workflow. **All data shown here is synthetic and for demonstration purposes only.**

## 📄 Input Data Format

### Raw JSON Chat Log Example

```json
{
  "chatId": "chat_12345",
  "startTime": "2024-03-15T10:30:00Z",
  "messages": [
    {
      "messageId": "msg_001",
      "timestamp": "2024-03-15T10:30:15Z",
      "sender": {
        "t": "v",
        "name": "Visitor"
      },
      "msg": "Hi, I need help with my booking"
    },
    {
      "messageId": "msg_002",
      "timestamp": "2024-03-15T10:30:30Z",
      "sender": {
        "t": "a",
        "name": "Agent"
      },
      "msg": "Hello! I'd be happy to help. What's your reservation number?"
    },
    {
      "messageId": "msg_003",
      "timestamp": "2024-03-15T10:31:00Z",
      "sender": {
        "t": "v",
        "name": "Visitor"
      },
      "msg": "My name is John Doe, email: john@example.com, booking #12345"
    },
    {
      "messageId": "msg_004",
      "timestamp": "2024-03-15T10:31:30Z",
      "sender": {
        "t": "v",
        "name": "Visitor"
      },
      "msg": "I want to change my check-in date from 03/20/2024 to 03/22/2024"
    }
  ]
}
```

**Key Fields:**
- `sender.t`: "v" for visitor, "a" for agent
- `msg`: The actual message content
- `timestamp`: When the message was sent

---

## 🧹 Cleaned Data Format

### After Running `Extract_visitor_q.py`

**Input Messages:**
```
"Hi, I need help with my booking"
"My name is John Doe, email: john@example.com, booking #12345"
"I want to change my check-in date from 03/20/2024 to 03/22/2024"
```

**Cleaned Output CSV:**
```csv
Cleaned Visitor Message
"need help with my booking"
"want to change my checkin date"
```

**What Was Removed:**
- Greetings: "Hi"
- Personal information: "John Doe", "john@example.com"
- Booking numbers: "#12345"
- Dates: "03/20/2024", "03/22/2024"
- Conversational noise

---

## 📊 Processing Pipeline Outputs

### 1. Combined_Cleaned_Chats.csv

After merging multiple monthly files:

```csv
Visitor_Messages
"need help with my booking"
"want to change my checkin date"
"how do i cancel my reservation"
"what is your refund policy"
"can i add extra guests to my room"
"is breakfast included in the price"
"how far is the hotel from the airport"
"do you have parking available"
```

---

### 2. Similar_Questions.csv

After running similarity search for query: "How to modify my booking?"

```csv
Sr No,Matched Question
1,"want to change my checkin date"
2,"need to modify my reservation"
3,"can i update my booking details"
4,"how do i change my room type"
5,"want to extend my stay"
6,"need to add another night"
7,"can i change guest information"
8,"how to update payment method"
9,"want to modify room preferences"
10,"need to change checkout date"
```

**Similarity Score:** Questions are ranked by semantic similarity using L2 distance in embedding space.

---

### 3. Clustered_Questions.csv

After K-Means clustering:

```csv
Visitor_Messages,Cluster
"want to change my checkin date",5
"need to modify my reservation",5
"can i update my booking details",5
"how do i cancel my reservation",12
"what is your refund policy",12
"can i get my money back",12
"is breakfast included in the price",8
"what amenities do you offer",8
"do you have a gym",8
"how far is the hotel from the airport",3
"is there public transport nearby",3
"do you provide shuttle service",3
```

**Cluster Interpretation:**
- Cluster 5: Booking Modifications
- Cluster 12: Cancellations & Refunds
- Cluster 8: Amenities & Services
- Cluster 3: Location & Transportation

---

### 4. AI_Categorized_Questions.csv

After assigning category names from representative questions:

```csv
Sr No,Matched Question,Cluster,Category
1,"want to change my checkin date",5,"want to change my checkin date"
2,"need to modify my reservation",5,"want to change my checkin date"
3,"can i update my booking details",5,"want to change my checkin date"
4,"how do i cancel my reservation",12,"how do i cancel my reservation"
5,"what is your refund policy",12,"how do i cancel my reservation"
6,"can i get my money back",12,"how do i cancel my reservation"
7,"is breakfast included in the price",8,"is breakfast included in the price"
8,"what amenities do you offer",8,"is breakfast included in the price"
9,"do you have a gym",8,"is breakfast included in the price"
```

**Category Assignment:**
- Each cluster gets a representative question as its category name
- Representative is the question closest to the cluster centroid

---

### 5. Cluster_Summary.csv

Summary of most common questions per cluster:

```csv
Cluster,Top_Questions
5,"[('want to change my checkin date', 45), ('need to modify my reservation', 38), ('can i update my booking details', 32)]"
12,"[('how do i cancel my reservation', 67), ('what is your refund policy', 54), ('can i get my money back', 41)]"
8,"[('is breakfast included in the price', 89), ('what amenities do you offer', 76), ('do you have a gym', 52)]"
3,"[('how far is the hotel from the airport', 93), ('is there public transport nearby', 71), ('do you provide shuttle service', 58)]"
```

**Format:** `(question, frequency_count)`

---

## 🗄️ Database Schema Example

### Hotel Reservation Database (Simplified)

```sql
-- Reservation Information
CREATE TABLE reservations (
    reservation_id BIGINT PRIMARY KEY,
    reservation_no VARCHAR(50),
    guest_name VARCHAR(100),
    check_in_date DATE,
    check_out_date DATE,
    room_type VARCHAR(50),
    status VARCHAR(20)
);

-- Guest Messages
CREATE TABLE guest_messages (
    message_id BIGINT PRIMARY KEY,
    reservation_id BIGINT,
    message_text TEXT,
    sent_at DATETIME,
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
);

-- Sample Data
INSERT INTO reservations VALUES
(1001, 'RES-2024-001', 'Guest A', '2024-03-20', '2024-03-23', 'Deluxe', 'Confirmed'),
(1002, 'RES-2024-002', 'Guest B', '2024-03-22', '2024-03-25', 'Suite', 'Checked-in');

INSERT INTO guest_messages VALUES
(5001, 1001, 'need help with my booking', '2024-03-15 10:30:00'),
(5002, 1001, 'want to change my checkin date', '2024-03-15 10:35:00'),
(5003, 1002, 'is breakfast included in the price', '2024-03-22 08:15:00');
```

---

## 🤖 Chatbot Query Examples

### Natural Language to SQL

**User Query:** "How many reservations do we have for next week?"

**Generated SQL:**
```sql
SELECT COUNT(*) as total_reservations
FROM reservations
WHERE check_in_date BETWEEN '2024-03-18' AND '2024-03-24'
AND status IN ('Confirmed', 'Checked-in');
```

**Response:** "You have 47 reservations for next week."

---

**User Query:** "What are the most common questions from guests?"

**Generated SQL:**
```sql
SELECT message_text, COUNT(*) as frequency
FROM guest_messages
GROUP BY message_text
ORDER BY frequency DESC
LIMIT 10;
```

**Response:**
```
Top 10 most common questions:
1. "is breakfast included in the price" (89 times)
2. "how far is the hotel from the airport" (93 times)
3. "how do i cancel my reservation" (67 times)
...
```

---

## 📈 Embedding Visualization (Conceptual)

### How Embeddings Work

```
Original Text → Sentence-BERT → 384-dimensional Vector

"need help with booking" → [0.23, -0.45, 0.67, ..., 0.12]
"want to modify reservation" → [0.21, -0.43, 0.69, ..., 0.14]
"is breakfast included" → [-0.67, 0.34, -0.12, ..., 0.89]
```

**Similar questions have similar vectors:**
- Booking-related questions cluster together
- Amenity questions form another cluster
- Cancellation queries group separately

---

## 🔍 FAISS Index Search Example

### Query Process

```python
# Query
query = "How to modify my booking?"

# Convert to embedding
query_embedding = model.encode([query])
# Result: [0.22, -0.44, 0.68, ..., 0.13]

# Search in FAISS index
distances, indices = index.search(query_embedding, top_n=5)

# Results (sorted by distance - lower is more similar)
# Index 1234: "want to change my checkin date" (distance: 0.12)
# Index 5678: "need to modify my reservation" (distance: 0.15)
# Index 9012: "can i update my booking details" (distance: 0.18)
```

---

## 📋 Complete Example Workflow

### Step-by-Step Data Transformation

**1. Raw JSON Input:**
```json
{"msg": "Hi! My name is John, email john@example.com. I want to change my booking from 03/20 to 03/22"}
```

**2. After Cleaning:**
```
"want to change my booking"
```

**3. After Embedding:**
```
[0.23, -0.45, 0.67, 0.12, ..., 0.34]  (384 dimensions)
```

**4. After Clustering:**
```
Cluster: 5 (Booking Modifications)
```

**5. After Categorization:**
```
Category: "want to change my checkin date"
```

**6. Final Output:**
```csv
Visitor_Messages,Cluster,Category
"want to change my booking",5,"want to change my checkin date"
```

---

## 🎯 Use Cases

### 1. Customer Support Analytics
- Identify most common customer issues
- Track trending questions over time
- Optimize FAQ sections

### 2. Automated Response Systems
- Match incoming questions to existing solutions
- Suggest relevant help articles
- Route to appropriate support agents

### 3. Training & Quality Assurance
- Identify knowledge gaps in support team
- Create training materials for common scenarios
- Improve response templates

### 4. Product Improvement
- Discover pain points in booking process
- Identify missing features customers ask about
- Prioritize product roadmap

---

## ⚠️ Important Notes

1. **All data in this document is synthetic** - created for demonstration purposes
2. **No real customer data** is included in this repository
3. **Privacy compliance** - Always anonymize data before processing
4. **Data security** - Use environment variables for sensitive credentials
5. **Testing** - Test with sample data before processing production data

---

## 🔗 Related Files

- `README.md` - Main project documentation
- `requirements.txt` - Python dependencies
- `CONFIGURATION.md` - Detailed configuration guide
- `WORKFLOW_DIAGRAM.md` - Visual workflow representation

---

**Remember:** When working with real customer data, always:
- ✅ Obtain proper authorization
- ✅ Comply with data privacy regulations (GDPR, CCPA)
- ✅ Anonymize personal information
- ✅ Secure database credentials
- ✅ Use encryption for sensitive data
