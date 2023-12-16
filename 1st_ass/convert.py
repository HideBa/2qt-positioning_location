import csv
import sqlite3

# Replace with your SQLite .db file and the table you want to export
db_file = "./1st_ass/nmea3.db"
table_name = "sentence"
output_csv = "nmea.csv"

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Query to select all data from the table
query = f"SELECT * FROM {table_name}"

# Execute the query
cursor.execute(query)

# Fetch all rows from the query result
rows = cursor.fetchall()

# Get the column names
column_names = [description[0] for description in cursor.description]

# Writing to CSV
with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the column headers
    csv_writer.writerow(column_names)

    # Write the rows of data
    csv_writer.writerows(rows)

# Close the connection
conn.close()

print(f"Data exported to {output_csv} successfully.")
