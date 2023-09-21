from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.Categories_API.as_view()),
    path('categories/<int:id>', views.Categories_API.as_view()),
    path('categories/count', views.CategoryProduct_API.as_view()),
    
    path('carts/', views.Carts_API.as_view()),
    path('carts/<int:id>', views.Carts_API.as_view()),
    
    path('products/', views.Products_API.as_view()),
    path('products/<int:id>', views.Products_API.as_view()),
    
    path('cartItems/', views.CartItems_API.as_view()),
    path('cartItems/<int:id>', views.CartItems_API.as_view()),
    path('cartItems/count', views.CartProduct_API.as_view()),
    
]
