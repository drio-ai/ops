## Controller VPC setup

Following script creates a VPC CONTROLLER_VPC_NAME="ControllerVPC" in CONTROLLER_REGION="us-east-1"
(both parameters are defined in aws/aws.env)

    aws/controller_vpc/create-controller-vpc-cloudformation.sh
