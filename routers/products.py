from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"], responses={404: {"message": "No encontrado"}})

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    available: bool

products_list = [
    Product(id=1, name="Product1", description="Description1", price=10.0, stock=100, available=True),
    Product(id=2, name="Product2", description="Description2", price=20.0, stock=200, available=True),
    Product(id=3, name="Product3", description="Description3", price=30.0, stock=300, available=False)
]
    
@router.get("/")
async def products():
    try:
        return products_list
    except:
        return{"error": "No se ha encontrado la lista de productos"}

    