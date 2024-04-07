import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="👋",
)

st.title("REGEXER")
st.markdown(
    """
    # A RegEx pattern generator using LLM.
    """
)

# Update
ai = st.selectbox('Choose AI: ', ('OpenAI', 'Anthropic'), )
api_key = st.text_input('API Key: ', type='password')

st.session_state['ai'] = ai
st.session_state['api_key'] = api_key