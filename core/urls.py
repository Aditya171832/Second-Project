from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Basic pages
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/farmer/', views.farmer_register, name='farmer_register'),
    path('register/dealer/', views.dealer_register, name='dealer_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboards
    path('dashboard/farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/dealer/', views.dealer_dashboard, name='dealer_dashboard'),
    
    # Profile Management
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Phase 3: Products & Cart
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Dealer product management
    path('dealer/products/add/', views.dealer_add_product, name='dealer_add_product'),
    path('dealer/products/edit/<int:product_id>/', views.dealer_edit_product, name='dealer_edit_product'),
    
    # Phase 4: Order Management & Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('dealer/orders/', views.dealer_orders, name='dealer_orders'),
    path('dealer/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
]