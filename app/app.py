#Python Standard
import csv
import json
import codecs
from typing import List  # Puedes añadir otros tipos si es necesario

#Thirdparty packages
import numpy as np
from fastapi import FastAPI, UploadFile, File
from mangum import Mangum
import uvicorn
import boto3
from mysql.connector import connect, Error
from keras.models import Sequential
from keras.layers import Dense

#Local files
import functions_api as F

ENV_VARIABLES = {
    "SECRET_RDS" : "rds!db-6849e7f9-0614-42df-8224-eeee9f554f17",
    "RDS_HOST" : "dbchallenge-mysql.c4t6rybb9zgh.us-east-1.rds.amazonaws.com",
    "RDS_PORT" : "3306",
    "REGION" : "us-east-1",
    "DB_NAME" : "migration_db"
} # This needs to be moved to environmental variables in AWS Lambda maybe with cdk


LOCAL_FLAG = False

RDS_HOST = ENV_VARIABLES['RDS_HOST']
RDS_CREDENTIALS = ENV_VARIABLES['SECRET_RDS']
RDS_PORT = ENV_VARIABLES['RDS_PORT']
REGION = ENV_VARIABLES['REGION']
DB_NAME = ENV_VARIABLES['DB_NAME']
ROWS_LIMIT = 1000
PROFILE_NAME = 'PERSONAL'

app = FastAPI()
handler = Mangum(app)

@app.get("/")
def read_root():
    print("Just for testing connections...")
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG,PROFILE_NAME,REGION,RDS_CREDENTIALS, RDS_HOST)
    print(rds_host, username, password)
    try:
       with connect(
            host=rds_host,
            user=username,
            password=password
            ) as connection:
            print(connection)
    except Error as e:
        print(e)

    return {'status': "Succed"}

@app.post("/jobs/upload")
def jobs_upload(file: UploadFile = File(...)):
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG,PROFILE_NAME,REGION,RDS_CREDENTIALS, RDS_HOST)

    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), fieldnames=['id', 'job'])
    data = [row for row in csvReader]
    file.file.close()

    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")
            insert_query = "INSERT INTO jobs (id, job) VALUES (%s, %s)"
            data_to_insert = data[:ROWS_LIMIT]
            values = [(record['id'], record['job']) for record in data_to_insert]
            cursor.executemany(insert_query, values)
            conn.commit()
            cursor.close()
            conn.close()
    except Error as e:
        print(e)
        return {"error": "Failed to insert data into the database."}

    return {"data_inserted": data_to_insert}

@app.post("/departments/upload")
def departments_upload(file: UploadFile = File(...)):
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG,PROFILE_NAME,REGION,RDS_CREDENTIALS, RDS_HOST)

    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), fieldnames=['id', 'department'])
    data = [row for row in csvReader]
    file.file.close()

    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")
            insert_query = "INSERT INTO departments (id, department) VALUES (%s, %s)"
            data_to_insert = data[:ROWS_LIMIT]
            values = [(record['id'], record['department']) for record in data_to_insert]
            cursor.executemany(insert_query, values)
            conn.commit()
            cursor.close()
            conn.close()
    except Error as e:
        print(e)
        return {"error": "Failed to insert data into the database."}

    return {"data_inserted": data_to_insert}

@app.post("/employees/upload")
def employees_upload(file: UploadFile = File(...)):
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG, PROFILE_NAME, REGION, RDS_CREDENTIALS, RDS_HOST)

    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), fieldnames=['id', 'name', 'datetime', 'department_id', 'job_id'])
    data = [row for row in csvReader]
    file.file.close()

    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")
            insert_query = "INSERT INTO employees (id, name, datetime, department_id, job_id) VALUES (%s, %s, %s, %s, %s)"
            
            valid_records = []  # Lista para almacenar los registros válidos
            invalid_records = []  # Lista para almacenar los registros inválidos
            
            job_ids = set(record['job_id'] for record in data)
            department_ids = set(record['department_id'] for record in data)
            # Verificar si todos los job_ids existen en la tabla jobs
            cursor.execute("SELECT DISTINCT id FROM jobs WHERE id IN ({})".format(','.join(['%s'] * len(job_ids))), tuple(job_ids))
            valid_job_ids = {row[0] for row in cursor}
            
            # Verificar si todos los department_ids existen en la tabla departments
            cursor.execute("SELECT DISTINCT id FROM departments WHERE id IN ({})".format(','.join(['%s'] * len(department_ids))), tuple(department_ids))
            valid_department_ids = {row[0] for row in cursor}
            
            # Filtrar los registros válidos e inválidos
            for record in data:
                if len(valid_records) > ROWS_LIMIT:
                    break
                try:
                    if int(record['job_id']) in valid_job_ids and int(record['department_id']) in valid_department_ids:
                        valid_records.append(record)
                    else:
                        invalid_records.append(record)
                except:
                    invalid_records.append(record)
            values = [(record['id'], record['name'], record['datetime'], record['department_id'], record['job_id']) for record in valid_records]
            cursor.executemany(insert_query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            if invalid_records:
                return {"data_inserted": valid_records, "data_discarded": invalid_records}
            else:
                return {"data_inserted": valid_records}
    except Error as e:
        print(e)
        return {"error": "Failed to insert data into the database."}

@app.get("/metrics/quarterhires")
def quarterhires():
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG, PROFILE_NAME, REGION, RDS_CREDENTIALS, RDS_HOST)
    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")

            query_hired_quarter = """
                                SELECT department, job,
                                    SUM(Q1) AS Q1,
                                    SUM(Q2) AS Q2,
                                    SUM(Q3) AS Q3,
                                    SUM(Q4) AS Q4
                                FROM (
                                SELECT employees.id, datetime, name, department_id, job_id, job, department,
                                        CASE
                                            WHEN datetime >= '2021-01-01T00' AND datetime <= '2021-03-31T23' THEN 1
                                            ELSE 0
                                        END AS Q1,
                                        CASE
                                            WHEN datetime >= '2021-04-01T00' AND datetime <= '2021-06-30T23' THEN 1
                                            ELSE 0
                                        END AS Q2,
                                        CASE
                                            WHEN datetime >= '2021-07-01T00' AND datetime <= '2021-09-30T23' THEN 1
                                            ELSE 0
                                        END AS Q3,
                                        CASE
                                            WHEN datetime >= '2021-10-01T00' AND datetime <= '2021-12-31T23' THEN 1
                                            ELSE 0
                                        END AS Q4
                                    FROM employees
                                    LEFT JOIN jobs ON employees.job_id = jobs.id
                                    LEFT JOIN departments ON employees.department_id = departments.id
                                ) AS subquery
                                GROUP BY department, job 
                                ORDER BY department, job;
                                    """
            cursor.execute(query_hired_quarter)
            results = cursor.fetchall()
            result_dicts = [dict(zip(cursor.column_names, row)) for row in results]
                        
            conn.commit()
            cursor.close()
            conn.close()
            return {"data":result_dicts}
        
    except Error as e:
        print(e)
        return {"error": "Failed to obtain metric."}

@app.get("/metrics/topdepartments")
def topdepartments():
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG, PROFILE_NAME, REGION, RDS_CREDENTIALS, RDS_HOST)
    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")

            query_top_departments = """
                                    SELECT MAX(department_id) AS id,
                                        MAX(department) AS department,
                                        COUNT(employees.id) AS hired
                                    FROM employees
                                    LEFT JOIN departments ON employees.department_id = departments.id
                                    GROUP BY department
                                    HAVING COUNT(employees.id) > (SELECT AVG(subquery.count_employees) FROM (SELECT COUNT(id) AS count_employees FROM employees GROUP BY department_id) AS subquery)
                                    ORDER BY hired DESC;
                                    """
            cursor.execute(query_top_departments)
            results = cursor.fetchall()
            result_dicts = [dict(zip(cursor.column_names, row)) for row in results]
                        
            conn.commit()
            cursor.close()
            conn.close()
            return {"data":result_dicts}
        
    except Error as e:
        print(e)
        return {"error": "Failed to obtain metric."}

@app.get("/predictions/departmenthires/{department_id}")
def predict_hires(department_id: int):
    rds_host, username, password = F.get_rds_credentials(LOCAL_FLAG, PROFILE_NAME, REGION, RDS_CREDENTIALS, RDS_HOST)
    try:
        with connect(
            host=rds_host,
            user=username,
            password=password
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")

            #Create sql query to get almost organized data
            cursor.execute(f"""SELECT DATE_FORMAT(datetime, '%Y-%m') AS yearmonth, DATE_FORMAT(datetime, '%Y') AS year, DATE_FORMAT(datetime, '%m') AS month,
                COUNT(*) AS count
            FROM employees
            WHERE {department_id} = 2
            GROUP BY yearmonth
            ORDER BY yearmonth""")

            results = cursor.fetchall()
            result_dicts = [dict(zip(cursor.column_names, row)) for row in results]

            #Fill missing values
            result_dicts = F.fill_missing_months(result_dicts)

            #Choose a number of time steps and create sequence
            n_steps = 3
            raw_seq = [element['count'] for element in result_dicts]

            # split into samples
            X, y = F.split_sequence(raw_seq, n_steps)

            #Create model
            model = Sequential()
            model.add(Dense(100, activation='tanh', input_dim=n_steps))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mse')

            #Predict next value
            model.fit(X, y, epochs=1000, verbose=0)
            yhat = model.predict(np.array(raw_seq[-3:]).reshape((1, n_steps)), verbose=0)
            output = round(yhat[0][0])
                        
            conn.commit()
            cursor.close()
            conn.close()
            return {"nextmonth_hires":output}
        
    except Error as e:
        print(e)
        return {"error": "Failed to obtain metric."}

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)
