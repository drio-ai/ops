#!/bin/bash

# Setting environment variables using single source file
source ../aws.env

get_stack_output() {
    # Fetch stack outputs
    echo "Fetching stack outputs..."
    OUTPUT=$(aws cloudformation describe-stacks --stack-name $CONTROLLER_STACK_NAME --region $CONTROLLER_REGION --query "Stacks[0].Outputs" --output json)

    echo "Stack output:"
    if command -v jq &> /dev/null; then
        echo $OUTPUT | jq
    else
        echo $OUTPUT
    fi
}

# Check if VPC already exists
VPC_ID=$(aws ec2 describe-vpcs --region $CONTROLLER_REGION --filters "Name=tag:Name,Values=$CONTROLLER_VPC_NAME" --query "Vpcs[0].VpcId" --output text)

if [ "$VPC_ID" != "None" ]; then
    echo "VPC with name $CONTROLLER_VPC_NAME already exists with VPC ID $VPC_ID"
    get_stack_output
    exit 0
fi

# Create CloudFormation stack
echo "Creating CloudFormation stack..."
aws cloudformation create-stack --stack-name $CONTROLLER_STACK_NAME --template-body file://$CONTROLLER_TEMPLATE_FILE --parameters ParameterKey=VPCName,ParameterValue=$CONTROLLER_VPC_NAME --region $CONTROLLER_REGION

# Wait for stack creation to complete
echo "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $CONTROLLER_STACK_NAME --region $CONTROLLER_REGION

echo "Fetching stack output..."
OUTPUT=$(aws cloudformation describe-stacks --stack-name $CONTROLLER_STACK_NAME --region $CONTROLLER_REGION --query "Stacks[0].Outputs" --output json)

echo "Stack output:"
if command -v jq &> /dev/null; then
    echo $OUTPUT | jq
else
    echo $OUTPUT
fi
