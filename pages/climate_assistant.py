# =============================================================================
# EcoGuard AI - Climate Assistant Page
# =============================================================================
# Powered by IBM watsonx.ai · ibm/granite-4-h-small
#
# Chat history is stored in st.session_state["chat_messages"] as a list of
#   {"role": "user"|"assistant", "content": str}
# entries so previous turns survive Streamlit reruns.
#
# Connection status is tested once per session (not on every rerun) using
# utils/watsonx_client.test_connection().
# =============================================================================

import streamlit as st

from utils.ui_components import (
    page_header, section_divider, chat_user, chat_bot, footer,
)
from utils.watsonx_client import test_connection
from modules.climate_chatbot import get_chatbot_response, list_supported_topics

# ---------------------------------------------------------------------------
# Quick-start topic buttons
# ---------------------------------------------------------------------------

QUICK_TOPICS = [
    ("🌡️", "Heatwaves",      "Why are heatwaves increasing?"),
    ("🌧️", "Heavy Rain",     "How does heavy rainfall cause flooding?"),
    ("🧊", "Melting Ice",    "How does melting ice affect sea level?"),
    ("🌊", "Sea Level",      "What are the effects of rising sea levels?"),
    ("🌳", "Deforestation",  "How does deforestation affect climate change?"),
    ("♻️", "Sustainability", "How can I reduce my carbon footprint?"),
]

# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------

def _init_session():
    """Initialise session state keys on first load."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm EcoGuard AI, powered by IBM watsonx.ai (Granite). "
                    "I can answer questions about climate change, extreme weather, "
                    "sustainability, carbon footprints, biodiversity, and the UN SDGs. "
                    "What would you like to know?"
                ),
            }
        ]
    # Persistent connection status: None = not tested, True = ok, False = failed
    if "watsonx_connected" not in st.session_state:
        st.session_state.watsonx_connected = None
    if "watsonx_status_msg" not in st.session_state:
        st.session_state.watsonx_status_msg = ""


# ---------------------------------------------------------------------------
# Connection status bar
# ---------------------------------------------------------------------------

def _render_status():
    """
    Show the IBM connection status.  Run the test once per session (not on
    every rerun) — testing on every rerun would send unnecessary IBM requests.
    """
    col_info, col_test = st.columns([5, 1])

    with col_info:
        if st.session_state.watsonx_connected is True:
            st.success(
                f"🤖 **Powered by IBM watsonx.ai · Granite** — "
                f"{st.session_state.watsonx_status_msg}"
            )
        elif st.session_state.watsonx_connected is False:
            st.warning(
                f"⚠️ IBM watsonx.ai not available — "
                f"{st.session_state.watsonx_status_msg}"
            )
        else:
            st.info("🤖 **Powered by IBM watsonx.ai · Granite** — Click 'Test' to verify connection.")

    with col_test:
        if st.button("🔌 Test", key="wx_test_btn", width="stretch",
                     help="Send a test request to verify IBM watsonx.ai is reachable"):
            with st.spinner("Testing IBM connection…"):
                ok, msg = test_connection()
            st.session_state.watsonx_connected  = ok
            st.session_state.watsonx_status_msg = msg
            st.rerun()


# ---------------------------------------------------------------------------
# Message processor — adds to session history and calls Granite
# ---------------------------------------------------------------------------

def _process_message(question: str):
    """
    Append the user question to chat history, call IBM Granite, and append
    the assistant response.  Uses existing history for multi-turn context.
    """
    # Only add if this message isn't already the last user message (avoid duplicates)
    msgs = st.session_state.chat_messages
    if msgs and msgs[-1]["role"] == "user" and msgs[-1]["content"] == question:
        return

    # Append user turn
    msgs.append({"role": "user", "content": question})

    # Build history for multi-turn (exclude the opening greeting)
    context_history = [
        {"role": m["role"], "content": m["content"]}
        for m in msgs[1:-1]   # skip the assistant greeting; the current user msg is last
        if m["role"] in ("user", "assistant")
    ]

    # Call IBM Granite
    with st.spinner("🤖 EcoGuard AI is thinking…"):
        response = get_chatbot_response(question, history=context_history)

    msgs.append({"role": "assistant", "content": response})

    # Mark connection as confirmed if we got a real response (not an error msg)
    if not response.startswith("⚠️") and st.session_state.watsonx_connected is not True:
        st.session_state.watsonx_connected  = True
        st.session_state.watsonx_status_msg = "Connected to IBM watsonx.ai · ibm/granite-4-h-small"


# ---------------------------------------------------------------------------
# Main page renderer
# ---------------------------------------------------------------------------

def show():
    _init_session()

    page_header(
        "🤖", "EcoGuard Climate Assistant",
        "Ask questions about climate change, extreme weather, sustainability, and environmental protection.",
    )

    # ── Connection status bar ──────────────────────────────────────────────
    _render_status()

    # ── Quick-topic buttons ────────────────────────────────────────────────
    section_divider("⚡ QUICK QUESTIONS")
    btn_cols = st.columns(3)
    quick_clicked = None
    for i, (icon, label, question) in enumerate(QUICK_TOPICS):
        with btn_cols[i % 3]:
            if st.button(f"{icon} {label}", key=f"quick_{i}", width="stretch"):
                quick_clicked = question

    # ── Conversation display ───────────────────────────────────────────────
    section_divider("💬 CONVERSATION")
    with st.container():
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                chat_user(msg["content"])
            else:
                chat_bot(msg["content"])

    # ── Handle quick-topic click (before input box so it shows above it) ──
    if quick_clicked:
        _process_message(quick_clicked)
        st.rerun()

    # ── Handle Home page prefill (from "Ask EcoGuard →" button) ──────────
    prefill = st.session_state.pop("assistant_prefill", None)
    if prefill:
        _process_message(prefill)
        st.rerun()

    # ── Text input + Send button ───────────────────────────────────────────
    section_divider("✏️ ASK A QUESTION")
    ic, bc = st.columns([5, 1])
    with ic:
        user_input = st.text_input(
            "Question",
            placeholder="Ask EcoGuard anything about climate or sustainability…",
            label_visibility="collapsed",
            key="climate_chat_input",
        )
    with bc:
        send = st.button("➤ Ask", key="climate_chat_send", width="stretch")

    if send and user_input.strip():
        _process_message(user_input.strip())
        st.rerun()
    elif send:
        st.warning("Please enter a question before clicking Ask.")

    # ── Clear conversation ─────────────────────────────────────────────────
    if st.button("🗑️ Clear Conversation", key="chat_clear"):
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! Ask me anything about climate change or sustainability.",
            }
        ]
        st.rerun()

    # ── Topics footer ──────────────────────────────────────────────────────
    section_divider("📚 TOPICS I CAN ANSWER")
    topics = list_supported_topics()
    st.markdown(
        "  ".join(f"<code>{t}</code>" for t in topics),
        unsafe_allow_html=True,
    )
    st.caption(
        "Responses are generated by IBM Granite (ibm/granite-4-h-small) via IBM watsonx.ai. "
        "EcoGuard AI is an educational tool — always follow official guidance for emergencies."
    )

    footer()
