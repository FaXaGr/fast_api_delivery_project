from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash

from database.database import session,engine
from common.helper import verify_jwt_admin, verify_jwt
from models.models import User, Order
from models.schemas import ChangePasswordModel

user_routes = APIRouter(
    prefix='/user'
)
session = session(bind=engine)

@user_routes.get('/all',dependencies=[Depends(verify_jwt_admin)])
async def getUsers():
    return jsonable_encoder(session.query(User).all())

@user_routes.get('/{user_id}',dependencies=[Depends(verify_jwt)])
async def getUserDetails(user_id : int):
    user = session.query(User).options(
        joinedload(User.orders).joinedload(Order.product)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "orders": [
            {
                "order_id": order.id,
                "quantity": order.quantity,
                "status": order.order_status.code,
                "product": {
                    "product_id": order.product.id,
                    "product_name": order.product.name,
                    "product_price": order.product.price,
                } if order.product else None
            }
            for order in user.orders
        ]
    }
    return response

@user_routes.patch('/change-password',dependencies=[Depends(verify_jwt)])
async def changePassword(password : ChangePasswordModel,Authorize : AuthJWT = Depends()):
    username = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = generate_password_hash(password.password)
    session.commit()

    return {"message" : "password changed successfully"}

@user_routes.delete('/delete/{user_id}',dependencies=[Depends(verify_jwt)])
async def deleteUser(user_id : int):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()

    return {"message" : "User deleted successfully"}
