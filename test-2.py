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
r = requests.post('https://localhost:5000/data-upload', data=json)
print(r)