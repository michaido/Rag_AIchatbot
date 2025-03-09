import streamlit as st
import os
import pickle
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

# Φόρτωση μεταβλητών περιβάλλοντος από το .env
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Διαμόρφωση του DeepSeek API
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

def get_response(input):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": input}],
        "temperature": 0.7,
        "top_p": 1,
        "max_tokens": 2048
    }
    
    response = requests.post(DEEPSEEK_ENDPOINT, json=payload, headers=headers)
    response_data = response.json()
    
    return response_data["choices"][0]["message"]["content"]

encoder = SentenceTransformer('lighteternal/stsb-xlm-r-greek-transfer')

rag_db = "rag_df.pkl"
with open(rag_db, "rb") as fh:
    rag_df = pickle.load(fh)

index_file = "index.pkl"
with open(index_file, "rb") as fh:
    index, rag_df = pickle.load(fh)

with st.sidebar:
    st.image("IHU_logo_blue_clear_gr.png", width=150)

st.title("Διαλογικός βοηθός διαχείρισης της έρευνας στον ΕΛΚΕ")
st.header("Ρωτήστε σχετικά με τρόπους διαχείρισης της έρευνας")

if 'prompts' not in st.session_state:
    st.session_state['prompts'] = []

if 'responses' not in st.session_state:
    st.session_state['responses'] = []

prompt = st.text_area("Χρήστης:", placeholder="Γράψτε κείμενο")

submit_button = st.button("Αποστολή")

if submit_button:
    print("Submitted!")  # ✅ Επιβεβαίωση υποβολής
    if prompt is not None and prompt != "":
        print(f"Prompt:\n{prompt}")  # ✅ Εκτύπωση ερωτήματος χρήστη
        search_vector = encoder.encode(prompt)
        _vector = np.array([search_vector])
        faiss.normalize_L2(_vector)

        k = 15
        dist, idx = index.search(_vector, k=k)

        rag_prompt = f"{prompt}\nΒάσισε την απάντηση στα παρακάτω:\n"

        # ✅ Εκτύπωση των κειμένων στα οποία βασίζεται η απάντηση
        print("Βάσισε την απάντηση στα παρακάτω:")
        for i in range(k):
            chunk = rag_df[idx[0][i]]
            rag_prompt += f"{chunk['text']}\n"
            print(f" - {chunk['text']}")  # ✅ Τυπώνει κάθε πηγή στο CMD

        response = get_response(rag_prompt)
        final_response = f"{response}"
        st.session_state.prompts.append(prompt)
        st.session_state.responses.append(final_response)
        st.write(f"Βοηθός:  \n>{final_response}")
    else:
        print("Not submitted")  # ✅ Μήνυμα αν δεν δόθηκε input
        st.write(":red[Κενό κείμενο]")
