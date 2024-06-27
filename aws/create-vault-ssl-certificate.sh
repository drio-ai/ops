#!/bin/bash

# Variables
REGION="us-west-2" # Change this to your desired region
DOMAIN="vault.ddx.drio.ai"
STACK_NAME="SSLCertificateStack"
TEMPLATE_FILE="ssl-certificate-template.yaml"

# Function to check if the domain certificate already exists
check_certificate_exists() {
    CERTIFICATE_ARN=$(aws acm list-certificates --region $REGION --query "CertificateSummaryList[?DomainName=='$DOMAIN'].CertificateArn" --output text)
    if [ -z "$CERTIFICATE_ARN" ]; then
        echo "Certificate for domain $DOMAIN does not exist."
        return 1
    else
        echo "Certificate for domain $DOMAIN already exists with ARN: $CERTIFICATE_ARN"
        return 0
    fi
}

# Function to create the CloudFormation stack
create_stack() {
    echo "Creating CloudFormation stack..."
    aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://$TEMPLATE_FILE --region $REGION
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
    echo "Stack output in JSON format:"
    echo $OUTPUT
}

# Main script
check_certificate_exists
if [ $? -eq 1 ]; then
    create_stack
    wait_for_stack
    get_stack_output
else
    echo "No action needed. Certificate already exists."
fi
