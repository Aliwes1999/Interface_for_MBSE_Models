#!/usr/bin/env python3
"""Test script to verify that file_view page renders correctly"""

from app import create_app
from app.models import User, Project, ProjectFile

app = create_app()

def test_file_view_render():
    """Test that file_view page renders correctly"""
    with app.app_context():
        with app.test_client() as client:
            # Find test user
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                print("✗ Test user not found")
                return
            
            # Find test project
            project = Project.query.filter_by(name='Test Project', user_id=user.id).first()
            if not project:
                print("✗ Test project not found")
                return
            
            # Find test file
            file = ProjectFile.query.filter_by(project_id=project.id).first()
            if not file:
                print("✗ No test files found")
                return
            
            print(f"✓ Test file found: {file.filename} (Type: {file.file_type}, ID: {file.id})")
            
            # Login first
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'test123'
            }, follow_redirects=True)
            
            print(f"✓ Login response status: {response.status_code}")
            
            # Now access the file_view page
            response = client.get(f'/project/{project.id}/file/{file.id}')
            
            print(f"\nFile view page response status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.data.decode('utf-8')
                
                # Check for key elements
                checks = [
                    ('File title', f'Datei: {file.filename}' in html),
                    ('Back button', 'Zurück zum Überblick' in html),
                    ('File type badge', 'badge' in html),
                    ('Erkannte Spalten', 'Spalten' in html or 'Vorschau' in html),
                    ('Download button', 'Herunterladen' in html),
                ]
                
                print(f"\n✓ Page rendered successfully. Checking elements:")
                for check_name, check_result in checks:
                    status = '✓' if check_result else '✗'
                    print(f"  {status} {check_name}")
            else:
                print(f"✗ File view page returned status {response.status_code}")
                print(f"Response: {response.data[:200]}")

if __name__ == '__main__':
    test_file_view_render()
