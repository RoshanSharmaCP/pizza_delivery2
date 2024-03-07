from fastapi import APIRouter,status,Depends, Query
from fastapi.exceptions import HTTPException
from typing import Optional
from database import Session,engine
from schemas import SignUpModel, LoginModel
from models import User, InvalidToken
from werkzeug.security import generate_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
import secrets

auth_router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)


session=Session(bind=engine)

@auth_router.get('/')
async def hello():
    return {"message": "hello world"}

@auth_router.post('/signup')
async def signup(user:SignUpModel):
    
    db_email=session.query(User).filter(User.email==user.email).first()

    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username=session.query(User).filter(User.username==user.username).first()

    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the username already exists"
        )

    new_user=User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)

    session.commit()

    return new_user

@auth_router.post('/login', status_code=200)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):
    db_user=session.query(User).filter(User.username==user.username).first()
    # breakpoint()
    if db_user and secrets.compare_digest(db_user.password, user.password):
        raw_jwt = Authorize.get_raw_jwt()
        if raw_jwt is not None and 'jti' in raw_jwt:
            if session.query(InvalidToken).filter(InvalidToken.user_id == db_user.id, InvalidToken.token == Authorize.get_raw_jwt()['jti']).first():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
        
        
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token=Authorize.create_refresh_token(subject=db_user.username)

        response={
            "access":access_token,
            "refresh":refresh_token
        }
        
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password"
                        )
    
@auth_router.post('/invalidate-token')
async def invalidate_token(token: str = Query(..., title="Token"), Authorize: AuthJWT = Depends()):
    # try:
    #     Authorize.jwt_required()
    # except Exception as e:
    #     raise HTTPException(
    #         status_code= status.HTTP_401_UNAUTHORIZED,
    #         detail = "Invalid Token"
    #     )
    breakpoint()
    current_user = Authorize.get_jwt_subject()
    
    db_user = session.query(User).filter(User.username == current_user).first()
    invalid_token = InvalidToken(token=token, user_id=db_user.id)
    session.add(invalid_token)
    session.commit()

    return {"message": "Token invalidated successfully"}

 
        