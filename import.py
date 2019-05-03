import os
import sys
import csv
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for database environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# create the books table in the database
try:
    db.execute("""CREATE TABLE books(id SERIAL PRIMARY KEY,
    isbn VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL);""")
except exc.SQLAlchemyError: 
    print("table already exists")

# open the csv file and store the information in a variable and add the data to the SQL Database
with open("books.csv") as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    header = next(readCSV)
    for row in readCSV:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year);", { "isbn": row[0], "title": row[1], "author": row[2], "year": row[3] })

print("database updated")
db.commit()