# Project Manager — Memory

## App Overview
Single-user project management app. Flask + SQLite3 + Bootstrap 5. No JavaScript.

## Data Model
- **projects**: id, name, description, created_date
- **tasks**: id, project_id, title, description, status, priority, due_date, created_date

## Status values: To Do | In Progress | Done
## Priority values: Low | Medium | High

## Routes
- `/projects` — list all projects
- `/projects/new` — create project
- `/projects/<id>/edit` — edit project
- `/projects/<id>/delete` — delete project (confirm page)
- `/projects/<id>/tasks` — list tasks (supports ?status=&priority=&sort=)
- `/projects/<id>/tasks/new` — create task
- `/projects/<id>/tasks/<tid>/edit` — edit task
- `/projects/<id>/tasks/<tid>/delete` — delete task (confirm page)

## Design Decisions
- No authentication (single user)
- No subtasks (two-level hierarchy only)
- List view only (no kanban — avoids JS)
- Filter + sort via URL query params
