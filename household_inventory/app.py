from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')

SORT_FIELDS = {
    'name': 'name',
    'category': 'category',
    'location': 'location',
    'quantity': 'quantity',
    'condition': 'condition',
    'purchase_date': 'purchase_date',
    'purchase_price': 'purchase_price',
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                location TEXT,
                quantity INTEGER DEFAULT 1,
                condition TEXT,
                purchase_date TEXT,
                purchase_price REAL,
                notes TEXT
            )
        ''')

@app.route('/')
def index():
    filter_category = request.args.get('category', '')
    filter_location = request.args.get('location', '')
    filter_condition = request.args.get('condition', '')
    sort_by = request.args.get('sort_by', 'location')
    sort_dir = request.args.get('sort_dir', 'asc')

    if sort_by not in SORT_FIELDS:
        sort_by = 'location'
    order = 'ASC' if sort_dir == 'asc' else 'DESC'

    query = 'SELECT * FROM items WHERE 1=1'
    params = []

    if filter_category:
        query += ' AND category = ?'
        params.append(filter_category)
    if filter_location:
        query += ' AND location = ?'
        params.append(filter_location)
    if filter_condition:
        query += ' AND condition = ?'
        params.append(filter_condition)

    query += f' ORDER BY {SORT_FIELDS[sort_by]} {order}'

    with get_db() as conn:
        items = conn.execute(query, params).fetchall()
        categories = [r[0] for r in conn.execute('SELECT DISTINCT category FROM items WHERE category IS NOT NULL ORDER BY category').fetchall()]
        locations = [r[0] for r in conn.execute('SELECT DISTINCT location FROM items WHERE location IS NOT NULL ORDER BY location').fetchall()]
        conditions = [r[0] for r in conn.execute('SELECT DISTINCT condition FROM items WHERE condition IS NOT NULL ORDER BY condition').fetchall()]
        total = conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]

    return render_template('index.html',
        items=items,
        categories=categories,
        locations=locations,
        conditions=conditions,
        filter_category=filter_category,
        filter_location=filter_location,
        filter_condition=filter_condition,
        sort_by=sort_by,
        sort_dir=sort_dir,
        total=total,
        sort_fields=SORT_FIELDS,
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        location = request.form['location'].strip()
        quantity = request.form['quantity'].strip() or '1'
        condition = request.form['condition'].strip()
        purchase_date = request.form['purchase_date'].strip()
        purchase_price = request.form['purchase_price'].strip()
        notes = request.form['notes'].strip()

        price = float(purchase_price) if purchase_price else None
        qty = int(quantity) if quantity else 1

        with get_db() as conn:
            conn.execute('''
                INSERT INTO items (name, category, location, quantity, condition, purchase_date, purchase_price, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, location, qty, condition, purchase_date, price, notes))

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    with get_db() as conn:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()

    if not item:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        location = request.form['location'].strip()
        quantity = request.form['quantity'].strip() or '1'
        condition = request.form['condition'].strip()
        purchase_date = request.form['purchase_date'].strip()
        purchase_price = request.form['purchase_price'].strip()
        notes = request.form['notes'].strip()

        price = float(purchase_price) if purchase_price else None
        qty = int(quantity) if quantity else 1

        with get_db() as conn:
            conn.execute('''
                UPDATE items SET name=?, category=?, location=?, quantity=?, condition=?,
                purchase_date=?, purchase_price=?, notes=? WHERE id=?
            ''', (name, category, location, qty, condition, purchase_date, price, notes, item_id))

        return redirect(url_for('index'))

    return render_template('edit.html', item=item)

@app.route('/delete/<int:item_id>', methods=['GET', 'POST'])
def delete(item_id):
    with get_db() as conn:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()

    if not item:
        return redirect(url_for('index'))

    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
        return redirect(url_for('index'))

    return render_template('confirm_delete.html', item=item)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
