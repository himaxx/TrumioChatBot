import os
import streamlit as st
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from linkedin_api import Linkedin
import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Page config
st.set_page_config(page_title="Interactive Chatbot with Web Scraping & LinkedIn Fetching", layout="centered", initial_sidebar_state="auto")

# Load environment variables
load_dotenv()

# Initialize the ChatCohere model
@st.cache_resource
def initialize_cohere():
    return ChatCohere()

chat = initialize_cohere()

# Initialize conversation memory
memory = ConversationBufferMemory()

# Create a conversation chain
conversation = ConversationChain(
    llm=chat,
    memory=memory,
    verbose=False
)

def typewriter_effect(text, delay=0.01):
    """Simulates typing animation by printing each character with a small delay."""
    response = ""
    message_container = st.empty()  # Placeholder for the message
    for char in text:
        response += char
        message_container.markdown(response)  # Update message as new character is added
        time.sleep(delay)
    return response

# LinkedIn profile fetching function
def fetch_and_format_profile(username, api_key, api_secret):
    api = Linkedin(api_key, api_secret)
    try:
        data = api.get_profile(username)
        formatted_data = {
            'name': f"{data['firstName']} {data['lastName']}",
            'headline': data.get('headline', ''),
            'summary': data.get('summary', ''),
            'location': data.get('geoLocationName', ''),
            'industry': data.get('industryName', ''),
            'public_id': data.get('public_id', ''),
            'education': [{'school': edu['schoolName'], 'degree': edu.get('degreeName', '')} for edu in data.get('education', [])],
            'experience': [{'title': exp['title'], 'company': exp['companyName']} for exp in data.get('experience', [])],
            'skills': data.get('skills', []),
            'languages': data.get('languages', []),
            'certifications': data.get('certifications', []),
            'volunteer_experience': data.get('volunteer', []),
            'honors_awards': data.get('honors', []),
            'projects': data.get('projects', []),
            'profile_url': f"https://www.linkedin.com/in/{data['public_id']}",
        }
        return formatted_data
    except Exception as e:
        st.error(f"Error fetching profile: {str(e)}")
        return None

# Web Scraping functions
def scrape_website(website):
    """Scrapes the given website URL using Selenium."""
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(website)
        time.sleep(5)
        html = driver.page_source
        return html
    finally:
        driver.quit()

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return " "

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)]

# Function to handle web scraping queries
def handle_web_scraping(user_input):
    match = re.search(r"scrape the website (.+)", user_input, re.IGNORECASE)
    if match:
        website = match.group(1).strip()
        try:
            html = scrape_website(website)
            body_content = extract_body_content(html)
            cleaned_content = clean_body_content(body_content)
            response = f"Website scraped successfully! Here's the cleaned content:\n\n{cleaned_content[:500]}..."  # Limit content for display
            return response
        except Exception as e:
            return f"Error scraping website: {str(e)}"
    return None

# Main function
def main():
    st.title("Interactive Chatbot with Web Scraping & LinkedIn Profile Fetching")
    
    # LinkedIn API credentials
    api_key = os.getenv('LINKEDIN_API_KEY')
    api_secret = os.getenv('LINKEDIN_API_SECRET')

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Handle LinkedIn profile fetching query
        linkedin_response = handle_linkedin_query(prompt, api_key, api_secret)
        if linkedin_response:
            with st.chat_message("assistant"):
                typewriter_effect(linkedin_response)
            st.session_state.messages.append({"role": "assistant", "content": linkedin_response})
        else:
            # Handle web scraping query
            web_scraping_response = handle_web_scraping(prompt)
            if web_scraping_response:
                with st.chat_message("assistant"):
                    typewriter_effect(web_scraping_response)
                st.session_state.messages.append({"role": "assistant", "content": web_scraping_response})
            else:
                # Use ChatCohere to get an AI-generated response
                with st.chat_message("assistant"):
                    response = conversation.predict(input=prompt)
                    typewriter_effect(response, delay=0.005)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
