import boto3
import logging
from botocore.exceptions import ClientError

def receive_from_sqs(region, queue_url, max_messages=10, wait_time=10):
    """
    Receive messages from an SQS queue.

    :param region: AWS region where the SQS queue is located
    :param queue_url: URL of the SQS queue
    :param max_messages: Maximum number of messages to retrieve
    :param wait_time: Wait time in seconds for long polling
    :return: List of messages or an empty list if no messages are available
    """
    try:
        print(f"Receiving messages from SQS queue: {queue_url}")
        sqs_client = boto3.client("sqs", region_name=region)
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time,
        )
        return response.get("Messages", [])
    except ClientError as e:
        logging.error(f"Failed to receive messages from queue {queue_url}: {e.response['Error']['Message']}")
    except Exception as e:
        logging.error(f"Unexpected error while receiving messages from queue {queue_url}: {e}")
    return []

def delete_from_sqs(region, queue_url, receipt_handle):
    """
    Delete a message from an SQS queue.

    :param region: AWS region where the SQS queue is located
    :param queue_url: URL of the SQS queue
    :param receipt_handle: Receipt handle of the message to delete
    :return: True if the message was deleted successfully, else False
    """
    try:
        print(f"Deleting message from SQS queue: {queue_url}")
        sqs_client = boto3.client("sqs", region_name=region)
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print("Message successfully deleted from the queue.")
        return True
    except ClientError as e:
        logging.error(f"Failed to delete message from queue {queue_url}: {e.response['Error']['Message']}")
    except Exception as e:
        logging.error(f"Unexpected error while deleting message from queue {queue_url}: {e}")
    return False
