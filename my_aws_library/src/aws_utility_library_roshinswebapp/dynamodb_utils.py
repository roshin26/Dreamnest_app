import boto3
import logging
from botocore.exceptions import ClientError

def store_an_item(region, table_name, item):
    """
    Store an item in a DynamoDB table.

    :param region: AWS region where the DynamoDB table is located
    :param table_name: Name of the DynamoDB table
    :param item: Dictionary containing the item data to save
    :return: True if item was stored successfully, else False
    """
    try:
        print(f"\nStoring the item {item} in the table {table_name}...")  
        dynamodb_resource = boto3.resource("dynamodb", region_name=region)
        table = dynamodb_resource.Table(table_name)
        table.put_item(Item=item)
        print(f"Item successfully stored in table {table_name}.")
        return True
    
    except ClientError as e:
        logging.error(f"Failed to store item in table {table_name}: {e.response['Error']['Message']}")

    except Exception as e:
        logging.error(f"Unexpected error while storing item in table {table_name}: {e}")
    
    return False

def get_property(region, table_name, property_id):
    """
    Retrieve a property record from a DynamoDB table using the property_id.

    Args:
        region (str): AWS region where the DynamoDB table is hosted.
        table_name (str): Name of the DynamoDB table.
        property_id (str): Unique ID of the property to retrieve.

    Returns:
        dict: The property record if found.
        None: If the property does not exist.
    Raises:
        Exception: If there is an error during the DynamoDB operation.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={"property_id": property_id})
        return response.get("Item")
    except ClientError as e:
        raise Exception(f"Failed to retrieve property: {e.response['Error']['Message']}")
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the property: {str(e)}")


def scan_table(region, table_name, filter_expression=None):
    """
    Scan a DynamoDB table with optional filtering.

    :param region: AWS region where DynamoDB table resides
    :param table_name: Name of the DynamoDB table
    :param filter_expression: (Optional) A filter expression to apply when scanning the table
    :return: List of items from the table, or None if an error occurs
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    try:
        if filter_expression:
            response = table.scan(FilterExpression=filter_expression)
        else:
            response = table.scan()

        items = response.get('Items', []) 
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=filter_expression,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        return items

    except ClientError as e:
        print(f"Error scanning table {table_name}: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"Unexpected error scanning table {table_name}: {str(e)}")
        return None
