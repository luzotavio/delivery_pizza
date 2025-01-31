from fastapi import FastAPI, Depends
from auth_routes import auth_router
from order_routes import order_router
from database import engine, Base
from security import get_current_user
from models import User

app = FastAPI()

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(order_router)

@app.get('/')
async def root(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}!"}


