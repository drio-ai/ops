#!/bin/bash

# Setting environment variables using single source file
source ../aws.env

# Function to wait for the stack to complete
wait_for_stack() {
    echo "Waiting for CloudFormation stack to complete..."
    aws cloudformation wait stack-create-complete --stack-name $POSTGRES_STACK_NAME --region $BACKEND_REGION
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
    OUTPUT=$(aws cloudformation describe-stacks --stack-name $POSTGRES_STACK_NAME --region $BACKEND_REGION --query "Stacks[0].Outputs" --output json)

    echo "Stack output:"
    if command -v jq &> /dev/null; then
        echo $OUTPUT | jq
    else
        echo $OUTPUT
    fi
}

get_VPC_id() {
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${BACKEND_VPC_NAME}" --region $BACKEND_REGION --query "Vpcs[*].VpcId" --output text)

    if [ "${VPC_ID}" == "None" ]; then
        echo "None"
    else
        echo "$VPC_ID"
    fi
}

get_private_subnet1_id() {
    PRIVATE_SUBNET1_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${BACKEND_PRIVATE_SUBNET1}" --region $BACKEND_REGION --query "Subnets[*].SubnetId" --output text)

    if [ "${PRIVATE_SUBNET1_ID}" == "" ]; then
        echo "None"
    else
        echo $PRIVATE_SUBNET1_ID
    fi
}

get_private_subnet2_id() {
    PRIVATE_SUBNET2_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${BACKEND_PRIVATE_SUBNET2}" --region $BACKEND_REGION --query "Subnets[*].SubnetId" --output text)
    if [ "${PRIVATE_SUBNET2_ID}" == "" ]; then
        echo "None"
    else
        echo $PRIVATE_SUBNET2_ID
    fi
}

create_stack() {
    Echo "Creating Cloudformation stack"
    aws cloudformation create-stack --stack-name ${POSTGRES_STACK_NAME} \
        --template-body file://postgres-rds-cloudformation.yaml \
        --parameters ParameterKey=VpcId,ParameterValue=${VPC_ID} \
        ParameterKey=SubnetId1,ParameterValue=${SUBNET1} \
        ParameterKey=SubnetId2,ParameterValue=${SUBNET2} \
        ParameterKey=MasterUserPassword,ParameterValue=${MASTER_USER_PASSWORD} \
        --capabilities CAPABILITY_NAMED_IAM --region ${BACKEND_REGION}
}

VPC_ID=$(get_VPC_id)
SUBNET1=$(get_private_subnet1_id)
SUBNET2=$(get_private_subnet2_id)
if [ $SUBNET1 == "None" ] || [ $SUBNET2 == "None" ] || [ $VPC_ID == "None" ]; then
    echo "Unable to fetch Subnet IDs or VPC ID, exiting.."
fi

create_stack
wait_for_stack
get_stack_output
