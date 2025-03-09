import os
import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pdfplumber import open as pdf_open
from pypdf import PdfReader
import deepseek

# Φόρτωση μεταβλητών περιβάλλοντος
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Φόρτωση του sentence transformer για embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Αρχικοποίηση FAISS index
index = faiss.IndexFlatL2(384)
texts = []

# Φόρτωση και επεξεργασία PDF
def load_pdf(file):
    global texts, index
    pdf = PdfReader(file)
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
            vector = model.encode(text)
            index.add(np.array([vector]))

# Ερώτημα στο DeepSeek API
def query_deepseek(prompt):
    deepseek.api_key = DEEPSEEK_API_KEY
    response = deepseek.ChatCompletion.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("RAG Chatbot with DeepSeek")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    load_pdf(uploaded_file)

query = st.text_input("Ask a question:")
if query:
    query_vector = model.encode(query)
    _vector = np.array([query_vector])
    k = 5
    dist, idx = index.search(_vector, k=k)
    
    context = " ".join([texts[i] for i in idx[0] if i < len(texts)])
    full_prompt = f"Context: {context}\n\nQuestion: {query}"
    
    response = query_deepseek(full_prompt)
    st.write(response)
