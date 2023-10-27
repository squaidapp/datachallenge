# Python Database Initialization Script

This Python script connects to a MySQL database and initializes tables based on schema definitions stored in a `schemas.json` file. It also makes use of AWS Boto3 to retrieve credentials from AWS Secrets Manager. 

## Prerequisites

Before running this script, make sure you have the following prerequisites:

- Python 3.x installed
- Required Python packages: `json`, `boto3`, and `mysql-connector-python`. You can install them using pip:

```bash
pip install json boto3 mysql-connector-python