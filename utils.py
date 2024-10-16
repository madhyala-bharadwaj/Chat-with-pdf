import time
import json
import streamlit as st
import logging
import os

# Logging configuration
log_file_path = os.path.join('data', 'logs', 'app.log')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Save chat history to a local file
def save_chat_history(chat_history_path):
    """
    Saves the current chat history from `st.session_state.chat_history` to a specified file in JSON format.
    
    Inputs:
    - chat_history_path (str): The path to the file where the chat history will be saved.
    
    Returns:
    - None
    
    This function opens the file at the specified `chat_history_path` in write mode and saves the chat history 
    from `st.session_state.chat_history` as JSON. It logs a success message if the operation is successful, 
    or logs an error message if there is a failure during the save operation.
    """
    try:
        with open(chat_history_path, "w") as f:
            json.dump(st.session_state.chat_history, f)
        logger.info("Chat history saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save chat history: {str(e)}")

# Feedback Handling
def save_feedback(feedback, feedback_path):
    """
    Appends user feedback to a specified local file.
    
    Inputs:
    - feedback (str): The feedback message provided by the user.
    - feedback_path (str): The path to the file where the feedback will be saved.
    
    Returns:
    - None
    
    This function opens the file at `feedback_path` in append mode and writes the provided `feedback` to it. 
    If successful, it logs a success message. If there is an issue saving the feedback, it logs an error 
    message.
    """
    try:
        with open(feedback_path, "a") as f:
            f.write(feedback + "\n")
        logger.info("Feedback saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save feedback: {str(e)}")

# Load chat history from a local file
def load_chat_history(chat_history_path):
    """
    Loads chat history from a specified JSON file and restores it into `st.session_state.chat_history`.
    
    Inputs:
    - chat_history_path (str): The path to the file from which the chat history will be loaded.
    
    Returns:
    - None
    
    This function checks if the file at `chat_history_path` exists. If it does, it opens the file, reads its 
    contents, and loads the chat history into `st.session_state.chat_history`. It logs a success message if 
    the chat history is successfully loaded, or logs an error message if there is any issue during the process.
    """
    try:
        if os.path.exists(chat_history_path):
            with open("chat_history.json", "r") as f:
                st.session_state.chat_history = json.load(f)
            logger.info("Chat history loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load chat history: {str(e)}")

# Handle retry mechanism for network operations
def retry_operation(operation, retries=3, delay=2):
    """
    Retries a network or external operation multiple times in case of failure.
    
    Inputs:
    - operation (function): A callable function representing the network operation to be retried.
    - retries (int): The maximum number of retry attempts (default is 3).
    - delay (int): The delay (in seconds) between each retry attempt (default is 2 seconds).
    
    Returns:
    - result: The result of the operation if successful, or None if all retry attempts fail.
    
    This function attempts to execute the given `operation` function. If it fails, it retries the operation 
    up to `retries` times, waiting for `delay` seconds between each attempt. A warning message is logged 
    for each failed attempt. If all retries are exhausted, the function returns None.
    """
    for i in range(retries):
        try:
            result = operation()
            return result
        except Exception as e:
            logger.warning(f"Operation failed, retry {i+1}/{retries}. Error: {str(e)}")
            time.sleep(delay)
    return None