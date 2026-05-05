# Contacts List New — Memory

## Overview
Flask contacts manager with vibrant Monday.com-style UI, stats dashboard, filter/sort persisted in DB, favorites, archive/restore, and confirm-before-delete.

## Tech Stack
- Python / Flask, SQLite3 (raw SQL), Jinja2, no JavaScript
- Port: 5053

## Schema

### contacts
`id`, `first_name`, `last_name`, `email`, `phone`, `company`, `contact_type` (Friend/Family/Work/Acquaintance/Other), `favorite` (0/1), `active` (0/1), `address`, `city`, `state`, `zip`, `notes`, `created_date`, `updated_at`

### ui_prefs (single row id=1)
`filter_contact_type`, `sort_field`, `sort_dir` — persists filter/sort across sessions

## Routes
| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/` | Index: list + filter + sort |
| GET | `/clear` | Reset filter/sort prefs |
| GET/POST | `/add` | Add contact |
| GET/POST | `/edit/<id>` | Edit contact |
| GET | `/view/<id>` | Detail view |
| POST | `/toggle_favorite/<id>` | Toggle ★ favorite |
| POST | `/toggle_active/<id>` | Archive / restore |
| GET | `/delete/<id>` | Confirm delete page |
| POST | `/delete/<id>/confirm` | Hard delete |

## UI Features
- 6 tinted stat cards with progress bars (Total, Favorites, Active, Archived, Work, Family)
- Left-border color keyed to contact_type (green=Friend, purple=Family, blue=Work, amber=Acquaintance, gray=Other)
- Archived rows: opacity 0.55 + strikethrough on name
- Star button (★) — one-click favorite toggle via form POST
- Archive/restore button per row
- Sticky filter bar and sticky thead
- Colorful edit (amber) / delete (red) / archive (purple) buttons
- Empty state: pure-CSS avatar illustration + CTA
- Gradient header (teal → purple), tinted body background
- Footer with last_updated timestamp on every page
