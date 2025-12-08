# Archive

Dieses Verzeichnis enthält alte Skripte und Dateien, die nicht mehr aktiv verwendet werden, aber für Referenzzwecke aufbewahrt werden.

## Struktur

- **migrations/**: Alte Datenbankmigrationssk ripte
  - `add_*.py`: Skripte zum Hinzufügen von Spalten
  - `fix_*.py`: Skripte zur Behebung von Datenbankproblemen
  - `migrate_*.py`: Migrationssk ripte
  - `database_migration.py`: Allgemeine Migrationsskripte
  - `complete_database_reset.py`: Datenbank-Reset-Skript
  - `remove_old_columns.py`: Skript zum Entfernen alter Spalten
  - `update_database_schema.py`: Schema-Update-Skript

- **tests/**: Test-Dateien aus der Entwicklungsphase
  - `test_*.py`: Verschiedene Testskripte
  - `create_test_*.py`: Skripte zum Erstellen von Testdaten

- **debug/**: Debug-Hilfsskripte
  - `debug_*.py`: Debug-Skripte
  - `list_project_files.py`: Dateiauflistungsskript

## Hinweis

Diese Dateien werden **nicht** mehr aktiv gewartet oder verwendet. Sie wurden archiviert, um:
- Die Projektstruktur sauber zu halten
- Historische Referenz zu bewahren
- Bei Bedarf auf alte Implementierungen zurückgreifen zu können

**Verwenden Sie diese Skripte nicht in der Produktion!**
