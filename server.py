from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from flask_socketio import SocketIO, emit



app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

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

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    name = data.get('name')
    date = data.get('date')
    amount = data.get('amount')

    # Validate input
    if not name or not date or amount is None:
        return jsonify({'error': 'Invalid input: missing required fields'}), 400
    try:
        # Convert amount to float for validation
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid input: amount must be a number'}), 400

    # Check that the amount is non-negative
    if amount < 0:
        return jsonify({'error': 'Invalid input: amount cannot be negative'}), 400

    # Proceed with adding the expense to the database
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (name, date, amount) VALUES (?, ?, ?)', (name, date, amount))
    conn.commit()
    conn.close()

    socketio.emit('update', {'message': 'New expense added'})

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
    
    socketio.emit('update', {'message': 'Expense deleted'})

    return jsonify({'message': 'Expense deleted successfully'}), 200


# route DELETE ALL
@app.route('/delete_all_expenses', methods=['DELETE'])
def delete_all_expenses():
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses')
    conn.commit()
    conn.close()
    
    socketio.emit('update', {'message': 'All expenses deleted'})

    return jsonify({'message': 'All expenses deleted successfully'}), 200

# route kõik kulud
@app.route('/get_total_expenses', methods=['GET'])
def get_total_expenses():
    conn = sqlite3.connect('kulud.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total = cursor.fetchone()[0]  # Fetch the total sum
    conn.close()

    total = total if total else 0  # If no expenses, return 0
    return jsonify({'total': total})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
