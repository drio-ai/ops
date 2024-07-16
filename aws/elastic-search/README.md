# Elasticsearch Deployment on AWS EC2 using Docker Compose

This repository contains the necessary files to deploy an Elasticsearch cluster on AWS EC2 instances using Docker Compose and CloudFormation.

## Prerequisites

- AWS account
- An existing VPC.
- An existing EC2 Key Pair (e.g., `elastic.pem`)

## CloudFormation Template

The `elastic-search.yaml` CloudFormation template provisions the following resources:
- Three EC2 instances (`es01`, `es02`, `es03`) in the specified VPC and subnets
- One EC2 instance (`fluentd`) in the specified VPC
- A Security Group allowing traffic on ports 9200, 9300 and 24224 (Elasticsearch)
- An Internal Application Load Balancer (ALB) for Elasticsearch with a target group
- An Internet-Facing Application Load Balancer (ALB) for Fluentd with a target group 


## Parameters

The following parameters can be configured in the CloudFormation template:

- `InstanceType`: EC2 instance type for Elasticsearch nodes (default: `m5ad.large`)
- `InstanceTypeForESBuilder`: EC2 instance type for ES Builder (default: `t2.micro`)
- `VPCID`: VPC ID where the resources will be deployed
- `KeyName`: Name of an existing EC2 Key Pair for SSH access (default: `elastic`)
- `S3Bucket`: S3 bucket containing the SSH key
- `S3Key`: S3 key of the SSH key file
- `AccessKeyId`: AWS Access Key ID
- `SecretAccessKey`: AWS Secret Access Key (hidden in output)
- `Subnet1Cidr`: CIDR block for the first private subnet (default: `172.31.96.0/20`)
- `Subnet2Cidr`: CIDR block for the second private subnet (default: `172.31.112.0/20`)
- `Subnet3Cidr`: CIDR block for the third private subnet (default: `172.31.128.0/20`)

## Deployment

### Step 1: Create the CloudFormation Stack

1. Go to the AWS Management Console and navigate to CloudFormation.
2. Create a new stack and upload the `elastic-search.yaml` template.
3. Provide the required parameters and create the stack.

## Cleanup

To clean up the resources created by this stack, delete the CloudFormation stack from the AWS Management Console.


