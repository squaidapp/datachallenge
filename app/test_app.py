from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

CSV_FILE_PATH_TEST_EMPLOYEE = "../data/test_hired_employees.csv" 
CSV_FILE_PATH_TEST_DEPARTMENTS = "../data/test_departments.csv" 
CSV_FILE_PATH_TEST_JOBS = "../data/test_jobs.csv" 

def test_dbconnection():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Succed"}

def test_upload_jobs():
    files = {'file': open(CSV_FILE_PATH_TEST_JOBS,'rb')}
    response = client.post("/jobs/upload", files=files)
    assert response.status_code == 200
    assert len(json.loads(response.text)['data_inserted']) > 0  

def test_upload_departments():
    files = {'file': open(CSV_FILE_PATH_TEST_DEPARTMENTS,'rb')}
    response = client.post("/departments/upload", files=files)
    assert response.status_code == 200
    assert len(json.loads(response.text)['data_inserted']) > 0

def test_upload_employees():
    files = {'file': open(CSV_FILE_PATH_TEST_EMPLOYEE,'rb')}
    response = client.post("/employees/upload", files=files)
    assert response.status_code == 200
    assert len(json.loads(response.text)['data_inserted']) > 0
    assert len(json.loads(response.text)['data_discarded']) > 0       


def test_metrics_topdepartments():
    response = client.get("/metrics/topdepartments")
    assert response.status_code == 200
    assert len(response.json()['data']) > 0
    assert list(response.json()['data'][0].keys()) == ['id', 'department', 'hired']   


def test_metrics_quarterhires():
    response = client.get("/metrics/quarterhires")
    assert response.status_code == 200
    assert len(response.json()['data']) > 0
    assert list(response.json()['data'][0].keys()) == ['department', 'job', 'Q1', 'Q2', 'Q3', 'Q4']       