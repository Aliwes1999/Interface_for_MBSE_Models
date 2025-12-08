"""
Vollständiger Funktionstest für die Flask-Anwendung
Testet alle kritischen Endpoints und Funktionen
"""
import os
import sys
import requests
import json
from time import sleep

# Set development environment
os.environ['FLASK_ENV'] = 'development'

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5000"

# Test results
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(test_name, status, message=""):
    status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
    print(f"{status_symbol} {test_name}: {message}")
    
    if status == "PASS":
        test_results["passed"].append(test_name)
    elif status == "FAIL":
        test_results["failed"].append(test_name)
    else:
        test_results["warnings"].append(test_name)

def test_server_running():
    """Test if the Flask server is running"""
    print_header("1. SERVER CONNECTIVITY TEST")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code in [200, 302, 401]:  # 302 for redirect, 401 for auth required
            print_test("Server Running", "PASS", f"Server responded with status {response.status_code}")
            return True
        else:
            print_test("Server Running", "FAIL", f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("Server Running", "FAIL", "Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print_test("Server Running", "FAIL", f"Error: {str(e)}")
        return False

def test_static_resources():
    """Test if static resources are accessible"""
    print_header("2. STATIC RESOURCES TEST")
    
    static_files = [
        "/static/style.css",
        "/static/bootstrap.min.css",
        "/static/bootstrap.bundle.min.js",
        "/static/project.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(BASE_URL + file_path, timeout=5)
            if response.status_code == 200:
                print_test(f"Static file: {file_path}", "PASS", "Accessible")
            else:
                print_test(f"Static file: {file_path}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Static file: {file_path}", "FAIL", str(e))

def test_main_routes():
    """Test main application routes"""
    print_header("3. MAIN ROUTES TEST")
    
    routes = [
        ("/", "Home/Start Page"),
        ("/auth/login", "Login Page"),
        ("/auth/register", "Register Page"),
    ]
    
    for route, description in routes:
        try:
            response = requests.get(BASE_URL + route, timeout=5, allow_redirects=False)
            if response.status_code in [200, 302]:
                print_test(f"{description} ({route})", "PASS", f"Status: {response.status_code}")
            else:
                print_test(f"{description} ({route})", "WARN", f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"{description} ({route})", "FAIL", str(e))

def test_database_connection():
    """Test database connectivity"""
    print_header("4. DATABASE CONNECTION TEST")
    
    from app import create_app, db
    from app.models import User, Project, Requirement
    
    try:
        app = create_app()
        with app.app_context():
            # Try to query the database
            user_count = User.query.count()
            project_count = Project.query.count()
            requirement_count = Requirement.query.count()
            
            print_test("Database Connection", "PASS", "Successfully connected to database")
            print(f"  - Users: {user_count}")
            print(f"  - Projects: {project_count}")
            print(f"  - Requirements: {requirement_count}")
            
            # Check if tables exist
            tables = db.engine.table_names()
            print(f"  - Tables found: {len(tables)}")
            for table in tables:
                print(f"    • {table}")
            
            return True
    except Exception as e:
        print_test("Database Connection", "FAIL", str(e))
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print_header("5. USER REGISTRATION TEST")
    
    test_user = {
        "username": f"testuser_{int(sleep(0) or 1)}",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            BASE_URL + "/auth/register",
            data=test_user,
            allow_redirects=False,
            timeout=5
        )
        
        if response.status_code in [200, 302]:
            print_test("User Registration", "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_test("User Registration", "WARN", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("User Registration", "FAIL", str(e))
        return False

def test_api_endpoints():
    """Test API endpoints availability"""
    print_header("6. API ENDPOINTS TEST")
    
    # These endpoints might require authentication
    api_endpoints = [
        "/agent/chat",
        "/migration/export",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(BASE_URL + endpoint, timeout=5, allow_redirects=False)
            # We expect 401/403 (auth required) or 405 (method not allowed) or 302 (redirect)
            if response.status_code in [200, 302, 401, 403, 405]:
                print_test(f"API Endpoint: {endpoint}", "PASS", f"Endpoint exists (Status: {response.status_code})")
            else:
                print_test(f"API Endpoint: {endpoint}", "WARN", f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"API Endpoint: {endpoint}", "FAIL", str(e))

def test_configuration():
    """Test application configuration"""
    print_header("7. CONFIGURATION TEST")
    
    from app import create_app
    
    try:
        app = create_app()
        
        # Check DEBUG mode
        if app.config.get('DEBUG'):
            print_test("Debug Mode", "PASS", "Enabled (Development)")
        else:
            print_test("Debug Mode", "WARN", "Disabled")
        
        # Check database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite:///' in db_uri:
            print_test("Database Type", "PASS", "SQLite (Development)")
            print(f"  - Path: {db_uri}")
        else:
            print_test("Database Type", "WARN", f"Not SQLite: {db_uri}")
        
        # Check secret key
        if app.config.get('SECRET_KEY'):
            print_test("Secret Key", "PASS", "Configured")
        else:
            print_test("Secret Key", "FAIL", "Not configured")
        
        return True
    except Exception as e:
        print_test("Configuration", "FAIL", str(e))
        return False

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✓ Passed: {len(test_results['passed'])}")
    print(f"✗ Failed: {len(test_results['failed'])}")
    print(f"⚠ Warnings: {len(test_results['warnings'])}")
    
    if test_results["failed"]:
        print("\n❌ Failed Tests:")
        for test in test_results["failed"]:
            print(f"  - {test}")
    
    if test_results["warnings"]:
        print("\n⚠️  Warnings:")
        for test in test_results["warnings"]:
            print(f"  - {test}")
    
    print("\n" + "=" * 70)
    
    if len(test_results["failed"]) == 0:
        print("✅ ALL CRITICAL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED - Please review the results above")
    
    print("=" * 70 + "\n")

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  FLASK APPLICATION - COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 70)
    print(f"\nTesting server at: {BASE_URL}")
    print("Make sure the Flask server is running before executing this test.\n")
    
    # Run tests
    if not test_server_running():
        print("\n❌ Server is not running. Please start the server with 'flask run' and try again.")
        return
    
    test_static_resources()
    test_main_routes()
    test_database_connection()
    test_configuration()
    test_user_registration()
    test_api_endpoints()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
