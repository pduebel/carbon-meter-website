import sqlite3

from flask import Flask

app = Flask(__name__)

conn = sqlite3.connect('energy.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS energy (
                 timestamp TEXT PRIMARY KEY,
                 battery INTEGER,
                 kWh FLOAT,
                 kW FLOAT
                 );''')
conn.commit()
conn.close()

from app import routes