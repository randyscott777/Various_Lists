# Created by Claude Code
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = "C:/Users/randy/OneDrive/VisualStudioCode/Various_Lists/goals_list_new/goals.db"

CATEGORIES = ["Personal", "Career", "Health", "Financial", "Education", "Other"]
PRIORITIES  = ["Low", "Medium", "High", "Urgent"]
STATUSES    = ["Not Started", "In Progress", "On Hold", "Completed"]
VALID_SORT_FIELDS = ["title", "category", "priority", "status", "due_date", "created_date"]
SORT_LABELS = {
    "title":        "Title",
    "category":     "Category",
    "priority":     "Priority",
    "status":       "Status",
    "due_date":     "Due Date",
    "created_date": "Created",
}

PRIORITY_RANK = "CASE priority WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 3 WHEN 'Urgent' THEN 4 END"
STATUS_RANK   = "CASE status WHEN 'Not Started' THEN 1 WHEN 'In Progress' THEN 2 WHEN 'On Hold' THEN 3 WHEN 'Completed' THEN 4 END"

SEED_DATA = [
    # (title, description, category, priority, status, due_date)
    ("Run a 5K",                    "Train and complete a 5K race event",              "Health",     "Medium", "In Progress",  "2026-06-15"),
    ("Learn Python Flask",          "Build 3 Flask web apps from scratch",             "Education",  "High",   "Completed",    "2026-03-01"),
    ("Save $10,000 Emergency Fund", "Build a 6-month emergency savings cushion",       "Financial",  "High",   "In Progress",  "2026-12-31"),
    ("Get a Promotion",             "Achieve senior developer title this year",        "Career",     "High",   "In Progress",  "2026-09-01"),
    ("Read 12 Books This Year",     "One book per month throughout the year",          "Personal",   "Low",    "In Progress",  "2026-12-31"),
    ("Learn Spanish",               "Reach conversational fluency in Spanish",         "Education",  "Medium", "Not Started",  "2027-01-01"),
    ("Lose 15 Pounds",              "Reach target weight through diet and exercise",   "Health",     "High",   "Not Started",  "2026-08-01"),
    ("Pay Off Credit Card Debt",    "Eliminate $5,000 in credit card balances",        "Financial",  "Urgent", "In Progress",  "2026-06-01"),
    ("Start a Side Business",       "Launch a freelance consulting service",           "Career",     "Medium", "Not Started",  "2026-10-01"),
    ("Meditate Daily",              "Build a consistent 10-minute daily habit",        "Personal",   "Low",    "On Hold",      "2026-12-31"),
    ("Visit Europe",                "2-week trip through France and Italy",            "Personal",   "Medium", "Not Started",  "2027-06-01"),
    ("Get AWS Certification",       "Pass the AWS Solutions Architect exam",           "Career",     "High",   "Not Started",  "2026-07-01"),
    ("Improve Sleep Schedule",      "Sleep 8 hours nightly and track quality",        "Health",     "Medium", "On Hold",      "2026-05-31"),
    ("Organize Home Office",        "Declutter and set up a productive workspace",    "Other",      "Low",    "Completed",    "2026-02-01"),
    ("Volunteer Monthly",           "Give 4 hours per month to a local charity",      "Other",      "Low",    "In Progress",  "2026-12-31"),
    ("Master Advanced Excel",       "Complete an advanced spreadsheet skills course", "Education",  "Medium", "Not Started",  "2026-09-01"),
    ("Build Investment Portfolio",  "Diversify savings into index funds and ETFs",    "Financial",  "Medium", "Not Started",  "2026-12-31"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            description  TEXT DEFAULT '',
            category     TEXT NOT NULL DEFAULT 'Personal',
            priority     TEXT NOT NULL DEFAULT 'Medium',
            status       TEXT NOT NULL DEFAULT 'Not Started',
            due_date     TEXT DEFAULT '',
            created_date TEXT DEFAULT '',
            updated_at   TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ui_prefs (
            id               INTEGER PRIMARY KEY CHECK (id = 1),
            filter_category  TEXT DEFAULT '',
            filter_status    TEXT DEFAULT '',
            filter_priority  TEXT DEFAULT '',
            sort_field       TEXT DEFAULT 'due_date',
            sort_dir         TEXT DEFAULT 'asc'
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO ui_prefs
            (id, filter_category, filter_status, filter_priority, sort_field, sort_dir)
        VALUES (1, '', '', '', 'due_date', 'asc')
    """)
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0] == 0:
        today = date.today().isoformat()
        now   = now_str()
        rows  = [(t, d, cat, p, s, dd, today, now) for t, d, cat, p, s, dd in SEED_DATA]
        conn.executemany("""
            INSERT INTO goals
                (title, description, category, priority, status, due_date, created_date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
    conn.close()


def get_prefs():
    conn = get_db()
    row = conn.execute("SELECT * FROM ui_prefs WHERE id = 1").fetchone()
    conn.close()
    return row


def save_prefs(fc, fs, fp, sf, sd):
    conn = get_db()
    conn.execute("""
        UPDATE ui_prefs
        SET filter_category=?, filter_status=?, filter_priority=?, sort_field=?, sort_dir=?
        WHERE id = 1
    """, (fc, fs, fp, sf, sd))
    conn.commit()
    conn.close()


def get_sort_expr(sf):
    if sf == "priority":
        return PRIORITY_RANK
    if sf == "status":
        return STATUS_RANK
    return sf


@app.context_processor
def inject_globals():
    try:
        conn = get_db()
        result = conn.execute("SELECT MAX(updated_at) FROM goals").fetchone()
        conn.close()
        lu = result[0] if result and result[0] else None
        if lu:
            dt = datetime.strptime(lu[:19], "%Y-%m-%d %H:%M:%S")
            lu = dt.strftime("%B %d, %Y")
        else:
            lu = "N/A"
    except Exception:
        lu = "N/A"
    return dict(last_updated=lu, today_iso=date.today().isoformat())


@app.route("/", methods=["GET", "POST"])
def index():
    prefs = get_prefs()
    if request.method == "POST":
        fc = request.form.get("filter_category", "")
        fs = request.form.get("filter_status", "")
        fp = request.form.get("filter_priority", "")
        sf = request.form.get("sort_field", "due_date")
        sd = request.form.get("sort_dir", "asc")
        save_prefs(fc, fs, fp, sf, sd)
    else:
        fc = prefs["filter_category"]
        fs = prefs["filter_status"]
        fp = prefs["filter_priority"]
        sf = prefs["sort_field"]
        sd = prefs["sort_dir"]

    if sf not in VALID_SORT_FIELDS:
        sf = "due_date"
    if sd not in ("asc", "desc"):
        sd = "asc"

    query  = "SELECT * FROM goals WHERE 1=1"
    params = []
    if fc:
        query += " AND category = ?"
        params.append(fc)
    if fs:
        query += " AND status = ?"
        params.append(fs)
    if fp:
        query += " AND priority = ?"
        params.append(fp)
    query += f" ORDER BY {get_sort_expr(sf)} {sd.upper()}, id ASC"

    today = date.today().isoformat()
    conn  = get_db()
    goals = conn.execute(query, params).fetchall()
    all_g = conn.execute("SELECT status, due_date FROM goals").fetchall()
    conn.close()

    total     = len(all_g)
    by_status = {s: sum(1 for g in all_g if g["status"] == s) for s in STATUSES}
    overdue   = sum(1 for g in all_g
                    if g["due_date"] and g["due_date"] < today and g["status"] != "Completed")

    return render_template("index.html",
        goals=goals, categories=CATEGORIES, statuses=STATUSES, priorities=PRIORITIES,
        sort_labels=SORT_LABELS, valid_sort_fields=VALID_SORT_FIELDS,
        filter_category=fc, filter_status=fs, filter_priority=fp,
        sort_field=sf, sort_dir=sd,
        total=total, by_status=by_status, overdue=overdue,
    )


@app.route("/clear")
def clear():
    save_prefs("", "", "", "due_date", "asc")
    return redirect(url_for("index"))


@app.route("/toggle/<int:id>", methods=["POST"])
def toggle(id):
    new_status = request.form.get("status", "Not Started")
    if new_status not in STATUSES:
        new_status = "Not Started"
    conn = get_db()
    conn.execute("UPDATE goals SET status=?, updated_at=? WHERE id=?",
                 (new_status, now_str(), id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/done/<int:id>", methods=["POST"])
def quick_done(id):
    conn = get_db()
    row  = conn.execute("SELECT status FROM goals WHERE id=?", (id,)).fetchone()
    if row:
        new_status = "Not Started" if row["status"] == "Completed" else "Completed"
        conn.execute("UPDATE goals SET status=?, updated_at=? WHERE id=?",
                     (new_status, now_str(), id))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add():
    error = None
    if request.method == "POST":
        title  = request.form.get("title", "").strip()
        desc   = request.form.get("description", "").strip()
        cat    = request.form.get("category", "Personal")
        pri    = request.form.get("priority", "Medium")
        status = request.form.get("status", "Not Started")
        due    = request.form.get("due_date", "")
        if not title:
            error = "Title is required."
        else:
            conn = get_db()
            conn.execute("""
                INSERT INTO goals
                    (title, description, category, priority, status, due_date, created_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, desc, cat, pri, status, due, date.today().isoformat(), now_str()))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("add.html",
        categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES, error=error)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    goal = conn.execute("SELECT * FROM goals WHERE id=?", (id,)).fetchone()
    conn.close()
    if not goal:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        title  = request.form.get("title", "").strip()
        desc   = request.form.get("description", "").strip()
        cat    = request.form.get("category", "Personal")
        pri    = request.form.get("priority", "Medium")
        status = request.form.get("status", "Not Started")
        due    = request.form.get("due_date", "")
        if not title:
            error = "Title is required."
        else:
            conn = get_db()
            conn.execute("""
                UPDATE goals
                SET title=?, description=?, category=?, priority=?, status=?, due_date=?, updated_at=?
                WHERE id=?
            """, (title, desc, cat, pri, status, due, now_str(), id))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("edit.html",
        goal=goal, categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES, error=error)


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    goal = conn.execute("SELECT * FROM goals WHERE id=?", (id,)).fetchone()
    conn.close()
    if not goal:
        return redirect(url_for("index"))
    return render_template("confirm_delete.html", goal=goal)


@app.route("/delete/<int:id>/confirm", methods=["POST"])
def delete_confirm(id):
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5052)
