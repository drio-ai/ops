
# AWS Setup files and scripts

Current directory contains files and scripts to setup environment for Hashicorp Vault, Postgres and Controller.

## Setup Backend environment

To setup Backend environment, we have to create a VPC in any region having 3 Public Subnets, 3 Private Subnets, 1 Internet Gateway, 1 NAT Gateway, 1 SSL/TLS certificate created/imported in AWS Certificate Manager (ACM)

To setup above environment there are 2 ways: i) Using shell script, OR ii) using cloudformation template

#### NOTE: USE ONLY ONE OF THE FOLLOWING WAYS TO CREATE BACKEND VPC

    1.1) RECOMMENDED: Cloudformation template to create above resources:

    ./create-backend-cloudformation-stack.sh

    1.2) OPTINAL WAY - Using shell script:

    ./setup_backend_vpc.sh


## Create SSL Certificate (Before creating vault cloudformation stack)

To create SSl certificate, which is needed while deploying vault, use following script, which checks if certificate is already created or not, and creates the certificate with domain name 'vault.ddx.drio.ai':

    ./create-vault-ssl-certificate.sh


## Deploy Postgres RDS instance in Backend environment

Following script to deploy Postgres RDS needs some environment pre-requisites:

    i) VPC with 2 Subnets in different availability zones. Above "setup_backend_vpc.sh" script creates suitable environment needed to deploy Postgres RDS.
    ii) Subnet Groupt with minimum 2 subnets in different availibility zone.

Steps to deploy Postgres RDS:

#### NOTE: USE ONLY ONE OF THE FOLLOWING WAYS TO CREATE BACKEND VPC

    1.1) RECOMMENDED WAY: Modify the script and edit variable value "MASTER_USER_PASSWORD", modify other variables as well as per requirement.

    ./create-postgres-rds-cloudformation.sh

    1.2) OPTIONAL WAY: Using shell script

    ./create-postgres-rds.sh

## Create VPC Pairing between 2 VPCs in different region:

#### NOTE: (VPC Names and regions are hardcoded in below scripts, you might need to update the values of variables in script before executing it)

    ./create-backend-controller-vpc-pairing.sh