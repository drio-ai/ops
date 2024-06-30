#!/bin/bash

VPC_NAME="controllerVPC"
REGION="us-east-1"
STACK_NAME="ControllerVPCStack"
TEMPLATE_FILE="controller-vpc.yaml"

# Check if VPC already exists
VPC_ID=$(aws ec2 describe-vpcs --region $REGION --filters "Name=tag:Name,Values=$VPC_NAME" --query "Vpcs[0].VpcId" --output text)

if [ "$VPC_ID" != "None" ]; then
    echo "VPC with name $VPC_NAME already exists with VPC ID $VPC_ID"
    exit 0
fi

# Create CloudFormation stack
echo "Creating CloudFormation stack..."
aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://$TEMPLATE_FILE --parameters ParameterKey=VPCName,ParameterValue=$VPC_NAME --region $REGION

# Wait for stack creation to complete
echo "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION

# Fetch stack outputs
echo "Fetching stack outputs..."
aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs"
