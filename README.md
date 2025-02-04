# Suraksha Shield
An Open Source Threat Intelligence Service

This repository provides an AWS CloudFormation template ([cf.json](./infra/aws/cf.json)) to create and manage a Lambda function and EventBridge scheduler for IP set management. The IP set can be used as a rule in your AWS WAF WebACL.

### API Endpoints

1. IOCs API
  - **Endpoint**: https://surakshashield.razorpay.com/v1/surakshashield/iocs
  - **Description**: This API endpoint retrieves Indicators of Compromise (IOCs). IOCs are pieces of information that help identify potential threats or malicious activity.
  - **Response Format**:
    ```json
      [
        {
          "category": "****",
          "value": "**.**.**.**",
          "event_timestamp": "***",
          "cluster_tags": "****",
          "type": "****",
          "attributeid": "***",
          "tags": "****"
        }
      ]
    ```
2. IOCTypes API
  - **Endpoint**: https://surakshashield.razorpay.com/v1/surakshashield/ioctypes
  - **Description**: This API endpoint provides a list of IOC types. IOC types categorize the different kinds of indicators used in threat intelligence.
  - **Response**: Returns a list of IOCTypes
3. IOCCategories API
  - **Endpoint**: https://surakshashield.razorpay.com/v1/surakshashield/ioccategories
  - **Description**: This API endpoint returns a list of IOC categories. Categories group different IOCs into meaningful classifications to help in organizing and understanding threat data.
  - **Response**: Returns a list of IOCCategories

## Getting Started

### Prerequisites

Before you start, make sure you have the following:
- An AWS account with sufficient permissions to create CloudFormation stacks, Lambda functions, and EventBridge rules.
- AWS CLI installed and configured on your local machine.

### Cloning the Repository

Clone the repository to your local machine:
  ```bash
   git clone https://github.com/freedom-finance-stack/suraksha-shield.git
   cd suraksha-shield
  ```
### Editing the CloudFormation Template

To configure the [cf.json](./infra/aws/cf.json) file for your Lambda function, follow these steps:

1. Open the [cf.json](./infra/aws/cf.json) file in your preferred text editor.

3. Locate the `SurakshaShieldLambdaFunction` resource block. It should look similar to this:

    ```json
    "SurakshaShieldLambdaFunction": {
            "Type": "AWS::Serverless::Function",
            "Properties": {
              "Handler": "lambda.lambda_handler",
              "Runtime": "python3.9",
              "CodeUri": "/home/cloudshell-user/suraksha-shield/infra/aws/lambda",
              "Role": { "Fn::GetAtt" : [ "SurakshaShieldLambdaRole" , "Arn" ] },
              "Environment": {
                "Variables": {
                    "IP_SET_NAME": "ipset-suraksha-shield-block",
                    "REGION": "ap-south-1",
                    "SURAKSHASHIELD_API_KEY": "XXXXX"
                }
             },
             "VpcConfig": {
                "SecurityGroupIds": ["sg-xxxxxxxx"],
                "SubnetIds": ["subnet-xxxxxxxx"]
             }
        }
    }
    ```

4. Update the environment variables under the Environment section as needed:

-  **IP_SET_NAME**: Set this to the name you want for your IP set.
-  **REGION**: Update this to the AWS region where you are deploying the resources.
-  **SURAKSHASHIELD_API_KEY**: Replace "XXXXX" with your actual API key provided by razorpay security team.
  
      Example:
      ```json
      "Environment": {
          "Variables": {
              "IP_SET_NAME": "your-ip-set-name",
              "REGION": "your-region",
              "SURAKSHASHIELD_API_KEY": "your-api-key"
          }
      }
      ```
    
5. Save your changes to the JSON file.
Make sure to replace all placeholder values with your actual data and adjust the configuration according to your specific requirements.

### Deploying the CloudFormation Stack

To deploy the CloudFormation stack using your JSON template, follow these steps:

1. **Package the CloudFormation Template**

   First, package the CloudFormation template to upload local artifacts (e.g., Lambda function code) to an S3 bucket. Run the following AWS CLI command:

    ```bash
    aws cloudformation package \
        --template-file ./infra/aws/cf.json \
        --s3-bucket your-s3-bucket-name \
        --s3-prefix your-s3-prefix \
        --output-template-file packaged-template.json \
        --use-json
    ```
- Replace **'your-s3-bucket-name'** with the name of the S3 bucket where the artifacts will be uploaded.
- Replace **'your-s3-prefix'** with a prefix for the S3 objects (optional).
The command will generate a packaged-template.json file that references the uploaded artifacts.

2. **Deploy the CloudFormation Template**

    Deploy the CloudFormation stack using the packaged template file:

    ```bash
    aws cloudformation deploy \
        --template-file packaged-template.json \
        --stack-name my-threat-intelligence-stack \
        --capabilities CAPABILITY_IAM
    ```
- Replace **'packaged-template.json'** with the path to the packaged template file if it's located elsewhere.
- Replace **'my-threat-intelligence-stack'** with the name you want to assign to your CloudFormation stack.

3. **Set Up AWS NAT Gateway and VPC**

   After deploying the CloudFormation stack, set up an AWS NAT Gateway and run the Lambda function inside a VPC to get a static IP. This static IP needs to be whitelisted by the Razorpay Security Team (security@razorpay.com).

### Steps to Set Up NAT Gateway & VPC for Static IP:

1. **Create a VPC (if one doesn't exist):**
   - Go to the VPC Console and create a new VPC.
   - Ensure that the VPC has both private and public subnets:
     - Private subnets for Lambda functions.
     - Public subnet for the NAT Gateway.

2. **Set Up a NAT Gateway:**
   - Go to the VPC Console and create a NAT Gateway in the public subnet.
   - Elastic IP (EIP): Allocate an Elastic IP for the NAT Gateway. This will be the static IP used by Lambda for outbound traffic.

3. **Configure Route Tables:**
   - Create two route tables:
     - Public Route Table: Associate this with the public subnet and set a route to the Internet Gateway for public access.
     - Private Route Table: Associate this with the private subnet where your Lambda function will reside. Set a route to the NAT Gateway for outbound access.

4. **Update Lambda Function to Run in VPC:**
   - After your CloudFormation stack is deployed, manually update the Lambda function configuration to run in the private subnet within the VPC.
     - Go to the Lambda Console.
     - Select the Lambda function you created via CloudFormation.
     - Under the VPC section, select your newly created VPC.
     - Choose the private subnet(s) (where the Lambda function should run).
     - Add the security group that is appropriate for your Lambda function (you can use an existing one or create a new security group).

5. **Obtain the Static IP:**
   - Once the NAT Gateway is configured, the Elastic IP (EIP) you allocated to the NAT Gateway will be used by your Lambda function for outbound traffic.
   - You can find the Elastic IP in the EC2 Console.

6. **Share the Static IP with Razorpay:**
   - Once everything is set up, provide the Elastic IP from the NAT Gateway to the Razorpay Security Team (security@razorpay.com) for IP whitelisting.

### Next Steps

**Creating and Managing the IP Set**
The CloudFormation template will create a Lambda function and an EventBridge scheduler to manage the IP set. The IP set can then be used as a rule in your AWS WAF WebACL.
1. Navigate to the AWS WAF console.
2. Create or update your WebACL.
3. Add a new rule to the WebACL and choose the IP set created by the CloudFormation stack.
