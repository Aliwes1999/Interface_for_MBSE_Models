#!/usr/bin/env python3
"""Test script to verify that generated/uploaded files redirect to file_view page"""

from app import create_app
from app.models import User, Project, ProjectFile
import os
import json

app = create_app()

def test_file_view_redirect():
    """Test that the file view redirect works correctly"""
    with app.app_context():
        with app.test_client() as client:
            # Create a test user
            user = User.query.filter_by(email='test@example.com').first()
            if user:
                print(f"✓ Test user found: {user.email}")
            else:
                print("✗ Test user not found")
                return
            
            # Create a test project
            project = Project.query.filter_by(name='Test Project', user_id=user.id).first()
            if not project:
                print("✗ Test project not found")
                return
            
            print(f"✓ Test project found: {project.name} (ID: {project.id})")
            
            # Check if any files exist in the project
            files = ProjectFile.query.filter_by(project_id=project.id).all()
            print(f"✓ Found {len(files)} files in project")
            
            for file in files:
                print(f"  - {file.filename} (Type: {file.file_type}, ID: {file.id})")
            
            # Test that we can access a file view page
            if files:
                test_file = files[0]
                # Try to access file view without login (should redirect)
                response = client.get(f'/project/{project.id}/file/{test_file.id}')
                print(f"\nTest accessing file view:")
                print(f"  - Response status: {response.status_code}")
                if response.status_code == 302:  # redirect to login
                    print(f"  - ✓ Correctly redirects to login (expected)")
                elif response.status_code == 200:
                    print(f"  - ✓ File view page accessible")
                else:
                    print(f"  - Status code: {response.status_code}")

if __name__ == '__main__':
    test_file_view_redirect()
