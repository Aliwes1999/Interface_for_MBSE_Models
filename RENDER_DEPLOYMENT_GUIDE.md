# Render Deployment Guide

## Problembehebung

Die ursprüngliche Fehlermeldung:

```
AttributeError: module 'app' has no attribute 'app'
```

wurde durch folgende Änderungen behoben:

### 1. PostgreSQL-Treiber hinzugefügt

- `psycopg2-binary==2.9.10` zu `requirements.txt` hinzugefügt

### 2. PostgreSQL URL-Format korrigiert

- Render verwendet `postgres://` URLs
- SQLAlchemy 1.4+ benötigt `postgresql://` URLs
- `config.py` wurde aktualisiert, um automatisch zu konvertieren

### 3. WSGI-Konfiguration verbessert

- `FLASK_ENV=production` wird automatisch gesetzt
- Bessere Fehlerbehandlung für lokale Entwicklung

## Deployment-Schritte auf Render

### Schritt 1: Repository vorbereiten

Stelle sicher, dass alle Änderungen committed und gepusht sind:

```bash
git add .
git commit -m "Fix Render deployment configuration"
git push origin main
```

### Schritt 2: PostgreSQL-Datenbank erstellen

1. Gehe zu deinem Render Dashboard
2. Klicke auf "New +" → "PostgreSQL"
3. Konfiguriere die Datenbank:
   - **Name**: `mbse-interface-db` (oder ein anderer Name)
   - **Database**: `mbse_interface`
   - **User**: (wird automatisch generiert)
   - **Region**: Wähle die gleiche Region wie dein Web Service
   - **Plan**: Free (für Entwicklung)
4. Klicke auf "Create Database"
5. **Wichtig**: Kopiere die "Internal Database URL" (nicht die External URL)

### Schritt 3: Web Service erstellen/aktualisieren

1. Gehe zu deinem Web Service auf Render
2. Gehe zu "Environment" Tab
3. Füge folgende Environment Variables hinzu:

#### Erforderliche Variablen:

```
DATABASE_URL=<Internal Database URL von Schritt 2>
SECRET_KEY=<generiere einen sicheren zufälligen String>
FLASK_ENV=production
OPENAI_API_KEY=<dein OpenAI API Key>
```

#### Optionale Variablen:

```
OPENAI_MODEL=gpt-4o-mini
```

### Schritt 4: Build-Einstellungen überprüfen

Stelle sicher, dass folgende Einstellungen korrekt sind:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`
- **Branch**: `main` (oder dein Hauptbranch)

### Schritt 5: Deployment starten

1. Klicke auf "Manual Deploy" → "Deploy latest commit"
2. Oder warte auf automatisches Deployment nach dem Push

### Schritt 6: Datenbank initialisieren

Nach dem ersten erfolgreichen Deployment:

1. Öffne die Render Shell für deinen Web Service
2. Führe folgende Befehle aus:

```bash
flask db upgrade
```

Falls Migrations-Fehler auftreten:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Umgebungsvariablen generieren

### SECRET_KEY generieren

In Python:

```python
import secrets
print(secrets.token_hex(32))
```

Oder in der Shell:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Troubleshooting

### Problem: "relation does not exist" Fehler

**Lösung**: Datenbank-Migrationen ausführen

```bash
flask db upgrade
```

### Problem: "No module named 'psycopg2'"

**Lösung**: Stelle sicher, dass `psycopg2-binary` in `requirements.txt` ist und redeploy

### Problem: "Connection refused" zur Datenbank

**Lösung**:

- Verwende die **Internal Database URL**, nicht die External URL
- Stelle sicher, dass Web Service und Datenbank in der gleichen Region sind

### Problem: "Application failed to start"

**Lösung**: Überprüfe die Logs in Render Dashboard:

1. Gehe zu deinem Web Service
2. Klicke auf "Logs"
3. Suche nach spezifischen Fehlermeldungen

### Problem: Statische Dateien werden nicht geladen

**Lösung**: Flask serviert statische Dateien automatisch. Stelle sicher, dass:

- Dateien im `app/static/` Verzeichnis sind
- URLs mit `/static/` beginnen

## Wichtige Hinweise

1. **Kostenloser Plan**:

   - Web Service schläft nach 15 Minuten Inaktivität
   - Erste Anfrage nach dem Aufwachen dauert länger
   - PostgreSQL Free Plan hat 90 Tage Laufzeit

2. **Datenbank-Backups**:

   - Render erstellt automatische Backups (abhängig vom Plan)
   - Für wichtige Daten: Regelmäßige manuelle Backups erstellen

3. **Logs überwachen**:

   - Überprüfe regelmäßig die Logs auf Fehler
   - Render behält Logs für 7 Tage (Free Plan)

4. **Sicherheit**:
   - Verwende starke SECRET_KEY
   - Halte OPENAI_API_KEY geheim
   - Aktiviere HTTPS (automatisch auf Render)

## Nächste Schritte nach Deployment

1. Teste alle Funktionen der Anwendung
2. Erstelle einen Test-User und Test-Projekt
3. Überprüfe die AI-Agent-Funktionalität
4. Teste Export-Funktionen (Excel, PDF)
5. Überprüfe die Versionierung

## Support

Bei Problemen:

1. Überprüfe die Render-Logs
2. Überprüfe die Datenbank-Verbindung
3. Stelle sicher, dass alle Environment Variables gesetzt sind
4. Kontaktiere Render Support bei Plattform-spezifischen Problemen

## Erfolgreiche Deployment-Checkliste

- [ ] PostgreSQL-Datenbank erstellt
- [ ] Alle Environment Variables gesetzt
- [ ] Repository gepusht
- [ ] Deployment erfolgreich
- [ ] Datenbank-Migrationen ausgeführt
- [ ] Anwendung erreichbar
- [ ] Login funktioniert
- [ ] Projekt erstellen funktioniert
- [ ] AI-Agent funktioniert
- [ ] Export-Funktionen funktionieren
