from flask import render_template, request, redirect, url_for, flash, send_file
from . import bp
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Global list to store projects (in-memory, resets on restart)
projects = []

@bp.route("/")
def home():
    return render_template("start.html", projects=projects)

@bp.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        if project_name:
            new_id = max([p['id'] for p in projects]) + 1 if projects else 1
            projects.append({
                'id': new_id,
                'name': project_name,
                'columns': ['Title', 'Beschreibung', 'Kategorie', 'Status'],
                'created': [],
                'intermediate': [],
                'saved': [],
                'deleted': []
            })
        return redirect(url_for('main.home'))
    return render_template("create.html")

@bp.route("/project/<int:project_id>", methods=['GET', 'POST'])
def manage_project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        if 'add_column' in request.form:
            column_name = request.form.get('column_name')
            if column_name and column_name not in project['columns']:
                project['columns'].append(column_name)
                for req_list in [project['created'], project['intermediate'], project['saved'], project['deleted']]:
                    for req in req_list:
                        req[column_name] = ''
        elif 'add_requirement' in request.form:
            new_req = {'id': max([r['id'] for r in project['created'] + project['intermediate'] + project['saved'] + project['deleted']]) + 1 if any(project[k] for k in ['created', 'intermediate', 'saved', 'deleted']) else 1}
            for col in project['columns']:
                new_req[col] = request.form.get(col, '')
            project['created'].append(new_req)
        return redirect(url_for('main.manage_project', project_id=project_id))
    return render_template("create.html", projects=projects, project=project)

@bp.route("/move/<int:project_id>/<int:req_id>/<string:from_table>/<string:to_table>")
def move_requirement(project_id, req_id, from_table, to_table):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project and from_table in ['created', 'intermediate', 'saved', 'deleted'] and to_table in ['created', 'intermediate', 'saved', 'deleted']:
        req = None
        for r in project[from_table]:
            if r['id'] == req_id:
                req = r
                break
        if req:
            project[from_table].remove(req)
            project[to_table].append(req)
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/edit/<int:project_id>/<int:req_id>", methods=['POST'])
def edit_requirement(project_id, req_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return redirect(url_for('main.home'))
    req = None
    for table in ['created', 'intermediate', 'saved', 'deleted']:
        for r in project[table]:
            if r['id'] == req_id:
                req = r
                break
        if req:
            break
    if not req:
        return redirect(url_for('main.manage_project', project_id=project_id))
    for col in project['columns']:
        req[col] = request.form.get(col, '')
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/export/<int:project_id>/<string:format>")
def export_requirements(project_id, format):
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return redirect(url_for('main.home'))
    if format == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Gespeicherte Requirements"
        ws.append(['ID'] + project['columns'])
        for req in project['saved']:
            row = [req['id']] + [req[col] for col in project['columns']]
            ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(output, download_name=f"{project['name']}_requirements.xlsx", as_attachment=True)
    elif format == 'pdf':
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=letter)
        c.drawString(100, 750, f"Requirements for {project['name']}")
        y = 720
        for req in project['saved']:
            c.drawString(100, y, f"ID: {req['id']}")
            y -= 20
            for col in project['columns']:
                c.drawString(120, y, f"{col}: {req[col]}")
                y -= 20
            y -= 20
        c.save()
        output.seek(0)
        return send_file(output, download_name=f"{project['name']}_requirements.pdf", as_attachment=True)
    return redirect(url_for('main.manage_project', project_id=project_id))

@bp.route("/hello")
def hello():
    return "Hello from Blueprint!"
