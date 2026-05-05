# Chart of Accounts (New)

## Stack
Python / Flask · SQLite3 (raw SQL) · Jinja2 · CSS only (no JS) · Port 5051

## DB Path
`C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/chart_of_accounts_new/chart_of_accounts.db`

## Schema
**accounts** — id, account_number (TEXT UNIQUE 3-digit), account_name, account_type, account_subtype, is_active (Yes/No)  
**ui_prefs** — single row (id=1): filter_type, filter_subtype, filter_active, sort_field, sort_dir

## Account Types / Ranges
- Asset 100–199 · Liability 200–299 · Equity 300–399 · Revenue 400–499 · Expense 500–599

## Routes
- `GET/POST /` — dashboard: stats, sticky filter bar, accounts table
- `GET /clear` — reset filter/sort prefs
- `POST /toggle/<id>` — flip is_active Yes↔No inline
- `GET/POST /add` — create account
- `GET/POST /edit/<id>` — update account
- `GET /delete/<id>` — confirm delete page
- `POST /delete/<id>/confirm` — execute delete

## Color Scheme
Asset=green #10b981 · Liability=red #ef4444 · Equity=purple #8b5cf6  
Revenue=blue #3b82f6 · Expense=amber #f59e0b · Header gradient #667eea→#764ba2

## Seed Data
62 standard accounts seeded automatically on first run.
