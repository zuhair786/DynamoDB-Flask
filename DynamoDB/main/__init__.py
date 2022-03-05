from flask import Flask,render_template,request,abort,jsonify
import boto3
from core import *
from werkzeug.security import generate_password_hash, check_password_hash


dynamodb=boto3.resource("dynamodb",endpoint_url="http://localhost:8000",region_name='us-west-2',aws_access_key_id="fakeid",aws_secret_access_key="fakekey")
client=boto3.client('dynamodb',endpoint_url='http://localhost:8000',region_name='us-west-2',aws_access_key_id='fakeid',aws_secret_access_key='fakekey')

app=Flask(__name__)
@app.route('/dynamo/signin', methods=['POST'])
def check_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) 
    data,status=signin(dynamodb,username,password)
    return (jsonify(data),status)
    
@app.route("/dynamo/<string:tablename>",methods=['POST','DELETE'])
@role_acceptance('CreDel01')
def create_table(tablename):
    if request.method=='POST':
        form=request.get_json()
        if not check_exist(client,tablename):
            hashname=form['HashName']
            hashtype=form['HashType']
            readcapacity=form['readcapacity']
            writecapacity=form['writecapacity']
            if form['SortName']==None:
                print("No Sort Key")
                table=create_table2(dynamodb,tablename,hashname,hashtype,readcapacity,writecapacity)
            else:
                sortname=form['SortName']
                sorttype=form['SortType']
                table=create_table1(dynamodb,tablename,hashname,hashtype,sortname,sorttype,readcapacity,writecapacity)
            return 'Table Created Successfully'
        else:
            return 'Table with name %s already existed!' % tablename
    elif request.method=='DELETE':
        delete_table(dynamodb,tablename)
        #Efficient Python code writing
        return 'Table %s deleted Successfully' %  tablename  #Always use this,instead of +   

@app.route('/dynamo/<string:name>/modify',methods=['PUT','POST','DELETE'])
@role_acceptance('IteMod01')
def modify_items(name):
    if request.method=='PUT':
        form=request.json
        #print(form[0])
        response=load_table(dynamodb,name,form)
        if response:
            return 'Values added to %s successfully' %name
        else:
            return 'Error Please check JSON'
    elif request.method=='POST':
        form=request.get_json()
        hashname=form['hashname']
        hashvalue=form['hashvalue']
        updatename=form['updatename']
        updatevalue=form['updatevalue']
        if form['sortname'] is None:
            if update_item(dynamodb,name,hashname,hashvalue,updatename,updatevalue):
                return 'Values Updated Successfully'
            else:
                return 'Error,please check JSON values'
        else:
            if update_item(dynamodb,name,hashname,hashvalue,updatename,updatevalue,form['sortname'],form['sortvalue']):
                return 'Values Updated Successfully'
            else:
                return 'Error,please check JSON values'
    elif request.method=='DELETE':
        hashname=request.args.get('hashname')
        hashvalue=request.args.get('hashvalue')
        if request.args.get('sortname'):
            flag,msg=delete_item(dynamodb,name,hashname,hashvalue,request.args.get('sortname'),request.args.get('sortvalue'))
            if flag:
                return 'Item with '+hashname+' as '+hashvalue+' and '+request.args.get('sortname')+' as '+request.args.get('sortvalue')+' was deleted successfully'
            else:
                return msg
        else:
            flag,msg=delete_item(dynamodb,name,hashname,hashvalue)
            if flag:
                return 'Item with '+hashname+' as '+hashvalue+' was deleted successfully'
            else:
                return msg

@app.route('/dynamo/view/<string:name>',methods=['GET','POST'])
def pagination(name):
    tablename=name
    if request.method=='POST':
        form=request.get_json()
        hashname=form['Hashname']
        hashvalue=form['Hashvalue']
        projection=form['projection']
        page=form['page']
        result,length=view_table_specific(dynamodb,tablename,hashname,hashvalue,projection,page)
        return render_template('specificView.html',result=result,length=length,name=name,hashvalue=hashvalue) 
    elif request.method=='GET':
        if request.args.get('projection'):
            projection=request.args.get('projection')
            result=view_table_full2(dynamodb,tablename,projection)
            return render_template('fullView.html',result=result)
        else:
            result=view_table_full1(dynamodb,tablename)
            return render_template('fullView.html',result=result)

@app.route('/dynamo/filter_query/<string:name>',methods=['POST'])
def call_filter_details1(name):
    form=request.get_json()
    queriesname=form['filtername']
    queriesvalues=form['filtervalues']
    result=filter_details1(dynamodb,name,queriesname,queriesvalues,client)
    if len(result) !=0:
        return render_template('fullView.html',result=result)
    else:
        return render_template('empty.html',result=result)

@app.route('/dynamo/filter/<string:name>',methods=['POST'])
def call_filter_details2(name):
    form=request.get_json()
    queriesname=form['filtername']
    queriesvalues=form['filtervalues']
    result=filter_details2(dynamodb,name,queriesname,queriesvalues,client)
    if len(result) !=0:
        return render_template('fullView.html',result=result)
    else:
        return render_template('error.html',result=result)
if __name__=='__main__':
    app.run(debug=True)


