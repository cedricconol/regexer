import streamlit as st
from functions import create_chain, prompt_create_regex, tester, prompt_retry, prompt_intent
from langchain_core.messages import HumanMessage, AIMessage

st.title("REGEXER")

default_input = "CSV here"
input_csv = st.text_area("Input CSV", default_input)
max_retries = st.number_input("Maximum retries", 3)
validation_output = 'N'

# Input validation

if input_csv != default_input:
    prompt_validation = prompt_intent()
    chain_validation = create_chain(prompt_validation)
    chat_history_validation = [HumanMessage(content=input_csv)]

    validation_output = chain_validation.invoke(
        {"input": input_csv,
        "chat_history": []
        }).content

    if validation_output!='Y':
        st.write(validation_output)

# Regexer
prompt = prompt_create_regex()
chain = create_chain(prompt)

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
        score = tester(input_csv, patterns[-1])

        if score < 1:
            df = tester(input_csv, patterns[-1], 'dataframe', True)

            prompt_retried = prompt_retry(df)

            chat_history.append(HumanMessage(content=prompt_retried))

            pattern_new = chain.invoke({
            "input":prompt_retry,
            "chat_history":chat_history
            }).content

            chat_history.append(AIMessage(content=pattern_new))

            patterns.append(pattern_new)

        else:
            break
    
    st.write("Regex pattern: ")
    st.code(patterns[-1])
    st.write("Performance (%)", score*100)