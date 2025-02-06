import streamlit as st
import ollama
import fitz  # PyMuPDF for PDF handling
from PIL import Image
import time

# 🎨 Page Configuration
st.set_page_config(page_title="DeepSeek Chat - Local AI", layout="wide")

# 💾 Initialize Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📂 Sidebar: File Upload Section
with st.sidebar:
    st.header("📂 Uploaded Documents & Images")
    uploaded_files = st.file_uploader("Upload PDFs, TXT, PNG, JPG", accept_multiple_files=True)

    file_texts = []  # Stores extracted texts
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

# 📜 Chat Layout - Chat messages above, input below
st.title("🤖 DeepSeek Chat - Local AI")

# 📢 Display Chat History
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

# ⌨️ Chat Input Area (Now Below Chat History)
user_input = st.chat_input("Type your message here...")

if user_input:
    # 📝 Add User Input to Chat
    st.session_state.chat_history.append(("User", user_input))

    # 📜 Combine extracted text from uploaded files for context
    context = "\n".join(file_texts) if file_texts else ""
    prompt = f"Context:\n{context}\n\nUser: {user_input}\nDeepSeek:"

    # 🚀 Stream AI Response with "Thinking" Animation
    with st.chat_message("DeepSeek"):
        response_container = st.empty()
        bot_message = ""

        # 🧠 Show "thinking" animation while DeepSeek generates response
        with response_container:
            st.markdown("🤖 *DeepSeek is thinking...* ⏳")
            time.sleep(2)  # Simulate delay before response starts

        # 💬 Stream AI Response from Ollama (Word by Word Typing Effect)
        response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}], stream=True)

        bot_response_text = ""
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                bot_response_text += chunk["message"]["content"]
                response_container.markdown(bot_response_text + " █")  # Typing effect

        response_container.markdown(bot_response_text)  # Final response

        # 💾 Save AI Response to Chat History
        st.session_state.chat_history.append(("DeepSeek", bot_response_text))
