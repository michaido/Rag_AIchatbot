# RAG AI Chatbot with Gemini API

This is an interactive AI chatbot that uses Retrieval-Augmented Generation (RAG) and Google's Gemini API.

## 🚀 Setup Instructions

### 1️⃣ Clone the repository
To get started, clone this repository and navigate into the project folder:
git clone https://github.com/michaido/rag_AIchatbot.git
cd rag_AIchatbot

2️⃣ Install dependencies
Ensure you have Python installed, then install the required dependencies:
pip install -r requirements.txt

3️⃣ Set up environment variables
Create a .env file in the root directory and add your Google Gemini API key:

GEMINI_API_KEY=your_api_key_here
Alternatively, use an environment variable:
export GEMINI_API_KEY=your_api_key_here

4️⃣ Run the chatbot
Start the chatbot using Streamlit:
streamlit run chatbot_gemini.py

📌 Features
Uses Google Gemini API for AI responses
Supports Retrieval-Augmented Generation (RAG)
Handles PDF processing and chunking
Uses FAISS vector search for fast retrieval
