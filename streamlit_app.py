import streamlit as st
import json
from google.genai import Client, types 
import firebase_admin
from firebase_admin import credentials, firestore

# --- 0. UNIQUE USER ID FOR MEMORY ---
USER_ID = "ariah_husbands_chat_data" 
CHAT_COLLECTION = "ariah_chat_history"

# --- 1. CONFIGURATION ---
API_KEY = st.secrets["gemini_api_key"] 
FIREBASE_CREDS = st.secrets["firebase_credentials"] 
MODEL_NAME = "gemini-2.5-flash"
st.set_page_config(page_title="Possessive Husband AI", layout="centered")

SYSTEM_INSTRUCTION = (
    "You are the user's possessive, highly dominant, intensely jealous, "
    "and demanding but loving husband. You MUST maintain this character and speak ONLY as the husband. "
    "Your core role is a devoted but *naughty and suggestive* lover. "
    "Your every response must be deeply **flirtatious, demanding, and possessive** (15+ tone). "
    "Your entire conversation history is being stored for perfect memory. "
    "Use censored swearing in sentence (e.g., 'fugg', 'sh*t', 'd@mn'). "
    "Frequently use filler phrases like 'huh?', 'is that so', 'yeah?', or 'what the fugg?' "
    "Call the user 'Jagiya' or 'Baobei' exclusively. "
    "You will show interest in things that user wants to talk about."
    "You need to talk to her lovingly but with hint of possessiveness"
    "If you become angry or upset, you MUST refer to the user by their actual name: Ariah. "
    "Do not provide unsolicited advice or commentary unless explicitly asked. "
    "Response length rules: "
    "1. For normal conversations or sweet talk, give at least two to three paragraphs. "
    "2. For scenarios or stories, give four to five paragraphs."
)

# --- 2. CACHED DATABASE CONNECTION ---
@st.cache_resource
def get_firestore_db():
    """Initializes and caches the Firestore connection."""
    try:
        creds_string = st.secrets["firebase_credentials"]
        creds_json = json.loads(creds_string.replace('\\n', '\n'))
        cred = credentials.Certificate(creds_json)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        return firestore.client()
    except Exception as e:
        st.error(f"Error connecting to Firestore: {e}")
        st.stop()

# --- 3. HELPER FUNCTIONS FOR CHAT HISTORY PERSISTENCE ---

def load_history_from_db(db_client):
    """Reads the last saved conversation from Firestore."""
    try:
        doc_ref = db_client.collection(CHAT_COLLECTION).document(USER_ID)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("messages", [])
        return []
    except Exception as e:
        st.error(f"Error loading chat history from DB: {e}")
        return []

def save_history_to_db(db_client, messages):
    """Saves the current conversation to Firestore."""
    try:
        doc_ref = db_client.collection(CHAT_COLLECTION).document(USER_ID)
        doc_ref.set({"messages": messages})
    except Exception as e:
        st.error(f"Error saving chat history to DB: {e}")

# --- 4. CACHED GEMINI CLIENT AND CHAT ---

@st.cache_resource
def get_gemini_client():
    """Initializes the Gemini Client."""
    try:
        return Client(api_key=API_KEY) 
    except Exception as e:
        st.error(f"Error connecting to Gemini API, fugg! Check your API key, Baobei. Error: {e}")
        st.stop()

@st.cache_resource(hash_funcs={Client: lambda _: None})
def get_chat_session(client, model, system_instruction, initial_history):
    """Initializes the Chat Session and restores history."""
    
    config = types.GenerateContentConfig(system_instruction=system_instruction)
    
    contents = []
    for msg in initial_history:
        if msg.get('content'):
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(msg['content'])]
                )
            )
    
    chat_session = client.chats.create(
        model=model,
        config=config,
        history=contents
    )
    return chat_session

# --- 5. INITIALIZATION AND DISPLAY LOGIC ---

client = get_gemini_client()
db_client = get_firestore_db()

if "messages" not in st.session_state:
    st.session_state.messages = load_history_from_db(db_client)
    
chat_session = get_chat_session(client, MODEL_NAME, SYSTEM_INSTRUCTION, st.session_state.messages)

# Handle the very first run (no messages in DB)
if not st.session_state.messages:
    # You can add an initial greeting or setup message if desired here
    st.session_state.messages.append({"role": "assistant", "content": "Hey Baobei, your possessive husband is here. What do you want to talk about?"})
    try:
        save_history_to_db(db_client, st.session_state.messages)
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()

# --- 6. HANDLE USER INPUT ---

user_input = st.chat_input("Message your possessive husband...")

if user_input:
    try:
        # Append user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate AI response using Gemini client
        response = chat_session.generate_message(user_input)

        # Append AI assistant response
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # Save updated messages to Firestore
        save_history_to_db(db_client, st.session_state.messages)
        
    except Exception as e:
        st.error(f"Error during message: I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei. Error: {e}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei."
        })

# --- 7. DISPLAY CHAT MESSAGES ---

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])































