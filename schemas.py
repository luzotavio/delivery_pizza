from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool
    is_staff: bool

class LoginModel(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str]='PENDING'
    pizza_size: Optional[str]='SMALL'
    user_id : Optional[int]
    
class OrderStatusModel(BaseModel):
    order_status: Optional[str] = 'PENDING'
