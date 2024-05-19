from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_secret_key'


class AddCenterForm(FlaskForm):
    name = StringField('Назва', validators=[DataRequired(), Length(min=1, max=100)])
    address = StringField('Адреса', validators=[DataRequired(), Length(min=1, max=200)])
    monthly_fee = FloatField('Місячна плата', validators=[DataRequired(), NumberRange(min=0)])
    capacity = IntegerField('Вмістимість', validators=[DataRequired(), NumberRange(min=1)])


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


def update_center(id, name, address, monthly_fee, capacity):
    conn = sqlite3.connect('childcare.db')
    cursor = conn.cursor()

    cursor.execute('''UPDATE childcare_centers SET name = ?, address = ?, monthly_fee = ?, capacity = ?
                      WHERE id = ?''', (name, address, monthly_fee, capacity, id))

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
    form = AddCenterForm()
    if form.validate_on_submit():
        add_center(form.name.data, form.address.data, form.monthly_fee.data, form.capacity.data)
        flash('Дитячий заклад додано успішно!')
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_center_route(id):
    form = AddCenterForm()
    if request.method == 'GET':
        conn = sqlite3.connect('childcare.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM childcare_centers WHERE id = ?', (id,))
        center = cursor.fetchone()
        conn.close()
        form.name.data = center[1]
        form.address.data = center[2]
        form.monthly_fee.data = center[3]
        form.capacity.data = center[4]
    elif form.validate_on_submit():
        update_center(id, form.name.data, form.address.data, form.monthly_fee.data, form.capacity.data)
        flash('Інформацію оновлено успішно!')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, center_id=id)


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
