from app import app

from flask import Flask, render_template, request, redirect, flash, url_for, Blueprint, session, g

import psycopg2
import psycopg2.extras

auth = Blueprint('auth', __name__)

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

@app.route('/logged', methods=["GET", "POST"])
def index_logged():
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

    if request.method == "POST":
        product_id = request.form['product']
        amount = int(request.form['amount'])
        price = request.form['price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT add_to_basket(%s, %s, %s, %s)', (session['user_id'], product_id, amount, price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index_logged'))

    return render_template("user/logged.html", products=products, on_sale=on_sale)

@app.route('/logged_coffee', methods=["GET", "POST"])
def logged_coffee():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coffee ORDER BY cena_za_100g;')
    coffees = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        product_id = request.form['product']
        amount = int(request.form['amount'])
        price = request.form['price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT add_to_basket(%s, %s, %s, %s)', (session['user_id'], product_id, amount, price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('logged_coffee'))

    return render_template("user/logged_coffee.html", coffees=coffees)

@app.route('/logged_tea', methods=["GET", "POST"])
def logged_tea():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tea ORDER BY cena_za_100g;')
    teas = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        product_id = request.form['product']
        amount = int(request.form['amount'])
        price = request.form['price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT add_to_basket(%s, %s, %s, %s)', (session['user_id'], product_id, amount, price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('logged_tea'))

    return render_template("user/tea.html", teas = teas)

@app.route('/logged_accessories', methods=["GET", "POST"])
def logged_accessories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM accesories ORDER BY cena_za_100g;')
    accessories = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        product_id = request.form['product']
        amount = int(request.form['amount'])
        price = request.form['price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT add_to_basket(%s, %s, %s, %s)', (session['user_id'], product_id, amount, price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('logged_accessories'))
    return render_template("user/accessories.html", accessories=accessories)

@app.route('/account', methods=["GET", "POST"])
def account():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM uzytkownicy WHERE id_uzytkownika = %s;', (session['user_id'],))
    my_info = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM adresy WHERE id_uzytkownika = %s;', (session['user_id'],))
    adress = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        street = request.form['street']
        building_number = int(request.form['building_number'])
        apartment_number = int(request.form['apartment_number'])
        city = request.form['city']
        postal_code = request.form['postalcode']


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO adresy (id_uzytkownika, miasto, kod_pocztowy, ulica, nr_domu, nr_mieszkania)'
                    'VALUES (%s, %s, %s, %s, %s, %s)', 
                    (session['user_id'], city, postal_code, street, building_number, apartment_number))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('account'))


    return render_template("user/account.html", my_info = my_info, adress=adress)

@app.route('/orders')
def orders():
    return render_template("user/orders.html")

@app.route('/basket', methods=["GET", "POST"])
def basket():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_basket WHERE id_uzytkownika = %s;', (session['user_id'],))
    items = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        product_id = request.form['product_id']
        print(product_id)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM koszyki_klientow WHERE id_produktu = %s', (product_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('basket'))

    return render_template("user/basket.html", items=items)


@app.route('/user/<product_id>', methods=["GET", "POST"])
def product_logged(product_id):
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

    if request.method == "POST":
        amount = int(request.form['amount'])
        price = product_info[0][6] - 0.01 * product_info[0][7] * product_info[0][6]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT add_to_basket(%s, %s, %s, %s)', (session['user_id'], product_id, amount, price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index_logged'))


    return render_template("user/product_page.html", product_info=product_info, ingridients=ingridients)

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM adresy WHERE id_uzytkownika = %s;', (session['user_id'], ))
    adresy = cur.fetchall()
    cur.close()
    conn.close()


    if request.method == 'POST':
        adres = request.form['adres']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT zamow(%s, %s)', (session['user_id'], adres))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index_logged'))
    return render_template("user/checkout_page.html", adresy=adresy) 

