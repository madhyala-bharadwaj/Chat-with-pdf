import os
import requests 
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

# environment variables from the .env file
load_dotenv()

# Pinata API URL for pinning files to IPFS
PINATA_API_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

# API keys from environment variables
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

def upload_pdf_to_pinata(file_path):
    """
    Uploads a PDF file to Pinata's IPFS service.

    Args:
        file_path (str): The path to the PDF file to be uploaded.

    Returns:
        str: The IPFS hash of the uploaded file if successful, None otherwise.
    """

    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    try:
        with open(file_path, 'rb') as file:
            # POST request to Pinata API to upload the file
            response = requests.post(PINATA_API_URL, files={'file': file}, headers=headers)

            if response.status_code == 200:
                logger.info("File uploaded successfully to Pinata.")
                return response.json()['IpfsHash']
            else:
                logger.error(f"Pinata upload failed: {response.text}")
                return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while uploading to Pinata: {str(e)}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.text}")
    except FileNotFoundError:
        logging.error("The specified file was not found.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return None