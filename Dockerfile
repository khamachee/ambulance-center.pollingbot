FROM python
WORKDIR /app 
COPY requirements.txt .
EXPOSE 8000
RUN pip install -Ur requirements.txt
