# Requirements Management Tool mit KI-Unterstützung

Eine moderne Flask-basierte Webanwendung für professionelles Requirements Engineering mit integrierter OpenAI KI-Unterstützung.

## 📋 Überblick

Dieses System ermöglicht die systematische Erstellung, Verwaltung und Versionierung von Software-Anforderungen nach modernen Requirements Engineering Standards. Die KI-Integration unterstützt bei der Generierung, Optimierung und Qualitätssicherung von Anforderungen.

## ✨ Hauptfunktionen

### 👤 Benutzerverwaltung
- Sichere Registrierung und Authentifizierung
- Passwort-Hashing mit Werkzeug
- Sitzungsverwaltung mit Flask-Login

### 📁 Projektmanagement
- Multi-Projekt-Unterstützung
- Dynamische Spaltenkonfiguration pro Projekt
- Projekt-Sharing zwischen Benutzern
- Versionsverwaltung (A, B, C, ...)

### 📝 Anforderungsmanagement
- CRUD-Operationen für Anforderungen
- Versionierung mit vollständiger Historie
- Status-Tracking (Offen, In Arbeit, Fertig)
- Soft-Delete mit Wiederherstellungsfunktion
- Anforderungs-Blockierung für Workflow-Management

### 🤖 KI-Unterstützung
- **Neue Anforderungen generieren**: KI erstellt mindestens 5 neue, kreative Anforderungen
- **Excel-Optimierung**: KI verbessert bestehende Anforderungen aus Excel-Dateien
- **Alternative Versionen**: Automatische Generierung von Anforderungs-Alternativen
- 4-Phasen-Methodik: Analyse → Struktur → Erstellung → Review
- SMART-Kriterien und Normenkonformität

### 📊 Datenmanagement
- Excel Import mit KI-Optimierung
- Excel Export mit vollständiger Historie
- Dateiarchiv mit Quellenreferenzierung
- Dynamische Spaltenunterstützung

### 🎨 Benutzeroberfläche
- Responsive Bootstrap 5 Design
- Filterbare und durchsuchbare Anforderungslisten
- Inline-Bearbeitung
- Archiv-Ansicht für alle importierten/generierten Dateien

## 🏗️ Architektur

### Backend-Stack
```
Flask 3.1.2           - Web Framework
SQLAlchemy 2.0.43     - ORM
Flask-Login 0.6.3     - Authentifizierung
OpenAI >= 1.0.0       - KI-Integration
openpyxl 3.1.2        - Excel-Verarbeitung
```

### Datenbankmodell
```
User
  └── Project (many-to-many sharing)
       ├── Requirement
       │    └── RequirementVersion (versioniert)
       │         └── source_file (FK zu ProjectFile)
       └── ProjectFile (Upload/Generated/Export)
```

### KI-Dienste
- **`generate_new_requirements()`**: Neue Anforderungen generieren
- **`optimize_excel_requirements()`**: Excel-Anforderungen optimieren
- **`AIClient.analyze_requirements()`**: Anforderungsanalyse
- **`AIClient.suggest_improvements()`**: Verbesserungsvorschläge

## 📦 Installation

### Voraussetzungen
- Python 3.8+
- OpenAI API Key

### Setup

1. **Repository klonen**
```bash
git clone <repository-url>
cd Interface_for_MBSE_Models
```

2. **Virtuelle Umgebung erstellen**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren**

Erstelle eine `.env` Datei im Hauptverzeichnis:
```env
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

5. **Anwendung starten**
```bash
python main.py
```

Die Anwendung läuft auf: `http://127.0.0.1:5000`

## 🗂️ Projektstruktur

```
Interface_for_MBSE_Models/
├── app/                          # Hauptanwendung
│   ├── __init__.py              # Flask App Factory
│   ├── auth.py                  # Authentifizierung
│   ├── routes.py                # Haupt-Routen
│   ├── agent.py                 # KI-Routen
│   ├── models.py                # Datenbankmodelle
│   ├── migration.py             # Migrationsskripte
│   ├── services/                # Business Logic
│   │   ├── ai_client.py        # OpenAI Integration
│   │   └── exel_service.py     # Excel-Verarbeitung
│   ├── static/                  # Statische Dateien
│   │   ├── project.js          # Frontend-Logik
│   │   ├── style.css           # Custom CSS
│   │   └── bootstrap.*         # Bootstrap Dateien
│   └── templates/               # Jinja2 Templates
│       ├── base.html           # Basis-Template
│       ├── create.html         # Projekt-Übersicht
│       ├── agent/              # KI-Templates
│       └── auth/               # Auth-Templates
├── archive/                     # Alte Skripte (nicht verwenden!)
│   ├── migrations/             # Alte Migrationen
│   ├── tests/                  # Alte Tests
│   └── debug/                  # Debug-Skripte
├── instance/                    # SQLite DB & Uploads
│   ├── db.db                   # Datenbank
│   └── temp/                   # Temporäre Dateien
├── uploads/                     # Hochgeladene Dateien
├── scripts/                     # Hilfsskripte
├── main.py                      # Einstiegspunkt
├── config.py                    # Konfiguration
├── requirements.txt             # Python Dependencies
├── .env                         # Umgebungsvariablen (nicht committen!)
└── README.md                    # Diese Datei
```

## 🚀 Verwendung

### 1. Projekt erstellen
- Anmelden/Registrieren
- "Neues Projekt" erstellen
- Projekt öffnen

### 2. Anforderungen hinzufügen

**Option A: Mit KI generieren**
- "KI-Agent" öffnen
- Beschreibung eingeben
- "Generieren" klicken
- Mindestens 5 neue Anforderungen werden erstellt

**Option B: Excel hochladen**
- "Excel hochladen" auswählen
- Excel-Datei auswählen
- Optional: Beschreibung für KI-Optimierung
- KI optimiert die Anforderungen und behält die Struktur bei

### 3. Anforderungen bearbeiten
- Anforderung in der Tabelle anklicken
- "Bearbeiten" wählen
- Änderungen vornehmen
- "Zwischenspeichern" (Status: In Arbeit) oder "Fertigstellen" (Status: Fertig)

### 4. Versionen verwalten
- Dropdown neben jeder Anforderung zeigt alle Versionen (A, B, C, ...)
- Version auswählen um Inhalt zu sehen
- "Neu generieren" erstellt alternative Version mit KI

### 5. Exportieren
- "Als Excel exportieren" im Projekt
- Datei wird im Archiv gespeichert und heruntergeladen

## 🔧 Konfiguration

### OpenAI Einstellungen

In `config.py`:
```python
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
```

### Datenbankzugriff

SQLite Datenbank in `instance/db.db`. Für andere Datenbanken SQLAlchemy URI in `app/__init__.py` anpassen.

## 🤝 KI-Integration Details

### Zwei verschiedene KI-Modi:

1. **Neue Anforderungen generieren**
   - Erstellt 5+ neue Anforderungen
   - Kreativ und vielfältig
   - Verwendet Project-Spalten

2. **Excel-Optimierung**
   - Behält Anzahl und Struktur bei
   - Verbessert Formulierung, SMART-Kriterien
   - Keine zusätzlichen Spalten

### KI-Prompts

Beide Modi verwenden das 4-Phasen-Modell:
- **Phase 1 & 2**: Analyse und Strukturierung
- **Phase 3**: Erstellung/Optimierung
- **Phase 4**: Qualitätsprüfung

## 📚 Weitere Dokumentation

- `DOCUMENTATION.md` - Detaillierte technische Dokumentation
- `TODO.md` - Geplante Features und Verbesserungen
- `archive/README.md` - Informationen zu archivierten Skripten

## 🐛 Fehlerbehandlung

- **OpenAI Fehler**: Prüfe API-Key in `.env`
- **Datenbankfehler**: Datenbank mit Migration-Blueprint zurücksetzen
- **Excel-Import**: Stelle sicher, dass Excel-Datei erste Zeile als Header hat

## 📝 Lizenz

[Lizenzinformation hier einfügen]

## 👥 Autoren

[Autoreninformation hier einfügen]

## 🙏 Danksagungen

- OpenAI für GPT-4o-mini API
- Flask und SQLAlchemy Community
- Bootstrap Team für das UI Framework
