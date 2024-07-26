# irondome
An Open Source Threat Intelligence Service

This repository provides an AWS CloudFormation template (`cf.json`) to create and manage a Lambda function and EventBridge scheduler for IP set management. The IP set can be used as a rule in your AWS WAF WebACL.

## Getting Started

### Prerequisites

Before you start, make sure you have the following:
- An AWS account with sufficient permissions to create CloudFormation stacks, Lambda functions, and EventBridge rules.
- Your IP address whitelisted by the Razorpay Security Team.

### Cloning the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/freedom-finance-stack/irondome.git
cd irondome
```
### Editing the CloudFormation Template

To configure the `cf.json` file for your Lambda function, follow these steps:

1. Open the `cf.json` file in your preferred text editor.

2. Locate the `IrondomeLambdaFunction` resource block. It should look similar to this:

```json
"IrondomeLambdaFunction": {
    "Type": "AWS::Serverless::Function",
    "Properties": {
        "Handler": "lambda.lambda_handler",
        "Runtime": "python3.9",
        "CodeUri": "/home/cloudshell-user/irondome",
        "Role": { "Fn::GetAtt": ["IrondomeLambdaRole", "Arn"] },
        "Environment": {
            "Variables": {
                "IP_SET_NAME": "ipset-irondome-block",
                "REGION": "ap-south-1",
                "IRONDOME_API_KEY": "XXXXX"
            }
        }
    }
}
```
3. Update the CodeUri property to point to the location of your Lambda function code. If you are using an S3 bucket, it might look like this:
```json
"CodeUri": "s3://your-bucket/your-code"
```
4.Update the environment variables under the Environment section as needed:

  **IP_SET_NAME**: Set this to the name you want for your IP set.
  **REGION**: Update this to the AWS region where you are deploying the resources.
  **IRONDOME_API_KEY**: Replace "XXXXX" with your actual API key provided by razorpay security team.
  Example:
```json
"Environment": {
    "Variables": {
        "IP_SET_NAME": "your-ip-set-name",
        "REGION": "your-region",
        "IRONDOME_API_KEY": "your-api-key"
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
    --template-file ./cf.json \
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
- 
### Next Steps
**Creating and Managing the IP Set**
The CloudFormation template will create a Lambda function and an EventBridge scheduler to manage the IP set. The IP set can then be used as a rule in your AWS WAF WebACL.
1. Navigate to the AWS WAF console.
2. Create or update your WebACL.
3. Add a new rule to the WebACL and choose the IP set created by the CloudFormation stack.
