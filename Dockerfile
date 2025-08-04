# Base image with Python 3.10 (compatible with pyaudio and streamlit)
FROM python:3.10-slim

# System-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    libmagic-dev \
    git \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit entrypoint
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.enableXsrfProtection=false"]
