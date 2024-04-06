import re
import csv
from io import StringIO

import streamlit as st
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder

def create_chain(prompt, version="gpt-4-0125-preview", temperature=0.0):
    model = ChatOpenAI(
        model=version,
        temperature=temperature,
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    chain = prompt | model

    return chain

def prompt_intent():
    delimiter = "###"
    system_prompt = f"""
        You are an AI assistant. Your task is to classify the string provided in <input> as valid or invalid.
        {delimiter}
        The criteria for a valid <input> is:
        1. Must be a comma-separated string (CSV string)
        2. Must have 2 columns only
        3. The first column must have a header name of `base_string`
        4. The second column must have a header name of `search_string`
        5. Each row must contain a value for each column
        {delimiter}
        If all the criteria above are met, return Y.
        {delimiter}
        Otherwise, provide a helpful step by step instruction so that all criteria are met.
    """

    prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    return prompt

def prompt_create_regex():
    delimiter = "####"
    system_prompt = f"""
        You are an AI Assistant expert in formulating regex patterns using Python Regex.
        {delimiter}
        You will be provided a CSV with 2 columns namely: base_string, search_string.
        {delimiter}
        Your task is to write a regex pattern using Python Regex that will extract search_string from base_string.
        {delimiter}
        Provide the Python regex pattern alone as a string and nothing else. 
        Do not include the following in the output:
        1. markdown formatting
        2. raw string prefix
        3. string quotation
    """

    prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    return prompt

def extract_search_string(base_string, pattern):
    
    search_string = re.search(pattern, base_string)
    
    if search_string:
        return search_string.group(0)
    return None

def tester(csv_string, pattern, output='score', verbose=False):
    csv_sio = StringIO(csv_string)
    df = pd.read_csv(csv_sio, sep=",", header=0)

    score = 0
    total = 0
    result = []

    for _, row in df.iterrows():
        base_string = row['base_string']
        search_string = row['search_string']
        output_string = extract_search_string(base_string, pattern)
        result.append(output_string)

        total+=1

        if output_string == search_string:
            score+=1

        if verbose:
            print('Example number: ', total)
            print('base_string: ', base_string)
            print('output: ', output_string)
            print('expected: ', search_string)

            if output_string == search_string:
                print('result: ', 'correct')
                print('---')
            else:
                print('result: ', 'incorrect')
                print('---')
    
    if output=='score':
        return score/total
    
    if output=='dataframe':
        df['result'] = result
        df['is_correct'] = df.apply(lambda row: row.search_string==row.result, axis=1)
        return df

def prompt_retry(df):
    df = df[(df['is_correct']==False)]
    df=df[['base_string', 'search_string', 'result']]
    s = StringIO()
    df.to_csv(s, index=False)
    failed = s.getvalue()

    delimiter = "####"
    prompt = f"""The pattern fails on some rows of the initially provided CSV. Regenerate the Python regex pattern such that it will also work for these failed examples.
    {delimiter}
    Failed rows are provided in a CSV format below with the following columns:
    1. base_string: string where `search_string` will be extracted
    2. search_string: expected output of the last regex pattern
    3. result: column is the output of the last regex pattern you have provided
    {delimiter}
    Provide the Python regex pattern alone as a string and nothing else. 
    Do not include the following in the output:
    1. markdown formatting
    2. raw string prefix
    3. string quotation
    {delimiter}
    Here are the list of failed rows in CSV:
    {failed}
"""
    return prompt

sample_csv="""base_string,search_string
"https://docs.google.com/spreadsheets/d/aabc-d12/edit#gid=0","aabc-d12"
"https://docs.google.com/spreadsheets/d/33_eed/33_eed","33_eed"
"""