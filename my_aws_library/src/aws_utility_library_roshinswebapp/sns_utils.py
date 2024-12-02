import boto3
import logging
from botocore.exceptions import ClientError

def publish_to_sns(region, topic_arn, message, subject=None):
    """
    Publish a message to an SNS topic.

    :param region: AWS region where the SNS topic is located
    :param topic_arn: ARN of the SNS topic
    :param message: The content of the message
    :param subject: Optional subject for the message
    :return: True if the message was published successfully, else False
    """
    try:
        print(f"Publishing message to SNS topic: {topic_arn}")
        sns_client = boto3.client("sns", region_name=region)
        publish_params = {"TopicArn": topic_arn, "Message": message}
        if subject:
            publish_params["Subject"] = subject
        sns_client.publish(**publish_params)
        print("Message successfully published to SNS topic.")
        return True
    except ClientError as e:
        logging.error(f"Failed to publish message to SNS topic {topic_arn}: {e.response['Error']['Message']}")
    except Exception as e:
        logging.error(f"Unexpected error while publishing message to SNS topic {topic_arn}: {e}")
    return False
