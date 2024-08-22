import streamlit as st
import pandas as pd
import requests
from io import StringIO
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

# File location in the GitHub repository
GITHUB_URL = "https://raw.githubusercontent.com/jamesnicholls4m/NATA_chatbot_v4/main/NATA%20A2Z%20List%20-%20August%202024%20-%20v1.csv"

# List of encodings to try
encodings = ["utf-8", "ISO-8859-1", "utf-16"]

def load_csv_from_github(url, encodings):
    for encoding in encodings:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check that the request was successful
            csv_content = response.content.decode(encoding)
            return pd.read_csv(StringIO(csv_content)), encoding
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
        except requests.RequestException as e:
            st.error(f"Failed to retrieve the file: {e}")
            return None, None
    return None, None

st.write("## Attempting to load the CSV file from the GitHub repository")
df, encoding = load_csv_from_github(GITHUB_URL, encodings)
if df is not None:
    st.write(f"### Data Preview (Encoding: {encoding})")
    st.write(df)
else:
    st.error("Could not decode the file with any of the tried encodings. Please ensure it is encoded in UTF-8 or verify the file exists in the repository.")
