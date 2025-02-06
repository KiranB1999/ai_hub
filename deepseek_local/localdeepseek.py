import streamlit as st
import ollama
import fitz  # PyMuPDF for PDF handling
from PIL import Image
import json
import time

# 🎨 Page Configuration
st.set_page_config(page_title="DeepSeek Chat - Local AI", layout="wide")

# 💾 Load Chat History (Persistent Storage)
def load_chat_history():
    try:
        with open("chat_history.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_chat_history():
    with open("chat_history.json", "w") as file:
        json.dump(st.session_state.chat_history, file)

# 🔄 Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if "total_chats" not in st.session_state:
    st.session_state.total_chats = 0
if "avg_response_time" not in st.session_state:
    st.session_state.avg_response_time = 0

# 📂 Sidebar: File Upload Section
with st.sidebar:
    st.header("📂 Uploaded Documents & Images")
    uploaded_files = st.file_uploader("Upload PDFs, TXT, PNG, JPG", accept_multiple_files=True)

    file_texts = []
    if uploaded_files:
        st.markdown("### 📑 Uploaded Files")
        for file in uploaded_files:
            file_ext = file.name.split(".")[-1].lower()
            if file_ext in ["png", "jpg", "jpeg"]:
                image = Image.open(file)
                st.image(image, caption=file.name, use_column_width=True)
            elif file_ext in ["pdf", "txt"]:
                with st.expander(f"📄 {file.name} (Click to Preview)"):
                    if file_ext == "pdf":
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        text = "\n".join([page.get_text() for page in doc])
                    else:
                        text = file.read().decode("utf-8")
                    st.text_area("Extracted Text:", text, height=150)
                    file_texts.append(text)

# 📖 AI-Powered Document Q&A
st.sidebar.subheader("📖 Ask AI about uploaded documents:")
doc_question = st.sidebar.text_input("Type your question...")

if doc_question and file_texts:
    doc_context = "\n".join(file_texts)
    prompt = f"Based on the uploaded document:\n\n{doc_context}\n\nUser's Question: {doc_question}\nDeepSeek Answer:"
    
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}], stream=False)
    
    st.sidebar.write("**📜 AI Answer:**", response["message"]["content"])

# 🎭 Chat Layout - Messages Above, Input Below
st.title("🤖 DeepSeek Chat - Local AI")

# 🔄 Dark Mode Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #0e1117; color: white; }
        .stTextInput, .stChatMessage, .stTextArea { background-color: #262730 !important; color: white !important; }
        </style>
        """, 
        unsafe_allow_html=True
    )

# 💬 Display Chat History
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

# ⌨️ Chat Input (Below Chat)
user_input = st.chat_input("Type your message here...")

if user_input:
    # 📝 Add User Input to Chat
    st.session_state.chat_history.append(("User", user_input))

    # 📜 Choose AI Memory Mode
    context_mode = st.sidebar.radio("Context Mode", ["Recent Only", "Full History"])
    if context_mode == "Recent Only":
        limited_history = st.session_state.chat_history[-5:]  # Last 5 messages
    else:
        limited_history = st.session_state.chat_history  # Full history

    prompt = f"{limited_history}\n\nUser: {user_input}\nDeepSeek:"

    # 🚀 Stream AI Response with "Thinking" Animation
    with st.chat_message("DeepSeek"):
        response_container = st.empty()
        bot_message = ""

        # 🧠 Show "thinking" animation while DeepSeek generates response
        with response_container:
            st.markdown("🤖 *DeepSeek is thinking...* ⏳")
            time.sleep(2)

        # 💬 Stream AI Response from Ollama (Word by Word Typing Effect)
        start_time = time.time()
        response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}], stream=True)

        bot_response_text = ""
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                bot_response_text += chunk["message"]["content"]
                response_container.markdown(bot_response_text + " █")  # Typing effect

        response_container.markdown(bot_response_text)  # Final response
        response_time = time.time() - start_time

        # 💾 Save AI Response to Chat History
        st.session_state.chat_history.append(("DeepSeek", bot_response_text))
        save_chat_history()

        # 🔢 Update Stats
        st.session_state.total_chats += 1
        st.session_state.avg_response_time = (
            (st.session_state.avg_response_time * (st.session_state.total_chats - 1) + response_time)
            / st.session_state.total_chats
        )

# 📊 AI Analytics Dashboard
st.sidebar.subheader("📊 AI Chat Stats")
st.sidebar.write(f"🗣️ Total Chats: {st.session_state.total_chats}")
st.sidebar.write(f"⏳ Avg Response Time: {st.session_state.avg_response_time:.2f} sec")