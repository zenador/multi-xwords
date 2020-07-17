FROM python:3.8.4-slim
WORKDIR /proj
COPY download.sh .
COPY requirements.txt .
RUN \
    bash ./download.sh && \
    pip install -r ./requirements.txt
COPY . .
CMD ["python", "flaskapp.py"]
