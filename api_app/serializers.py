from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import Category, Product, Cart, CartItem
from marshmallow import fields

class CategorySchema(SQLAlchemyAutoSchema):

    id = fields.Int()
    name = fields.String()
    
    class Meta:
        model = Category
        fields = ("id", "name")
        
class ProductGetSchema(SQLAlchemyAutoSchema):

    id = fields.Int()
    price = fields.Float()
    name = fields.String()
    category = fields.Nested(CategorySchema)

    class Meta:
        ordered = True
        model = Product
        #fields = ("id", "price", "name", "category")

class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        fields = ("id", "price", "name", "category_id")
    
class CartSchema(SQLAlchemyAutoSchema):
    id = fields.Int()
    
    class Meta:
        model = Cart
       
class CartItemGetSchema(SQLAlchemyAutoSchema):
    id = fields.Int()
    cart = fields.Nested(CartSchema)
    product = fields.Nested(ProductSchema)
    quantity = fields.Int()
    
    class Meta:
        ordered = True
        model = CartItem
        #fields = ("id", "cart", "product", "quantity")

        
class CartItemSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = CartItem
        fields = ("id", "cart_id", "product_id", "quantity")

# to count products
class CategoryProductSchema(SQLAlchemyAutoSchema):
    name = fields.String()
    product_count = fields.Function(lambda obj: obj[1])

# to get total price of a cart
class CartProductSchema(SQLAlchemyAutoSchema):
    Cart_id = fields.Int()
    total_price = fields.Function(lambda obj: obj[1])

