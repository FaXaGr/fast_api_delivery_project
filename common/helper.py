from fastapi import Depends, HTTPException,status
from fastapi_jwt_auth import AuthJWT
from database.database import session, engine
from models.models import User

session = session(bind=engine)


def verify_jwt(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

def verify_jwt_admin(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = session.query(User).filter(User.username == current_user).first()
        if not user.is_staff:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )