from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas import SignUpModel, Token
from models import User
from database import get_db
from security import create_access_token, verify_password, get_current_user, get_password_hash

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

T_Session = Annotated[Session, Depends(get_db)]

@auth_router.post('/signup', response_model=SignUpModel)
async def signup(user: SignUpModel, session: T_Session):
    user_db = session.scalar(select(User).where((User.email == user.email) | (User.username == user.username)))
    
    if user_db:
        raise HTTPException(
            status_code=400,
            detail='Email or username already exists'
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@auth_router.post('/token', response_model=Token)
async def login_for_access_token(
    session: T_Session, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = session.scalar(select(User).where(User.username == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect username or password'
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}

@auth_router.post('/refresh_token', response_model=Token)
async def refresh_access_token(
    user: User = Depends(get_current_user),
):
    new_access_token = create_access_token(data={'sub': user.username})

    return {'access_token': new_access_token, 'token_type': 'bearer'}






        
        
    