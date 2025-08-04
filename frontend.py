import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

#st component session state - st.session state-> dict --> erase only when page is manuualy refresed

config = {'configurable':{'thread_id':'123'}}
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


#loading the message history
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['content'])


# {'role':'user','content':"hi"}
# {'role':'assistant','content':"heloo"}

user_input = st.chat_input("Type here")

if user_input:
    # first add the messagte to message history
    st.session_state['message_history'].append({'role':'user', "content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    
    ai_message = response['messages'][-1].content

    st.session_state['message_history'].append({'role':'assistant', "content":ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)

