import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = "C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/chart_of_accounts/chart_of_accounts.db"

ACCOUNT_TYPES = ["Asset", "Liability", "Equity", "Revenue", "Expense"]
ACCOUNT_SUBTYPES = {
    "Asset": ["Current Asset", "Fixed Asset", "Other Asset"],
    "Liability": ["Current Liability", "Long-Term Liability", "Other Liability"],
    "Equity": ["Owner Equity", "Retained Earnings", "Other Equity"],
    "Revenue": ["Operating Revenue", "Non-Operating Revenue", "Other Revenue"],
    "Expense": ["Operating Expense", "Non-Operating Expense", "Other Expense"],
}
ALL_SUBTYPES = sorted(set(s for subs in ACCOUNT_SUBTYPES.values() for s in subs))
ACTIVE_OPTIONS = ["Yes", "No"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT NOT NULL,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            account_subtype TEXT NOT NULL,
            is_active TEXT NOT NULL DEFAULT 'Yes'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ui_prefs (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            filter_type TEXT DEFAULT '',
            filter_subtype TEXT DEFAULT '',
            filter_active TEXT DEFAULT '',
            sort_field TEXT DEFAULT 'account_number',
            sort_dir TEXT DEFAULT 'asc'
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO ui_prefs (id, filter_type, filter_subtype, filter_active, sort_field, sort_dir)
        VALUES (1, '', '', '', 'account_number', 'asc')
    """)
    conn.commit()
    conn.close()


def get_prefs():
    conn = get_db()
    prefs = conn.execute("SELECT * FROM ui_prefs WHERE id = 1").fetchone()
    conn.close()
    return prefs


def save_prefs(filter_type, filter_subtype, filter_active, sort_field, sort_dir):
    conn = get_db()
    conn.execute("""
        UPDATE ui_prefs SET filter_type=?, filter_subtype=?, filter_active=?, sort_field=?, sort_dir=?
        WHERE id=1
    """, (filter_type, filter_subtype, filter_active, sort_field, sort_dir))
    conn.commit()
    conn.close()


VALID_SORT_FIELDS = ["account_number", "account_name", "account_type", "account_subtype", "is_active"]


@app.route("/", methods=["GET", "POST"])
def index():
    prefs = get_prefs()

    if request.method == "POST":
        filter_type = request.form.get("filter_type", "")
        filter_subtype = request.form.get("filter_subtype", "")
        filter_active = request.form.get("filter_active", "")
        sort_field = request.form.get("sort_field", "account_number")
        sort_dir = request.form.get("sort_dir", "asc")
    else:
        filter_type = prefs["filter_type"]
        filter_subtype = prefs["filter_subtype"]
        filter_active = prefs["filter_active"]
        sort_field = prefs["sort_field"]
        sort_dir = prefs["sort_dir"]

    if sort_field not in VALID_SORT_FIELDS:
        sort_field = "account_number"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "asc"

    save_prefs(filter_type, filter_subtype, filter_active, sort_field, sort_dir)

    query = "SELECT * FROM accounts WHERE 1=1"
    params = []
    if filter_type:
        query += " AND account_type = ?"
        params.append(filter_type)
    if filter_subtype:
        query += " AND account_subtype = ?"
        params.append(filter_subtype)
    if filter_active:
        query += " AND is_active = ?"
        params.append(filter_active)

    query += f" ORDER BY {sort_field} {sort_dir.upper()}"

    conn = get_db()
    accounts = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("index.html",
        accounts=accounts,
        account_types=ACCOUNT_TYPES,
        all_subtypes=ALL_SUBTYPES,
        active_options=ACTIVE_OPTIONS,
        filter_type=filter_type,
        filter_subtype=filter_subtype,
        filter_active=filter_active,
        sort_field=sort_field,
        sort_dir=sort_dir,
        valid_sort_fields=VALID_SORT_FIELDS,
    )


@app.route("/clear")
def clear():
    save_prefs("", "", "", "account_number", "asc")
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        account_number = request.form["account_number"].strip()
        account_name = request.form["account_name"].strip()
        account_type = request.form["account_type"]
        account_subtype = request.form["account_subtype"]
        is_active = request.form["is_active"]

        conn = get_db()
        conn.execute("""
            INSERT INTO accounts (account_number, account_name, account_type, account_subtype, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (account_number, account_name, account_type, account_subtype, is_active))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html",
        account_types=ACCOUNT_TYPES,
        account_subtypes=ACCOUNT_SUBTYPES,
        active_options=ACTIVE_OPTIONS,
    )


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not account:
        return redirect(url_for("index"))

    if request.method == "POST":
        account_number = request.form["account_number"].strip()
        account_name = request.form["account_name"].strip()
        account_type = request.form["account_type"]
        account_subtype = request.form["account_subtype"]
        is_active = request.form["is_active"]

        conn = get_db()
        conn.execute("""
            UPDATE accounts SET account_number=?, account_name=?, account_type=?, account_subtype=?, is_active=?
            WHERE id=?
        """, (account_number, account_name, account_type, account_subtype, is_active, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("edit.html",
        account=account,
        account_types=ACCOUNT_TYPES,
        account_subtypes=ACCOUNT_SUBTYPES,
        active_options=ACTIVE_OPTIONS,
    )


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    conn = get_db()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not account:
        return redirect(url_for("index"))

    if request.method == "POST":
        conn = get_db()
        conn.execute("DELETE FROM accounts WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("delete.html", account=account)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
