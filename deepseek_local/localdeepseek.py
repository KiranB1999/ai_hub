import streamlit as st
import ollama
import fitz  # PyMuPDF for PDF handling
from PIL import Image

# 🎨 Page Configuration
st.set_page_config(page_title="DeepSeek Chat - Local AI", layout="wide")

# 🚀 Sidebar: File Upload Section
with st.sidebar:
    st.header("📂 Uploaded Documents & Images")
    uploaded_files = st.file_uploader("Upload PDFs, TXT, PNG, JPG", accept_multiple_files=True)

    file_texts = []  # Stores extracted texts

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

# 🎭 Chat Layout (Two Columns)
col1, col2 = st.columns([2, 1])  # Chat on left, Files on right

# 💬 Chat History (Session State)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 💬 Chat Interface
with col1:
    st.title("🤖 DeepSeek Local Chat")

    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

    user_input = st.chat_input("Type your message here...")

    if user_input:
        # 🧠 Add user input to chat
        st.session_state.chat_history.append(("User", user_input))

        # 📜 Combine extracted text from files for context
        context = "\n".join(file_texts) if file_texts else ""
        prompt = f"Context:\n{context}\n\nUser: {user_input}\nDeepSeek:"

        # 🚀 Stream AI Response from Ollama
        response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}], stream=True)

        with st.chat_message("DeepSeek"):
            response_container = st.empty()
            bot_message = ""

            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    bot_message += chunk["message"]["content"]
                    response_container.markdown(bot_message)  # Live update message

            st.session_state.chat_history.append(("DeepSeek", bot_message))  # Save to history