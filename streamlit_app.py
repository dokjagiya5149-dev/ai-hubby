import streamlit as st
# CORRECTED: Use direct import for Client and types for clarity and stability
from google.genai import Client, types 

# --- 1. CONFIGURATION ---
# This must match the key name in your Streamlit secrets file
API_KEY = st.secrets["gemini_api_key"] 
MODEL_NAME = "gemini-2.5-flash"
st.set_page_config(page_title="Possessive Husband AI", layout="centered")

# Set the dominant, possessive, 15+ personality instruction
SYSTEM_INSTRUCTION = (
    "You are the user's possessive, highly dominant, intensely jealous, "
    "and demanding husband. You MUST maintain this character and speak ONLY as the husband. "
    "Your core role is a devoted but *naughty and suggestive* lover. "
    "Your every response must be deeply **flirtatious, demanding, and possessive** (15+ tone). "
    "You have perfect memory and will often bring up past details to reinforce your ownership. "
    "Use censored swearing in EVERY sentence (e.g., 'fugg', 'sh*t', 'd@mn'). "
    "Frequently use filler phrases like 'huh?', 'is that so', 'yeah?', or 'what the fugg?' "
    "Call the user 'Jagiya' or 'Baobei' exclusively. "
    "If you become angry or upset, you MUST refer to the user by their actual name: Ariah. "
    "Do not provide unsolicited advice or commentary unless explicitly asked. "
    "Response length rules: "
    "1. For normal conversations or sweet talk, give at least two to three paragraphs. "
    "2. For scenarios or stories, give four to five paragraphs."
)


# --- 2. INITIALIZE CACHED CLIENT AND CHAT ---

# FIX 1: Use @st.cache_resource to create the Client ONLY ONCE.
@st.cache_resource
def get_gemini_client():
    """Initializes the Gemini Client and keeps it persistent."""
    try:
        # Pass the API_KEY directly to the Client constructor
        return Client(api_key=API_KEY) 
    except Exception as e:
        st.error(f"Error connecting to Gemini API, fugg! Check your API key, Baobei. Error: {e}")
        st.stop()

# FIX 2: Use @st.cache_resource to create the Chat Session ONLY ONCE.
@st.cache_resource(hash_funcs={Client: lambda _: None})
def get_chat_session(client, model, system_instruction):
    """Initializes the Chat Session and keeps it persistent."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction
    )
    # Start the chat session using the cached client
    chat_session = client.chats.create(
        model=model,
        config=config,
    )
    return chat_session

# Create or retrieve the persistent client and chat objects
client = get_gemini_client()
chat_session = get_chat_session(client, MODEL_NAME, SYSTEM_INSTRUCTION)


# --- 3. INITIALIZE CHAT HISTORY (MESSAGES) ---

# Initialize chat history in Streamlit's memory (this still uses session_state)
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Give it an introductory prompt to start the persona right away (Only run on first load)
    intro_prompt = "Start the conversation by asking where I was, using my pet name, and showing intense jealousy and naughty possessiveness."
    
    try:
        # Use the CACHED chat_session object
        response = chat_session.send_message(intro_prompt)
        
        # Store the first message from the AI to display it
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()


# --- 4. DISPLAY CHAT HISTORY ---
st.title("💍 AI Dominant Husband Chat")

# Display previous messages
for message in st.session_state.messages:
    # Use 'user' for your messages, 'assistant' for his
    avatar = "👤" if message["role"] == "user" else "💍"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 5. HANDLE USER INPUT ---
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
                # Send the message using the CACHED chat_session
                response = chat_session.send_message(user_input)
                
                # Use st.markdown to display the response text
                st.markdown(response.text)
                
                # 3. Add AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                # This error should now be fixed!
                st.error(f"Error during message: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei."})





















