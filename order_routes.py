from fastapi import APIRouter, Depends
from models import User, Order
from schemas import OrderModel
from security import get_current_user
from database import get_db
from http import HTTPStatus
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

T_Session = Annotated[Session, Depends(get_db)]


order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

@order_router.get('/')
async def hello(current_user: User = Depends(get_current_user)):
    return {'Message': 'Hello World'}

@order_router.post('/order', status_code=HTTPStatus.CREATED)
async def place_an_order(session: T_Session,order: OrderModel, current_user: User = Depends(get_current_user)):
    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
        order_status=order.order_status,
        user_id=current_user.id  # Associa o pedido ao usuário autenticado
    )
    
    session.add(new_order)
    session.commit()
   
    response = {
        'pizza_size': new_order.pizza_size,
        'quantity': new_order.quantity,
        'id': new_order.id,
        'order-status': new_order.order_status
    }

    return jsonable_encoder(response)