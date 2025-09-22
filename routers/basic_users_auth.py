from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/bsc_auth", tags=["bsc_auth"], responses={404: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str


users_db = {
    "kevin" : {
        "username" : "kevin",
        "full_name" : "Kevin Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe@gmail.com",
        "disabled" : False,
        "password" : "1234"
    },
    "kevin1" : {
        "username" : "kevin1",
        "full_name" : "Kevin1 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe1@gmail.com",
        "disabled" : True,
        "password" : "123456"
    },
    "kevin2" : {
        "username" : "kevin2",
        "full_name" : "Kevin2 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe2@gmail.com",
        "disabled" : False,
        "password" : "1234"
    }
}


def seach_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de autenticacion invalidas", headers={"WWW-Autenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    

    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_bd = users_db.get(form.username)
    if not user_bd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no es correcto")
    
    user = seach_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contraseña no es correcto")
    
    return{"acces_token" : user.username, "token_type" : "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user