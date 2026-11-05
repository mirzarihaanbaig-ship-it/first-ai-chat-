import streamlit as st
from groq import Groq
import requests
import re
from PIL import Image

# Page Config
st.set_page_config(page_title="AI Search & Study Assistant", page_icon="🤖", layout="wide")

# Initialize Groq client
client = Groq(api_key="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")

# --- Session State Initialization for Multiple Chats ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# --- Sidebar: Recents & New Chat ---
st.sidebar.title("💬 Recent Chats")
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_chat_name = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_name] = []
    st.session_state.current_chat = new_chat_name
    st.rerun()

st.sidebar.markdown("---")
chat_selected = st.sidebar.radio(
    "Switch Chat", 
    list(st.session_state.chats.keys()), 
    index=list(st.session_state.chats.keys()).index(st.session_state.current_chat)
)
if chat_selected != st.session_state.current_chat:
    st.session_state.current_chat = chat_selected
    st.rerun()

# Main Header
st.title("🤖 AI Study & Search Assistant")
st.caption("CREATED BY MIRZA RIHAAN BAIG")

# --- File / Photo Upload Option ---
uploaded_file = st.file_uploader("📁 Upload a photo or document (optional)", type=["png", "jpg", "jpeg", "pdf", "txt"])

# Helper function to clean search prompts
def clean_prompt_for_search(text):
    text = re.sub(r'(?i)\b(what is|what are|tell me about|who is|where is|show me|explain|details on)\b', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Function to fetch accurate image URL from Wikipedia API
def get_wikipedia_image(query):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={query}&prop=pageimages&format=json&pithumbsize=600"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        pages = response['query']['pages']
        for page_id in pages:
            if 'thumbnail' in pages[page_id]:
                return pages[page_id]['thumbnail']['source']
    except Exception:
        pass
    return None

# Load current chat messages
messages = st.session_state.chats[st.session_state.current_chat]

# Display past messages
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            st.image(message["image"], caption=message.get("caption", ""))

# User Input
if prompt := st.chat_input("Ask a question or describe your file..."):
    # Handle uploaded file context
    file_context = ""
    if uploaded_file is not None:
        file_context = f"[Uploaded file: {uploaded_file.name}] "

    full_user_prompt = file_context + prompt
    messages.append({"role": "user", "content": full_user_prompt})
    
    with st.chat_message("user"):
        st.markdown(full_user_prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking..."):
            try:
                system_prompt = (
                    "You are a helpful AI assistant. "
                    "Provide a clear, informative breakdown, description, or facts about whatever the user asks."
                )

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[
                            {"role": m["role"], "content": m["content"]}
                            for m in messages
                        ]
                    ],
                )
                
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)
                
                # Fetch exact matching image from Wikipedia based on clean prompt
                search_keyword = clean_prompt_for_search(prompt)
                img_url = get_wikipedia_image(search_keyword)
                
                if img_url:
                    st.image(img_url, caption=f"Photo of: {search_keyword}")
                
                # Save assistant response to session state
                messages.append({
                    "role": "assistant", 
                    "content": ai_response, 
                    "image": img_url, 
                    "caption": f"Photo of: {search_keyword}" if img_url else ""
                })
            except Exception as e:
                st.error(f"Error: {e}")