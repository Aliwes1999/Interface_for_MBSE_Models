# Implementation Plan - Neue Features

## Status: ✅ Basis-Versionierung funktioniert

## Zu implementierende Features:

### 1. Dynamische Spalten pro Projekt

- [ ] Project-Modell: JSON-Feld für Spaltenkonfiguration hinzufügen
- [ ] Route zum Hinzufügen neuer Spalten
- [ ] Route zum Löschen von Spalten
- [ ] UI: "Aktuelle Spalten" Bereich mit Chips/Badges
- [ ] UI: Formular zum Hinzufügen neuer Spalten
- [ ] RequirementVersion: JSON-Feld für dynamische Spaltenwerte
- [ ] Tabelle: Dynamische Spalten zwischen Beschreibung und Kategorie anzeigen

### 2. Versionswechsel in der Tabelle

- [ ] Query: Alle Versionen pro Requirement laden (nicht nur neueste)
- [ ] UI: Dropdown/Buttons für Versionswahl (A/B/C)
- [ ] JavaScript: Beim Wechsel Zeile aktualisieren (ohne Reload)
- [ ] Alle Versionen als data-attributes im DOM speichern

### 3. Ampelsystem für Status

- [ ] Status-Werte definieren: "Offen" (Rot), "In Arbeit" (Gelb), "Fertig" (Grün)
- [ ] UI: Farbige Badges in Status-Spalte
- [ ] Routes: Status-Update-Aktionen
- [ ] UI: Buttons/Dropdown zum Statuswechsel

### 4. Aktionen-Spalte wiederherstellen

- [ ] Historie Button (bereits vorhanden)
- [ ] Status-Wechsel Buttons
- [ ] Bearbeiten Button (für aktuelle Version)
- [ ] Löschen Button (für gesamtes Requirement)

### 5. Tests

- [ ] Dynamische Spalten hinzufügen/löschen
- [ ] Mehrfache KI-Generierung (A → B → C)
- [ ] Versionswechsel in UI
- [ ] Ampelsystem testen
- [ ] Alle Aktionen testen

## Reihenfolge:

1. **Models erweitern** (Project + RequirementVersion)
2. **Routes für dynamische Spalten**
3. **Routes für Status-Updates**
4. **UI: Projektseite komplett überarbeiten**
5. **JavaScript für Versionswechsel**
6. **CSS für Ampelsystem**
7. **Tests durchführen**
