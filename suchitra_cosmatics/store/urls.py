from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_results, name='search'),
]