from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from . import db
from .models import Project, Requirement
from .services.ai_client import generate_requirements

agent_bp = Blueprint('agent', __name__, template_folder='templates/agent')

@agent_bp.route('/agent/<int:project_id>', methods=['GET'])
@login_required
def agent_page(project_id):
    """
    Render the AI agent page for a specific project.
    Only accessible by the project owner.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    return render_template('agent/agent.html', project=project)


@agent_bp.route('/agent/generate/<int:project_id>', methods=['POST'])
@login_required
def generate(project_id):
    """
    Generate requirements using AI based on user description and inputs.
    
    Expected JSON body:
    {
        "user_description": "optional string",
        "inputs": [{"key": "...", "value": "..."}, ...]
    }
    
    Returns:
    {
        "ok": true,
        "count": N,
        "redirect": "/manage/<project_id>"
    }
    or
    {
        "ok": false,
        "error": "error message"
    }
    """
    # Verify project ownership
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'ok': False, 'error': 'Zugriff verweigert. Sie sind nicht der Besitzer dieses Projekts.'}), 403

    # Parse request data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'Keine Daten empfangen.'}), 400
    except Exception:
        return jsonify({'ok': False, 'error': 'Ungültiges JSON-Format.'}), 400

    user_description = data.get('user_description', '').strip() or None
    inputs_array = data.get('inputs', [])

    # Convert inputs array to dict
    inputs_dict = {}
    if isinstance(inputs_array, list):
        for item in inputs_array:
            if isinstance(item, dict):
                key = item.get('key', '').strip()
                value = item.get('value', '').strip()
                if key and value:
                    inputs_dict[key] = value

    # Get project columns for dynamic AI generation
    columns = project.get_columns()

    # Generate requirements using AI with dynamic columns
    try:
        requirements_data = generate_requirements(user_description, inputs_dict, columns)

        # Get current created requirements to determine next ID
        created = project.get_created_requirements()
        next_id = max([r['id'] for r in created] + [0]) + 1

        # Add generated requirements to created list with all columns
        saved_count = 0
        for req_data in requirements_data:
            new_req = {'id': next_id}
            
            # Fill in all columns from AI response
            for col in columns:
                # Get value from AI response, default to empty string
                new_req[col] = req_data.get(col, '')
            
            created.append(new_req)
            next_id += 1
            saved_count += 1

        # Save updated created requirements
        project.set_created_requirements(created)
        db.session.commit()

        # Return success response with redirect URL
        return jsonify({
            'ok': True,
            'count': saved_count,
            'redirect': url_for('main.manage_project', project_id=project_id)
        }), 200

    except ValueError as e:
        # Configuration error (e.g., missing API key)
        return jsonify({
            'ok': False,
            'error': f'Konfigurationsfehler: {str(e)}'
        }), 500

    except RuntimeError as e:
        # AI service error
        return jsonify({
            'ok': False,
            'error': f'KI-Service-Fehler: {str(e)}'
        }), 500

    except Exception as e:
        # Unexpected error
        db.session.rollback()
        return jsonify({
            'ok': False,
            'error': f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}'
        }), 500
