#%%
import sqlite3
import requests
import pandas as pd
# %%
conn = sqlite3.connect('pro-test.db')
df = pd.read_sql('SELECT * FROM energy', con=conn)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M')
# %%
json = df.to_json()
# %%
json_df = pd.read_json(json)
# %%
r = requests.post('http://localhost:5000/get-data', data=json)
print(r)