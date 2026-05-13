import sqlite3
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = 'campus_parking.db'
CSV_FILE = 'raw_parking_data.csv'

def setup_and_populate_db():
    """Initializes the DB and auto-fills it from CSV if empty."""
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    
    # Phase 1: Create the table for raw PII storage [cite: 29, 34]
    cursor.execute('''CREATE TABLE IF NOT EXISTS permits 
                     (student_name TEXT, 
                      matric_number TEXT, 
                      phone_number TEXT, 
                      license_plate TEXT, 
                      vehicle_model TEXT)''')
    
    # Check if the table already has data to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM permits")
    if cursor.fetchone()[0] == 0:
        print("Database is empty. Starting auto-population from CSV...")
        try:
            with open(CSV_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute('''INSERT INTO permits VALUES (?, ?, ?, ?, ?)''', 
                                 (row['student_name'], 
                                  row['matric_number'], 
                                  row['phone_number'], 
                                  row['license_plate'], 
                                  row['vehicle_model']))
            print("Auto-population complete.")
        except FileNotFoundError:
            print(f"Warning: {CSV_FILE} not found. Starting with empty DB.")
    
    connection.commit()
    connection.close()

@app.route('/api/register', methods=['POST'])
def register_parking():
    """Endpoint for new parking permit applications."""
    data = request.json
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    
    cursor.execute("INSERT INTO permits VALUES (?, ?, ?, ?, ?)", 
                  (data.get('student_name'), 
                   data.get('matric_number'), 
                   data.get('phone_number'), 
                   data.get('license_plate'), 
                   data.get('vehicle_model')))
    
    connection.commit()
    connection.close()
    return jsonify({"status": "success", "message": "Application received and saved"}), 201

if __name__ == '__main__':
    # Run the setup before the server starts
    setup_and_populate_db()
    # Run the micro-prototype locally for total architectural visibility [cite: 18]
    app.run(port=5000, debug=True)