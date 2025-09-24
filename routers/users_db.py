# Importación de módulos necesarios para FastAPI y MongoDB
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId  # Para trabajar con ObjectId de MongoDB
from db.models.user import User  # Modelo de datos del usuario
from db.schemas.user import user_schema, users_schema  # Esquemas para serialización
from db.client import db_client  # Cliente de conexión a MongoDB


# Configuración del router con prefijo "/usersdb", etiqueta y respuesta de error por defecto
router = APIRouter(
    prefix="/usersdb",
    tags=["usersdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)


# Función auxiliar para buscar un usuario en la base de datos por campo específico
def search_user(field: str, key):
    # Busca un documento en la colección 'users' usando el campo y valor especificados
    user = db_client.users.find_one({field: key})
    if user:
        # Si encuentra el usuario, lo convierte usando el esquema y retorna una instancia User
        return User(**user_schema(user))
    return None  # Retorna None si no encuentra el usuario


# Endpoint GET para obtener la lista completa de usuarios desde MongoDB
# Ruta: GET /usersdb/
@router.get("/", response_model=list[User])
async def get_users():
    # Obtiene todos los documentos de la colección 'users' y los serializa
    return users_schema(db_client.users.find())


# Endpoint GET para obtener un usuario específico por ID desde MongoDB
# Ruta: GET /usersdb/{id}
@router.get("/{id}", response_model=User)
async def get_user(id: str):
    # Busca el usuario usando el ObjectId de MongoDB
    user = search_user("_id", ObjectId(id))
    if not user:
        # Si no encuentra el usuario, lanza una excepción HTTP 404 (Not Found)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


# Endpoint POST para crear un nuevo usuario en MongoDB
# Ruta: POST /usersdb/
# Retorna código 201 (Created) si es exitoso
@router.post("/", status_code=201, response_model=User)
async def create_user(user: User):
    # Verifica si ya existe un usuario con el mismo email
    if search_user("email", user.email):
        # Si existe, lanza una excepción HTTP 409 (Conflict)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")

    # Convierte el usuario a diccionario y elimina el campo 'id' (MongoDB usa '_id')
    user_dict = dict(user)
    del user_dict["id"]

    # Inserta el nuevo usuario en la base de datos y obtiene el ID generado
    id = db_client.users.insert_one(user_dict).inserted_id
    # Busca el usuario recién creado para retornarlo
    new_user = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)


# Endpoint PUT para actualizar un usuario existente en MongoDB
# Ruta: PUT /usersdb/
# Retorna código 200 (OK) si es exitoso
@router.put("/", status_code=200)
async def update_user(user: User):
    # Convierte el usuario a diccionario y elimina el campo 'id'
    new_user = dict(user)
    new_user.pop("id", None)

    # Valida que el ID esté presente
    if not user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El id es requerido")

    # Verifica que el usuario exista en la base de datos
    if not search_user("_id", ObjectId(user.id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    try:
        # Reemplaza completamente el documento en MongoDB
        result = db_client.users.replace_one({"_id": ObjectId(user.id)}, new_user)

        if result.modified_count == 1:
            return {"message": "Usuario actualizado correctamente"}
        else:
            # Si no se modificó ningún documento, lanza excepción HTTP 304 (Not Modified)
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="El usuario no se actualizó")
    except Exception as e:
        # Manejo de errores durante la actualización
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al actualizar: {str(e)}")


# Endpoint DELETE para eliminar un usuario por ID de MongoDB
# Ruta: DELETE /usersdb/{id}
# Retorna código 200 (OK) si es exitoso
@router.delete("/{id}", status_code=200)
async def delete_user(id: str):
    # Verifica que el usuario exista antes de intentar eliminarlo
    if not search_user("_id", ObjectId(id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    try:
        # Elimina el documento de la colección usando el ObjectId
        db_client.users.delete_one({"_id": ObjectId(id)})
        return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        # Manejo de errores durante la eliminación
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al eliminar: {str(e)}")
