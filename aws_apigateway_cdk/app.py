#!/usr/bin/env python3
import os
import json
import aws_cdk as core
from datachallenge.datachallenge_stack import DatachallengeStack

with open('cdk.json', 'r') as file:
    env_variables = json.load(file)


PROD_ACCOUNT = env_variables["context"]['shared_values']['prod_values']['account_number']
PROD_REGION = env_variables["context"]['shared_values']['prod_values']['region']

# DEV_ACCOUNT = env_variables["context"]['shared_values']['dev_values']['account_number']
# DEV_REGION = env_variables["context"]['shared_values']['dev_values']['region']

# TEST_ACCOUNT = env_variables["context"]['shared_values']['test_values']['account_number']
# TEST_REGION = env_variables["context"]['shared_values']['test_values']['region']


prod = core.Environment(account=PROD_ACCOUNT, region=PROD_REGION)
# dev = core.Environment(account=DEV_ACCOUNT, region=DEV_REGION)
# test = core.Environment(account=TEST_ACCOUNT, region=TEST_REGION)


app = core.App()

DatachallengeStack(app, "datachallenge-api", env=core.Environment(
    account=PROD_ACCOUNT,
    region=PROD_REGION), stage='prod',
    tags = {
        "environment":"prod",
        "owner":"miguelangel",
        "region":PROD_REGION,
    })

# DatachallengeStack(app, "datachallenge-api", env=core.Environment(
#     account=DEV_ACCOUNT,
##     region=DEV_REGION), stage='dev',
#     tags = {
#         "environment":"dev",
#         "owner":"miguelangel",
#         "region":DEV_REGION,
#     })

# DatachallengeStack(app, "datachallenge-api", env=core.Environment(
#     account=TEST_ACCOUNT,
##     region=TEST_REGION), stage='test',
#     tags = {
#         "environment":"test",
#         "owner":"miguelangel",
#         "region":TEST_REGION,
#     })

app.synth()
