# Χρησιμοποιούμε επίσημο Python image για τη βάση μας
FROM python:3.11-slim

# Εγκαθιστούμε το λειτουργικό σύστημα και τα dependencies για το Streamlit και το Gemini API
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Ορίζουμε τον κατάλογο εργασίας για την εφαρμογή
WORKDIR /app

# Αντιγράφουμε το τοπικό μας έργο στον κατάλογο του container
COPY . .

# Εγκαθιστούμε τις βιβλιοθήκες που αναφέρονται στο requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Εκθέτουμε την πόρτα στην οποία θα τρέξει η εφαρμογή μας (π.χ. 8000)
EXPOSE 8000

# Ορίζουμε την εντολή εκκίνησης για το container (τρεχουμε την εφαρμογή με Streamlit)
CMD ["sh", "-c", "pip install -r requirements.txt && python -m streamlit run chatbot_gemini.py --server.port=8000 --server.address=0.0.0.0"]
