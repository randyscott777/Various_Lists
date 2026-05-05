from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'budget_tracker.db')

CATEGORIES = ['Education', 'Entertainment', 'Food', 'Healthcare', 'Housing',
              'Income', 'Transport', 'Utilities', 'Other']

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    category = request.args.get('category', '')
    item_type = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    conn = get_db()

    query = 'SELECT * FROM budget_items WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if item_type:
        query += ' AND type = ?'
        params.append(item_type)
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY category, date DESC'

    items = conn.execute(query, params).fetchall()

    total_income = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) FROM budget_items WHERE type = "income"'
    ).fetchone()[0]
    total_expense = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) FROM budget_items WHERE type = "expense"'
    ).fetchone()[0]
    balance = total_income - total_expense

    conn.close()

    return render_template('index.html',
                           items=items,
                           categories=CATEGORIES,
                           selected_category=category,
                           selected_type=item_type,
                           date_from=date_from,
                           date_to=date_to,
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        category = request.form['category']
        item_type = request.form['type']
        date = request.form['date']
        notes = request.form.get('notes', '')

        conn = get_db()
        conn.execute(
            'INSERT INTO budget_items (name, amount, category, type, date, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (name, amount, category, item_type, date, notes)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html', categories=CATEGORIES)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        category = request.form['category']
        item_type = request.form['type']
        date = request.form['date']
        notes = request.form.get('notes', '')

        conn.execute(
            'UPDATE budget_items SET name=?, amount=?, category=?, type=?, date=?, notes=? WHERE id=?',
            (name, amount, category, item_type, date, notes, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    item = conn.execute('SELECT * FROM budget_items WHERE id = ?', (id,)).fetchone()
    conn.close()

    if not item:
        return redirect(url_for('index'))

    return render_template('edit.html', item=item, categories=CATEGORIES)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    conn = get_db()
    item = conn.execute('SELECT * FROM budget_items WHERE id = ?', (id,)).fetchone()

    if not item:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM budget_items WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', item=item)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
