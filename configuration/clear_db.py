import json
import boto3
from mysql.connector import connect
import sys
sys.path.append('..')
import functions as F

def main():
    # Get RDS_CREDENTIALS
    ENV_VARIABLES = json.load(open('../env_variables.json'))
    BOTO3_SESSION = boto3.Session(profile_name="PERSONAL")

    # Read Schemas
    TABLES = json.load(open('schemas.json'))
    DB_NAME = ENV_VARIABLES["DB_NAME"]
    DB_CREDENTIALS = F.get_secret(BOTO3_SESSION, 'us-east-1', ENV_VARIABLES["SECRET_RDS"])

    conn = connect(
        host="localhost",
        user=DB_CREDENTIALS['username'],
        password=DB_CREDENTIALS['password']
    )

    cursor = conn.cursor()
    cursor.execute(F"USE {DB_NAME}")

    table_names = list(TABLES.keys())
    # Create tables
    for table_name in table_names:
        cursor.execute(F"DELETE FROM {table_name}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

