import sqlite3
import datetime
import pickle

import pandas as pd
from flask import render_template, request
import gviz_api
from werkzeug.security import check_password_hash

from app import app, auth
from config import users

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/')
@auth.login_required
def index():
    conn = sqlite3.connect('energy.db')
    cur = conn.cursor()
    query_dict = {}
    total_query_dict = {}
    days_dict = {'day': [1, 5],
                 'week': [7, 60],
                 'month': [30, 1440],
                 'year': [365, 1440]}
    for period, period_list in days_dict.items():
        query_dict[period] = f'''
            SELECT
              timestamp_floor,
              SUM(kWh),
              SUM(carbon)
            FROM (
                SELECT 
                  DATETIME(
                      STRFTIME("%s", timestamp) - (STRFTIME("%s", timestamp) % ({period_list[1]} * 60)), 
                      "unixepoch"
                  ) AS timestamp_floor,
                  kWh,
                  carbon
                FROM energy
                WHERE (
                    (
                        SELECT MAX(JULIANDAY(timestamp)) 
                        FROM energy
                    ) - JULIANDAY(timestamp)
                ) <= {period_list[0]}
            )
            GROUP BY timestamp_floor
        '''
        total_query_dict[period] = f'''
            SELECT
              ROUND(SUM(kWh), 2),
              ROUND(SUM(carbon), 2)
            FROM energy
            WHERE (
                    (
                        SELECT MAX(JULIANDAY(timestamp)) 
                        FROM energy
                    ) - JULIANDAY(timestamp)
                ) <= {period_list[0]}
        '''
    
    graph_df_dict ={}
    totals_dict  ={}
    data_table_dict = {}
    json_dict = {}
    description = [('timestamp_floor', 'datetime', 'Time stamp'),
                   ('kWh', 'number', 'kWh'),
                   ('carbon', 'number', 'Carbon')]
    for period, query in query_dict.items(): 
        try:
            graph_df_dict[period] = pd.read_sql_query(query, con=conn)
            graph_df_dict[period]['timestamp_floor'] = pd.to_datetime(graph_df_dict[period]['timestamp_floor'])
            totals_dict[period] = cur.execute(total_query_dict[period]).fetchone()
        except:
            graph_df_dict[period] = pd.DataFrame()
            totals_dict[period] = ['N/A', 'N/A']
            
        data_table_dict[period] = gviz_api.DataTable(description)
        data_table_dict[period].LoadData(graph_df_dict[period].values)
        json_dict[period] = data_table_dict[period].ToJSon()
     
    carbon_query = '''
        SELECT 
          carbon_intensity,
          intensity_index
        FROM energy
        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM energy
        )
    '''
    try:
        carbon_data =  cur.execute(carbon_query).fetchone()
    except:
        carbon_data = ['N/A', 'N/A']
    
    try:
        kw_query = '''
            SELECT kW
            FROM kW
            WHERE id=1
        '''
        kW = cur.execute(kw_query).fetchone()[0]
    except:
        kW = 'N/A'

    conn.close()

    return render_template('chart.html', 
                           day_json=json_dict['day'], 
                           week_json=json_dict['week'], 
                           month_json=json_dict['month'],
                           year_json=json_dict['year'],
                           kW=kW,
                           carbon_data=carbon_data,
                           day_totals=totals_dict['day'],
                           week_totals=totals_dict['week'],
                           month_totals=totals_dict['month'],
                           year_totals=totals_dict['year'])

@app.route('/data-upload', methods=['POST'])
def get_data():
    try:
        r = request.get_json()
        df = pd.read_json(r, convert_dates=False)
        df.set_index('timestamp', inplace=True)
        conn = sqlite3.connect('energy.db')
        df.to_sql('temp_table', con=conn, if_exists='replace')
        c = conn.cursor()
        c.execute('REPLACE INTO energy SELECT * FROM temp_table')
        conn.commit()
        conn.close()
        return 'Data upload request successful', 200
    except Exception as e:
        return str(e), 400

@app.route('/kW-upload', methods=['POST'])
def get_kW():
    try:
        kW = request.form['kW']
        id = 1
        conn = sqlite3.connect('energy.db')
        c = conn.cursor()
        c.execute(f'REPLACE INTO kW (id, kW) VALUES ({id}, {kW})')
        conn.commit()
        conn.close()
        return 'kW upload request successful', 200
    except Exception as e:
        return str(e), 400 