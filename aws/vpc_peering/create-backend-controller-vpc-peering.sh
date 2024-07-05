#!/bin/bash

# Setting environment variables using single source file
source ../aws.env

# Fetch VPC IDs
echo "Fetching VPC ID for ${BACKEND_VPC_NAME} & ${CONTROLLER_VPC_NAME} from regions ${BACKEND_REGION} & ${CONTROLLER_REGION}, respectively"
BACKEND_VPC_ID=$(aws ec2 describe-vpcs --region $BACKEND_REGION --filters "Name=tag:Name,Values=$BACKEND_VPC_NAME" --query "Vpcs[0].VpcId" --output text)
CONTROLLER_VPC_ID=$(aws ec2 describe-vpcs --region $CONTROLLER_REGION --filters "Name=tag:Name,Values=$CONTROLLER_VPC_NAME" --query "Vpcs[0].VpcId" --output text)

if [ "$BACKEND_VPC_ID" == "None" ] || [ "$CONTROLLER_VPC_ID" == "None" ]; then
    echo "One or both VPCs not found"
    exit 1
fi

echo "BACKEND_VPC_ID: ${BACKEND_VPC_ID}"
echo "CONTROLLER_VPC_ID: ${CONTROLLER_VPC_ID}"
echo

# Check if VPC Peering already exists
echo "Checking if peering connection already exists between above VPCs..."
PEERING_CONNECTION_ID=$(aws ec2 describe-vpc-peering-connections --region $BACKEND_REGION --filters "Name=tag:Name,Values=Backend-Controller-VPC-Peering" --query "VpcPeeringConnections[0].VpcPeeringConnectionId" --output text)

if [ "$PEERING_CONNECTION_ID" != "None" ]; then
    PEERING_CONNECTION_STATE=$(aws ec2 describe-vpc-peering-connections --region $BACKEND_REGION --vpc-peering-connection-ids $PEERING_CONNECTION_ID --query 'VpcPeeringConnections[0].Status.Code' --output text)

    if [ "$PEERING_CONNECTION_STATE" != "deleted" ]; then
        echo "VPC Peering connection already exists with ID $PEERING_CONNECTION_ID and state $PEERING_CONNECTION_STATE"
        exit 1
    fi
fi
echo "Active peering connection not found, resuming VPC peering connection creation.."
echo

# Fetch private subnet IDs
echo "Fetching private subnet IDs from ${BACKEND_VPC_NAME} & ${CONTROLLER_VPC_NAME}"
BACKEND_PRIVATE_SUBNET_ID=$(aws ec2 describe-subnets --region $BACKEND_REGION --filters "Name=vpc-id,Values=$BACKEND_VPC_ID" "Name=tag:Name,Values=BackendVPC-PrivateSubnet1" --query "Subnets[0].SubnetId" --output text)
CONTROLLER_PRIVATE_SUBNET_ID=$(aws ec2 describe-subnets --region $CONTROLLER_REGION --filters "Name=vpc-id,Values=$CONTROLLER_VPC_ID" "Name=tag:Name,Values=PrivateSubnet" --query "Subnets[0].SubnetId" --output text)
echo "BACKEND_PRIVATE_SUBNET_ID: $BACKEND_PRIVATE_SUBNET_ID"
echo "CONTROLLER_PRIVATE_SUBNET_ID: $CONTROLLER_PRIVATE_SUBNET_ID"
echo

# Fetch VPC CIDR blocks
echo "Fetching BACKEND_VPC_CIDR & CONTROLLER_VPC_CIDR"
BACKEND_VPC_CIDR=$(aws ec2 describe-vpcs --region $BACKEND_REGION --vpc-ids $BACKEND_VPC_ID --query "Vpcs[0].CidrBlock" --output text)
CONTROLLER_VPC_CIDR=$(aws ec2 describe-vpcs --region $CONTROLLER_REGION --vpc-ids $CONTROLLER_VPC_ID --query "Vpcs[0].CidrBlock" --output text)
echo "BACKEND_VPC_CIDR: $BACKEND_VPC_CIDR"
echo "CONTROLLER_VPC_CIDR: $CONTROLLER_VPC_CIDR"
echo

# Backend and Controller Route table IDs
echo "Fetching ROUTE_TABLE_ID_BACKEND & ROUTE_TABLE_ID_CONTROLLER"
ROUTE_TABLE_ID_BACKEND=$(aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=$BACKEND_PRIVATE_SUBNET_ID" --query "RouteTables[*].{RouteTableId:RouteTableId}" --output text --region $BACKEND_REGION)
ROUTE_TABLE_ID_CONTROLLER=$(aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=$CONTROLLER_PRIVATE_SUBNET_ID" --query "RouteTables[*].{RouteTableId:RouteTableId}" --output text --region $CONTROLLER_REGION)
echo "ROUTE_TABLE_ID_BACKEND: $ROUTE_TABLE_ID_BACKEND"
echo "ROUTE_TABLE_ID_CONTROLLER: $ROUTE_TABLE_ID_CONTROLLER"
echo

# Create CloudFormation stack
echo "Creating CloudFormation stack..."
aws cloudformation create-stack --stack-name $VPC_PEERING_STACK_NAME --template-body file://$VPC_PEERING_TEMPLATE_FILE --parameters ParameterKey=VPC1Id,ParameterValue=$BACKEND_VPC_ID ParameterKey=VPC2Id,ParameterValue=$CONTROLLER_VPC_ID ParameterKey=VPC1Region,ParameterValue=$BACKEND_REGION ParameterKey=VPC2Region,ParameterValue=$CONTROLLER_REGION ParameterKey=PrivateSubnet1Id,ParameterValue=$BACKEND_PRIVATE_SUBNET_ID ParameterKey=PrivateSubnet2Id,ParameterValue=$CONTROLLER_PRIVATE_SUBNET_ID ParameterKey=VPC1CIDR,ParameterValue=$BACKEND_VPC_CIDR ParameterKey=VPC2CIDR,ParameterValue=$CONTROLLER_VPC_CIDR --region $BACKEND_REGION
echo

# Wait for stack creation to complete
echo "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $VPC_PEERING_STACK_NAME --region $BACKEND_REGION
echo

# Fetch stack outputs
echo "Fetching stack outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name $VPC_PEERING_STACK_NAME --region $BACKEND_REGION --query "Stacks[0].Outputs")

PEERING_CONNECTION_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="VPCPeeringConnectionId") | .OutputValue')
echo "PEERING_CONNECTION_ID: $PEERING_CONNECTION_ID"
echo

# Approve VPC Peering connection from the backend VPC side
echo "Approving VPC Peering connection..."
aws ec2 accept-vpc-peering-connection --region $CONTROLLER_REGION --vpc-peering-connection-id $PEERING_CONNECTION_ID > /dev/null
echo "VPC Peering connection approved with ID $PEERING_CONNECTION_ID"
echo

echo "Updating route table of Backend Private Subnet with VPC Peering connection entry.."
aws ec2 create-route --route-table-id $ROUTE_TABLE_ID_BACKEND --destination-cidr-block $CONTROLLER_VPC_CIDR --region $BACKEND_REGION --vpc-peering-connection-id $PEERING_CONNECTION_ID
echo

echo "Updating route table of Controller private Subnet with VPC Peering connection entry.."
aws ec2 create-route --route-table-id $ROUTE_TABLE_ID_CONTROLLER --destination-cidr-block $BACKEND_VPC_CIDR --region $CONTROLLER_REGION --vpc-peering-connection-id $PEERING_CONNECTION_ID
echo
