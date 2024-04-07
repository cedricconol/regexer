from regexer.security import hasher

import streamlit as st

from langchain_openai import ChatOpenAI

def create(prompt, api_key, version="gpt-4-0125-preview", temperature=0.0):
    if hasher(api_key) == st.secrets["OPENAI_API_HASH"]:
        api_key = st.secrets["OPENAI_API_KEY"]

    model = ChatOpenAI(
        model=version,
        temperature=temperature,
        api_key=api_key
    )

    chain = prompt | model

    return chain