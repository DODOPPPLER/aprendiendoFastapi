from fastapi import APIRouter, HTTPException
from routers.users import users_list,User

router = APIRouter(prefix="/user", tags=["user"], responses={404: {"message": "No encontrado"}})

def find(param):
    user = list(filter(lambda us: us.id == param, users_list))  
    try:
        return user
    except:
        return{"error": "No se ha encontrado el usuario"}
    
@router.get("/{id}") #path obligatorio
async def user_by_id(id:int):
    us=find(id)
    return us

@router.get("/") #query opcional o condicional
async def user_by_id(id:int):
    us=find(id)
    return us


@router.post("/", status_code=201)
async def user(user: User):
    if (find(user.id)): 
        raise HTTPException(status_code=304,detail="El Usuario ya existe")       
    else:
        users_list.append(user)
        return users_list       
    
@router.put("/", status_code=200)
async def user(user: User):
    if find(user.id):
        for index, user_saved in enumerate(users_list):
            users_list[index] = user if user_saved.id == user.id else user_saved
        return users_list
    else:
        raise HTTPException(status_code=404, detail="Usuario no existe")

@router.delete("/{id}", status_code=200)
async def user(id: int):
    if find(id):
        for index, user_saved in enumerate(users_list):
            if user_saved.id == id:
                users_list.pop(index)
                break
        return users_list
    else:
        raise HTTPException(status_code=404, detail="Usuario no existe")