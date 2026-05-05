# Bucket List App — Memory

## Overview
Flask app for managing a personal bucket list.
Port: 5020
DB: bucket_list.db (SQLite3, same folder as app.py)

## Fields
- title, category, priority, status, description, target_date, completed_date, notes, created_at

## Dropdown Values
- **Categories:** Travel, Adventure, Learning, Career, Family, Health, Creative, Other
- **Priorities:** High, Medium, Low
- **Statuses:** Not Started, In Progress, Completed, Abandoned

## Features
- Dashboard with stats (total, not started, in progress, completed, % complete)
- Filter by category / priority / status — persisted across sessions via user_prefs table
- Sort by any field, ascending or descending — also persisted
- Full CRUD with delete confirmation prompt
- Dark theme, Monday.com-style colored badges
