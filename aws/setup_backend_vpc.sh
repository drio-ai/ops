#!/bin/bash

# Variables
REGION="us-west-2"
VPC_NAME="vault-vaultVPC"
CIDR_BLOCK="10.0.0.0/16"
AZS=("us-west-2a" "us-west-2b" "us-west-2c")
PUBLIC_SUBNET_CIDR=("10.0.1.0/24" "10.0.2.0/24" "10.0.3.0/24")
PRIVATE_SUBNET_CIDR=("10.0.4.0/24" "10.0.5.0/24" "10.0.6.0/24")
PUBLIC_SUBNET_PREFIX="vault-subnet-public"
PRIVATE_SUBNET_PREFIX="vault-subnet-private"
IGW_NAME="vault-igw"
PUBLIC_RT_NAME="vault-public-rt"
PRIVATE_RT_NAME="vault-private-rt"
SG_NAME="vault-sg"
KEY_NAME="vault-private-ec2-kp"
TAG_KEY="Name"
TAG_VALUE="vault-elastic-ip"

# Function to configure AWS CLI to use the specified region
set_aws_region() {
    aws configure set region ${REGION}
    if [ $? -eq 0 ]; then
        echo "AWS region set to ${REGION}"
        echo
    else
        echo "Failed to set AWS region"
        exit 1
    fi
}

check_public_route_table_exist() {
    ROUTE_TABLES=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --query 'RouteTables[*].{ID:RouteTableId,Name:Tags[?Key==`Name`].Value|[0]}' --output json)
    ROUTE_TABLE_ID=$(echo "$rt_tables" | jq -r --arg PUBLIC_RT_NAME "$PUBLIC_RT_NAME" '.[] | select(.Name == $PUBLIC_RT_NAME) | .ID')
    ROUTE_TABLE_NAME=$(echo "$ROUTE_TABLES" | jq -r --arg PUBLIC_RT_NAME "$PUBLIC_RT_NAME" '.[] | select(.Name == $PUBLIC_RT_NAME) | .Name')

    if [[ "$ROUTE_TABLE_NAME" == "$PUBLIC_RT_NAME" ]]; then
        echo ${ROUTE_TABLE_ID}
    else
        echo "None"
    fi
}

# Function to create a public route table and return its ID
create_public_route_table() {
    local VPC_ID="$1"
    local IGW_ID="$2"

    # Create Route Table for public subnets
    PUBLIC_RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
    if [ -n "$PUBLIC_RT_ID" ]; then
        aws ec2 create-tags --resources $PUBLIC_RT_ID --tags Key=Name,Value=$PUBLIC_RT_NAME
        aws ec2 create-route --route-table-id $PUBLIC_RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
        echo "$PUBLIC_RT_ID"
    else
        echo ""
    fi
}

# Function to check if the specified number of subnets with a given prefix exist in the VPC
check_subnets_exist() {
    local VPC_ID="$1"
    local PREFIX="$2"
    local SUBNET_COUNT="$3"

    # Get the count of subnets with the specified prefix in the VPC
    COUNT=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:Name,Values=${PREFIX}*" --query 'length(Subnets)' --output text)

    if [ "$COUNT" -eq "$SUBNET_COUNT" ]; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to create the specified number of subnets with a given prefix in the VPC
create_subnets() {
    local VPC_ID="$1"
    local PREFIX="$2"
    local SUBNET_COUNT="$3"
    local SUBNET_TYPE="$4" # 'private' or 'public'
    local AZ=('a' 'b' 'c')

    for ((i = 1; i <= $SUBNET_COUNT; i++)); do
        c=-1
        if [ $PREFIX == $PUBLIC_SUBNET_PREFIX ]; then
            c=2
        fi
        SUBNET_CIDR="10.0.$((c + i + 1)).0/24" # Adjust CIDR range as needed
        SUBNET_NAME="${PREFIX}$i"

        # Create subnet
        SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $SUBNET_CIDR --availability-zone ${REGION}${AZ[$((i - 1))]} --query 'Subnet.SubnetId' --output text)
        if [ -n "$SUBNET_ID" ]; then
            aws ec2 create-tags --resources $SUBNET_ID --tags Key=Name,Value=$SUBNET_NAME
            echo "Created $SUBNET_TYPE subnet: $SUBNET_NAME ($SUBNET_ID)"
        else
            echo "Failed to create $SUBNET_TYPE subnet: $SUBNET_NAME"
        fi
    done
}

# Function to ensure VPC has required subnets
ensure_vpc_subnets() {
    local VPC_ID="$1"

    # Check if private subnets exist
    if ! $(check_subnets_exist "$VPC_ID" "$PRIVATE_SUBNET_PREFIX" 3); then
        create_subnets "$VPC_ID" "$PRIVATE_SUBNET_PREFIX" 3 "private"
    else
        echo "Required number of private subnets already exist."
    fi

    # Check if public subnets exist
    if ! $(check_subnets_exist "$VPC_ID" "$PUBLIC_SUBNET_PREFIX" 3); then
        create_subnets "$VPC_ID" "$PUBLIC_SUBNET_PREFIX" 3 "public"
    else
        echo "Required number of public subnets already exist."
    fi
}

# Function to check if an Internet Gateway with the specified name exists
# and if attached to the specified VPC
check_igw_exists() {
    local VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --query 'Vpcs[0].VpcId' --output text)
    if [ -z "$VPC_ID" ]; then
        echo "VPC ${VPC_NAME} not found."
        return 1
    fi

    local IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=tag:Name,Values=${IGW_NAME}" --query 'InternetGateways[0].InternetGatewayId' --output text)
    if [ "$IGW_ID" == "None" ]; then
        echo $IGW_ID
        return
    fi
    if [ -n "$IGW_ID" ]; then
        # Check if the Internet Gateway is attached to the VPC
        local ATTACHED_VPC_ID=$(aws ec2 describe-internet-gateways --internet-gateway-ids ${IGW_ID} --query 'InternetGateways[0].Attachments[0].VpcId' --output text)
        if [ "$ATTACHED_VPC_ID" == "$VPC_ID" ]; then
            echo "$IGW_ID"
        else
            # Attach Internet Gateway to the VPC
            aws ec2 attach-internet-gateway --internet-gateway-id ${IGW_ID} --vpc-id ${VPC_ID}
            echo "$IGW_ID"
        fi
    else
        echo ""
    fi
}

# Function to create an Internet Gateway with the specified name
# and attach it to the specified VPC
create_igw() {
    local VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --query 'Vpcs[0].VpcId' --output text)
    if [ -z "$VPC_ID" ]; then
        echo "VPC ${VPC_NAME} not found."
        return 1
    fi

    local IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
    if [ -n "$IGW_ID" ]; then
        aws ec2 create-tags --resources ${IGW_ID} --tags Key=Name,Value=${IGW_NAME}
        aws ec2 attach-internet-gateway --internet-gateway-id ${IGW_ID} --vpc-id ${VPC_ID}
        echo "$IGW_ID"
    else
        echo ""
    fi
}

# Function to allocate and tag an Elastic IP
allocate_and_tag_elastic_ip() {
    # Check if Elastic IP with the specified tag already exists
    EXISTING_IP=$(aws ec2 describe-addresses --region $REGION --filters "Name=tag:$TAG_KEY,Values=$TAG_VALUE" --query 'Addresses[0].PublicIp' --output text)

    if [ "$EXISTING_IP" != "None" ]; then
        echo "$EXISTING_IP"
        return 0
    fi

    # Allocate Elastic IP
    ALLOCATION_ID=$(aws ec2 allocate-address --region $REGION --query 'AllocationId' --output text)

    if [ -z "$ALLOCATION_ID" ]; then
        echo "Failed to allocate Elastic IP."
        return 1
    fi

    # Tag the Elastic IP
    aws ec2 create-tags --region $REGION --resources $ALLOCATION_ID --tags Key=$TAG_KEY,Value=$TAG_VALUE

    if [ $? -ne 0 ]; then
        echo "Failed to tag Elastic IP."
        # Release the allocated Elastic IP if tagging fails
        aws ec2 release-address --region $REGION --allocation-id $ALLOCATION_ID
        echo "Elastic IP released due to tagging failure."
        return 1
    fi

    # Get the public IP of the allocated Elastic IP
    PUBLIC_IP=$(aws ec2 describe-addresses --region $REGION --allocation-ids $ALLOCATION_ID --query 'Addresses[0].PublicIp' --output text)

    echo "$PUBLIC_IP"
}

# Function to check if a VPC with the specified name already exists
check_vpc_exists() {
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${VPC_NAME}" --query 'Vpcs[0].VpcId' --output text)

    if [ "$VPC_ID" != "None" ]; then
        echo ${VPC_ID}
    else
        echo "None"
    fi
}

# Function to create a VPC with the specified CIDR block and name
create_vpc() {
    VPC_ID=$(aws ec2 create-vpc --cidr-block ${CIDR_BLOCK} --query 'Vpc.VpcId' --output text)

    if [ -z "$VPC_ID" ]; then
        echo "Failed to create VPC."
        exit 1
    fi

    # Tag the VPC with the specified name
    aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}

    # Enable DNS hostnames & DNS support
    aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-support "{\"Value\":true}"
    aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-hostnames "{\"Value\":true}"

    echo ${VPC_ID}
}

create_nat_gateway() {
    EIP_ALLOC_IP=$1

    # Check if NAT Gateway with specific tag exists
    NAT_GATEWAY_ID=$(aws ec2 describe-nat-gateways \
        --filter "Name=tag:Name,Values=${TAG_NAME}" \
        --query 'NatGateways[0].NatGatewayId' \
        --output text)

    if [ -n "$NAT_GATEWAY_ID" ]; then
        echo ${NAT_GATEWAY_ID}
    else
        # Fetch Elastic IP allocation ID
        EIP_ALLOC_ID=$(aws ec2 describe-addresses --filters "Name=public-ip,Values=${EIP_ALLOC_IP}" --query 'Addresses[0].AllocationId' --output text)

        if [ -n "$EIP_ALLOC_ID" ]; then
            continue
        else
            exit 1
        fi

        # Create NAT Gateway in the first public subnet
        SUBNET_NAME=${PUBLIC_SUBNET_PREFIX}1

        # Fetch subnet ID
        SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=${SUBNET_NAME}" --query 'Subnets[0].SubnetId' --output text)

        if [ -n "$SUBNET_ID" ]; then
            continue
        else
            echo "None"
        fi

        NAT_GW_ID=$(aws ec2 create-nat-gateway --subnet-id ${SUBNET_ID} --allocation-id $EIP_ALLOC_ID --query 'NatGateway.NatGatewayId' --output text)

        # Wait for the NAT Gateway to become available
        echo "Waiting for NAT Gateway to become available..."
        aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID
        echo "NAT Gateway is now available."

        # Tag NAT Gateway with appropriate name
        TAG_NAME="vault-nat-gw"
        aws ec2 create-tags --resources $NAT_GW_ID --tags Key=Name,Value="$TAG_NAME"
        echo $NAT_GW_ID
    fi
}

# Set AWS region
set_aws_region

# Check and create VPC
VPC_ID=$(check_vpc_exists)
if [ "$VPC_ID" == "None" ]; then
    echo "VPC ${VPC_NAME} didn't exists in ${REGION} region, creating..."
    VPC_ID=$(create_vpc)
    echo "VPC ${VPC_NAME}=${VPC_ID} created successfully"
else
    echo "VPC ${VPC_NAME}=${VPC_ID} already exists"
    echo
fi

# Check and create Internet Gateway and attach to VPC
IGW_ID=$(check_igw_exists)
if [ "$IGW_ID" == "None" ]; then
    echo "Internet Gateway named ${IGW_NAME} does not exists, creating"
    IGW_ID=$(create_igw)
    echo "Internet Gateway ${IGW_NAME}=${IGW_ID} created succesfully"
else
    echo "Internet Gateway ${IGW_NAME}=${IGW_ID} already exists"
    echo
fi

# Create the public route table if VPC_ID and IGW_ID are not empty
PUBLIC_RT_ID=$(check_public_route_table_exist)
if [ -n "$VPC_ID" ] && [ -n "$IGW_ID" ] && [ "$PUBLIC_RT_ID" == "None" ]; then
    echo "Public route table with name ${PUBLIC_RT_NAME} does not exists, creating"
    PUBLIC_RT_ID=$(create_public_route_table "$VPC_ID" "$IGW_ID")
    echo "Public route table ${PUBLIC_RT_NAME}=${PUBLIC_RT_ID} created successfully"
else
    echo "Public route table ${PUBLIC_RT_NAME}=${PUBLIC_RT_ID} already exists"
    echo
fi

# Ensure VPC has required subnets
if [ -n "$VPC_ID" ]; then
    ensure_vpc_subnets "$VPC_ID"
else
    echo "Failed to create or find VPC."
fi

exit

# Create Elastic IP for NAT Gateway
EIP_ALLOC_IP=$(allocate_and_tag_elastic_ip)
echo "Elastic IP allocated with ID $EIP_ALLOC_IP"

# Create NAT gateway
NAT_GW_ID=$(create_nat_gateway $EIP_ALLOC_IP)

# Create Route Tables for private subnets and associate them
for i in ${!PRIVATE_SUBNET_IDS[@]}; do
    PRIVATE_RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
    aws ec2 create-tags --resources $PRIVATE_RT_ID --tags Key=Name,Value="${PRIVATE_RT_NAME}-${i}"
    aws ec2 create-route --route-table-id $PRIVATE_RT_ID --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_GW_ID
    aws ec2 associate-route-table --subnet-id ${PRIVATE_SUBNET_IDS[$i]} --route-table-id $PRIVATE_RT_ID
    echo "Private Route Table created with ID $PRIVATE_RT_ID and associated with private subnet ${PRIVATE_SUBNET_IDS[$i]}"
done

echo "VPC, Subnets, Route Tables, and NAT Gateway setup completed."
