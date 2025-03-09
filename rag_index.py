import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Φόρτωση των chunks από το rag_df.pkl
print("Φόρτωση των chunks από το rag_df.pkl...")
with open("rag_df.pkl", "rb") as f:
    chunks = pickle.load(f)

# Φόρτωση SentenceTransformer για δημιουργία embeddings
print("Φόρτωση SentenceTransformer για δημιουργία embeddings...")
encoder = SentenceTransformer("lighteternal/stsb-xlm-r-greek-transfer")

# Συνδυασμός metadata με το κείμενο των chunks
print("Μετατροπή των chunks σε embeddings με metadata...")
def format_chunk(chunk):
    if "article_number" in chunk:  # PDF με άρθρα
        return f"{chunk.get('article_number', '')} {chunk.get('article_title', '')} {chunk['text']}"
    else:  # PDF χωρίς άρθρα
        return f"{chunk.get('main_title', '')} {chunk.get('sub_title', '')} {chunk.get('section', '')} {chunk['text']}"

text_data = [format_chunk(chunk) for chunk in chunks]

# Μετατροπή σε embeddings
embeddings = encoder.encode(text_data, convert_to_numpy=True)
faiss.normalize_L2(embeddings)

# Δημιουργία FAISS index
print("Δημιουργία FAISS Index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Αποθήκευση FAISS index μαζί με τα metadata των chunks
with open("index.pkl", "wb") as f:
    pickle.dump((index, chunks), f)

print("✅ FAISS Index δημιουργήθηκε και αποθηκεύτηκε επιτυχώς.")
