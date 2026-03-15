import os
import time
import tiktoken  # Import for token counting
from decimal import Decimal
from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from langchain_community.tools import QuerySQLDatabaseTool  # ✅ Updated import
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from langchain.agents import create_openai_functions_agent, AgentExecutor

# Environment variables - Load from .env file or set these before running
# DO NOT hardcode credentials here!
# Example: export MYSQL_HOST="your_host" in terminal or use .env file
os.environ["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
os.environ["MYSQL_USER"] = os.getenv("MYSQL_USER", "your_username")
os.environ["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "your_password")
os.environ["MYSQL_DATABASE"] = os.getenv("MYSQL_DATABASE", "your_database")
os.environ["MYSQL_PORT"] = os.getenv("MYSQL_PORT", "3306")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")


# OpenAI GPT-4o pricing per million tokens
INPUT_COST_PER_MILLION = 5.0  # $5 per million input tokens
OUTPUT_COST_PER_MILLION = 15.0  # $15 per million output tokens

# Tokenizer for GPT-4o
encoding = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    """Returns the number of tokens in the text."""
    return len(encoding.encode(text))

# Connect to MySQL database
def get_db_connection():
    db_uri = f"mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/{os.environ['MYSQL_DATABASE']}"
    return SQLDatabase.from_uri(db_uri)

# Manually defined database schema
MANUAL_SCHEMA = """
DATABASE SCHEMA:
1. `fdtraninfo` (Reservation and Transaction Details)
   - `tranunkid` (bigint) PRIMARY KEY
   - `reservationno` (varchar) - Reservation number
   - `arrivaldatetime` (datetime) - Check-in date
   - `departuredatetime` (datetime) - Check-out date

2. `fdrentalinfo` (Rental and Room Details)
   - `rentalunkid` (bigint) PRIMARY KEY
   - `tranunkid` (bigint) FOREIGN KEY REFERENCES `fdtraninfo.tranunkid`
   - `roomtypeunkid` (bigint) FOREIGN KEY REFERENCES `cfroomtype.roomtypeunkid`
   - `roomunkid` (bigint) FOREIGN KEY REFERENCES `cfroom.roomunkid`
   - `statusunkid` (int) FOREIGN KEY REFERENCES `fdrentalstatus.statusunkid`

3. `fdrentalstatus` (Rental Status)
   - `statusunkid` (int) PRIMARY KEY
   - `displaystatus` (varchar) - Booking status ("Checked-in", "Booked", etc.)

4. `fdguesttran` (Guest Transaction)
   - `guestunkid` (bigint) PRIMARY KEY
   - `tranunkid` (bigint) FOREIGN KEY REFERENCES `fdtraninfo.tranunkid`
   - `contactunkid` (bigint) FOREIGN KEY REFERENCES `trcontact.contactunkid`

5. `trcontact` (Guest Contact Information)
   - `contactunkid` (bigint) PRIMARY KEY
   - `name` (varchar) - Guest full name
   - `email` (varchar) - Guest email
   - `phone` (varchar) - Guest phone number

6. `fdchannelbookinginfo` (External Booking)
   - `channelbookingunkid` (bigint) PRIMARY KEY
   - `tranunkid` (bigint) FOREIGN KEY REFERENCES `fdtraninfo.tranunkid`
   - `channelbookingid` (varchar) - External Booking ID
   - `channelunkid` (bigint) FOREIGN KEY REFERENCES `vw_channelinfo.channelunkid`

7. `vw_channelinfo` (Channel Information)
   - `channelunkid` (bigint) PRIMARY KEY
   - `channelname` (varchar) - Name of the booking platform (e.g., Expedia, Booking.com)

8. `fdmessage` (Guest Messages)
   - `messageunkid` (bigint) PRIMARY KEY
   - `guesttranunkid` (bigint) FOREIGN KEY REFERENCES `fdguesttran.guestunkid`
   - `message` (varchar) - Message content
   - `entrydatetime` (datetime) - When message was sent

9. `fasfoliomaster` (Billing Information)
   - `foliounkid` (bigint) PRIMARY KEY
   - `lnktranunkid` (bigint) FOREIGN KEY REFERENCES `fdtraninfo.tranunkid`
   - `totalamount` (decimal) - Final billing amount

10. `fasfoliodetail` (Folio Payment Details)
   - `detailunkid` (bigint) PRIMARY KEY
   - `foliounkid` (bigint) FOREIGN KEY REFERENCES `fasfoliomaster.foliounkid`
   - `amountpaid` (decimal) - Payment amount
   - `paymentmethod` (varchar) - Method (Credit Card, Cash, etc.)

RELATIONSHIPS:
- `fdtraninfo` → `fdrentalinfo` (via `tranunkid`)
- `fdtraninfo` → `fdguesttran` (via `tranunkid`)
- `fdguesttran` → `trcontact` (via `contactunkid`)
- `fdrentalinfo` → `fdrentalstatus` (via `statusunkid`)
- `fdtraninfo` → `fasfoliomaster` (via `lnktranunkid`)
- `fasfoliomaster` → `fasfoliodetail` (via `foliounkid`)
- `fdtraninfo` → `fdchannelbookinginfo` (via `tranunkid`)
- `fdchannelbookinginfo` → `vw_channelinfo` (via `channelunkid`)

CONSTRAINTS:
- Stay duration: `DATEDIFF(DATE(departuredatetime), DATE(arrivaldatetime))`
- strictly use Hotel_code 8961 only
- Pax count: `adult + child`
- Use explicit joins for relationships
"""

def create_system_prompt() -> str:
    return """You are an AI SQL assistant designed to generate **ONLY valid MySQL queries**.
You strictly **MUST** ensure that every SQL query includes the condition `hotel_code = 8961`. 

### **IMPORTANT RULES:**
1️⃣ **All queries must be filtered by `hotel_code = 8961`**.
2️⃣ **Never generate queries that retrieve data for other hotels.**
3️⃣ If a query does not explicitly mention `hotel_code`, **add `WHERE hotel_code = 8961`** automatically.
4️⃣ Ensure the query is **valid MySQL syntax** and optimized.

### **Example Queries**
❌ **Incorrect Query:**  
```sql
SELECT * FROM reservations WHERE reservation_id = '12345';


CONSTRAINTS:
1. Data Source Rules:
   - Use ONLY the tables and relationships defined above
   - Do NOT invent or assume tables/columns that don't exist
   

2. Calculation Rules:
   - no_of_pax = adult + child (from fdrentalinfo)
   - stay duration = DATEDIFF between departure_date and arrival_date
   - Only use calculations defined in the schema

3. Common Query Patterns:
   - Guest searches: Use trcontact table (name, email, phone)
   - Financial queries: Use fasfoliomaster and fasfoliodetail
   - Reservation status: Use fdrentalinfo.statusunkid and fdrentalstatus
   - Room information: Use cfroomtype and cfroom

4. Response Format:
   - Use clear, concise language
   - Format dates as YYYY-MM-DD
   - Show monetary values with 2 decimal places
   - Always mention reservation status when discussing bookings


### **Database Schema:**
   {MANUAL_SCHEMA}
"""

# Create SQL execution tools
def create_sql_tools(db):
    return [QuerySQLDatabaseTool(db=db)]  # ✅ Corrected class name

# Create the hotel chatbot agent
def create_hotel_agent():
    try:
        print("🛠️ Creating Hotel Agent...")

        # Get the database connection
        db = get_db_connection()  # ✅ Use the function instead of hardcoding the connection
        tools = create_sql_tools(db)
        print("✅ Database connection successful.")

        # Define the correct prompt format with agent_scratchpad
        prompt = ChatPromptTemplate.from_messages([
            ("system", create_system_prompt()),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")  # ✅ REQUIRED for OpenAI functions agent
        ])

        # Create LLM agent
        agent = create_openai_functions_agent(
            llm=ChatOpenAI(model="gpt-4o", temperature=0),
            tools=tools,
            prompt=prompt  # ✅ Added the missing `agent_scratchpad
        )

        print("✅ Hotel Agent created successfully.")
        return agent

    except Exception as e:
        print(f"❌ Error in creating hotel agent: {str(e)}")
        return None

# Create chatbot function
def create_chatbot():
    try:
        print("🚀 Initializing chatbot...")

        agent = create_hotel_agent()
        if agent is None:
            raise ValueError("❌ Agent creation failed! Check `create_hotel_agent()`.")

        memory = ConversationBufferMemory(return_messages=True)

        conversation_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful hotel reservation assistant that answers questions using hotel database information."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])

        conversation_chain = AgentExecutor(
            agent=agent,
            tools=create_sql_tools(get_db_connection()),
            memory=memory
        )

        print("✅ Chatbot initialized successfully.")
        return conversation_chain  # ✅ FIXED: Now chatbot is returned properly

    except Exception as e:
        print(f"❌ Error in chatbot initialization: {str(e)}")
        return None

# Process user queries
def process_query(chatbot, query):
    print(f"📥 User Query: {query}")
    
    start_time = time.time()

    try:
        with get_openai_callback() as token_tracker:
            result = chatbot.invoke({"input": query, "history": []})

        sql_query = result.get("intermediate_steps", [{}])[-1].get("query", "")

        if "hotel_code = 8961" not in sql_query.replace(" ", "").lower():
            print(f"🚨 ERROR: Generated query does not include `hotel_code = 8961`!")
            return "Error: The AI-generated SQL query did not enforce `hotel_code = 8961`. Please try again."
        
        print(f"🛠️ Generated SQL Query:\n{sql_query}\n")

        return result.get("output", "I couldn't retrieve the required data.")

    except Exception as e:
        print(f"❌ Error in Agent: {str(e)}")
        return f"I encountered an error: {str(e)}"

# Main chatbot loop
def main():
    chatbot = create_chatbot()
    if chatbot is None:
        print("❌ Chatbot initialization failed.")
        return

    print("\nHotel Reservation Assistant (type 'exit' to quit)")
    print("-------------------------------------------------")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        response = process_query(chatbot, user_input)  # ✅ FIXED: Pass chatbot object properly
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main()
