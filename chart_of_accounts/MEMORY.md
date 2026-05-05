# Chart of Accounts App

## Overview
Flask web app for managing a chart of accounts. No JavaScript.

## Stack
- Python / Flask
- SQLite3 (raw SQL) — `chart_of_accounts.db` in app folder
- Jinja2 templates
- CSS only (no JS)

## Fields
- account_number, account_name, account_type, account_subtype, is_active

## Account Types
Asset, Liability, Equity, Revenue, Expense

## Subtypes (grouped by type)
- Asset: Current Asset, Fixed Asset, Other Asset
- Liability: Current Liability, Long-Term Liability, Other Liability
- Equity: Owner Equity, Retained Earnings, Other Equity
- Revenue: Operating Revenue, Non-Operating Revenue, Other Revenue
- Expense: Operating Expense, Non-Operating Expense, Other Expense

## Routes
- `/` — dashboard with filter + sort (persisted in DB)
- `/clear` — reset filter/sort prefs
- `/add` — create account
- `/edit/<id>` — update account
- `/delete/<id>` — delete with confirmation

## Run
```
python app.py
```
Runs on port 5050.
