import streamlit as st
from regexer import helper
from regexer.openai import chains, prompts
from langchain_core.messages import HumanMessage, AIMessage

st.title("REGEXER")

default_input = "CSV here"
input_csv = st.text_area("Input CSV", default_input)
max_retries = st.number_input("Maximum retries", 3)
validation_output = 'N'

# config
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = 'none'

api_key = st.session_state.api_key

if api_key == 'none':
    st.write("Input API Key in Home Page.")

# Input validation
if input_csv != default_input and st.session_state.api_key != 'none':
    prompt_validation = prompts.intent()
    chain_validation = chains.create(prompt_validation, api_key)
    chat_history_validation = [HumanMessage(content=input_csv)]

    validation_output = chain_validation.invoke(
        {"input": input_csv,
        "chat_history": []
        }).content

    if validation_output!='Y':
        st.write(validation_output)

# Regexer
prompt = prompts.regex()
chain = chains.create(prompt, api_key)

if validation_output=='Y':
    pattern = chain.invoke(
        {"input":input_csv,
         "chat_history": []}
        ).content

    chat_history = [
        HumanMessage(content=input_csv),
        AIMessage(content=pattern)
    ]

    patterns = [pattern]

    i=0
    while i < max_retries:
        i+=1
        score = helper.tester(input_csv, patterns[-1])

        if score < 1:
            df = helper.tester(input_csv, patterns[-1], 'dataframe', True)

            prompt_retried = prompts.retry(df)

            chat_history.append(HumanMessage(content=prompt_retried))

            pattern_new = chain.invoke({
            "input":prompt_retried,
            "chat_history":chat_history
            }).content

            chat_history.append(AIMessage(content=pattern_new))

            patterns.append(pattern_new)

        else:
            break
    
    st.write("Regex pattern: ")
    st.code(patterns[-1])
    st.write("Performance (%)", score*100)