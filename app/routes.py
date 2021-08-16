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
    
    try:
        day_graph_df = pd.read_sql_query(query_dict['day'], con=conn)
        day_graph_df['timestamp_floor'] = pd.to_datetime(day_graph_df['timestamp_floor'])
    except:
        day_graph_df = pd.DataFrame()
    '''df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    day_timestamp = df['timestamp'].max() - datetime.timedelta(hours=24)
    day_df = df[df['timestamp'] >= day_timestamp].copy()
    grouped_day_df = day_df.groupby(day_df['timestamp'].dt.floor('5min'))['kWh'].max().reset_index()
    grouped_day_df['kWh_diff'] = grouped_day_df['kWh'].diff()
    grouped_day_df['min_diff'] = grouped_day_df['timestamp'].diff().dt.total_seconds().div(60)
    grouped_day_df['min_diff'] = grouped_day_df['min_diff'].fillna(1).astype(int)
    grouped_day_df['diff'] = grouped_day_df['kWh_diff'] / grouped_day_df['min_diff']
    
    df.rename(columns={'kWh': 'diff'}, inplace=True)
    day_graph_df = df[['timestamp', 'diff']]'''
    
    try:
        week_graph_df = pd.read_sql_query(query_dict['week'], con=conn)
        week_graph_df['timestamp_floor'] = pd.to_datetime(week_graph_df['timestamp_floor'])
    except:
        week_graph_df = pd.DataFrame()
    '''
    week_timestamp = df['timestamp'].max() - datetime.timedelta(days=7)
    week_df = df[df['timestamp'] >= week_timestamp].copy()
    grouped_week_df = week_df.groupby(week_df['timestamp'].dt.floor('H'))['kWh'].max().reset_index()
    grouped_week_df['kWh_diff'] = grouped_week_df['kWh'].diff()
    grouped_week_df['hour_diff'] = grouped_week_df['timestamp'].diff().dt.total_seconds().div(60 * 60)
    grouped_week_df['hour_diff'] = grouped_week_df['hour_diff'].fillna(1).astype(int)
    grouped_week_df['diff'] = grouped_week_df['kWh_diff'] / grouped_week_df['hour_diff']
    week_graph_df = grouped_week_df[['timestamp', 'diff']]'''
    
    try:
        month_graph_df = pd.read_sql_query(query_dict['month'], con=conn)
        month_graph_df['timestamp_floor'] = pd.to_datetime(month_graph_df['timestamp_floor'])
    except:
        month_graph_df = pd.DataFrame()
    '''month_timestamp = df['timestamp'].max() - datetime.timedelta(days=30)
    month_df = df[df['timestamp'] >= month_timestamp].copy()
    grouped_month_df = month_df.groupby(month_df['timestamp'].dt.floor('D'))['kWh'].max().reset_index()
    grouped_month_df['kWh_diff'] = grouped_month_df['kWh'].diff()
    grouped_month_df['day_diff'] = grouped_month_df['timestamp'].diff().dt.total_seconds().div(60 * 60 * 24)
    grouped_month_df['day_diff'] = grouped_month_df['day_diff'].fillna(1).astype(int)
    grouped_month_df['diff'] = grouped_month_df['kWh_diff'] / grouped_month_df['day_diff']
    month_graph_df = grouped_month_df[['timestamp', 'diff']]'''

    description = [('timestamp_floor', 'datetime', 'Time stamp'),
                   #('battery', 'number', 'Battery'),
                   #('kWh', 'number', 'Total kWh'),
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
        carbon_intensity = carbon_data[0]
        intensity_index = carbon_data[1]
    except:
        carbon_intensity = 'N/A'
        intensity_index = 'N/A'
    
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
                           carbon_intensity=carbon_intensity,
                           intensity_index=intensity_index)

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
        return 'We did it!', 200
    except:
        return 'Sad face :(', 400

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
        return 'We did it!', 200
    except:
        return 'Sad face :(', 400 