FROM python:3.11-slim

WORKDIR /app

# Installiere notwendige Pakete
RUN apt-get update && apt-get install -y \
    iputils-ping \
    netcat-openbsd \
    arp-scan \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setze die notwendigen Capabilities für ping
RUN setcap cap_net_raw+ep /usr/bin/ping

# Installiere die IEEE OUI-Datei
RUN mkdir -p /usr/share/arp-scan && \
    curl -o /usr/share/arp-scan/ieee-oui.txt https://standards-oui.ieee.org/oui/oui.txt && \
    sed -i '/^[0-9A-F]\{2\}-[0-9A-F]\{2\}-[0-9A-F]\{2\}/!d' /usr/share/arp-scan/ieee-oui.txt

# Kopiere die Anforderungen und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . .

# Create volume for config
VOLUME ["/app/config"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/status || exit 1

# Starte die Anwendung
CMD ["python", "backend.py"] 