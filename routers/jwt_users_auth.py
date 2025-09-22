from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCES_TOKEN_DURATION = 1
SECRET = "402b95dd64ba5d93893fb04e1aa960ee6dbcef84d109897d401a78bf56916ed2"

router = APIRouter(prefix="/jwt_auth", tags=["jwt_auth"], responses={404: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

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
        "password" : "$2a$12$NOAnUHIZpS.x02XXnOE0S.S8SFHGTudMBFGQ7921.dswkSTiHQN7m"
    },
    "kevin1" : {
        "username" : "kevin1",
        "full_name" : "Kevin1 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe1@gmail.com",
        "disabled" : True,
        "password" : "$2a$12$fswJbP6UBVq0sQZsTFewwuRRBhuFiZcTHLQGQsfXybRXUs6lTqovO"
    },
    "kevin2" : {
        "username" : "kevin2",
        "full_name" : "Kevin2 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe2@gmail.com",
        "disabled" : False,
        "password" : "$2a$12$UuECOLdnbupH9O6vPtaCCuwPMpceRuS8B6y1smPkj3q/H8jiXnyNG"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])

def search_user(username: str ):
    if username in users_db:
        return User(**users_db[username])
    

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de autenticacion invalidas", headers={"WWW-Autenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception
    
    return search_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_bd = users_db.get(form.username)
    if not user_bd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no es correcto")
    
    user = search_user_db(form.username)

    crypt.verify(form.password, user.password)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contraseña no es correcto")

    acces_token = {"sub":user.username,
                   "exp": datetime.utcnow() + timedelta(minutes=ACCES_TOKEN_DURATION)}

    return{"acces_token" : jwt.encode(acces_token, SECRET, algorithm=ALGORITHM), "token_type" : "bearer"}



@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user