FROM python:3.10-slim

WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libasound-dev \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=10000", "--server.enableCORS=false"]
