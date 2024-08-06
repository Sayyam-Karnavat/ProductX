import sqlite3
from flask import Flask, app, jsonify, request

app = Flask(__name__)

def get_connection():
    try:
        conn = sqlite3.connect('Quiz.db')  # Update with your database file
        print("Database connection established")
        return conn
    except sqlite3.Error as e:
        print(f"Error occurred while connecting to the database: {e}")
        return None
    
@app.route('/create_student_data', methods=['POST'])
def create_student_data():
    conn = get_connection()
    cobj = conn.cursor()
    cobj.execute("DROP TABLE IF EXISTS STUDENT_DATA")
    table = "CREATE TABLE STUDENT_DATA(wallet_address VARCHAR(255),booklet VARCHAR(255),start_time VARCHAR(255),que_ans VARCHAR(255),end_time VARCHAR(255),transaction_id VARCHAR(255))"
    cobj.execute(table)
    conn.commit()
    conn.close()
    return jsonify({"message": "STUDENT_DATA table is created"}), 200

@app.route('/add_student_data', methods=['POST'])
def add_student_data():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    booklet = data.get('booklet')
    start_time = data.get('start_time')
    que_ans = data.get('que_ans')
    end_time = data.get('end_time')
    transaction_id = data.get('transaction_id')

    if not all([wallet_address, booklet, start_time, que_ans, end_time,transaction_id]):
        return jsonify({"error": "Missing parameters"}), 400

    conn = get_connection()
    cobj = conn.cursor()
    cobj.execute("""INSERT INTO STUDENT_DATA (wallet_address, booklet, start_time, que_ans, end_time,transaction_id) VALUES (?, ?, ?, ?, ?, ?)""",(wallet_address, booklet, start_time, que_ans, end_time, transaction_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student data added successfully"}), 200

@app.route('/show_student_data', methods=['GET'])
def show_student_data():
    conn = get_connection()
    cobj = conn.cursor()
    studentdata = cobj.execute("SELECT * FROM STUDENT_DATA")
    rows = studentdata.fetchall()
    conn.close()
    student_data = [
        {
            "wallet_address": row[0],
            "booklet": row[1],
            "start_time": row[2],
            "que_ans": row[3],
            "end_time": row[4],
            "transaction_id": row[5]
        } for row in rows
    ]
    return jsonify(student_data), 200

if __name__ == '__main__':
    app.run(debug=True)