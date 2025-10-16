# TODO for Implementing Three Independent Tables for Requirements Management

- [ ] Update app/routes.py: Change data structure to have 'created', 'intermediate', 'saved', 'deleted' lists instead of 'requirements'.
- [ ] Update app/templates/create.html: Add tabs for three tables (Erstellt, Zwischengespeichert, Gespeichert), each with specific actions menu.
- [ ] Add new routes in app/routes.py: For moving requirements between tables (save, intermediate, delete), edit modal/form, export to Excel/PDF.
- [ ] Update requirements.txt: Add openpyxl and reportlab for export functionality.
- [ ] Test the app: Create projects, add requirements, move between tables, edit, export.
