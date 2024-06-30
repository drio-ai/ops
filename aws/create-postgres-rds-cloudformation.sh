#!/bin/bash

REGION=us-west-2
STACK_NAME=postgres-stack1
VPC_NAME=BackendStack-VPC
POSTGRES_PASSWORD=sushilpostgres123
PRIVATE_SUBNET1=BackendStack-PrivateSubnet1
PRIVATE_SUBNET2=BackendStack-PrivateSubnet2

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
        echo $OUTPUT | jq
    else
        echo $OUTPUT
    fi
}

get_VPC_id() {
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --region us-west-2 --query "Vpcs[*].VpcId" --output text)

    if [ "${VPC_ID}" == "None" ]; then
        echo "VPC with name ${VPC_NAME} not found, exiting.."
        exit 1
    fi

    echo "$VPC_ID"
}

get_private_subnet1_id() {
    PRIVATE_SUBNET1_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${PRIVATE_SUBNET1}" --region us-west-2 --query "Subnets[*].SubnetId" --output text)

    if [ "${PRIVATE_SUBNET1_ID}" == "" ]; then
        echo "Unable to fetch ID of subnet named ${PRIVATE_SUBNET1}"
        exit
    fi
    echo $PRIVATE_SUBNET1_ID
}

get_private_subnet2_id() {
    PRIVATE_SUBNET2_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${PRIVATE_SUBNET2}" --region us-west-2 --query "Subnets[*].SubnetId" --output text)
    if [ "${PRIVATE_SUBNET2_ID}" == "" ]; then
        echo "Unable to fetch ID of subnet named ${PRIVATE_SUBNET2}"
        exit
    fi
    echo $PRIVATE_SUBNET2_ID

}

create_stack() {
    Echo "Creating Cloudformation stack"
    aws cloudformation create-stack --stack-name ${STACK_NAME} \
        --template-body file://postgres-rds-cloudformation.yaml \
        --parameters ParameterKey=VpcId,ParameterValue=${VPC_ID} \
        ParameterKey=SubnetId1,ParameterValue=${SUBNET1} \
        ParameterKey=SubnetId2,ParameterValue=${SUBNET2} \
        ParameterKey=MasterUserPassword,ParameterValue=${POSTGRES_PASSWORD} \
        --capabilities CAPABILITY_NAMED_IAM --region ${REGION}
}

VPC_ID=$(get_VPC_id)
SUBNET1=$(get_private_subnet1_id)
SUBNET2=$(get_private_subnet2_id)
create_stack
wait_for_stack
get_stack_output
