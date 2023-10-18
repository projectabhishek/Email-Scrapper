import streamlit as st

from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


from bs4 import BeautifulSoup
import requests
import re


from googleapiclient.discovery import build
from google.oauth2 import service_account

# Define functions for web scraping and data updates

# Define the Streamlit app
def main():
    st.title("Email Scrapping Application and Saving in Google SpreadSheet")
    st.sidebar.title("Enter The Details Below")

    # Create input fields or widgets for user input (e.g., college_name and college_branch)
    name = st.sidebar.text_input("Enter the college name:")
    branch = st.sidebar.text_input("Enter the branch:")

    # Create a button to trigger the data extraction and update
    if st.sidebar.button("Run"):
        # 1. Selenium WebPage Link Extraction

        # Get the college name from the user
        college_name = name
        college_branch= branch
        options = Options()
        # Create a Selenium WebDriver instance (change the path to the driver as needed)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

        # Navigate to Google search
        driver.get("https://www.google.com")

        # Find the search input element and enter the query
        search_input = driver.find_element(By.NAME, "q")
        search_input.send_keys(f"faculty information of {college_branch} department of {college_name} University")

        # Submit the search query
        search_input.submit()

        # Wait for the search results page to load (you might need to adjust the waiting time)
        driver.implicitly_wait(10)

        # Find the first search result link
        search_results = driver.find_elements(By.TAG_NAME, "a")

        # Get the current page URL using JavaScript
        current_url = driver.execute_script("return window.location.href")

        print(current_url)
        driver.close()


        # 2. First Link Extraction

        url=str(current_url)

        #url='https://www.google.com/search?q=faculty+information+of+computer+science+department+of+DDU+University&sca_esv=568129103&source=hp&ei=NEIRZYSQHIeG4dUP68aQ6Ag&iflsig=AO6bgOgAAAAAZRFQRAKAwQmiH3ASkjB4H0KDaAa6K2rq'

        first_page_text = requests.get(url).text
        soup = BeautifulSoup(first_page_text,'lxml')
        firstlink=soup.find('div',class_='egMi0 kCrYT')
        htmllink=str(firstlink)


        html = htmllink

        # Define a regular expression pattern to match the URL
        pattern = r'href="([^"]+)"'

        # Use re.findall to find all matches of the pattern in the HTML
        matches = re.findall(pattern, html)

        # Extract the URL from the matches
        if matches:
            extracted_url = matches[0]
            print(extracted_url[7:])
            x=extracted_url[7:]
        else:
            print("URL not found in the HTML")



        def extract_extension_string(input_string):
            # Define a regular expression pattern to match the specified extensions
            pattern = r'.*(\.php|\.html|\.in|\.com|\.org)'

            # Use re.search to find the match
            match = re.search(pattern, input_string)

            if match:
                # Extract the matched part of the string
                extracted_string = match.group(0)
                return extracted_string
            else:
                # If no match is found, return None or raise an error as needed
                return None

        # Test the function


            
        def extract_before_amp(input_string):
            # Split the input string at the '&amp;' sequence
            parts = input_string.split('&amp;')

            # Return the part before the '&amp;' sequence
            if len(parts) > 0:
                return parts[0]
            else:
                # If the '&amp;' sequence is not found, return the original string
                return input_string

        # Test the function

        if '&' in x:
            result = extract_before_amp(x)
            print("Extracted string:", result)
        else:
            result = extract_extension_string(x)
            if result:
                print("Extracted string:", result)
            else:
                print("No matching extension found.")



        # 3. Email Extraction

        final_url=result
        #final_url=str('https://cs.du.ac.in/faculty/')



        html_text=requests.get(final_url).text
        soup = BeautifulSoup(html_text,'lxml')
        text=str(soup.prettify())
        #print(text)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        # Use re.findall to find all email addresses in the HTML content
        email_addresses = re.findall(email_pattern, text)
        data=[]
        # Print the extracted email addresses
        for email in email_addresses:
            data.append([college_name,college_branch,email])



        # 4. Google SpreadSheet Function

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        creds=None
        creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # The ID and range of a sample spreadsheet.
        SAMPLE_SPREADSHEET_ID = '1xbL-5c1T8KN0tPInkWRISILwuUK0xgTaMxJKGmVTb0M'
        service = build('sheets', 'v4', credentials=creds)
        sheet_name='Master'

        def update_data(data):
            
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=sheet_name).execute()
            values = result.get('values', [])
            
            # Determine the number of columns (assuming the first row contains column headers)
            num_columns = len(values[0]) if values else 0
            
            # Define the data you want to append
            new_data = data  # Replace with your data
            
            # Append the data to the next available row
            range_to_update = f'{sheet_name}!A{len(values) + 1}:{chr(ord("A") + num_columns)}{len(values) + 1}'
            request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_to_update, valueInputOption='RAW', body={'values': new_data})
            response = request.execute()



        # 5. Dump Function

        for row in data:
            update_data([row])
        print('Update Successful')
        st.write("Data updated successfully!")

if __name__ == '__main__':
    main()
