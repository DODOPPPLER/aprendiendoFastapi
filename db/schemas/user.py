# Esquemas de serialización para convertir documentos de MongoDB a diccionarios Python

# Función para serializar un documento de usuario individual de MongoDB
def user_schema(user) -> dict:
    # Convierte un documento de MongoDB a un diccionario Python
    # Transforma el ObjectId de MongoDB ('_id') a string para JSON
    return{"id": str(user["_id"]),      # Convierte ObjectId a string
           "username": user["username"], # Nombre de usuario
           "email": user["email"],}      # Correo electrónico del usuario

# Función para serializar una lista de documentos de usuarios de MongoDB
def users_schema(users) -> list:
    # Aplica user_schema a cada documento de la lista usando list comprehension
    return [user_schema(user) for user in users]