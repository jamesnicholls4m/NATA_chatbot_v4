import streamlit as st
import pandas as pd
import openai

# Set up the OpenAI API key
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# File upload
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    
    # Display available sheets
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("Select the sheet to analyze:", sheet_names)
    
    # Load the selected sheet
    data = pd.read_excel(xls, sheet_name=sheet_name)
    st.write("Data Preview:")
    st.write(data.head())
    
    # Enter your question
    question = st.text_input("Ask a question about the data:")
    
    if st.button("Search"):
        if not openai_api_key:
            st.error("Please enter your OpenAI API key.")
        else:
            # Ask GPT for interpretation
            openai.api_key = openai_api_key
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=question,
                max_tokens=150
            )
            gpt_answer = response.choices[0].text.strip()
            st.write("GPT's Interpretation:", gpt_answer)
            
            # Search the Excel file based on the GPT's interpretation
            if 'ISO 15189' in gpt_answer:
                relevant_data = data[(data['Standard'] == 'ISO 15189') & (~data['QLD\n07 3721 7300 WA\n08 9486 2800'].isnull())]
                qld_contacts = relevant_data['QLD\n07 3721 7300 WA\n08 9486 2800'].unique()
                st.write("Contacts:", qld_contacts)
                st.write("Phone Number: +61 7 3721 7300")
            else:
                st.write("No relevant data found for your question.")
