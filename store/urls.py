from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:pk>/', views.buy_now, name='buy_now'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/<int:pk>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='orders'),
    path('order/cancel/<int:pk>/', views.cancel_order, name='cancel_order'),
    
    # Notifications
    path('notification/read/<int:pk>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notification/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Seller Dashboard
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('seller/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('seller/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('seller/update-order-item/<int:pk>/', views.update_order_status, name='update_order_status'),
    path('seller/update-stock/<int:pk>/', views.update_stock, name='update_stock'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/toggle-status/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin-dashboard/approve-seller/<int:pk>/', views.approve_seller, name='approve_seller'),
]
