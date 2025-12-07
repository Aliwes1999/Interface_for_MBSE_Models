from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, and_
import json
from . import db
from .models import Project, Requirement, RequirementVersion
from .services.ai_client import generate_requirements
from .services.excel_service import export_excel as export_excel_service, import_excel as import_excel_service
from .services.requirement_service import regenerate_requirement as regenerate_requirement_service

bp = Blueprint('main', __name__)

@bp.route("/")
@login_required
def home():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("start.html", projects=projects)

@bp.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        if project_name:
            # The concept of dynamic columns is removed in the new model.
            new_project = Project(name=project_name, user_id=current_user.id)
            db.session.add(new_project)
            db.session.commit()
        return redirect(url_for('main.home'))
    # The create.html is now a generic "new project" page if no project is passed.
    return render_template("create.html", project=None)

@bp.route("/project/<int:project_id>")
@login_required
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    # Get all requirements with ALL versions (not just the latest)
    # Filter out deleted requirements
    requirements = (
        Requirement.query
        .filter_by(project_id=project_id, is_deleted=False)
        .all()
    )
    
    # For each requirement, get all versions
    req_with_versions = []
    for req in requirements:
        # Get all versions for this requirement
        versions = req.versions
        if versions:  # Only include requirements that have versions
            req_with_versions.append((req, versions))
    
    # Get custom columns for this project
    custom_columns = project.get_custom_columns()
    
    return render_template(
        "create.html", 
        project=project, 
        req_with_versions=req_with_versions,
        custom_columns=custom_columns
    )

@bp.route("/deleted_requirements")
@login_required
def deleted_requirements_overview():
    """Show all deleted requirements across all user's projects."""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Collect deleted requirements from all projects
    all_deleted = []
    for project in projects:
        deleted_reqs = Requirement.query.filter_by(
            project_id=project.id, 
            is_deleted=True
        ).all()
        
        for req in deleted_reqs:
            latest_version = req.get_latest_version()
            if latest_version:
                all_deleted.append({
                    'project': project,
                    'requirement': req,
                    'version': latest_version
                })
    
    return render_template(
        "deleted_requirements_overview.html",
        deleted_items=all_deleted
    )

@bp.route("/requirement/<int:rid>/history")
@login_required
def requirement_history(rid):
    req = Requirement.query.get_or_404(rid)
    # Authorization check: ensure the user owns the project this requirement belongs to.
    if req.project.user_id != current_user.id:
        abort(403)
    
    # The 'versions' relationship is already ordered by version_index
    versions = req.versions
    return render_template("requirement_history.html", req=req, versions=versions)


@bp.route("/project/delete/<int:project_id>", methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    db.session.delete(project)
    db.session.commit()
    flash(f"Project '{project.name}' has been deleted.", "success")
    return redirect(url_for('main.home'))


# The routes below are now obsolete due to the data model refactoring
# and have been removed:
# - /project/<int:project_id>/deleted
# - /deleted_requirements_overview
# - /move/<int:project_id>/<int:req_id>/<string:from_table>/<string:to_table>
# - /edit/<int:project_id>/<int:req_id>
# - /export/<int:project_id>/<string:format>
# - /delete_column/<int:project_id>
# - /delete_requirement_permanently/<int:project_id>/<int:req_id>
# The simple /requirements and /add_requirement routes were also based on the old model.

# Routes for dynamic columns
@bp.route("/project/<int:project_id>/add_column", methods=['POST'])
@login_required
def add_column(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    column_name = request.form.get('column_name', '').strip()
    if not column_name:
        flash("Column name cannot be empty.", "danger")
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Get current columns and add the new one
    columns = project.get_custom_columns()
    if column_name in columns:
        flash(f"Column '{column_name}' already exists.", "warning")
    else:
        columns.append(column_name)
        project.set_custom_columns(columns)
        db.session.commit()
        flash(f"Column '{column_name}' added successfully.", "success")
    
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/project/<int:project_id>/remove_column/<column_name>", methods=['POST'])
@login_required
def remove_column(project_id, column_name):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    # Get current columns and remove the specified one
    columns = project.get_custom_columns()
    if column_name in columns:
        columns.remove(column_name)
        project.set_custom_columns(columns)
        db.session.commit()
        flash(f"Column '{column_name}' removed successfully.", "success")
    else:
        flash(f"Column '{column_name}' not found.", "warning")
    
    return redirect(url_for('main.manage_project', project_id=project_id))

# Route to update custom column data for a requirement version
@bp.route("/requirement_version/<int:version_id>/update_custom_data", methods=['POST'])
@login_required
def update_custom_data(version_id):
    version = RequirementVersion.query.get_or_404(version_id)
    # Authorization check
    if version.requirement.project.user_id != current_user.id:
        abort(403)
    
    column_name = request.form.get('column_name')
    value = request.form.get('value', '').strip()
    
    # Get current custom data and update it
    custom_data = version.get_custom_data()
    custom_data[column_name] = value
    version.set_custom_data(custom_data)
    db.session.commit()
    
    return jsonify({'success': True})

# Route to update requirement status
@bp.route("/requirement_version/<int:version_id>/update_status", methods=['POST'])
@login_required
def update_status(version_id):
    version = RequirementVersion.query.get_or_404(version_id)
    # Authorization check
    if version.requirement.project.user_id != current_user.id:
        abort(403)
    
    status = request.form.get('status')
    if status in ['Offen', 'In Arbeit', 'Fertig']:
        version.status = status
        db.session.commit()
        flash(f"Status updated to '{status}'.", "success")
    else:
        flash("Invalid status value.", "danger")
    
    return redirect(url_for('main.manage_project', project_id=version.requirement.project_id))

# AJAX route to get all versions of a requirement
@bp.route("/requirement/<int:req_id>/versions_json")
@login_required
def requirement_versions_json(req_id):
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)
    
    versions_data = []
    for ver in req.versions:
        versions_data.append({
            'id': ver.id,
            'version_index': ver.version_index,
            'version_label': ver.version_label,
            'title': ver.title,
            'description': ver.description,
            'category': ver.category,
            'status': ver.status,
            'status_color': ver.get_status_color(),
            'custom_data': ver.get_custom_data(),
            'created_at': ver.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify(versions_data)

# Route to update requirement version data
@bp.route("/requirement_version/<int:version_id>/update", methods=['POST'])
@login_required
def update_requirement_version(version_id):
    version = RequirementVersion.query.get_or_404(version_id)
    # Authorization check
    if version.requirement.project.user_id != current_user.id:
        abort(403)
    
    # Get form data
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    save_type = request.form.get('save_type', 'intermediate')  # 'intermediate' or 'final'
    
    # Validate required fields
    if not title or not description:
        flash("Title and description are required.", "danger")
        return redirect(url_for('main.manage_project', project_id=version.requirement.project_id))
    
    # Update fields
    version.title = title
    version.description = description
    version.category = category
    
    # Update status based on save type
    if save_type == 'intermediate':
        version.status = 'In Arbeit'
    elif save_type == 'final':
        version.status = 'Fertig'
    
    # Track who modified this version
    version.last_modified_by_id = current_user.id
    
    # Update custom data
    custom_data = version.get_custom_data()
    project = version.requirement.project
    custom_columns = project.get_custom_columns()
    
    for column in custom_columns:
        value = request.form.get(f'custom_{column}', '').strip()
        custom_data[column] = value
    
    version.set_custom_data(custom_data)
    
    # Save changes
    db.session.commit()
    
    flash(f"Requirement updated successfully. Status: {version.status}", "success")
    return redirect(url_for('main.manage_project', project_id=version.requirement.project_id))

# Route to delete a specific version of a requirement
@bp.route("/requirement_version/<int:version_id>/delete", methods=['POST'])
@login_required
def delete_requirement_version(version_id):
    version = RequirementVersion.query.get_or_404(version_id)
    req = version.requirement

    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)

    project_id = req.project_id

    # Check if there are any remaining versions
    remaining_versions = RequirementVersion.query.filter_by(requirement_id=req.id).count()

    if remaining_versions == 1:
        # This is the last version, mark the requirement as deleted instead of deleting the version
        req.is_deleted = True
        flash("Last version deleted. Requirement moved to trash.", "success")
    else:
        # Delete this specific version
        db.session.delete(version)
        flash(f"Version {version.version_label} deleted successfully.", "success")

    db.session.commit()

    return redirect(url_for('main.deleted_requirements_overview'))

# Route to soft delete a requirement (kept for compatibility, but marks all versions as deleted)
@bp.route("/requirement/<int:req_id>/delete", methods=['POST'])
@login_required
def delete_requirement(req_id):
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)

    # Soft delete
    req.is_deleted = True
    db.session.commit()

    flash("Requirement moved to trash.", "success")
    return redirect(url_for('main.deleted_requirements_overview'))

# Route to restore a deleted requirement
@bp.route("/requirement/<int:req_id>/restore", methods=['POST'])
@login_required
def restore_requirement(req_id):
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)
    
    # Restore
    req.is_deleted = False
    db.session.commit()
    
    flash("Requirement restored successfully.", "success")
    return redirect(url_for('main.deleted_requirements_overview'))

# Route to permanently delete a requirement
@bp.route("/requirement/<int:req_id>/delete_permanently", methods=['POST'])
@login_required
def delete_requirement_permanently(req_id):
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)
    
    project_id = req.project_id
    
    # Permanently delete (cascade will delete all versions)
    db.session.delete(req)
    db.session.commit()
    
    flash("Requirement permanently deleted.", "success")
    return redirect(url_for('main.deleted_requirements_overview'))

# Route to regenerate a single requirement with AI
@bp.route("/requirement/<int:req_id>/regenerate", methods=['POST'])
@login_required
def regenerate_requirement(req_id):
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        abort(403)
    
    # Get the latest version to use as context
    latest_version = req.get_latest_version()
    if not latest_version:
        flash("No existing version found to regenerate.", "danger")
        return redirect(url_for('main.manage_project', project_id=req.project_id))
    
    try:
        # Get project's custom columns
        custom_columns = req.project.get_custom_columns()
        
        # Prepare context for AI
        context = {
            "project_name": req.project.name,
            "requirement_title": latest_version.title,
            "requirement_description": latest_version.description,
            "requirement_category": latest_version.category or "",
            "custom_data": latest_version.get_custom_data()
        }
        
        # Build complete columns list: title, description, custom columns, category
        columns = ["title", "description"] + custom_columns + ["category"]
        
        # Generate a new version with AI
        result = generate_single_requirement_alternative(context, columns)
        
        if not result:
            flash("Failed to generate alternative. AI returned empty result.", "danger")
            return redirect(url_for('main.manage_project', project_id=req.project_id))
        
        # Calculate next version
        next_index = latest_version.version_index + 1
        next_label = chr(ord('A') + (next_index - 1))
        
        # Create new version
        new_version = RequirementVersion(
            requirement_id=req.id,
            version_index=next_index,
            version_label=next_label,
            title=result.get("title", latest_version.title),
            description=result.get("description", latest_version.description),
            category=result.get("category", latest_version.category),
            status="Offen",  # New version starts as "Open"
            created_by_id=current_user.id  # Track who created this version
        )
        
        # Get custom data from AI result or copy from previous version
        custom_data = {}
        for col in custom_columns:
            # Try to get value from AI result first, fallback to previous version
            value = result.get(col, latest_version.get_custom_data().get(col, ""))
            if value:
                custom_data[col] = value
        
        if custom_data:
            new_version.set_custom_data(custom_data)
        
        db.session.add(new_version)
        db.session.commit()
        
        flash(f"New version {next_label} generated successfully!", "success")
        
    except Exception as e:
        flash(f"Error generating alternative: {str(e)}", "danger")
    
    return redirect(url_for('main.manage_project', project_id=req.project_id))

def generate_single_requirement_alternative(context, columns):
    """Generate an alternative version of a requirement using AI."""
    try:
        # Prepare prompt for AI
        prompt = f"""
        Generate an alternative version of the following requirement:
        
        Project: {context['project_name']}
        
        Original Requirement:
        Title: {context['requirement_title']}
        Description: {context['requirement_description']}
        Category: {context['requirement_category']}
        
        Additional Context:
        {context['custom_data']}
        
        Please provide an improved version with:
        1. A clearer title
        2. A more detailed description
        3. The same or improved category
        
        Keep the core meaning but enhance clarity, completeness, and precision.
        """
        
        # Call the AI service
        ai_result = generate_requirements(prompt, {}, columns)
        
        # We expect a list of requirements, but we only need the first one
        if ai_result and len(ai_result) > 0:
            return ai_result[0]
        
        return None
        
    except Exception as e:
        print(f"Error in generate_single_requirement_alternative: {str(e)}")
        raise

# Route to export project requirements to Excel
@bp.route("/project/<int:project_id>/export_excel")
@login_required
def export_excel(project_id):
    return export_excel_service(project_id)

# Route to import requirements from Excel
@bp.route("/project/<int:project_id>/import_excel", methods=['POST'])
@login_required
def import_excel(project_id):
    file = request.files.get('excel_file')
    return import_excel_service(project_id, file)

# Route to share project with another user
@bp.route("/project/<int:project_id>/share", methods=['POST'])
@login_required
def share_project(project_id):
    from .models import User
    
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    email = request.form.get('email', '').strip()
    if not email:
        flash("Bitte geben Sie eine E-Mail-Adresse ein.", "danger")
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        flash(f"Benutzer mit E-Mail '{email}' nicht gefunden.", "danger")
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    if user.id == current_user.id:
        flash("Sie können das Projekt nicht mit sich selbst teilen.", "warning")
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Check if already shared
    if user in project.shared_with:
        flash(f"Projekt ist bereits mit {email} geteilt.", "warning")
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Share project
    project.shared_with.append(user)
    db.session.commit()
    
    flash(f"Projekt erfolgreich mit {email} geteilt!", "success")
    return redirect(url_for('main.manage_project', project_id=project_id))

# Route to unshare project
@bp.route("/project/<int:project_id>/unshare/<int:user_id>", methods=['POST'])
@login_required
def unshare_project(project_id, user_id):
    from .models import User
    
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if user in project.shared_with:
        project.shared_with.remove(user)
        db.session.commit()
        flash(f"Projekt-Freigabe für {user.email} entfernt.", "success")
    else:
        flash("Benutzer hat keinen Zugriff auf dieses Projekt.", "warning")
    
    return redirect(url_for('main.manage_project', project_id=project_id))

# Route to toggle requirement version block status
@bp.route("/requirement_version/<int:version_id>/toggle_block", methods=['POST'])
@login_required
def toggle_block_requirement(version_id):
    from datetime import datetime
    
    version = RequirementVersion.query.get_or_404(version_id)
    project = version.requirement.project
    
    # Authorization check - only project owner can block
    if project.user_id != current_user.id:
        abort(403)
    
    # Toggle block status
    if version.is_blocked:
        # Unblock
        version.is_blocked = False
        version.blocked_by_id = None
        version.blocked_at = None
        flash(f"Version {version.version_label} wurde freigegeben.", "success")
    else:
        # Block
        version.is_blocked = True
        version.blocked_by_id = current_user.id
        version.blocked_at = datetime.utcnow()
        flash(f"Version {version.version_label} wurde blockiert.", "warning")
    
    db.session.commit()
    return redirect(url_for('main.manage_project', project_id=project.id))

@bp.route("/hello")
def hello():
    return "Hello from Blueprint!"

