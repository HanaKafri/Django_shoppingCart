from django.http import JsonResponse
from .models import Category, Product, Cart, CartItem
from .serializers import CategorySchema, ProductSchema, CartSchema, CartItemSchema,\
    ProductGetSchema, CartItemGetSchema, CategoryProductSchema,CartProductSchema
from .base import db_session
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy import func
import logging

from django.http import JsonResponse
from rest_framework import status
from .components import CategoryComponent
from sqlalchemy.orm import sessionmaker



# to print queries sent to the DB
logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size = 20  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size allowed


class Categories_API(APIView):
    #pagination_class = CustomPagination
    
    def get(self, request, id=None):
        if id:
            queryset = db_session.query(Category).get(id)
            if not queryset:
                return JsonResponse({"message": "Category not found"}, status=404)
            serializer = CategorySchema()
        # dump: method from Marshmallow to serialize a queryset into a Python data structure to be converted to JSON
            result = serializer.dump(queryset) 
            return JsonResponse(result)
        
        queryset = db_session.query(Category).all()
        
        # Pagination:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = CategorySchema(many=True)
            result = serializer.dump(page)
            return paginator.get_paginated_response(result)
        
        serializer = CategorySchema(many=True)
        result = serializer.dump(queryset)
        return JsonResponse(result, safe=False)
    
    

    
    
    # validation (required fields)
    def post(self, request):
        schema = CategorySchema()
        try:
            # Specify required fields in the "required_fields" list
            required_fields = ["name"]
            
            # Check if the required fields are missing in the request data
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"message": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            category_data = schema.load(request.data)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Create a new category instance and add it to the database
        new_category = Category(**category_data)
        db_session.add(new_category) # add data to session
        db_session.commit() # to add everything in the session to the database

        # Serialize the newly created category and return it in the response
        result = schema.dump(new_category)
        return JsonResponse(result, status=201)

    
    
    

    # validation (required fields)
    def patch(self, request, id):
        # Check if the category with the specified id exists
        category = db_session.query(Category).get(id)
        if not category:
            return JsonResponse({"message": "Category not found"}, status=404)

        schema = CategorySchema()
        
        try:
            # Check if there are any fields to update
            if not request.data:
                return Response(
                    {"message": "No fields to update"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            category_data = schema.load(request.data, partial=True)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Update the category's attributes
        for key, value in category_data.items():
            setattr(category, key, value)

        db_session.commit()

        result = schema.dump(category)
        return JsonResponse(result, status=200)
    
    
    
    def delete(self, request, id):
        # Check if the category with the specified id exists
        category = db_session.query(Category).get(id)
        if not category:
            return JsonResponse({"message": "Category not found"}, status=404)

        # Delete the category
        db_session.delete(category)
        db_session.commit()

        return JsonResponse({"message": "Category deleted"}, status=204)


    
class Products_API(APIView):
    # pagination_class = CustomPagination
    
    def get(self, request, id=None):
        if id: # if id is provided in the request
            queryset = db_session.query(Product).get(id)
            if not queryset:
                return JsonResponse({"message": "Product not found"}, status=404)
            schema = ProductGetSchema()
            result = schema.dump(queryset)
            return JsonResponse(result)
        
        product_name = request.GET.get('name')
        Price = request.GET.get('price')
        
        # eager loading:
        
        # queryset = db_session.query(Product).join(Category).options(contains_eager(Product.category))
        queryset = db_session.query(Product).join(Category).options(joinedload(Product.category))

        if product_name:
            queryset = queryset.filter(Product.name.contains(product_name))
        
        if Price:
            queryset = queryset.filter(Product.price.__gt__(Price)) # gt: greater than

        # Pagination:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ProductGetSchema(many=True)
            result = serializer.dump(page)
            return paginator.get_paginated_response(result)
        
        schema = ProductGetSchema(many=True)
        result = schema.dump(queryset)
        #render(request, "template.html", Context) # to open html page ???????
        return JsonResponse(result, safe=False)
    
    
    # validation (required fields)
    def post(self, request):
        # Deserialize the request data using the ProductSchema
        schema = ProductSchema()
        try:
            # Specify required fields in the "required_fields" list
            required_fields = ["name", "price", "category_id"]
            
            # Check if the required fields are missing in the request data
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"message": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                    
                # Check if the specified category exists
                category_id = request.data['category_id']
                category = db_session.query(Category).get(category_id)
                if not category:
                    return JsonResponse({"message": f"Category with ID {category_id} not found"}, status=400)
            
                product_price = request.data['price']
                if product_price <= 0:
                    return JsonResponse({"message": f"Price {product_price} not positive"}, status=400)
                

            Product_data = schema.load(request.data)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Create a new Product instance and add it to the database
        new_Product = Product(**Product_data)
        db_session.add(new_Product)
        db_session.commit()

        # Serialize the newly created Product and return it in the response
        result = schema.dump(new_Product)
        return JsonResponse(result, status=201)



    # validation (required fields)
    def patch(self, request, id=None):
        
        if id:
            # Check if the Product with the specified id exists
            product = db_session.query(Product).get(id)
            if not product:
                return JsonResponse({"message": "Product not found"}, status=404)

            # Deserialize the request data using the ProductSchema
            schema = ProductSchema()
            try:
                # Check if the 'category_id' is provided in the request data
                if 'category_id' in request.data:
                    # Check if the specified category exists
                    category_id = request.data['category_id']
                    category = db_session.query(Category).get(category_id)
                    if not category:
                        return JsonResponse({"message": f"Category with ID {category_id} not found"}, status=400)

                # Check if there are any fields to update
                if not request.data:
                    return Response(
                        {"message": "No fields to update"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                Product_data = schema.load(request.data, partial=True)
            except Exception as e:
                return Response({"message": "Invalid data", "errors": str(e)}, status=400)

            # Update the Product's attributes
            for key, value in Product_data.items():
                setattr(product, key, value)

            db_session.commit()

            # Serialize the updated Product and return it in the response
            result = schema.dump(product)
            return JsonResponse(result, status=200)
        
        else:
            return JsonResponse({"message": "missing ID"}, status=500)
        
        
    def delete(self, request, id):
        # Check if the Product with the specified id exists
        product_instance = db_session.query(Product).get(id)
        if not product_instance:
            return JsonResponse({"message": "Product not found"}, status=404)

        # Delete the Product instance
        db_session.delete(product_instance)
        db_session.commit()

        return JsonResponse({"message": "Product deleted"}, status=204)


    
class Carts_API(APIView):
    #pagination_class = CustomPagination
    
    
    def get(self, request, id=None):
        if id:
            queryset = db_session.query(Cart).get(id)
            if not queryset:
                return JsonResponse({"message": "Cart not found"}, status=404)
            schema = CartSchema()
            result = schema.dump(queryset)
            return JsonResponse(result)
        
        queryset = db_session.query(Cart).all()
        
        # Pagination:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = CartSchema(many=True)
            result = serializer.dump(page)
            return paginator.get_paginated_response(result)
        
        schema = CartSchema(many=True)
        result = schema.dump(queryset)
        return JsonResponse(result, safe=False)
    
    
    def post(self, request):
        # Deserialize the request data using the CartSchema
        schema = CartSchema()
        try:
            Cart_data = schema.load(request.data)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Create a new Cart instance and add it to the database
        new_Cart = Cart(**Cart_data)
        db_session.add(new_Cart)
        db_session.commit()

        # Serialize the newly created Cart and return it in the response
        result = schema.dump(new_Cart)
        return JsonResponse(result, status=201)
    
    
    
    def patch(self, request, id):
        # Check if the Cart with the specified id exists
        Cart = db_session.query(Cart).get(id)
        if not Cart:
            return JsonResponse({"message": "Cart not found"}, status=404)

        # Deserialize the request data using the CartSchema
        schema = CartSchema()
        try:
            Cart_data = schema.load(request.data, partial=True)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Update the Cart's attributes
        for key, value in Cart_data.items():
            setattr(Cart, key, value)

        db_session.commit()

        # Serialize the updated Cart and return it in the response
        result = schema.dump(Cart)
        return JsonResponse(result, status=200)
    
    
    def delete(self, request, id):
        # Check if the Cart with the specified id exists
        Cart = db_session.query(Cart).get(id)
        if not Cart:
            return JsonResponse({"message": "Cart not found"}, status=404)

        # Delete the Cart
        db_session.delete(Cart)
        db_session.commit()

        return JsonResponse({"message": "Cart deleted"}, status=204)

    
    
    
class CartItems_API(APIView):
    #pagination_class = CustomPagination
    
    def get(self, request, id=None):
        if id:
            queryset = db_session.query(CartItem).get(id)
            if not queryset:
                return JsonResponse({"message": "CartItem not found"}, status=404)
            serializer = CartItemGetSchema()
    # dump: method from Marshmallow to serialize a queryset into a Python data structure to be converted to JSON
            result = serializer.dump(queryset)
            return JsonResponse(result)
        
        product_name = request.GET.get('product')  # Get the 'product_name' query parameter
        
        #queryset = db_session.query(CartItem).join(Product).options(joinedload(CartItem.product))

        if product_name:
            # Filter cart items by product name
            #queryset = queryset.filter(CartItem.product.contains(product_name))
            queryset = db_session.query(CartItem).filter(CartItem.product.has(name=product_name))
        else:
            queryset = db_session.query(CartItem).all()

        # Pagination:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = CartItemGetSchema(many=True)
            result = serializer.dump(page)
            return paginator.get_paginated_response(result)
        
        serializer = CartItemGetSchema(many=True)
        result = serializer.dump(queryset)
        return JsonResponse(result, safe=False)
    
    
    
    # validation (required fields)
    def post(self, request):
        schema = CartItemSchema()
        try:
            # Specify required fields in the "required_fields" list
            required_fields = ["cart_id", "product_id", "quantity"]
            
            # Check if the required fields are missing in the request data
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"message": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            CartItem_data = schema.load(request.data)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Create a new CartItem instance and add it to the database
        new_CartItem = CartItem(**CartItem_data)
        db_session.add(new_CartItem) # add data to session
        db_session.commit() # to be added to database

        # Serialize the newly created CartItem and return it in the response
        result = schema.dump(new_CartItem)
        return JsonResponse(result, status=201)



    # validation (required fields)
    def patch(self, request, id):
        # Check if the CartItem with the specified id exists
        cartItem = db_session.query(CartItem).get(id)
        if not cartItem:
            return JsonResponse({"message": "CartItem not found"}, status=404)

        schema = CartItemSchema()
        try:
            # Specify required fields in the "required_fields" list
            required_fields = ["name"]
            
            # Check if the required fields are missing in the request data
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"message": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            CartItem_data = schema.load(request.data, partial=True)
        except Exception as e:
            return Response({"message": "Invalid data", "errors": str(e)}, status=400)

        # Update the CartItem's attributes
        for key, value in CartItem_data.items():
            setattr(cartItem, key, value)

        db_session.commit()

        result = schema.dump(cartItem)
        return JsonResponse(result, status=200)
    
    
    
    def delete(self, request, id):
        # Check if the CartItem with the specified id exists
        cartItem = db_session.query(CartItem).get(id)
        if not cartItem:
            return JsonResponse({"message": "CartItem not found"}, status=404)

        # Delete the CartItem
        db_session.delete(cartItem)
        db_session.commit()

        return JsonResponse({"message": "CartItem deleted"}, status=204)


# API to count number of products for each category
class CategoryProduct_API(APIView):
    
    def get(self, request, id=None):
        
        queryset = db_session.query(Category.name, func.count(Product.id)).outerjoin(Product).group_by(Category.id).all()

        serializer = CategoryProductSchema(many=True)
        result = serializer.dump(queryset)
        return JsonResponse(result, safe=False)
    
    
# API to get the total price for each cart
class CartProduct_API(APIView):
    
    def get(self, request, id=None):
        
        queryset = db_session.query(Cart.id.label("Cart_id"), func.sum(Product.price * CartItem.quantity).label('total_price')).\
            join(CartItem, Product.id == CartItem.product_id).\
            join(Cart, CartItem.cart_id == Cart.id).\
            group_by(Cart.id).order_by(Cart.id)
    
        serializer = CartProductSchema(many=True)
        result = serializer.dump(queryset)
        return JsonResponse(result, safe=False)
    