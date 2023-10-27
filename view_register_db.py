import sqlite3

# Connect to the 'register.db' database
conn = sqlite3.connect('register.db')
cursor = conn.cursor()

# Execute a SQL query to retrieve data from the 'registered_users' table
cursor.execute("SELECT * FROM registered_users")

# Fetch all the rows from the result set
rows = cursor.fetchall()

# Print the data
for row in rows:
    print(row)

# Close the database connection
conn.close()
