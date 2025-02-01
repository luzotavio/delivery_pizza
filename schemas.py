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
    quantity: int
    order_status: Optional[str]='PENDING'
    pizza_size: Optional[str]='SMALL'
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 1,
                "order_status": "PENDING",
                "pizza_size": "SMALL",
            }
    }
    
class OrderStatusModel(BaseModel):
    order_status: Optional[str] = 'PENDING'
