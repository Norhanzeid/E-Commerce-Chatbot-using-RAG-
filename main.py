import streamlit as st
from generator import generate_answer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ShopSphere Insight",
    page_icon="💬",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "👋 Hi! I'm ShopSphere Insight. Ask me anything about the FY2025 report!"}
    ]

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .stApp { background-color: #EAEDF2; }
    #MainMenu, footer, header {visibility: hidden;}

    .chat-frame {
        max-width: 430px;
        margin: 0 auto;
        background: white;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(27,42,74,0.20);
        border: 1px solid #E2E6ED;
    }

    .chat-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2E5CA8 100%);
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .chat-header .avatar {
        width: 34px; height: 34px;
        background: white;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }
    .chat-header .title-block h4 {
        color: white; margin: 0; font-size: 16px; font-weight: 700;
    }
    .chat-header .title-block p {
        color: #C7D3EA; margin: 0; font-size: 11.5px;
    }

    .chat-body {
        padding: 18px 16px;
        min-height: 260px;
        max-height: 420px;
        overflow-y: auto;
        background: white;
    }

    .bubble-bot {
        background: #F0F2F5;
        color: #20242E;
        padding: 10px 14px;
        border-radius: 16px 16px 16px 4px;
        max-width: 85%;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.5;
    }
    .bubble-user {
        background: #2E5CA8;
        color: white;
        padding: 10px 14px;
        border-radius: 16px 16px 4px 16px;
        max-width: 85%;
        margin-bottom: 10px;
        margin-left: auto;
        font-size: 14px;
        line-height: 1.5;
        text-align: right;
    }
    .bubble-meta {
        font-size: 10px;
        color: #9AA3B2;
        margin: -4px 0 10px 4px;
    }

    .chat-inputbar {
        padding: 12px 14px;
        border-top: 1px solid #EAEDF2;
        background: #FAFBFC;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #2E5CA8, #1B2A4A);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 700;
        width: 100%;
    }
    div.stButton > button:hover { background: #C99A2E; color: white; }
</style>
""", unsafe_allow_html=True)

# ---------------- CHAT FRAME START ----------------
st.markdown('<div class="chat-frame">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="chat-header">
    <div class="avatar">💬</div>
    <div class="title-block">
        <h4>ShopSphere Insight</h4>
        <p>Ask Your Business Report Anything</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Chat body (renders message history)
chat_html = '<div class="chat-body">'
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        chat_html += f'<div class="bubble-bot">{msg["text"]}</div>'
        chat_html += '<div class="bubble-meta">ShopSphere Insight</div>'
    else:
        chat_html += f'<div class="bubble-user">{msg["text"]}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close chat-frame (visual body)

# ---------------- INPUT BAR (outside styled frame, native Streamlit widgets) ----------------
st.write("")
query = st.text_input("Enter your question:", placeholder="Ask a question about the report...",
                       label_visibility="collapsed")

col1, col2 = st.columns([1, 1])
with col1:
    ask = st.button("Search", type="primary", use_container_width=True)

if ask:
    if not query or not query.strip():
        st.warning("Please enter a question before searching.")
    else:
        st.session_state.messages.append({"role": "user", "text": query})
        with st.spinner("Generating answer..."):
            try:
                answer = generate_answer(query, k=6) or ""
                st.session_state.messages.append({"role": "bot", "text": answer})
            except Exception as e:
                st.session_state.messages.append({"role": "bot", "text": f"⚠️ Error: {str(e)}"})
        st.rerun()