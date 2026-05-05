from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'passwords.db')

CATEGORIES = [
    "Personal", "Work", "Finance", "Social",
    "Email", "Shopping", "Entertainment", "Other"
]

SORT_FIELDS = {
    "site_name": "Site",
    "username": "Username",
    "category": "Category",
    "created_at": "Date Added",
    "updated_at": "Last Updated"
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL,
            url TEXT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            category TEXT DEFAULT 'Personal',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS filter_sort_state (
            id INTEGER PRIMARY KEY DEFAULT 1,
            filter_category TEXT DEFAULT '',
            sort_field TEXT DEFAULT 'site_name',
            sort_direction TEXT DEFAULT 'ASC'
        )
    """)
    cur.execute("SELECT COUNT(*) FROM filter_sort_state")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO filter_sort_state (id, filter_category, sort_field, sort_direction)
            VALUES (1, '', 'site_name', 'ASC')
        """)
    conn.commit()
    conn.close()


def get_state():
    conn = get_db()
    state = conn.execute("SELECT * FROM filter_sort_state WHERE id = 1").fetchone()
    conn.close()
    return state


def save_state(filter_category, sort_field, sort_direction):
    conn = get_db()
    conn.execute("""
        UPDATE filter_sort_state
        SET filter_category = ?, sort_field = ?, sort_direction = ?
        WHERE id = 1
    """, (filter_category, sort_field, sort_direction))
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        filter_category = request.form.get("filter_category", "")
        sort_field = request.form.get("sort_field", "site_name")
        sort_direction = request.form.get("sort_direction", "ASC")
        if sort_field not in SORT_FIELDS:
            sort_field = "site_name"
        if sort_direction not in ("ASC", "DESC"):
            sort_direction = "ASC"
        save_state(filter_category, sort_field, sort_direction)
        return redirect(url_for("index"))

    state = get_state()
    filter_category = state["filter_category"]
    sort_field = state["sort_field"]
    sort_direction = state["sort_direction"]

    conn = get_db()
    if filter_category:
        rows = conn.execute(
            f"SELECT * FROM passwords WHERE category = ? ORDER BY {sort_field} {sort_direction}",
            (filter_category,)
        ).fetchall()
    else:
        rows = conn.execute(
            f"SELECT * FROM passwords ORDER BY {sort_field} {sort_direction}"
        ).fetchall()
    conn.close()

    return render_template("index.html",
        passwords=rows,
        categories=CATEGORIES,
        sort_fields=SORT_FIELDS,
        filter_category=filter_category,
        sort_field=sort_field,
        sort_direction=sort_direction,
        total=len(rows)
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        site_name = request.form.get("site_name", "").strip()
        url = request.form.get("url", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        category = request.form.get("category", "Personal")
        notes = request.form.get("notes", "").strip()

        errors = []
        if not site_name:
            errors.append("Site name is required.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        if errors:
            return render_template("add.html", errors=errors, categories=CATEGORIES,
                                   form=request.form)

        conn = get_db()
        conn.execute("""
            INSERT INTO passwords (site_name, url, username, password, category, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (site_name, url, username, password, category, notes))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html", errors=[], categories=CATEGORIES, form={})


@app.route("/view/<int:id>")
def view(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM passwords WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return redirect(url_for("index"))
    return render_template("view.html", pw=row)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM passwords WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return redirect(url_for("index"))

    if request.method == "POST":
        site_name = request.form.get("site_name", "").strip()
        url = request.form.get("url", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        category = request.form.get("category", "Personal")
        notes = request.form.get("notes", "").strip()

        errors = []
        if not site_name:
            errors.append("Site name is required.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        if errors:
            return render_template("edit.html", errors=errors, categories=CATEGORIES,
                                   pw=row, form=request.form)

        conn = get_db()
        conn.execute("""
            UPDATE passwords
            SET site_name=?, url=?, username=?, password=?, category=?, notes=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (site_name, url, username, password, category, notes, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("edit.html", errors=[], categories=CATEGORIES, pw=row, form=row)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM passwords WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return redirect(url_for("index"))

    if request.method == "POST":
        confirmed = request.form.get("confirmed")
        if confirmed == "yes":
            conn = get_db()
            conn.execute("DELETE FROM passwords WHERE id = ?", (id,))
            conn.commit()
            conn.close()
        return redirect(url_for("index"))

    return render_template("delete_confirm.html", pw=row)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5010)
