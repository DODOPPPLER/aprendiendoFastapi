from fastapi import APIRouter,HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}})


class User(BaseModel):
    id: int
    name: str
    last_name: str
    age: int
    mail: str

users_list = [
    User(id=1, name="Kevin1", last_name="Moreno1", age=201, mail="morenokevinfelipe@gmail.com"),
    User(id=2, name="Kevin2", last_name="Moreno2", age=202, mail=""),
    User(id=3, name="Kevin3", last_name="Moreno3", age=203, mail="")
]

@router.get("/")
async def usesrs_list():
    return users_list

