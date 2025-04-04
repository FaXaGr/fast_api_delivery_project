from datetime import timedelta

from pydantic import BaseModel
from typing import Optional,List

class ProductModel(BaseModel):
    name : str
    price : int

class OrderModel(BaseModel):
    quantity : int
    product_id : str

    class Config:
        from_attributes = True

class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]
    orders : Optional[List[OrderModel]] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'username': "mohirdev",
                'email': "mohirdev.praktikum@gmail.com",
                'password': "password12345",
                'is_staff': False,
                "is_active": True
            }
        }
class ChangePasswordModel(BaseModel):
    password : str

class Settings(BaseModel):
    authjwt_secret_key = 'asdfa124343131324jh12j3h4jh134kh1b23j12nk1j23nkj1'
    authjwt_access_token_expires = timedelta(days=15)


class LoginModel(BaseModel):
    username_or_email : str
    password : str




class ProductUpdate(BaseModel):
    name : Optional[str] = None
    price : Optional[int] = None
