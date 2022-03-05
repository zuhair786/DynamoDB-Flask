from unicodedata import name
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
secret="hdhjabvcgcxfzdghhjjkkllnnvfdertyuiihgfsdfghbvgghaassddfghjkvdx"


print(generate_password_hash("IteMod01"))
#print(check_password_hash("pbkdf2:sha256:260000$oG4VWIzjpaVn4SLf$edbefbc7d62558411c7ff0f6823dd68680048f82f8c48fab70362e865e554ff5","Zuhair"))

token=jwt.encode(
            {'password':'ajbbdbsdhb','exp': time.time() + 600},
            secret, algorithm='HS256')
print(token.decode('ascii'))

#data = jwt.decode("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Ilp1aGFpciIsInBhc3N3b3JkIjoiYWpiYmRic2RoYiIsImV4cCI6MTY0NDg0MTk2Ny4wNjM5MDV9.LcpMKSQezLYofyoEOFWOq8kEnzEhaiKYis20R5XNPaM", "hdhja",algorithms=['HS256'])
#print(data)

from pathlib import Path
p = Path('.')
[print(x) for x in p.iterdir() if x.is_dir()]
print(list(p.glob('**/*.py')))
