#!/bin/bash

# Setting environment variables using single source file
source ../aws.env

# Function to check if the domain certificate already exists
check_certificate_exists() {
    CERTIFICATE_ARN=$(aws acm list-certificates --region $BACKEND_REGION --query "CertificateSummaryList[?DomainName=='$VAULT_DOMAIN'].CertificateArn" --output text)
    if [ -z "$CERTIFICATE_ARN" ]; then
        echo "Certificate for domain $VAULT_DOMAIN does not exist."
        return 1
    else
        echo "Certificate for domain $VAULT_DOMAIN already exists with ARN: $CERTIFICATE_ARN"
        return 0
    fi
}

# Function to create the CloudFormation stack
create_stack() {
    echo "Creating CloudFormation stack..."
    aws cloudformation create-stack --stack-name $SSL_CERTIFICATE_STACK_NAME --template-body file://$SSL_CERTIFICATE_TEMPLATE_FILE --region $BACKEND_REGION
}

# Function to wait for the stack to complete
wait_for_stack() {
    echo "Waiting for CloudFormation stack to complete..."
    aws cloudformation wait stack-create-complete --stack-name $SSL_CERTIFICATE_STACK_NAME --region $BACKEND_REGION
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
    OUTPUT=$(aws cloudformation describe-stacks --stack-name $SSL_CERTIFICATE_STACK_NAME --region $BACKEND_REGION --query "Stacks[0].Outputs" --output json)

    echo "Stack output:"
    if command -v jq &> /dev/null; then
        echo $OUTPUT | jq
    else
        echo $OUTPUT
    fi
}

# Main script
check_certificate_exists
if [ $? -eq 1 ]; then
    create_stack
    wait_for_stack
else
    echo "No action needed. Certificate already exists."
fi

get_stack_output
