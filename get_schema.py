import sqlite3

conn = sqlite3.connect('customer_data.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print('DATABASE SCHEMA')
print('=' * 50)

for table in tables:
    table_name = table[0]
    print(f'\nTABLE: {table_name}')
    print('-' * 30)
    
    # Get table schema
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, name, data_type, not_null, default, pk = col
        pk_str = ' (PRIMARY KEY)' if pk else ''
        not_null_str = ' NOT NULL' if not_null else ''
        default_str = f' DEFAULT {default}' if default else ''
        print(f'  {name}: {data_type}{not_null_str}{default_str}{pk_str}')

conn.close()