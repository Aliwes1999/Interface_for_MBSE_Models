# TODO: Implement AI-Agent Feature for MBSE Project

## Pending Tasks

- [x] Update app/models.py: Modify Requirement model to include title, description, category, status, project_id, created_at. Add requirements relationship to Project model.
- [x] Create app/services/ai_client.py: Implement generate_requirements function to call AI endpoint, parse JSON response with regex fallback.
- [x] Create app/agent.py: New blueprint with GET /agent/<project_id> route to render agent template and POST /agent/generate/<project_id> route to handle generation, validate ownership, call AI, save to DB, return JSON.
- [x] Create templates/agent/agent.html: Bootstrap 5 layout with dynamic key-value fields (add/remove via JS), system_prompt textarea (optional), user_prompt textarea (required), generate button with fetch POST, loading spinner, success message and redirect.
- [x] Update requirements.txt: Add 'requests' library.
- [x] Update app/**init**.py: Import and register the new agent blueprint.
- [x] Update app/templates/start.html: Add "KI-Agent" button/link in the projects table for each project.
- [x] Run db.create_all() to ensure updated tables are created.
- [ ] Test the flow: Create project, access agent page, input data, generate requirements, check DB, and redirect to project view.
