import streamlit as st
import ollama
import json
import time
import os
from datetime import datetime
import re  # For regex processing

# 🎨 Page Configuration
st.set_page_config(page_title="DeepSeek Chat - Multi-Session", layout="wide")

# 🌑 Apply Dark Mode Styling (Black Background, White Text)
st.markdown(
    """
    <style>
        body { background-color: black; color: white; }
        .stApp { background-color: black !important; }
        .stTextInput, .stChatMessage, .stTextArea, .stButton, .stMarkdown, .stTitle, .stHeader, .stSubheader, .stCodeBlock, .stDataFrame, .stTable { 
            background-color: black !important; color: white !important; 
        }
        .stChatMessage { border-radius: 10px; padding: 10px; }
        .stButton>button { background-color: #444 !important; color: white !important; }
        .stMarkdown span { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# 💾 File to store chat history
CHAT_HISTORY_FILE = "chat_sessions.json"

# 📝 Load and Save Chat History
def load_chat_sessions():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # Return an empty dictionary if JSON is corrupted
    return {}

def save_chat_sessions():
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(st.session_state.chat_sessions, file, indent=4)

# 🔄 Initialize Session State
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chat_sessions()

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None  # No chat selected initially

if "editing_chat" not in st.session_state:
    st.session_state.editing_chat = None  # Track which chat is being renamed

# 📂 Sidebar - Chat List & Controls
with st.sidebar:
    st.title("📂 Chat Sessions")

    # 🆕 New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = f"chat_{int(time.time())}"  # Unique ID
        st.session_state.chat_sessions[new_chat_id] = {
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        st.session_state.active_chat = new_chat_id
        save_chat_sessions()

    # 📜 Show list of existing chats
    for chat_id, chat_data in sorted(st.session_state.chat_sessions.items(), key=lambda x: x[1]["created_at"], reverse=True):
        cols = st.columns([0.7, 0.15, 0.15])

        if st.session_state.editing_chat == chat_id:
            new_name = cols[0].text_input("Rename chat:", chat_data["title"], key=f"rename_{chat_id}")
            if cols[1].button("✔️", key=f"save_{chat_id}"):
                st.session_state.chat_sessions[chat_id]["title"] = new_name
                st.session_state.editing_chat = None
                save_chat_sessions()
                st.rerun()
        else:
            if cols[0].button(chat_data["title"], use_container_width=True, key=f"chat_{chat_id}"):
                st.session_state.active_chat = chat_id
            if cols[1].button("✏️", key=f"edit_{chat_id}"):
                st.session_state.editing_chat = chat_id
                st.rerun()
            if cols[2].button("🗑️", key=f"delete_{chat_id}"):
                del st.session_state.chat_sessions[chat_id]
                save_chat_sessions()
                st.rerun()

# 🎭 Main Chat Interface
st.title("🤖 DeepSeek Chat - Multi-Session")

if st.session_state.active_chat and st.session_state.active_chat in st.session_state.chat_sessions:
    chat_id = st.session_state.active_chat
    chat_data = st.session_state.chat_sessions[chat_id]

    st.subheader(chat_data["title"])

    # 💬 Display Chat History
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            content = msg["content"]

            # ✅ Ensure <think> parts are shown in gray
            if "<think>" in content and "</think>" in content:
                think_parts = re.findall(r"<think>(.*?)</think>", content, flags=re.DOTALL)
                for think_text in think_parts:
                    content = content.replace(
                        f"<think>{think_text}</think>",
                        f'<span style="color:gray;">{think_text}</span>'
                    )

            # ✅ Display the formatted response
            st.markdown(f"<span style='color:white;'>{content}</span>", unsafe_allow_html=True)

    # ⌨️ Chat Input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        chat_data["messages"].append({"role": "User", "content": user_input})

        with st.chat_message("DeepSeek"):
            response_container = st.empty()
            response_container.markdown("🤖 *DeepSeek is thinking...* ⏳")
            time.sleep(1.5)

        response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": user_input}], stream=False)

        bot_response = response["message"]["content"]

        # ✅ Preserve <think> sections and format them in gray
        if "<think>" in bot_response and "</think>" in bot_response:
            think_parts = re.findall(r"<think>(.*?)</think>", bot_response, flags=re.DOTALL)
            for think_text in think_parts:
                bot_response = bot_response.replace(
                    f"<think>{think_text}</think>",
                    f'<span style="color:gray;">{think_text}</span>'
                )

        chat_data["messages"].append({"role": "DeepSeek", "content": bot_response})

        save_chat_sessions()
        st.rerun()

else:
    st.warning("⚠️ Selected chat does not exist. Please select another chat or start a new one.")