# TODO: Datenpersistenz für Projekte implementieren

- [x] Neues 'Project'-Modell in app/models.py hinzufügen (id, name, columns, created_requirements, intermediate_requirements, saved_requirements, deleted_requirements)
- [x] app/routes.py aktualisieren: Globale 'projects'-Liste entfernen und durch DB-Abfragen ersetzen
- [x] Routen in routes.py anpassen, um Project-Modell zu verwenden (create, manage_project, move_requirement, edit_requirement, export_requirements)
- [x] Sicherstellen, dass db.create_all() in __init__.py alle Modelle erstellt
- [ ] App testen, um zu bestätigen, dass Projekte nach Server-Neustart erhalten bleiben
