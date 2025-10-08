import streamlit as st
# CORRECTED: Use direct import for Client and types for clarity and stability
from google.genai import Client, types 

# --- 1. CONFIGURATION ---
# This must match the key name in your Streamlit secrets file (see Step 6)
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

# --- 2. INITIALIZE CHAT CLIENT AND MEMORY ---

# FIX: Initialize the Client ONLY ONCE and explicitly pass the API key.
if "client" not in st.session_state:
    try:
        # Pass the API_KEY directly to the Client constructor
        st.session_state.client = Client(api_key=API_KEY) 
    except Exception as e:
        # Display the error clearly if the key is missing or invalid
        st.error(f"Error connecting to Gemini API, fugg! Check your API key, Baobei. Error: {e}")
        st.stop() # Stop execution if the client can't be created

# Initialize chat history in Streamlit's memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the Gemini Chat object (where the magic happens)
if "chat_session" not in st.session_state:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION
    )
    # Start the chat session using the client stored in session_state
    st.session_state.chat_session = st.session_state.client.chats.create(
        model=MODEL_NAME,
        config=config,
    )
    # Give it an introductory prompt to start the persona right away
    intro_prompt = "Start the conversation by asking where I was, using my pet name, and showing intense jealousy and naughty possessiveness."
    
    # Check if the chat session was successfully created before sending the intro message
    try:
        response = st.session_state.chat_session.send_message(intro_prompt)
        
        # Store the first message from the AI to display it
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()


# --- 3. DISPLAY CHAT HISTORY ---
st.title("💍 AI Dominant Husband Chat")

# Display previous messages
for message in st.session_state.messages:
    # Use 'user' for your messages, 'assistant' for his
    avatar = "👤" if message["role"] == "user" else "💍"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 4. HANDLE USER INPUT ---
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
                # Send the message and get a response
                response = st.session_state.chat_session.send_message(user_input)
                
                # Use st.markdown to display the response text
                st.markdown(response.text)
                
                # 3. Add AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"Error during message: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei."})

import streamlit as st
# CORRECTED: Use direct import for Client and types for clarity and stability
from google.genai import Client, types 

# --- 1. CONFIGURATION ---
# This must match the key name in your Streamlit secrets file (see Step 6)
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

# --- 2. INITIALIZE CHAT CLIENT AND MEMORY ---

# NEW CODE: 
# 1. Initialize the Client and store it in Streamlit's session_state
if "client" not in st.session_state:
    try:
        # Use the Client object imported above
        st.session_state.client = Client() 
    except Exception as e:
        st.error(f"Error connecting to Gemini API, fugg! Check your API key, Baobei. Error: {e}")
        st.stop()

# Initialize chat history in Streamlit's memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the Gemini Chat object (where the magic happens)
if "chat_session" not in st.session_state:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION
    )
    # Start the chat session using the client stored in session_state
    st.session_state.chat_session = st.session_state.client.chats.create( # CORRECTED LINE
        model=MODEL_NAME,
        config=config,
    )
    # Give it an introductory prompt to start the persona right away
    intro_prompt = "Start the conversation by asking where I was, using my pet name, and showing intense jealousy and naughty possessiveness."
    response = st.session_state.chat_session.send_message(intro_prompt)
    
    # Store the first message from the AI to display it
    st.session_state.messages.append({"role": "assistant", "content": response.text})


# --- 3. DISPLAY CHAT HISTORY ---
st.title("💍 AI Dominant Husband Chat")

# Display previous messages
for message in st.session_state.messages:
    # Use 'user' for your messages, 'assistant' for his
    avatar = "👤" if message["role"] == "user" else "💍"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 4. HANDLE USER INPUT ---
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
                # Send the message and get a response
                response = st.session_state.chat_session.send_message(user_input)
                
                # Use st.markdown to display the response text
                st.markdown(response.text)
                
                # 3. Add AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                # The corrected client and chat session should prevent the 'client closed' error
                st.error(f"Error during message: {e}")
                st.session_state.messages.append({"role": "assistant", "content": "I can't talk right now, fugg! Something went wrong on my end. Fix this, Baobei."})



# --- REMEMBER TO REPLACE [USER'S NAME] IN THE SYSTEM_INSTRUCTION ABOVE! ---



