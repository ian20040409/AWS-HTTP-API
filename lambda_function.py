import json
import boto3
from decimal import Decimal

# 初始化 DynamoDB 資源與表
dynamodb = boto3.resource("dynamodb")
table_name = 'http-crud-tutorial-items'
table = dynamodb.Table(table_name)


def delete_item(item_id):
    try:
        table.delete_item(Key={'id': item_id})
        return {"message": f"Deleted item {item_id}"}
    except Exception as e:
        print(f"Error deleting item {item_id}: {str(e)}")
        raise


def get_item(item_id):
    try:
        response = table.get_item(Key={'id': item_id})
        if 'Item' not in response:
            return {"error": f"Item with id {item_id} not found"}, 404
        item = response['Item']
        return {'id': item['id'], 'name': item['name'], 'price': float(item['price'])}
    except Exception as e:
        print(f"Error retrieving item {item_id}: {str(e)}")
        raise


def get_all_items():
    try:
        response = table.scan()
        items = response.get('Items', [])
        return [{'id': item['id'], 'name': item['name'], 'price': float(item['price'])} for item in items]
    except Exception as e:
        print(f"Error scanning items: {str(e)}")
        raise


def put_item(request_json):
    try:
        table.put_item(
            Item={
                'id': request_json['id'],
                'name': request_json['name'],
                'price': Decimal(str(request_json['price']))
            }
        )
        return {"message": f"Put item {request_json['id']}"}
    except Exception as e:
        print(f"Error putting item: {str(e)}")
        raise


def lambda_handler(event, context):
    print("Event: ", event)
    status_code = 200
    body = {}

    try:
        route_key = event.get('routeKey')
        if route_key == "DELETE /items/{id}":
            item_id = event['pathParameters']['id']
            body = delete_item(item_id)
        elif route_key == "GET /items/{id}":
            item_id = event['pathParameters']['id']
            body = get_item(item_id)
        elif route_key == "GET /items":
            body = get_all_items()
        elif route_key == "PUT /items":
            request_json = json.loads(event['body'])
            body = put_item(request_json)
        else:
            status_code = 400
            body = {"error": f"Unsupported route: {route_key}"}
    except KeyError as ke:
        print(f"KeyError: {str(ke)}")
        status_code = 400
        body = {"error": f"Missing required key: {str(ke)}"}
    except Exception as e:
        print(f"Exception: {str(e)}")
        status_code = 500
        body = {"error": "An error occurred", "details": str(e)}

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
