from flask import Flask, render_template, request, redirect, url_for, abort
from database import get_connection, init_db

app = Flask(__name__)

STATUSES = ['To Do', 'In Progress', 'Done']
PRIORITIES = ['Low', 'Medium', 'High']
SORT_OPTIONS = {
    'created_date': 'Date Created',
    'due_date': 'Due Date',
    'priority': 'Priority',
    'status': 'Status',
    'title': 'Title',
}


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('projects'))


@app.route('/projects')
def projects():
    conn = get_connection()
    rows = conn.execute('''
        SELECT p.*, COUNT(t.id) AS task_count
        FROM projects p
        LEFT JOIN tasks t ON t.project_id = p.id
        GROUP BY p.id
        ORDER BY p.created_date DESC
    ''').fetchall()
    conn.close()
    return render_template('projects.html', projects=rows)


@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if not name:
            return render_template('project_form.html', error='Name is required.', project=None)
        conn = get_connection()
        conn.execute('INSERT INTO projects (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        conn.close()
        return redirect(url_for('projects'))
    return render_template('project_form.html', project=None)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        conn.close()
        abort(404)
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if not name:
            conn.close()
            return render_template('project_form.html', error='Name is required.', project=project)
        conn.execute('UPDATE projects SET name = ?, description = ? WHERE id = ?',
                     (name, description, project_id))
        conn.commit()
        conn.close()
        return redirect(url_for('projects'))
    conn.close()
    return render_template('project_form.html', project=project)


@app.route('/projects/<int:project_id>/delete', methods=['GET', 'POST'])
def delete_project(project_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        conn.close()
        abort(404)
    if request.method == 'POST':
        conn.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
        conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('projects'))
    conn.close()
    return render_template('confirm_delete.html',
                           item_type='project',
                           item_name=project['name'],
                           cancel_url=url_for('projects'))


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@app.route('/projects/<int:project_id>/tasks')
def tasks(project_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        conn.close()
        abort(404)

    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    sort = request.args.get('sort', 'created_date')
    if sort not in SORT_OPTIONS:
        sort = 'created_date'

    query = 'SELECT * FROM tasks WHERE project_id = ?'
    params = [project_id]

    if status_filter and status_filter in STATUSES:
        query += ' AND status = ?'
        params.append(status_filter)
    if priority_filter and priority_filter in PRIORITIES:
        query += ' AND priority = ?'
        params.append(priority_filter)

    priority_order = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END"
    if sort == 'priority':
        query += f' ORDER BY {priority_order}'
    else:
        query += f' ORDER BY {sort}'

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('tasks.html',
                           project=project,
                           tasks=rows,
                           statuses=STATUSES,
                           priorities=PRIORITIES,
                           sort_options=SORT_OPTIONS,
                           current_status=status_filter,
                           current_priority=priority_filter,
                           current_sort=sort)


@app.route('/projects/<int:project_id>/tasks/new', methods=['GET', 'POST'])
def new_task(project_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        conn.close()
        abort(404)
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'To Do')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date', '').strip() or None
        if not title:
            conn.close()
            return render_template('task_form.html', project=project, task=None,
                                   statuses=STATUSES, priorities=PRIORITIES,
                                   error='Title is required.')
        conn.execute('''
            INSERT INTO tasks (project_id, title, description, status, priority, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, title, description, status, priority, due_date))
        conn.commit()
        conn.close()
        return redirect(url_for('tasks', project_id=project_id))
    conn.close()
    return render_template('task_form.html', project=project, task=None,
                           statuses=STATUSES, priorities=PRIORITIES)


@app.route('/projects/<int:project_id>/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(project_id, task_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND project_id = ?',
                        (task_id, project_id)).fetchone()
    if not project or not task:
        conn.close()
        abort(404)
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'To Do')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date', '').strip() or None
        if not title:
            conn.close()
            return render_template('task_form.html', project=project, task=task,
                                   statuses=STATUSES, priorities=PRIORITIES,
                                   error='Title is required.')
        conn.execute('''
            UPDATE tasks SET title=?, description=?, status=?, priority=?, due_date=?
            WHERE id=?
        ''', (title, description, status, priority, due_date, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('tasks', project_id=project_id))
    conn.close()
    return render_template('task_form.html', project=project, task=task,
                           statuses=STATUSES, priorities=PRIORITIES)


@app.route('/projects/<int:project_id>/tasks/<int:task_id>/delete', methods=['GET', 'POST'])
def delete_task(project_id, task_id):
    conn = get_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND project_id = ?',
                        (task_id, project_id)).fetchone()
    if not project or not task:
        conn.close()
        abort(404)
    if request.method == 'POST':
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('tasks', project_id=project_id))
    conn.close()
    return render_template('confirm_delete.html',
                           item_type='task',
                           item_name=task['title'],
                           cancel_url=url_for('tasks', project_id=project_id))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
