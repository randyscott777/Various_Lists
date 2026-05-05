# Prescriptions List - Memory

## Overview
Flask app to track personal prescriptions with CRUD operations.

## Stack
- Python / Flask
- SQLite3 (raw SQL)
- No JavaScript

## Database
- Path: `C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\prescriptions_list\prescriptions_list.db`
- Tables: `prescriptions`, `preferences`

## Fields
- medication_name, dosage, frequency, prescribing_doctor, pharmacy, refill_date, status, notes

## Dropdowns
- **Frequency:** Once Daily, Twice Daily, Three Times Daily, As Needed, Weekly
- **Status:** Active, Inactive, Discontinued

## Features
- Dashboard with counts by status
- Filter by status and frequency
- Sort on any field (persisted via preferences table)
- Full CRUD with delete confirmation
