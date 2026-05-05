import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "important_dates_secret_key"

DB_PATH = os.path.join(os.path.dirname(__file__), "important_dates.db")

CATEGORIES = ["birthday", "anniversary", "holiday", "other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS important_dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["filter_category"] = request.form.get("filter_category", "")
        session["filter_month"] = request.form.get("filter_month", "")
        session["sort_field"] = request.form.get("sort_field", "date")
        session["sort_dir"] = request.form.get("sort_dir", "asc")
        return redirect(url_for("index"))

    filter_category = session.get("filter_category", "")
    filter_month = session.get("filter_month", "")
    sort_field = session.get("sort_field", "date")
    sort_dir = session.get("sort_dir", "asc")

    valid_sort_fields = {"date", "title", "category"}
    if sort_field not in valid_sort_fields:
        sort_field = "date"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "asc"

    query = "SELECT * FROM important_dates WHERE 1=1"
    params = []

    if filter_category:
        query += " AND category = ?"
        params.append(filter_category)

    if filter_month:
        query += " AND strftime('%m', date) = ?"
        params.append(filter_month.zfill(2))

    query += f" ORDER BY {sort_field} {sort_dir.upper()}"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    months = [
        ("01", "January"), ("02", "February"), ("03", "March"),
        ("04", "April"), ("05", "May"), ("06", "June"),
        ("07", "July"), ("08", "August"), ("09", "September"),
        ("10", "October"), ("11", "November"), ("12", "December"),
    ]

    return render_template(
        "index.html",
        rows=rows,
        categories=CATEGORIES,
        months=months,
        filter_category=filter_category,
        filter_month=filter_month,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        category = request.form.get("category", "").strip()
        notes = request.form.get("notes", "").strip()

        if not title or not date or not category:
            error = "Title, date, and category are required."
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO important_dates (title, date, category, notes) VALUES (?, ?, ?, ?)",
                (title, date, category, notes),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("add.html", categories=CATEGORIES, error=error)


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM important_dates WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    if row is None:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        category = request.form.get("category", "").strip()
        notes = request.form.get("notes", "").strip()

        if not title or not date or not category:
            error = "Title, date, and category are required."
        else:
            conn = get_db()
            conn.execute(
                "UPDATE important_dates SET title=?, date=?, category=?, notes=? WHERE id=?",
                (title, date, category, notes, item_id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("edit.html", row=row, categories=CATEGORIES, error=error)


@app.route("/delete/<int:item_id>", methods=["GET", "POST"])
def delete(item_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM important_dates WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    if row is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        conn = get_db()
        conn.execute("DELETE FROM important_dates WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("delete.html", row=row)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
