import streamlit as st
from langgraph_tool_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()

    st.session_state['thread_id'] = thread_id

    add_thread(thread_id)

    st.session_state['message_history']  = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):

    state = chatbot.get_state(
        config={
            'configurable': {
                'thread_id': thread_id
            }
        }
    )

    return state.values.get('messages', [])


def get_chat_title(thread_id):

    messages = load_conversation(thread_id)

    for msg in messages:

        if isinstance(msg, HumanMessage):

            title = " ".join(
                msg.content.split()[:10]
            )

            return title if title else "New Chat"

    return "New Chat"


# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:

    title = get_chat_title(thread_id)

    if st.sidebar.button(
            title,
            key=str(thread_id)):

        st.session_state['thread_id'] = thread_id

        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append(
                {
                    'role': role,
                    'content': msg.content
                }
            )

        st.session_state['message_history'] = temp_messages

        st.rerun()


# **************************************** Main UI ************************************

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):

        st.write(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    st.session_state['message_history'].append(
        {
            'role': 'user',
            'content': user_input
        }
    )

    with st.chat_message('user'):

        st.write(user_input)

    CONFIG = {

        "configurable": {
            "thread_id":
            st.session_state["thread_id"]
        },

        "metadata": {
            "thread_id":
            st.session_state["thread_id"]
        },

        "run_name": "chat_turn"

    }

    with st.chat_message('assistant'):

        ai_message = st.write_stream(

            message_chunk.content

            for message_chunk, metadata in chatbot.stream(

                {
                    'messages': [
                        HumanMessage(
                            content=user_input
                        )
                    ]
                },

                config=CONFIG,

                stream_mode='messages'
            )
            if message_chunk.content
        )

    st.session_state['message_history'].append(

        {
            'role': 'assistant',
            'content': ai_message
        }

    )