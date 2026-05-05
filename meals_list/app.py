import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'meals-secret-key'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meals.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity TEXT,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()


# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    filter_name = request.args.get('filter_name', session.get('filter_name', ''))
    sort_field  = request.args.get('sort_field',  session.get('sort_field',  'name'))
    sort_dir    = request.args.get('sort_dir',    session.get('sort_dir',    'asc'))

    # persist
    session['filter_name'] = filter_name
    session['sort_field']  = sort_field
    session['sort_dir']    = sort_dir

    allowed_fields = {'name', 'created_at'}
    if sort_field not in allowed_fields:
        sort_field = 'name'
    order = 'ASC' if sort_dir == 'asc' else 'DESC'

    conn = get_db()
    meals = conn.execute(
        f'SELECT m.*, COUNT(i.id) AS ingredient_count '
        f'FROM meals m LEFT JOIN ingredients i ON i.meal_id = m.id '
        f'WHERE m.name LIKE ? '
        f'GROUP BY m.id '
        f'ORDER BY m.{sort_field} {order}',
        (f'%{filter_name}%',)
    ).fetchall()
    conn.close()

    return render_template('index.html',
                           meals=meals,
                           filter_name=filter_name,
                           sort_field=sort_field,
                           sort_dir=sort_dir)


# ── Meals CRUD ─────────────────────────────────────────────────────────────────

@app.route('/meal/add', methods=['GET', 'POST'])
def meal_add():
    if request.method == 'POST':
        name        = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            conn = get_db()
            conn.execute('INSERT INTO meals (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('meal_add.html')


@app.route('/meal/<int:meal_id>')
def meal_view(meal_id):
    conn = get_db()
    meal        = conn.execute('SELECT * FROM meals WHERE id = ?', (meal_id,)).fetchone()
    ingredients = conn.execute(
        'SELECT * FROM ingredients WHERE meal_id = ? ORDER BY name ASC', (meal_id,)
    ).fetchall()
    conn.close()
    if not meal:
        return redirect(url_for('index'))
    return render_template('meal_view.html', meal=meal, ingredients=ingredients)


@app.route('/meal/<int:meal_id>/edit', methods=['GET', 'POST'])
def meal_edit(meal_id):
    conn = get_db()
    meal = conn.execute('SELECT * FROM meals WHERE id = ?', (meal_id,)).fetchone()
    if not meal:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name        = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            conn.execute('UPDATE meals SET name = ?, description = ? WHERE id = ?',
                         (name, description, meal_id))
            conn.commit()
        conn.close()
        return redirect(url_for('meal_view', meal_id=meal_id))

    conn.close()
    return render_template('meal_edit.html', meal=meal)


@app.route('/meal/<int:meal_id>/delete', methods=['GET', 'POST'])
def meal_delete(meal_id):
    conn = get_db()
    meal = conn.execute('SELECT * FROM meals WHERE id = ?', (meal_id,)).fetchone()
    if not meal:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM ingredients WHERE meal_id = ?', (meal_id,))
        conn.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('meal_delete.html', meal=meal)


# ── Ingredients CRUD ───────────────────────────────────────────────────────────

@app.route('/meal/<int:meal_id>/ingredient/add', methods=['GET', 'POST'])
def ingredient_add(meal_id):
    conn = get_db()
    meal = conn.execute('SELECT * FROM meals WHERE id = ?', (meal_id,)).fetchone()
    if not meal:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name     = request.form['name'].strip()
        quantity = request.form.get('quantity', '').strip()
        unit     = request.form.get('unit', '').strip()
        if name:
            conn.execute(
                'INSERT INTO ingredients (meal_id, name, quantity, unit) VALUES (?, ?, ?, ?)',
                (meal_id, name, quantity, unit)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('meal_view', meal_id=meal_id))

    conn.close()
    return render_template('ingredient_add.html', meal=meal)


@app.route('/ingredient/<int:ing_id>/edit', methods=['GET', 'POST'])
def ingredient_edit(ing_id):
    conn = get_db()
    ing  = conn.execute('SELECT * FROM ingredients WHERE id = ?', (ing_id,)).fetchone()
    if not ing:
        conn.close()
        return redirect(url_for('index'))

    meal = conn.execute('SELECT * FROM meals WHERE id = ?', (ing['meal_id'],)).fetchone()

    if request.method == 'POST':
        name     = request.form['name'].strip()
        quantity = request.form.get('quantity', '').strip()
        unit     = request.form.get('unit', '').strip()
        if name:
            conn.execute(
                'UPDATE ingredients SET name = ?, quantity = ?, unit = ? WHERE id = ?',
                (name, quantity, unit, ing_id)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('meal_view', meal_id=ing['meal_id']))

    conn.close()
    return render_template('ingredient_edit.html', ing=ing, meal=meal)


@app.route('/ingredient/<int:ing_id>/delete', methods=['GET', 'POST'])
def ingredient_delete(ing_id):
    conn = get_db()
    ing  = conn.execute('SELECT * FROM ingredients WHERE id = ?', (ing_id,)).fetchone()
    if not ing:
        conn.close()
        return redirect(url_for('index'))

    meal = conn.execute('SELECT * FROM meals WHERE id = ?', (ing['meal_id'],)).fetchone()

    if request.method == 'POST':
        meal_id = ing['meal_id']
        conn.execute('DELETE FROM ingredients WHERE id = ?', (ing_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('meal_view', meal_id=meal_id))

    conn.close()
    return render_template('ingredient_delete.html', ing=ing, meal=meal)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
