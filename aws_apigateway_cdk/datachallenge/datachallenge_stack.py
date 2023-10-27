from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as _agw,
   # aws_cognito as cognito,
    aws_lambda as _lambda,
    aws_iam as _iam
    # aws_sqs as sqs,
)


from constructs import Construct


class DatachallengeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        # Get variables by stage
        shared_values = self.get_variables(self, stage)
        
        lambda_arn = shared_values['lambda_arn']

        # Obtiene una referencia a la función Lambda existente
        existing_lambda = _lambda.Function.from_function_arn(
            self,
            "ExistingLambda",
            function_arn=lambda_arn,
        )

        # Create the Api
        api_name = 'Datachallenge'
        if stage == 'test':
            api_name = 'Datachallenge_test'
        if stage == 'dev':
            api_name = 'Datachallenge_dev'
        elif stage == 'prod':
            api_name = 'Datachallenge_prod'
            
        api = _agw.RestApi(
            self,
            api_name,
            description='API to retrieve data from de data challenge exercise',
            deploy=True  
        )
        
        # Creating API's Resources

        metrics_resource = api.root.add_resource("metrics")
        metrics_quarterhires_resource = metrics_resource.add_resource("quarterhires")
        metrics_topdepartments_resource = metrics_resource.add_resource("topdepartments")


        departments_resource = api.root.add_resource("departments")
        departments_resource_resource = departments_resource.add_resource("upload")
        employees_resource = api.root.add_resource("employees")
        employees_resource_resource = employees_resource.add_resource("upload")
        jobs_resource = api.root.add_resource('jobs')
        jobs_resource_resource = jobs_resource.add_resource("upload")


        # Add methods 
        metrics_quarterhires_resource.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        metrics_topdepartments_resource.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        departments_resource_resource.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        employees_resource_resource.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        jobs_resource_resource.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        api.root.add_method("GET", 
                                                integration=_agw.LambdaIntegration(existing_lambda, proxy=True),
                                                authorization_type=None,
                                                authorization_scopes=None)
        
        


        
        #Add CORS
        metrics_quarterhires_resource.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        
        metrics_topdepartments_resource.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        
        departments_resource_resource.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        
        employees_resource_resource.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        
        jobs_resource_resource.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        
        api.root.add_cors_preflight(allow_origins=_agw.Cors.ALL_ORIGINS,
                                                    status_code=200,
                                                    allow_headers = ['Content-Type','X-Amz-Date','Authorization','X-Api-Key','X-Amz-Security-Token','id_token'],
                                                    allow_methods = ['GET','OPTIONS'])
        


        # Deployment
        if stage == 'test':
            deployment_test = _agw.Deployment(self, id='deployment_test', api=api)
            _agw.Stage(self, id='test_stage', deployment=deployment_test, stage_name='test')
        elif stage == 'dev':
            deployment_dev = _agw.Deployment(self, id='deployment_dev', api=api)
            _agw.Stage(self, id='dev_stage', deployment=deployment_dev, stage_name='dev')
        else:
            deployment_prod = _agw.Deployment(self, id='deployment', api=api)
            _agw.Stage(self, id='prod_stage', deployment=deployment_prod, stage_name='v1')

    @staticmethod
    def get_variables(self, stage):
        shared_values = self.node.try_get_context('shared_values')

        if stage == 'test':
            return shared_values['test_values']
        elif stage == 'dev':
            return shared_values['dev_values']
        elif stage == 'prod':
            return shared_values['prod_values']
        