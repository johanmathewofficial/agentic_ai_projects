import os
import streamlit as st
from ollama import Client

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ollama Cloud Chat",
    page_icon="☁️",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0a0e1a; color: #e2e8f0; }

    .chat-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.5rem;
    }
    .chat-header h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        background: linear-gradient(90deg, #818cf8, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .chat-header p { color: #64748b; font-size: 0.85rem; margin-top: 4px; }

    .msg-user {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px 12px 2px 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 0.5rem 3rem;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .msg-assistant {
        background: #0f172a;
        border: 1px solid #1d4ed8;
        border-radius: 12px 12px 12px 2px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 3rem 0.5rem 0;
        color: #bfdbfe;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .msg-label {
        font-size: 0.7rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .label-user { color: #94a3b8; }
    .label-bot  { color: #60a5fa; }

    [data-testid="stSidebar"] {
        background-color: #080c18;
        border-right: 1px solid #1e293b;
    }

    .stButton > button {
        background: #1d4ed8;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #2563eb; }

    .api-key-set {
        display: inline-block;
        background: #052e16;
        color: #4ade80;
        border: 1px solid #166534;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .api-key-missing {
        display: inline-block;
        background: #2d0000;
        color: #f87171;
        border: 1px solid #7f1d1d;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
OLLAMA_CLOUD_HOST = "https://ollama.com"

# Reads from:  set OLLAMA_API_KEY=your_key   (Windows CMD)
API_KEY = os.environ.get("OLLAMA_API_KEY", "")

CLOUD_MODELS = [
    "gpt-oss:120b",
    "gpt-oss:20b",
    "deepseek-v3.1:671b-cloud",
    "qwen3-coder:480b-cloud",
    "llama4:maverick",
    "llama4:scout",
    "gemma3:27b",
    "mistral:latest",
]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☁️ Ollama Cloud")
    st.markdown("---")

    if API_KEY:
        st.markdown('<span class="api-key-set">● API Key Loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-key-missing">✕ OLLAMA_API_KEY not set</span>', unsafe_allow_html=True)
        st.caption("In CMD:  `set OLLAMA_API_KEY=your_key`")

    st.markdown("")
    selected_model = st.selectbox("Cloud Model", CLOUD_MODELS)

    st.markdown("---")
    st.markdown("**System Prompt**")
    system_prompt = st.text_area(
        "sys",
        value="You are a helpful, concise assistant.",
        height=120,
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='color:#475569;font-size:0.75rem;text-align:center'>"
        "Powered by <code style='color:#60a5fa'>ollama.com</code> Cloud</p>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h1>☁️ Ollama Cloud Chat</h1>
    <p>Remote Inference · No Local GPU Required</p>
</div>
""", unsafe_allow_html=True)

# ── Guard: no API key ─────────────────────────────────────────────────────────
if not API_KEY:
    st.warning(
        "**OLLAMA_API_KEY is not set.**\n\n"
        "In your VSCode CMD terminal run:\n"
        "```\n"
        "set OLLAMA_API_KEY=your_api_key_here\n"
        "streamlit run ollama_cloud_chatbot.py\n"
        "```\n\n"
        "Get your key → https://ollama.com/settings/keys"
    )
    st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-label label-user">YOU</div>'
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-label label-bot">☁️ {selected_model.upper()}</div>'
            f'<div class="msg-assistant">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type a message…")

if user_input:
    # Save & show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(
        f'<div class="msg-label label-user">YOU</div>'
        f'<div class="msg-user">{user_input}</div>',
        unsafe_allow_html=True,
    )

    # Build message list for Ollama
    ollama_messages = []
    if system_prompt.strip():
        ollama_messages.append({"role": "system", "content": system_prompt.strip()})
    ollama_messages += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Ollama Cloud client
    client = Client(
        host=OLLAMA_CLOUD_HOST,
        headers={"Authorization": f"Bearer {API_KEY}"},
    )

    # Stream the response
    st.markdown(
        f'<div class="msg-label label-bot">☁️ {selected_model.upper()}</div>',
        unsafe_allow_html=True,
    )
    placeholder = st.empty()
    full_response = ""

    try:
        for part in client.chat(selected_model, messages=ollama_messages, stream=True):
            token = part["message"]["content"]
            full_response += token
            placeholder.markdown(
                f'<div class="msg-assistant">{full_response}▌</div>',
                unsafe_allow_html=True,
            )

        # Final without cursor
        placeholder.markdown(
            f'<div class="msg-assistant">{full_response}</div>',
            unsafe_allow_html=True,
        )
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            placeholder.error("❌ Invalid API key — check https://ollama.com/settings/keys")
        elif "404" in err:
            placeholder.error(f"❌ Model '{selected_model}' not found on Ollama Cloud.")
        elif "connect" in err.lower():
            placeholder.error("❌ Cannot reach ollama.com — check your internet connection.")
        else:
            placeholder.error(f"❌ Error: {e}")