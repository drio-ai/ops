
# AWS Setup files and scripts

Current directory contains files and scripts to setup environment for Hashicorp Vault, Postgres and Controller Components.

## Backend VPC setup scripts and files

To setup Backend environment, we have to create a VPC in any region having 3 Public Subnets, 3 Private Subnets, 1 Internet Gateway, 1 NAT Gateway, 1 SSL/TLS certificate created/imported in AWS Certificate Manager (ACM)

#### Steps:

    1) Run following script which checks for cloudformation stack and VPC existance and creates resources accordingly:

    aws/backend_vpc/create-backend-vpc-cloudformation-stack.sh


## Create SSL Certificate (Before creating vault cloudformation stack)

To create SSl certificate, which is needed while deploying vault, use following script, which checks if certificate is already created or not, and creates the certificate with domain name 'vault.ddx.drio.ai':

    aws/vault/create-vault-ssl-certificate-cloudformation-stack.sh

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

## Create VPC Peering between 2 VPCs in different region:

#### NOTE: VPC Names and regions are hardcoded in below scripts, you might need to update the values of variables in script before executing it

#### NOTE: Below script creates VPC Peering between VPCs named ControllerVPC (us-east-1 region) and BackendVPC (us-west-2 region), either change the parameters in create-backend-controller-vpc-peering.sh script named $CONTROLLER_REGION and $CONTROLLER_VPC_NAME or run following script which creates pre-requisite controller VPC in appropriate region.

#### Steps:

    1) Pre-requisite: You must have VPC named ControllerVPC in us-east-1 region or change script parameters as mentioned above. To create this ControllerVPC, run following script:

    aws/controller_vpc/create-controller-vpc-cloudformation.sh

Once controller VPC is in place, we can run following script to create peering between the 2 VPCs

#### Note: If the Name and region of Controller VPC is not 'ControllerVPC' and us-east-1 respectively, then update environment variables in aws/aws.env file named 'CONTROLLER_REGION' & 'CONTROLLER_VPC_NAME' or add these 2 variables in below script to overwrite existing values.

    aws/vpc_peering/create-backend-controller-vpc-peering.sh