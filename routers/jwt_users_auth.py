# Importación de módulos necesarios para autenticación JWT con FastAPI
from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Para OAuth2 y formularios de login
from jose import jwt, JWTError  # Para manejo de tokens JWT
from passlib.context import CryptContext  # Para encriptación de contraseñas
from datetime import datetime, timedelta  # Para manejo de fechas y expiración de tokens

# Configuración de constantes para JWT
ALGORITHM = "HS256"  # Algoritmo de encriptación para JWT
ACCES_TOKEN_DURATION = 1  # Duración del token en minutos
SECRET = "402b95dd64ba5d93893fb04e1aa960ee6dbcef84d109897d401a78bf56916ed2"  # Clave secreta para firmar JWT

# Configuración del router con prefijo "/jwt_auth", etiqueta y respuesta de error por defecto
router = APIRouter(prefix="/jwt_auth", tags=["jwt_auth"], responses={404: {"message": "No encontrado"}})

# Esquema OAuth2 que especifica la URL del endpoint de login para obtener tokens
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Contexto de encriptación para manejar contraseñas con bcrypt
crypt = CryptContext(schemes=["bcrypt"])

# Modelo de datos Pydantic para el usuario (sin contraseña, para respuestas públicas)
class User(BaseModel):
    username: str    # Nombre de usuario único
    full_name: str   # Nombre completo del usuario
    email: str       # Correo electrónico del usuario
    disabled: bool   # Estado de habilitación del usuario

# Modelo de datos Pydantic para el usuario en base de datos (incluye contraseña encriptada)
class UserDB(User):
    password: str    # Contraseña encriptada del usuario


# Base de datos en memoria que simula usuarios con contraseñas encriptadas
users_db = {
    "kevin" : {
        "username" : "kevin",
        "full_name" : "Kevin Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe@gmail.com",
        "disabled" : False,  # Usuario activo
        "password" : "$2a$12$NOAnUHIZpS.x02XXnOE0S.S8SFHGTudMBFGQ7921.dswkSTiHQN7m"  # Contraseña: "123456"
    },
    "kevin1" : {
        "username" : "kevin1",
        "full_name" : "Kevin1 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe1@gmail.com",
        "disabled" : True,   # Usuario deshabilitado
        "password" : "$2a$12$fswJbP6UBVq0sQZsTFewwuRRBhuFiZcTHLQGQsfXybRXUs6lTqovO"  # Contraseña encriptada
    },
    "kevin2" : {
        "username" : "kevin2",
        "full_name" : "Kevin2 Felipe Moreno Ramirez",
        "email" : "morenokevinfelipe2@gmail.com",
        "disabled" : False,  # Usuario activo
        "password" : "$2a$12$UuECOLdnbupH9O6vPtaCCuwPMpceRuS8B6y1smPkj3q/H8jiXnyNG"  # Contraseña encriptada
    }
}

# Función para buscar un usuario en la base de datos incluyendo la contraseña
def search_user_db(username: str):
    if username in users_db:
        # Retorna una instancia UserDB con todos los datos incluyendo la contraseña
        return UserDB(**users_db[username])

# Función para buscar un usuario en la base de datos sin incluir la contraseña
def search_user(username: str ):
    if username in users_db:
        # Retorna una instancia User sin la contraseña (para respuestas públicas)
        return User(**users_db[username])
    
# Función dependencia para autenticar usuario mediante token JWT
async def auth_user(token: str = Depends(oauth2)):
    # Configuración de excepción para credenciales inválidas
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Credenciales de autenticacion invalidas", 
        headers={"WWW-Autenticate": "Bearer"})

    try:
        # Decodifica el token JWT y extrae el username del campo 'sub'
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception  # Si no hay username en el token, lanza excepción

    except JWTError:
        # Si hay error al decodificar el JWT, lanza excepción
        raise exception
    
    # Busca y retorna el usuario si las credenciales son válidas
    return search_user(username)


# Función dependencia para obtener el usuario actual y verificar que esté activo
async def current_user(user: User = Depends(auth_user)):
    # Verifica si el usuario está deshabilitado
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo")

    return user  # Retorna el usuario si está activo

# Endpoint POST para login y generación de token JWT
# Ruta: POST /jwt_auth/login
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
    user = search_user_db(form.username)

    # Verifica la contraseña proporcionada contra la almacenada (encriptada)
    crypt.verify(form.password, user.password)

    if not crypt.verify(form.password, user.password):
        # Si la contraseña no coincide, lanza excepción HTTP 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contraseña no es correcto")

    # Crea el payload del token JWT con username y tiempo de expiración
    acces_token = {"sub":user.username,
                   "exp": datetime.utcnow() + timedelta(minutes=ACCES_TOKEN_DURATION)}

    # Retorna el token JWT firmado y el tipo de token
    return{"acces_token" : jwt.encode(acces_token, SECRET, algorithm=ALGORITHM), "token_type" : "bearer"}



# Endpoint GET protegido para obtener información del usuario autenticado
# Ruta: GET /jwt_auth/users/me
# Requiere token JWT válido en el header Authorization
@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    # Retorna la información del usuario autenticado (sin contraseña)
    return user