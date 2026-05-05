import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "projects.db")

STATUS_OPTIONS = ["Not Started", "In Progress", "Done", "Blocked", "On Hold"]
PRIORITY_OPTIONS = ["Low", "Medium", "High"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pref(key, default=""):
    conn = get_db()
    row = conn.execute("SELECT value FROM user_prefs WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_pref(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO user_prefs (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_prefs (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Not Started',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Not Started',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Not Started',
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- PROJECTS ----------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        set_pref("proj_filter_status", request.form.get("filter_status", ""))
        set_pref("proj_filter_priority", request.form.get("filter_priority", ""))
        set_pref("proj_sort_field", request.form.get("sort_field", "name"))
        set_pref("proj_sort_dir", request.form.get("sort_dir", "asc"))
        return redirect(url_for("index"))

    filter_status = get_pref("proj_filter_status", "")
    filter_priority = get_pref("proj_filter_priority", "")
    sort_field = get_pref("proj_sort_field", "name")
    sort_dir = get_pref("proj_sort_dir", "asc")

    allowed_fields = {"name", "status", "priority", "due_date", "created_at"}
    if sort_field not in allowed_fields:
        sort_field = "name"
    order = "ASC" if sort_dir == "asc" else "DESC"

    conn = get_db()
    query = "SELECT p.*, (SELECT COUNT(*) FROM tasks WHERE project_id=p.id) as task_count FROM projects p WHERE 1=1"
    params = []
    if filter_status:
        query += " AND p.status = ?"
        params.append(filter_status)
    if filter_priority:
        query += " AND p.priority = ?"
        params.append(filter_priority)
    query += f" ORDER BY p.{sort_field} {order}"
    projects = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("index.html",
        projects=projects,
        filter_status=filter_status,
        filter_priority=filter_priority,
        sort_field=sort_field,
        sort_dir=sort_dir,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS
    )


@app.route("/project/new", methods=["GET", "POST"])
def project_new():
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        conn = get_db()
        conn.execute(
            "INSERT INTO projects (name, description, status, priority, due_date) VALUES (?,?,?,?,?)",
            (name, description, status, priority, due_date or None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("project_form.html",
        project=None,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS,
        title="New Project"
    )


@app.route("/project/<int:project_id>/edit", methods=["GET", "POST"])
def project_edit(project_id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        conn.execute(
            "UPDATE projects SET name=?, description=?, status=?, priority=?, due_date=? WHERE id=?",
            (name, description, status, priority, due_date or None, project_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("project_form.html",
        project=project,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS,
        title="Edit Project"
    )


@app.route("/project/<int:project_id>/delete", methods=["GET", "POST"])
def project_delete(project_id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        conn.execute("DELETE FROM subtasks WHERE task_id IN (SELECT id FROM tasks WHERE project_id=?)", (project_id,))
        conn.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("confirm_delete.html",
        item_type="Project",
        item_name=project["name"],
        cancel_url=url_for("index"),
        warning="This will also delete all tasks and sub-tasks within this project."
    )


# ---------- TASKS ----------

@app.route("/project/<int:project_id>/tasks", methods=["GET", "POST"])
def tasks(project_id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for("index"))

    pk = f"task_{project_id}"
    if request.method == "POST":
        set_pref(f"{pk}_filter_status", request.form.get("filter_status", ""))
        set_pref(f"{pk}_filter_priority", request.form.get("filter_priority", ""))
        set_pref(f"{pk}_sort_field", request.form.get("sort_field", "name"))
        set_pref(f"{pk}_sort_dir", request.form.get("sort_dir", "asc"))
        return redirect(url_for("tasks", project_id=project_id))

    filter_status = get_pref(f"{pk}_filter_status", "")
    filter_priority = get_pref(f"{pk}_filter_priority", "")
    sort_field = get_pref(f"{pk}_sort_field", "name")
    sort_dir = get_pref(f"{pk}_sort_dir", "asc")

    allowed_fields = {"name", "status", "priority", "due_date", "created_at"}
    if sort_field not in allowed_fields:
        sort_field = "name"
    order = "ASC" if sort_dir == "asc" else "DESC"

    query = "SELECT t.*, (SELECT COUNT(*) FROM subtasks WHERE task_id=t.id) as subtask_count FROM tasks t WHERE t.project_id=?"
    params = [project_id]
    if filter_status:
        query += " AND t.status=?"
        params.append(filter_status)
    if filter_priority:
        query += " AND t.priority=?"
        params.append(filter_priority)
    query += f" ORDER BY t.{sort_field} {order}"
    tasks_list = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("tasks.html",
        project=project,
        tasks=tasks_list,
        filter_status=filter_status,
        filter_priority=filter_priority,
        sort_field=sort_field,
        sort_dir=sort_dir,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS
    )


@app.route("/project/<int:project_id>/task/new", methods=["GET", "POST"])
def task_new(project_id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        conn.execute(
            "INSERT INTO tasks (project_id, name, description, status, priority, due_date) VALUES (?,?,?,?,?,?)",
            (project_id, name, description, status, priority, due_date or None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("tasks", project_id=project_id))
    conn.close()
    return render_template("task_form.html",
        task=None,
        project=project,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS,
        title="New Task"
    )


@app.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
def task_edit(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return redirect(url_for("index"))
    project = conn.execute("SELECT * FROM projects WHERE id=?", (task["project_id"],)).fetchone()
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        conn.execute(
            "UPDATE tasks SET name=?, description=?, status=?, priority=?, due_date=? WHERE id=?",
            (name, description, status, priority, due_date or None, task_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("tasks", project_id=task["project_id"]))
    conn.close()
    return render_template("task_form.html",
        task=task,
        project=project,
        status_options=STATUS_OPTIONS,
        priority_options=PRIORITY_OPTIONS,
        title="Edit Task"
    )


@app.route("/task/<int:task_id>/delete", methods=["GET", "POST"])
def task_delete(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return redirect(url_for("index"))
    project_id = task["project_id"]
    if request.method == "POST":
        conn.execute("DELETE FROM subtasks WHERE task_id=?", (task_id,))
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("tasks", project_id=project_id))
    conn.close()
    return render_template("confirm_delete.html",
        item_type="Task",
        item_name=task["name"],
        cancel_url=url_for("tasks", project_id=project_id),
        warning="This will also delete all sub-tasks within this task."
    )


# ---------- SUBTASKS ----------

@app.route("/task/<int:task_id>/subtasks", methods=["GET", "POST"])
def subtasks(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return redirect(url_for("index"))
    project = conn.execute("SELECT * FROM projects WHERE id=?", (task["project_id"],)).fetchone()

    sk = f"sub_{task_id}"
    if request.method == "POST":
        set_pref(f"{sk}_filter_status", request.form.get("filter_status", ""))
        set_pref(f"{sk}_sort_field", request.form.get("sort_field", "name"))
        set_pref(f"{sk}_sort_dir", request.form.get("sort_dir", "asc"))
        return redirect(url_for("subtasks", task_id=task_id))

    filter_status = get_pref(f"{sk}_filter_status", "")
    sort_field = get_pref(f"{sk}_sort_field", "name")
    sort_dir = get_pref(f"{sk}_sort_dir", "asc")

    allowed_fields = {"name", "status", "due_date", "created_at"}
    if sort_field not in allowed_fields:
        sort_field = "name"
    order = "ASC" if sort_dir == "asc" else "DESC"

    query = "SELECT * FROM subtasks WHERE task_id=?"
    params = [task_id]
    if filter_status:
        query += " AND status=?"
        params.append(filter_status)
    query += f" ORDER BY {sort_field} {order}"
    subtasks_list = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("subtasks.html",
        task=task,
        project=project,
        subtasks=subtasks_list,
        filter_status=filter_status,
        sort_field=sort_field,
        sort_dir=sort_dir,
        status_options=STATUS_OPTIONS
    )


@app.route("/task/<int:task_id>/subtask/new", methods=["GET", "POST"])
def subtask_new(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return redirect(url_for("index"))
    project = conn.execute("SELECT * FROM projects WHERE id=?", (task["project_id"],)).fetchone()
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        due_date = request.form.get("due_date", "")
        conn.execute(
            "INSERT INTO subtasks (task_id, name, description, status, due_date) VALUES (?,?,?,?,?)",
            (task_id, name, description, status, due_date or None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("subtasks", task_id=task_id))
    conn.close()
    return render_template("subtask_form.html",
        subtask=None,
        task=task,
        project=project,
        status_options=STATUS_OPTIONS,
        title="New Sub-task"
    )


@app.route("/subtask/<int:subtask_id>/edit", methods=["GET", "POST"])
def subtask_edit(subtask_id):
    conn = get_db()
    subtask = conn.execute("SELECT * FROM subtasks WHERE id=?", (subtask_id,)).fetchone()
    if not subtask:
        conn.close()
        return redirect(url_for("index"))
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (subtask["task_id"],)).fetchone()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (task["project_id"],)).fetchone()
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Not Started")
        due_date = request.form.get("due_date", "")
        conn.execute(
            "UPDATE subtasks SET name=?, description=?, status=?, due_date=? WHERE id=?",
            (name, description, status, due_date or None, subtask_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("subtasks", task_id=subtask["task_id"]))
    conn.close()
    return render_template("subtask_form.html",
        subtask=subtask,
        task=task,
        project=project,
        status_options=STATUS_OPTIONS,
        title="Edit Sub-task"
    )


@app.route("/subtask/<int:subtask_id>/delete", methods=["GET", "POST"])
def subtask_delete(subtask_id):
    conn = get_db()
    subtask = conn.execute("SELECT * FROM subtasks WHERE id=?", (subtask_id,)).fetchone()
    if not subtask:
        conn.close()
        return redirect(url_for("index"))
    task_id = subtask["task_id"]
    if request.method == "POST":
        conn.execute("DELETE FROM subtasks WHERE id=?", (subtask_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("subtasks", task_id=task_id))
    conn.close()
    return render_template("confirm_delete.html",
        item_type="Sub-task",
        item_name=subtask["name"],
        cancel_url=url_for("subtasks", task_id=task_id),
        warning=None
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
