import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bucket_list_secret_key_2024'

DB_PATH = r'C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\bucket_list\bucket_list.db'

CATEGORIES = ['Travel', 'Adventure', 'Learning', 'Career', 'Family', 'Health', 'Creative', 'Other']
PRIORITIES = ['High', 'Medium', 'Low']
STATUSES = ['Not Started', 'In Progress', 'Completed', 'Abandoned']


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bucket_list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Not Started',
            description TEXT,
            target_date DATE,
            completed_date DATE,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_prefs (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_pref(key, default=''):
    conn = get_db()
    row = conn.execute('SELECT value FROM user_prefs WHERE key = ?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_pref(key, value):
    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO user_prefs (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()


@app.route('/')
def index():
    # Load persisted filter/sort or use session
    filter_category = request.args.get('filter_category', get_pref('filter_category', ''))
    filter_priority = request.args.get('filter_priority', get_pref('filter_priority', ''))
    filter_status = request.args.get('filter_status', get_pref('filter_status', ''))
    sort_by = request.args.get('sort_by', get_pref('sort_by', 'created_at'))
    sort_dir = request.args.get('sort_dir', get_pref('sort_dir', 'DESC'))

    # Persist preferences
    if 'filter_category' in request.args or 'sort_by' in request.args:
        set_pref('filter_category', filter_category)
        set_pref('filter_priority', filter_priority)
        set_pref('filter_status', filter_status)
        set_pref('sort_by', sort_by)
        set_pref('sort_dir', sort_dir)

    valid_sort_cols = ['title', 'category', 'priority', 'status', 'target_date', 'created_at']
    if sort_by not in valid_sort_cols:
        sort_by = 'created_at'
    if sort_dir not in ['ASC', 'DESC']:
        sort_dir = 'DESC'

    query = 'SELECT * FROM bucket_list_items WHERE 1=1'
    params = []

    if filter_category:
        query += ' AND category = ?'
        params.append(filter_category)
    if filter_priority:
        query += ' AND priority = ?'
        params.append(filter_priority)
    if filter_status:
        query += ' AND status = ?'
        params.append(filter_status)

    query += f' ORDER BY {sort_by} {sort_dir}'

    conn = get_db()
    items = conn.execute(query, params).fetchall()

    # Stats
    total = conn.execute('SELECT COUNT(*) as c FROM bucket_list_items').fetchone()['c']
    completed = conn.execute("SELECT COUNT(*) as c FROM bucket_list_items WHERE status = 'Completed'").fetchone()['c']
    in_progress = conn.execute("SELECT COUNT(*) as c FROM bucket_list_items WHERE status = 'In Progress'").fetchone()['c']
    not_started = conn.execute("SELECT COUNT(*) as c FROM bucket_list_items WHERE status = 'Not Started'").fetchone()['c']
    conn.close()

    return render_template('index.html',
        items=items,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        statuses=STATUSES,
        filter_category=filter_category,
        filter_priority=filter_priority,
        filter_status=filter_status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        total=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started
    )


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title'].strip()
        category = request.form['category']
        priority = request.form['priority']
        status = request.form['status']
        description = request.form['description'].strip()
        target_date = request.form['target_date'] or None
        completed_date = request.form['completed_date'] or None
        notes = request.form['notes'].strip()

        conn = get_db()
        conn.execute('''
            INSERT INTO bucket_list_items (title, category, priority, status, description, target_date, completed_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, category, priority, status, description, target_date, completed_date, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html', categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    conn = get_db()
    item = conn.execute('SELECT * FROM bucket_list_items WHERE id = ?', (item_id,)).fetchone()
    conn.close()

    if not item:
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        category = request.form['category']
        priority = request.form['priority']
        status = request.form['status']
        description = request.form['description'].strip()
        target_date = request.form['target_date'] or None
        completed_date = request.form['completed_date'] or None
        notes = request.form['notes'].strip()

        conn = get_db()
        conn.execute('''
            UPDATE bucket_list_items
            SET title=?, category=?, priority=?, status=?, description=?, target_date=?, completed_date=?, notes=?
            WHERE id=?
        ''', (title, category, priority, status, description, target_date, completed_date, notes, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', item=item, categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES)


@app.route('/delete/<int:item_id>', methods=['GET', 'POST'])
def delete(item_id):
    conn = get_db()
    item = conn.execute('SELECT * FROM bucket_list_items WHERE id = ?', (item_id,)).fetchone()
    conn.close()

    if not item:
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db()
        conn.execute('DELETE FROM bucket_list_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('delete_confirm.html', item=item)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5020)
