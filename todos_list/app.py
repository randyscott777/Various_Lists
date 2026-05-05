import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'todos_secret_key'

DB_PATH = r'C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\todos_list\todos.db'

STATUSES = ['Not Started', 'In Progress', 'Completed', 'On Hold']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
SORT_FIELDS = ['title', 'status', 'priority', 'due_date', 'created_at']


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Not Started',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    filter_status = request.args.get('filter_status', session.get('filter_status', ''))
    filter_priority = request.args.get('filter_priority', session.get('filter_priority', ''))
    sort_field = request.args.get('sort_field', session.get('sort_field', 'created_at'))
    sort_dir = request.args.get('sort_dir', session.get('sort_dir', 'desc'))

    # Persist filter/sort in session
    session['filter_status'] = filter_status
    session['filter_priority'] = filter_priority
    session['sort_field'] = sort_field if sort_field in SORT_FIELDS else 'created_at'
    session['sort_dir'] = sort_dir if sort_dir in ('asc', 'desc') else 'desc'

    sort_field = session['sort_field']
    sort_dir = session['sort_dir']

    query = 'SELECT * FROM todos WHERE 1=1'
    params = []
    if filter_status:
        query += ' AND status = ?'
        params.append(filter_status)
    if filter_priority:
        query += ' AND priority = ?'
        params.append(filter_priority)

    query += f' ORDER BY {sort_field} {sort_dir.upper()}'

    conn = get_db()
    todos = conn.execute(query, params).fetchall()

    counts = {}
    for s in STATUSES:
        row = conn.execute('SELECT COUNT(*) FROM todos WHERE status = ?', (s,)).fetchone()
        counts[s] = row[0]
    conn.close()

    next_dir = 'asc' if sort_dir == 'desc' else 'desc'

    return render_template('index.html',
                           todos=todos,
                           statuses=STATUSES,
                           priorities=PRIORITIES,
                           sort_fields=SORT_FIELDS,
                           filter_status=filter_status,
                           filter_priority=filter_priority,
                           sort_field=sort_field,
                           sort_dir=sort_dir,
                           next_dir=next_dir,
                           counts=counts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        status = request.form['status']
        priority = request.form['priority']
        due_date = request.form['due_date']

        conn = get_db()
        conn.execute(
            'INSERT INTO todos (title, description, status, priority, due_date) VALUES (?, ?, ?, ?, ?)',
            (title, description, status, priority, due_date or None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html', statuses=STATUSES, priorities=PRIORITIES)


@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit(todo_id):
    conn = get_db()
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    conn.close()

    if not todo:
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        status = request.form['status']
        priority = request.form['priority']
        due_date = request.form['due_date']

        conn = get_db()
        conn.execute(
            'UPDATE todos SET title=?, description=?, status=?, priority=?, due_date=? WHERE id=?',
            (title, description, status, priority, due_date or None, todo_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', todo=todo, statuses=STATUSES, priorities=PRIORITIES)


@app.route('/delete/<int:todo_id>', methods=['GET', 'POST'])
def delete(todo_id):
    conn = get_db()
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    conn.close()

    if not todo:
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db()
        conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('delete.html', todo=todo)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
