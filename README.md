# DynamoDB-Flask
Using flask-REST Api,doing dynamodb functions by getting required parameters through body and params.

# PreRequisite
1. Python (https://www.python.org/downloads/)
2. Docker (For windows: https://hub.docker.com/editions/community/docker-ce-desktop-windows)
3. PostMan (https://www.postman.com/downloads/)

# Steps

1. install required packages from "requirements.txt".Open Cmd,goto main folder and type "pip install requirements.txt"
2. Start the Docker engine
3. Open Cmd, and run "docker run -itd -p 8000:8000  --name dev-db amazon/dynamodb-local:latest -jar DynamoDBLocal.jar -sharedDb"
4. Run __init__.py 
5. Open Postman and try out various functions(provided sample test case body) of dynamodb.
