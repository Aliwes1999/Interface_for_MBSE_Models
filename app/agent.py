from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from . import db
from .models import Requirement, RequirementVersion, Project, ProjectFile
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


@agent_bp.route('/upload/<int:project_id>')
@login_required
def upload_page(project_id):
    """Render a dedicated upload page where users can upload an Excel file to be
    analyzed/optimized by the AI."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id and current_user not in project.shared_with:
        abort(403)

    return render_template('agent/upload.html', project=project)


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
        uploaded_file_path = None
        uploaded_file_id = None
        if 'excel_file' in request.files:
            file = request.files['excel_file']
            if file and file.filename and file.filename.endswith(('.xlsx', '.xls')):
                # Secure filename and add timestamp to prevent overwrites
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{name}_{timestamp}{ext}"

                # Save file permanently in uploads folder
                uploads_dir = os.path.join('uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                uploaded_file_path = os.path.join(uploads_dir, unique_filename)
                file.save(uploaded_file_path)

                try:
                    # Parse Excel file
                    excel_data = parse_excel_to_data(uploaded_file_path)
                    existing_requirements = excel_data

                    # Create database entry for uploaded file
                    project_file = ProjectFile(
                        project_id=project_id,
                        filename=filename,  # Original filename for display
                        filepath=uploaded_file_path,
                        file_type='upload',
                        created_by_id=current_user.id
                    )
                    db.session.add(project_file)
                    db.session.commit()
                    uploaded_file_id = project_file.id

                except Exception as e:
                    # Clean up uploaded file on error
                    if uploaded_file_path and os.path.exists(uploaded_file_path):
                        try:
                            os.remove(uploaded_file_path)
                        except:
                            pass  # Ignore cleanup errors
                    raise e
        
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

        # After saving generated requirements, also create an Excel snapshot
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment

            wb = Workbook()
            ws = wb.active
            ws.title = "Generated Requirements"

            # use same columns list (title, description, custom..., category)
            headers = [c.capitalize() for c in columns]
            # write headers
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="top")

            # write generated rows
            row_num = 2
            for req in generated_reqs:
                row = []
                for col in columns:
                    row.append(req.get(col, ""))
                for col_num, val in enumerate(row, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=val)
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
                row_num += 1

            # set some column widths
            for i in range(1, len(headers) + 1):
                col_letter = chr(ord('A') + i - 1)
                ws.column_dimensions[col_letter].width = 20

            # save workbook to uploads dir
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"generated_requirements_{project.name.replace(' ', '_')}_{timestamp}.xlsx"
            uploads_dir = os.path.join('uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            filepath = os.path.join(uploads_dir, filename)
            wb.save(filepath)

            # create ProjectFile entry
            project_file = ProjectFile(
                project_id=project_id,
                filename=filename,
                filepath=filepath,
                file_type='generated',
                created_by_id=current_user.id
            )
            db.session.add(project_file)
            db.session.commit()
            
            # Get the file ID for redirect
            generated_file_id = project_file.id
        except Exception:
            # non-fatal: ignore snapshot errors
            generated_file_id = None
            db.session.rollback()

        # Redirect to the project overview and focus the requirements tab
        # for the created/uploaded file so the user can edit the requirements.
        if uploaded_file_id:
            redirect_url = url_for('main.project_overview', project_id=project_id, file_id=uploaded_file_id)
        elif generated_file_id:
            redirect_url = url_for('main.project_overview', project_id=project_id, file_id=generated_file_id)
        else:
            redirect_url = url_for('main.project_overview', project_id=project_id)

        return jsonify({
            'ok': True,
            'count': saved_count,
            'redirect': redirect_url
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
