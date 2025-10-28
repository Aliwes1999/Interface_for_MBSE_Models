# TODO: Add User Authentication to Flask App

## Steps to Complete

- [x] Update requirements.txt: Add Flask-Login and Werkzeug
- [x] Update app/models.py: Add User model with id, email (unique), password_hash, created_at; Add user_id to Project model
- [x] Update app/**init**.py: Initialize LoginManager and user_loader
- [x] Create app/auth.py: Blueprint with /auth/login (GET/POST), /auth/register (GET/POST), /auth/logout routes
- [x] Update app/routes.py: Protect all project routes with @login_required, show only user's projects, set user_id on create, check ownership on delete
- [x] Create app/templates/auth/login.html: Login form with email and password
- [x] Create app/templates/auth/register.html: Registration form
- [x] Update app/templates/base.html: Add navbar links for Login/Logout/Register based on login status
- [x] Migrate database: Update models, handle existing data
- [x] Test authentication: Start app and verify login, register, logout, project management
