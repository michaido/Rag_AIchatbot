# Χρησιμοποιούμε επίσημο Python image
FROM python:3.11-slim

# Ενημερώνουμε το σύστημα και εγκαθιστούμε απαραίτητα πακέτα
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Ορίζουμε τον κατάλογο εργασίας
WORKDIR /app

# Αντιγράφουμε τα αρχεία στον container
COPY . /app

# Debugging: Δες αν τα αρχεία είναι εκεί
RUN ls -l /app

# Εγκαθιστούμε τις απαιτούμενες βιβλιοθήκες
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Εκθέτουμε την πόρτα 8000
EXPOSE 8000

# Εκτελούμε την εφαρμογή
CMD ["python", "-m", "streamlit", "run", "chatbot_gemini.py", "--server.port=8000", "--server.address=0.0.0.0"]
