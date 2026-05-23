import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yemen_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/sync', methods=['POST'])
def sync_contacts():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    saved_count = 0
    for item in data:
        name = item.get('name')
        phone = item.get('phone')
        if name and phone:
            try:
                cursor.execute('INSERT OR IGNORE INTO yemen_contacts (name, phone) VALUES (?, ?)', (name, phone))
                saved_count += 1
            except Exception:
                continue
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Synced {saved_count} contacts"}), 200

@app.route('/search', methods=['GET'])
def search_number():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"status": "error", "message": "Phone number required"}), 400
        
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM yemen_contacts WHERE phone = ?', (phone,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({"status": "success", "name": result[0]})
    else:
        return jsonify({"status": "not_found", "name": None})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
