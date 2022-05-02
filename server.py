#Fast API server
import base64
import hashlib
import hmac
import hashlib
import json
from typing import Optional

from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response

app = FastAPI()

SECRET_KEY = "4605b0a6c625a8c49b148f4b0728139f60018ef830f31aa341fc4ddfa504a9e0"

PASSWORD_SALT = "468d479828908528d4bccb4c10ab38e54ddf5bfd4257caf846e0be1af1ad5f78"

def sign_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def get_login_from_signed_string(login_signed) -> Optional[str]:
    login_base64, sign = login_signed.split(".")
    print("login_base64", login_base64, sign)
    print(login_base64.encode())
    login = base64.b64decode(login_base64.encode()).decode()
    valid_sign = sign_data(login)
    if hmac.compare_digest(valid_sign, sign):
        return login

def verify_password(login: str, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() )\
        .hexdigest().lower()
    stored_password_hash = users[login]["password"].lower()
    return password_hash == stored_password_hash 


users = {
    'alexey@com': {
        "name": "Alexey",
        "password": "24f22f3c244e19a2d4d4bef22fe59b6f2d38f84355693da4a13d4f3c9919ca58",
        "balance": 100
    },
    "petr@com": {
        "name": "Petr",
        "password": "a9e40bb7f7d91e462618d69ae8376afb56258f51bf19a22559a5766ad3315fc6",
        "balance": 200
    }
}

@app.get("/")
def index_page(login: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not login:
        return Response(login_page, media_type="text/html")
       
    valid_login = get_login_from_signed_string(login)
    
    if not valid_login:
        response = Response(login_page,  media_type="text/html")
        response.delete_cookie(key="login")
        return response

    try:
        user = users[valid_login]
    except KeyError:
        response = Response(login_page,  media_type="text/html")
        response.delete_cookie(key="login")
        return response 
    return Response(
        f"hell, {users[valid_login]['name']}! <br>"
        f"balance: {users[valid_login]['balance']}"
        , media_type="text/html")
    

@app.post("/login")
def process_login_page(data: dict = Body(...)):
    print('data is', data)
    login = data["login"]
    password = data["password"]
    user = users.get(login)
    print('user is', user)
    print('password is', password)
    if not user or not verify_password(login, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "no exist login or password"
            }),
            media_type="application/json")

    response = Response(
        json.dumps({
            "success": True,
            "message": f"User: {user['name']} <br> Balance: {user['balance']}"
        }), media_type="application/json")

    
    login_signed = base64.b64encode(login.encode()).decode() + "." + sign_data(login)
    
    response.set_cookie(key="login", value = login_signed)
    return response

