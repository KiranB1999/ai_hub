function sendMessage() {
    let userInput = document.getElementById("userInput").value.trim();
    if (!userInput) return;

    let chatbox = document.getElementById("chatbox");

    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.innerText = userInput;
    chatbox.appendChild(userMessage);

    document.getElementById("userInput").value = "";

    let botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");
    botMessage.innerHTML = "<b>🤖 DeepSeek is typing...</b>";
    chatbox.appendChild(botMessage);

    fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        botMessage.innerHTML = "";
        let thinkMessage = document.createElement("div");
        thinkMessage.classList.add("think");
        thinkMessage.innerText = "<think> " + data.response + " </think>";
        chatbox.appendChild(thinkMessage);
    })
    .catch(() => {
        botMessage.innerText = "⚠️ Error: Unable to connect.";
    });

    chatbox.scrollTop = chatbox.scrollHeight;
}
