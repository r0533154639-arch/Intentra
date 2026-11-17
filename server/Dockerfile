
FROM python:3.12-slim

# Install system certificate management tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add NetFree CA certificate
COPY certs/netfree-ca.crt /usr/local/share/ca-certificates/netfree-ca.crt
COPY certs/netfree-root-rsa.crt /usr/local/share/ca-certificates/netfree-root-rsa.crt
COPY certs/netfree-root-legacy-rsa.crt /usr/local/share/ca-certificates/netfree-root-legacy-rsa.crt

# Update trusted certificates
RUN update-ca-certificates

# Configure Python tools to use the system CA certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt


WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
