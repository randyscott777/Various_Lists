import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'images_app_secret_key'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT,
            description TEXT,
            category TEXT,
            tags TEXT,
            date_added TEXT DEFAULT (date('now'))
        )
    ''')
    conn.commit()
    conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    # Persist filter/sort in session
    filter_category = request.args.get('filter_category', session.get('filter_category', ''))
    filter_tags = request.args.get('filter_tags', session.get('filter_tags', ''))
    sort_by = request.args.get('sort_by', session.get('sort_by', 'date_added'))
    sort_dir = request.args.get('sort_dir', session.get('sort_dir', 'DESC'))

    # Handle reset
    if 'reset' in request.args:
        filter_category = ''
        filter_tags = ''
        sort_by = 'date_added'
        sort_dir = 'DESC'

    session['filter_category'] = filter_category
    session['filter_tags'] = filter_tags
    session['sort_by'] = sort_by
    session['sort_dir'] = sort_dir

    valid_columns = ['id', 'title', 'category', 'tags', 'date_added']
    if sort_by not in valid_columns:
        sort_by = 'date_added'
    if sort_dir not in ['ASC', 'DESC']:
        sort_dir = 'DESC'

    conn = get_db()
    query = 'SELECT * FROM images WHERE 1=1'
    params = []

    if filter_category:
        query += ' AND category LIKE ?'
        params.append(f'%{filter_category}%')
    if filter_tags:
        query += ' AND tags LIKE ?'
        params.append(f'%{filter_tags}%')

    query += f' ORDER BY {sort_by} {sort_dir}'
    images = conn.execute(query, params).fetchall()

    categories = [r[0] for r in conn.execute(
        'SELECT DISTINCT category FROM images WHERE category IS NOT NULL AND category != "" ORDER BY category'
    ).fetchall()]
    total = conn.execute('SELECT COUNT(*) FROM images').fetchone()[0]
    conn.close()

    return render_template('index.html',
                           images=images,
                           categories=categories,
                           filter_category=filter_category,
                           filter_tags=filter_tags,
                           sort_by=sort_by,
                           sort_dir=sort_dir,
                           total=total)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        filename = ''

        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            filename = fname

        conn = get_db()
        conn.execute(
            'INSERT INTO images (title, filename, description, category, tags) VALUES (?, ?, ?, ?, ?)',
            (title, filename, description, category, tags)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/view/<int:image_id>')
def view(image_id):
    conn = get_db()
    image = conn.execute('SELECT * FROM images WHERE id = ?', (image_id,)).fetchone()
    conn.close()
    if not image:
        return redirect(url_for('index'))
    return render_template('view.html', image=image)


@app.route('/edit/<int:image_id>', methods=['GET', 'POST'])
def edit(image_id):
    conn = get_db()
    image = conn.execute('SELECT * FROM images WHERE id = ?', (image_id,)).fetchone()

    if not image:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        filename = image['filename']

        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            filename = fname

        conn.execute(
            'UPDATE images SET title=?, filename=?, description=?, category=?, tags=? WHERE id=?',
            (title, filename, description, category, tags, image_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', image=image)


@app.route('/delete/<int:image_id>', methods=['GET', 'POST'])
def delete(image_id):
    conn = get_db()
    image = conn.execute('SELECT * FROM images WHERE id = ?', (image_id,)).fetchone()

    if not image:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Delete file from disk if it exists
        if image['filename']:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
        conn.execute('DELETE FROM images WHERE id = ?', (image_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', image=image)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5009)
