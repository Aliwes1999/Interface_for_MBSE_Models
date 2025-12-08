#!/usr/bin/env python3
"""Test the generation-only flow (no upload)"""

import os
os.environ['OPENAI_API_KEY'] = 'test-key'

from app import create_app
from app.models import User, Project, ProjectFile
from unittest.mock import patch

app = create_app()

def mock_generate_requirements(*args, **kwargs):
    """Mock the AI requirement generation"""
    return [
        {
            'title': 'Generated Req 1',
            'description': 'Auto-generated requirement',
            'category': 'Functional'
        },
        {
            'title': 'Generated Req 2',
            'description': 'Another auto-generated requirement',
            'category': 'Non-Functional'
        }
    ]

def test_generation_only():
    """Test generation-only flow (no file upload)"""
    with app.app_context():
        with app.test_client() as client:
            # Find test user
            user = User.query.filter_by(email='test@example.com').first()
            project = Project.query.filter_by(name='Test Project', user_id=user.id).first()
            
            print("=== STEP 1: Login ===")
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'test123'
            }, follow_redirects=True)
            print(f"✓ Login status: {response.status_code}")
            
            print("\n=== STEP 2: Generate Requirements (No Upload) ===")
            
            with patch('app.agent.generate_requirements', side_effect=mock_generate_requirements):
                response = client.post(
                    f'/agent/generate/{project.id}',
                    data={
                        'user_description': 'Generate from scratch',
                        'inputs': '[]'
                        # Note: NO excel_file uploaded
                    }
                )
            
            print(f"✓ Generation status: {response.status_code}")
            data = response.get_json()
            print(f"✓ Generated {data.get('count')} requirements")
            
            # Extract file ID from redirect
            redirect_url = data.get('redirect', '')
            if '/file/' in redirect_url:
                file_id = int(redirect_url.split('/file/')[-1])
                print(f"✓ Redirecting to generated file ID: {file_id}")
                
                # Check the file type
                file_obj = ProjectFile.query.get(file_id)
                print(f"  - File: {file_obj.filename}")
                print(f"  - Type: {file_obj.file_type}")
                
                if file_obj.file_type == 'generated':
                    print(f"  - ✓ Correctly marked as 'generated'")
                else:
                    print(f"  - ✗ Wrong file type: {file_obj.file_type}")
            else:
                print(f"✗ No file ID in redirect: {redirect_url}")
                return
            
            print("\n=== STEP 3: View Generated File Details ===")
            response = client.get(f'/project/{project.id}/file/{file_id}')
            print(f"✓ File view status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.data.decode('utf-8')
                
                # Check for generated file badge
                if 'Erstellte Anforderungen' in html:
                    print(f"✓ Correctly shows 'Erstellte Anforderungen' badge")
                else:
                    print(f"✗ Badge not found in page")
                
                print(f"\n✓ GENERATION-ONLY TEST COMPLETE!")
            else:
                print(f"✗ File view returned status {response.status_code}")

if __name__ == '__main__':
    test_generation_only()
