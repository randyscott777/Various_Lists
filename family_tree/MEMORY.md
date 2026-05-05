# Family Tree App

## Stack
- Python / Flask
- SQLite3 (raw SQL)
- Bootstrap 5 (CDN, CSS only)
- No JavaScript

## Database: family_tree.db
Single table: `people`
- id, first_name, last_name, birth_date, death_date, gender, notes
- father_id, mother_id, spouse_id (all nullable FK → people.id)

## Tree Logic
- Each person stored under their father in the tree; if no father, under mother
- Roots = people with no father_id AND no mother_id in the DB
- Multiple roots supported (separate family branches)
- Spouse displayed inline next to person in tree view

## Routes
| Route | Purpose |
|-------|---------|
| GET / | Tree view (nested list) |
| GET/POST /person/add | Add person |
| GET /person/<id> | Detail view |
| GET/POST /person/<id>/edit | Edit person |
| GET/POST /person/<id>/delete | Delete with confirmation |

## Delete Behavior
- Nullifies father_id, mother_id, spouse_id references before deleting
- Spouse link is bidirectional — updated on add/edit/delete

## Design Decisions
- Jinja2 recursive macro for tree rendering (no JS required)
- Confirmation page required before delete
