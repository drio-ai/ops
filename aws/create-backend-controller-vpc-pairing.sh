#!/bin/bash

BACKEND_VPC="BackendStack-VPC"
CONTROLLER_VPC="controllerVPC"
WESTREGION="us-west-2"
EASTREGION="us-east-1"
STACK_NAME="Backend-Controller-VPC-Pairing-Stack"
TEMPLATE_FILE="vpc-pairing-cloudformation.yaml"

# Fetch VPC IDs
BACKEND_VPC_ID=$(aws ec2 describe-vpcs --region $WESTREGION --filters "Name=tag:Name,Values=$BACKEND_VPC" --query "Vpcs[0].VpcId" --output text)
CONTROLLER_VPC_ID=$(aws ec2 describe-vpcs --region $EASTREGION --filters "Name=tag:Name,Values=$CONTROLLER_VPC" --query "Vpcs[0].VpcId" --output text)

if [ "$BACKEND_VPC_ID" == "None" ] || [ "$CONTROLLER_VPC_ID" == "None" ]; then
    echo "One or both VPCs not found"
    exit 1
fi

# # Check if VPC Peering already exists
# PEERING_CONNECTION_ID=$(aws ec2 describe-vpc-peering-connections --region $WESTREGION --filters "Name=tag:Name,Values=Backend-Controller-VPC-Pairing" --query "VpcPeeringConnections[0].VpcPeeringConnectionId" --output text)

# if [ "$PEERING_CONNECTION_ID" != "None" ]; then
#     echo "VPC Peering connection already exists with ID $PEERING_CONNECTION_ID"
#     exit 0
# fi

# Fetch private subnet IDs
BACKEND_PRIVATE_SUBNET_ID=$(aws ec2 describe-subnets --region $WESTREGION --filters "Name=vpc-id,Values=$BACKEND_VPC_ID" "Name=tag:Name,Values=BackendStack-PrivateSubnet1" --query "Subnets[0].SubnetId" --output text)
CONTROLLER_PRIVATE_SUBNET_ID=$(aws ec2 describe-subnets --region $EASTREGION --filters "Name=vpc-id,Values=$CONTROLLER_VPC_ID" "Name=tag:Name,Values=PrivateSubnet" --query "Subnets[0].SubnetId" --output text)

# Fetch VPC CIDR blocks
BACKEND_VPC_CIDR=$(aws ec2 describe-vpcs --region $WESTREGION --vpc-ids $BACKEND_VPC_ID --query "Vpcs[0].CidrBlock" --output text)
CONTROLLER_VPC_CIDR=$(aws ec2 describe-vpcs --region $EASTREGION --vpc-ids $CONTROLLER_VPC_ID --query "Vpcs[0].CidrBlock" --output text)

ROUTE_TABLE_ID_BACKEND=$(aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=$BACKEND_PRIVATE_SUBNET_ID" --query "RouteTables[*].{RouteTableId:RouteTableId}" --output text --region $WESTREGION)
ROUTE_TABLE_ID_CONTROLLER=$(aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=$CONTROLLER_PRIVATE_SUBNET_ID" --query "RouteTables[*].{RouteTableId:RouteTableId}" --output text --region $EASTREGION)

# Create CloudFormation stack
echo "Creating CloudFormation stack..."
aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://$TEMPLATE_FILE --parameters ParameterKey=VPC1Id,ParameterValue=$BACKEND_VPC_ID ParameterKey=VPC2Id,ParameterValue=$CONTROLLER_VPC_ID ParameterKey=VPC1Region,ParameterValue=$WESTREGION ParameterKey=VPC2Region,ParameterValue=$EASTREGION ParameterKey=PrivateSubnet1Id,ParameterValue=$BACKEND_PRIVATE_SUBNET_ID ParameterKey=PrivateSubnet2Id,ParameterValue=$CONTROLLER_PRIVATE_SUBNET_ID ParameterKey=VPC1CIDR,ParameterValue=$BACKEND_VPC_CIDR ParameterKey=VPC2CIDR,ParameterValue=$CONTROLLER_VPC_CIDR --region $WESTREGION

# Wait for stack creation to complete
echo "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $WESTREGION

# Fetch stack outputs
echo "Fetching stack outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $WESTREGION --query "Stacks[0].Outputs")

PEERING_CONNECTION_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="VPCPeeringConnectionId") | .OutputValue')

# Approve VPC Peering connection from the backend VPC side
echo "Approving VPC Peering connection..."
aws ec2 accept-vpc-peering-connection --region $EASTREGION --vpc-peering-connection-id $PEERING_CONNECTION_ID

echo "VPC Peering connection approved with ID $PEERING_CONNECTION_ID"

echo "Updating route table of Backend Private Subnet with VPC Peering connection entry.."
aws ec2 create-route --route-table-id $ROUTE_TABLE_ID_BACKEND --destination-cidr-block $CONTROLLER_VPC_CIDR --region $WESTREGION --vpc-peering-connection-id $PEERING_CONNECTION_ID

echo "Updating route table of Controller private Subnet with VPC Peering connection entry.."
aws ec2 create-route --route-table-id $ROUTE_TABLE_ID_CONTROLLER --destination-cidr-block $BACKEND_VPC_CIDR --region $EASTREGION --vpc-peering-connection-id $PEERING_CONNECTION_ID
