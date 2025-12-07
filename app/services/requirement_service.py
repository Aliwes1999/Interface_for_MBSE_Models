from flask import flash, redirect, url_for
from flask_login import current_user
from .. import db
from ..models import Requirement, RequirementVersion
from .ai_client import generate_requirements

def regenerate_requirement(req_id):
    """Regenerate a single requirement with AI."""
    req = Requirement.query.get_or_404(req_id)
    # Authorization check
    if req.project.user_id != current_user.id:
        from flask import abort
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
