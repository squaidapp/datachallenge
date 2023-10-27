# Data Challenge README

## Project Overview

This project is a multi-component system for creating and managing a FastAPI-based API that connects to a MySQL database hosted on AWS. It comprises three folders, each serving a specific purpose:

**app**: Contains the FastAPI application, which connects to MySQL databases locally and remotely. Details of the API are explained within the folder, including unit testing for each endpoint.

**aws_apigateway_cdk**: Houses an AWS CDK Python project that creates an API Gateway API and uses a Lambda function to host the FastAPI API from the "app" folder.

**configuration**: Includes scripts to initialize the MySQL database from scratch.

## Folder Descriptions

### app

The "app" folder contains the FastAPI application, structured as follows:

- Main entry point of the FastAPI application.
- Database configuration and interaction files (local and remote).
- Data models used by the FastAPI application.
- FastAPI routers and endpoints.
- Business logic and services for request processing.
- Utility functions and helper modules.
- Configuration files for setting up the API.

In addition, the "app" folder includes unit testing for each endpoint, ensuring the API's functionality is thoroughly validated.

### aws_apigateway_cdk

The "aws_apigateway_cdk" folder contains an AWS CDK Python project to deploy the API Gateway and Lambda function:

- Main CDK application file that defines the infrastructure.
- AWS CDK stacks for configuring resources (API Gateway and Lambda).
- Lambda function code and dependencies.

### configuration

The "configuration" folder includes scripts and configuration files for setting up the MySQL database:

- SQL script for initializing the database, creating tables, and inserting initial data (if needed).
- Configuration file with database connection settings and parameters.

## Usage

To use this project effectively, follow the instructions in each folder's respective README.md file. Here is a high-level overview of the steps:

1. **app**:
   - Review the README.md in the "app" folder for API details and how to run the FastAPI application locally.
   - Configure the database connection settings in the "config" folder.
   - Run the FastAPI application to serve the API.
   - Execute unit tests for each endpoint for thorough validation.

2. **aws_apigateway_cdk**:
   - Review the README.md in the "aws_apigateway_cdk" folder for deploying the AWS infrastructure.
   - Deploy the AWS CDK project, which provisions the API Gateway and Lambda function to expose the FastAPI API.

3. **configuration**:
   - Review the README.md in the "configuration" folder for instructions on initializing the MySQL database from scratch using the provided scripts.

By following these steps, you can set up and deploy a FastAPI-based API that connects to a MySQL database hosted on AWS and make it accessible through API Gateway, all while ensuring endpoint functionality through unit testing.
