import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'family_tree.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date TEXT,
            death_date TEXT,
            gender TEXT,
            notes TEXT,
            father_id INTEGER REFERENCES people(id),
            mother_id INTEGER REFERENCES people(id),
            spouse_id INTEGER REFERENCES people(id)
        )
    """)
    db.commit()
    db.close()


def build_tree(people_dict):
    for pid in people_dict:
        people_dict[pid]['children'] = []

    assigned = set()
    for pid, person in people_dict.items():
        father_id = person['father_id']
        mother_id = person['mother_id']
        if father_id and father_id in people_dict:
            people_dict[father_id]['children'].append(pid)
            assigned.add(pid)
        elif mother_id and mother_id in people_dict:
            people_dict[mother_id]['children'].append(pid)
            assigned.add(pid)

    roots = [pid for pid in people_dict if pid not in assigned]
    return roots


@app.route('/')
def index():
    db = get_db()
    rows = db.execute("SELECT * FROM people ORDER BY last_name, first_name").fetchall()
    people_dict = {row['id']: dict(row) for row in rows}
    roots = build_tree(people_dict)
    return render_template('index.html', people=people_dict, roots=roots)


@app.route('/person/add', methods=['GET', 'POST'])
def person_add():
    db = get_db()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form.get('birth_date') or None
        death_date = request.form.get('death_date') or None
        gender = request.form.get('gender') or None
        notes = request.form.get('notes') or None
        father_id = request.form.get('father_id') or None
        mother_id = request.form.get('mother_id') or None
        spouse_id = request.form.get('spouse_id') or None

        cur = db.execute(
            """INSERT INTO people
               (first_name, last_name, birth_date, death_date, gender, notes, father_id, mother_id, spouse_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (first_name, last_name, birth_date, death_date, gender, notes, father_id, mother_id, spouse_id)
        )
        new_id = cur.lastrowid

        if spouse_id:
            db.execute("UPDATE people SET spouse_id = ? WHERE id = ?", (new_id, spouse_id))

        db.commit()
        return redirect(url_for('index'))

    people = db.execute("SELECT id, first_name, last_name FROM people ORDER BY last_name, first_name").fetchall()
    return render_template('person_form.html', person=None, people=people, title='Add Person')


@app.route('/person/<int:pid>')
def person_detail(pid):
    db = get_db()
    person = db.execute("SELECT * FROM people WHERE id = ?", (pid,)).fetchone()
    if not person:
        return redirect(url_for('index'))

    father = db.execute("SELECT * FROM people WHERE id = ?", (person['father_id'],)).fetchone() if person['father_id'] else None
    mother = db.execute("SELECT * FROM people WHERE id = ?", (person['mother_id'],)).fetchone() if person['mother_id'] else None
    spouse = db.execute("SELECT * FROM people WHERE id = ?", (person['spouse_id'],)).fetchone() if person['spouse_id'] else None
    children = db.execute(
        "SELECT * FROM people WHERE father_id = ? OR mother_id = ? ORDER BY last_name, first_name",
        (pid, pid)
    ).fetchall()

    return render_template('person_detail.html', person=person, father=father, mother=mother, spouse=spouse, children=children)


@app.route('/person/<int:pid>/edit', methods=['GET', 'POST'])
def person_edit(pid):
    db = get_db()
    person = db.execute("SELECT * FROM people WHERE id = ?", (pid,)).fetchone()
    if not person:
        return redirect(url_for('index'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form.get('birth_date') or None
        death_date = request.form.get('death_date') or None
        gender = request.form.get('gender') or None
        notes = request.form.get('notes') or None
        father_id = request.form.get('father_id') or None
        mother_id = request.form.get('mother_id') or None
        new_spouse_id = request.form.get('spouse_id') or None
        old_spouse_id = person['spouse_id']

        db.execute(
            """UPDATE people SET first_name=?, last_name=?, birth_date=?, death_date=?,
               gender=?, notes=?, father_id=?, mother_id=?, spouse_id=? WHERE id=?""",
            (first_name, last_name, birth_date, death_date, gender, notes, father_id, mother_id, new_spouse_id, pid)
        )

        if old_spouse_id and str(old_spouse_id) != str(new_spouse_id):
            db.execute("UPDATE people SET spouse_id = NULL WHERE id = ?", (old_spouse_id,))
        if new_spouse_id:
            db.execute("UPDATE people SET spouse_id = ? WHERE id = ?", (pid, new_spouse_id))

        db.commit()
        return redirect(url_for('person_detail', pid=pid))

    people = db.execute(
        "SELECT id, first_name, last_name FROM people WHERE id != ? ORDER BY last_name, first_name",
        (pid,)
    ).fetchall()
    return render_template('person_form.html', person=dict(person), people=people, title='Edit Person')


@app.route('/person/<int:pid>/delete', methods=['GET', 'POST'])
def person_delete(pid):
    db = get_db()
    person = db.execute("SELECT * FROM people WHERE id = ?", (pid,)).fetchone()
    if not person:
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.execute("UPDATE people SET father_id = NULL WHERE father_id = ?", (pid,))
        db.execute("UPDATE people SET mother_id = NULL WHERE mother_id = ?", (pid,))
        db.execute("UPDATE people SET spouse_id = NULL WHERE spouse_id = ?", (pid,))
        db.execute("DELETE FROM people WHERE id = ?", (pid,))
        db.commit()
        return redirect(url_for('index'))

    return render_template('person_delete.html', person=person)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
