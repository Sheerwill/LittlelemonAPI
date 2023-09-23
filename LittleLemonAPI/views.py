from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from . models import MenuItem, Cart, Order, OrderItem
from . serializers import MenuItemSerializer, UserSerializer, OrderSerializerPatchCrew, OrderSerializerPatch, OrderSerializer, GetCartSerializer, PostCartSerializer, OrderItemSerializerGet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import UserRateThrottle

# Create your views here.
@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default = 2)
        page = request.query_params.get('page', default = 1)
        if category_name:
            items = items.filter(category__title = category_name)
        if to_price:
            items = items.filter(price = to_price)
        if search:
            items = items.filter(title__contains = search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page = perpage)
        try:
            items = Paginator.page(number=page, self=paginator)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
        
    if request.method == 'POST':
        if request.user.groups.filter(name = "Manager").exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception = True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item(request, pk):
    if request.method == 'GET':
        item = get_object_or_404(MenuItem, pk=pk)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    if request.user.groups.filter(name = "Manager").exists():
        if request.method == 'POST':
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception = True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)  
        if request.method == 'PUT':
            serialized_item = MenuItemSerializer(MenuItem.objects.select_related('category').get(pk=pk), data=request.data)
            serialized_item.is_valid(raise_exception = True)
            serialized_item.save()
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'PATCH':
            serialized_item = MenuItemSerializer(MenuItem.objects.select_related('category').get(pk=pk), data=request.data, partial=True)
            serialized_item.is_valid(raise_exception = True)
            serialized_item.save()
            return Response(status=status.HTTP_201_CREATED)            
        if request.method == 'DELETE':
            item = get_object_or_404(MenuItem, pk=pk)
            item.delete()
            return Response(status.HTTP_204_NO_CONTENT)                          
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)   
    
@api_view(['GET', 'POST'])
def managers(request):
    if request.user.groups.filter(name = "Manager").exists():
        if request.method == 'GET':
            managers = Group.objects.get(name="Manager")
            members = managers.user_set.all()
            serialized_item = UserSerializer(members, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status = status.HTTP_403_FORBIDDEN)
    
@api_view(['DELETE'])
def delete_manager(request, userId):
    if request.user.groups.filter(name = "Manager").exists():
        user = get_object_or_404(User, pk=userId)
        managers = Group.objects.get(name = "Manager")
        managers.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'POST'])
def delivery_crew(request):
    if request.user.groups.filter(name = "Manager").exists():
        if request.method == 'GET':
            delivery_crew = Group.objects.get(name = "Delivery crew")
            members = delivery_crew.user_set.all()
            serialized_members = UserSerializer(members, many=True)
            return Response(serialized_members.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            username = request.data['username']  
            user = get_object_or_404(User, username=username)          
            delivery_crew = Group.objects.get(name = 'Delivery crew')
            delivery_crew.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['DELETE'])
def delete_mgr(request, userId):
    if request.user.groups.filter(name = "Manager").exists():
        user = get_object_or_404(User, pk=userId)
        managers = Group.objects.get(name = "Manager")
        managers.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    if not request.user.groups.exists():
        if request.method == 'GET':
            user = request.user
            cart_items = Cart.objects.select_related('menuitem').filter(user=user)
            serialized_items = GetCartSerializer(cart_items, many = True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            serialized_item = PostCartSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            id = request.data['menuitem']
            quantity = request.data['quantity'] 
            item = get_object_or_404(MenuItem, id=id)
            price = int(quantity ) * item.price
            Cart.objects.create(user=request.user, menuitem=item, quantity=quantity, unit_price=item.price, price=price)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            cart = Cart.objects.all().filter(user=user)
            cart.delete()
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_items(request):
    if not request.user.groups.exists():
        if request.method == 'GET':
            user = request.user
            order = OrderItem.objects.all().select_related('menuitem', 'order').filter(order__user = user)
            menuitem = request.query_params.get('menuitem')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            perpage = request.query_params.get('perpage', default = 2)
            page = request.query_params.get('page', default = 1)
            if menuitem:
                order = order.filter(menuitem__title = menuitem)
            if to_price:
                order = order.filter(unit_price = to_price)
            if search:
                order = order.filter(menuitem__title__contains = search)
            if ordering:
                ordering_fields = ordering.split(",")
                order = order.order_by(*ordering_fields)
            paginator = Paginator(order, per_page = perpage)
            try:
                order = Paginator.page(number=page, self=paginator)
            except EmptyPage:
                order = []
            serialized_item = OrderItemSerializerGet(order, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        if request.method == 'POST':                         
            cart_items=Cart.objects.all().filter(user=request.user)
            total = 0
            for cart_item in cart_items:
                total += cart_item.price
            order = Order.objects.create(user=request.user, delivery_crew=None, status=0, total=total)
            order.save()            
            for item in cart_items:
                order_items = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)            
            cart_items.delete()
            return Response(status=status.HTTP_201_CREATED)
    elif request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            order_items = OrderItem.objects.select_related('menuitem', 'order').all()
            serialized_item = OrderItemSerializerGet(order_items, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
    elif request.user.groups.filter(name='Delivery crew').exists():
        if request.method == 'GET':
            order = Order.objects.select_related('user').filter(delivery_crew__isnull=False)
            serialized_item = OrderSerializer(order, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)                    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def order(request, pk):
    if not request.user.groups.exists():
        if request.method == 'GET':
            user = request.user
            order_item = OrderItem.objects.select_related('order', 'menuitem').all().filter(id=pk, order__user=user)
            if order_item:
                serialized_item = OrderItemSerializerGet(order_item, many=True)
                return Response(serialized_item.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
    elif request.user.groups.filter(name='Manager').exists():
        if request.method == 'PATCH':
            serialized_item = OrderSerializerPatch(Order.objects.select_related('user').get(id=pk), data=request.data, partial=True)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()            
            return Response(status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            item = get_object_or_404(OrderItem, id=pk)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        if request.method == 'PATCH':
            serialized_item = OrderSerializerPatchCrew(Order.objects.select_related('user').get(id=pk), data=request.data, partial=True)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()            
            return Response(status=status.HTTP_200_OK)
        


    
        






    

