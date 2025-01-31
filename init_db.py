# -*- coding: utf-8 -*-

from database import engine, Base
from models import Order, User

Base.metadata.create_all(bind=engine)