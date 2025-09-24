# Importación de módulos necesarios para FastAPI
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel

# Configuración del router con prefijo "/users", etiqueta y respuesta de error por defecto
router = APIRouter(prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}})

# Modelo de datos Pydantic para el usuario
class User(BaseModel):
    id: int          # ID único del usuario
    name: str        # Nombre del usuario
    last_name: str   # Apellido del usuario
    age: int         # Edad del usuario
    mail: str        # Correo electrónico del usuario

# Lista en memoria que simula una base de datos de usuarios
users_list = [
    User(id=1, name="Kevin1", last_name="Moreno1", age=201, mail="morenokevinfelipe@gmail.com"),
    User(id=2, name="Kevin2", last_name="Moreno2", age=202, mail=""),
    User(id=3, name="Kevin3", last_name="Moreno3", age=203, mail=""),
    User(id=4, name="Kevin4", last_name="Moreno4", age=204, mail="")    
]

# Función auxiliar para buscar un usuario por ID
def find(param):
    # Filtra la lista de usuarios para encontrar uno con el ID especificado
    user = list(filter(lambda us: us.id == param, users_list))  
    try:
        return user  # Retorna la lista de usuarios encontrados (puede estar vacía)
    except:
        return{"error": "No se ha encontrado el usuario"}
    


# Endpoint GET para obtener la lista completa de usuarios
# Ruta: GET /users/
@router.get("/")
async def usesrs_list():
    return users_list

# Endpoint GET con query parameter opcional para buscar usuario por ID
# Ruta: GET /users/?id=1
@router.get("/") #query opcional o condicional
async def user_by_id(id:int):
    us=find(id)
    return us

# Endpoint GET con path parameter obligatorio para buscar usuario por ID
# Ruta: GET /users/1
@router.get("/{id}") #path obligatorio
async def user_by_id(id:int):
    us=find(id)
    return us


# Endpoint POST para crear un nuevo usuario
# Ruta: POST /users/
# Retorna código 201 (Created) si es exitoso
@router.post("/", status_code=201)
async def user(user: User):
    # Verifica si el usuario ya existe basándose en el ID
    if (find(user.id)): 
        # Si existe, lanza una excepción HTTP 304 (Not Modified)
        raise HTTPException(status_code=304,detail="El Usuario ya existe")       
    else:
        # Si no existe, agrega el usuario a la lista y retorna la lista actualizada
        users_list.append(user)
        return users_list       
    
    
# Endpoint PUT para actualizar un usuario existente
# Ruta: PUT /users/
# Retorna código 200 (OK) si es exitoso
@router.put("/", status_code=200)
async def user(user: User):
    # Verifica si el usuario existe basándose en el ID
    if find(user.id):
        # Si existe, busca y reemplaza el usuario en la lista
        for index, user_saved in enumerate(users_list):
            # Reemplaza el usuario si el ID coincide, de lo contrario mantiene el original
            users_list[index] = user if user_saved.id == user.id else user_saved
        return users_list
    else:
        # Si no existe, lanza una excepción HTTP 404 (Not Found)
        raise HTTPException(status_code=404, detail="Usuario no existe")


# Endpoint DELETE para eliminar un usuario por ID
# Ruta: DELETE /users/{id}
# Retorna código 200 (OK) si es exitoso
@router.delete("/{id}", status_code=200)
async def user(id: int):
    # Verifica si el usuario existe basándose en el ID
    if find(id):
        # Si existe, busca y elimina el usuario de la lista
        for index, user_saved in enumerate(users_list):
            if user_saved.id == id:
                # Elimina el usuario de la lista cuando encuentra el ID coincidente
                users_list.pop(index)
                break  # Sale del bucle una vez encontrado y eliminado
        return users_list
    else:
        # Si no existe, lanza una excepción HTTP 404 (Not Found)
        raise HTTPException(status_code=404, detail="Usuario no existe")