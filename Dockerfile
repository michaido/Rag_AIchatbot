FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "chatbot_deepseek.py", "--server.port=8000", "--server.address=0.0.0.0"]
