import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "spiritual_journal_secret"

DB_PATH = r"C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\spiritual_journal\spiritual_journal.db"

CATEGORIES = [
    "Meditation",
    "Prayer",
    "Study",
    "Retreat",
    "Practice",
    "Pilgrimage",
    "Service",
    "Reflection",
]

CATEGORY_COLORS = {
    "Meditation": "#7B68EE",
    "Prayer":     "#4CAF50",
    "Study":      "#2196F3",
    "Retreat":    "#FF9800",
    "Practice":   "#E91E63",
    "Pilgrimage": "#009688",
    "Service":    "#F44336",
    "Reflection": "#9C27B0",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS spiritual_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prefs (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_pref(conn, key, default=""):
    row = conn.execute("SELECT value FROM prefs WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_pref(conn, key, value):
    conn.execute(
        "INSERT INTO prefs (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value)
    )


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    if request.method == "POST":
        set_pref(conn, "filter_category", request.form.get("filter_category", ""))
        set_pref(conn, "sort_field", request.form.get("sort_field", "title"))
        set_pref(conn, "sort_dir", request.form.get("sort_dir", "asc"))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    filter_category = get_pref(conn, "filter_category", "")
    sort_field = get_pref(conn, "sort_field", "title")
    sort_dir = get_pref(conn, "sort_dir", "asc")

    allowed_fields = {"id", "title", "category", "notes"}
    if sort_field not in allowed_fields:
        sort_field = "title"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "asc"

    if filter_category:
        rows = conn.execute(
            f"SELECT * FROM spiritual_journal WHERE category = ? ORDER BY {sort_field} {sort_dir}",
            (filter_category,)
        ).fetchall()
    else:
        rows = conn.execute(
            f"SELECT * FROM spiritual_journal ORDER BY {sort_field} {sort_dir}"
        ).fetchall()
    conn.close()

    return render_template(
        "index.html",
        rows=rows,
        categories=CATEGORIES,
        category_colors=CATEGORY_COLORS,
        filter_category=filter_category,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )


@app.route("/reset_prefs")
def reset_prefs():
    conn = get_db()
    set_pref(conn, "filter_category", "")
    set_pref(conn, "sort_field", "title")
    set_pref(conn, "sort_dir", "asc")
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form["category"]
        notes = request.form.get("notes", "").strip()
        conn = get_db()
        conn.execute(
            "INSERT INTO spiritual_journal (title, category, notes) VALUES (?, ?, ?)",
            (title, category, notes)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html", categories=CATEGORIES, category_colors=CATEGORY_COLORS)


@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
def edit(entry_id):
    conn = get_db()
    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form["category"]
        notes = request.form.get("notes", "").strip()
        conn.execute(
            "UPDATE spiritual_journal SET title=?, category=?, notes=? WHERE id=?",
            (title, category, notes, entry_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    row = conn.execute(
        "SELECT * FROM spiritual_journal WHERE id=?", (entry_id,)
    ).fetchone()
    conn.close()
    return render_template("edit.html", row=row, categories=CATEGORIES, category_colors=CATEGORY_COLORS)


@app.route("/delete/<int:entry_id>", methods=["GET", "POST"])
def delete(entry_id):
    conn = get_db()
    if request.method == "POST":
        conn.execute("DELETE FROM spiritual_journal WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    row = conn.execute(
        "SELECT * FROM spiritual_journal WHERE id=?", (entry_id,)
    ).fetchone()
    conn.close()
    return render_template("confirm_delete.html", row=row, category_colors=CATEGORY_COLORS)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
