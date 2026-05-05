from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), 'help_desk.db')

CATEGORIES = ['Hardware', 'Software', 'Network', 'Account', 'Other']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed']


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')

    conn = get_db()

    query = 'SELECT * FROM tickets'
    params = []
    conditions = []
    if status_filter:
        conditions.append('status = ?')
        params.append(status_filter)
    if priority_filter:
        conditions.append('priority = ?')
        params.append(priority_filter)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    query += ' ORDER BY created_at DESC'

    tickets = conn.execute(query, params).fetchall()

    stats = {
        'total':       conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0],
        'open':        conn.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'").fetchone()[0],
        'in_progress': conn.execute("SELECT COUNT(*) FROM tickets WHERE status='In Progress'").fetchone()[0],
        'resolved':    conn.execute("SELECT COUNT(*) FROM tickets WHERE status='Resolved'").fetchone()[0],
        'closed':      conn.execute("SELECT COUNT(*) FROM tickets WHERE status='Closed'").fetchone()[0],
        'critical':    conn.execute("SELECT COUNT(*) FROM tickets WHERE priority='Critical'").fetchone()[0],
    }
    conn.close()

    return render_template('index.html', tickets=tickets, stats=stats,
                           status_filter=status_filter, priority_filter=priority_filter,
                           statuses=STATUSES, priorities=PRIORITIES)


@app.route('/ticket/new', methods=['GET', 'POST'])
def new_ticket():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        category = request.form['category']
        priority = request.form['priority']
        assigned_to = request.form['assigned_to'].strip()
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        conn = get_db()
        conn.execute(
            'INSERT INTO tickets (title, description, category, priority, status, assigned_to, created_at, updated_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (title, description, category, priority, 'Open', assigned_to, now, now)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('new.html', categories=CATEGORIES, priorities=PRIORITIES)


@app.route('/ticket/<int:id>')
def view_ticket(id):
    conn = get_db()
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not ticket:
        return redirect(url_for('index'))
    return render_template('view.html', ticket=ticket)


@app.route('/ticket/<int:id>/edit', methods=['GET', 'POST'])
def edit_ticket(id):
    conn = get_db()
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (id,)).fetchone()
    if not ticket:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        category = request.form['category']
        priority = request.form['priority']
        status = request.form['status']
        assigned_to = request.form['assigned_to'].strip()
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        conn.execute(
            'UPDATE tickets SET title=?, description=?, category=?, priority=?, status=?, assigned_to=?, updated_at=? '
            'WHERE id=?',
            (title, description, category, priority, status, assigned_to, now, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('view_ticket', id=id))

    conn.close()
    return render_template('edit.html', ticket=ticket,
                           categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES)


@app.route('/ticket/<int:id>/delete', methods=['GET', 'POST'])
def delete_ticket(id):
    conn = get_db()
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (id,)).fetchone()
    if not ticket:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM tickets WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', ticket=ticket)


if __name__ == '__main__':
    app.run(debug=True)
