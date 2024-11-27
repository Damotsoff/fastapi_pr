from datetime import datetime, timedelta
from models.user import User
import os
from jose import jwt
from data import user as data
from fastapi import Depends, Request

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as data
else:
    from data import user as data

from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def veryfy_password(plain, hash):
    hashed = get_hash(hash)
    return pwd_context.verify(plain, hashed)


def get_hash(plain):
    return pwd_context.hash(plain)


def get_jwt_username(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not (username := payload.get("sub")):
            print("Token is valid, but no 'sub' field found.")
            return None
        expire = payload.get("exp")
        if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
            print("Token has expired.")
            return None
    except jwt.JWTError as e:
        print(f"JWT decoding error: {e}")
        return None
    print(f"Token is valid. Username: {username}")
    return username


def get_token(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        print("No token found in cookies.")
    return token



def get_current_user(access_token: str = Depends(get_token)) -> User | None:
    if not access_token:
        print("No token found in cookies.")
        return None
    if not (username := get_jwt_username(access_token)):
        print("Invalid token or no username found in the token.")
        return None
    if user := lookup_user(username):
        return user
    return None


def lookup_user(username: str) -> User | None:
    user = data.get_one(username)
    if not user:
        print(f"User '{username}' not found in the database.")
    return user


def auth_user(name: str, plain: str) -> User | None:
    if not (user := lookup_user(name)):
        return None
    if not veryfy_password(plain, user.hash):
        return None
    return user


def create_access_token(data: dict, expires: timedelta | None = None):
    src = data.copy()
    now = datetime.utcnow()
    if not expires:
        expires = timedelta(minutes=1)
    src.update({"exp": now + expires})
    encoded_jwt = jwt.encode(src, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_all() -> list[User]:
    return data.get_all()


def get_one(name) -> User | None:
    return data.get_one(name)


def create(user: User) -> User | None:
    return data.create(user)


def modify(name: str, user: User) -> User:
    return data.modify(name, user)


def delete(name: str) -> bool | None:
    return data.delete(name)
