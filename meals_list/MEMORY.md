# Meals App — Memory

## Purpose
Flask app for managing a list of meals, each with sub-items for ingredients.

## Stack
- Python / Flask
- SQLite3 (raw SQL) — `meals.db` in the app folder
- No JavaScript
- All CSS in `static/style.css`

## Database
- `meals` — id, name, description, created_at
- `ingredients` — id, meal_id, name, quantity, unit, created_at

## Routes
| Route | Purpose |
|---|---|
| `GET /` | Dashboard with filter (name) and sort (name, created_at) |
| `GET/POST /meal/add` | Add meal |
| `GET /meal/<id>` | View meal + ingredients table |
| `GET/POST /meal/<id>/edit` | Edit meal |
| `GET/POST /meal/<id>/delete` | Confirm + delete meal (cascades ingredients) |
| `GET/POST /meal/<id>/ingredient/add` | Add ingredient |
| `GET/POST /ingredient/<id>/edit` | Edit ingredient |
| `GET/POST /ingredient/<id>/delete` | Confirm + delete ingredient |

## Notes
- Filter and sort values are persisted via Flask session
- Delete always shows a confirmation page before acting
