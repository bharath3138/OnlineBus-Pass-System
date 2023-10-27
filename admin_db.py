import sqlite3

# Define the database name for admin users (change to your actual database name)
DB_ADMIN_NAME = 'admin.db'

# Connect to the admin database
conn = sqlite3.connect(DB_ADMIN_NAME)
cursor = conn.cursor()

# Execute a SQL query to retrieve data from the 'admin_users' table
cursor.execute("SELECT * FROM admin_users")

# Fetch all the rows from the result set
rows = cursor.fetchall()

# Print the data
for row in rows:
    print(row)

# Close the database connection
conn.close()
