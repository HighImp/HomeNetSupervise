# HomeNetSupervise

Eine lokale Webanwendung zur Überwachung von Netzwerkdiensten und verbundenen Geräten im Heimnetzwerk.

## Features

- Überwachung von Diensten via Ping und Portprüfung
- Anzeige verbundener Netzwerkgeräte
- Manuelle Überprüfung beliebiger Hosts und Ports
- Einfache Weboberfläche
- Automatische Aktualisierung alle 30 Sekunden
- Docker-Container für einfache Installation

## Voraussetzungen

- Docker und Docker Compose
- Linux-Host mit Netzwerkzugriff
- Root-Rechte für Ping-Befehle

## Installation

1. Repository klonen:
```bash
git clone https://github.com/yourusername/homenetsupervise.git
cd homenetsupervise
```

2. Konfiguration anpassen:
- Kopieren Sie die `config.yaml` und passen Sie die Dienste und Geräte an
- Die Konfigurationsdatei muss im `config`-Verzeichnis liegen

3. Container starten:
```bash
docker-compose up -d
```

Die Anwendung ist dann unter `http://localhost:8000` erreichbar.

## Konfiguration

Die `config.yaml` enthält zwei Hauptabschnitte:

### Services
```yaml
services:
  - name: Home Assistant
    host: 192.168.178.100
    port: 8123
```

### Devices
```yaml
devices:
  - mac: "AA:BB:CC:DD:EE:FF"
    alias: "Wohnzimmer TV"
    ip: "192.168.178.50"
```

## Entwicklung

1. Virtuelle Umgebung erstellen:
```bash
python -m venv venv
source venv/bin/activate
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. Backend starten:
```bash
python backend.py
```

## Lizenz

MIT 