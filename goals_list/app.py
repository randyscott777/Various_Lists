from flask import Flask, render_template, request, redirect, url_for
from database import get_db, init_db

app = Flask(__name__)

CATEGORIES = ['Personal', 'Work', 'Health', 'Finance', 'Education']
PRIORITIES = ['High', 'Medium', 'Low']
STATUSES = ['Not Started', 'In Progress', 'Completed', 'On Hold']


@app.route('/')
def index():
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    valid_sorts = ['title', 'category', 'priority', 'status', 'target_date', 'created_at']
    if sort not in valid_sorts:
        sort = 'created_at'
    if order not in ['asc', 'desc']:
        order = 'desc'

    conn = get_db()
    query = 'SELECT * FROM goals WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if priority:
        query += ' AND priority = ?'
        params.append(priority)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += f' ORDER BY {sort} {order.upper()}'
    goals = conn.execute(query, params).fetchall()

    counts = {}
    for s in STATUSES:
        row = conn.execute('SELECT COUNT(*) as c FROM goals WHERE status = ?', (s,)).fetchone()
        counts[s] = row['c']
    total = conn.execute('SELECT COUNT(*) as c FROM goals').fetchone()['c']
    conn.close()

    return render_template('index.html',
                           goals=goals,
                           categories=CATEGORIES,
                           priorities=PRIORITIES,
                           statuses=STATUSES,
                           counts=counts,
                           total=total,
                           sel_category=category,
                           sel_priority=priority,
                           sel_status=status,
                           sort=sort,
                           order=order)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Personal')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Not Started')
        target_date = request.form.get('target_date') or None

        if title:
            conn = get_db()
            conn.execute('''
                INSERT INTO goals (title, description, category, priority, status, target_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, category, priority, status, target_date))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('add.html', categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES)


@app.route('/<int:goal_id>')
def detail(goal_id):
    conn = get_db()
    goal = conn.execute('SELECT * FROM goals WHERE id = ?', (goal_id,)).fetchone()
    conn.close()
    if not goal:
        return redirect(url_for('index'))
    return render_template('detail.html', goal=goal)


@app.route('/<int:goal_id>/edit', methods=['GET', 'POST'])
def edit(goal_id):
    conn = get_db()
    goal = conn.execute('SELECT * FROM goals WHERE id = ?', (goal_id,)).fetchone()

    if not goal:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Personal')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Not Started')
        target_date = request.form.get('target_date') or None

        if title:
            conn.execute('''
                UPDATE goals
                SET title = ?, description = ?, category = ?, priority = ?, status = ?,
                    target_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, description, category, priority, status, target_date, goal_id))
            conn.commit()
            conn.close()
            return redirect(url_for('detail', goal_id=goal_id))

    conn.close()
    return render_template('edit.html', goal=goal, categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES)


@app.route('/<int:goal_id>/delete', methods=['GET', 'POST'])
def delete(goal_id):
    conn = get_db()
    goal = conn.execute('SELECT * FROM goals WHERE id = ?', (goal_id,)).fetchone()

    if not goal:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', goal=goal)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
