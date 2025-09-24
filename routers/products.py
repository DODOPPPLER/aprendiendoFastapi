# Importación de módulos necesarios para FastAPI
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel

# Configuración del router con prefijo "/products", etiqueta y respuesta de error por defecto
router = APIRouter(prefix="/products", tags=["products"], responses={404: {"message": "No encontrado"}})

# Modelo de datos Pydantic para el producto
class Product(BaseModel):
    id: int            # ID único del producto
    name: str          # Nombre del producto
    description: str   # Descripción del producto
    price: float       # Precio del producto
    stock: int         # Cantidad en stock
    available: bool    # Disponibilidad del producto

# Lista en memoria que simula una base de datos de productos
products_list = [
    Product(id=1, name="Product1", description="Description1", price=10.0, stock=100, available=True),
    Product(id=2, name="Product2", description="Description2", price=20.0, stock=200, available=True),
    Product(id=3, name="Product3", description="Description3", price=30.0, stock=300, available=False)
]
    
# Función auxiliar para buscar un producto por ID
def find(param):
    # Filtra la lista de productos para encontrar uno con el ID especificado
    product = list(filter(lambda pr: pr.id == param, products_list))  
    try:
        return product  # Retorna la lista de productos encontrados (puede estar vacía)
    except:
        return{"error": "No se ha encontrado el producto"}
    
# Endpoint GET para obtener la lista completa de productos
# Ruta: GET /products/
@router.get("/")
async def products():
    try:
        return products_list  # Retorna todos los productos de la lista
    except:
        return{"error": "No se ha encontrado la lista de productos"}
    
# Endpoint GET con path parameter obligatorio para buscar producto por ID
# Ruta: GET /products/{id}
@router.get("/{id}") #path obligatorio
async def product_by_id(id:int):
    product=find(id)
    return product

# Endpoint GET con query parameter opcional para buscar producto por ID
# Ruta: GET /products/?id=1
@router.get("/") #query opcional o condicional
async def product_by_id(id:int):
    product=find(id)
    return product

# Endpoint POST para crear un nuevo producto
# Ruta: POST /products/
# Retorna código 201 (Created) si es exitoso
@router.post("/", status_code=201)
async def product(product: Product):
    # Verifica si el producto ya existe basándose en el ID
    if (find(product.id)): 
        # Si existe, lanza una excepción HTTP 304 (Not Modified)
        raise HTTPException(status_code=304,detail="El Producto ya existe")       
    else:
        # Si no existe, agrega el producto a la lista y retorna la lista actualizada
        products_list.append(product)
        return products_list

# Endpoint PUT para actualizar un producto existente
# Ruta: PUT /products/product/
# Retorna código 200 (OK) si es exitoso
@router.put("/product/", status_code=200)
async def product(product: Product):
    # Verifica si el producto existe basándose en el ID
    if find(product.id):
        # Si existe, busca y reemplaza el producto en la lista
        for index, product_saved in enumerate(products_list):
            # Reemplaza el producto si el ID coincide, de lo contrario mantiene el original
            products_list[index] = product if product_saved.id == product.id else product_saved
        return products_list
    else:
        # Si no existe, lanza una excepción HTTP 404 (Not Found)
        raise HTTPException(status_code=404, detail="Producto no existe")
    
# Endpoint DELETE para eliminar un producto por ID
# Ruta: DELETE /products/{id}
# Retorna código 200 (OK) si es exitoso
@router.delete("/{id}", status_code=200)
async def product(id: int):
    # Verifica si el producto existe basándose en el ID
    if find(id):
        # Si existe, busca y elimina el producto de la lista
        for index, product_saved in enumerate(products_list):
            if product_saved.id == id:
                # Elimina el producto de la lista cuando encuentra el ID coincidente
                products_list.pop(index)
                break  # Sale del bucle una vez encontrado y eliminado
        return products_list
    else:
        # Si no existe, lanza una excepción HTTP 404 (Not Found)
        raise HTTPException(status_code=404, detail="Producto no existe")