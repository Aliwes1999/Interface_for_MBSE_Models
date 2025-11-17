# Vollständige Dokumentation - Interface für MBSE-Modelle

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Architektur](#architektur)
3. [Datenbankmodell](#datenbankmodell)
4. [API-Referenz](#api-referenz)
5. [Template-Struktur](#template-struktur)
6. [Konfiguration](#konfiguration)
7. [Entwicklung](#entwicklung)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## 🔍 Überblick

### Anwendungszweck

Die Interface für MBSE-Modelle ist eine umfassende Webanwendung für das Management von Software-Anforderungen. Sie kombiniert traditionelle Requirements-Engineering-Praktiken mit modernen KI-Funktionen und bietet eine skalierbare, benutzerfreundliche Plattform für Teams.

### Kernfunktionalitäten

- **Benutzerverwaltung**: Sichere Authentifizierung und Autorisierung
- **Projektmanagement**: Mehrere isolierte Projekte pro Benutzer
- **Anforderungslebenszyklus**: Erstellung, Versionierung, Löschung
- **KI-Integration**: Automatische Anforderungsgenerierung
- **Datenpersistenz**: Robuste SQLite-Datenbank mit Migrationen
- **Import/Export**: Excel-basierte Datenübertragung

## 🏗️ Architektur

### Systemarchitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │────│   Flask App     │────│   SQLite DB     │
│                 │    │   (Backend)     │    │   (Data)        │
│ - HTML/CSS/JS   │    │                 │    │                 │
│ - Bootstrap UI  │    │ - Routes        │    │ - Users         │
│ - AJAX Calls    │    │ - Models        │    │ - Projects      │
│                 │    │ - Services      │    │ - Requirements  │
└─────────────────┘    │ - Templates     │    │ - Versions      │
                       └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (AI Service)  │
                       └─────────────────┘
```

### Komponentenübersicht

#### Backend (Flask)

- **app/**init**.py**: Anwendungsfactory und Konfiguration
- **app/routes.py**: HTTP-Routen und Geschäftslogik
- **app/models.py**: Datenbankmodelle und Beziehungen
- **app/auth.py**: Authentifizierungs- und Autorisierungslogik
- **app/agent.py**: KI-Agent Integration
- **app/services/ai_client.py**: OpenAI API Client

#### Frontend (Jinja2 + Bootstrap)

- **base.html**: Basis-Template mit Navigation
- **start.html**: Dashboard/Homepage
- **create.html**: Projekt- und Anforderungsverwaltung
- **deleted_requirements_overview.html**: Papierkorb-Übersicht

#### Konfiguration

- **config.py**: Umgebungsvariablen und Einstellungen
- **main.py**: Anwendungsstartpunkt

## 💾 Datenbankmodell

### ER-Diagramm

```
User (1) ──── (N) Project (1) ──── (N) Requirement (1) ──── (N) RequirementVersion
  │              │                   │                        │
  │              │                   │                        │
  └──────────────┼───────────────────┼────────────────────────┘
                 │                   │
                 └───────────────────┼───────────────────────── ProjectUser (M:N)
                                     │
                                     └───────────────────────── is_deleted (Soft Delete)
```

### Tabellen-Details

#### User

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Project

```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    custom_columns TEXT DEFAULT '[]',
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

#### ProjectUser (Association Table)

```sql
CREATE TABLE project_user_association (
    project_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES project(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

#### Requirement

```sql
CREATE TABLE requirement (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    key VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

#### RequirementVersion

```sql
CREATE TABLE requirement_version (
    id INTEGER PRIMARY KEY,
    requirement_id INTEGER NOT NULL,
    version_index INTEGER NOT NULL,
    version_label VARCHAR(4) NOT NULL,
    title VARCHAR(160) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(80),
    status VARCHAR(30) DEFAULT 'Offen',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    custom_data TEXT DEFAULT '{}',
    created_by_id INTEGER,
    last_modified_by_id INTEGER,
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_by_id INTEGER,
    blocked_at DATETIME,
    FOREIGN KEY (requirement_id) REFERENCES requirement(id),
    FOREIGN KEY (created_by_id) REFERENCES user(id),
    FOREIGN KEY (last_modified_by_id) REFERENCES user(id),
    FOREIGN KEY (blocked_by_id) REFERENCES user(id),
    UNIQUE(requirement_id, version_index)
);
```

### Beziehungen und Constraints

- **User-Project**: 1:N (Ein User kann mehrere Projekte haben)
- **Project-Requirement**: 1:N (Ein Projekt kann mehrere Requirements haben)
- **Requirement-RequirementVersion**: 1:N (Ein Requirement kann mehrere Versionen haben)
- **Project-Sharing**: N:M (Projekte können mit mehreren Usern geteilt werden)
- **Version Blocking**: Versions können von Usern blockiert werden

## 🔌 API-Referenz

### Authentifizierung

#### POST /auth/login

Benutzeranmeldung

```python
# Request
{
    "email": "user@example.com",
    "password": "password123"
}

# Response
HTTP 302 -> Redirect to home
```

#### POST /auth/register

Benutzerregistrierung

```python
# Request
{
    "email": "user@example.com",
    "password": "password123",
    "confirm_password": "password123"
}

# Response
HTTP 302 -> Redirect to login
```

### Projektmanagement

#### GET /

Dashboard mit Projektliste

```python
# Response
{
    "projects": [
        {
            "id": 1,
            "name": "Projekt A",
            "created_at": "2024-01-01T00:00:00"
        }
    ]
}
```

#### POST /create

Neues Projekt erstellen

```python
# Request Form Data
{
    "project_name": "Neues Projekt"
}

# Response
HTTP 302 -> Redirect to home
```

#### GET /project/{project_id}

Projekt-Details und Requirements

```python
# Response
{
    "project": {...},
    "req_with_versions": [...],
    "custom_columns": [...]
}
```

### Anforderungsmanagement

#### POST /requirement/{req_id}/delete

Soft-Delete einer Anforderung

```python
# Response
HTTP 302 -> Redirect to deleted_requirements_overview
```

#### POST /requirement/{req_id}/restore

Wiederherstellung einer gelöschten Anforderung

```python
# Response
HTTP 302 -> Redirect to deleted_requirements_overview
```

#### POST /requirement/{req_id}/delete_permanently

Permanente Löschung einer Anforderung

```python
# Response
HTTP 302 -> Redirect to deleted_requirements_overview
```

### KI-Integration

#### POST /aiAgent (via Template)

KI-gestützte Anforderungsgenerierung

```python
# Request Form Data
{
    "user_description": "Benutzerbeschreibung",
    "inputs": {"key": "value"},
    "columns": ["title", "description", "category"]
}

# Response
{
    "requirements": [
        {
            "title": "Generierter Titel",
            "description": "Generierte Beschreibung",
            "category": "Funktional"
        }
    ]
}
```

### AJAX-Endpunkte

#### GET /requirement/{req_id}/versions_json

Versionsdaten für eine Anforderung

```python
# Response
[
    {
        "id": 1,
        "version_index": 1,
        "version_label": "A",
        "title": "Titel",
        "description": "Beschreibung",
        "status": "Offen",
        "custom_data": {...}
    }
]
```

#### POST /requirement_version/{version_id}/update_custom_data

Update von Custom Column Data

```python
# Request
{
    "column_name": "custom_field",
    "value": "new_value"
}

# Response
{"success": true}
```

## 🎨 Template-Struktur

### Basis-Template (base.html)

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}Requirements Tool{% endblock %}</title>
    <!-- Bootstrap CSS, Icons, Custom CSS -->
  </head>
  <body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-dark bg-dark">
      <!-- Menu Items -->
    </nav>

    <main class="container">
      <!-- Flash Messages -->
      {% with messages = get_flashed_messages(with_categories=true) %}
      <!-- Message Display -->
      {% endfor %} {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer>...</footer>

    <!-- Scripts -->
  </body>
</html>
```

### Projekt-Template (create.html)

```html
{% extends "base.html" %} {% block content %}
<div class="project-header">
  <h2>{{ project.name }}</h2>
  <!-- Project Actions -->
</div>

<div class="requirements-table">
  <!-- Dynamic Table with Custom Columns -->
  <table class="table">
    <thead>
      <tr>
        <th>Version</th>
        <th>ID</th>
        <th>Title</th>
        <!-- Custom Columns -->
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <!-- Requirements Rows -->
    </tbody>
  </table>
</div>
{% endblock %}
```

## ⚙️ Konfiguration

### Umgebungsvariablen

#### Erforderlich

```bash
OPENAI_API_KEY=sk-proj-...
```

#### Optional

```bash
OPENAI_MODEL=gpt-4o-mini
SYSTEM_PROMPT_PATH=/path/to/prompt.txt
SYSTEM_PROMPT=Custom prompt text
```

### Datenbank-Konfiguration

```python
# In config.py
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(app.instance_path, "db.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### KI-Konfiguration

```python
# In config.py
DEFAULT_SYSTEM_PROMPT = """
Du bist ein erfahrener Requirements Engineer...
"""

def get_system_prompt(columns=None):
    # Dynamic prompt generation based on columns
    pass
```

## 💻 Entwicklung

### Lokale Entwicklungsumgebung

1. **Repository klonen**

```bash
git clone <repo-url>
cd interface_for_mbse_models
```

2. **Virtuelle Umgebung**

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Umgebung konfigurieren**

```bash
# .env erstellen
OPENAI_API_KEY=your_key_here
```

4. **Anwendung starten**

```bash
python main.py
```

### Testen

#### Unit Tests

```bash
python -m pytest tests/
```

#### Integration Tests

```bash
python test_integration.py
```

#### API Tests

```bash
python test_quick.py
```

### Code-Qualität

#### Linting

```bash
flake8 app/
```

#### Type Checking

```bash
mypy app/
```

### Datenbankmigrationen

#### Neue Migration erstellen

```python
# In migrate_new_feature.py
from app import create_app

app = create_app()

with app.app_context():
    # Migration logic here
    pass
```

#### Migration ausführen

```bash
python migrate_new_feature.py
```

## 🚀 Deployment

### Produktionsumgebung

#### WSGI Server (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

#### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

#### Environment Variables für Production

```bash
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-production-api-key
```

### Skalierung

#### Datenbank

- Für höhere Last: PostgreSQL/MySQL migrieren
- Connection Pooling konfigurieren
- Database Indexing optimieren

#### Caching

- Redis für Session Storage
- Flask-Caching für Template Caching
- CDN für statische Assets

#### Monitoring

- Application Performance Monitoring (APM)
- Error Tracking (Sentry)
- Log Aggregation

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. OpenAI API Fehler

```
RuntimeError: OpenAI request failed
```

**Lösung:**

- API Key überprüfen
- Rate Limits prüfen
- Netzwerkverbindung testen

#### 2. Datenbankfehler

```
sqlalchemy.exc.OperationalError
```

**Lösung:**

- Datenbankdatei-Berechtigungen prüfen
- Migrationen ausführen
- SQLite-Version kompatibilität

#### 3. Template-Fehler

```
jinja2.exceptions.TemplateNotFound
```

**Lösung:**

- Template-Pfade überprüfen
- Groß-/Kleinschreibung beachten
- Template-Vererbung prüfen

#### 4. Import-Fehler

```
ModuleNotFoundError
```

**Lösung:**

- Virtuelle Umgebung aktivieren
- requirements.txt installieren
- Python-Pfad prüfen

### Debug-Modus

#### Flask Debug aktivieren

```python
app.run(debug=True)
```

#### SQLAlchemy Query Logging

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Logs analysieren

#### Anwendungslogs

```bash
tail -f logs/application.log
```

#### Datenbanklogs

```python
# In config.py
SQLALCHEMY_ECHO = True
```

## 📊 Performance

### Optimierungen

#### Datenbank

- N+1 Query Problem vermeiden
- Indizes für häufige Queries
- Connection Pooling

#### Frontend

- Asset Bundling und Minification
- Lazy Loading für große Tabellen
- AJAX für dynamische Updates

#### KI-Integration

- Response Caching
- Batch Processing
- Rate Limiting

### Monitoring

#### Metriken

- Response Times
- Error Rates
- Database Query Performance
- Memory Usage

#### Alerts

- API Key Expiry
- Database Connection Issues
- High Error Rates

## 🔒 Sicherheit

### Best Practices implementiert

#### Authentifizierung

- Passwort-Hashing (Werkzeug)
- Session Management (Flask-Login)
- Account Lockout nach fehlgeschlagenen Versuchen

#### Autorisierung

- Owner-Checks für alle Ressourcen
- Shared Project Permissions
- Version Blocking für Concurrency Control

#### Input Validation

- Server-side Validation
- SQL Injection Prevention (SQLAlchemy)
- XSS Protection (Jinja2 Auto-Escaping)

#### API Security

- API Key Management
- Rate Limiting
- Error Message Sanitization

### Sicherheitsaudits

#### Regelmäßige Checks

- Dependency Scanning (Safety)
- SAST (Bandit)
- Container Security (Trivy)

## 📈 Roadmap

### Geplante Features

#### Phase 1 (Q1 2024)

- [ ] Advanced Search und Filter
- [ ] Bulk Operations
- [ ] Export to PDF

#### Phase 2 (Q2 2024)

- [ ] Real-time Collaboration
- [ ] Advanced Reporting
- [ ] API für Third-Party Integration

#### Phase 3 (Q3 2024)

- [ ] Mobile App
- [ ] Advanced AI Features
- [ ] Multi-Language Support

### Technische Verbesserungen

#### Performance

- [ ] Database Query Optimization
- [ ] Frontend Performance
- [ ] Caching Layer

#### Skalierbarkeit

- [ ] Microservices Architecture
- [ ] Horizontal Scaling
- [ ] Cloud Deployment

---

_Diese Dokumentation wird kontinuierlich aktualisiert. Bei Fragen oder Verbesserungsvorschlägen bitte ein Issue erstellen._
