import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'travel.db')

SORT_FIELDS = ['destination', 'start_date', 'end_date', 'travelers', 'status', 'budget', 'created_at']
STATUS_OPTIONS = ['Planned', 'Booked', 'In Progress', 'Completed', 'Cancelled']

# ── DB helpers ────────────────────────────────────────────────────────────────

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
        CREATE TABLE IF NOT EXISTS travel_plans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT    NOT NULL,
            start_date  DATE,
            end_date    DATE,
            travelers   INTEGER DEFAULT 1,
            status      TEXT    DEFAULT 'Planned',
            budget      REAL    DEFAULT 0.0,
            notes       TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()

# ── Persistent filter/sort via session-like query params ──────────────────────

def safe_sort(field):
    return field if field in SORT_FIELDS else 'start_date'

def safe_order(order):
    return 'DESC' if order == 'DESC' else 'ASC'

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()

    filter_destination = request.args.get('filter_destination', '')
    filter_status      = request.args.get('filter_status', '')
    sort_field         = safe_sort(request.args.get('sort_field', 'start_date'))
    sort_order         = safe_order(request.args.get('sort_order', 'ASC'))

    query  = 'SELECT * FROM travel_plans WHERE 1=1'
    params = []

    if filter_destination:
        query += ' AND destination LIKE ?'
        params.append(f'%{filter_destination}%')
    if filter_status:
        query += ' AND status = ?'
        params.append(filter_status)

    query += f' ORDER BY {sort_field} {sort_order}'

    plans = db.execute(query, params).fetchall()

    return render_template('index.html',
        plans=plans,
        filter_destination=filter_destination,
        filter_status=filter_status,
        sort_field=sort_field,
        sort_order=sort_order,
        sort_fields=SORT_FIELDS,
        status_options=STATUS_OPTIONS,
    )


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        destination = request.form['destination'].strip()
        start_date  = request.form['start_date'] or None
        end_date    = request.form['end_date'] or None
        travelers   = request.form.get('travelers', 1)
        status      = request.form.get('status', 'Planned')
        budget      = request.form.get('budget', 0.0)
        notes       = request.form.get('notes', '').strip()

        db = get_db()
        db.execute(
            'INSERT INTO travel_plans (destination, start_date, end_date, travelers, status, budget, notes) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (destination, start_date, end_date, travelers, status, budget, notes)
        )
        db.commit()
        return redirect(url_for('index'))

    return render_template('add.html', status_options=STATUS_OPTIONS)


@app.route('/edit/<int:plan_id>', methods=['GET', 'POST'])
def edit(plan_id):
    db   = get_db()
    plan = db.execute('SELECT * FROM travel_plans WHERE id = ?', (plan_id,)).fetchone()

    if plan is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        destination = request.form['destination'].strip()
        start_date  = request.form['start_date'] or None
        end_date    = request.form['end_date'] or None
        travelers   = request.form.get('travelers', 1)
        status      = request.form.get('status', 'Planned')
        budget      = request.form.get('budget', 0.0)
        notes       = request.form.get('notes', '').strip()

        # detect changed key fields and ask for confirmation
        changed = []
        if destination != plan['destination']:
            changed.append(f"Destination: '{plan['destination']}' → '{destination}'")
        if str(start_date) != str(plan['start_date']):
            changed.append(f"Start date: '{plan['start_date']}' → '{start_date}'")
        if str(end_date) != str(plan['end_date']):
            changed.append(f"End date: '{plan['end_date']}' → '{end_date}'")
        if str(status) != str(plan['status']):
            changed.append(f"Status: '{plan['status']}' → '{status}'")

        if changed and not request.form.get('confirmed'):
            return render_template('confirm_edit.html',
                plan=plan,
                changed=changed,
                form_data=request.form,
                status_options=STATUS_OPTIONS,
            )

        db.execute(
            'UPDATE travel_plans SET destination=?, start_date=?, end_date=?, travelers=?, status=?, budget=?, notes=? '
            'WHERE id=?',
            (destination, start_date, end_date, travelers, status, budget, notes, plan_id)
        )
        db.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', plan=plan, status_options=STATUS_OPTIONS)


@app.route('/delete/<int:plan_id>', methods=['GET', 'POST'])
def delete(plan_id):
    db   = get_db()
    plan = db.execute('SELECT * FROM travel_plans WHERE id = ?', (plan_id,)).fetchone()

    if plan is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.execute('DELETE FROM travel_plans WHERE id = ?', (plan_id,))
        db.commit()
        return redirect(url_for('index'))

    return render_template('confirm_delete.html', plan=plan)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
