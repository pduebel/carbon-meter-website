import sqlite3
import datetime
import pickle

import pandas as pd
from flask import render_template, request, send_file
import gviz_api

from app import app

@app.route('/')
def index():
    conn = sqlite3.connect('energy.db')
    cur = conn.cursor()
    query_dict = {}
    total_dict = {}
    days_dict = {'day': [1, 5],
                 'week': [7, 60],
                 'month': [30, 1440]}
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
        total_dict[period] = f'''
            SELECT
              SUM(kWh),
              SUM(carbon)
            FROM energy
            WHERE (
                    (
                        SELECT MAX(JULIANDAY(timestamp)) 
                        FROM energy
                    ) - JULIANDAY(timestamp)
                ) <= {period_list[0]}
        '''
    
    try:
        day_graph_df = pd.read_sql_query(query_dict['day'], con=conn)
        day_graph_df['timestamp_floor'] = pd.to_datetime(day_graph_df['timestamp_floor'])
        day_totals = cur.execute(total_dict['day']).fetchone()
    except:
        day_graph_df = pd.DataFrame()
        day_totals = ['N/A', 'N/A']
    
    try:
        week_graph_df = pd.read_sql_query(query_dict['week'], con=conn)
        week_graph_df['timestamp_floor'] = pd.to_datetime(week_graph_df['timestamp_floor'])
        week_totals = cur.execute(total_dict['week']).fetchone()
    except:
        week_graph_df = pd.DataFrame()
        week_totals = ['N/A', 'N/A']
    
    try:
        month_graph_df = pd.read_sql_query(query_dict['month'], con=conn)
        month_graph_df['timestamp_floor'] = pd.to_datetime(month_graph_df['timestamp_floor'])
        month_totals = cur.execute(total_dict['month']).fetchone()
    except:
        month_graph_df = pd.DataFrame()
        month_totals = ['N/A', 'N/A']

    description = [('timestamp_floor', 'datetime', 'Time stamp'),
                   ('kWh', 'number', 'kWh'),
                   ('carbon', 'number', 'Carbon')]

    day_data_table = gviz_api.DataTable(description)
    day_data_table.LoadData(day_graph_df.values)
    day_json = day_data_table.ToJSon()

    week_data_table = gviz_api.DataTable(description)
    week_data_table.LoadData(week_graph_df.values)
    week_json = week_data_table.ToJSon()

    month_data_table = gviz_api.DataTable(description)
    month_data_table.LoadData(month_graph_df.values)
    month_json = month_data_table.ToJSon()
     
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
                           day_json=day_json, 
                           week_json=week_json, 
                           month_json=month_json, 
                           kW=kW,
                           carbon_data=carbon_data,
                           day_totals=day_totals,
                           week_totals=week_totals,
                           month_totals=month_totals)

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