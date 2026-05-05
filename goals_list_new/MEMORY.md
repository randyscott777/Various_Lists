# Goals List New

## Stack
Python / Flask · SQLite3 (raw SQL) · Jinja2 · CSS only (no JS) · Port 5052

## DB Path
`C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/goals_list_new/goals.db`

## Schema
**goals** — id, title, description, category, priority, status, due_date, created_date, updated_at  
**ui_prefs** — single row (id=1): filter_category, filter_status, filter_priority, sort_field, sort_dir

## Values
- Categories: Personal, Career, Health, Financial, Education, Other
- Priorities: Low, Medium, High, Urgent
- Statuses: Not Started, In Progress, On Hold, Completed

## Routes
- `GET/POST /` — dashboard with stats, sticky filter bar, goals table
- `GET /clear` — reset filter/sort prefs
- `POST /toggle/<id>` — inline status update from select dropdown
- `POST /done/<id>` — quick-done toggle (Completed ↔ Not Started)
- `GET/POST /add` — create goal
- `GET/POST /edit/<id>` — update goal
- `GET /delete/<id>` — confirm delete page
- `POST /delete/<id>/confirm` — execute delete

## Color Scheme
Priority borders: Low=green · Medium=blue · High=orange · Urgent=red  
Status chips: Not Started=gray · In Progress=blue · On Hold=amber · Completed=green  
Category chips: Personal=purple · Career=cyan · Health=green · Financial=amber · Education=blue · Other=gray  
Header gradient: #4f46e5 → #7c3aed

## Seed Data
17 sample goals seeded automatically on first run across all 6 categories.

## Footer
Every page shows "Last updated: [date]" via Flask context_processor querying MAX(updated_at).
