from io import StringIO

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

def intent():
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

def regex():
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

def retry(df):
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