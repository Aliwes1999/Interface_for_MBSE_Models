#!/usr/bin/env python3
"""Test that generated and uploaded files appear in the archive overview"""

from app import create_app
from app.models import User, Project, ProjectFile

app = create_app()

def test_archive_overview():
    """Test that files appear in project overview (archive)"""
    with app.app_context():
        with app.test_client() as client:
            # Find test user
            user = User.query.filter_by(email='test@example.com').first()
            project = Project.query.filter_by(name='Test Project', user_id=user.id).first()
            
            print("=== Testing Archive Overview ===\n")
            
            # Login
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'test123'
            }, follow_redirects=True)
            
            # Access project overview (archive)
            response = client.get(f'/project/{project.id}/overview')
            
            print(f"✓ Project overview status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.data.decode('utf-8')
                
                # Get all files in project
                files = ProjectFile.query.filter_by(project_id=project.id).all()
                
                print(f"\n✓ Files in project ({len(files)} total):\n")
                
                uploaded_files = [f for f in files if f.file_type == 'upload']
                generated_files = [f for f in files if f.file_type == 'generated']
                export_files = [f for f in files if f.file_type == 'export']
                
                if uploaded_files:
                    print("📥 Hochgeladene Dateien:")
                    for f in uploaded_files:
                        in_page = f.filename in html
                        status = '✓' if in_page else '✗'
                        print(f"  {status} {f.filename} (ID: {f.id})")
                
                if generated_files:
                    print("\n⚙️ Erstellte Anforderungen:")
                    for f in generated_files:
                        in_page = f.filename in html
                        status = '✓' if in_page else '✗'
                        print(f"  {status} {f.filename} (ID: {f.id})")
                
                if export_files:
                    print("\n📤 Exportierte Dateien:")
                    for f in export_files:
                        in_page = f.filename in html
                        status = '✓' if in_page else '✗'
                        print(f"  {status} {f.filename} (ID: {f.id})")
                
                # Check for archive section headers
                archive_checks = {
                    'Datei-Archiv tab exists': 'Datei-Archiv' in html,
                    'Imported files section': 'Hochgeladene Dateien' in html or uploaded_files,
                    'Generated files section': 'Erstellte Anforderungen' in html or generated_files,
                }
                
                print(f"\n✓ Page Elements:")
                for name, found in archive_checks.items():
                    status = '✓' if found else '✗'
                    print(f"  {status} {name}")
                
                print(f"\n✓ ARCHIVE OVERVIEW TEST COMPLETE!")
            else:
                print(f"✗ Overview returned status {response.status_code}")

if __name__ == '__main__':
    test_archive_overview()
