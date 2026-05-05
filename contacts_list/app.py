import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'contacts-secret-key-2026'

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contacts.db')


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()


SORTABLE_FIELDS = ['last_name', 'first_name', 'company', 'city', 'state', 'email', 'phone']
FILTERABLE_FIELDS = ['first_name', 'last_name', 'company', 'city', 'state', 'email', 'phone', 'address', 'zip', 'notes']


@app.route('/')
def index():
    filter_text = request.args.get('filter_text', '').strip()
    filter_field = request.args.get('filter_field', '').strip()
    sort_field = request.args.get('sort_field', 'last_name')
    sort_dir = request.args.get('sort_dir', 'asc')

    if sort_field not in SORTABLE_FIELDS:
        sort_field = 'last_name'
    if sort_dir not in ('asc', 'desc'):
        sort_dir = 'asc'
    if filter_field not in FILTERABLE_FIELDS:
        filter_field = ''

    conn = get_db()
    if filter_text:
        like = f'%{filter_text}%'
        if filter_field:
            rows = conn.execute(f'''
                SELECT * FROM contacts
                WHERE {filter_field} LIKE ?
                ORDER BY {sort_field} {sort_dir.upper()}
            ''', (like,)).fetchall()
        else:
            rows = conn.execute(f'''
                SELECT * FROM contacts
                WHERE first_name LIKE ? OR last_name LIKE ? OR company LIKE ?
                   OR city LIKE ? OR state LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY {sort_field} {sort_dir.upper()}
            ''', (like, like, like, like, like, like, like)).fetchall()
    else:
        rows = conn.execute(f'''
            SELECT * FROM contacts
            ORDER BY {sort_field} {sort_dir.upper()}
        ''').fetchall()
    conn.close()

    return render_template('index.html', contacts=rows,
                           filter_text=filter_text,
                           filter_field=filter_field,
                           sort_field=sort_field,
                           sort_dir=sort_dir,
                           sortable_fields=SORTABLE_FIELDS)


@app.route('/filter')
def filter_contacts():
    return render_template('filter.html',
                           filter_text=request.args.get('filter_text', ''),
                           filter_field=request.args.get('filter_field', ''),
                           sort_field=request.args.get('sort_field', 'last_name'),
                           sort_dir=request.args.get('sort_dir', 'asc'),
                           sortable_fields=SORTABLE_FIELDS,
                           filterable_fields=FILTERABLE_FIELDS)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db()
        conn.execute('''
            INSERT INTO contacts (first_name, last_name, email, phone, company, address, city, state, zip, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['first_name'].strip(),
            request.form['last_name'].strip(),
            request.form['email'].strip(),
            request.form['phone'].strip(),
            request.form['company'].strip(),
            request.form['address'].strip(),
            request.form['city'].strip(),
            request.form['state'].strip(),
            request.form['zip'].strip(),
            request.form['notes'].strip(),
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/view/<int:contact_id>')
def view(contact_id):
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    conn.close()
    if contact is None:
        return redirect(url_for('index'))
    return render_template('view.html', contact=contact)


@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit(contact_id):
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if contact is None:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('''
            UPDATE contacts SET first_name=?, last_name=?, email=?, phone=?,
            company=?, address=?, city=?, state=?, zip=?, notes=?
            WHERE id=?
        ''', (
            request.form['first_name'].strip(),
            request.form['last_name'].strip(),
            request.form['email'].strip(),
            request.form['phone'].strip(),
            request.form['company'].strip(),
            request.form['address'].strip(),
            request.form['city'].strip(),
            request.form['state'].strip(),
            request.form['zip'].strip(),
            request.form['notes'].strip(),
            contact_id,
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('view', contact_id=contact_id))

    conn.close()
    return render_template('edit.html', contact=contact)


@app.route('/delete/<int:contact_id>', methods=['GET', 'POST'])
def delete(contact_id):
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if contact is None:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', contact=contact)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
