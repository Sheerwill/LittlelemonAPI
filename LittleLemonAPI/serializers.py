from rest_framework import serializers
from . models import Category, MenuItem, Cart, OrderItem, Order
from django.contrib.auth.models import Group, User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)    
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializerHelper(serializers.ModelSerializer):    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']

class GetCartSerializer(serializers.ModelSerializer):
    menuitem = CartSerializerHelper()
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class PostCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']

class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    delivery_crew = UserSerializer(read_only=True)  
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']

class MenuItemSerializerHelper(serializers.ModelSerializer):    
    class Meta:
        model = MenuItem
        fields = ['title', 'price']  

class OrderItemSerializerGet(serializers.ModelSerializer):
    menuitem = MenuItemSerializerHelper(read_only=True)
    order = OrderSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'price', 'order']

class OrderSerializerPatch(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = ['delivery_crew', 'status']

class OrderSerializerPatchCrew(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = ['status']



"""class OrderSerializerPost(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    class Meta:
        model = Order
        fields = ['user']"""



           
    