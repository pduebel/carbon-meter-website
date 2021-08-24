import sqlite3

from flask import Flask
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

conn = sqlite3.connect('energy.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS energy (
                           timestamp TEXT PRIMARY KEY,
                           battery INTEGER,
                           total_kWh FLOAT,
                           kWh FLOAT,
                           kW FLOAT,
                           carbon_intensity INTEGER,
                           intensity_index TEXT,
                           carbon INTEGER
                          );''')
c.execute('''CREATE TABLE IF NOT EXISTS kW (
                 id INTEGER PRIMARY KEY,
                 kW FLOAT
                 );''')
conn.commit()
conn.close()

from app import routes