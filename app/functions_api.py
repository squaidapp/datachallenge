
import json
import boto3
import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from typing import List, Dict, Tuple, Union


def get_rds_credentials(local_flag: bool, profile_name: str, region: str, rds_credentials: str, rds_host: str) -> tuple:
    """
    Retrieves RDS credentials based on the local flag.

    Args:
        local_flag (bool): A flag indicating whether the application is running locally.
        profile_name (str): The AWS profile name for the local environment.
        region (str): The AWS region for accessing secrets.
        rds_credentials (str): The identifier for RDS credentials in AWS Secrets Manager.

    Returns:
        tuple: A tuple containing RDS host, username, and password.

    Example:
        >>> host, username, password = get_rds_credentials(True, "local_profile", "us-east-1", "my_rds_credentials")
        >>> print(host)
        'localhost'
    """
    if local_flag:
        boto3_session = boto3.Session(profile_name=profile_name)
        client = None
        rds_host = "localhost"
    else:
        client = boto3.client(service_name='secretsmanager')
        boto3_session = None
        
    response = get_secret(region, rds_credentials, session=boto3_session, client=client)
    return rds_host, response['username'], response['password']

def get_secret(region_name: str, secret_name: str, session: Union[boto3.Session,None] = None, client: Union[boto3.client,None] = None) -> dict:
    """
    Retrieve a secret from AWS Secrets Manager.

    This function retrieves a secret from AWS Secrets Manager using the provided parameters.

    Parameters:
    - region_name (str): The AWS region in which the secret is stored.
    - secret_name (str): The name or ARN of the secret to retrieve.
    - session (Union[boto3.Session, None], optional): An optional boto3.Session object
      for making AWS API requests. If not provided, the 'client' parameter must be set.
    - client (Union[boto3.client, None], optional): An optional boto3 client for Secrets
      Manager. If not provided, the 'session' parameter must be set.

    Returns:
    dict: A dictionary containing the secret information retrieved from AWS Secrets Manager.

    Raises:
    - ClientError: If an error occurs while attempting to retrieve the secret from AWS Secrets Manager.

    Note:
    - Either the 'session' or 'client' parameter must be provided to make API requests.
    - The secret is assumed to be stored in JSON format and is returned as a parsed dictionary.

    Example Usage:
    ```
    region_name = 'us-east-1'
    secret_name = 'MySecret'
    session = boto3.Session(profile_name="my_profile")
    secret = get_secret(region_name, secret_name, session=session)
    print(secret)
    ```

    Ensure that you have the necessary AWS credentials and proper IAM permissions to access the secret.
    """
    print("get secret")
    if session:
        # Create a Secrets Manager client
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
    elif not client: 
        return {'error':'Client of Session must be provided'}
    print(secret_name)
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
    print(secret)

    # Your code goes here.
    return json.loads(secret)

def fill_missing_months(data: dict)->dict:
    """
    Fill in missing months in a dataset and remove records with 'None' in 'month' or 'year'.

    Parameters:
    ----------
    data : List[Dict]
        A list of dictionaries containing data with 'yearmonth', 'year', 'month', and 'count' fields.

    Returns:
    --------
    List[Dict]
        A list of dictionaries representing the complete data, with missing months added, and records
        with 'None' in 'month' or 'year' removed.

    Example:
    --------
    >>> data = [{'yearmonth': '2021-02', 'year': '2021', 'month': '02', 'count': 1},
    ...         {'yearmonth': '2021-04', 'year': '2021', 'month': '04', 'count': 5}]
    >>> result = fill_missing_months(data)
    >>> print(result)
    [{'yearmonth': '2021-02', 'year': '2021', 'month': '02', 'count': 1},
    {'yearmonth': '2021-03', 'year': '2021', 'month': '03', 'count': 0},
    {'yearmonth': '2021-04', 'year': '2021', 'month': '04', 'count': 5}]

    Notes:
    ------
    This function takes a list of dictionaries representing data with 'yearmonth', 'year', 'month', and 'count' fields.
    It fills in missing months in the time sequence and removes records with 'None' in 'month' or 'year.
    """
    # Filtra los registros con None en 'month' o 'year'
    data = [entry for entry in data if entry['month'] is not None and entry['year'] is not None]

    # Convierte los strings de 'yearmonth' en objetos datetime
    data = sorted(data, key=lambda x: datetime.strptime(x['yearmonth'], '%Y-%m'))

    # Obtiene el rango de fechas desde el primer hasta el último mes
    start_date = datetime.strptime(data[0]['yearmonth'], '%Y-%m')
    end_date = datetime.strptime(data[-1]['yearmonth'], '%Y-%m')

    current_date = start_date
    result = []

    while current_date <= end_date:
        month_str = current_date.strftime('%Y-%m')
        entry_exists = False

        for entry in data:
            if entry['yearmonth'] == month_str:
                result.append(entry)
                entry_exists = True
                break

        if not entry_exists:
            result.append({'yearmonth': month_str, 'year': str(current_date.year), 'month': str(current_date.month), 'count': 0})

        current_date = (current_date + timedelta(days=32)).replace(day=1)

    return result

def split_sequence(sequence: List[float], n_steps: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Split a univariate sequence into input and output samples.

    Parameters:
    ----------
    sequence : List[float]
        A list of values representing the univariate sequence.

    n_steps : int
        Number of steps in each sample.

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        A tuple containing two NumPy arrays. The first array represents input samples (X),
        and the second array represents output samples (y).

    Example:
    --------
    >>> sequence = [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> n_steps = 3
    >>> X, y = split_sequence(sequence, n_steps)
    >>> print(X)
    array([[1.0, 2.0, 3.0],
           [2.0, 3.0, 4.0]])
    >>> print(y)
    array([4.0, 5.0])

    Notes:
    ------
    This function takes a univariate sequence and divides it into input and output samples.
    Each input sample contains "n_steps" consecutive values from the sequence, and the output sample
    contains the next value in the sequence.
    """
    X, y = [], []
    sequence = np.array(sequence)  # Convertir la secuencia de entrada en un array NumPy
    
    for i in range(len(sequence) - n_steps):
        seq_x = sequence[i:i + n_steps]
        seq_y = sequence[i + n_steps]
        X.append(seq_x)
        y.append(seq_y)

    X = np.array(X)
    y = np.array(y)
    return X, y