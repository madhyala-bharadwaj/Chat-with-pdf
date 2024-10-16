import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

data_directory = 'data'
os.makedirs(data_directory, exist_ok=True)

# Logging configuration
log_file_path = os.path.join(data_directory, 'logs', 'app.log')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# environment variables from .env file
load_dotenv()

# Initialize OpenAI client with the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(text, pdf_text):
    try:
        logger.info("User Input: %s", text)

        # Combining the user's input and PDF content for context
        messages = [
            {"role": "system", "content": "You are a helpful assistant for answering questions about the PDF."},
            {"role": "user", "content": pdf_text},  # Providing PDF content
            {"role": "user", "content": text}  # Providing  user question
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        return response.choices[0].message.content  
    except Exception as e:
        logger.error(f"Error while getting OpenAI response: {str(e)}")
        if "rate limit" in str(e).lower():
            return "Rate limit exceeded. Please try again later."
        return f"Error: {str(e)}"
