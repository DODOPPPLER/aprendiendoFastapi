# Importación de módulos necesarios para autenticación básica con FastAPI
from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Para OAuth2 y formularios de login

# Configuración del router con prefijo "/bsc_auth", etiqueta y respuesta de error por defecto
router = APIRouter(prefix="/bsc_auth", tags=["bsc_auth"], responses={404: {"message": "No encontrado"}})

# Esquema OAuth2 que especifica la URL del endpoint de login (autenticación básica sin JWT)
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Modelo de datos Pydantic para el usuario (sin contraseña, para respuestas públicas)
class User(BaseModel):
    username: str    # Nombre de usuario único
    full_name: str   # Nombre completo del usuario
    email: str       # Correo electrónico del usuario
    disabled: bool   # Estado de habilitación del usuario

# Modelo de datos Pydantic para el usuario en base de datos (incluye contraseña en texto plano)
class UserDB(User):
    password: str    # Contraseña en texto plano (NO recomendado para producción)


# Base de datos en memoria que simula usuarios con contraseñas en texto plano
# NOTA: Este es un ejemplo educativo - en producción NUNCA usar contraseñas en texto plano
users_db = {
    "kevin" : {
        "username" : "kevin",
        "full_name" : "Kevin Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe@gmail.com",
        "disabled" : False,  # Usuario activo
        "password" : "1234"  # Contraseña en texto plano (INSEGURO)
    },
    "kevin1" : {
        "username" : "kevin1",
        "full_name" : "Kevin1 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe1@gmail.com",
        "disabled" : True,   # Usuario deshabilitado
        "password" : "123456"  # Contraseña en texto plano
    },
    "kevin2" : {
        "username" : "kevin2",
        "full_name" : "Kevin2 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe2@gmail.com",
        "disabled" : False,  # Usuario activo
        "password" : "1234"  # Contraseña en texto plano
    }
}


# Función para buscar un usuario en la base de datos incluyendo la contraseña
def seach_user_db(username: str):
    if username in users_db:
        # Retorna una instancia UserDB con todos los datos incluyendo la contraseña
        return UserDB(**users_db[username])


# Función para buscar un usuario en la base de datos sin incluir la contraseña
def search_user(username: str):
    if username in users_db:
        # Retorna una instancia User sin la contraseña (para respuestas públicas)
        return User(**users_db[username])

# Función dependencia para obtener el usuario actual usando autenticación básica
# NOTA: En autenticación básica, el "token" es directamente el username (INSEGURO)
async def current_user(token: str = Depends(oauth2)):
    # Busca el usuario usando el token (que en este caso es el username)
    user = search_user(token)
    if not user:
        # Si no encuentra el usuario, lanza excepción HTTP 401 (Unauthorized)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autenticacion invalidas", 
            headers={"WWW-Autenticate": "Bearer"})
    
    # Verifica si el usuario está deshabilitado
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo")
    
    return user  # Retorna el usuario si está activo y autenticado


# Endpoint POST para login con autenticación básica (sin JWT)
# Ruta: POST /bsc_auth/login
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Busca el usuario en la base de datos por username
    user_bd = users_db.get(form.username)
    if not user_bd:
        # Si el usuario no existe, lanza excepción HTTP 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no es correcto")
    
    # Obtiene los datos completos del usuario incluyendo la contraseña
    user = seach_user_db(form.username)
    # Compara directamente las contraseñas en texto plano (INSEGURO)
    if not form.password == user.password:
        # Si la contraseña no coincide, lanza excepción HTTP 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contraseña no es correcto")
    
    # Retorna el username como "token" (sistema básico e inseguro)
    # NOTA: En autenticación básica, no hay token real, se usa el username
    return{"acces_token" : user.username, "token_type" : "bearer"}

# Endpoint GET protegido para obtener información del usuario autenticado
# Ruta: GET /bsc_auth/users/me
# Requiere "token" (username) en el header Authorization
@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    # Retorna la información del usuario autenticado (sin contraseña)
    return user