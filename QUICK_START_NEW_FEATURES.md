# Schnellstart-Anleitung - Neue Features

**Version**: 2.0  
**Datum**: 17. November 2024

---

## 🚀 Erste Schritte

### 1. Datenbank aktualisieren

```bash
python add_is_deleted_column.py
```

✅ Erstellt Backup und fügt `is_deleted` Spalte hinzu

### 2. Anwendung starten

```bash
python main.py
```

✅ Öffnet Browser auf `http://localhost:5000`

---

## 📋 Feature-Übersicht

### 1. Dynamische Spalten verwalten

**Spalte hinzufügen:**

1. Projektseite öffnen
2. Auf "Spalte hinzufügen" klicken
3. Namen eingeben (z.B. "Priorität", "Aufwand")
4. "Hinzufügen" klicken

**Spalte löschen:**

1. X-Button auf dem Spalten-Badge klicken
2. Bestätigen
3. Spalte verschwindet aus Tabelle

💡 **Tipp**: Feste Spalten (Version, ID, Title, etc.) können nicht gelöscht werden.

---

### 2. Anforderungen bearbeiten

**Bearbeiten:**

1. In Zeile auf "Bearbeiten" klicken
2. Felder im Modal ändern:
   - Title
   - Beschreibung
   - Kategorie
   - Alle benutzerdefinierten Spalten

**Speichern:**

- **"Zwischenspeichern"**: Status → 🟡 "In Arbeit"
- **"Speichern"**: Status → 🟢 "Fertig"

💡 **Tipp**: Neue Anforderungen haben Status 🔴 "Offen"

---

### 3. Alternative Versionen mit KI generieren

**Einzelne Anforderung neu generieren:**

1. In Zeile auf "Neu generieren" klicken
2. KI erstellt alternative Version
3. Neue Version erscheint im Dropdown

**Beispiel:**

- Erste Generierung → Version A
- "Neu generieren" → Version B
- "Neu generieren" → Version C
- usw.

💡 **Tipp**: Die KI nutzt die aktuelle Version als Kontext für Verbesserungen.

---

### 4. Zwischen Versionen wechseln

**Versionswechsel:**

1. Dropdown in Version-Spalte öffnen
2. Version auswählen (A, B, C...)
3. Zeile aktualisiert sich automatisch

**Was wird aktualisiert:**

- ✅ Title
- ✅ Beschreibung
- ✅ Kategorie
- ✅ Status (mit Farbe)
- ✅ Alle benutzerdefinierten Spalten

💡 **Tipp**: Kein Neuladen der Seite erforderlich!

---

### 5. Anforderungen löschen und wiederherstellen

**Löschen:**

1. In Zeile auf "Löschen" klicken
2. Bestätigen
3. Anforderung verschwindet aus Haupttabelle

**Gelöschte anzeigen:**

1. Auf "Gelöschte Anforderungen anzeigen" klicken
2. Alle gelöschten Anforderungen werden angezeigt

**Wiederherstellen:**

1. Auf Gelöscht-Seite
2. "Wiederherstellen" klicken
3. Anforderung erscheint wieder in Haupttabelle

💡 **Tipp**: Gelöschte Anforderungen werden nicht physisch gelöscht (Soft-Delete).

---

## 🎨 Status-Ampelsystem

### Farben und Bedeutung

| Status        | Farbe   | Badge        | Bedeutung                           |
| ------------- | ------- | ------------ | ----------------------------------- |
| **Offen**     | 🔴 Rot  | `bg-danger`  | Neu, noch nicht bearbeitet          |
| **In Arbeit** | 🟡 Gelb | `bg-warning` | Zwischengespeichert, in Bearbeitung |
| **Fertig**    | 🟢 Grün | `bg-success` | Final gespeichert, abgeschlossen    |

### Status-Übergänge

```
Neue Anforderung
    ↓
🔴 Offen
    ↓ (Zwischenspeichern)
🟡 In Arbeit
    ↓ (Speichern)
🟢 Fertig
```

---

## 💡 Workflow-Beispiele

### Beispiel 1: Neues Projekt mit benutzerdefinierten Spalten

```
1. Projekt erstellen: "Smart Home System"
2. Spalten hinzufügen:
   - "Priorität"
   - "Aufwand (Stunden)"
   - "Verantwortlich"
3. KI-Agent aufrufen
4. Requirements generieren
5. Spalten mit Werten füllen (Bearbeiten)
```

### Beispiel 2: Anforderung iterativ verbessern

```
1. Anforderung "User Authentication" (Version A)
2. "Neu generieren" → Version B (verbessert)
3. Version A und B vergleichen (Dropdown)
4. Beste Version auswählen
5. Bearbeiten und finalisieren
6. Status → Fertig (grün)
```

### Beispiel 3: Anforderungen organisieren

```
1. Alle Anforderungen durchgehen
2. Unwichtige löschen
3. Wichtige bearbeiten und Status setzen:
   - Fertig → Grün
   - In Arbeit → Gelb
   - Noch offen → Rot
4. Übersicht: Ampel-Status zeigt Fortschritt
```

---

## 🔧 Tastenkombinationen & Tipps

### Browser-Tipps

- **F5**: Seite neu laden (falls nötig)
- **Strg + Shift + R**: Hard Refresh (Cache leeren)
- **F12**: Developer Tools öffnen (bei Problemen)

### Workflow-Tipps

1. **Spalten zuerst definieren**: Vor der ersten Generierung
2. **Versionen vergleichen**: Dropdown nutzen statt Historie
3. **Status konsequent setzen**: Ampelsystem für Übersicht
4. **Soft-Delete nutzen**: Nichts geht verloren
5. **KI iterativ nutzen**: Mehrfach generieren für beste Ergebnisse

---

## ⚠️ Wichtige Hinweise

### Datenbank-Backup

Vor größeren Änderungen:

```bash
copy instance\db.db instance\db.db.backup
```

### Spalten löschen

- ⚠️ Spalte löschen entfernt nur die Anzeige
- ✅ Gespeicherte Daten bleiben erhalten
- ✅ Spalte kann jederzeit wieder hinzugefügt werden

### Versionen

- ✅ Alle Versionen bleiben gespeichert
- ✅ Jede Version hat eigene custom_data
- ✅ Versionswechsel ist nicht-destruktiv

### Löschen

- ✅ Soft-Delete: Keine physische Löschung
- ✅ Alle Versionen bleiben erhalten
- ✅ Jederzeit wiederherstellbar

---

## 🐛 Troubleshooting

### Problem: Spalte erscheint nicht

**Lösung:**

1. Seite neu laden (F5)
2. Prüfen ob Spalte in "Aktuelle Spalten" angezeigt wird
3. Browser-Cache leeren

### Problem: Version-Dropdown funktioniert nicht

**Lösung:**

1. Browser-Konsole öffnen (F12)
2. JavaScript-Fehler prüfen
3. Seite neu laden
4. Bootstrap JS korrekt geladen?

### Problem: KI-Regenerierung schlägt fehl

**Lösung:**

1. API-Key in `.env` prüfen
2. Internet-Verbindung prüfen
3. Fehler-Nachricht lesen
4. Logs in Terminal prüfen

### Problem: Modal öffnet nicht

**Lösung:**

1. Bootstrap JS geladen? (base.html prüfen)
2. Browser-Konsole auf Fehler prüfen
3. Bootstrap Icons geladen?

---

## 📊 Beispiel-Workflow: Vollständiges Projekt

### Schritt 1: Projekt Setup (5 Min)

```
1. Projekt erstellen: "E-Commerce Platform"
2. Spalten hinzufügen:
   - Priorität (Hoch/Mittel/Niedrig)
   - Aufwand (1-10 Stunden)
   - Sprint (1, 2, 3...)
   - Verantwortlich (Name)
```

### Schritt 2: Initiale Requirements (10 Min)

```
1. KI-Agent öffnen
2. Beschreibung eingeben:
   "E-Commerce platform with user management,
    product catalog, shopping cart, and payment"
3. Generieren → 10-15 Requirements (Version A)
```

### Schritt 3: Requirements verfeinern (20 Min)

```
Für jede Anforderung:
1. Bearbeiten öffnen
2. Priorität setzen
3. Aufwand schätzen
4. Sprint zuweisen
5. Verantwortlichen eintragen
6. Zwischenspeichern (Status → Gelb)
```

### Schritt 4: Kritische Requirements verbessern (15 Min)

```
Für wichtige Requirements:
1. "Neu generieren" klicken
2. Version A und B vergleichen
3. Beste Version auswählen
4. Final bearbeiten
5. Speichern (Status → Grün)
```

### Schritt 5: Aufräumen (5 Min)

```
1. Unwichtige Requirements löschen
2. Duplikate entfernen
3. Finale Übersicht:
   - Grün: Fertig definiert
   - Gelb: In Bearbeitung
   - Rot: Noch zu bearbeiten
```

**Gesamt: ~55 Minuten für vollständiges Projekt-Setup**

---

## 📈 Best Practices

### 1. Spalten-Management

✅ **DO:**

- Spalten vor erster Generierung definieren
- Konsistente Namensgebung
- Nur benötigte Spalten hinzufügen

❌ **DON'T:**

- Zu viele Spalten (max. 5-7)
- Spalten mit sehr langen Namen
- Feste Spalten löschen versuchen

### 2. Versionierung

✅ **DO:**

- Mehrere Versionen für kritische Requirements
- Versionen vergleichen vor Finalisierung
- Alte Versionen als Referenz behalten

❌ **DON'T:**

- Zu viele Versionen (max. 3-4)
- Versionen ohne Vergleich löschen
- Erste Version überschreiben

### 3. Status-Management

✅ **DO:**

- Status konsequent setzen
- Ampelsystem für Übersicht nutzen
- Regelmäßig Status aktualisieren

❌ **DON'T:**

- Status ignorieren
- Alle auf "Offen" lassen
- Status ohne Grund ändern

### 4. KI-Nutzung

✅ **DO:**

- Kontext in Beschreibung geben
- Mehrfach generieren für Alternativen
- Ergebnisse nachbearbeiten

❌ **DON'T:**

- Blind KI-Ergebnisse übernehmen
- Ohne Kontext generieren
- Zu oft regenerieren (Kosten!)

---

## 🎯 Zusammenfassung

### Neue Features im Überblick

| Feature                      | Beschreibung                     | Nutzen                 |
| ---------------------------- | -------------------------------- | ---------------------- |
| **Spalten löschen**          | X-Button auf Badges              | Flexible Anpassung     |
| **KI-Regenerierung**         | Einzelne Requirements verbessern | Iterative Verfeinerung |
| **Vollständiges Bearbeiten** | Alle Felder editierbar           | Komplette Kontrolle    |
| **Status-Ampel**             | Rot/Gelb/Grün System             | Visueller Fortschritt  |
| **Soft-Delete**              | Papierkorb-Funktion              | Sicherheit             |
| **Versionswechsel**          | Dropdown ohne Reload             | Schneller Vergleich    |

### Nächste Schritte

1. ✅ Datenbank aktualisieren
2. ✅ Anwendung starten
3. ✅ Projekt erstellen
4. ✅ Spalten definieren
5. ✅ Requirements generieren
6. ✅ Features ausprobieren!

---

**Viel Erfolg mit dem Requirements Management Tool! 🚀**

Bei Fragen oder Problemen: Siehe Troubleshooting-Sektion oder COMPLETE_FEATURES_IMPLEMENTATION.md

---

**Letzte Aktualisierung**: 17. November 2024  
**Version**: 2.0
