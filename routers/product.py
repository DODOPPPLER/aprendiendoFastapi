from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from routers.products import products_list,Product

router = APIRouter(prefix="/product", tags=["product"], responses={404: {"message": "No encontrado"}})

def find(param):
    product = list(filter(lambda pr: pr.id == param, products_list))  
    try:
        return product
    except:
        return{"error": "No se ha encontrado el producto"}
    
@router.get("/{id}") #path obligatorio
async def product_by_id(id:int):
    product=find(id)
    return product

@router.get("/") #query opcional o condicional
async def product_by_id(id:int):
    product=find(id)
    return product

@router.post("/", status_code=201)
async def product(product: Product):
    if (find(product.id)): 
        raise HTTPException(status_code=304,detail="El Producto ya existe")       
    else:
        products_list.append(product)
        return products_list

@router.put("/product/", status_code=200)
async def product(product: Product):
    if find(product.id):
        for index, product_saved in enumerate(products_list):
            products_list[index] = product if product_saved.id == product.id else product_saved
        return products_list
    else:
        raise HTTPException(status_code=404, detail="Producto no existe")
    
@router.delete("/{id}", status_code=200)
async def product(id: int):
    if find(id):
        for index, product_saved in enumerate(products_list):
            if product_saved.id == id:
                products_list.pop(index)
                break
        return products_list
    else:
        raise HTTPException(status_code=404, detail="Producto no existe")