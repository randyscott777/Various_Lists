import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "watchlist.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            genre TEXT,
            platform TEXT,
            status TEXT NOT NULL DEFAULT 'Want to Watch',
            rating INTEGER,
            year INTEGER,
            notes TEXT,
            date_added TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()

    filter_type = request.args.get("filter_type", "")
    filter_status = request.args.get("filter_status", "")
    filter_genre = request.args.get("filter_genre", "")
    sort_by = request.args.get("sort_by", "date_added")
    sort_dir = request.args.get("sort_dir", "desc")

    allowed_sorts = {"title", "type", "genre", "platform", "status", "rating", "year", "date_added"}
    if sort_by not in allowed_sorts:
        sort_by = "date_added"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"

    query = "SELECT * FROM watchlist WHERE 1=1"
    params = []

    if filter_type:
        query += " AND type = ?"
        params.append(filter_type)
    if filter_status:
        query += " AND status = ?"
        params.append(filter_status)
    if filter_genre:
        query += " AND genre = ?"
        params.append(filter_genre)

    query += f" ORDER BY {sort_by} {sort_dir.upper()}"

    items = conn.execute(query, params).fetchall()

    genres = conn.execute("SELECT DISTINCT genre FROM watchlist WHERE genre IS NOT NULL AND genre != '' ORDER BY genre").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    counts = {
        "total": total,
        "tv": conn.execute("SELECT COUNT(*) FROM watchlist WHERE type='TV Show'").fetchone()[0],
        "movie": conn.execute("SELECT COUNT(*) FROM watchlist WHERE type='Movie'").fetchone()[0],
        "live": conn.execute("SELECT COUNT(*) FROM watchlist WHERE type='Live Event'").fetchone()[0],
        "want": conn.execute("SELECT COUNT(*) FROM watchlist WHERE status='Want to Watch'").fetchone()[0],
        "watching": conn.execute("SELECT COUNT(*) FROM watchlist WHERE status='Watching'").fetchone()[0],
        "watched": conn.execute("SELECT COUNT(*) FROM watchlist WHERE status='Watched'").fetchone()[0],
    }
    conn.close()

    return render_template("index.html",
        items=items,
        genres=[g["genre"] for g in genres],
        counts=counts,
        filter_type=filter_type,
        filter_status=filter_status,
        filter_genre=filter_genre,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"].strip()
        item_type = request.form["type"]
        genre = request.form.get("genre", "").strip()
        platform = request.form.get("platform", "").strip()
        status = request.form.get("status", "Want to Watch")
        rating = request.form.get("rating") or None
        year = request.form.get("year") or None
        notes = request.form.get("notes", "").strip()
        today = date.today().isoformat()

        conn = get_db()
        conn.execute("""
            INSERT INTO watchlist (title, type, genre, platform, status, rating, year, notes, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, item_type, genre, platform, status, rating, year, notes, today))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/view/<int:item_id>")
def view(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM watchlist WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not item:
        return redirect(url_for("index"))
    return render_template("view.html", item=item)


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM watchlist WHERE id = ?", (item_id,)).fetchone()

    if not item:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        # Check for confirmation if key fields changed
        new_title = request.form["title"].strip()
        new_type = request.form["type"]
        new_status = request.form.get("status", "Want to Watch")
        confirmed = request.form.get("confirmed")

        key_changed = (new_title != item["title"] or new_type != item["type"] or new_status != item["status"])

        if key_changed and not confirmed:
            # Re-render form with confirmation prompt
            form_data = {
                "title": new_title,
                "type": new_type,
                "genre": request.form.get("genre", ""),
                "platform": request.form.get("platform", ""),
                "status": new_status,
                "rating": request.form.get("rating", ""),
                "year": request.form.get("year", ""),
                "notes": request.form.get("notes", ""),
            }
            conn.close()
            return render_template("edit.html", item=item, form_data=form_data, needs_confirm=True)

        genre = request.form.get("genre", "").strip()
        platform = request.form.get("platform", "").strip()
        rating = request.form.get("rating") or None
        year = request.form.get("year") or None
        notes = request.form.get("notes", "").strip()

        conn.execute("""
            UPDATE watchlist SET title=?, type=?, genre=?, platform=?, status=?, rating=?, year=?, notes=?
            WHERE id=?
        """, (new_title, new_type, genre, platform, new_status, rating, year, notes, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for("view", item_id=item_id))

    conn.close()
    return render_template("edit.html", item=item, form_data=None, needs_confirm=False)


@app.route("/delete/<int:item_id>", methods=["GET", "POST"])
def delete(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM watchlist WHERE id = ?", (item_id,)).fetchone()

    if not item:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        conn.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("delete_confirm.html", item=item)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
