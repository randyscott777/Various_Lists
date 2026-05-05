import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = "C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/chart_of_accounts_new/chart_of_accounts.db"

ACCOUNT_TYPES = ["Asset", "Liability", "Equity", "Revenue", "Expense"]
ACCOUNT_SUBTYPES = {
    "Asset":     ["Current Asset", "Fixed Asset", "Other Asset"],
    "Liability": ["Current Liability", "Long-Term Liability", "Other Liability"],
    "Equity":    ["Owner Equity", "Retained Earnings", "Other Equity"],
    "Revenue":   ["Operating Revenue", "Non-Operating Revenue", "Other Revenue"],
    "Expense":   ["Operating Expense", "Non-Operating Expense", "Other Expense"],
}
ALL_SUBTYPES = sorted(set(s for subs in ACCOUNT_SUBTYPES.values() for s in subs))
VALID_SORT_FIELDS = ["account_number", "account_name", "account_type", "account_subtype", "is_active"]
SORT_LABELS = {
    "account_number": "Account #",
    "account_name":   "Name",
    "account_type":   "Type",
    "account_subtype": "Subtype",
    "is_active":      "Active",
}

SEED_DATA = [
    # ── ASSETS (100–199) ────────────────────────────────────────────────
    ("100", "Cash - Checking",                  "Asset", "Current Asset",   "Yes"),
    ("101", "Cash - Savings",                   "Asset", "Current Asset",   "Yes"),
    ("110", "Petty Cash",                       "Asset", "Current Asset",   "Yes"),
    ("120", "Accounts Receivable",              "Asset", "Current Asset",   "Yes"),
    ("125", "Allowance for Doubtful Accounts",  "Asset", "Current Asset",   "Yes"),
    ("130", "Inventory",                        "Asset", "Current Asset",   "Yes"),
    ("140", "Prepaid Insurance",                "Asset", "Current Asset",   "Yes"),
    ("145", "Prepaid Rent",                     "Asset", "Current Asset",   "Yes"),
    ("150", "Office Supplies",                  "Asset", "Current Asset",   "Yes"),
    ("160", "Land",                             "Asset", "Fixed Asset",     "Yes"),
    ("165", "Buildings",                        "Asset", "Fixed Asset",     "Yes"),
    ("166", "Accum Depreciation - Buildings",   "Asset", "Fixed Asset",     "Yes"),
    ("170", "Equipment",                        "Asset", "Fixed Asset",     "Yes"),
    ("171", "Accum Depreciation - Equipment",   "Asset", "Fixed Asset",     "Yes"),
    ("175", "Vehicles",                         "Asset", "Fixed Asset",     "Yes"),
    ("176", "Accum Depreciation - Vehicles",    "Asset", "Fixed Asset",     "Yes"),
    ("180", "Furniture & Fixtures",             "Asset", "Fixed Asset",     "Yes"),
    ("190", "Security Deposits",                "Asset", "Other Asset",     "Yes"),
    ("195", "Intangible Assets",                "Asset", "Other Asset",     "Yes"),
    ("199", "Other Assets",                     "Asset", "Other Asset",     "Yes"),
    # ── LIABILITIES (200–299) ────────────────────────────────────────────
    ("200", "Accounts Payable",                 "Liability", "Current Liability",   "Yes"),
    ("205", "Credit Cards Payable",             "Liability", "Current Liability",   "Yes"),
    ("210", "Accrued Wages Payable",            "Liability", "Current Liability",   "Yes"),
    ("215", "Payroll Taxes Payable",            "Liability", "Current Liability",   "Yes"),
    ("220", "Sales Tax Payable",                "Liability", "Current Liability",   "Yes"),
    ("225", "Income Tax Payable",               "Liability", "Current Liability",   "Yes"),
    ("230", "Unearned Revenue",                 "Liability", "Current Liability",   "Yes"),
    ("240", "Notes Payable - Short Term",       "Liability", "Current Liability",   "Yes"),
    ("260", "Notes Payable - Long Term",        "Liability", "Long-Term Liability", "Yes"),
    ("265", "Mortgage Payable",                 "Liability", "Long-Term Liability", "Yes"),
    ("270", "Deferred Tax Liability",           "Liability", "Long-Term Liability", "Yes"),
    ("299", "Other Liabilities",                "Liability", "Other Liability",     "Yes"),
    # ── EQUITY (300–399) ─────────────────────────────────────────────────
    ("300", "Owner's Capital",                  "Equity", "Owner Equity",      "Yes"),
    ("310", "Owner's Drawings",                 "Equity", "Owner Equity",      "Yes"),
    ("320", "Common Stock",                     "Equity", "Owner Equity",      "Yes"),
    ("330", "Additional Paid-in Capital",       "Equity", "Owner Equity",      "Yes"),
    ("340", "Retained Earnings",                "Equity", "Retained Earnings", "Yes"),
    ("350", "Dividends Paid",                   "Equity", "Retained Earnings", "Yes"),
    ("399", "Other Equity",                     "Equity", "Other Equity",      "Yes"),
    # ── REVENUE (400–499) ────────────────────────────────────────────────
    ("400", "Sales Revenue",                    "Revenue", "Operating Revenue",     "Yes"),
    ("410", "Service Revenue",                  "Revenue", "Operating Revenue",     "Yes"),
    ("415", "Sales Returns & Allowances",       "Revenue", "Operating Revenue",     "Yes"),
    ("420", "Sales Discounts",                  "Revenue", "Operating Revenue",     "Yes"),
    ("450", "Interest Income",                  "Revenue", "Non-Operating Revenue", "Yes"),
    ("460", "Rental Income",                    "Revenue", "Non-Operating Revenue", "Yes"),
    ("465", "Gain on Sale of Assets",           "Revenue", "Non-Operating Revenue", "Yes"),
    ("499", "Other Income",                     "Revenue", "Other Revenue",         "Yes"),
    # ── EXPENSES (500–599) ───────────────────────────────────────────────
    ("500", "Cost of Goods Sold",               "Expense", "Operating Expense",     "Yes"),
    ("510", "Salaries & Wages",                 "Expense", "Operating Expense",     "Yes"),
    ("515", "Payroll Tax Expense",              "Expense", "Operating Expense",     "Yes"),
    ("520", "Employee Benefits",                "Expense", "Operating Expense",     "Yes"),
    ("525", "Rent Expense",                     "Expense", "Operating Expense",     "Yes"),
    ("530", "Utilities Expense",                "Expense", "Operating Expense",     "Yes"),
    ("535", "Office Supplies Expense",          "Expense", "Operating Expense",     "Yes"),
    ("540", "Depreciation Expense",             "Expense", "Operating Expense",     "Yes"),
    ("545", "Insurance Expense",                "Expense", "Operating Expense",     "Yes"),
    ("550", "Advertising & Marketing",          "Expense", "Operating Expense",     "Yes"),
    ("555", "Professional Fees",                "Expense", "Operating Expense",     "Yes"),
    ("560", "Repairs & Maintenance",            "Expense", "Operating Expense",     "Yes"),
    ("565", "Travel & Entertainment",           "Expense", "Operating Expense",     "Yes"),
    ("570", "Vehicle Expense",                  "Expense", "Operating Expense",     "Yes"),
    ("575", "Telephone & Internet",             "Expense", "Operating Expense",     "Yes"),
    ("580", "Bank Charges & Fees",              "Expense", "Operating Expense",     "Yes"),
    ("590", "Interest Expense",                 "Expense", "Non-Operating Expense", "Yes"),
    ("592", "Loss on Sale of Assets",           "Expense", "Non-Operating Expense", "Yes"),
    ("595", "Income Tax Expense",               "Expense", "Non-Operating Expense", "Yes"),
    ("599", "Other Expenses",                   "Expense", "Other Expense",         "Yes"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT    NOT NULL UNIQUE,
            account_name   TEXT    NOT NULL,
            account_type   TEXT    NOT NULL,
            account_subtype TEXT   NOT NULL,
            is_active      TEXT    NOT NULL DEFAULT 'Yes'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ui_prefs (
            id              INTEGER PRIMARY KEY CHECK (id = 1),
            filter_type     TEXT DEFAULT '',
            filter_subtype  TEXT DEFAULT '',
            filter_active   TEXT DEFAULT '',
            sort_field      TEXT DEFAULT 'account_number',
            sort_dir        TEXT DEFAULT 'asc'
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO ui_prefs
            (id, filter_type, filter_subtype, filter_active, sort_field, sort_dir)
        VALUES (1, '', '', '', 'account_number', 'asc')
    """)
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
        conn.executemany("""
            INSERT INTO accounts (account_number, account_name, account_type, account_subtype, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, SEED_DATA)
        conn.commit()
    conn.close()


def get_prefs():
    conn = get_db()
    row = conn.execute("SELECT * FROM ui_prefs WHERE id = 1").fetchone()
    conn.close()
    return row


def save_prefs(ft, fs, fa, sf, sd):
    conn = get_db()
    conn.execute("""
        UPDATE ui_prefs
        SET filter_type=?, filter_subtype=?, filter_active=?, sort_field=?, sort_dir=?
        WHERE id = 1
    """, (ft, fs, fa, sf, sd))
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    prefs = get_prefs()
    if request.method == "POST":
        ft = request.form.get("filter_type", "")
        fs = request.form.get("filter_subtype", "")
        fa = request.form.get("filter_active", "")
        sf = request.form.get("sort_field", "account_number")
        sd = request.form.get("sort_dir", "asc")
        save_prefs(ft, fs, fa, sf, sd)
    else:
        ft = prefs["filter_type"]
        fs = prefs["filter_subtype"]
        fa = prefs["filter_active"]
        sf = prefs["sort_field"]
        sd = prefs["sort_dir"]

    if sf not in VALID_SORT_FIELDS:
        sf = "account_number"
    if sd not in ("asc", "desc"):
        sd = "asc"

    query = "SELECT * FROM accounts WHERE 1=1"
    params = []
    if ft:
        query += " AND account_type = ?"
        params.append(ft)
    if fs:
        query += " AND account_subtype = ?"
        params.append(fs)
    if fa:
        query += " AND is_active = ?"
        params.append(fa)
    query += f" ORDER BY {sf} {sd.upper()}"

    conn = get_db()
    accounts = conn.execute(query, params).fetchall()
    all_rows = conn.execute("SELECT account_type, is_active FROM accounts").fetchall()
    conn.close()

    total    = len(all_rows)
    active   = sum(1 for r in all_rows if r["is_active"] == "Yes")
    inactive = total - active
    by_type  = {t: sum(1 for r in all_rows if r["account_type"] == t) for t in ACCOUNT_TYPES}

    return render_template("index.html",
        accounts=accounts,
        account_types=ACCOUNT_TYPES,
        all_subtypes=ALL_SUBTYPES,
        sort_labels=SORT_LABELS,
        valid_sort_fields=VALID_SORT_FIELDS,
        filter_type=ft, filter_subtype=fs, filter_active=fa,
        sort_field=sf, sort_dir=sd,
        total=total, active=active, inactive=inactive, by_type=by_type,
    )


@app.route("/clear")
def clear():
    save_prefs("", "", "", "account_number", "asc")
    return redirect(url_for("index"))


@app.route("/toggle/<int:id>", methods=["POST"])
def toggle(id):
    conn = get_db()
    row = conn.execute("SELECT is_active FROM accounts WHERE id = ?", (id,)).fetchone()
    if row:
        new_val = "No" if row["is_active"] == "Yes" else "Yes"
        conn.execute("UPDATE accounts SET is_active = ? WHERE id = ?", (new_val, id))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add():
    error = None
    if request.method == "POST":
        num     = request.form["account_number"].strip()
        name    = request.form["account_name"].strip()
        atype   = request.form["account_type"]
        subtype = request.form["account_subtype"]
        active  = request.form.get("is_active", "Yes")
        if not num or not name:
            error = "Account number and name are required."
        else:
            try:
                conn = get_db()
                conn.execute("""
                    INSERT INTO accounts (account_number, account_name, account_type, account_subtype, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (num, name, atype, subtype, active))
                conn.commit()
                conn.close()
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                error = f"Account number {num} already exists."
    return render_template("add.html",
        account_types=ACCOUNT_TYPES,
        account_subtypes=ACCOUNT_SUBTYPES,
        error=error,
    )


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not account:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        num     = request.form["account_number"].strip()
        name    = request.form["account_name"].strip()
        atype   = request.form["account_type"]
        subtype = request.form["account_subtype"]
        active  = request.form.get("is_active", "Yes")
        if not num or not name:
            error = "Account number and name are required."
        else:
            try:
                conn = get_db()
                conn.execute("""
                    UPDATE accounts
                    SET account_number=?, account_name=?, account_type=?,
                        account_subtype=?, is_active=?
                    WHERE id = ?
                """, (num, name, atype, subtype, active, id))
                conn.commit()
                conn.close()
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                error = f"Account number {num} already exists."
    return render_template("edit.html",
        account=account,
        account_types=ACCOUNT_TYPES,
        account_subtypes=ACCOUNT_SUBTYPES,
        error=error,
    )


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not account:
        return redirect(url_for("index"))
    return render_template("confirm_delete.html", account=account)


@app.route("/delete/<int:id>/confirm", methods=["POST"])
def delete_confirm(id):
    conn = get_db()
    conn.execute("DELETE FROM accounts WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5051)
