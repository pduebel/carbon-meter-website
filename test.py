#%%
import sqlite3
import pandas as pd
# %%
conn = sqlite3.connect('processed_test.db')
# %%
df = pd.read_sql('SELECT * FROM energy', con=conn)
df.set_index('timestamp', inplace=True)
# %%
df.to_sql('temp_table', con=conn, if_exists='replace')
# %%
c = conn.cursor()
c.execute('REPLACE INTO energy SELECT * FROM temp_table')
conn.commit()
conn.close()
# %%
