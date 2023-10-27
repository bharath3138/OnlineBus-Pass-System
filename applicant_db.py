import sqlite3

# Connect to the 'applicant.db' database
conn = sqlite3.connect('applicant.db')
cursor = conn.cursor()

# Create the 'applicants' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS applicants (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT NOT NULL,
        mobile TEXT NOT NULL,
        email TEXT NOT NULL,
        adhar TEXT NOT NULL,
        residence TEXT NOT NULL,
        permanent TEXT NOT NULL,
        pass_type TEXT NOT NULL
    )
''')

# Sample data to be inserted
data = ('APP-1234', 'John Doe', 25, '1998-05-10', 'Male', '1234567890', 'johndoe@example.com', '1234-5678-9012', '123 Main St', '456 Elm St', 'Student Pass')

# Execute the SQL statement to insert data
cursor.execute("INSERT INTO applicants (id, name, age, dob, gender, mobile, email, adhar, residence, permanent, pass_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

# Commit the transaction
conn.commit()

# Close the database connection
conn.close()
