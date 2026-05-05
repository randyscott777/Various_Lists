# Spiritual Journal App

## Overview
Flask web app for tracking a personal spiritual journey.

## Fields
- **Title** — text, required
- **Category** — dropdown (Meditation, Prayer, Study, Retreat, Practice, Pilgrimage, Service, Reflection)
- **Notes** — textarea, optional

## Tech Stack
- Python / Flask
- SQLite3 (raw SQL)
- No JavaScript

## Files
- `app.py` — main Flask app with routes
- `spiritual_journal.db` — SQLite database (auto-created on first run)
- `templates/base.html` — shared layout
- `templates/index.html` — dashboard with filter + sort (persisted in session)
- `templates/add.html` — add new entry
- `templates/edit.html` — edit existing entry
- `templates/confirm_delete.html` — delete confirmation
- `static/style.css` — all styling

## Notes
- Filter by Category and Sort by any field persisted in Flask session
- Category badges are colored rectangles with white text (Monday.com style)
- Delete always requires confirmation
