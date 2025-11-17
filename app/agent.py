import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from . import db
from .models import Project, Requirement, RequirementVersion, version_label
from .services.ai_client import generate_requirements

agent_bp = Blueprint('agent', __name__, template_folder='templates/agent')

def normalize_key(title: str) -> str:
    """Creates a stable, lowercase key from a title string."""
    if not title:
        return ""
    s = title.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def next_version_info(req: Requirement) -> tuple[int, str]:
    """Determines the next version index and label for a requirement."""
    if not req.versions:
        return 1, version_label(1)
    # The versions are ordered by version_index, so the last one is the latest.
    last_idx = req.versions[-1].version_index
    new_idx = last_idx + 1
    return new_idx, version_label(new_idx)


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
    return render_template('agent.html', project=project)


@agent_bp.route('/agent/generate/<int:project_id>', methods=['POST'])
@login_required
def generate(project_id):
    """
    Generate requirements using AI and create versioned entries in the database.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'ok': False, 'error': 'Zugriff verweigert.'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'Keine Daten empfangen.'}), 400
    except Exception:
        return jsonify({'ok': False, 'error': 'Ungültiges JSON-Format.'}), 400

    user_description = data.get('user_description', '').strip() or None
    inputs_array = data.get('inputs', [])
    inputs_dict = {item.get('key'): item.get('value') for item in inputs_array if item.get('key')}

    # Get project's custom columns
    custom_columns = project.get_custom_columns()
    
    # Build complete columns list: title, description, custom columns, category, status
    columns = ["title", "description"] + custom_columns + ["category", "status"]

    try:
        requirements_data = generate_requirements(user_description, inputs_dict, columns)
        
        saved_count = 0
        for item in requirements_data:
            title = item.get("title", "").strip()
            if not title:
                continue  # Skip requirements without a title

            description = item.get("description", "").strip()
            category = item.get("category", "") or ""
            status = item.get("status", "") or "Offen"
            
            key = normalize_key(title)

            # Find existing logical requirement in the current project
            req = Requirement.query.filter_by(project_id=project_id, key=key).first()

            if not req:
                # It's a new logical requirement, create it
                req = Requirement(project_id=project_id, key=key)
                db.session.add(req)
                # Flush to get the ID for the foreign key relationship
                db.session.flush()
                version_index, label = 1, version_label(1)
            else:
                # It's a new version of an existing requirement
                version_index, label = next_version_info(req)

            # Create the new version
            new_version = RequirementVersion(
                requirement_id=req.id,
                version_index=version_index,
                version_label=label,
                title=title,
                description=description,
                category=category,
                status=status,
                created_by_id=current_user.id  # Track who created this version
            )
            
            # Save custom column data
            custom_data = {}
            for col in custom_columns:
                value = item.get(col, "")
                if value:
                    custom_data[col] = value
            
            if custom_data:
                new_version.set_custom_data(custom_data)
            
            db.session.add(new_version)
            saved_count += 1

        db.session.commit()

        return jsonify({
            'ok': True,
            'count': saved_count,
            'redirect': url_for('main.manage_project', project_id=project_id)
        }), 200

    except ValueError as e:
        return jsonify({'ok': False, 'error': f'Konfigurationsfehler: {str(e)}'}), 500
    except RuntimeError as e:
        return jsonify({'ok': False, 'error': f'KI-Service-Fehler: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}'}), 500
