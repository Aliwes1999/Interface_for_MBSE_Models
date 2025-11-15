from flask import render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from . import bp, db
from .models import Requirement, Project
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
            new_project = Project(name=project_name, user_id=current_user.id)
            new_project.set_columns(['Title', 'Beschreibung', 'Kategorie', 'Status'])
            db.session.add(new_project)
            db.session.commit()
        return redirect(url_for('main.home'))
    return render_template("create.html")

@bp.route("/project/<int:project_id>", methods=['GET', 'POST'])
@login_required
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    projects = Project.query.filter_by(user_id=current_user.id).all()
    columns = project.get_columns()
    created = project.get_created_requirements()
    intermediate = project.get_intermediate_requirements()
    saved = project.get_saved_requirements()
    deleted = project.get_deleted_requirements()
    if request.method == 'POST':
        if 'add_column' in request.form:
            column_name = request.form.get('column_name')
            if column_name:
                if column_name not in columns:
                    columns.append(column_name)
                    project.set_columns(columns)
                    # Add new column to all requirements
                    for req_list_name in ['created_requirements', 'intermediate_requirements', 'saved_requirements', 'deleted_requirements']:
                        req_list = getattr(project, f'get_{req_list_name}')()
                        for req in req_list:
                            req[column_name] = ''
                        getattr(project, f'set_{req_list_name}')(req_list)
                    db.session.commit()
        elif 'add_requirement' in request.form:
            new_req_id = max([r['id'] for r in created] + [0]) + 1
            new_req = {'id': new_req_id}
            for col in columns:
                new_req[col] = request.form.get(col, '')
            created.append(new_req)
            project.set_created_requirements(created)
            db.session.commit()
        return redirect(url_for('main.manage_project', project_id=project_id))
    return render_template("create.html", projects=projects, project=project, columns=columns, created=created, intermediate=intermediate, saved=saved, deleted=deleted)

@bp.route("/project/<int:project_id>/deleted")
@login_required
def deleted_requirements(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    return render_template("deleted_requirements.html", project=project)

@bp.route("/deleted_requirements_overview")
@login_required
def deleted_requirements_overview():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("deleted_requirements_projects.html", projects=projects)

@bp.route("/move/<int:project_id>/<int:req_id>/<string:from_table>/<string:to_table>")
@login_required
def move_requirement(project_id, req_id, from_table, to_table):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    table_map = {
        'created': 'created_requirements',
        'intermediate': 'intermediate_requirements',
        'saved': 'saved_requirements',
        'deleted': 'deleted_requirements'
    }
    if from_table in table_map and to_table in table_map:
        from_list = getattr(project, f'get_{table_map[from_table]}')()
        to_list = getattr(project, f'get_{table_map[to_table]}')()
        req = next((r for r in from_list if r['id'] == req_id), None)
        if req:
            from_list.remove(req)
            to_list.append(req)
            getattr(project, f'set_{table_map[from_table]}')(from_list)
            getattr(project, f'set_{table_map[to_table]}')(to_list)
            db.session.commit()

    if from_table == 'deleted':
        return redirect(url_for('main.deleted_requirements', project_id=project_id))
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/edit/<int:project_id>/<int:req_id>", methods=['POST'])
@login_required
def edit_requirement(project_id, req_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    table_map = {
        'created': 'created_requirements',
        'intermediate': 'intermediate_requirements',
        'saved': 'saved_requirements',
        'deleted': 'deleted_requirements'
    }
    req = None
    req_table = None
    for table_name, attr_name in table_map.items():
        req_list = getattr(project, f'get_{attr_name}')()
        for r in req_list:
            if r['id'] == req_id:
                req = r
                req_table = attr_name
                break
        if req:
            break
    if req and req_table:
        for col in project.get_columns():
            req[col] = request.form.get(col, '')
        getattr(project, f'set_{req_table}')(req_list)
        db.session.commit()
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/export/<int:project_id>/<string:format>")
@login_required
def export_requirements(project_id, format):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    saved_reqs = project.get_saved_requirements()
    columns = project.get_columns()
    if format == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Gespeicherte Requirements"
        ws.append(['ID'] + columns)
        for req in saved_reqs:
            row = [req['id']] + [req[col] for col in columns]
            ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(output, download_name=f"{project.name}_requirements.xlsx", as_attachment=True)
    elif format == 'pdf':
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=letter)
        c.drawString(100, 750, f"Requirements for {project.name}")
        y = 720
        for req in saved_reqs:
            c.drawString(100, y, f"ID: {req['id']}")
            y -= 20
            for col in columns:
                c.drawString(120, y, f"{col}: {req[col]}")
                y -= 20
            y -= 20
        c.save()
        output.seek(0)
        return send_file(output, download_name=f"{project.name}_requirements.pdf", as_attachment=True)
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/hello")
def hello():
    return "Hello from Blueprint!"

@bp.route("/requirements")
def list_requirements():
    requirements = Requirement.query.all()
    return render_template("requirements.html", requirements=requirements)

@bp.route("/add_requirement", methods=['POST'])
def add_requirement():
    nummer = request.form.get('nummer')
    beschreibung = request.form.get('beschreibung')
    kategorie = request.form.get('kategorie')
    status = request.form.get('status')
    if nummer and beschreibung and kategorie and status:
        new_req = Requirement(nummer=nummer, beschreibung=beschreibung, kategorie=kategorie, status=status)
        db.session.add(new_req)
        db.session.commit()
    return redirect(url_for('main.list_requirements'))

@bp.route("/delete/<int:project_id>", methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Projekt erfolgreich gelöscht.', 'success')
    return redirect(url_for('main.home'))

@bp.route("/delete_column/<int:project_id>", methods=['POST'])
@login_required
def delete_column(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    column_name = request.form.get('column_name')
    
    # Define fixed columns that cannot be deleted
    FIXED_COLUMNS = ['ID', 'Titel', 'Beschreibung']
    
    if not column_name:
        flash('Kein Spaltenname angegeben.', 'error')
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Check if column is fixed
    if column_name in FIXED_COLUMNS:
        flash(f'Die Spalte "{column_name}" kann nicht gelöscht werden, da sie eine feste Spalte ist.', 'error')
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Get current columns
    columns = project.get_columns()
    
    # Check if column exists
    if column_name not in columns:
        flash(f'Die Spalte "{column_name}" existiert nicht.', 'error')
        return redirect(url_for('main.manage_project', project_id=project_id))
    
    # Remove column from columns list
    columns.remove(column_name)
    project.set_columns(columns)
    
    # Remove column data from all requirement tables
    for req_list_name in ['created_requirements', 'intermediate_requirements', 'saved_requirements', 'deleted_requirements']:
        req_list = getattr(project, f'get_{req_list_name}')()
        for req in req_list:
            if column_name in req:
                del req[column_name]
        getattr(project, f'set_{req_list_name}')(req_list)
    
    db.session.commit()
    flash(f'Spalte "{column_name}" wurde erfolgreich gelöscht.', 'success')
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/delete_requirement_permanently/<int:project_id>/<int:req_id>", methods=['POST'])
@login_required
def delete_requirement_permanently(project_id, req_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    deleted_list = project.get_deleted_requirements()
    req_to_delete = next((r for r in deleted_list if r['id'] == req_id), None)
    
    if req_to_delete:
        deleted_list.remove(req_to_delete)
        project.set_deleted_requirements(deleted_list)
        db.session.commit()
        flash('Requirement endgültig gelöscht.', 'success')
    else:
        flash('Requirement nicht gefunden.', 'error')
        
    return redirect(url_for('main.deleted_requirements', project_id=project_id))

