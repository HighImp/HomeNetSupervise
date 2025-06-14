# HomeNetSupervise

Ein leistungsstarkes Netzwerküberwachungstool für Heimnetzwerke, das Geräte, Dienste und offene Ports automatisch erkennt und überwacht.

## Features

- 🔍 Automatische Erkennung von Netzwerkgeräten
- 🌐 Port-Scanning und Dienstüberwachung
- 📊 Übersichtliche Darstellung aller Netzwerkgeräte und Dienste
- 🔄 Echtzeit-Statusüberwachung
- 📱 Responsive Web-Oberfläche
- 🔐 MAC-Adress-Erkennung und Herstelleridentifikation
- 💾 Konfigurationsimport/-export

## Systemanforderungen

- Python 3.8 oder höher
- Linux-Betriebssystem (für ARP-Scanning)
- Netzwerkzugriff auf das zu überwachende Subnetz

## Installation

1. Repository klonen:
```bash
git clone https://github.com/HighImp/HomeNetSupervise.git
cd HomeNetSupervise
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
.\venv\Scripts\activate  # Windows
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Anwendung starten:
```bash
python backend.py
```

5. Webinterface aufrufen:
```
http://localhost:8000
```

## Konfiguration

Die Anwendung kann über die `config.yaml` Datei konfiguriert werden:

```yaml
# Beispiel-Konfiguration
network:
  subnet: "192.168.178.0/24"  # Zu überwachendes Subnetz
  scan_interval: 300          # Scan-Intervall in Sekunden (5 Minuten)
  port_scan_timeout: 1        # Timeout pro Port in Sekunden
  max_concurrent_scans: 10    # Maximale Anzahl gleichzeitiger Scans
```

## Verwendung

### Autoscan
1. Öffne das Webinterface
2. Navigiere zum "Autoscan" Bereich
3. Gib das zu scannende Subnetz ein (z.B. 192.168.178.0/24)
4. Wähle die zu scannenden Ports
5. Starte den Scan

### Einzelgerät-Scan
1. Wähle ein Gerät aus der Liste
2. Klicke auf "Ports scannen"
3. Warte auf die Ergebnisse

### Konfiguration exportieren/importieren
1. Nutze die Buttons "Konfiguration exportieren" oder "Konfiguration importieren"
2. Die Konfiguration wird als JSON-Datei gespeichert/geladen

## Sicherheitshinweise

- Die Anwendung benötigt Root-Rechte für ARP-Scanning
- Stelle sicher, dass nur autorisierte Benutzer Zugriff auf das Webinterface haben
- Verwende HTTPS in Produktionsumgebungen

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

## Beitragen

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue für Verbesserungsvorschläge.

## Support

Bei Problemen oder Fragen:
1. Überprüfe die [Issues](https://github.com/HighImp/HomeNetSupervise/issues)
2. Erstelle ein neues Issue, falls dein Problem noch nicht dokumentiert ist 