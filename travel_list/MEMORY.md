# Travel Plans App — Memory

## Overview
Flask web app for managing personal travel plans with full CRUD operations.

## Stack
- Python / Flask
- SQLite3 (raw SQL, `travel.db` in app root)
- Jinja2 templates, no JavaScript
- All styles in `static/style.css`

## Database: `travel_plans`
| Column      | Type      | Notes                                      |
|-------------|-----------|--------------------------------------------|
| id          | INTEGER   | Primary key, auto-increment                |
| destination | TEXT      | Required                                   |
| start_date  | DATE      |                                            |
| end_date    | DATE      |                                            |
| travelers   | INTEGER   | Default 1                                  |
| status      | TEXT      | Planned / Booked / In Progress / Completed / Cancelled |
| budget      | REAL      | Default 0.0                                |
| notes       | TEXT      |                                            |
| created_at  | TIMESTAMP | Auto-set on insert                         |

## Routes
| Route              | Method    | Purpose                        |
|--------------------|-----------|--------------------------------|
| /                  | GET       | Dashboard + filter/sort        |
| /add               | GET/POST  | Add new trip                   |
| /edit/<id>         | GET/POST  | Edit trip (confirm key changes)|
| /delete/<id>       | GET/POST  | Delete trip (confirm prompt)   |

## Features
- Dashboard summary cards by status
- Filter by destination (partial match) and status
- Sort by any field, ASC or DESC (persisted in query params)
- Confirmation prompt on delete and on key field changes (destination, dates, status)

## Created
2026-04-06
