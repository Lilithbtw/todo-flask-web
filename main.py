from flask import Flask, render_template, jsonify
import pymysql
from dataclasses import dataclass
from os import getenv
import time

app = Flask(__name__, template_folder='templates')

def getenv_int(var_name, default):
    raw = getenv(var_name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        raise RuntimeError(f"Valor inválido para {var_name}: {raw!r}")

hostname = getenv("HOSTNAME")
user = getenv("DB_USER")
password = getenv("DB_PASSWD")
port = getenv_int("MYSQL_PORT", 3306)

max_retries = 30
db = None

for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
        print(f"Connecting to: {hostname}:{port} as user {user}")
        
        db = pymysql.connect(
            host=hostname,
            user=user,
            password=password,
            port=port
        )
        print("Successfully connected to database!")
        break
        
    except Exception as e:
        print(f"Connection attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            print("Retrying in 2 seconds...")
            time.sleep(2)
        else:
            print("Max retries reached. Could not connect to database.")
            raise

if db is None:
    raise RuntimeError("Failed to establish database connection")

cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS FlaskToDoDB")

cursor.execute("USE FlaskToDoDB")
cursor.execute("CREATE TABLE IF NOT EXISTS todo_list ("
               "id INT PRIMARY KEY,"
               "title VARCHAR(255) NOT NULL,"
               "complete BOOLEAN NOT NULL"
               ")")
db.commit()

cursor.execute("DELETE FROM todo_list")
db.commit()


insert_query = "INSERT INTO todo_list (id, title, complete) VALUES (%s, %s, %s)"
data = [
    (1, 'Buy groceries', False),
    (2, 'Finish homework', True),
    (3, 'Call Alice', False)
]

for record in data:
    cursor.execute(insert_query, record)

db.commit()


cursor.execute("SELECT * FROM todo_list")
todo_list = cursor.fetchall()

cursor.close()
db.close()

@dataclass
class todo:
    id: int
    title: str
    complete: int


values = []

for stuff in todo_list:
    values.append(
        todo(
            id = stuff[0],
            title = stuff[1],
            complete = stuff[2]
        )
    )

@app.route("/")
def home():
    return render_template("base.html", todo_list=values)

@app.route("/health")
def health():
    health=[{"response": "ok"}]
    return jsonify(health)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)