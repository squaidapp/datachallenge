
import json
import boto3
import mysql.connector as mysqlconn
from botocore.exceptions import ClientError

def initialize_tables(mysql_cursor: mysqlconn.cursor, tables_schemas: dict) -> dict:
    """
    Initialize database tables based on the provided schema descriptions.

    This function takes a MySQL cursor and a dictionary of table schemas as input and
    initializes the specified database tables.

    Parameters:
    - mysql_cursor (mysqlconn.cursor): A MySQL cursor object to execute SQL statements.
    - tables_schemas (dict): A dictionary with table names as keys and SQL table schema
      descriptions as values.

    Returns:
    dict: A dictionary where keys are table names, and values represent the result of
          initializing each table. The value can be one of the following:
          - 'OK': Table was successfully initialized.
          - 'already exists.': Table already exists in the database.
          - Error message: An error message if an error occurred during initialization.

    Example Usage:
    ```
    cursor = connection.cursor()
    table_schemas = {
        'users': 'CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))',
        'orders': 'CREATE TABLE orders (order_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, total DECIMAL(10, 2))',
    }
    result = initialize_tables(cursor, table_schemas)
    cursor.close()
    print(result)
    ```

    Note:
    - This function executes SQL statements provided in the `tables_schemas` dictionary
      to create tables. It handles errors related to table existence.
    - Make sure to establish a database connection before calling this function.

    Raises:
    - This function may raise exceptions if there are errors in the SQL statements or
      if there are connection issues with the MySQL database.
    """
    response = {}

    for table_name in tables_schemas:
        
        table_description = tables_schemas[table_name]
        try:
            mysql_cursor.execute(table_description)
        except mysqlconn.Error as err:
            if err.errno == mysqlconn.errorcode.ER_TABLE_EXISTS_ERROR:
                response[table_name] = "already exists."
            else:
                response[table_name] = err.msg
        else:
            response[table_name] = 'OK'
            
    return response

def get_secret(session: boto3.Session, region_name: str, secret_name: str) -> dict:
    """
    Retrieve a secret from AWS Secrets Manager.

    This function connects to AWS Secrets Manager using the provided Boto3 session and retrieves a secret with the
    specified name in the given region.

    Args:
        session (boto3.Session): A Boto3 session configured with AWS credentials and region information.
        region_name (str): The AWS region where the secret is stored.
        secret_name (str): The name or ARN of the secret to retrieve.

    Returns:
        dict: The secret value as a dict.

    Raises:
        botocore.exceptions.ClientError: If there is an error when communicating with AWS Secrets Manager.

    Note:
        - The `session` parameter should be configured with the necessary AWS credentials and region information.
        - The `region_name` parameter specifies the AWS region where the secret is located.
        - The `secret_name` parameter specifies the name or ARN of the secret to retrieve.

    Example:
        # Create a Boto3 session
        session = boto3.Session(aws_access_key_id='your_access_key',
                                aws_secret_access_key='your_secret_key',
                                region_name='us-east-1')

        # Retrieve a secret
        secret_value = get_secret(session, 'us-east-1', 'my-secret-name')

    See also:
        - AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
        - Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    """
    # Create a Secrets Manager client
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    # Your code goes here.
    return json.loads(secret)