from . import views
from django.urls import path

urlpatterns = [
    path('menu-items', views.menu_items),
    path('menu-item-detail/<int:pk>', views.menu_item),
    path('groups/managers/users', views.managers),
    path('groups/manager/users/<int:userId>', views.delete_manager),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>', views.delete_mgr),
    path('cart/menu-items', views.cart),
    path('orders', views.order_items),
    path('orders/<int:pk>', views.order),
    
]