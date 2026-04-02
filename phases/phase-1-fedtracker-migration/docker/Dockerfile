#Use Oracle Linux 9 as the base image
FROM oraclelinux:9-slim AS builder

LABEL maintainer="lab-operator" \
            app="fedtracker" \
            version="1.0"

#Install Python 3.11
RUN microdnf install -y python3 python3-pip &&\
    microdnf clean all

#Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

#Copy application 
COPY main.py .

#Create non root user
RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser /app
USER appuser 

#Expose the application port
EXPOSE 8000

#Health check for orchestration
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

#Run the application
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

