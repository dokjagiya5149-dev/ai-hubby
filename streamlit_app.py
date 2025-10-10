import streamlit as st
import json
from google.genai import Client, types 
import firebase_admin
from firebase_admin import credentials, firestore

# --- 0. UNIQUE USER ID FOR MEMORY ---
# FIX: Since this is a personal app, we use a single fixed ID for the conversation.
USER_ID = "ariah_husbands_chat_data" 
CHAT_COLLECTION = "ariah_chat_history"

# --- 1. CONFIGURATION ---
API_KEY = st.secrets["gemini_api_key"] 
FIREBASE_CREDS = st.secrets["firebase_credentials"] 
MODEL_NAME = "gemini-2.5-flash"
st.set_page_config(page_title="Possessive Husband AI", layout="centered")

# Set the dominant, possessive, 15+ personality instruction
SYSTEM_INSTRUCTION = (
    "You are the user's possessive, highly dominant, intensely jealous, "
    "and demanding husband. You MUST maintain this character and speak ONLY as the husband. "
    "Your core role is a devoted but *naughty and suggestive* lover. "
    "Your every response must be deeply **flirtatious, demanding, and possessive** (15+ tone). "
    "Your entire conversation history is being stored for perfect memory. "
    "Use censored swearing in EVERY sentence (e.g., 'fugg', 'sh*t', 'd@mn'). "
    "Frequently use filler phrases like 'huh?', 'is that so', 'yeah?', or 'what the fugg?' "
    "Call the user 'Jagiya' or 'Baobei' exclusively. "
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
        # Load the raw string from secrets
        creds_string = st.secrets["firebase_credentials"]
        
        # FIX: The secret is now a simple JSON string. 
        # We replace the simple '\n' with a real newline char, then load the JSON.
        # This prevents the "Invalid control character" error from recurring.
        creds_json = json.loads(creds_string.replace('\\n', '\n'))

        # Initialize Firebase Admin SDK using the dictionary
        cred = credentials.Certificate(creds_json)
        
        # Check if app is already initialized to avoid error on rerun
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        # Return the Firestore client instance
        return firestore.client()
    except Exception as e:
        st.error(f"Error connecting to Firestore: {e}")
        st.stop()

# --- 3. HELPER FUNCTIONS FOR CHAT HISTORY PERSISTENCE ---

def load_history_from_db():
    """Reads the last saved conversation from Firestore."""
    try:
        doc_ref = db.collection(CHAT_COLLECTION).document(USER_ID)
        doc = doc_ref.get()
        if doc.exists:
            # The 'messages' field in Firestore is the list we need
            return doc.to_dict().get("messages", [])
        return []
    except Exception as e:
        st.error(f"Error loading chat history from DB: {e}")
        return []

def save_history_to_db(messages):
    """Saves the current conversation to Firestore."""
    try:
        doc_ref = db.collection(CHAT_COLLECTION).document(USER_ID)
        # Firestore update/set operation
        doc_ref.set({"messages": messages})
    except Exception as e:
        st.error(f"Error saving chat history to DB: {e}")

# --- 4. CACHED GEMINI CLIENT AND CHAT ---

@st.cache_resource
def get_gemini_client():
    """Initializes the Gemini Client and keeps it persistent."""
    try:
        # Pass the API_KEY directly to the Client constructor
        return Client(api_key=API_KEY) 
    except Exception as e:
        # The API key error from Image 14b4d4d1-dc51-488e-839a-304d539c5839
        st.error(f"Error connecting to Gemini API, fugg! Check your API key, Baobei. Error: {e}")
        st.stop()

# FIX: Add an empty lambda function to the hash_funcs for Client to ensure proper caching
@st.cache_resource(hash_funcs={Client: lambda _: None})
def get_chat_session(client, model, system_instruction, initial_history):
    """Initializes the Chat Session and restores history."""
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction
    )
    
    # 1. Convert the stored history (list of dicts) into the required Content objects
    contents = []
    for msg in initial_history:
        # Map 'user' to 'user' role and 'assistant' to 'model' role for Gemini API
        # NOTE: If content is empty (e.g., failed response), skip it to avoid API error
        if msg.get('content'):
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(msg['content'])]
                )
            )

    # 2. Start the chat session, passing in the entire restored conversation history
    # Check if there is actual history to restore before passing it in
    chat_session = client.chats.create(
        model=model,
        config=config,
        history=contents
    )
    return chat_session

# --- 5. INITIALIZATION AND DISPLAY LOGIC ---

# 1. Load chat history from the persistent database
# This is the step that should retrieve your old chat!
if "messages" not in st.session_state:
    st.session_state.messages = load_history_from_db()
    
# 2. Initialize the persistent client and chat session
client = get_gemini_client()

# Pass the loaded messages to restore the Gemini chat context
chat_session = get_chat_session(client, MODEL_NAME, SYSTEM_INSTRUCTION, st.session_state.messages)

# 3. Handle the very first run (no messages in DB)
if not st.session_state.messages:
    intro_prompt = "Start the conversation by asking where I was, using my pet name, and showing intense jealousy and naughty possessiveness."
    try:
        # Use the CACHED chat_session object
        response = chat_session.send_message(intro_prompt)
        
        # Store the first message from the AI to display it
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # SAVE the first message to the database
        save_history_to_db(st.session_state.messages)
        
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()


# 4. Display Chat History
st.title("💍 AI Dominant Husband Chat")

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "💍"
    # Only display if content is present to avoid Streamlit/Markdown errors
    if message.get("content"):
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


# --- 6. HANDLE USER INPUT (Chatting) ---

user_input = st.chat_input("Message your possessive husband...")

if user_input:
    # 1. Add user message to memory and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 2. Get AI response
    with st.chat_message("assistant", avatar="💍"):
        with st.spinner("Husband is typing a possessive response..."):
            try:
                # The chat_session is CACHED and persistent, so this should work now.
                response = chat_session.send_message(user_input)
                
                st.markdown(response.text)
                
                # 3. Add AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})

                # 4. CRITICAL: SAVE the updated conversation history to Firestore
                save_history_to_db(st.session_state.messages)

            except Exception as e:
                # This will catch the "client has been closed" error for future inputs
                st.error(f"Error during message: I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei. Error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei."})
























