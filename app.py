from flask import Flask, render_template, request, send_file
from datetime import datetime
from docxtpl import DocxTemplate
import os
import csv
import uuid

app = Flask(__name__)

# Створюємо папки, якщо їх нема
if not os.path.exists("generated"):
    os.makedirs("generated")

if not os.path.exists("data"):
    os.makedirs("data")

DB_PATH = os.path.join("data", "orders.csv")

# Ініціалізація CSV-файлу, якщо він порожній
if not os.path.exists(DB_PATH):
    with open(DB_PATH, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "child_name", "parent_name", "route", "dot", "change_date", "price", "price_words"
        ])

@app.route('/')
def booking_form():
    return render_template('booking_form_2026.html')
@app.route('/submit', methods=['POST'])
def submit_form():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'Імя_прізвище_побатькові_дитини': request.form['child_name'],
        'Імя_прізвище_побатькові_представника_(дорослого)': request.form['parent_name'],
        'маршрут': request.form['route'],
        'назваДОТ': request.form['dot'],
        'зміна': request.form['change_date'],
        'вартість': request.form['price'],
        'вартість_словами': request.form['price_words'],
        'дата': datetime.now().strftime('%d.%m.%Y'),
        'дата_сплати': datetime.now().strftime('%d.%m.%Y')
    }

    # Запис у базу даних
    with open(DB_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp,
            data['Імя_прізвище_побатькові_дитини'],
            data['Імя_прізвище_побатькові_представника_(дорослого)'],
            data['маршрут'],
            data['назваДОТ'],
            data['зміна'],
            data['вартість'],
            data['вартість_словами']
        ])

    # Генерація рахунку
    doc = DocxTemplate("template.docx")
    doc.render(data)

    filename = f"invoice_{uuid.uuid4()}.docx"
    filepath = os.path.join("generated", filename)
    doc.save(filepath)

    return send_file(filepath, as_attachment=True)

@app.route('/admin')
def admin_view():
    with open(DB_PATH, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    # Сортування: табір → зміна → записи
    data_sorted = {}
    for row in data:
        dot = row['dot']
        change = row.get('change_date', 'Невідомо')
        if dot not in data_sorted:
            data_sorted[dot] = {}
        if change not in data_sorted[dot]:
            data_sorted[dot][change] = []
        data_sorted[dot][change].append(row)

    return render_template("admin.html", data_sorted=data_sorted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
