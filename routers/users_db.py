# --- Importaciones ---
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.client import db_client


# --- Inicialización del router ---
router = APIRouter(
    prefix="/usersdb",
    tags=["usersdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)


# --- Funciones auxiliares ---
def search_user(field: str, key):
    user = db_client.users.find_one({field: key})
    if user:
        return User(**user_schema(user))
    return None


# --- Endpoints CRUD ---

# GET - obtener todos los usuarios
@router.get("/", response_model=list[User])
async def get_users():
    return users_schema(db_client.users.find())


# GET - obtener un usuario por id
@router.get("/{id}", response_model=User)
async def get_user(id: str):
    user = search_user("_id", ObjectId(id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


# POST - crear un nuevo usuario
@router.post("/", status_code=201, response_model=User)
async def create_user(user: User):
    if search_user("email", user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")

    user_dict = dict(user)
    del user_dict["id"]

    id = db_client.users.insert_one(user_dict).inserted_id
    new_user = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)


# PUT - actualizar un usuario existente
@router.put("/", status_code=200)
async def update_user(user: User):

    new_user = dict(user)
    new_user.pop("id", None)

    if not user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El id es requerido")

    if not search_user("_id", ObjectId(user.id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    try:
        result = db_client.users.replace_one({"_id": ObjectId(user.id)}, new_user)

        if result.modified_count == 1:
            return {"message": "Usuario actualizado correctamente"}
        else:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="El usuario no se actualizó")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al actualizar: {str(e)}")


# DELETE - eliminar un usuario por id
@router.delete("/{id}", status_code=200)
async def delete_user(id: str):
    if not search_user("_id", ObjectId(id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    try:
        db_client.users.delete_one({"_id": ObjectId(id)})
        return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al eliminar: {str(e)}")
