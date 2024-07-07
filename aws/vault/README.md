## Vault Setup

#### To deploy Hashicorp Vault following are the pre-requisites:

    1) A VPC in BACKEND_REGION="us-west-2"
    2) VPC containing 3 Public and 3 Private Subnets in different Availability Zones
    3) NAT Gateway attached to that VPC
    4) Internet Gateway
    5) SSl Certificate either imported or created in AWS Certificate Manager
    6) SSH Key-pair

#### You can create SSL Certificate using following Cloudformation template:

    /aws/vault/create-vault-ssl-certificate-cloudformation-stack.sh

#### To deploy vault, Once above pre-requisites are in place, Create A AWS Cloudformation Stack using following yaml file:

    aws/vault/hashicorp-vault-cloudformation-spec.yaml

This template has UI interface to accept VPC Name, VPC CIDR, Subnet IDs, key-pair name, SSL Certificate ARN, etc