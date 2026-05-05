from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r'C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\prescriptions_list\prescriptions_list.db'

FREQUENCIES = ['Once Daily', 'Twice Daily', 'Three Times Daily', 'As Needed', 'Weekly']
STATUSES = ['Active', 'Inactive', 'Discontinued']


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            prescribing_doctor TEXT,
            pharmacy TEXT,
            refill_date TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            filter_status TEXT DEFAULT '',
            filter_frequency TEXT DEFAULT '',
            filter_pharmacy TEXT DEFAULT '',
            filter_doctor TEXT DEFAULT '',
            sort_field TEXT DEFAULT 'medication_name',
            sort_dir TEXT DEFAULT 'asc'
        )
    ''')
    for col in ('filter_pharmacy', 'filter_doctor'):
        try:
            conn.execute(f"ALTER TABLE preferences ADD COLUMN {col} TEXT DEFAULT ''")
        except Exception:
            pass
    conn.execute('''
        INSERT OR IGNORE INTO preferences (id, filter_status, filter_frequency, filter_pharmacy, filter_doctor, sort_field, sort_dir)
        VALUES (1, '', '', '', '', 'medication_name', 'asc')
    ''')
    conn.commit()
    conn.close()


def get_prefs():
    conn = get_db()
    prefs = conn.execute('SELECT * FROM preferences WHERE id = 1').fetchone()
    conn.close()
    return prefs


def save_prefs(filter_status, filter_frequency, filter_pharmacy, filter_doctor, sort_field, sort_dir):
    conn = get_db()
    conn.execute('''
        UPDATE preferences SET filter_status=?, filter_frequency=?, filter_pharmacy=?, filter_doctor=?,
            sort_field=?, sort_dir=?
        WHERE id = 1
    ''', (filter_status, filter_frequency, filter_pharmacy, filter_doctor, sort_field, sort_dir))
    conn.commit()
    conn.close()


VALID_SORT_FIELDS = {'medication_name', 'dosage', 'frequency', 'prescribing_doctor',
                     'pharmacy', 'refill_date', 'status'}


@app.route('/', methods=['GET', 'POST'])
def index():
    prefs = get_prefs()

    if request.method == 'POST':
        filter_status = request.form.get('filter_status', '')
        filter_frequency = request.form.get('filter_frequency', '')
        filter_pharmacy = request.form.get('filter_pharmacy', '')
        filter_doctor = request.form.get('filter_doctor', '')
        sort_field = request.form.get('sort_field', 'medication_name')
        sort_dir = request.form.get('sort_dir', 'asc')
        save_prefs(filter_status, filter_frequency, filter_pharmacy, filter_doctor, sort_field, sort_dir)
        return redirect(url_for('index'))

    filter_status = prefs['filter_status']
    filter_frequency = prefs['filter_frequency']
    filter_pharmacy = prefs['filter_pharmacy'] or ''
    filter_doctor = prefs['filter_doctor'] or ''
    sort_field = prefs['sort_field'] if prefs['sort_field'] in VALID_SORT_FIELDS else 'medication_name'
    sort_dir = prefs['sort_dir'] if prefs['sort_dir'] in ('asc', 'desc') else 'asc'

    conn = get_db()
    query = 'SELECT * FROM prescriptions WHERE 1=1'
    params = []

    if filter_status:
        query += ' AND status = ?'
        params.append(filter_status)
    if filter_frequency:
        query += ' AND frequency = ?'
        params.append(filter_frequency)
    if filter_pharmacy:
        query += ' AND pharmacy = ?'
        params.append(filter_pharmacy)
    if filter_doctor:
        query += ' AND prescribing_doctor = ?'
        params.append(filter_doctor)

    query += f' ORDER BY {sort_field} {sort_dir.upper()}'
    prescriptions = conn.execute(query, params).fetchall()

    counts = {}
    for s in STATUSES:
        counts[s] = conn.execute(
            'SELECT COUNT(*) FROM prescriptions WHERE status = ?', (s,)
        ).fetchone()[0]
    counts['Total'] = conn.execute('SELECT COUNT(*) FROM prescriptions').fetchone()[0]

    pharmacies = [r[0] for r in conn.execute(
        "SELECT DISTINCT pharmacy FROM prescriptions WHERE pharmacy IS NOT NULL AND pharmacy != '' ORDER BY pharmacy"
    ).fetchall()]
    doctors = [r[0] for r in conn.execute(
        "SELECT DISTINCT prescribing_doctor FROM prescriptions WHERE prescribing_doctor IS NOT NULL AND prescribing_doctor != '' ORDER BY prescribing_doctor"
    ).fetchall()]

    conn.close()

    return render_template('index.html',
                           prescriptions=prescriptions,
                           counts=counts,
                           filter_status=filter_status,
                           filter_frequency=filter_frequency,
                           filter_pharmacy=filter_pharmacy,
                           filter_doctor=filter_doctor,
                           sort_field=sort_field,
                           sort_dir=sort_dir,
                           statuses=STATUSES,
                           frequencies=FREQUENCIES,
                           pharmacies=pharmacies,
                           doctors=doctors)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        medication_name = request.form['medication_name'].strip()
        dosage = request.form['dosage'].strip()
        frequency = request.form['frequency']
        prescribing_doctor = request.form.get('prescribing_doctor', '').strip()
        pharmacy = request.form.get('pharmacy', '').strip()
        refill_date = request.form.get('refill_date', '')
        status = request.form['status']
        notes = request.form.get('notes', '').strip()

        conn = get_db()
        conn.execute('''
            INSERT INTO prescriptions (medication_name, dosage, frequency, prescribing_doctor,
                pharmacy, refill_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (medication_name, dosage, frequency, prescribing_doctor, pharmacy, refill_date, status, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html', statuses=STATUSES, frequencies=FREQUENCIES)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    item = conn.execute('SELECT * FROM prescriptions WHERE id = ?', (id,)).fetchone()

    if not item:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        medication_name = request.form['medication_name'].strip()
        dosage = request.form['dosage'].strip()
        frequency = request.form['frequency']
        prescribing_doctor = request.form.get('prescribing_doctor', '').strip()
        pharmacy = request.form.get('pharmacy', '').strip()
        refill_date = request.form.get('refill_date', '')
        status = request.form['status']
        notes = request.form.get('notes', '').strip()

        conn.execute('''
            UPDATE prescriptions SET medication_name=?, dosage=?, frequency=?, prescribing_doctor=?,
                pharmacy=?, refill_date=?, status=?, notes=?
            WHERE id=?
        ''', (medication_name, dosage, frequency, prescribing_doctor, pharmacy, refill_date, status, notes, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', item=item, statuses=STATUSES, frequencies=FREQUENCIES)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    conn = get_db()
    item = conn.execute('SELECT * FROM prescriptions WHERE id = ?', (id,)).fetchone()

    if not item:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM prescriptions WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', item=item)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
