from app import app

from flask import Flask, render_template, request, redirect, flash, url_for, Blueprint, session, g

import psycopg2
import psycopg2.extras

app.secret_key = "niewiemcoto"

@app.before_request
def before_request():
    if 'user_id' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id_uzytkownika FROM uzytkownicy WHERE id_uzytkownika = %s', (session['user_id'],))
        user_id= cur.fetchall()
        user = user_id[0][0]
        g.user = user  


DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS)
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM najpopularniejsze_v2;')
    products = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM produkty WHERE promocja > 0 LIMIT 6;')
    on_sale = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("public/index.html", products=products, on_sale=on_sale)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT logowanie(%s, %s)', (email, password))
        verified = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        if verified[0][0] == 'TRUE':
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id_uzytkownika FROM uzytkownicy WHERE e_mail = %s', (email,))
            user_id = cur.fetchall()
            session['user_id'] = user_id[0][0]
            g.user = user_id[0][0]
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('index_logged'))
        else:
            return redirect(url_for('login'))
        
    return render_template("public/login.html")

@app.route('/signin/', methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO uzytkownicy (nazwisko, imie, e_mail, haslo, rodzaj_konta)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (surname, name, email, password, 'user'))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template("public/signin.html")


@app.route('/coffee')
def coffee():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coffee;')
    coffees = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("public/coffee.html", coffees=coffees)

@app.route('/tea')
def tea():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tea;')
    teas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("public/tea.html", teas=teas)

@app.route('/accessories')
def accessories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM accesories;')
    accessories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("public/accessories.html", accessories=accessories)

@app.route('/<product_id>')
def product(product_id):
    print(product_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM produkty WHERE id_produktu = %s', (product_id,))
    product_info = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sklad_produktow WHERE id_produktu = %s', (product_id,))
    ingridients = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("public/product_page.html", product_info=product_info, ingridients=ingridients)



