import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


# **************************************** utility functions ************************* Add a dynamic threadid and it to sesssion*****
## using UUID

def generate_thread_id():
    thread_id = uuid.uuid4() # generatees random threadid
    return thread_id


#*******************************************************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

#****************************Side bar UI************************

st.sidebar.title("Langgraph Chatbot")

st.sidebar.button("New Chat")
st.sidebar.header("My Conversations")

st.sidebar.text(st.session_state['thread_id'])

##******************MAIN UI*********************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
