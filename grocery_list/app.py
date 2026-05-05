import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grocery.db')

CATEGORIES = ['Produce', 'Dairy', 'Meat', 'Bakery', 'Frozen',
              'Beverages', 'Snacks', 'Pantry', 'Household', 'Other']

UNITS = ['', 'ea', 'lbs', 'oz', 'kg', 'g', 'gal', 'qt', 'pt', 'fl oz',
         'L', 'mL', 'pkg', 'box', 'can', 'bag', 'bunch', 'dozen']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            quantity REAL DEFAULT 1,
            unit TEXT DEFAULT '',
            is_bought INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()


@app.route('/')
def index():
    db = get_db()
    filter_category = request.args.get('category', 'All')
    filter_status = request.args.get('status', 'All')
    sort_by = request.args.get('sort', 'created_at')
    sort_dir = request.args.get('dir', 'desc')

    valid_sorts = {'name', 'category', 'created_at', 'is_bought'}
    if sort_by not in valid_sorts:
        sort_by = 'created_at'
    order = 'ASC' if sort_dir == 'asc' else 'DESC'

    query = 'SELECT * FROM items WHERE 1=1'
    params = []

    if filter_category != 'All':
        query += ' AND category = ?'
        params.append(filter_category)

    if filter_status == 'Needed':
        query += ' AND is_bought = 0'
    elif filter_status == 'Bought':
        query += ' AND is_bought = 1'

    query += f' ORDER BY {sort_by} {order}'

    items = db.execute(query, params).fetchall()

    total = db.execute('SELECT COUNT(*) FROM items').fetchone()[0]
    bought = db.execute('SELECT COUNT(*) FROM items WHERE is_bought = 1').fetchone()[0]
    needed = total - bought

    next_dir = 'asc' if sort_dir == 'desc' else 'desc'

    return render_template('index.html',
                           items=items,
                           categories=CATEGORIES,
                           filter_category=filter_category,
                           filter_status=filter_status,
                           sort_by=sort_by,
                           sort_dir=sort_dir,
                           next_dir=next_dir,
                           total=total,
                           bought=bought,
                           needed=needed)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form.get('category', 'Other')
        quantity = request.form.get('quantity', '1') or '1'
        unit = request.form.get('unit', '')
        notes = request.form.get('notes', '').strip()

        if name:
            db = get_db()
            db.execute(
                'INSERT INTO items (name, category, quantity, unit, notes) VALUES (?, ?, ?, ?, ?)',
                (name, category, float(quantity), unit, notes)
            )
            db.commit()
        return redirect(url_for('index'))

    return render_template('add.html', categories=CATEGORIES, units=UNITS)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if item is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form.get('category', 'Other')
        quantity = request.form.get('quantity', '1') or '1'
        unit = request.form.get('unit', '')
        notes = request.form.get('notes', '').strip()

        if name:
            db.execute(
                'UPDATE items SET name=?, category=?, quantity=?, unit=?, notes=? WHERE id=?',
                (name, category, float(quantity), unit, notes, item_id)
            )
            db.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', item=item, categories=CATEGORIES, units=UNITS)


@app.route('/toggle/<int:item_id>', methods=['POST'])
def toggle(item_id):
    db = get_db()
    db.execute('UPDATE items SET is_bought = NOT is_bought WHERE id = ?', (item_id,))
    db.commit()
    return redirect(request.referrer or url_for('index'))


@app.route('/delete/<int:item_id>')
def delete_confirm(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if item is None:
        return redirect(url_for('index'))
    return render_template('delete_confirm.html', item=item)


@app.route('/delete/<int:item_id>/confirm', methods=['POST'])
def delete(item_id):
    db = get_db()
    db.execute('DELETE FROM items WHERE id = ?', (item_id,))
    db.commit()
    return redirect(url_for('index'))


@app.route('/clear_bought', methods=['POST'])
def clear_bought():
    db = get_db()
    db.execute('DELETE FROM items WHERE is_bought = 1')
    db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
