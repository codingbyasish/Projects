import psycopg2

##Connecting to DB
conn = psycopg2..connect(dbname="",username="",password="",host="",portnumber="")
## Creating a cursor
cur=conn.cursor()
cur.execute('''CREATE TABLE student(ID SERIAL,NAME TEXT,AGE TEXT,ADDRESS TEXT);''')
conn.commit() ##to create the table in db
conn.close()
print("Connection Success")
