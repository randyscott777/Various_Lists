import sqlite3

DB_PATH = "C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/chart_of_accounts/chart_of_accounts.db"

accounts = [
    # ── ASSETS (100–199) ──────────────────────────────────────────────
    ("100", "Cash",                               "Asset", "Current Asset",   "Yes"),
    ("110", "Petty Cash",                         "Asset", "Current Asset",   "Yes"),
    ("120", "Accounts Receivable",                "Asset", "Current Asset",   "Yes"),
    ("130", "Allowance for Doubtful Accounts",    "Asset", "Current Asset",   "Yes"),
    ("140", "Inventory",                          "Asset", "Current Asset",   "Yes"),
    ("150", "Prepaid Expenses",                   "Asset", "Current Asset",   "Yes"),
    ("160", "Office Supplies",                    "Asset", "Current Asset",   "Yes"),
    ("170", "Land",                               "Asset", "Fixed Asset",     "Yes"),
    ("180", "Buildings",                          "Asset", "Fixed Asset",     "Yes"),
    ("181", "Accum Depreciation - Buildings",     "Asset", "Fixed Asset",     "Yes"),
    ("190", "Equipment",                          "Asset", "Fixed Asset",     "Yes"),
    ("191", "Accum Depreciation - Equipment",     "Asset", "Fixed Asset",     "Yes"),
    ("195", "Intangible Assets",                  "Asset", "Other Asset",     "Yes"),
    ("199", "Other Assets",                       "Asset", "Other Asset",     "Yes"),

    # ── LIABILITIES (200–299) ─────────────────────────────────────────
    ("200", "Accounts Payable",                   "Liability", "Current Liability",   "Yes"),
    ("210", "Accrued Liabilities",                "Liability", "Current Liability",   "Yes"),
    ("220", "Notes Payable - Short Term",         "Liability", "Current Liability",   "Yes"),
    ("230", "Unearned Revenue",                   "Liability", "Current Liability",   "Yes"),
    ("240", "Income Tax Payable",                 "Liability", "Current Liability",   "Yes"),
    ("250", "Current Portion of Long-Term Debt",  "Liability", "Current Liability",   "Yes"),
    ("260", "Long-Term Notes Payable",            "Liability", "Long-Term Liability", "Yes"),
    ("270", "Mortgage Payable",                   "Liability", "Long-Term Liability", "Yes"),
    ("280", "Deferred Tax Liability",             "Liability", "Long-Term Liability", "Yes"),
    ("299", "Other Liabilities",                  "Liability", "Other Liability",     "Yes"),

    # ── EQUITY (300–399) ──────────────────────────────────────────────
    ("300", "Owner's Capital",                    "Equity", "Owner Equity",       "Yes"),
    ("310", "Owner's Drawings",                   "Equity", "Owner Equity",       "Yes"),
    ("320", "Common Stock",                       "Equity", "Owner Equity",       "Yes"),
    ("330", "Additional Paid-in Capital",         "Equity", "Owner Equity",       "Yes"),
    ("340", "Retained Earnings",                  "Equity", "Retained Earnings",  "Yes"),
    ("350", "Dividends Paid",                     "Equity", "Retained Earnings",  "Yes"),
    ("399", "Other Equity",                       "Equity", "Other Equity",       "Yes"),

    # ── REVENUE (400–499) ─────────────────────────────────────────────
    ("400", "Sales Revenue",                      "Revenue", "Operating Revenue",     "Yes"),
    ("410", "Service Revenue",                    "Revenue", "Operating Revenue",     "Yes"),
    ("420", "Sales Returns & Allowances",         "Revenue", "Operating Revenue",     "Yes"),
    ("430", "Sales Discounts",                    "Revenue", "Operating Revenue",     "Yes"),
    ("450", "Interest Income",                    "Revenue", "Non-Operating Revenue", "Yes"),
    ("460", "Gain on Sale of Assets",             "Revenue", "Non-Operating Revenue", "Yes"),
    ("499", "Other Income",                       "Revenue", "Other Revenue",         "Yes"),

    # ── EXPENSES (500–599) ────────────────────────────────────────────
    ("500", "Cost of Goods Sold",                 "Expense", "Operating Expense",     "Yes"),
    ("510", "Salaries & Wages Expense",           "Expense", "Operating Expense",     "Yes"),
    ("520", "Payroll Tax Expense",                "Expense", "Operating Expense",     "Yes"),
    ("530", "Rent Expense",                       "Expense", "Operating Expense",     "Yes"),
    ("540", "Utilities Expense",                  "Expense", "Operating Expense",     "Yes"),
    ("550", "Office Supplies Expense",            "Expense", "Operating Expense",     "Yes"),
    ("560", "Depreciation Expense",               "Expense", "Operating Expense",     "Yes"),
    ("570", "Insurance Expense",                  "Expense", "Operating Expense",     "Yes"),
    ("575", "Advertising & Marketing Expense",    "Expense", "Operating Expense",     "Yes"),
    ("580", "Professional Fees",                  "Expense", "Operating Expense",     "Yes"),
    ("585", "Repairs & Maintenance Expense",      "Expense", "Operating Expense",     "Yes"),
    ("590", "Interest Expense",                   "Expense", "Non-Operating Expense", "Yes"),
    ("592", "Loss on Sale of Assets",             "Expense", "Non-Operating Expense", "Yes"),
    ("595", "Income Tax Expense",                 "Expense", "Non-Operating Expense", "Yes"),
    ("599", "Other Expenses",                     "Expense", "Other Expense",         "Yes"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    existing = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    if existing > 0:
        print(f"Database already has {existing} account(s). Skipping seed.")
        conn.close()
        return

    conn.executemany("""
        INSERT INTO accounts (account_number, account_name, account_type, account_subtype, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, accounts)
    conn.commit()
    print(f"Seeded {len(accounts)} accounts.")
    conn.close()


if __name__ == "__main__":
    seed()
