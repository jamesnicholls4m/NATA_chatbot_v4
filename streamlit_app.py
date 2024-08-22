import pandas as pd
import openai
from tkinter import Tk, filedialog

def load_excel_file():
    """Prompt user to upload an Excel file and load it."""
    root = Tk()
    root.withdraw()  # Close the root window
    file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        raise ValueError("No file selected.")
    
    xls = pd.ExcelFile(file_path)
    return xls

def ask_question_to_gpt(api_key, question):
    """Ask a question to OpenAI GPT model and get the response."""
    openai.api_key = api_key
    
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=question,
      max_tokens=150
    )
    
    return response.choices[0].text.strip()

def search_excel_for_answer(xls, sheet_name, question):
    """Search the Excel file based on the GPT-3's interpretation of the question."""
    data = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Simplified example: filter based on a keyword extracted from the question
    if 'ISO 15189' in question:
        relevant_data = data[(data['Standard'] == 'ISO 15189') & (~data['QLD\n07 3721 7300 WA\n08 9486 2800'].isnull())]
        qld_contacts = relevant_data['QLD\n07 3721 7300 WA\n08 9486 2800'].unique()
        return {
            "contacts": qld_contacts.tolist(),
            "phone_number": "+61 7 3721 7300"
        }
    else:
        return "No relevant data found for your question."

def main():
    print("Welcome to the Excel Search Application!")
    
    # Step 1: User inputs their OpenAI API key
    api_key = input("Please enter your OpenAI API key: ").strip()
    
    # Step 2: User uploads an Excel file
    try:
        xls = load_excel_file()
    except ValueError as e:
        print(e)
        return
    
    # Step 3: User enters their question
    question = input("Please enter your question: ").strip()
    
    # Step 4: Application asks the question to GPT
    gpt_answer = ask_question_to_gpt(api_key, question)
    print(f"GPT's Interpretation: {gpt_answer}")
    
    # Step 5: Search the Excel file based on the GPT interpretation
    try:
        result = search_excel_for_answer(xls, sheet_name='Staff List for ICT', question=gpt_answer)
        print("Search Results:", result)
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    main()
