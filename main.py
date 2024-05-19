from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

app = Flask(__name__, template_folder='pages')


def create_database():
    conn = sqlite3.connect('childcare.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS childcare_centers (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        address TEXT NOT NULL,
                        monthly_fee REAL NOT NULL,
                        capacity INTEGER NOT NULL)''')

    conn.commit()
    conn.close()


create_database()


def add_center(name, address, monthly_fee, capacity):
    conn = sqlite3.connect('childcare.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO childcare_centers (name, address, monthly_fee, capacity)
                      VALUES (?, ?, ?, ?)''', (name, address, monthly_fee, capacity))

    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = sqlite3.connect('childcare.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM childcare_centers')
    centers = cursor.fetchall()
    conn.close()
    return render_template('index.html', centers=centers)


@app.route('/add', methods=['GET', 'POST'])
def add_center_route():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        monthly_fee = float(request.form['monthly_fee'])
        capacity = int(request.form['capacity'])

        add_center(name, address, monthly_fee, capacity)
        return redirect('/')

    return render_template('add.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        max_fee = float(request.form['max_fee'])
        conn = sqlite3.connect('childcare.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM childcare_centers WHERE monthly_fee <= ?', (max_fee,))
        centers = cursor.fetchall()
        conn.close()
        return render_template('search_results.html', centers=centers)

    return render_template('search.html')


@app.route('/visualization')
def visualization():
    conn = sqlite3.connect('childcare.db')
    df = pd.read_sql_query("SELECT * FROM childcare_centers", conn)
    conn.close()

    # Створення графіків з використанням Seaborn та Matplotlib
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='name', y='monthly_fee')
    plt.xticks(rotation=45)
    plt.title('Місячна плата за дитячими закладами')
    plt.xlabel('Назва закладу')
    plt.ylabel('Місячна плата (грн)')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
