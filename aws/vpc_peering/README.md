## Create VPC Peering between 2 VPCs in different region:

#### NOTE: VPC Names and regions are mentioned in below aws.env, you might need to update the values of variables in script before executing it

#### NOTE: Below script creates VPC Peering between VPCs named ControllerVPC (us-east-1 region) and BackendVPC (us-west-2 region), either change the parameters in create-backend-controller-vpc-peering.sh script named $CONTROLLER_REGION and $CONTROLLER_VPC_NAME or run following named 'create-controller-vpc-cloudformation.sh' script which creates pre-requisite controller VPC in appropriate region.

#### Steps:

    1) Pre-requisite: You must have VPC named ControllerVPC in us-east-1 region or change script parameters as mentioned above. To create this ControllerVPC, run following script:

    aws/controller_vpc/create-controller-vpc-cloudformation.sh

Once controller VPC is in place, we can run following script to create peering between the 2 VPCs

#### Note: If the Name and region of Controller VPC is not 'ControllerVPC' and us-east-1 respectively, then update environment variables in aws/aws.env file named 'CONTROLLER_REGION' & 'CONTROLLER_VPC_NAME' or add these 2 variables in below script after source ../aws.env statement to overwrite existing values.

    aws/vpc_peering/create-backend-controller-vpc-peering.sh