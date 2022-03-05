import boto3
dynamodb=boto3.resource("dynamodb",endpoint_url="http://localhost:8000",region_name='us-west-2',aws_access_key_id="fakeid",aws_secret_access_key="fakekey")

table = dynamodb.create_table(
        TableName="Identity",
        KeySchema=[
            {
                'AttributeName': "username",
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': "password",
                'KeyType': 'RANGE'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': "username",
                'AttributeType': "S"
            },
            {
                'AttributeName': "password",
                'AttributeType': "S"
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

table=dynamodb.Table('Identity')
table.put_item(Item={'username':"CreDel01",'password':"pbkdf2:sha256:260000$BuHgA28kuh1znoHZ$051f472c3aa780f9a04ab971f763373f242f05e376d5a8aff4ffdf576b94605a"})
table.put_item(Item={'username':"IteMod01",'password':"pbkdf2:sha256:260000$R8x83FtGsVe5KvIF$696a08e55a7ce7b959f486f60e5400e898b4157ab24e34f282825543ae94f4e2"})
print("Added")