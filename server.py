from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) 

@app.route('/')
def home():
    return render_template('index.html')

# teeb kulud databasi kui ei ole
def init_db():
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# route ADD
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    name = data.get('name')
    date = data.get('date')
    amount = data.get('amount')

    if not name or not date or not amount:
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (name, date, amount) VALUES (?, ?, ?)', (name, date, amount))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Expense added successfully'}), 201

# Route GET
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, date, amount FROM expenses')
    rows = cursor.fetchall()
    conn.close()

    expenses = [{'id': row[0], 'name': row[1], 'date': row[2], 'amount': row[3]} for row in rows]
    return jsonify(expenses)

# route DELETE
@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Expense deleted successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
