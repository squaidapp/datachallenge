# Python Database Initialization Script

initialize.py Python script connects to a MySQL database and initializes tables based on schema definitions stored in a `schemas.json` file. It also makes use of AWS Boto3 to retrieve credentials from AWS Secrets Manager. 
clear_db.py Python script connects to a MySQL database and clear all tables. It also makes use of AWS Boto3 to retrieve credentials from AWS Secrets Manager. 
clear_test_data.py Python script connects to a MySQL database and data injected in the testing process. It also makes use of AWS Boto3 to retrieve credentials from AWS Secrets Manager. 

## Prerequisites

Before running any script, make sure you have the following prerequisites:

- Python 3.x installed
- Required Python packages: `json`, `boto3`, and `mysql-connector-python`. You can install them using pip:

```bash
pip install json boto3 mysql-connector-python