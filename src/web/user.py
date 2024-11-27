from datetime import timedelta
import os
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
from errors import Missing, Duplicate

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as service
else:
    from service import user as service


router = APIRouter(prefix="/user", tags=["auth_user"])


def unauthed():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all() -> list[User]:
    return service.get_all()


@router.get("/{name}")
def get_one(
    name: str, current_user: User = Depends(service.get_current_user)
) -> User | dict[str, str] | None:
    if not current_user:
        unauthed()
    try:
        if current_user.name == "admin":
            return service.get_one(name)
        return {"message": "You are not admin to access this resource"}
    except Missing as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.msg)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(user: User) -> User | None:
    try:
        return service.create(user)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.msg)


@router.patch("/{name}")
def modify(
    name: str, user: User, current_user: User = Depends(service.get_current_user)
) -> User | dict[str, str] | None:
    if not current_user:
        unauthed()
    try:
        if current_user.name == "admin":
            return service.modify(name, user)
        return {"message": "You are not admin to access this resource"}
    except Missing as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.msg)


@router.delete("/{name}", status_code=status.HTTP_200_OK)
def delete(name: str, current_user=Depends(service.get_current_user)) -> bool | None:
    if not current_user:
        unauthed()
    try:
        return service.delete(name)
    except Missing as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.msg)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None
) -> dict:
    # Аутентификация пользователя(User Authentication)
    user = service.auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генерация токена(Token generation)
    access_token_expires = timedelta(minutes=5)
    access_token = service.create_access_token(
        data={"sub": user.name}, expires=access_token_expires
    )

    # Сохранение токена в куки(Saving the token to a cookie)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"msg": "Logged out successfully"}


@router.get("/get/me", status_code=status.HTTP_200_OK)
def read_current_user(current_user: User = Depends(service.get_current_user)):
    if not current_user:
        unauthed()
    return {"username": current_user.name, "password": current_user.hash}
