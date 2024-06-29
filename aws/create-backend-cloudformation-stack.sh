#!/bin/bash

# Variables
VPC_NAME="Backend-VPC"
STACK_NAME="BackendStack"
REGION="us-west-2"
TEMPLATE_FILE="backend-vpc.yaml"

# Function to check if VPC with name $VPC_NAME already exists
check_VPC_exists() {
    # Check if VPC with the given name already exists
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --query "Vpcs[0].VpcId" --output text --region ${REGION})
    if [[ $VPC_ID == "None" ]]; then
        echo "VPC with name ${VPC_NAME} does not exist"
        return 1
    else
        echo "VPC with name ${VPC_NAME} already exists with VPC ID: ${VPC_ID}. Skipping stack creation."
        return 0
    fi
}

# Function to create the CloudFormation stack
create_stack() {
    echo "Creating CloudFormation stack..."
    aws cloudformation create-stack --stack-name ${STACK_NAME} --template-body file://${TEMPLATE_FILE} --capabilities CAPABILITY_NAMED_IAM --region ${REGION}
}

# Function to wait for the stack to complete
wait_for_stack() {
    echo "Waiting for CloudFormation stack to complete..."
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    if [ $? -eq 0 ]; then
        echo "Stack creation completed successfully."
    else
        echo "Stack creation failed."
        exit 1
    fi
}

# Function to get stack output in JSON format
get_stack_output() {
    echo "Fetching stack output..."
    OUTPUT=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs" --output json)

    echo "Stack output:"
    if command -v jq &> /dev/null; then
        echo "Pretty printing stack output using jq:"
        echo $OUTPUT | jq
    else
        echo "jq is not installed. Printing stack output in normal format:"
        echo $OUTPUT
    fi
}

check_VPC_exists
if [ $? -eq 1 ]; then
    create_stack
    wait_for_stack
else
    echo "No action needed. Certificate already exists."
fi

get_stack_output
