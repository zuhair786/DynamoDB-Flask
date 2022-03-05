from flask import jsonify, request
from helper import *
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json
import math
import jwt
from botocore.exceptions import ClientError
from werkzeug.security import check_password_hash
from functools import wraps

def role_acceptance(*userrole):
    def token_required(f):
        @wraps(f)
        def decorated(*args,**kwargs):
            if 'Authorization' in request.headers:
                token=request.headers['Authorization']
                try:
                    data=jwt.decode(token,Secret_Key,algorithm='HS256')
                    if data['username'] not in userrole:
                        return jsonify({'message':'Your are restrict to access this site'}),401
                except:
                    return jsonify({'message':'Token is invalid!'}),401
            else:
                return jsonify({'message':'Token is missing'}),404
            return f(*args,**kwargs)
        return decorated
    return token_required

def signin(dynamodb,username,password):
    if check_user_exist(dynamodb,username):   
        password_hash=get_password(dynamodb,username)
        if check_password_hash(password_hash,password):
            token=generate_auth_token(username)
            return {'username':username,'token':token.decode('utf-8'),'Message':"Please attach token in your request header with Key Name as 'Authentication'"}, 200
        else:
            return "Invalid Password",401
    else:
        return "Invalid Username",401

def addTODB(dynamodb,username,password_hash):
    table=dynamodb.Table("Identity")
    try:
        table.put_item(Item={'username':username,'password':password_hash})
        print("Added")
        return generate_auth_token(username),"Please attach token in your request header with Key Name as 'Authentication'"
    except:
        return None,"Error in authenticating your credentials"
  
def check_exist(client,name):
    response=client.list_tables()
    if name not in response['TableNames']:
        return False
    else:
        return True

def create_table1(dynamodb,tablename,hashname,hashtype,sortname,sorttype,readcapacity,writecapacity):
    readcapacity=int(readcapacity)
    writecapacity=int(writecapacity)
    hashtype=str.upper(hashtype)
    sorttype=str.upper(sorttype)
    table = dynamodb.create_table(
        TableName=tablename,
        KeySchema=[
            {
                'AttributeName': hashname,
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': sortname,
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': hashname,
                'AttributeType': hashtype
            },
            {
                'AttributeName': sortname,
                'AttributeType': sorttype
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': readcapacity,
            'WriteCapacityUnits': writecapacity
        }
    )
    return table

def create_table2(dynamodb,tablename,hashname,hashtype,readcapacity,writecapacity):
    readcapacity=int(readcapacity)
    writecapacity=int(writecapacity)
    hashtype=str.upper(hashtype)
    table = dynamodb.create_table(
        TableName=tablename,
        KeySchema=[
            {
                'AttributeName': hashname,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': hashname,
                'AttributeType': hashtype
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': readcapacity,
            'WriteCapacityUnits': writecapacity
        }
    )
    return table


def load_table(dynamodb,tablename,files):
    table = dynamodb.Table(tablename)
    try:
        for single_file in files:
            single_file=json.dumps(single_file)
            single_file=json.loads(single_file,parse_float=Decimal)
            #print(single_file)
            table.put_item(Item=single_file)
        return True
    except Exception:
        return False

def delete_table(dynamodb,name):
    table = dynamodb.Table(name)
    table.delete()

def view_table_specific(dynamodb,name,key,value,projection,page):
        queryCount=1
        result=list()
        length=list()
        print(page)
        #print(projection,' ',type(projection))
        table=dynamodb.Table(name)
        totalresp=table.query(KeyConditionExpression=Key(key).eq(value))
        totalresp=totalresp['Items']
        lenDatas=math.ceil(len(totalresp)/5)
        length.append(lenDatas)
        single_data=totalresp[0]
        main_values,dist_values,dist_names=clean_projection(projection,single_data)
        resp=table.query(KeyConditionExpression=Key(key).eq(value),ProjectionExpression=projection,Limit=5)
        #print(resp)
        datas=resp['Items']
        for data in datas:
            #For efficiency, use list and join
            string=list() #list
            for ele in main_values:
                string.append(data[ele])
            for i in range(0,len(dist_values),2):
                string.append(str(data[dist_values[i]].get(dist_values[i+1])))
            for ele in dist_names:
                string.append(data[ele])
            ' '.join(string) #join
            result.append(str(queryCount)+"-"+string)        
        if page is None:
            return result,length
        else:
            while page>queryCount:
                if 'LastEvaluatedKey' in resp:
                    endkey=resp['LastEvaluatedKey']
                    resp=table.query(KeyConditionExpression=Key(key).eq(value),ProjectionExpression=projection,Limit=5,ExclusiveStartKey=endkey)
                    queryCount+=1
                else:
                    break
            datas=resp['Items']
            result.clear()
            for data in datas:
                string=""
                for ele in main_values:
                    string+=data[ele]+" "
                for i in range(0,len(dist_values),2):
                    string+=str(data[dist_values[i]].get(dist_values[i+1]))
                result.append(str(queryCount)+"-"+string)  
            return result,length

def view_table_full1(dynamodb,tablename):
    table=dynamodb.Table(tablename)
    result=list()
    scan_args=dict()
    done=False
    start_key=False
    while not done:
        if start_key:
            scan_args['ExclusiveStartKey']=start_key
        resp=table.scan(**scan_args)
        datas=resp['Items']
        for data in datas:
            result.append(data)
        start_key = resp.get('LastEvaluatedKey', None)
        if start_key is None:
            done=True
    return result

def view_table_full2(dynamodb,tablename,projection):
    table=dynamodb.Table(tablename)
    result=list()
    totalresp=table.scan(Limit=1)
    totalresp=totalresp['Items']
    main_values,dist_values,dist_names=clean_projection(projection,totalresp[0])   
    scan_args={
        'ProjectionExpression':projection
    }
    done=False
    start_key=False
    while not done:
        if start_key:
            scan_args['ExclusiveStartKey']=start_key
        resp=table.scan(**scan_args)
        datas=resp['Items']
        for data in datas:
            string=""
            for ele in main_values:
                string+=data[ele]+" "
            for i in range(0,len(dist_values),2):
                string+=str(data[dist_values[i]].get(dist_values[i+1]))
            for ele in dist_names:
                for props in data[ele]:
                    string+=str(data[ele].get(props))+" "
            result.append(string)
        start_key = resp.get('LastEvaluatedKey', None)
        if start_key is None:
            done=True
    return result

def update_item(dynamodb,tablename,hashname,hashvalue,updatename,updatevalue,sortname=None,sortvalue=None):
    table=dynamodb.Table(tablename)
    updateexpression='set '
    attributevalues={}
    for i in range(0,len(updatename)):
            naming1=updatename[i].replace(".","")
            updateexpression+=updatename[i]+' = :'+naming1+','
            attributevalues[':'+naming1]=updatevalue[i]
    updateexpression=updateexpression[:len(updateexpression)-1]
    print(updateexpression) 
    #print(attributenames)
    #print(attributevalues)
    if sortname is None:
        key_args={
            hashname: hashvalue
        }
    else:
        key_args={
            hashname: hashvalue,
            sortname: sortvalue
        }
    try:
        response = table.update_item(
            Key=key_args,
            UpdateExpression=updateexpression,
            ExpressionAttributeValues=attributevalues,
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
            print(e.response['Error']['Message'])
            return False
    else:
        return True

def delete_item(dynamodb,tablename,hashname,hashvalue,sortname=None,sortvalue=None):
    table=dynamodb.Table(tablename)
    if sortname is None:
        key_args={
            hashname: hashvalue
        }
    else:
        key_args={
            hashname: hashvalue,
            sortname: sortvalue
        }
    try:
        response = table.delete_item(
            Key=key_args,
        )
    except ClientError as e:
            print(e.response['Error']['Message'])
            return False,e.response['Error']['Message']
    else:
        return True,None

def filter_details1(dynamodb,tablename,queriesname,queriesvalues,client):
    table=dynamodb.Table(tablename)
    result=list()
    totalresp=table.scan(Limit=1)
    totalresp=totalresp['Items']
    keyexpression,filterexpression,attributenames,attributevalues=filter_details_helper_query(tablename,queriesname,queriesvalues,totalresp[0],client)
    keyexpression=keyexpression[:len(keyexpression)-4]
    filterexpression=filterexpression[:len(filterexpression)-4]
    print(keyexpression)
    print(attributenames)
    print(filterexpression)
    print(attributevalues)
    if (not filterexpression):
        resp=table.query(KeyConditionExpression=keyexpression,ExpressionAttributeNames=attributenames,ExpressionAttributeValues=attributevalues,Limit=10)
    else:
        resp=table.query(KeyConditionExpression=keyexpression,FilterExpression=filterexpression,ExpressionAttributeNames=attributenames,ExpressionAttributeValues=attributevalues,Limit=10)
    datas=resp['Items']
    for data in datas:
        result.append(data)
    return result

def filter_details2(dynamodb,tablename,queriesnames,queriesvalues,client):
    table=dynamodb.Table(tablename)
    result=list()
    totalresp=table.scan(Limit=1)
    totalresp=totalresp['Items']
    filterexpression,attributevalues=filter_details_helper_scan(queriesnames,queriesvalues,totalresp[0])
    filterexpression=filterexpression[:len(filterexpression)-4]
    print(filterexpression)
    scan_args={
            'FilterExpression':filterexpression,
            'ExpressionAttributeValues':attributevalues
        }
    done=False
    start_key=False
    while not done:
        if start_key:
            scan_args['ExclusiveStartKey']=start_key
        resp=table.scan(**scan_args)
        datas=resp['Items']
        for data in datas:           
            result.append(data)
        start_key = resp.get('LastEvaluatedKey', None)
        if start_key is None:
            done=True
    return result






     