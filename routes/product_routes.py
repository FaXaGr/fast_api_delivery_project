from fastapi.encoders import jsonable_encoder

from database.database import session, engine
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi_jwt_auth import AuthJWT
from common.helper import verify_jwt_admin
from models.models import User,Product
from models.schemas import ProductModel,ProductUpdate

product_routes = APIRouter(
    prefix = '/product'
)
session = session(bind=engine)


@product_routes.get('/all')
async def productList():
    return jsonable_encoder(session.query(Product).all())


@product_routes.post('private/create',dependencies=[Depends(verify_jwt_admin)])
async def createProduct(product : ProductModel ,Authorize : AuthJWT = Depends()):

    current_username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_username).first()
    if user and user.is_staff:
        new_product = Product(
            name = product.name,
            price = product.price
        )
        session.add(new_product)
        session.commit()
        response = {
            "message" : "product is created",
            "code" : 200,
            "data" : {
                "id" : new_product.id,
                "name" : new_product.name,
                "price" : new_product.price
            }
        }
        return response
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@product_routes.get('/{product_id}',status_code=status.HTTP_200_OK)
async def getProductWithId(product_id: int):
    product = session.query(Product).filter(Product.id == product_id).first()
    return jsonable_encoder(product)

@product_routes.delete('/private/{product_id}',dependencies=[Depends(verify_jwt_admin)])
async def deleteProduct(product_id : int):
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="product not found")

    session.delete(product)
    session.commit()

    return {"message" : "product successfully deleted"}

@product_routes.patch('/private/{product_id}/update',dependencies=[Depends(verify_jwt_admin)])
async def update(new_product : ProductUpdate,product_id : int):
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="product not found")

    for key,value in new_product.dict(exclude_unset=True).items():
        setattr(product,key,value)
    session.commit()
    session.refresh(product)
    return jsonable_encoder(product)

