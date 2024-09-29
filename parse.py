import cohere
from langchain_core.prompts import ChatPromptTemplate

# Initialize Cohere with your API key
cohere_api_key = 'jVMoyMLTFvKiM1IitCgtEgcwWUqZ67tSPb8Da3uG'
cohere_client = cohere.Client(cohere_api_key)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

def parse_with_cohere(dom_chunks, parse_description):
    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        # Create the prompt using the template
        prompt = template.format(dom_content=chunk, parse_description=parse_description)
        
        # Send request to Cohere
        response = cohere_client.generate(
            model='command-xlarge-nightly',  # You can change this based on available models
            prompt=prompt,
            max_tokens=300,  # Adjust tokens based on content length
            temperature=0.7,  # Adjust temperature based on creativity required
        )
        
        # Append response to the result list
        parsed_results.append(response.generations[0].text.strip())
        print(f"Parsed batch: {i} of {len(dom_chunks)}")

    return "\n".join(parsed_results)
