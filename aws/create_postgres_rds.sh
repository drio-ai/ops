#!/bin/bash

# Variables
REGION="us-west-2" # Oregon region
DB_INSTANCE_IDENTIFIER="my-postgres-db3"
DB_INSTANCE_CLASS="db.t3.micro" # t3.micro is the current free tier eligible instance type for PostgreSQL
ENGINE="postgres"
ALLOCATED_STORAGE="20"
DB_NAME="mydatabase"
MASTER_USERNAME="sushil"            # MasterUsername admin cannot be used as it is a reserved word used by the engine
MASTER_USER_PASSWORD="yourpassword" # Change this to a strong password
BACKUP_RETENTION_PERIOD="7"
VPC_NAME="vault-vaultVPC"
SUBNET_NAME1="vault-subnet-private1"
SUBNET_NAME2="vault-subnet-private2"
SUBNET_GROUP_NAME="postgres-subnet-group"
SECURITY_GROUP_NAME="default"

# Function to fetch subnet identifiers for a given subnet group
fetch_subnet_identifiers() {
    local subnet_group_name=$1
    local region=$2

    # Fetch subnet identifiers
    aws rds describe-db-subnet-groups --region "$REGION" --query "DBSubnetGroups[?DBSubnetGroupName=='$SUBNET_GROUP_NAME'].Subnets[*].SubnetIdentifier[]" --output json
}

# Function to check subnet group exists or not and create if Does not exists
check_and_create_subnet_group() {
    local SUBNET_GROUP_NAME="$1"

    if [[ -z "$SUBNET_GROUP_NAME" ]]; then
        echo "Error: Subnet group name is required." >&2
        return 1
    fi

    # List all DB subnet groups
    local subnet_groups
    subnet_groups=$(aws rds describe-db-subnet-groups --query 'DBSubnetGroups[*].DBSubnetGroupName' --output json)

    # Check if the subnet group exists
    local subnet_group
    subnet_group=$(echo "$subnet_groups" | jq -r --arg SUBNET_GROUP_NAME "$SUBNET_GROUP_NAME" '.[] | select(. == $SUBNET_GROUP_NAME)')

    if [[ "$subnet_group" == "" ]]; then
        echo "Creating subnet group for RDS using following 2 subnets: ${SUBNET_ID1} & ${SUBNET_ID2}"
        echo

        aws rds create-db-subnet-group \
            --db-subnet-group-name $SUBNET_GROUP_NAME \
            --db-subnet-group-description "My DB Subnet Group" \
            --subnet-ids $SUBNET_ID1 $SUBNET_ID2 \
            --query "DBSubnetGroup.DBSubnetGroupName" \
            --output text \
            --region $REGION
    else
        subnet_identifiers=$(fetch_subnet_identifiers "$SUBNET_GROUP_NAME" "$REGION")
        subnet_identifiers_str=$(echo "$subnet_identifiers" | jq -r '.[]' | tr '\n' ' ' | sed 's/ $//')

        echo "Subnet Group with name ${SUBNET_GROUP_NAME} having following subnets: ${subnet_identifiers_str} already exists"
        echo
    fi

}

# Get VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=$VPC_NAME" \
    --query "Vpcs[0].VpcId" \
    --output text \
    --region $REGION)

if [ "$VPC_ID" == "None" ]; then
    echo "VPC with name $VPC_NAME not found."
    exit 1
fi

echo
echo "Following script will create Postgres RDS instance in region=${REGION} inside VPC ${VPC_NAME}=${VPC_ID}"
echo

# Get First Subnet ID
SUBNET_ID1=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=$SUBNET_NAME1" \
    "Name=vpc-id,Values=$VPC_ID" \
    --query "Subnets[0].SubnetId" \
    --output text \
    --region $REGION)

if [ "$SUBNET_ID1" == "None" ]; then
    echo "Subnet with name $SUBNET_NAME1 not found in VPC $VPC_NAME."
    exit 1
fi

# Get Second Subnet ID
SUBNET_ID2=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=$SUBNET_NAME2" \
    "Name=vpc-id,Values=$VPC_ID" \
    --query "Subnets[0].SubnetId" \
    --output text \
    --region $REGION)

if [ "$SUBNET_ID2" == "None" ]; then
    echo "Subnet with name $SUBNET_NAME2 not found in VPC $VPC_NAME."
    exit 1
fi

# Check if Subnet Group exists or not, create if does not exists
check_and_create_subnet_group "$SUBNET_GROUP_NAME"

# Get default security group ID for the VPC
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    "Name=group-name,Values=${SECURITY_GROUP_NAME}" \
    --query "SecurityGroups[0].GroupId" \
    --output text \
    --region $REGION)

if [ "$SECURITY_GROUP_ID" == "None" ]; then
    echo "Default security group not found in VPC $VPC_NAME."
    exit 1
fi

echo "Using ${SECURITY_GROUP_NAME}=${SECURITY_GROUP_ID} security group to create RDS instance"
echo

# Fetch available versions of postgres and select latest version
POSTGRES_LATEST_VERSION=$(aws rds describe-db-engine-versions --region us-west-2 --engine postgres --query "DBEngineVersions[*].EngineVersion" | jq -r '. | sort_by(.) | last')

echo "Creating Postgres database instance with ${POSTGRES_LATEST_VERSION} version"
echo

set -x
# Create the RDS PostgreSQL instance
aws rds create-db-instance \
    --region $REGION \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine $ENGINE \
    --engine-version $POSTGRES_LATEST_VERSION \
    --allocated-storage $ALLOCATED_STORAGE \
    --db-name $DB_NAME \
    --master-username $MASTER_USERNAME \
    --master-user-password $MASTER_USER_PASSWORD \
    --backup-retention-period $BACKUP_RETENTION_PERIOD \
    --vpc-security-group-ids $SECURITY_GROUP_ID \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --no-publicly-accessible > ${DB_INSTANCE_IDENTIFIER}.spec

# Wait for the instance to be available
echo
echo "Waiting for RDS instance to be available..."
aws rds wait db-instance-available --db-instance-identifier $DB_INSTANCE_IDENTIFIER --region $REGION

# Get the endpoint of the RDS instance
ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --query "DBInstances[0].Endpoint.Address" \
    --output text \
    --region $REGION)

echo
echo "RDS PostgreSQL instance created successfully!"
echo "Endpoint: $ENDPOINT"
