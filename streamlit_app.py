import streamlit as st
import pandas as pd
import requests
from io import StringIO
from openai import OpenAI

# Show title and description
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Asks for user OpenAI API key via `st.text_input`
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Define function to handle answering questions based on DataFrame
        def answer_question(prompt, df):
            if df is not None:
                st.write("Debug: DataFrame Loaded Successfully")
                st.write(df.head())  # Display first few rows of DataFrame for verification
                search_results = df[df.apply(lambda row: row.astype(str).str.contains(prompt, case=False).any(), axis=1)]
                st.write(f"Debug: Search results for '{prompt}'")
                st.write(search_results)  # Display search results for debugging
                if not search_results.empty:
                    return search_results
                else:
                    return "No matching results found."
            else:
                return "Data not loaded."

        # Generate a response using the DataFrame content
        df, encoding = st.session_state.get('df', (None, None))
        if df is not None:
            response_content = answer_question(prompt, df)
        else:
            response_content = "CSV file not loaded properly."

        # Store and display the response
        with st.chat_message("assistant"):
            if isinstance(response_content, pd.DataFrame):
                st.write(response_content)
                response_string = response_content.to_string(index=False)
            else:
                response_string = response_content
                st.markdown(response_string)
        st.session_state.messages.append({"role": "assistant", "content": response_string})

# File location in the GitHub repository
GITHUB_URL = "https://raw.githubusercontent.com/jamesnicholls4m/NATA_chatbot_v4/main/NATA%20A2Z%20List%20-%20August%202024%20-%20v1.csv"

# List of encodings to try
encodings = ["utf-8", "ISO-8859-1", "utf-16"]

def load_csv_from_github(url, encodings):
    for encoding in encodings:
        try:
            st.write(f"Trying to fetch the file from URL: {url} with encoding: {encoding}")
            response = requests.get(url)
            if response.status_code == 200:
                csv_content = response.content.decode(encoding)
                return pd.read_csv(StringIO(csv_content)), encoding
            else:
                st.error(f"Failed to retrieve the file: {response.status_code} {response.reason}")
                return None, None
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
        except requests.RequestException as e:
            st.error(f"Failed to retrieve the file: {e}")
            return None, None
    return None, None

st.write("## Attempting to load the CSV file from the GitHub repository")
df, encoding = load_csv_from_github(GITHUB_URL, encodings)
if df is not None:
    st.session_state['df'] = (df, encoding)
    st.write(f"### Data Preview (Encoding: {encoding})")
    st.write(df.head())  # Show the first few rows to verify the DataFrame content
else:
    st.error("Could not decode the file with any of the tried encodings. Please ensure it is encoded in UTF-8 or verify the file exists in the repository.")
