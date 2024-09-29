import streamlit as st
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_cohere  # Updated to use Cohere

st.title("Web Scraping using AI")
url = st.text_input("Enter a Website URL:")

if st.button("Scrape Site"):
    if url:
        st.write("Scraping the website...")
        try:
            result = scrape_website(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)

            st.session_state.dom_content = cleaned_content

            with st.expander("View DOM Content"):
                st.text_area("Dom Content", cleaned_content, height=300)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a URL before scraping.")

if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse?")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")

            dom_chunks = split_dom_content(st.session_state.dom_content)
            parsed_results = parse_with_cohere(dom_chunks, parse_description)
            st.text_area("Parsed Content", parsed_results, height=300)
