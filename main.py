from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import products,users,basic_users_auth,jwt_users_auth,users_db

app = FastAPI()

#routers
app.include_router(products.router)
app.include_router(product.router)

app.include_router(users.router)
app.include_router(user.router)
app.include_router(users_db.router)

app.include_router(basic_users_auth.router)
app.include_router(jwt_users_auth.router)

@app.get("/")
async def root():
    return {"Hello": "World"}