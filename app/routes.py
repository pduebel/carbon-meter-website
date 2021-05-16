import sqlite3
import datetime
import pickle

import pandas as pd
from flask import render_template, request, send_file
import gviz_api

from app import app

@app.route('/')
def index():
    conn = sqlite3.connect('processed_test.db')
    df = pd.read_sql('SELECT * FROM energy', con=conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M')
    
    day_timestamp = df['timestamp'].max() - datetime.timedelta(hours=24)
    day_df = df[df['timestamp'] >= day_timestamp].copy()
    grouped_day_df = day_df.groupby(day_df['timestamp'].dt.floor('5min'))['kWh'].max().reset_index()
    grouped_day_df['kWh_diff'] = grouped_day_df['kWh'].diff()
    grouped_day_df['min_diff'] = grouped_day_df['timestamp'].diff().dt.total_seconds().div(60)
    grouped_day_df['min_diff'] = grouped_day_df['min_diff'].fillna(1).astype(int)
    grouped_day_df['diff'] = grouped_day_df['kWh_diff'] / grouped_day_df['min_diff']
    day_graph_df = grouped_day_df[['timestamp', 'diff']]

    week_timestamp = df['timestamp'].max() - datetime.timedelta(days=7)
    week_df = df[df['timestamp'] >= week_timestamp].copy()
    grouped_week_df = week_df.groupby(week_df['timestamp'].dt.floor('H'))['kWh'].max().reset_index()
    grouped_week_df['kWh_diff'] = grouped_week_df['kWh'].diff()
    grouped_week_df['hour_diff'] = grouped_week_df['timestamp'].diff().dt.total_seconds().div(60 * 60)
    grouped_week_df['hour_diff'] = grouped_week_df['hour_diff'].fillna(1).astype(int)
    grouped_week_df['diff'] = grouped_week_df['kWh_diff'] / grouped_week_df['hour_diff']
    week_graph_df = grouped_week_df[['timestamp', 'diff']]

    month_timestamp = df['timestamp'].max() - datetime.timedelta(days=30)
    month_df = df[df['timestamp'] >= month_timestamp].copy()
    grouped_month_df = month_df.groupby(month_df['timestamp'].dt.floor('D'))['kWh'].max().reset_index()
    grouped_month_df['kWh_diff'] = grouped_month_df['kWh'].diff()
    grouped_month_df['day_diff'] = grouped_month_df['timestamp'].diff().dt.total_seconds().div(60 * 60 * 24)
    grouped_month_df['day_diff'] = grouped_month_df['day_diff'].fillna(1).astype(int)
    grouped_month_df['diff'] = grouped_month_df['kWh_diff'] / grouped_month_df['day_diff']
    month_graph_df = grouped_month_df[['timestamp', 'diff']]

    description = [('timestamp', 'datetime', 'Time stamp'),
                   #('battery', 'number', 'Battery'),
                   #('kWh', 'number', 'Total kWh'),
                   #('kW', 'number', 'kW'),
                   ('diff', 'number', 'kWh')]

    day_data_table = gviz_api.DataTable(description)
    day_data_table.LoadData(day_graph_df.values)
    day_json = day_data_table.ToJSon()

    week_data_table = gviz_api.DataTable(description)
    week_data_table.LoadData(week_graph_df.values)
    week_json = week_data_table.ToJSon()

    month_data_table = gviz_api.DataTable(description)
    month_data_table.LoadData(month_graph_df.values)
    month_json = month_data_table.ToJSon()

    conn.close()

    return render_template('chart.html', day_json=day_json, week_json=week_json, month_json=month_json)

@app.route('/data-upload', methods=['POST'])
def get_data():
    try:
        r = request.get_json()
        df = pd.read_json(r, convert_dates=False)
        df.set_index('timestamp', inplace=True)
        conn = sqlite3.connect('processed_test.db')
        df.to_sql('temp_table', con=conn, if_exists='replace')
        c = conn.cursor()
        c.execute('REPLACE INTO energy SELECT * FROM temp_table')
        conn.commit()
        conn.close()
        return 'We did it!', 200
    except:
        return 'Sad face :(', 400