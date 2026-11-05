import streamlit as st
from groq import Groq

st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")

st.title("🤖 AI Study Assistant Chatbot")
st.caption("CREATED BY MIRZA RIHAAN BAIG AND VAISHNAV (SEO)")
st.write("Ask me anything about your studies or coding!")

# 1. Initialize the Groq client 
# (Replace with your free API key from console.groq.com)
client = Groq(api_key="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")

# 2. Store chat history in Streamlit session state so it doesn't disappear on refresh
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display past messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Accept user input from the chat box at the bottom
if prompt := st.chat_input("What is on your mind?"):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Generate the AI response using Groq API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                )
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)
                
                # Add assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Error: Please make sure your API key is correct. Details: {e}")