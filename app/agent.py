from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from . import db
from .models import Requirement, RequirementVersion, Project
from .services.ai_client import AIClient, generate_requirements
from .services.exel_service import parse_excel_to_data

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')


def normalize_key(title: str) -> str:
    """
    Normalize a requirement title to create a unique key.
    
    Args:
        title (str): The requirement title
    
    Returns:
        str: Normalized key (lowercase, no special chars, max 100 chars)
    """
    import re
    # Convert to lowercase and replace spaces with underscores
    key = title.lower().strip()
    # Remove special characters except underscores and hyphens
    key = re.sub(r'[^a-z0-9_\-]', '_', key)
    # Replace multiple underscores with single underscore
    key = re.sub(r'_+', '_', key)
    # Trim to max 100 characters
    key = key[:100]
    # Remove leading/trailing underscores
    key = key.strip('_')
    return key


@agent_bp.route('/<int:project_id>')
@login_required
def agent_page(project_id):
    """Render the AI agent page for a specific project"""
    project = Project.query.get_or_404(project_id)
    
    # Authorization check
    if project.user_id != current_user.id:
        abort(403)
    
    return render_template('agent/agent.html', project=project)


@agent_bp.route('/generate/<int:project_id>', methods=['POST'])
@login_required
def generate_requirements_route(project_id):
    """Generate requirements using AI for a specific project"""
    project = Project.query.get_or_404(project_id)
    
    # Authorization check
    if project.user_id != current_user.id:
        abort(403)
    
    try:
        # Get form data
        user_description = request.form.get('user_description', '').strip()
        inputs_json = request.form.get('inputs', '[]')
        
        # Parse inputs
        try:
            inputs_list = json.loads(inputs_json)
            inputs = {item['key']: item['value'] for item in inputs_list if 'key' in item and 'value' in item}
        except:
            inputs = {}
        
        # Check if Excel file was uploaded
        existing_requirements = None
        temp_path = None
        if 'excel_file' in request.files:
            file = request.files['excel_file']
            if file and file.filename and file.filename.endswith(('.xlsx', '.xls')):
                # Save file temporarily
                filename = secure_filename(file.filename)
                temp_path = os.path.join('instance', 'temp', filename)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                file.save(temp_path)
                
                try:
                    # Parse Excel file
                    excel_data = parse_excel_to_data(temp_path)
                    existing_requirements = excel_data
                except Exception as e:
                    # Clean up temp file on error
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass  # Ignore cleanup errors
                    raise e
                finally:
                    # Clean up temp file - use a delay to ensure file is closed
                    if temp_path and os.path.exists(temp_path):
                        import time
                        import gc
                        gc.collect()  # Force garbage collection to close file handles
                        time.sleep(0.1)  # Small delay to ensure file is released
                        try:
                            os.remove(temp_path)
                        except Exception as cleanup_error:
                            # If we still can't delete, log it but don't fail the request
                            print(f"Warning: Could not delete temp file {temp_path}: {cleanup_error}")
        
        # Get project's custom columns
        custom_columns = project.get_custom_columns()
        
        # Build complete columns list: title, description, custom columns, category
        columns = ["title", "description"] + custom_columns + ["category"]
        
        # Generate requirements using AI
        generated_reqs = generate_requirements(
            user_description=user_description if user_description else None,
            inputs=inputs,
            columns=columns,
            existing_requirements=existing_requirements
        )
        
        if not generated_reqs:
            return jsonify({
                'ok': False,
                'error': 'Keine Requirements generiert. Bitte versuchen Sie es erneut.'
            }), 400
        
        # Save generated requirements to database
        saved_count = 0
        for req_data in generated_reqs:
            title = req_data.get('title', '').strip()
            description = req_data.get('description', '').strip()
            
            if not title or not description:
                continue
            
            # Create normalized key
            key = normalize_key(title)
            
            # Check if requirement with this key already exists
            req = Requirement.query.filter_by(project_id=project_id, key=key).first()
            
            if not req:
                # Create new requirement
                req = Requirement(project_id=project_id, key=key)
                db.session.add(req)
                db.session.flush()
                version_index = 1
                version_label = 'A'
            else:
                # Create new version for existing requirement
                last_version = req.versions[-1] if req.versions else None
                version_index = last_version.version_index + 1 if last_version else 1
                version_label = chr(ord('A') + (version_index - 1))
            
            # Create requirement version
            category = req_data.get('category', '').strip()
            
            new_version = RequirementVersion(
                requirement_id=req.id,
                version_index=version_index,
                version_label=version_label,
                title=title,
                description=description,
                category=category,
                status='Offen',
                created_by_id=current_user.id
            )
            
            # Add custom column data
            custom_data = {}
            for col in custom_columns:
                value = req_data.get(col, '').strip()
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
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'ok': False,
            'error': f'Fehler beim Generieren: {str(e)}'
        }), 500


@agent_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_requirements():
    """Analyze requirements using AI"""
    try:
        data = request.get_json()
        requirements_text = data.get('requirements', '')
        
        if not requirements_text:
            return jsonify({'error': 'No requirements provided'}), 400
        
        # Initialize AI client
        ai_client = AIClient()
        
        # Analyze requirements
        analysis = ai_client.analyze_requirements(requirements_text)
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agent_bp.route('/suggest/<int:requirement_id>', methods=['POST'])
@login_required
def suggest_improvements(requirement_id):
    """Suggest improvements for requirements"""
    try:
        requirement = Requirement.query.get_or_404(requirement_id)
        
        # Authorization check
        if requirement.project.user_id != current_user.id:
            abort(403)
        
        # Get latest version
        latest_version = requirement.get_latest_version()
        if not latest_version:
            return jsonify({'error': 'No version found for this requirement'}), 404
        
        # Initialize AI client
        ai_client = AIClient()
        
        # Get suggestions
        suggestions = ai_client.suggest_improvements(latest_version)
        
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
