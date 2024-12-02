import boto3
import logging
from botocore.exceptions import ClientError

def upload_file(file_name, bucket, object_key=None, extra_args=None):
    """
    Upload a file to an S3 bucket.

    :param file_name: Path to the file to upload
    :param bucket: Name of the S3 bucket
    :param object_key: S3 object key (optional). Defaults to file_name if not specified
    :param extra_args: Dictionary of extra parameters to pass to S3 upload (e.g., ACL, ContentType)
    :return: True if file was uploaded successfully, else False
    """
    if object_key is None:
        object_key = file_name
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_key, ExtraArgs=extra_args)
        logging.info(f"File {file_name} uploaded to {bucket}/{object_key}.")
        return True
    except ClientError as e:
        logging.error(e)
        return False
