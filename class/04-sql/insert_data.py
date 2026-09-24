#!/usr/bin/env python3

import json
import os
import mysql.connector

# In your terminal, define the following environment variables:
# export DBHOST='ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com'
# export DBUSER='ds2022'
# export DBPASS='<see AWS_RDS_CREDENTIALS.txt on Canvas>'
# export DBNAME='<your database name>'

DBHOST = os.environ.get('DBHOST')
DBUSER = os.environ.get('DBUSER')
DBPASS = os.environ.get('DBPASS')
DBNAME = os.environ.get('DBNAME')

db = mysql.connector.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
cursor = db.cursor(dictionary=True)

# Insert statement with parameterized values
add_record = "INSERT INTO mock_data (id, first_name, last_name, email, gender, ip_address) VALUES (%s, %s, %s, %s, %s, %s)"

# Data as a tuple
record_data = (1001, "Mickey", "Mouse", "mickey@disney.com", "Non-binary", "1.2.3.4")

# Set up the cursor execution
cursor.execute(add_record, record_data)

# Perform the actual commit
db.commit()

# Close the db connections
cursor.close()
db.close()