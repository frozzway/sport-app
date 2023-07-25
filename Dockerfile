FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt .
COPY requirements.freezed.txt .
RUN pip install -r requirements.freezed.txt
COPY src ./src
CMD ["sleep","3600"]
