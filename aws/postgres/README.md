## Deploy Postgres RDS instance in Backend environment

Following script which deploys Postgres RDS needs some environment pre-requisites:

    i) 'VPC with 2 Subnets' in different availability zones. Above "create-backend-vpc-cloudformation-stack.sh" script creates suitable environment needed to deploy Postgres RDS.
    ii) 'A Subnet Groupt' with minimum 2 subnets in different availibility zone.

Steps to deploy Postgres RDS:

#### NOTE: USE ONLY ONE OF THE FOLLOWING WAYS TO CREATE POSTGRES RDS

    1.1) RECOMMENDED WAY: Modify the script and edit variable value "POSTGRES_MASTER_USER_PASSWORD", modify other variables as well as per requirement.

    aws/postgres/create-postgres-rds-cloudformation.sh

    1.2) OPTIONAL WAY: Using shell script

    aws/postgres/create-postgres-rds-awscli.sh
