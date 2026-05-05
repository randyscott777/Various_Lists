# Projects App — Memory

## App Overview
3-level hierarchical project manager built with Flask + SQLite3.

## Hierarchy
- **Level 1 — Projects**: name, description, status, priority, due_date
- **Level 2 — Tasks**: belong to a project; name, description, status, priority, due_date
- **Level 3 — Sub-tasks**: belong to a task; name, description, status, due_date

## Status Values
Not Started (gray), In Progress (blue), Done (green), Blocked (red), On Hold (yellow)

## Priority Values
Low (teal), Medium (orange), High (purple)

## Database
- File: `projects.db` in the app folder
- Tables: `projects`, `tasks`, `subtasks`
- Cascade deletes handled in Python (delete subtasks → tasks → project)

## Files
- `app.py` — Flask routes and DB init
- `projects.db` — SQLite3 database (auto-created on first run)
- `static/style.css` — all styling
- `templates/index.html` — project dashboard with filter/sort
- `templates/tasks.html` — task list for a project
- `templates/subtasks.html` — sub-task list for a task
- `templates/project_form.html`, `task_form.html`, `subtask_form.html` — CRUD forms
- `templates/confirm_delete.html` — shared delete confirmation

## Running
```
cd projects_app
python app.py
```
Visit http://127.0.0.1:5000
