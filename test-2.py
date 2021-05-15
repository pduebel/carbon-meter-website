#%%
import sqlite3
import requests
import pandas as pd
# %%
conn = sqlite3.connect('processed_test.db')
df = pd.read_sql('SELECT * FROM energy', con=conn)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M')
conn.close()
# %%
json = df.to_json()
# %%
json_df = pd.read_json(json)
# %%
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}
r = requests.post('https://carbon-meter.herokuapp.com/data-upload', data=json, headers=headers)
print(r)