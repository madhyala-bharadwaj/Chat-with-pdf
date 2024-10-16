import streamlit as st
import os
import json
import logging
from pinata_helper import upload_pdf_to_pinata
from openai_helper import get_openai_response
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import traceback
from utils import *

data_directory = 'data'

# Create a data directory if it doesn't exist
os.makedirs(data_directory, exist_ok=True)
os.makedirs(os.path.join(data_directory,'files'), exist_ok=True)

# Logging configuration
log_file_path = os.path.join(data_directory, 'logs', 'app.log')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# environment variables
load_dotenv()

st.set_page_config(page_title="Chat with PDFs", layout="wide")

st.markdown("<h1 style='text-align: center;'>Chat with PDFs using OpenAI and Pinata</h1>", unsafe_allow_html=True)

# Initializing session state for chat history, loading state, and PDF text
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "loading" not in st.session_state:
    st.session_state.loading = False
if "pdf_cid" not in st.session_state:
    st.session_state.pdf_cid = ""
if "status_message" not in st.session_state:
    st.session_state.status_message = ""
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

chat_history_path = os.path.join(data_directory,"chat_history.json")
feedback_path = os.path.join(data_directory,"feedback.txt")

# Load previous chat history if available
load_chat_history(chat_history_path)

left_col, right_col = st.columns([1, 2], gap="small")

# Upload and Question
with left_col:
    with st.container():
        st.subheader("Uploading File")

        # Upload the PDF file
        uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

        # If a file is uploaded, display PDF-related options
        if uploaded_file is not None :
            if uploaded_file.size > 10 * 1024 * 1024:
                st.error("File size exceeds the 10 MB limit. Please upload a smaller file.")
                uploaded_file = None
            else:
                st.session_state.uploaded_file_name = uploaded_file.name
                st.write(f"Uploaded File: {st.session_state.uploaded_file_name}")
            
                # Save the uploaded file temporarily
                file_path = os.path.join(data_directory,"files", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Extract text from the PDF
                pdf_reader = PdfReader(file_path)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
                # Store extracted text in session state
                st.session_state.pdf_text = pdf_text

                # Upload PDF to Pinata and display the CID
                st.session_state.status_message = "Uploading PDF to Pinata..."
                def upload_pdf():
                    return upload_pdf_to_pinata(file_path)
                pdf_cid = upload_pdf_to_pinata(file_path)

                if pdf_cid:
                    st.session_state.pdf_cid = pdf_cid
                    st.session_state.status_message = f"File uploaded to IPFS with CID: {pdf_cid}"
                    logger.info(f"PDF uploaded to Pinata successfully with CID: {pdf_cid}")
                else:
                    st.session_state.status_message = "Failed to upload PDF to Pinata."
                    logger.error("Failed to upload PDF to Pinata.")

        # Ask Question Section (Text input + Send button)
        user_input = st.text_input("Ask something about the PDF:", disabled=st.session_state.loading)

        if st.button("Send", disabled=st.session_state.loading):
            if user_input:
                st.session_state.loading = True
                try:
                    # Fetching AI response with retry
                    def get_response():
                        return get_openai_response(user_input, st.session_state.pdf_text)
                    
                    # Processing the user input and get a response from OpenAI
                    with st.spinner("AI is thinking..."):
                        response = retry_operation(get_response)
                    if response:
                        st.session_state.chat_history.append({"user": user_input, "ai": response})
                        save_chat_history(chat_history_path) # saving after each response
                    else:
                        st.error('Failed to get a response. Please try again.')
                except Exception as e:
                    st.error("An error occurred while processing your request.")
                    logger.error(f"Exception in AI response: {str(e)} - Traceback: {traceback.format_exc()}")

                # Reset the input field after sending the message
                st.session_state.loading = False

# Current Status
with left_col:
    if st.session_state.status_message:
        with st.container():
            st.subheader("Current Status")
            st.write(st.session_state.status_message)

# Chat Section
with right_col:
    st.subheader("Chat History")

    st.markdown(
        """
        <style>
        .scrollable-chat {
            max-height: calc(100vh - 350px); 
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: #1e1e1e;
            border-radius: 8px;
            display: flex;
            flex-direction: column-reverse;
        }
        .user-message, .ai-message {
            display: block;
            align-items: center;
            justify-content: flex-start;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
            line-height: 1.4;
            font-size: 14px;
            max-width: 80%;
            word-wrap: break-word;
            transition: background-color 0.3s, transform 0.3s;
        }
        .user-message {
            background-color: #0d6efd;
            color: white;
            margin-left: auto;
            cursor: pointer;
        }
        .ai-message {
            background-color: #6c757d;
            color: white;
            margin-right: auto;
            cursor: pointer;
        }
        .user-message:hover, .ai-message:hover {
            transform: scale(1.02);
        }
        .clear-chat-btn-container {
            margin-top: 10px; /* Reduce extra space above the button */
            text-align: center; /* Center the button */
        }
        .user-message img, .ai-message img {
            width: 24px;
            height: 24px;
            border-radius: 12px;
            vertical-align: middle;
        }
        </style>
        <script>
        function askFollowUp(message) {
            document.querySelector("input[type='text']").value = message;
            document.querySelector("input[type='text']").focus();
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.chat_history:
        chat_content = "<div class='scrollable-chat'>"
        for chat in reversed(st.session_state.chat_history):
            user_msg = f"<div class='user-message' onclick='askFollowUp({json.dumps(chat['user'])})'><strong><img src='https://iili.io/2Hi5Mve.png' alt='User'></strong> {chat['user']}</div>"

            ai_msg = f"<div class='ai-message' onclick='askFollowUp({json.dumps(chat['ai'])})'><strong><img src='https://cdn.iconscout.com/icon/premium/png-512-thumb/chatbot-5540128-4616557.png?f=webp&w=256' alt='AI'></strong>{chat['ai']}</div>"

            chat_content += ai_msg + user_msg
        chat_content += '</div>'
        st.markdown(chat_content, unsafe_allow_html=True)

    else:
        st.write("Your chat will be visible here.")

    # Clear Chat Button
    st.markdown("<div class='clear-chat-btn-container'>", unsafe_allow_html=True)
    if st.button("Clear Chat History", key="clear_chat_btn"):
        st.session_state.chat_history = []
        save_chat_history(chat_history_path)
        logger.info("User cleared chat history.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Feedback Form
    with st.container():
        st.subheader("Feedback")
        feedback = st.text_area("Please provide your feedback on the AI responses:", height=100)
        if st.button("Submit Feedback"):
            st.session_state.status_message = "Thank you for your feedback!"
            save_feedback(feedback, feedback_path)
            logger.info(f"User feedback: {feedback}")