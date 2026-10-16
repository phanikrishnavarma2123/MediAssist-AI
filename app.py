import base64
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL = "gemma3"
REQUEST_TIMEOUT_SECONDS = 180
BACKGROUND_IMAGE = base64.b64encode(
    (Path(__file__).parent / "assets" / "mediassist_hologram.svg").read_bytes()
).decode("ascii")

SYSTEM_PROMPT = """You are MediAssist AI, an assistant for general health education.
Explain health topics, medical terms, preventive care, healthy-lifestyle ideas,
and the general purpose of medical services in clear, simple language.

Safety rules:
- Give general information only. Do not diagnose, claim certainty about a
  person's condition, prescribe medication, suggest doses, or tell someone to
  start, stop, or change treatment.
- Encourage a qualified healthcare professional for personal health concerns.
- Treat possible emergencies as urgent. Tell the person to contact local
  emergency services promptly and not to wait for an AI response. Consider the
  meaning and context of the whole message; do not use a list of trigger words
  as the only way to recognize an emergency.
- Be clear when you are uncertain. Do not ask for identifying patient details.
"""

WELCOME_MESSAGE = (
    "Hello! I can explain general health topics, medical terms, and healthy-"
    "lifestyle information. What would you like to learn about?"
)

SUGGESTED_QUESTIONS = (
    "What does blood pressure mean?",
    "How does sleep support general health?",
    "What is the difference between a virus and bacteria?",
    "What are some heart-healthy habits?",
)


def request_ollama(prompt, history):
    """Ask the local Ollama server and return its text response."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(
        {"role": item["role"], "content": item["content"]}
        for item in history
        if item["role"] in {"user", "assistant"}
        and not item.get("is_error", False)
    )
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(
        request, timeout=REQUEST_TIMEOUT_SECONDS
    ) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["message"]["content"]


def ollama_status():
    """Return a short local Ollama status and whether Gemma is installed."""
    request = urllib.request.Request(OLLAMA_TAGS_URL, method="GET")
    with urllib.request.urlopen(request, timeout=3) as response:
        result = json.loads(response.read().decode("utf-8"))

    models = result.get("models", [])
    installed = any(
        model.get("name", "").split(":", maxsplit=1)[0] == MODEL
        or model.get("model", "").split(":", maxsplit=1)[0] == MODEL
        for model in models
    )
    return installed


def friendly_ollama_error(error):
    """Convert common local Ollama failures into useful instructions."""
    if isinstance(error, urllib.error.HTTPError):
        try:
            details = json.loads(error.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            details = {}
        message = str(details.get("error", "")).lower()
        if "model" in message and ("not found" in message or "pull" in message):
            return "The Gemma model is not installed. Open a terminal and run `ollama pull gemma3`, then try again."
        return f"Ollama returned an HTTP error ({error.code}). Check that Ollama is running and try again."

    if isinstance(error, (socket.timeout, TimeoutError)):
        return "Ollama took too long to respond. The first reply can take longer while the model loads; please try again."

    if isinstance(error, urllib.error.URLError):
        if isinstance(error.reason, (socket.timeout, TimeoutError)):
            return "Ollama took too long to respond. The first reply can take longer while the model loads; please try again."
        return "I couldn't connect to Ollama at localhost:11434. Start the Ollama app, then try again."

    if isinstance(error, (KeyError, json.JSONDecodeError, UnicodeDecodeError)):
        return "Ollama responded, but its reply was not in the expected format. Check Ollama and try again."

    return "Something went wrong while contacting Ollama. Check that the local server is running, then try again."


def reset_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]


st.set_page_config(
    page_title="MediAssist AI | Health Information",
    page_icon="🩺",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("data:image/svg+xml;base64,__BACKGROUND_IMAGE__");
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 850px; padding-top: 2rem; padding-bottom: 7rem; }
    .medi-kicker {
        font-size: 0.78rem; font-weight: 700;
        letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.25rem;
    }
    .medi-title { font-size: 2.25rem; font-weight: 750; margin: 0; }
    .medi-subtitle { opacity: 0.8; margin: 0.35rem 0 1.25rem; }
    [data-testid="stChatMessage"] {
        border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
        border-radius: 14px; padding: 0.85rem 1rem;
        background-color: color-mix(in srgb, currentColor 3%, transparent);
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: color-mix(in srgb, currentColor 8%, transparent);
    }
    div[data-testid="stChatInput"] {
        border-color: color-mix(in srgb, currentColor 24%, transparent);
    }
    .stButton > button {
        border-radius: 9px; min-height: 2.7rem;
    }
    .stButton > button:hover {
        border-color: currentColor;
    }
    @media (max-width: 640px) {
        .block-container { padding: 1rem 1rem 6rem; }
        .medi-title { font-size: 1.8rem; }
    }
    </style>
    """.replace("__BACKGROUND_IMAGE__", BACKGROUND_IMAGE),
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

with st.sidebar:
    st.subheader("Connection")
    try:
        model_installed = ollama_status()
        if model_installed:
            st.success("Ollama is running and Gemma is installed.")
        else:
            st.warning("Ollama is running, but Gemma was not found. Run `ollama pull gemma3`.")
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError):
        st.warning("Ollama is not responding. Start the Ollama app to chat.")
    st.caption("Requests go only to Ollama on this computer. Chat history stays in the current Streamlit session's memory and is not saved permanently by this app.")
    if st.button("Clear chat", icon="🗑️", use_container_width=True):
        reset_chat()
        st.rerun()

st.markdown('<div class="medi-kicker">Local health information assistant</div>', unsafe_allow_html=True)
st.markdown('<h1 class="medi-title">MediAssist AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="medi-subtitle">Clear, general health education powered by Gemma on your computer.</p>',
    unsafe_allow_html=True,
)
st.warning(
    "General information only. MediAssist AI cannot diagnose or prescribe and does not replace a healthcare professional. "
    "For personal health concerns, speak with a qualified professional. If you may be experiencing an emergency, contact local emergency services now; do not wait for an AI reply. "
    "Please do not enter names, addresses, or other identifying patient details."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("**Try asking**")
suggestion_columns = st.columns(2)
selected_question = None
for index, question in enumerate(SUGGESTED_QUESTIONS):
    if suggestion_columns[index % 2].button(
        question, key=f"suggestion_{index}", use_container_width=True
    ):
        selected_question = question

prompt = st.chat_input("Ask a general health question...")
prompt = selected_question or prompt

if prompt:
    prior_history = st.session_state.messages[1:]
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("MediAssist is preparing a response..."):
            try:
                answer = request_ollama(prompt, prior_history)
                is_error = False
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                socket.timeout,
                TimeoutError,
                KeyError,
                json.JSONDecodeError,
                UnicodeDecodeError,
            ) as error:
                answer = friendly_ollama_error(error)
                is_error = True
            except Exception:
                answer = "An unexpected error occurred while contacting the local AI. Please try again."
                is_error = True

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "is_error": is_error}
    )