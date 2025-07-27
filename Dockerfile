FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir streamlit cryptography

RUN mkdir -p /app/.streamlit
RUN echo "\
[general]\nemail = \"cosmic@immortal.ai\"\
" > /app/.streamlit/credentials.toml

RUN echo "\
[browser]\ngatherUsageStats = false\
" > /app/.streamlit/config.toml

ENV STREAMLIT_CONFIG_DIR=/app/.streamlit
ENV HOME=/app

EXPOSE 8501
CMD ["streamlit", "run", "cosmic_immortal_core.py", "--server.port=8501", "--server.enableCORS=false"]
