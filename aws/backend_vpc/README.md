# Backend VPC setup scripts and files

To setup Backend environment, we have to create a VPC in any region having 3 Public Subnets, 3 Private Subnets, 1 Internet Gateway, 1 NAT Gateway, etc

To create above list of resources run following script

#### Steps:

    1) Run following script which checks for cloudformation stack and VPC existance and creates resources accordingly:

    ./create-backend-vpc-cloudformation-stack.sh
