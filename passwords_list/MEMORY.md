# Password Manager — Project Memory

## App Overview
Flask web app for storing and managing passwords locally.
- **Port:** 5010
- **Database:** `passwords.db` (SQLite3, same folder as app.py)
- **No JavaScript** — pure Flask/HTML/CSS

## Database Tables
- `passwords` — id, site_name, url, username, password, category, notes, created_at, updated_at
- `filter_sort_state` — persists dashboard filter (category) and sort (field + direction)

## Categories
Personal, Work, Finance, Social, Email, Shopping, Entertainment, Other

## Routes
| Route | Purpose |
|-------|---------|
| GET/POST `/` | Dashboard with filter + sort |
| GET/POST `/add` | Add new password |
| GET `/view/<id>` | View full entry (password visible) |
| GET/POST `/edit/<id>` | Edit entry |
| GET/POST `/delete/<id>` | Confirm + delete |

## Files
```
passwords/
├── app.py
├── passwords.db         (auto-created on first run)
├── MEMORY.md
├── static/style.css
└── templates/
    ├── index.html
    ├── add.html
    ├── view.html
    ├── edit.html
    └── delete_confirm.html
```

## Notes
- Password is shown masked (••••••••) on dashboard; visible only on view.html
- Delete requires confirmation (prompted on delete_confirm.html)
- Filter/sort state persisted in DB (filter_sort_state table)
- Created: 2026-04-06
