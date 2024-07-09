
# shop/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.first_page,name='first_page'),
    path('products', views.product_list, name='product_list'),  # No trailing slash
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('my-cart/', views.my_cart, name='my_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('logout/', views.logout_view, name='logout'),
    path('custom_logout/', auth_views.LogoutView.as_view(), name='custom_logout'),
    path('sell_item/', views.sell_item, name='sell_item'),   
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
