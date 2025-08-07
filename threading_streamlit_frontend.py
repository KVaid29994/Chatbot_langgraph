import streamlit as st
from backend import chatbot  # Assuming your LangGraph chatbot setup
from langchain_core.messages import HumanMessage
import uuid

# **************************************** Utility Functions ****************************************

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []
    st.session_state['thread_previews'][thread_id] = "New Chat"

def load_conversation(thread_id):
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])

# **************************************** Session Initialization ****************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_previews' not in st.session_state:
    st.session_state['thread_previews'] = {}

add_thread(st.session_state['thread_id'])
if st.session_state['thread_id'] not in st.session_state['thread_previews']:
    st.session_state['thread_previews'][st.session_state['thread_id']] = "New Chat"

# **************************************** Sidebar UI ****************************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.header("💬 My Conversations")

threads_to_delete = []

for thread_id in st.session_state['chat_threads'][::-1]:
    preview = st.session_state['thread_previews'].get(thread_id, f"Thread {str(thread_id)[:8]}")
    cols = st.sidebar.columns([6, 1])

    if cols[0].button(preview, key=f"load_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({'role': role, "content": msg.content})
        st.session_state['message_history'] = temp_messages

    if cols[1].button("🗑️", key=f"delete_{thread_id}"):
        threads_to_delete.append(thread_id)

for thread_id in threads_to_delete:
    st.session_state['chat_threads'].remove(thread_id)
    st.session_state['thread_previews'].pop(thread_id, None)
    if thread_id == st.session_state['thread_id']:
        reset_chat()

# **************************************** Main Chat UI ****************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Set preview for thread if first message
    if st.session_state['thread_id'] not in st.session_state['thread_previews'] or \
       st.session_state['thread_previews'][st.session_state['thread_id']] == "New Chat":
        st.session_state['thread_previews'][st.session_state['thread_id']] = user_input[:30] + ("..." if len(user_input) > 30 else "")

    # Stream assistant response
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, _ in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # Add assistant reply to history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
