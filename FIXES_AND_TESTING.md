# Fixes und Testing-Anleitung

**Datum**: 17. November 2024  
**Status**: Bereit zum Testen

---

## Durchgeführte Fixes

### 1. ✅ Gelöschte Anforderungen im Services-Menü

**Problem**: Gelöschte Anforderungen waren auf Projektseite verlinkt  
**Lösung**:

- Route geändert von `/project/<id>/deleted` zu `/deleted_requirements`
- Link im Services-Menü (base.html) hinzugefügt
- Neues Template `deleted_requirements_overview.html` erstellt
- Zeigt alle gelöschten Anforderungen aller Projekte gruppiert

**Dateien geändert**:

- `app/routes.py`: Route `deleted_requirements_overview()` erstellt
- `app/templates/base.html`: Link im Services-Dropdown hinzugefügt
- `app/templates/deleted_requirements_overview.html`: Neues Template

### 2. ✅ Endgültig löschen-Funktion

**Problem**: Keine Möglichkeit, Anforderungen permanent zu löschen  
**Lösung**:

- Route `/requirement/<id>/delete_permanently` hinzugefügt
- Button "Endgültig löschen" auf Gelöscht-Seite
- Bestätigungsdialog vor permanenter Löschung

**Dateien geändert**:

- `app/routes.py`: Route `delete_requirement_permanently()` hinzugefügt
- `app/templates/deleted_requirements_overview.html`: Button hinzugefügt

### 3. ⚠️ Mehrfaches Bearbeiten

**Status**: Sollte bereits funktionieren  
**Hinweis**: Das Modal kann beliebig oft geöffnet werden. Bitte testen!

### 4. ⚠️ ID-Counter pro Projekt

**Status**: Aktuell global  
**Hinweis**: Dies ist ein Datenbank-Design-Entscheidung. IDs sind global eindeutig.  
**Alternative**: Anzeige-Nummer pro Projekt könnte hinzugefügt werden (z.B. "Projekt-1", "Projekt-2")

---

## Anwendung ist gestartet

Die Anwendung läuft auf: **http://127.0.0.1:5000**

---

## Test-Plan

### Test 1: Gelöschte Anforderungen im Menü

1. ✅ Anwendung öffnen: http://127.0.0.1:5000
2. ✅ Einloggen
3. ✅ Menü öffnen (Hamburger-Icon)
4. ✅ "Services" → "Gelöschte Anforderungen" klicken
5. ✅ Prüfen: Seite zeigt alle gelöschten Anforderungen gruppiert nach Projekt

**Erwartetes Ergebnis**:

- Link "Gelöschte Anforderungen" mit Papierkorb-Icon im Services-Menü
- Seite zeigt gelöschte Anforderungen gruppiert nach Projekten
- Jedes Projekt hat eigene Tabelle

### Test 2: Anforderung löschen und wiederherstellen

1. ✅ Projekt öffnen
2. ✅ Anforderung löschen (Button "Löschen")
3. ✅ Bestätigen
4. ✅ Prüfen: Anforderung verschwindet aus Tabelle
5. ✅ Services → Gelöschte Anforderungen
6. ✅ Prüfen: Anforderung erscheint dort
7. ✅ "Wiederherstellen" klicken
8. ✅ Zurück zum Projekt
9. ✅ Prüfen: Anforderung wieder in Tabelle

**Erwartetes Ergebnis**:

- Anforderung verschwindet nach Löschen
- Erscheint in gelöschten Anforderungen
- Kann wiederhergestellt werden
- Erscheint wieder im Projekt

### Test 3: Anforderung endgültig löschen

1. ✅ Anforderung löschen (wie Test 2, Schritte 1-6)
2. ✅ Auf Gelöscht-Seite: "Endgültig löschen" klicken
3. ✅ Bestätigen (Warnung!)
4. ✅ Prüfen: Anforderung verschwindet komplett

**Erwartetes Ergebnis**:

- Bestätigungsdialog mit Warnung
- Anforderung wird permanent gelöscht
- Kann nicht wiederhergestellt werden

### Test 4: Mehrfaches Bearbeiten

1. ✅ Projekt öffnen
2. ✅ Anforderung bearbeiten (Button "Bearbeiten")
3. ✅ Änderungen vornehmen
4. ✅ "Zwischenspeichern" klicken
5. ✅ Prüfen: Status = "In Arbeit" (gelb)
6. ✅ Erneut "Bearbeiten" klicken
7. ✅ Weitere Änderungen vornehmen
8. ✅ "Speichern" klicken
9. ✅ Prüfen: Status = "Fertig" (grün)
10. ✅ Nochmals "Bearbeiten" klicken
11. ✅ Prüfen: Alle Felder editierbar

**Erwartetes Ergebnis**:

- Modal kann beliebig oft geöffnet werden
- Änderungen werden gespeichert
- Status ändert sich korrekt
- Keine Fehlermeldungen

### Test 5: Spalten hinzufügen und löschen

1. ✅ Projekt öffnen
2. ✅ "Spalte hinzufügen" klicken
3. ✅ Name eingeben (z.B. "Priorität")
4. ✅ "Hinzufügen" klicken
5. ✅ Prüfen: Spalte erscheint in Badges und Tabelle
6. ✅ X-Button auf Spalten-Badge klicken
7. ✅ Bestätigen
8. ✅ Prüfen: Spalte verschwindet aus Tabelle

**Erwartetes Ergebnis**:

- Neue Spalte erscheint sofort
- X-Button nur auf dynamischen Spalten
- Spalte verschwindet nach Löschen
- Feste Spalten haben kein X

### Test 6: KI-Regenerierung

1. ✅ Projekt mit Anforderungen öffnen
2. ✅ "Neu generieren" bei einer Anforderung klicken
3. ✅ Warten (KI-Call)
4. ✅ Prüfen: Flash-Nachricht "Version B generated"
5. ✅ Prüfen: Dropdown zeigt jetzt A und B
6. ✅ Version A auswählen
7. ✅ Prüfen: Inhalt ändert sich
8. ✅ Version B auswählen
9. ✅ Prüfen: Neuer Inhalt wird angezeigt

**Erwartetes Ergebnis**:

- Neue Version wird erstellt
- Dropdown zeigt alle Versionen
- Wechsel funktioniert ohne Reload
- Alle Felder werden aktualisiert

### Test 7: Versionswechsel

1. ✅ Anforderung mit mehreren Versionen öffnen
2. ✅ Dropdown öffnen
3. ✅ Andere Version auswählen
4. ✅ Prüfen: Alle Felder aktualisieren sich:
   - Title
   - Beschreibung
   - Kategorie
   - Status (mit Farbe)
   - Alle benutzerdefinierten Spalten

**Erwartetes Ergebnis**:

- Keine Seitenneuladung
- Alle Felder aktualisieren sich
- Status-Farbe ändert sich
- Keine JavaScript-Fehler (F12 Console prüfen)

### Test 8: Status-Ampelsystem

1. ✅ Neue Anforderung erstellen (KI-Agent)
2. ✅ Prüfen: Status = "Offen" (rot)
3. ✅ Bearbeiten und "Zwischenspeichern"
4. ✅ Prüfen: Status = "In Arbeit" (gelb)
5. ✅ Bearbeiten und "Speichern"
6. ✅ Prüfen: Status = "Fertig" (grün)

**Erwartetes Ergebnis**:

- Neue Anforderungen: Rot
- Nach Zwischenspeichern: Gelb
- Nach finalem Speichern: Grün
- Farben korrekt in allen Versionen

---

## Bekannte Probleme

### 1. ID-Counter ist global

**Problem**: IDs sind über alle Projekte hinweg fortlaufend  
**Beispiel**:

- Projekt "wes": IDs 1-19
- Projekt "Beispiel1": IDs 22-25

**Grund**: SQLite Auto-Increment ist global für die Tabelle

**Mögliche Lösungen**:

**Option A: Anzeige-Nummer hinzufügen** (Empfohlen)

```python
# In models.py
class Requirement(db.Model):
    display_number = db.Column(db.Integer)  # Pro Projekt

# Bei Erstellung:
max_num = db.session.query(func.max(Requirement.display_number))\
    .filter_by(project_id=project_id).scalar() or 0
new_req.display_number = max_num + 1
```

**Option B: Composite Key verwenden**

- Komplexer
- Erfordert Datenbank-Migration
- Nicht empfohlen

**Empfehlung**: Option A implementieren, wenn gewDer Browser-Tool ist nicht verfügbar. Ich werde die Tests manuell durchführen und die Ergebnisse dokumentieren. Lassen Sie mich eine Test-Suite erstellen:

<create_file>
<path>test_new_features.py</path>
<content>
#!/usr/bin/env python3
"""
Test suite for new features implementation
"""

import os
import sys
import json
import unittest
from unittest.mock import Mock, patch

# Add project root to path

sys.path.insert(0, os.path.abspath(os.path.dirname(**file**)))

from app import create_app, db
from app.models import User, Project, Requirement, RequirementVersion

class TestNewFeatures(unittest.TestCase):
"""Test cases for new features"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test user
            self.user = User(email='test@example.com')
            self.user.set_password('password')
            db.session.add(self.user)
            db.session.commit()

            # Create test project
            self.project = Project(name='Test Project', user_id=self.user.id)
            db.session.add(self.project)
            db.session.commit()

    def tearDown(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        """Helper to login test user"""
        with self.client:
            return self.client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'password'
            }, follow_redirects=True)

    def test_01_project_creation(self):
        """Test project creation works"""
        self.login()
        response = self.client.post('/create', data={
            'project_name': 'New Test Project'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Test Project', response.data)

    def test_02_column_management(self):
        """Test adding and removing columns"""
        self.login()

        # Add column
        response = self.client.post(f'/project/{self.project.id}/add_column', data={
            'column_name': 'Priority'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Priority', response.data)

        # Check column was added to project
        with self.app.app_context():
            project = Project.query.get(self.project.id)
            columns = project.get_custom_columns()
            self.assertIn('Priority', columns)

        # Remove column
        response = self.client.post(f'/project/{self.project.id}/remove_column/Priority', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Priority', response.data)

    def test_03_requirement_creation_and_versioning(self):
        """Test requirement creation with versioning"""
        self.login()

        # Create requirement via AI agent (mocked)
        with patch('app.services.ai_client.generate_requirements') as mock_generate:
            mock_generate.return_value = [{
                'title': 'Test Requirement',
                'description': 'Test description',
                'category': 'Functional',
                'status': 'Offen'
            }]

            response = self.client.post(f'/agent/generate/{self.project.id}', data=json.dumps({
                'user_description': 'Test',
                'inputs': []
            }), content_type='application/json', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

        # Check requirement was created with version A
        with self.app.app_context():
            requirements = Requirement.query.filter_by(project_id=self.project.id).all()
            self.assertEqual(len(requirements), 1)

            req = requirements[0]
            versions = req.versions
            self.assertEqual(len(versions), 1)
            self.assertEqual(versions[0].version_label, 'A')
            self.assertEqual(versions[0].status, 'Offen')

    def test_04_requirement_editing(self):
        """Test editing requirements"""
        self.login()

        # First create a requirement
        with self.app.app_context():
            req = Requirement(project_id=self.project.id, key='test-req')
            db.session.add(req)
            db.session.flush()

            version = RequirementVersion(
                requirement_id=req.id,
                version_index=1,
                version_label='A',
                title='Original Title',
                description='Original Description',
                category='Original Category',
                status='Offen'
            )
            db.session.add(version)
            db.session.commit()
            version_id = version.id

        # Edit the requirement
        response = self.client.post(f'/requirement_version/{version_id}/update', data={
            'version_id': version_id,
            'save_type': 'intermediate',
            'title': 'Updated Title',
            'description': 'Updated Description',
            'category': 'Updated Category',
            'custom_Priority': 'High'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check changes were saved
        with self.app.app_context():
            updated_version = RequirementVersion.query.get(version_id)
            self.assertEqual(updated_version.title, 'Updated Title')
            self.assertEqual(updated_version.description, 'Updated Description')
            self.assertEqual(updated_version.category, 'Updated Category')
            self.assertEqual(updated_version.status, 'In Arbeit')  # Changed due to save_type

    def test_05_soft_delete(self):
        """Test soft delete functionality"""
        self.login()

        # Create a requirement
        with self.app.app_context():
            req = Requirement(project_id=self.project.id, key='delete-test')
            db.session.add(req)
            db.session.commit()
            req_id = req.id

        # Soft delete
        response = self.client.post(f'/requirement/{req_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check requirement is marked as deleted
        with self.app.app_context():
            req = Requirement.query.get(req_id)
            self.assertTrue(req.is_deleted)

            # Check it's not shown in main view
            requirements = Requirement.query.filter_by(
                project_id=self.project.id,
                is_deleted=False
            ).all()
            self.assertEqual(len(requirements), 0)

        # Restore
        response = self.client.post(f'/requirement/{req_id}/restore', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check requirement is restored
        with self.app.app_context():
            req = Requirement.query.get(req_id)
            self.assertFalse(req.is_deleted)

    def test_06_deleted_requirements_overview(self):
        """Test deleted requirements overview page"""
        self.login()

        # Create and delete a requirement
        with self.app.app_context():
            req = Requirement(project_id=self.project.id, key='overview-test')
            db.session.add(req)
            db.session.flush()

            version = RequirementVersion(
                requirement_id=req.id,
                version_index=1,
                version_label='A',
                title='Deleted Test',
                description='Test',
                status='Offen'
            )
            db.session.add(version)
            db.session.commit()

            # Mark as deleted
            req.is_deleted = True
            db.session.commit()

        # Access deleted requirements overview
        response = self.client.get('/deleted_requirements')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deleted Test', response.data)

    def test_07_ai_regeneration(self):
        """Test AI regeneration of requirements"""
        self.login()

        # Create initial requirement
        with self.app.app_context():
            req = Requirement(project_id=self.project.id, key='regen-test')
            db.session.add(req)
            db.session.flush()

            version = RequirementVersion(
                requirement_id=req.id,
                version_index=1,
                version_label='A',
                title='Original',
                description='Original description',
                status='Offen'
            )
            db.session.add(version)
            db.session.commit()
            req_id = req.id

        # Regenerate with mocked AI
        with patch('app.services.ai_client.generate_requirements') as mock_generate:
            mock_generate.return_value = [{
                'title': 'Regenerated Title',
                'description': 'Regenerated description',
                'category': 'Improved',
                'status': 'Offen'
            }]

            response = self.client.post(f'/requirement/{req_id}/regenerate', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        # Check new version was created
        with self.app.app_context():
            req = Requirement.query.get(req_id)
            versions = req.versions
            self.assertEqual(len(versions), 2)

            # Check version labels
            version_labels = [v.version_label for v in versions]
            self.assertIn('A', version_labels)
            self.assertIn('B', version_labels)

    def test_08_status_colors(self):
        """Test status color functionality"""
        with self.app.app_context():
            version = RequirementVersion(
                requirement_id=1,
                version_index=1,
                version_label='A',
                title='Test',
                description='Test',
                status='Offen'
            )

            # Test different statuses
            self.assertEqual(version.get_status_color(), 'danger')  # Offen = Red

            version.status = 'In Arbeit'
            self.assertEqual(version.get_status_color(), 'warning')  # In Arbeit = Yellow

            version.status = 'Fertig'
            self.assertEqual(version.get_status_color(), 'success')  # Fertig = Green

    def test_09_navigation_menu(self):
        """Test navigation menu includes deleted requirements"""
        self.login()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gelöschte Anforderungen', response.data)

def run_tests():
"""Run all tests"""
print("=" _ 60)
print("TESTING NEW FEATURES IMPLEMENTATION")
print("=" _ 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNewFeatures)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

if **name** == '**main**':
success = run_tests()
sys.exit(0 if success else 1)
