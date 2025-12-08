# Lokale Entwicklung - Datenbankfehler behoben

## Problem

Die Flask-App konnte nicht lokal gestartet werden, da sie immer im Production-Modus lief und versuchte, eine PostgreSQL-Datenbank zu verwenden, anstatt SQLite für die lokale Entwicklung.

**Fehlermeldung:**

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

## Ursache

- `wsgi.py` und `app/__init__.py` erzwangen beide den Production-Modus (`FLASK_ENV=production`)
- Dies führte dazu, dass die App versuchte, PostgreSQL zu verwenden, auch bei lokaler Entwicklung
- Der SQLite-Datenbankpfad konnte nicht erstellt werden

## Lösung

### 1. `.flaskenv` Datei erstellt

Neue Datei für lokale Entwicklungsumgebung:

```
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1
```

### 2. `app/__init__.py` angepasst

- Entfernt: `os.environ.setdefault('FLASK_ENV', 'production')`
- Die App-Instanz wird nur noch erstellt, wenn das Modul importiert wird (für gunicorn)
- Lokale Entwicklung verwendet jetzt die Einstellungen aus `.flaskenv`

### 3. `wsgi.py` angepasst

- Production-Modus wird nur noch auf Render gesetzt (wenn `RENDER` Umgebungsvariable existiert)
- Lokale Entwicklung verwendet die Einstellungen aus `.flaskenv`

### 4. `instance` Ordner sichergestellt

- Der Ordner für die SQLite-Datenbank wurde erstellt

## Verwendung

### Lokale Entwicklung (SQLite)

```bash
# Virtuelle Umgebung aktivieren
.venv\Scripts\activate

# Flask-App starten
flask run
```

Die App läuft jetzt im Development-Modus mit SQLite-Datenbank unter `instance/db.db`.

### Production auf Render (PostgreSQL)

Keine Änderungen erforderlich - die App erkennt automatisch die Render-Umgebung und verwendet PostgreSQL.

## Konfigurationen

### Development (Lokal)

- **Datenbank:** SQLite (`instance/db.db`)
- **Debug-Modus:** Aktiviert
- **FLASK_ENV:** development

### Production (Render)

- **Datenbank:** PostgreSQL (von Render bereitgestellt)
- **Debug-Modus:** Deaktiviert
- **FLASK_ENV:** production

## Vorteile

✅ Lokale Entwicklung funktioniert ohne PostgreSQL-Installation
✅ Automatische Umgebungserkennung (lokal vs. Render)
✅ Keine manuellen Konfigurationsänderungen beim Deployment
✅ SQLite-Datenbank wird automatisch erstellt
