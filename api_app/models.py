from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    
    #products = relationship('Product', backref='category', lazy=True)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category")

class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, autoincrement=True)

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    product = relationship("Product")
    cart = relationship("Cart")

