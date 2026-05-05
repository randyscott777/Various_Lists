# Images App Memory

## Project Overview
Flask app for managing an image list with upload support.

## Created
2026-04-06

## Stack
- Python / Flask
- SQLite3 (raw SQL)
- No JavaScript
- Port: 5009

## Database
- Path: `C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\images_app\images.db`
- Table: `images`
- Fields: id, title, filename, description, category, tags, date_added

## File Uploads
- Stored in: `static/uploads/`
- Allowed: PNG, JPG, JPEG, GIF, WEBP, BMP
- Max size: 16MB

## Features
- Dashboard with image grid, filter by category/tags, sort by any field
- Filter/sort values persisted in Flask session
- File upload on add and replace on edit
- Delete confirmation page removes both DB record and file from disk
- CRUD: add, view, edit, delete

## Notes
- `secure_filename` used for all uploads
- Sort column validated against whitelist to prevent SQL injection
