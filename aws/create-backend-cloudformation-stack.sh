#!/bin/bash

# Define the VPC name to check
VPC_NAME="BackendStack-VPC"

# Define the stack name and region
STACK_NAME="BackendStack"
REGION="us-west-2"
TEMPLATE_FILE="backend-vpc.yaml"

# Check if VPC with the given name already exists
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --query "Vpcs[0].VpcId" --output text --region ${REGION})

if [[ $VPC_ID == "None" ]]; then
    echo "VPC with name ${VPC_NAME} does not exist. Proceeding to create CloudFormation stack."
    aws cloudformation create-stack --stack-name ${STACK_NAME} --template-body file://${TEMPLATE_FILE} --capabilities CAPABILITY_NAMED_IAM --region ${REGION}
else
    echo "VPC with name ${VPC_NAME} already exists with VPC ID: ${VPC_ID}. Skipping stack creation."
fi

# Wait for the stack creation to complete
echo "Waiting for stack to reach CREATE_COMPLETE state..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME} --region ${REGION}
