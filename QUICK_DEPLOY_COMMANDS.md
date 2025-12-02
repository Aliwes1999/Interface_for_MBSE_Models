# Schnelle Deployment-Befehle für Render

## 1. Code committen und pushen

```bash
git add .
git commit -m "Fix Render deployment: Add PostgreSQL support and fix URL format"
git push origin main
```

## 2. SECRET_KEY generieren

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Kopiere den Output und verwende ihn als SECRET_KEY in Render.

## 3. Render Environment Variables (im Dashboard setzen)

Gehe zu: **Dashboard → Dein Web Service → Environment**

Füge hinzu:

```
DATABASE_URL = <Internal Database URL von deiner PostgreSQL-Instanz>
SECRET_KEY = <generierter Key aus Schritt 2>
FLASK_ENV = production
OPENAI_API_KEY = <dein OpenAI API Key>
OPENAI_MODEL = gpt-4o-mini
```

## 4. Nach erfolgreichem Deployment: Datenbank initialisieren

Öffne die Render Shell (Dashboard → Dein Web Service → Shell) und führe aus:

```bash
flask db upgrade
```

Falls Fehler auftreten:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 5. Testen

Öffne deine Render-URL und teste:

- [ ] Registrierung
- [ ] Login
- [ ] Projekt erstellen
- [ ] AI-Agent verwenden
- [ ] Export-Funktionen

## Wichtige URLs

- **Render Dashboard**: https://dashboard.render.com
- **PostgreSQL Dashboard**: Dashboard → Databases → Deine DB
- **Web Service Logs**: Dashboard → Dein Service → Logs
- **Shell Access**: Dashboard → Dein Service → Shell

## Bei Problemen

1. **Logs überprüfen**: Dashboard → Logs
2. **Environment Variables überprüfen**: Dashboard → Environment
3. **PostgreSQL Status überprüfen**: Dashboard → Databases
4. **Siehe**: RENDER_DEPLOYMENT_GUIDE.md für detaillierte Hilfe

## Checkliste vor Deployment

- [ ] PostgreSQL-Datenbank auf Render erstellt
- [ ] Internal Database URL kopiert
- [ ] SECRET_KEY generiert
- [ ] OPENAI_API_KEY bereit
- [ ] Alle Environment Variables in Render gesetzt
- [ ] Code committed und gepusht
- [ ] Deployment gestartet

## Nach erfolgreichem Deployment

- [ ] Datenbank-Migrationen ausgeführt
- [ ] Test-User erstellt
- [ ] Test-Projekt erstellt
- [ ] AI-Agent getestet
- [ ] Export-Funktionen getestet

🎉 **Fertig!**
