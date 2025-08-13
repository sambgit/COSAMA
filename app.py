from flask import Flask, render_template, request, redirect, session, flash, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # remplace par quelque chose de solide
app.permanent_session_lifetime = timedelta(hours=1)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )

# Initialisation des tables
def init_db():

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Supprime l’ancienne table
        # cur.execute('DROP TABLE IF EXISTS admins')
        # cur.execute("ALTER TABLE IF EXISTS super_admins ADD created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        cur.execute('''
                CREATE TABLE IF NOT EXISTS super_admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

        cur.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prenom TEXT NOT NULL,
                    nom TEXT NOT NULL,
                    tel TEXT NOT NULL,
                    nin TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        cur.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        conn.commit()

        # Créer un admin par défaut si aucun n’existe
        cur.execute("SELECT COUNT(*) FROM admins")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (
                "admin",
                generate_password_hash("admin123")
            ))
        conn.commit()

        # Créer un superadmin par défaut si aucun n’existe
        cur.execute("SELECT COUNT(*) FROM super_admins")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO super_admins (username, password) VALUES (?, ?)", (
                "superadmin",
                generate_password_hash("superadmin123")
            ))
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Erreur de connexion")


# Page client
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/reserve', methods=['POST'])
def reserve():
    prenom = request.form.get('prenom')
    nom = request.form.get('nom')
    tel = request.form.get('tel')
    nin = request.form.get('nin')

    conn = get_db_connection()
    cur = conn.cursor()

    # Vérification de redondance
    cur.execute('''
        SELECT COUNT(*) FROM reservations WHERE prenom=? AND nom=? AND nin=?
    ''', (prenom, nom, nin))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return "Client déjà enregistré", 409

    cur.execute('''
        INSERT INTO reservations (prenom, nom, tel, nin)
        VALUES (?, ?, ?, ?)
    ''', (prenom, nom, tel, nin))
    conn.commit()
    cur.close()
    conn.close()

    return render_template('confirmation.html', prenom=prenom, nom=nom)

@app.route('/super_admin/search', methods=['GET'])
def search_admin():
    a = request.args.get('a', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    if a:
        like_a = f"%{a}%"

        cur.execute("""
          SELECT id, username
          FROM admins
          WHERE id          LIKE ?
             OR username    LIKE ?

        """, (like_a, like_a))

    else:
        cur.execute("""
                  SELECT id, username
                  FROM admins
                  ORDER BY created_at DESC
                """)
    admins = cur.fetchall()
    conn.close()
    if request.args.get('ajax'):
        # Prépare la liste de dicts
        results = [{
            'id': r[0],
            'username': r[1],
        } for r in admins]
        return jsonify(results)

    return render_template('super_dashboard.html', admins=admins, a=a)


@app.route('/super_admin/create', methods=['GET', 'POST'])
def create_admin():
    if 'super_admins' not in session:
        return redirect('/login_super')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO admins "
                        "(username, password) VALUES (?, ?)", (
                            username, hashed_pw))
            conn.commit()
            message = "Admin ajouté avec succès"
        except psycopg2.IntegrityError:
            message = "Ce nom d’utilisateur existe déjà"
        conn.close()

        return render_template('create_admin.html', message=message)

    return render_template('create_admin.html')


# Modifier Admin
@app.route('/edit_admin/<int:id>', methods=['GET', 'POST'])
def edit_admin(id):
    if 'super_admins' not in session:
        return redirect('/login_super')
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        cursor.execute("UPDATE admins SET username=?, password=? WHERE id=?", (
            new_username, generate_password_hash(new_password), id,
        ))
        conn.commit()
        conn.close()
        flash("Admin modifié avec succès")
        return redirect('/super_admin')

    cursor.execute('SELECT * FROM admins WHERE id=?', (id,))
    sup_admin = cursor.fetchone()
    conn.close()
    return render_template('edit_admin.html', sup_admin=sup_admin)

    # Préremplir les champs
    cursor.execute("SELECT username FROM admin WHERE id=?", (id,))
    result = cursor.fetchone()
    if result:
        form.username.data = result[0]
    conn.close()
    return render_template("edit_admin.html", form=form)


@app.route('/delete_admin/<int:id>')
def delete_admin(id):
    if 'super_admins' not in session:
        return redirect('/login_super')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM admins WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/super_admin')

# dasboard super admin
@app.route('/super_admin')
def super_admin():
    if 'super_admins' not in session:
        return redirect('/login_super')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM admins ORDER BY created_at DESC')
    admins = cur.fetchall()
    admins_dicts = [{
        'id': r[0],
        'usename': r[1]
    }for r in admins]
    conn.close()
    return render_template('super_dashboard.html', admins=admins, admins_json=admins_dicts)


# Authentification superadmin
@app.route('/login_super', methods=['GET', 'POST'])
def login_super():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM super_admins WHERE username = %s', (user,))
        data = cur.fetchone()
        conn.close()

        if data and check_password_hash(data[0], pw):
            session['super_admins'] = user
            return redirect('/super_admin')
        else:
            return redirect('login_super.html', "Identifiants invalides ❌"), 403
    return render_template('login_super.html')


# déconexion super admin
@app.route('/logout_super')
def logout_super():
    session.pop('super_admins', None)
    return redirect('/login_super')

# search client
@app.route('/search', methods=['GET'])
def search_person():
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    if q:
        like_q = f"%{q}%"

        cur.execute("""
          SELECT id, prenom, nom, tel, nin, created_at
          FROM reservations
          WHERE prenom    LIKE ?
             OR nom    LIKE ?
             OR tel LIKE ?
             OR nin LIKE ?
    
        """, (like_q, like_q, like_q, like_q))

    else:
        cur.execute("""
                  SELECT id, prenom, nom, tel, nin, created_at
                  FROM reservations
                  ORDER BY created_at DESC
                """)
    reservations = cur.fetchall()
    conn.close()
    if request.args.get('ajax'):
        # Prépare la liste de dicts
        results = [{
            'id': r[0],
            'prenom': r[1],
            'nom': r[2],
            'tel': r[3],
            'nin': r[4],
            'created_at': r[5]
        } for r in reservations]
        return jsonify(results)

    return render_template('admin_test.html', reservations=reservations, q=q)


# Authentification admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM admins WHERE username = %s', (user,))
        data = cur.fetchone()
        conn.close()

        if data and check_password_hash(data[0], pw):
            session['admin'] = user
            return redirect('/admin')
        else:
            return "Identifiants incorrects", 403
    return render_template('login.html')

@app.route('/logout_admin')
def logout():
    session.pop('admin', None)
    return redirect('/login')

# dasboard admin
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM reservations ORDER BY created_at DESC')
    reservations = cur.fetchall()
    reservations_dicts = [{
        'id': r[0],
        'prenom': r[1],
        'nom': r[2],
        'tel': r[3],
        'nin': r[4],
        'created_at': r[5]
    } for r in reservations]
    conn.close()
    return render_template('admin_test.html', reservations=reservations, reservations_json=reservations_dicts)


# Ajouter une réservation depuis l’admin
@app.route('/admin/add', methods=['GET', 'POST'])
def add_reservation():
    if 'admin' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template("add.html")

    conn = get_db_connection()
    cur = conn.cursor()

    prenom = request.form['prenom']
    nom = request.form['nom']
    tel = request.form['tel']
    nin = request.form['nin']

    cur.execute('''
        SELECT COUNT(*) FROM reservations WHERE prenom=? AND nom=? AND nin=?
    ''', (prenom, nom, nin))
    if cur.fetchone()[0] > 0:
        conn.close()
        return "Client déjà enregistré", 409

    cur.execute('''
        INSERT INTO reservations (prenom, nom, tel, nin)
        VALUES (?, ?, ?, ?)
    ''', (prenom, nom, tel, nin))
    conn.commit()
    conn.close()
    return render_template("confirmation.html", prenom=prenom, nom=nom)


# Modifier
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        tel = request.form['tel']
        nin = request.form['nin']

        cur.execute('''
            UPDATE reservations SET prenom=?, nom=?, tel=?, nin=? WHERE id=?
        ''', (prenom, nom, tel, nin, id))
        conn.commit()
        conn.close()
        return redirect('/admin')

    cur.execute('SELECT * FROM reservations WHERE id=?', (id,))
    res = cur.fetchone()
    conn.close()
    return render_template('edit.html', res=res)


# Supprimer
@app.route('/delete/<int:id>')
def delete(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM reservations WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
