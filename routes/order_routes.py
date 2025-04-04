from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,Depends
from fastapi_jwt_auth import AuthJWT
from starlette import status

from common.helper import verify_jwt, verify_jwt_admin
from models.schemas import OrderModel
from database.database import session, engine
from models.models import Order, User

order_router = APIRouter(
    prefix='/order'
)
session = session(bind=engine)

@order_router.post('/create',dependencies=[Depends(verify_jwt)])
async def createOrder(order : OrderModel, Authorize : AuthJWT = Depends()):
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        quantity = order.quantity,
        user_id = user.id,
        product_id = order.product_id
    )
    session.add(new_order)
    session.commit()
    response = {
        "message": "order is created",
        "code": 201,
        "data": {
            "id" : new_order.id,
            "quantity" : new_order.quantity,
            "user" : {
                "id" : new_order.user.id,
                "username" : new_order.user.username,
                "is_active" : new_order.user.is_active
            },
            "product" : {
                "id" : new_order.product.id,
                "name" : new_order.product.name,
                "price" : new_order.product.price
            }
        }
    }
    return response

@order_router.delete('/delete/{order_id}',dependencies=[Depends(verify_jwt)])
async def delete(order_id : int):
    order = session.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

    session.delete(order)
    session.commit()

    return {"message" : "Order deleted successfully"}

@order_router.get('/private/all/',dependencies=[Depends(verify_jwt_admin)])
async def getOrders(Authorize : AuthJWT  = Depends()):
    orders = session.query(Order).all()
    return jsonable_encoder(orders)