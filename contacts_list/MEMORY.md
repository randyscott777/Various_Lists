# Contacts App - Memory

## Project Overview
Flask-based contacts manager with SQLite3 persistence.

## Tech Stack
- Python / Flask
- SQLite3 (raw SQL, `contacts.db` in app root)
- Jinja2 templates, no JavaScript
- CSS in `static/style.css`

## Fields
`id`, `first_name`, `last_name`, `email`, `phone`, `company`, `address`, `city`, `state`, `zip`, `notes`

## Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET/POST | Dashboard with filter/sort |
| `/add` | GET/POST | Add new contact |
| `/view/<id>` | GET | View contact detail |
| `/edit/<id>` | GET/POST | Edit contact |
| `/delete/<id>` | GET/POST | Delete confirmation + delete |

## Features
- Filter persisted in session (name, company, city, email, phone)
- Sort persisted in session (any of 6 fields, asc/desc)
- Delete requires confirmation page
- Created: 2026-04-06
