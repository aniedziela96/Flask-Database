from app import app

from flask import Flask, render_template, request, redirect, flash, url_for

import logging

import psycopg2
import psycopg2.extras

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

@app.route('/admin')
def admin_dashboard():
    return render_template("admin/admin.html")

@app.route('/admin/orders')
def admin_orders():
    return render_template("admin/orders.html")

@app.route('/admin/add_product', methods=["GET", "POST"])
def admin_add_product():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM produkty;')
    products = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM kraje;')
    countries = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM producenci;')
    producents = cur.fetchall()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT kategoria FROM kategorie;')
    categories = cur.fetchall()
    cur.close()
    conn.close()


    if request.method == 'POST':

        conn = get_db_connection()
        cur = conn.cursor()
        if request.form['new_product'] == '0':
            product_id = request.form['what_product']
            amount = request.form['amount']
            cur.execute('SELECT add_product(%s, %s)', (product_id, amount))
            app.logger.info(request.form['new_product'])
        else:
            new_name = request.form['new_name']
            country = request.form['country']
            producent = request.form['producent']
            category = request.form['category']
            new_amount = request.form['new_amount']
            price = request.form['price']

            cur.execute('SELECT add_new_product(%s, %s, %s, %s, %s, %s)',
                        (new_name, country, producent, category, new_amount, price))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin_add_product'))
    return render_template("admin/add_product.html", products=products, countries=countries, 
                            producents=producents, categories=categories) 
