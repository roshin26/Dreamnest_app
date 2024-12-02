import boto3
import logging
import json
from botocore.exceptions import ClientError



def invoke_lambda(region, function_name, payload, invocation_type="RequestResponse"):
    """
    Invoke an AWS Lambda function.

    :param region: AWS region where the Lambda function is deployed
    :param function_name: Name of the Lambda function to invoke
    :param payload: Dictionary containing the input payload for the function
    :param invocation_type: Invocation type ('RequestResponse', 'Event', or 'DryRun')
                            - 'RequestResponse': Waits for the function's response
                            - 'Event': Asynchronous invocation
                            - 'DryRun': Validates if the function can be invoked
    :return: The response from the Lambda function or None if an error occurs
    """
    try:
        print(f"Invoking Lambda function: {function_name}")
        lambda_client = boto3.client("lambda", region_name=region)
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload),
        )
        if invocation_type == "RequestResponse":
            response_payload = json.loads(response["Payload"].read())
            logging.info(f"Lambda response: {response_payload}")
            return response_payload
        else:
            logging.info(f"Lambda invocation successful: {response}")
            return response
    except ClientError as e:
        logging.error(f"Failed to invoke Lambda function {function_name}: {e.response['Error']['Message']}")
    except Exception as e:
        logging.error(f"Unexpected error while invoking Lambda function {function_name}: {e}")
    return None
