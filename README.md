# Requirements Management Tool

## Projektübersicht
Dieses Projekt ist eine einfache Flask-Webanwendung zur Verwaltung von Anforderungen (Requirements). Sie ermöglicht das Erstellen, Markieren (Status ändern) und Löschen von Anforderungen in einer benutzerfreundlichen Oberfläche. Die Anwendung nutzt Bootstrap für das Design und speichert Daten vorübergehend im Speicher (in-memory).

## Aktueller Stand
Die Anwendung ist funktionsfähig und enthält die folgenden Features:
- **Startseite**: Willkommensseite mit Navigation.
- **Anforderungen erstellen (/create)**: Formular zum Hinzufügen neuer Anforderungen (Titel, Beschreibung, Kategorie). Anzeige aller Anforderungen in einer Tabelle mit Optionen zum Markieren (Status zwischen "Offen" und "Erledigt" toggeln) und Löschen.
- **AI-Agent Seite**: Platzhalter für zukünftige AI-Integration.
- Daten werden in einer globalen Liste gespeichert (resettet bei Neustart der App). Eine SQLite-Datenbank (instance/db.db) ist vorhanden, wird aber noch nicht verwendet.
- Navigation über eine Offcanvas-Menüleiste.

Abgeschlossene Aufgaben (aus TODO.md):
- Routen für Erstellen, Markieren und Löschen implementiert.
- Template für create.html aktualisiert.
- Grundlegende Tests durchgeführt.

## Vorgehensweise
- **Architektur**: Flask-App mit Blueprint-Struktur für modulare Routen.
- **Frontend**: Jinja2-Templates mit Bootstrap 5 für responsives Design.
- **Backend**: Python mit Flask, Routen für CRUD-Operationen auf Anforderungen.
- **Datenhaltung**: Aktuell in-memory (Liste in routes.py); geplant: Migration zu SQLite-Datenbank.
- **Entwicklung**: Lokale Entwicklung mit `python main.py`, Debug-Modus aktiviert.

## Verwendete Ressourcen
- **Frameworks/Libraries**:
  - Flask 3.1.2: Webframework.
  - Flask-SQLAlchemy 3.1.1: ORM (bereitgestellt, aber noch nicht verwendet).
  - SQLAlchemy 2.0.43: Datenbank-Interaktion.
  - Bootstrap 5.3.8: CSS/JS für UI (via CDN).
  - Jinja2 3.1.6: Template-Engine.
- **Sonstige**:
  - Python 3.x
  - Werkzeug 3.1.3: WSGI-Toolkit.
  - Andere Abhängigkeiten in requirements.txt.

## Notizen
- **Datenpersistenz**: Aktuell nicht persistent; bei App-Neustart gehen Daten verloren. Empfohlen: Implementierung von Datenbank-Modellen mit SQLAlchemy.
- **Sicherheit**: Keine Authentifizierung implementiert; für Produktion erforderlich.
- **Erweiterungen**: AI-Agent-Seite ist ein Platzhalter. TODO: Integration von AI-Funktionen.
- **Tests**: Grundlegende manuelle Tests durchgeführt; automatisierte Tests (z.B. mit pytest) empfohlen.
- **Deployment**: Für Produktion: Gunicorn oder ähnliches, Umgebungsvariablen für Konfiguration.

Um die App zu starten: `python main.py` (vorausgesetzt, Abhängigkeiten installiert via `pip install -r requirements.txt`).
