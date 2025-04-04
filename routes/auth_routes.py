from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from models.schemas import SignUpModel, LoginModel
from database.database import session, engine
from models.models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash

auth_router = APIRouter(
    prefix='/auth'
)

session = session(bind=engine)

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this email already exists')

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this username already exists')

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()
    data = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'is_staff': new_user.is_staff,
        'is_active': new_user.is_active
    }
    response_model = {
        'success': True,
        'code': 201,
        'message': "user is created successfully",
        'data': data
    }

    return response_model

@auth_router.post('/login',status_code=status.HTTP_200_OK)
async def login(user : LoginModel, Authorize : AuthJWT = Depends()):
    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()

    if db_user and check_password_hash(db_user.password,user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        data = {
            "access_token" : access_token,
            "refresh_token" : refresh_token
        }
        response = {
            "status" : "OK",
            "code" : 200,
            "message" : "successfully login",
            "data" : data
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid username or password")



@auth_router.get('/login/refresh')
async def refresh_token(Authorize : AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        db_user = session.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

        new_access_token = Authorize.create_access_token(subject=db_user.username)
        return {
            "message" : "successfully",
            "code" : 200,
            "data" : {
                "new_access_token" : new_access_token
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
