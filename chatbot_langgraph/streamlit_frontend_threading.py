import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# ---------------- Utility Functions ---------------- #

def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)

    st.session_state["message_history"] = []


def load_conversation(thread_id):
    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return state.values.get("messages", [])


# ---------------- Session State ---------------- #

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

add_thread(st.session_state["thread_id"])


# ---------------- Sidebar ---------------- #

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state["chat_threads"]:

    title = st.session_state["chat_titles"].get(
        thread_id,
        "New Chat"
    )

    if st.sidebar.button(title, key=thread_id):

        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"

            temp_messages.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )

        st.session_state["message_history"] = temp_messages

        st.rerun()

current_chat = st.session_state["chat_titles"].get(
    st.session_state["thread_id"],
    "New Chat"
)

st.sidebar.divider()
st.sidebar.caption(f"Current Chat: {current_chat}")


# ---------------- Chat History ---------------- #

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# ---------------- User Input ---------------- #

user_input = st.chat_input("Type here")

if user_input:

    current_thread = st.session_state["thread_id"]

    # Save title from first message only
    if current_thread not in st.session_state["chat_titles"]:

        st.session_state["chat_titles"][current_thread] = (
            " ".join(user_input.split()[:5])
        )

    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {
        "configurable": {
            "thread_id": current_thread
        }
    }

    with st.chat_message("assistant"):

        ai_message = st.write_stream(

            chunk.content

            for chunk, metadata in chatbot.stream(

                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },

                config=CONFIG,

                stream_mode="messages"
            )

        )

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )