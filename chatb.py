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
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from parse import parse_with_cohere  # Import parsing function

# Page config
st.set_page_config(page_title="Interactive Chatbot with LinkedIn Profile Fetching and Web Scraping", layout="centered", initial_sidebar_state="auto")

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
        formatted_data = {k: v for k, v in formatted_data.items() if v or isinstance(v, bool)}
        return formatted_data
    
    except Exception as e:
        st.error(f"Error fetching profile: {str(e)}")
        return None

def format_experience(experience_list):
    return ', '.join([f"{exp['title']} at {exp['company']}" for exp in experience_list])

def format_skills(skills_data):
    if not skills_data:
        return "N/A"
    return ", ".join([skill['name'] for skill in skills_data])

def format_education(education_data):
    if not education_data:
        return "N/A"
    return "\n".join([f"- {edu['degree']} from {edu['school']}" for edu in education_data])

# Function to handle LinkedIn profile queries
def handle_linkedin_query(user_input, api_key, api_secret):
    match = re.search(r"fetch the profile of (.+)", user_input, re.IGNORECASE)
    if match:
        username = match.group(1).strip().replace(" ", "").lower()
        profile_data = fetch_and_format_profile(username, api_key, api_secret)
        if profile_data:
            response = f"The Linkedin Profile of {username} contain: \n\n"
            response += f"**Name**: {profile_data['name']} \n\n "
            response += f"**Headline**: {profile_data['headline']} \n\n "
            response += f"**Location**: {profile_data['location']}\n\n"
            response += f"**Industry**: {profile_data['industry']}\n\n"
            response += f"**Education**:\n{format_education(profile_data.get('education', []))}\n\n"
            response += f"**Skills**: {format_skills(profile_data.get('skills', []))}\n\n"
            response += f"**Experience**: {format_experience(profile_data.get('experience', []))}\n\n"
            response += f"**LinkedIn Profile**: [View Profile]({profile_data['profile_url']})"
            return response
        else:
            return "Unable to fetch the LinkedIn profile. Please check the username and try again."
    return None

# Function to handle web scraping queries
def handle_scraping_query(user_input):
    match = re.search(r"scrape the website (.+)", user_input, re.IGNORECASE)
    if match:
        url = match.group(1).strip()
        st.write("Scraping the website... Please wait.")

        try:
            st.write("Attempting to scrape:", url)  # Logging statement
            result = scrape_website(url)  # Ensure scrape_website is defined correctly
            st.write("Successfully scraped the website!")  # Logging statement

            body_content = extract_body_content(result)  # Make sure this function is defined
            cleaned_content = clean_body_content(body_content)  # Make sure this function is defined
            dom_chunks = split_dom_content(cleaned_content)  # Make sure this function is defined

            # Save the cleaned content in session state for parsing
            st.session_state.dom_content = cleaned_content

            with st.expander("View DOM Content"):
                st.text_area("DOM Content", cleaned_content, height=300)

            st.write("The website has been scraped successfully! What specific information would you like to extract from this website?")
            return dom_chunks  # Return chunks for further parsing

        except Exception as e:
            st.warning(f"An error occurred while scraping: {str(e)}")  # Better error handling
    return None

# Function to handle the parsing process
def handle_parsing(dom_chunks, parse_description):
    if parse_description:
        try:
            parsed_results = parse_with_cohere(dom_chunks, parse_description)
            return parsed_results
        except Exception as e:
            st.warning(f"An error occurred during parsing: {str(e)}")
    else:
        st.warning("Please describe what you want to parse.")
    return None

# Main function
def main():
    st.title("Trumio: Your Smart Chat Companion.🤖")

    # Instructions for using the chatbot
    st.info("**Trumio Welcomes You !!**")
    st.write("Steps to be followed:")
    st.write("1. **Type your message below to start chatting.**")
    st.write("2. To fetch a LinkedIn profile, type '**Fetch the profile of [username]**' (e.g., 'Fetch the profile of kanishk-gupta-21372122b').")
    st.write("3. To scrape a website, type '**Scrape the website [URL]**' (e.g., 'Scrape the website https://amazon.in').")
    st.write("---")

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
        # Add user message to chat history
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
            dom_chunks = handle_scraping_query(prompt)
            if dom_chunks:
                st.write("What specific information would you like to extract from this website?")
                parse_description = st.text_input("Describe what you want to parse.")
                if st.button("Parse Content"):
                    parsed_results = handle_parsing(dom_chunks, parse_description)
                    if parsed_results:
                        with st.chat_message("assistant"):
                            typewriter_effect(parsed_results)
                        st.session_state.messages.append({"role": "assistant", "content": parsed_results})
                else:
                    st.warning("Please describe what you want to parse.")
            else:
                # Use ChatCohere to get an AI-generated response
                with st.chat_message("assistant"):
                    response = conversation.predict(input=prompt)
                    typewriter_effect(response, delay=0.005)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
