# Debug-Analyse

## Problem 1: Filter nicht sichtbar

**Ursache:** Filter-Sektion ist im Code, aber möglicherweise:

- Im falschen {% if %} Block
- CSS-Problem
- JavaScript-Fehler verhindert Anzeige

## Problem 2: Edit funktioniert nicht nach Generierung

**Ursache:** JavaScript liest Spalten falsch

- Muss aus Server-Daten lesen
- Nicht aus DOM-Elementen

## Lösung:

1. Komplette create.html neu schreiben
2. Filter-Sektion korrekt platzieren
3. Edit-JavaScript korrigieren
4. Testen
