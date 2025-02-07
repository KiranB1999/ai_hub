# DeepSeek Chat - Local AI

This project leverages **DeepSeek** models with **Streamlit** to create a 100% locally running AI-powered chat application.

---

## 🚀 Installation and Setup

### **1️⃣ Install Ollama**
Ollama is required to run DeepSeek models locally. Install it using:

#### **For Linux & Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
#### **For Windows:**
Download and install Ollama from the official website:  
🔗 [Ollama Official Site](https://ollama.com/)

Once installed, **pull the DeepSeek model**:
```bash
ollama pull deepseek-chat
```

---

### **2️⃣ Install Dependencies**
Ensure you have **Python 3.11+** installed. Then, install the required Python libraries:

```bash
pip install streamlit ollama
```

---

### **3️⃣ Run the Application**
To start the chat application, run:

```bash
streamlit run app.py
```

This will launch the **DeepSeek Chat** app in your browser.

---

## 🛠️ Troubleshooting

### **Q: The model isn't responding. What do I do?**  
🔹 Ensure **Ollama** is running (`ollama list` should show available models).  
🔹 Try restarting Ollama:  
```bash
ollama stop
ollama run deepseek-chat
```

### **Q: I get `ModuleNotFoundError` when running the script.**  
🔹 Install missing dependencies using:  
```bash
pip install -r requirements.txt
```

### **Q: How do I reset the chat sessions?**  
🔹 Delete the `chat_sessions.json` file in your project directory.

---


