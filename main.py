from fastapi import FastAPI
from routes.auth_routes import auth_router
from routes.order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from models.schemas import Settings
from routes.product_routes import product_routes
from routes.user_routes import user_routes

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(product_routes)
app.include_router(user_routes)

@AuthJWT.load_config
def get_config():
    return Settings()

@app.get("/")
async def root():
    return {"message": "bu asosiy sahifa"}