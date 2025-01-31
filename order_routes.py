from fastapi import APIRouter, Depends, HTTPException
from models import User, Order
from schemas import OrderModel, OrderStatusModel
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

@order_router.get('orders')
async def list_all_orders(session: T_Session, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        orders = session.query(Order).all()
        
        return jsonable_encoder(orders)
    
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="you are no super-user"
    )

@order_router.get('/orders{id}')
async def get_order_by_id(session: T_Session,id:int,current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        
        return jsonable_encoder(order)
        
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="you are no super-user"
    )
    
@order_router.get('/user/orders')
async def get_user_orders(current_user: User = Depends(get_current_user)):
    return jsonable_encoder(current_user.orders)


@order_router.get('/user/order/{order_id}')
async def get_specif_order(id:int, current_user: User = Depends(get_current_user)):
    orders = current_user.orders
    for order in orders:
        if order.id == id:
            return jsonable_encoder(order)
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail='No Order with such id'
    ) 
    
@order_router.put('/order/update/{order_id}')
async def update_order(session: T_Session,id:int,order: OrderModel, current_user: User = Depends(get_current_user)):
    order_to_update = session.query(Order).filter(Order.id == id).first()
    
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size
    
    session.commit()

    return jsonable_encoder(order_to_update)

@order_router.patch('/order/update{order_id}')
async def update_order_status(session: T_Session,order: OrderStatusModel,id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id). first()
        
        order_to_update.order_status = order.order_status
        
        session.commit()
        
        response = {
            'quantity': order_to_update.quantity,
            'pizza_size': order_to_update.pizza_size,
            'order_status': order_to_update.order_status
        }

        return jsonable_encoder(response)
    
@order_router.delete('/order/delete/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_an_order(session: T_Session,id:int, current_user: User = Depends(get_current_user)):
    order_to_delete = session.query(Order).filter(Order.id == id).first()
    
    session.delete(order_to_delete)
    
    session.commit()
    
    return order_to_delete