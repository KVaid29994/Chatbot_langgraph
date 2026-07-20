from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import random
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
import sqlite3
import aiosqlite
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

llm = ChatOpenAI()


client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": r"C:\Python314\python.exe",          
            "args": ["C://Users//kanha//Desktop//lang_revison//chatbot_langgraph//main.py"],
        },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)
## search tool

search_tool = DuckDuckGoSearchRun(region= 'us-en')



@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph ():

    tools = await client.get_tools()

    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState):
        messages = state['messages']
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)


    conn = await aiosqlite.connect('chatbot.db')
    # Checkpointer
    checkpointer = AsyncSqliteSaver(conn)



    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile(checkpointer=checkpointer)

    return chatbot

async def main():
    chatbot = await build_graph()
    CONFIG = {'configurable': {'thread_id': 'thread-1'}}

    response = await chatbot.ainvoke({'messages': [HumanMessage(content="what is product 0f 66666& 33")]}, config=CONFIG)
    print (response['messages'][-1].content)
        # # print (chatbot.get_state(config= CONFIG).values['messages'])

if __name__ == '__main__':
    asyncio.run(main())