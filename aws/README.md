
# AWS Setup files and scripts

Current directory contains files and scripts to setup environment for Hashicorp Vault, Postgres and Controller.

## Setup Backend environment

To setup Backend environment, we have to create a VPC in any region having 3 Public Subnets, 3 Private Subnets, 1 Internet Gateway, 1 NAT Gateway, 1 SSL/TLS certificate created/imported in AWS Certificate Manager (ACM)

To setup above environment run following scripts in mentioned order:

    1) To create VPC and Subnets:

    ./setup_backend_vpc.sh


## Deploy Postgres RDS instance in Backend environment

Following script to deploy Postgres RDS needs some environment pre-requisites:

    1) VPC with at 2 Subnets in different availability zones. Above "setup_backend_vpc.sh" script creates suitable environment needed to deploy Postgres RDS.

Steps to deploy Postgres RDS:

    1) Modify the script and edit variable value "MASTER_USER_PASSWORD", Please modify other variables as well as per requirement.

    ./create_postgres_rds.sh
