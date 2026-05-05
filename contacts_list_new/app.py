# Created by Claude Code - create a contacts list app with filter/sort/favorites/archive, vibrant Monday.com-style UI, stats dashboard, sticky header, and confirm-before-delete
import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contacts.db')

CONTACT_TYPES = ['Friend', 'Family', 'Work', 'Acquaintance', 'Other']
SORTABLE_FIELDS = ['last_name', 'first_name', 'company', 'contact_type', 'city', 'state', 'email', 'phone', 'favorite', 'active', 'created_date']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            company TEXT DEFAULT '',
            contact_type TEXT NOT NULL DEFAULT 'Friend',
            favorite INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            address TEXT DEFAULT '',
            city TEXT DEFAULT '',
            state TEXT DEFAULT '',
            zip TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_date TEXT DEFAULT '',
            updated_at TEXT DEFAULT ''
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ui_prefs (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            filter_contact_type TEXT DEFAULT '',
            sort_field TEXT DEFAULT 'last_name',
            sort_dir TEXT DEFAULT 'asc'
        )
    ''')
    row = conn.execute('SELECT id FROM ui_prefs WHERE id = 1').fetchone()
    if not row:
        conn.execute("INSERT INTO ui_prefs (id) VALUES (1)")
    count = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    if count == 0:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now().strftime('%Y-%m-%d')
        seed = [
            ('Alice', 'Johnson', 'alice@email.com', '555-0101', 'Sunrise Co', 'Friend', 1, 1, '123 Oak St', 'Austin', 'TX', '78701', 'Met at conference'),
            ('Bob', 'Martinez', 'bob@work.com', '555-0102', 'TechCorp', 'Work', 0, 1, '456 Elm Ave', 'Dallas', 'TX', '75201', 'Project lead'),
            ('Carol', 'Smith', 'carol@family.com', '555-0103', '', 'Family', 1, 1, '789 Pine Rd', 'Houston', 'TX', '77001', 'Sister'),
            ('David', 'Lee', 'david@email.com', '555-0104', 'Freelance', 'Acquaintance', 0, 1, '', 'Seattle', 'WA', '98101', 'Neighbor'),
            ('Emma', 'Wilson', 'emma@work.com', '555-0105', 'DesignHub', 'Work', 1, 1, '321 Maple Dr', 'Portland', 'OR', '97201', 'Designer'),
            ('Frank', 'Brown', 'frank@email.com', '555-0106', '', 'Friend', 0, 0, '', 'Chicago', 'IL', '60601', 'Old college friend'),
            ('Grace', 'Davis', 'grace@family.com', '555-0107', '', 'Family', 1, 1, '654 Cedar Ln', 'Austin', 'TX', '78702', 'Mom'),
            ('Henry', 'Taylor', 'henry@corp.com', '555-0108', 'MegaCorp', 'Work', 0, 1, '987 Birch Blvd', 'New York', 'NY', '10001', 'Client contact'),
            ('Iris', 'Anderson', '', '555-0109', '', 'Other', 0, 1, '', 'Denver', 'CO', '80201', 'Book club'),
            ('Jack', 'Thomas', 'jack@email.com', '555-0110', 'StartupXYZ', 'Acquaintance', 0, 0, '', 'Miami', 'FL', '33101', 'Met at meetup'),
            ('Karen', 'White', 'karen@family.com', '555-0111', '', 'Family', 1, 1, '111 Walnut St', 'Austin', 'TX', '78703', 'Aunt'),
            ('Liam', 'Harris', 'liam@work.com', '555-0112', 'TechCorp', 'Work', 0, 1, '222 Spruce Way', 'Dallas', 'TX', '75202', 'Colleague'),
        ]
        for s in seed:
            conn.execute('''
                INSERT INTO contacts (first_name, last_name, email, phone, company, contact_type, favorite, active, address, city, state, zip, notes, created_date, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (*s, today, now))
    conn.commit()
    conn.close()


@app.context_processor
def inject_globals():
    try:
        db = get_db()
        row = db.execute("SELECT MAX(updated_at) as lu FROM contacts").fetchone()
        last_updated = row['lu'] if row and row['lu'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {'last_updated': last_updated}


def get_prefs():
    db = get_db()
    row = db.execute('SELECT * FROM ui_prefs WHERE id = 1').fetchone()
    return {
        'filter_contact_type': row['filter_contact_type'] if row else '',
        'sort_field': row['sort_field'] if row else 'last_name',
        'sort_dir': row['sort_dir'] if row else 'asc',
    }


def save_prefs(fct, sf, sd):
    db = get_db()
    db.execute('UPDATE ui_prefs SET filter_contact_type=?, sort_field=?, sort_dir=? WHERE id=1',
               (fct, sf, sd))
    db.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fct = request.form.get('filter_contact_type', '')
        sf = request.form.get('sort_field', 'last_name')
        sd = request.form.get('sort_dir', 'asc')
        if sf not in SORTABLE_FIELDS:
            sf = 'last_name'
        if sd not in ('asc', 'desc'):
            sd = 'asc'
        save_prefs(fct, sf, sd)
        return redirect(url_for('index'))

    prefs = get_prefs()
    fct = prefs['filter_contact_type']
    sf = prefs['sort_field']
    sd = prefs['sort_dir']

    db = get_db()
    params = []
    where = []
    if fct and fct in CONTACT_TYPES:
        where.append('contact_type = ?')
        params.append(fct)
    where_clause = ('WHERE ' + ' AND '.join(where)) if where else ''
    contacts = db.execute(f'SELECT * FROM contacts {where_clause} ORDER BY {sf} {sd.upper()}', params).fetchall()

    total = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    favorites = db.execute('SELECT COUNT(*) FROM contacts WHERE favorite=1').fetchone()[0]
    active = db.execute('SELECT COUNT(*) FROM contacts WHERE active=1').fetchone()[0]
    archived = db.execute('SELECT COUNT(*) FROM contacts WHERE active=0').fetchone()[0]
    work = db.execute("SELECT COUNT(*) FROM contacts WHERE contact_type='Work'").fetchone()[0]
    family = db.execute("SELECT COUNT(*) FROM contacts WHERE contact_type='Family'").fetchone()[0]

    stats = {'total': total, 'favorites': favorites, 'active': active, 'archived': archived, 'work': work, 'family': family}
    return render_template('index.html', contacts=contacts, stats=stats,
                           filter_contact_type=fct, sort_field=sf, sort_dir=sd,
                           contact_types=CONTACT_TYPES, sortable_fields=SORTABLE_FIELDS)


@app.route('/clear')
def clear_prefs():
    save_prefs('', 'last_name', 'asc')
    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now().strftime('%Y-%m-%d')
        db = get_db()
        db.execute('''
            INSERT INTO contacts (first_name, last_name, email, phone, company, contact_type, favorite, active, address, city, state, zip, notes, created_date, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            request.form['first_name'].strip(),
            request.form['last_name'].strip(),
            request.form.get('email', '').strip(),
            request.form.get('phone', '').strip(),
            request.form.get('company', '').strip(),
            request.form.get('contact_type', 'Friend'),
            1 if request.form.get('favorite') else 0,
            1 if request.form.get('active') else 0,
            request.form.get('address', '').strip(),
            request.form.get('city', '').strip(),
            request.form.get('state', '').strip(),
            request.form.get('zip', '').strip(),
            request.form.get('notes', '').strip(),
            today, now,
        ))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add.html', contact_types=CONTACT_TYPES)


@app.route('/view/<int:cid>')
def view(cid):
    db = get_db()
    contact = db.execute('SELECT * FROM contacts WHERE id=?', (cid,)).fetchone()
    if contact is None:
        return redirect(url_for('index'))
    return render_template('view.html', contact=contact)


@app.route('/edit/<int:cid>', methods=['GET', 'POST'])
def edit(cid):
    db = get_db()
    contact = db.execute('SELECT * FROM contacts WHERE id=?', (cid,)).fetchone()
    if contact is None:
        return redirect(url_for('index'))
    if request.method == 'POST':
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('''
            UPDATE contacts SET first_name=?, last_name=?, email=?, phone=?, company=?, contact_type=?,
            favorite=?, active=?, address=?, city=?, state=?, zip=?, notes=?, updated_at=?
            WHERE id=?
        ''', (
            request.form['first_name'].strip(),
            request.form['last_name'].strip(),
            request.form.get('email', '').strip(),
            request.form.get('phone', '').strip(),
            request.form.get('company', '').strip(),
            request.form.get('contact_type', 'Friend'),
            1 if request.form.get('favorite') else 0,
            1 if request.form.get('active') else 0,
            request.form.get('address', '').strip(),
            request.form.get('city', '').strip(),
            request.form.get('state', '').strip(),
            request.form.get('zip', '').strip(),
            request.form.get('notes', '').strip(),
            now, cid,
        ))
        db.commit()
        return redirect(url_for('view', cid=cid))
    return render_template('edit.html', contact=contact, contact_types=CONTACT_TYPES)


@app.route('/toggle_favorite/<int:cid>', methods=['POST'])
def toggle_favorite(cid):
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute('UPDATE contacts SET favorite = 1 - favorite, updated_at=? WHERE id=?', (now, cid))
    db.commit()
    return redirect(url_for('index'))


@app.route('/toggle_active/<int:cid>', methods=['POST'])
def toggle_active(cid):
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute('UPDATE contacts SET active = 1 - active, updated_at=? WHERE id=?', (now, cid))
    db.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:cid>', methods=['GET'])
def delete(cid):
    db = get_db()
    contact = db.execute('SELECT * FROM contacts WHERE id=?', (cid,)).fetchone()
    if contact is None:
        return redirect(url_for('index'))
    return render_template('confirm_delete.html', contact=contact)


@app.route('/delete/<int:cid>/confirm', methods=['POST'])
def delete_confirm(cid):
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id=?', (cid,))
    db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5053)
